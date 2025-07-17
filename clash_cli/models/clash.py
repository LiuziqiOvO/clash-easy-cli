#!/usr/bin/env python
# coding=utf-8
'''
Author       : lzq 1021578619@qq.com
Date         : 2025-07-16 17:20:38
LastEditors  :  lzq 1021578619@qq.com
LastEditTime : 2025-07-16 17:30:02
FilePath     : /clash-easy-cli/clash_cli/models/clash.py
Description  : 
'''
"""
Clash API data models
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from enum import Enum


class ProxyType(str, Enum):
    """代理类型枚举"""
    DIRECT = "Direct"
    REJECT = "Reject"
    SELECTOR = "Selector"
    URL_TEST = "URLTest"
    FALLBACK = "Fallback"
    LOAD_BALANCE = "LoadBalance"
    SHADOWSOCKS = "Shadowsocks"
    VMESS = "Vmess"
    TROJAN = "Trojan"
    SNELL = "Snell"


class ProxyInfo(BaseModel):
    """代理节点信息"""
    name: str
    type: ProxyType
    alive: bool = True
    delay: Optional[int] = None
    history: List[Dict[str, Any]] = Field(default_factory=list)
    all: Optional[List[str]] = None  # 对于代理组
    now: Optional[str] = None        # 对于代理组当前选择


class ProxyGroup(BaseModel):
    """代理组信息"""
    name: str
    type: ProxyType
    proxies: List[str] = Field(default_factory=list)
    current: Optional[str] = None
    url: Optional[str] = None
    interval: Optional[int] = None


class ClashStatus(BaseModel):
    """Clash运行状态"""
    running: bool = False
    pid: Optional[int] = None
    api_available: bool = False
    proxy_enabled: bool = False
    current_mode: Optional[str] = None
    
    # 端口状态
    http_port_open: bool = False
    socks_port_open: bool = False
    redir_port_open: bool = False
    api_port_open: bool = False
    
    # 当前代理信息
    current_proxy: Optional[str] = None
    current_delay: Optional[int] = None


class DelayTestResult(BaseModel):
    """延迟测试结果"""
    proxy_name: str
    delay: int = -1  # -1表示超时或失败
    success: bool = False
    error: Optional[str] = None


class ConfigInfo(BaseModel):
    """配置信息"""
    port: int
    socks_port: int
    redir_port: int
    allow_lan: bool
    mode: str
    log_level: str 