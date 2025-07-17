"""
Process management for Clash service
"""

import os
import signal
import subprocess
import psutil
from pathlib import Path
from typing import Optional
from loguru import logger

from ..models.config import ClashConfig


class ProcessManager:
    """简化的进程管理器"""
    
    def __init__(self, config: ClashConfig):
        self.config = config
        
    def is_clash_running(self) -> Optional[int]:
        """检查Clash是否运行，返回PID或None"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and 'clash' in proc.info['name'].lower():
                        cmdline = proc.info['cmdline'] or []
                        if any('clash-linux' in cmd for cmd in cmdline):
                            return proc.info['pid']
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return None
        except Exception as e:
            logger.debug(f"检查进程失败: {e}")
            return None
    
    async def start_clash(self) -> bool:
        """启动Clash进程"""
        try:
            # 检查是否已运行
            if self.is_clash_running():
                logger.warning("Clash进程已在运行")
                return True
            
            # 检查二进制文件
            binary_path = self.config.get_clash_binary_path()
            if not binary_path.exists():
                logger.error(f"Clash二进制文件不存在: {binary_path}")
                return False
            
            # 确保有执行权限
            binary_path.chmod(0o755)
            
            # 检查配置文件
            config_file = self.config.get_config_file_path()
            if not config_file.exists():
                logger.error(f"配置文件不存在: {config_file}")
                return False
            
            # 启动进程
            cmd = [
                str(binary_path),
                "-d", str(self.config.config_dir),
                "-f", str(config_file)
            ]
            
            # 重定向输出到日志文件
            log_file = self.config.logs_dir / "clash.log"
            
            with open(log_file, 'w') as f:
                proc = subprocess.Popen(
                    cmd,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    start_new_session=True
                )
            
            logger.info(f"Clash进程已启动，PID: {proc.pid}")
            return True
            
        except Exception as e:
            logger.error(f"启动Clash进程失败: {e}")
            return False
    
    async def stop_clash(self) -> bool:
        """停止Clash进程"""
        try:
            pid = self.is_clash_running()
            if not pid:
                logger.info("Clash进程未运行")
                return True
            
            # 尝试优雅关闭
            try:
                os.kill(pid, signal.SIGTERM)
                logger.info(f"已发送SIGTERM信号到进程 {pid}")
                
                # 等待进程结束
                import time
                for _ in range(10):  # 等待最多10秒
                    if not self.is_clash_running():
                        logger.info("Clash进程已停止")
                        return True
                    time.sleep(1)
                
                # 如果还没停止，强制杀死
                logger.warning("进程未响应SIGTERM，使用SIGKILL")
                os.kill(pid, signal.SIGKILL)
                
            except ProcessLookupError:
                logger.info("进程已不存在")
                return True
            except PermissionError:
                logger.error("没有权限终止进程，可能需要sudo")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"停止Clash进程失败: {e}")
            return False 