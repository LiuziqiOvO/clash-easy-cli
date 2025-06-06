#!/bin/bash

# 获取脚本所在目录
SHELL_FOLDER=$(cd "$(dirname "$0")" || exit 1; pwd)

# 设置 http 代理
function proxy_on() {
    export http_proxy=http://127.0.0.1:7890
    export https_proxy=http://127.0.0.1:7890
    export all_proxy=socks5://127.0.0.1:7891
    echo "Clash 代理已开启"
}

# 关闭 http 代理
function proxy_off() {
    unset http_proxy
    unset https_proxy
    unset all_proxy
    echo "Clash 代理已关闭"
}

# 测试代理延迟
function proxy_test() {
    "${SHELL_FOLDER}/clash_latency.sh"
}

# 显示帮助信息
function show_help() {
    echo "Clash 代理控制工具"
    echo "用法:"
    echo "  proxy_on    - 开启代理"
    echo "  proxy_off   - 关闭代理"
    echo "  proxy_test  - 测试所有节点延迟"
}

# 导出函数
export -f proxy_on
export -f proxy_off
export -f proxy_test
export -f show_help 