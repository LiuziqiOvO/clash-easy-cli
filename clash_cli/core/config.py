"""
Configuration management for Clash CLI
"""

import os
import toml
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger

from ..models.config import ClashConfig

# 计算项目根目录（clash_cli 上三级目录）
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = Path(config_file) if config_file else None
        self._config: Optional[ClashConfig] = None
        self._env_vars: Dict[str, str] = {}
        
        # 加载配置
        self.load_config()
    
    def load_config(self) -> ClashConfig:
        """加载配置"""
        config_data = {}
        
        # 1. 首先加载默认配置
        config_data.update(self._get_default_config())
        
        # 2. 加载.env文件配置
        env_config = self._load_env_config()
        if env_config:
            config_data.update(env_config)
        
        # 3. 如果指定了配置文件，加载配置文件
        if self.config_file and self.config_file.exists():
            file_config = self._load_config_file()
            if file_config:
                config_data.update(file_config)
        
        # 4. 加载环境变量覆盖
        env_override = self._load_env_variables()
        if env_override:
            config_data.update(env_override)
        
        try:
            self._config = ClashConfig(**config_data)
            self._config.ensure_directories()
            logger.info("配置加载成功")
            return self._config
        except Exception as e:
            logger.error(f"配置加载失败: {e}")
            # 使用默认配置
            self._config = ClashConfig()
            self._config.ensure_directories()
            return self._config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "proxy": {
                "http_port": 7890,
                "socks_port": 7891,
                "redir_port": 7892,
                "api_port": 9090,
            },
            "allow_lan": True,
            "log_level": "info",
            "mode": "rule",
            "auto_start_proxy": True,
            "dashboard_enabled": True,
        }
    
    def _load_env_config(self) -> Optional[Dict[str, Any]]:
        """加载.env文件配置"""
        env_file = PROJECT_ROOT / ".env"
        if not env_file.exists():
            return None
        
        try:
            config = {}
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        # 兼容 'export KEY=VALUE' 形式
                        if key.startswith('export '):
                            key = key[len('export '):].strip()
                        value = value.strip().strip('\'"')
                        
                        # 存储环境变量
                        self._env_vars[key] = value
                        
                        # 转换为配置格式
                        if key == 'CLASH_URL':
                            config['subscription_url'] = value
                        elif key == 'CLASH_SECRET':
                            # 允许空字符串，空表示取消密码
                            config['secret'] = value
                        elif key == 'SKIP_SUBSCRIPTION_CHECK':
                            config['skip_subscription_check'] = value == '1'
            
            logger.debug(f"从.env文件加载配置: {config}")
            return config
            
        except Exception as e:
            logger.warning(f"读取.env文件失败: {e}")
            return None
    
    def _load_config_file(self) -> Optional[Dict[str, Any]]:
        """加载配置文件"""
        if not self.config_file or not self.config_file.exists():
            return None
        
        try:
            suffix = self.config_file.suffix.lower()
            
            if suffix in ['.toml']:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return toml.load(f)
            elif suffix in ['.yaml', '.yml']:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            else:
                logger.warning(f"不支持的配置文件格式: {suffix}")
                return None
                
        except Exception as e:
            logger.error(f"读取配置文件失败: {e}")
            return None
    
    def _load_env_variables(self) -> Dict[str, Any]:
        """加载环境变量覆盖"""
        config = {}
        
        # 支持通过环境变量覆盖配置
        env_mapping = {
            'CLASH_CLI_HTTP_PORT': ('proxy', 'http_port'),
            'CLASH_CLI_SOCKS_PORT': ('proxy', 'socks_port'),
            'CLASH_CLI_API_PORT': ('proxy', 'api_port'),
            'CLASH_CLI_LOG_LEVEL': ('log_level',),
            'CLASH_CLI_MODE': ('mode',),
        }
        
        for env_key, config_path in env_mapping.items():
            value = os.getenv(env_key)
            if value is not None:
                # 设置嵌套配置
                current = config
                for key in config_path[:-1]:
                    if key not in current:
                        current[key] = {}
                    current = current[key]
                
                # 类型转换
                if 'port' in config_path[-1]:
                    try:
                        value = int(value)
                    except ValueError:
                        continue
                
                current[config_path[-1]] = value
        
        return config
    
    @property
    def config(self) -> ClashConfig:
        """获取当前配置"""
        if self._config is None:
            self.load_config()
        return self._config
    
    def get_secret(self) -> Optional[str]:
        """获取Secret，优先从环境变量获取"""
        # 优先从.env文件获取
        if 'CLASH_SECRET' in self._env_vars and self._env_vars['CLASH_SECRET']:
            return self._env_vars['CLASH_SECRET']
        
        # 其次从配置获取
        if self.config.secret:
            return self.config.secret
        
        # 最后从config.yaml文件读取
        config_file = self.config.get_config_file_path()
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                    return config_data.get('secret')
            except Exception as e:
                logger.debug(f"从config.yaml读取secret失败: {e}")
        
        return None
    
    def save_env_config(self, subscription_url: str, secret: Optional[str] = None) -> bool:
        """保存配置到.env文件"""
        env_file = PROJECT_ROOT / ".env"
        
        try:
            # 读取现有配置
            lines = []
            if env_file.exists():
                with open(env_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            
            # 更新配置
            updated = set()
            for i, line in enumerate(lines):
                if line.strip().startswith('CLASH_URL=') or line.strip().startswith('export CLASH_URL='):
                    lines[i] = f"export CLASH_URL='{subscription_url}'\n"
                    updated.add('CLASH_URL')
                elif secret and (line.strip().startswith('CLASH_SECRET=') or line.strip().startswith('export CLASH_SECRET=')):
                    lines[i] = f"export CLASH_SECRET='{secret}'\n"
                    updated.add('CLASH_SECRET')
                elif line.strip().startswith('SKIP_SUBSCRIPTION_CHECK=') or line.strip().startswith('export SKIP_SUBSCRIPTION_CHECK='):
                    lines[i] = f"SKIP_SUBSCRIPTION_CHECK=0\n"
                    updated.add('SKIP_SUBSCRIPTION_CHECK')
            
            # 添加新配置
            if 'CLASH_URL' not in updated:
                lines.append(f"export CLASH_URL='{subscription_url}'\n")
            if secret and 'CLASH_SECRET' not in updated:
                lines.append(f"export CLASH_SECRET='{secret}'\n")
            if 'SKIP_SUBSCRIPTION_CHECK' not in updated:
                lines.append("SKIP_SUBSCRIPTION_CHECK=0\n")
            
            # 写入文件
            with open(env_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            # 更新内存中的环境变量
            self._env_vars['CLASH_URL'] = subscription_url
            if secret:
                self._env_vars['CLASH_SECRET'] = secret
            self._env_vars['SKIP_SUBSCRIPTION_CHECK'] = '0'
            
            logger.info("配置已保存到.env文件")
            return True
            
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            return False 