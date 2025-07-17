"""
Command Line Interface for Clash CLI
"""

import click
import asyncio
from rich.console import Console
from rich.table import Table
from loguru import logger

from .core.manager import ClashManager

console = Console()


@click.group(invoke_without_command=True)
@click.option('--config', '-c', help='配置文件路径')
@click.pass_context
def cli(ctx, config):
    """Clash 代理管理工具 - Python版本"""
    
    # 配置日志
    logger.remove()  # 移除默认处理器
    logger.add(
        lambda msg: None,  # 静默输出，只在debug时显示
        level="INFO"
    )
    
    ctx.ensure_object(dict)
    ctx.obj['manager'] = ClashManager(config_file=config)
    
    # 如果没有子命令，执行toggle功能
    if ctx.invoked_subcommand is None:
        asyncio.run(ctx.obj['manager'].toggle_proxy())


@cli.command()
@click.pass_context
def start(ctx):
    """启动Clash服务并开启代理"""
    manager = ctx.obj['manager']
    asyncio.run(manager.start())


@cli.command()
@click.pass_context
def stop(ctx):
    """停止Clash服务并关闭代理"""
    manager = ctx.obj['manager']
    asyncio.run(manager.stop())


@cli.command()
@click.pass_context  
def restart(ctx):
    """重启Clash服务"""
    manager = ctx.obj['manager']
    asyncio.run(manager.restart())


@cli.command()
@click.pass_context
def status(ctx):
    """查看运行状态"""
    manager = ctx.obj['manager']
    status_info = asyncio.run(manager.get_status())
    
    # 使用Rich创建美观的表格
    table = Table(title="Clash 运行状态")
    table.add_column("项目", style="cyan", no_wrap=True)
    table.add_column("状态", style="green")
    
    for key, value in status_info.items():
        table.add_row(key, str(value))
    
    console.print(table)


@cli.command()
@click.pass_context
def config(ctx):
    """配置向导"""
    manager = ctx.obj['manager']
    asyncio.run(manager.config_wizard())


@cli.command()
@click.pass_context
def test(ctx):
    """测试所有节点延迟"""
    manager = ctx.obj['manager']
    asyncio.run(manager.test_latency())


@cli.command()
@click.pass_context
def on(ctx):
    """开启系统代理"""
    manager = ctx.obj['manager']
    
    async def enable_proxy():
        if await manager.proxy_manager.enable_proxy():
            console.print("[green]✓ 系统代理已开启[/green]")
            await manager._show_proxy_info()
        else:
            console.print("[red]✗ 开启系统代理失败[/red]")
    
    asyncio.run(enable_proxy())


@cli.command()
@click.pass_context
def off(ctx):
    """关闭系统代理"""
    manager = ctx.obj['manager']
    
    async def disable_proxy():
        if await manager.proxy_manager.disable_proxy():
            console.print("[green]✓ 系统代理已关闭[/green]")
        else:
            console.print("[red]✗ 关闭系统代理失败[/red]")
    
    asyncio.run(disable_proxy())


@cli.command()
@click.pass_context
def select(ctx):
    """选择代理节点"""
    console.print("[yellow]节点选择功能暂未实现[/yellow]")
    console.print("[dim]可以使用 Web Dashboard 进行节点选择[/dim]")
    console.print(f"[dim]访问: http://localhost:9090/ui[/dim]")


if __name__ == '__main__':
    cli() 