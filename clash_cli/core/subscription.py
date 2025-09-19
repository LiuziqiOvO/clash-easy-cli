"""
Subscription management for Clash CLI
"""

import httpx
import yaml
import base64
import subprocess
from pathlib import Path
from typing import Optional
from loguru import logger

from ..models.config import ClashConfig, PROJECT_ROOT


class SubscriptionManager:
    """简化的订阅管理器"""
    
    def __init__(self, config: ClashConfig):
        self.config = config
        
    async def download_subscription(self, url: str) -> bool:
        """下载订阅配置"""
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                # 保存原始内容
                raw_file = self.config.temp_dir / "clash.yaml"
                raw_file.write_bytes(response.content)
                
                logger.info("订阅配置下载成功")
                return True
                
        except Exception as e:
            logger.error(f"下载订阅失败: {e}")
            return False
    
    async def process_subscription(self) -> bool:
        """处理订阅配置"""
        try:
            raw_file = self.config.temp_dir / "clash.yaml"
            if not raw_file.exists():
                logger.error("原始配置文件不存在")
                return False
            
            # 读取原始内容
            content = raw_file.read_text(encoding='utf-8')
            
            # 检查是否是标准Clash格式
            if self._is_clash_format(content):
                logger.info("配置已是标准Clash格式")
                processed_file = self.config.temp_dir / "clash_config.yaml"
                processed_file.write_text(content)
                return await self._merge_config()
            
            # 尝试base64解码
            try:
                decoded_content = base64.b64decode(content).decode('utf-8')
                if self._is_clash_format(decoded_content):
                    logger.info("配置为base64编码的Clash格式")
                    processed_file = self.config.temp_dir / "clash_config.yaml"
                    processed_file.write_text(decoded_content)
                    return await self._merge_config()
            except Exception:
                pass
            
            # 使用subconverter转换
            logger.info("使用subconverter转换配置格式")
            if await self._convert_with_subconverter():
                return await self._merge_config()
            
            logger.error("配置处理失败")
            return False
            
        except Exception as e:
            logger.error(f"处理订阅失败: {e}")
            return False
    
    def _is_clash_format(self, content: str) -> bool:
        """检查是否是标准Clash格式"""
        try:
            # 简单检查：包含必要的字段
            lines = content.strip().split('\n')
            has_proxies = any('proxies:' in line for line in lines)
            has_proxy_groups = any('proxy-groups:' in line for line in lines)
            has_rules = any('rules:' in line for line in lines)
            
            return has_proxies and has_proxy_groups and has_rules
            
        except Exception:
            return False
    
    async def _convert_with_subconverter(self) -> bool:
        """使用subconverter转换配置"""
        try:
            # 确定subconverter路径
            import platform
            arch = platform.machine().lower()
            
            if arch in ('x86_64', 'amd64'):
                subconverter = "subconverter"
            elif arch in ('aarch64', 'arm64'):
                subconverter = "subconverter_arm64"
            else:
                subconverter = "subconverter"
            
            subconverter_path = Path.cwd() / "tools" / "subconverter" / subconverter
            
            if not subconverter_path.exists():
                logger.error(f"subconverter不存在: {subconverter_path}")
                return False
            
            # 确保有执行权限
            subconverter_path.chmod(0o755)
            
            # 运行subconverter
            cmd = [str(subconverter_path), "-g"]
            
            # 重定向输出到日志
            log_file = self.config.logs_dir / "subconverter.log"
            
            with open(log_file, 'w') as f:
                result = subprocess.run(
                    cmd,
                    cwd=subconverter_path.parent,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    timeout=60
                )
            
            if result.returncode == 0:
                logger.info("subconverter转换成功")
                return True
            else:
                logger.error("subconverter转换失败")
                return False
                
        except Exception as e:
            logger.error(f"subconverter转换异常: {e}")
            return False
    
    async def _merge_config(self) -> bool:
        """合并配置文件"""
        try:
            # 读取处理后的配置
            processed_file = self.config.temp_dir / "clash_config.yaml"
            if not processed_file.exists():
                logger.error("处理后的配置文件不存在")
                return False
            
            processed_config = yaml.safe_load(processed_file.read_text())
            
            # 提取代理相关配置
            proxy_config = {}
            for key in ['proxies', 'proxy-groups', 'rules']:
                if key in processed_config:
                    proxy_config[key] = processed_config[key]
            
            # 读取模板配置
            template_file = self.config.temp_dir / "templete_config.yaml"
            if not template_file.exists():
                # 创建默认模板
                await self._create_default_template()
            
            template_config = yaml.safe_load(template_file.read_text())
            
            # 合并配置
            final_config = {**template_config, **proxy_config}
            
            # 更新端口和密钥配置
            final_config.update({
                'port': self.config.proxy.http_port,
                'socks-port': self.config.proxy.socks_port,
                'redir-port': self.config.proxy.redir_port,
                'external-controller': f'0.0.0.0:{self.config.proxy.api_port}',
                'allow-lan': self.config.allow_lan,
                'mode': self.config.mode,
                'log-level': self.config.log_level,
            })
            
            # 设置Secret
            secret = self.config.secret
            if secret is None:
                # 不再生成随机secret，使用空字符串以避免认证不匹配
                secret = ''
            final_config['secret'] = secret
            
            # 设置Dashboard路径
            if self.config.dashboard_enabled:
                dashboard_path = PROJECT_ROOT / "dashboard"
                if dashboard_path.exists():
                    final_config['external-ui'] = str(dashboard_path)
            
            # 保存最终配置
            final_file = self.config.get_config_file_path()
            with open(final_file, 'w', encoding='utf-8') as f:
                yaml.dump(final_config, f, default_flow_style=False, allow_unicode=True)
            
            logger.info("配置文件合并完成")
            return True
            
        except Exception as e:
            logger.error(f"合并配置失败: {e}")
            return False
    
    async def _create_default_template(self) -> None:
        """创建默认配置模板"""
        template_content = f"""# HTTP 代理端口
port: {self.config.proxy.http_port}

# SOCKS5 代理端口
socks-port: {self.config.proxy.socks_port}

# Linux 和 macOS 的 redir 代理端口
redir-port: {self.config.proxy.redir_port}

# 允许局域网的连接
allow-lan: {str(self.config.allow_lan).lower()}

# 规则模式：Rule（规则） / Global（全局代理）/ Direct（全局直连）
mode: {self.config.mode}

# 设置日志输出级别
log-level: {self.config.log_level}

# Clash 的 RESTful API
external-controller: '0.0.0.0:{self.config.proxy.api_port}'

# RESTful API 的口令
secret: ''
"""
        
        template_file = self.config.temp_dir / "templete_config.yaml"
        template_file.write_text(template_content) 