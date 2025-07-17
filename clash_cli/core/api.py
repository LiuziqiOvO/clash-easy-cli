"""
Clash API client for interacting with Clash RESTful API
"""

import httpx
import asyncio
from typing import Optional, Dict, List, Any
from loguru import logger

from ..models.clash import (
    ProxyInfo, 
    ProxyGroup, 
    ClashStatus, 
    DelayTestResult,
    ConfigInfo,
    ProxyType
)


class ClashAPIClient:
    """Clash API客户端"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:9090", secret: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.secret = secret
        self.timeout = httpx.Timeout(10.0, connect=5.0)
        
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {"Content-Type": "application/json"}
        if self.secret:
            headers["Authorization"] = f"Bearer {self.secret}"
        return headers
    
    async def is_api_available(self) -> bool:
        """检查API是否可用"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/",
                    headers=self._get_headers()
                )
                return response.status_code == 200
        except Exception as e:
            logger.debug(f"API不可用: {e}")
            return False
    
    async def get_proxies(self) -> Dict[str, ProxyInfo]:
        """获取所有代理节点信息"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/proxies",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                
                data = response.json()
                proxies = {}
                
                for name, proxy_data in data.get("proxies", {}).items():
                    try:
                        proxy_info = ProxyInfo(
                            name=name,
                            type=ProxyType(proxy_data.get("type", "Unknown")),
                            alive=proxy_data.get("alive", True),
                            delay=proxy_data.get("delay", 0) if proxy_data.get("delay") else None,
                            history=proxy_data.get("history", []),
                            all=proxy_data.get("all"),
                            now=proxy_data.get("now")
                        )
                        proxies[name] = proxy_info
                    except Exception as e:
                        logger.debug(f"解析代理信息失败 {name}: {e}")
                        continue
                
                return proxies
                
        except Exception as e:
            logger.error(f"获取代理列表失败: {e}")
            return {}
    
    async def get_proxy_groups(self) -> List[ProxyGroup]:
        """获取代理组信息"""
        proxies = await self.get_proxies()
        groups = []
        
        for name, proxy in proxies.items():
            if proxy.type in [ProxyType.SELECTOR, ProxyType.URL_TEST, ProxyType.FALLBACK, ProxyType.LOAD_BALANCE]:
                group = ProxyGroup(
                    name=name,
                    type=proxy.type,
                    proxies=proxy.all or [],
                    current=proxy.now
                )
                groups.append(group)
        
        return groups
    
    async def set_proxy(self, group: str, proxy: str) -> bool:
        """设置代理组的当前代理"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.put(
                    f"{self.base_url}/proxies/{group}",
                    json={"name": proxy},
                    headers=self._get_headers()
                )
                return response.status_code == 204
                
        except Exception as e:
            logger.error(f"设置代理失败: {e}")
            return False
    
    async def test_delay(self, proxy: str, url: str = "http://www.gstatic.com/generate_204", timeout: int = 5000) -> DelayTestResult:
        """测试单个代理的延迟"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/proxies/{proxy}/delay",
                    params={"timeout": str(timeout), "url": url},
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    delay = data.get("delay", -1)
                    return DelayTestResult(
                        proxy_name=proxy,
                        delay=delay,
                        success=delay > 0,
                        error=None
                    )
                else:
                    return DelayTestResult(
                        proxy_name=proxy,
                        delay=-1,
                        success=False,
                        error=f"HTTP {response.status_code}"
                    )
                    
        except Exception as e:
            logger.debug(f"测试延迟失败 {proxy}: {e}")
            return DelayTestResult(
                proxy_name=proxy,
                delay=-1,
                success=False,
                error=str(e)
            )
    
    async def test_all_delays(self, url: str = "http://www.gstatic.com/generate_204", timeout: int = 5000) -> List[DelayTestResult]:
        """测试所有代理的延迟"""
        proxies = await self.get_proxies()
        
        # 过滤出真实的代理节点（排除代理组和特殊类型）
        real_proxies = [
            name for name, proxy in proxies.items()
            if proxy.type not in [ProxyType.DIRECT, ProxyType.REJECT, ProxyType.SELECTOR, ProxyType.URL_TEST, ProxyType.FALLBACK, ProxyType.LOAD_BALANCE]
        ]
        
        # 并发测试延迟
        tasks = [
            self.test_delay(proxy, url, timeout)
            for proxy in real_proxies
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        delay_results = []
        for result in results:
            if isinstance(result, DelayTestResult):
                delay_results.append(result)
            elif isinstance(result, Exception):
                logger.debug(f"延迟测试异常: {result}")
        
        # 按延迟排序
        delay_results.sort(key=lambda x: x.delay if x.success else 999999)
        
        return delay_results
    
    async def get_config(self) -> Optional[ConfigInfo]:
        """获取当前配置信息"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/configs",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                
                data = response.json()
                return ConfigInfo(
                    port=data.get("port", 7890),
                    socks_port=data.get("socks-port", 7891),
                    redir_port=data.get("redir-port", 7892),
                    allow_lan=data.get("allow-lan", True),
                    mode=data.get("mode", "rule"),
                    log_level=data.get("log-level", "info")
                )
                
        except Exception as e:
            logger.error(f"获取配置信息失败: {e}")
            return None
    
    async def set_mode(self, mode: str) -> bool:
        """设置代理模式"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.patch(
                    f"{self.base_url}/configs",
                    json={"mode": mode},
                    headers=self._get_headers()
                )
                return response.status_code == 204
                
        except Exception as e:
            logger.error(f"设置模式失败: {e}")
            return False
    
    async def get_current_proxy(self) -> Optional[str]:
        """获取当前活跃的代理节点"""
        try:
            proxies = await self.get_proxies()
            
            # 查找主选择器（优先匹配"节点选择"或"GLOBAL"）
            main_selector = None
            for name, proxy in proxies.items():
                if proxy.type == ProxyType.SELECTOR and ("节点选择" in name or "GLOBAL" in name.upper()):
                    main_selector = name
                    break
            
            # 如果没找到，使用第一个选择器
            if not main_selector:
                for name, proxy in proxies.items():
                    if proxy.type == ProxyType.SELECTOR:
                        main_selector = name
                        break
            
            if not main_selector:
                return None
            
            # 获取主选择器当前选择的代理
            current_proxy_name = proxies[main_selector].now
            if not current_proxy_name:
                return None
            
            # 如果当前代理是URLTest类型，获取其实际选择的节点
            if current_proxy_name in proxies:
                current_proxy = proxies[current_proxy_name]
                if current_proxy.type == ProxyType.URL_TEST and current_proxy.now:
                    return current_proxy.now
            
            return current_proxy_name
            
        except Exception as e:
            logger.debug(f"获取当前代理失败: {e}")
            return None 