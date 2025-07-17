"""
Data models for Clash CLI
"""

from .config import ClashConfig, ProxyConfig
from .clash import ProxyInfo, ProxyGroup, ClashStatus

__all__ = [
    "ClashConfig",
    "ProxyConfig", 
    "ProxyInfo",
    "ProxyGroup",
    "ClashStatus",
] 