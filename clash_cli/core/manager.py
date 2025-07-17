"""
Main manager for Clash CLI
"""

import asyncio
from typing import Optional, Dict, Any
from loguru import logger
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm

from ..models.config import ClashConfig
from ..models.clash import ClashStatus
from .config import ConfigManager
from .api import ClashAPIClient
from .proxy import ProxyManager
from .process import ProcessManager
from .subscription import SubscriptionManager

console = Console()


class ClashManager:
    """Clash主管理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        # 初始化组件
        self.config_manager = ConfigManager(config_file)
        self.config = self.config_manager.config
        
        # 初始化其他管理器
        self.process_manager = ProcessManager(self.config)
        self.proxy_manager = ProxyManager(self.config)
        self.subscription_manager = SubscriptionManager(self.config)
        
        # API客户端需要动态获取secret
        self._api_client: Optional[ClashAPIClient] = None
    
    @property
    def api_client(self) -> ClashAPIClient:
        """获取API客户端，动态更新secret"""
        secret = self.config_manager.get_secret()
        if self._api_client is None or self._api_client.secret != secret:
            base_url = f"http://127.0.0.1:{self.config.proxy.api_port}"
            self._api_client = ClashAPIClient(base_url, secret)
        return self._api_client
    
    async def start(self) -> bool:
        """启动Clash服务"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            try:
                # 检查是否已运行
                if self.process_manager.is_clash_running():
                    console.print("[yellow]Clash 服务已在运行中[/yellow]")
                    return True
                
                # 检查配置
                task = progress.add_task("检查配置...", total=None)
                if not self.config.subscription_url and not self.config.skip_subscription_check:
                    progress.stop()
                    console.print("[red]未配置订阅地址，请先运行 'clash-cli config'[/red]")
                    return False
                
                # 处理订阅
                if not self.config.skip_subscription_check and self.config.subscription_url:
                    progress.update(task, description="下载订阅配置...")
                    if not await self.subscription_manager.download_subscription(str(self.config.subscription_url)):
                        progress.stop()
                        console.print("[red]下载订阅配置失败[/red]")
                        return False
                    
                    progress.update(task, description="处理订阅配置...")
                    if not await self.subscription_manager.process_subscription():
                        progress.stop()
                        console.print("[red]处理订阅配置失败[/red]")
                        return False
                
                # 启动Clash服务
                progress.update(task, description="启动Clash服务...")
                if not await self.process_manager.start_clash():
                    progress.stop()
                    console.print("[red]启动Clash服务失败[/red]")
                    return False
                
                # 等待API可用
                progress.update(task, description="等待API启动...")
                for _ in range(30):  # 等待最多30秒
                    if await self.api_client.is_api_available():
                        break
                    await asyncio.sleep(1)
                else:
                    progress.stop()
                    console.print("[yellow]警告: Clash API未响应，但服务可能已启动[/yellow]")
                
                # 开启系统代理（如果配置了自动开启）
                if self.config.auto_start_proxy:
                    progress.update(task, description="开启系统代理...")
                    await self.proxy_manager.enable_proxy()
                
                progress.stop()
                console.print("[green]✓ Clash 启动成功[/green]")
                
                # 显示当前代理信息
                await self._show_proxy_info()
                
                return True
                
            except Exception as e:
                progress.stop()
                logger.error(f"启动失败: {e}")
                console.print(f"[red]✗ 启动失败: {e}[/red]")
                return False
    
    async def stop(self) -> bool:
        """停止Clash服务"""
        try:
            # 关闭系统代理
            if self.proxy_manager.is_proxy_enabled():
                await self.proxy_manager.disable_proxy()
                console.print("[green]✓ 系统代理已关闭[/green]")
            
            # 停止Clash进程
            if await self.process_manager.stop_clash():
                console.print("[green]✓ Clash 服务已停止[/green]")
                return True
            else:
                console.print("[red]✗ 停止Clash服务失败[/red]")
                return False
                
        except Exception as e:
            logger.error(f"停止失败: {e}")
            console.print(f"[red]✗ 停止失败: {e}[/red]")
            return False
    
    async def restart(self) -> bool:
        """重启Clash服务"""
        console.print("[blue]正在重启Clash服务...[/blue]")
        
        if await self.stop():
            await asyncio.sleep(2)  # 等待2秒
            return await self.start()
        
        return False
    
    async def get_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        status = {
            "服务状态": "未运行",
            "API状态": "不可用", 
            "系统代理": "未开启",
            "当前节点": "未知",
            "Google延迟": "未测试"
        }
        
        try:
            # 检查进程状态
            pid = self.process_manager.is_clash_running()
            if pid:
                status["服务状态"] = f"运行中 (PID: {pid})"
                
                # 检查API状态
                if await self.api_client.is_api_available():
                    status["API状态"] = "可用"
                    
                    # 获取当前代理
                    current_proxy = await self.api_client.get_current_proxy()
                    if current_proxy:
                        status["当前节点"] = current_proxy
            
            # 检查系统代理状态
            if self.proxy_manager.is_proxy_enabled():
                status["系统代理"] = "已开启"
                
                # 测试Google延迟
                latency = await self.proxy_manager.test_google_latency()
                if latency:
                    status["Google延迟"] = f"{latency}ms"
            
        except Exception as e:
            logger.debug(f"获取状态失败: {e}")
        
        return status
    
    async def toggle_proxy(self) -> None:
        """智能切换代理状态"""
        try:
            # 检查服务是否运行
            if not self.process_manager.is_clash_running():
                console.print("[red]✗ Clash服务未运行，请先执行 'clash-cli start'[/red]")
                return
            
            # 切换代理状态
            if self.proxy_manager.is_proxy_enabled():
                # 关闭代理
                if await self.proxy_manager.disable_proxy():
                    console.print("[green]✓ 系统代理已关闭[/green]")
            else:
                # 开启代理
                if await self.proxy_manager.enable_proxy():
                    console.print("[green]✓ 系统代理已开启[/green]")
                    await self._show_proxy_info()
        
        except Exception as e:
            logger.error(f"切换代理失败: {e}")
            console.print(f"[red]✗ 切换代理失败: {e}[/red]")
    
    async def config_wizard(self) -> bool:
        """配置向导"""
        console.print("[blue]Clash 配置向导[/blue]")
        console.print()
        
        try:
            # 检查现有配置
            current_url = None
            if self.config.subscription_url:
                current_url = str(self.config.subscription_url)
                console.print(f"当前订阅地址: {current_url}")
                
                if not Confirm.ask("是否要更改订阅地址?", default=False):
                    console.print("[green]保持现有配置[/green]")
                    return True
            
            # 输入新的订阅地址
            console.print()
            console.print("请输入 Clash 订阅地址:")
            console.print("[dim]注意: 请确保订阅地址有效且可访问[/dim]")
            
            new_url = Prompt.ask("订阅地址", default=current_url or "")
            
            if not new_url:
                console.print("[red]订阅地址不能为空[/red]")
                return False
            
            # 验证订阅地址
            console.print("正在验证订阅地址...")
            
            if await self.subscription_manager.download_subscription(new_url):
                console.print("[green]✓ 订阅地址验证成功[/green]")
                
                # 保存配置
                if self.config_manager.save_env_config(new_url):
                    console.print("[green]✓ 配置已保存[/green]")
                    
                    # 重新加载配置
                    self.config_manager.load_config()
                    self.config = self.config_manager.config
                    
                    return True
                else:
                    console.print("[red]✗ 保存配置失败[/red]")
                    return False
            else:
                console.print("[red]✗ 订阅地址验证失败[/red]")
                return False
                
        except KeyboardInterrupt:
            console.print("\n[yellow]配置向导已取消[/yellow]")
            return False
        except Exception as e:
            logger.error(f"配置向导失败: {e}")
            console.print(f"[red]✗ 配置向导失败: {e}[/red]")
            return False
    
    async def test_latency(self) -> None:
        """测试节点延迟"""
        try:
            if not await self.api_client.is_api_available():
                console.print("[red]✗ Clash API不可用[/red]")
                return
            
            console.print("[blue]正在测试节点延迟...[/blue]")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("测试延迟...", total=None)
                results = await self.api_client.test_all_delays()
            
            if not results:
                console.print("[yellow]没有找到可测试的节点[/yellow]")
                return
            
            # 显示结果
            from rich.table import Table
            
            table = Table(title="节点延迟测试结果")
            table.add_column("节点名称", style="cyan", no_wrap=True)
            table.add_column("延迟", style="green")
            table.add_column("状态", style="yellow")
            
            for result in results:
                delay_str = f"{result.delay}ms" if result.success else "超时"
                status = "✓" if result.success else "✗"
                table.add_row(result.proxy_name, delay_str, status)
            
            console.print(table)
            
        except Exception as e:
            logger.error(f"延迟测试失败: {e}")
            console.print(f"[red]✗ 延迟测试失败: {e}[/red]")
    
    async def _show_proxy_info(self) -> None:
        """显示代理信息"""
        try:
            if not await self.api_client.is_api_available():
                return
            
            current_proxy = await self.api_client.get_current_proxy()
            latency = await self.proxy_manager.test_google_latency()
            
            if current_proxy:
                latency_str = f"{latency}ms" if latency else "超时"
                console.print(f"📡 当前节点: {current_proxy} | 延迟: {latency_str}")
            
        except Exception as e:
            logger.debug(f"显示代理信息失败: {e}") 