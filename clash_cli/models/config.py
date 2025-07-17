"""
Configuration data models for Clash CLI
"""

from pydantic import BaseModel, Field, HttpUrl, validator
from typing import Optional, Dict, Any, List
from pathlib import Path
import os


class ProxyConfig(BaseModel):
    """代理端口配置"""
    http_port: int = Field(default=7890, ge=1, le=65535)
    socks_port: int = Field(default=7891, ge=1, le=65535)
    redir_port: int = Field(default=7892, ge=1, le=65535)
    api_port: int = Field(default=9090, ge=1, le=65535)


class ClashConfig(BaseModel):
    """Clash主配置"""
    # 订阅配置
    subscription_url: Optional[HttpUrl] = None
    secret: Optional[str] = None
    
    # 代理端口配置
    proxy: ProxyConfig = Field(default_factory=ProxyConfig)
    
    # 服务配置
    allow_lan: bool = True
    log_level: str = Field(default="info", pattern="^(silent|error|warning|info|debug)$")
    mode: str = Field(default="rule", pattern="^(rule|global|direct)$")
    
    # 路径配置
    config_dir: Path = Field(default_factory=lambda: Path.cwd() / "conf")
    temp_dir: Path = Field(default_factory=lambda: Path.cwd() / "temp")
    bin_dir: Path = Field(default_factory=lambda: Path.cwd() / "bin")
    logs_dir: Path = Field(default_factory=lambda: Path.cwd() / "logs")
    
    # 运行时配置
    skip_subscription_check: bool = False
    auto_start_proxy: bool = True
    
    # 高级配置
    clash_binary_name: Optional[str] = None
    dashboard_enabled: bool = True
    external_ui_path: Optional[Path] = None
    
    @validator('config_dir', 'temp_dir', 'bin_dir', 'logs_dir', 'external_ui_path', pre=True)
    def validate_paths(cls, v):
        """验证路径并转换为Path对象"""
        if v is None:
            return v
        return Path(v).expanduser().resolve()
    
    @validator('clash_binary_name', always=True)
    def set_clash_binary_name(cls, v, values):
        """根据系统架构自动设置Clash二进制文件名"""
        if v is not None:
            return v
        
        import platform
        arch = platform.machine().lower()
        
        if arch in ('x86_64', 'amd64'):
            return 'clash-linux-amd64'
        elif arch in ('aarch64', 'arm64'):
            return 'clash-linux-arm64'
        elif arch.startswith('arm'):
            return 'clash-linux-armv7'
        else:
            return 'clash-linux-amd64'  # 默认
    
    def get_clash_binary_path(self) -> Path:
        """获取Clash二进制文件的完整路径"""
        return self.bin_dir / self.clash_binary_name
    
    def get_config_file_path(self) -> Path:
        """获取Clash配置文件路径"""
        return self.config_dir / "config.yaml"
    
    def get_env_file_path(self) -> Path:
        """获取环境变量文件路径"""
        return Path.cwd() / ".env"
    
    def ensure_directories(self) -> None:
        """确保所有必要的目录存在"""
        for dir_path in [self.config_dir, self.temp_dir, self.logs_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    class Config:
        # 允许任意类型，因为Path可能不是标准的pydantic类型
        arbitrary_types_allowed = True 