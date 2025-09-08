#!/usr/bin/env python
# coding=utf-8
'''
Author       : lzq 1021578619@qq.com
Date         : 2025-07-16 17:28:52
LastEditors  :  lzq 1021578619@qq.com
LastEditTime : 2025-09-08 17:01:27
FilePath     : /clash-easy-cli/clash_cli/main.py
Description  : 
'''
"""
Main entry point for Clash CLI
"""

from .cli import cli


def main():
    """Main entry point"""
    cli()


if __name__ == '__main__':
    main() 