"""
System proxy management
"""

import os
import subprocess
from pathlib import Path
from typing import Optional
from loguru import logger

from ..models.config import ClashConfig


class ProxyManager:
    """简化的代理管理器"""
    
    def __init__(self, config: ClashConfig):
        self.config = config
        self.status_file = Path.cwd() / ".proxy_status"
        
    def is_proxy_enabled(self) -> bool:
        """检查代理是否开启"""
        # 优先检查状态文件
        if self.status_file.exists():
            try:
                status = self.status_file.read_text().strip()
                return status == "on"
            except Exception:
                pass
        
        # 检查环境变量
        return bool(os.getenv('http_proxy') or os.getenv('HTTP_PROXY'))
    
    async def enable_proxy(self) -> bool:
        """开启系统代理"""
        try:
            proxy_url = f"http://127.0.0.1:{self.config.proxy.http_port}"
            
            # 设置环境变量（当前会话）
            os.environ['http_proxy'] = proxy_url
            os.environ['https_proxy'] = proxy_url
            os.environ['HTTP_PROXY'] = proxy_url
            os.environ['HTTPS_PROXY'] = proxy_url
            
            # 记录状态
            self.status_file.write_text("on")
            
            # 创建系统级代理脚本（如果不存在）
            await self._create_proxy_script()
            
            logger.info("系统代理已开启")
            return True
            
        except Exception as e:
            logger.error(f"开启代理失败: {e}")
            return False
    
    async def disable_proxy(self) -> bool:
        """关闭系统代理"""
        try:
            # 清除环境变量
            for var in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY']:
                if var in os.environ:
                    del os.environ[var]
            
            # 记录状态
            self.status_file.write_text("off")
            
            logger.info("系统代理已关闭")
            return True
            
        except Exception as e:
            logger.error(f"关闭代理失败: {e}")
            return False
    
    async def _create_proxy_script(self) -> None:
        """创建系统级代理脚本"""
        script_path = Path("/etc/profile.d/clash.sh")
        
        try:
            script_content = f'''#!/bin/bash
# Clash代理环境变量设置

proxy_on() {{
    export http_proxy=http://127.0.0.1:{self.config.proxy.http_port}
    export https_proxy=http://127.0.0.1:{self.config.proxy.http_port}
    export HTTP_PROXY=http://127.0.0.1:{self.config.proxy.http_port}
    export HTTPS_PROXY=http://127.0.0.1:{self.config.proxy.http_port}
    echo "代理已开启"
}}

proxy_off() {{
    unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
    echo "代理已关闭"
}}

# 自动加载代理状态
if [ -f "{self.status_file}" ]; then
    status=$(cat "{self.status_file}" 2>/dev/null)
    if [ "$status" = "on" ]; then
        proxy_on > /dev/null
    fi
fi
'''
            
            # 尝试写入系统脚本
            if os.geteuid() == 0:  # 如果是root用户
                script_path.write_text(script_content)
                script_path.chmod(0o755)
            else:
                # 使用sudo写入
                proc = subprocess.Popen(
                    ['sudo', 'tee', str(script_path)],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                proc.communicate(script_content.encode())
                
                subprocess.run(['sudo', 'chmod', '755', str(script_path)], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            logger.debug("代理脚本已创建")
            
        except Exception as e:
            logger.debug(f"创建代理脚本失败: {e}")
    
    async def test_google_latency(self) -> Optional[int]:
        """测试Google连接延迟"""
        import time
        try:
            start_time = time.time()
            
            # 构建curl命令
            cmd = ['curl', '-o', '/dev/null', '-s', '-m', '10', '-w', '%{http_code}']
            
            # 如果代理开启，添加代理参数
            if self.is_proxy_enabled():
                proxy_url = f"http://127.0.0.1:{self.config.proxy.http_port}"
                cmd.extend(['--proxy', proxy_url])
            
            cmd.append('http://www.google.com/generate_204')
            
            # 执行命令
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            end_time = time.time()
            latency = int((end_time - start_time) * 1000)
            
            if result.returncode == 0 and result.stdout.strip() in ['204', '200']:
                return latency
            else:
                return None
                
        except Exception as e:
            logger.debug(f"测试延迟失败: {e}")
            return None 