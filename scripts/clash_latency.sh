#!/bin/bash

# 获取脚本所在目录
SHELL_FOLDER=$(cd "$(dirname "$0")" || exit 1; pwd)
# 加载环境变量
source "${SHELL_FOLDER}/../.env"

# Clash API 配置
CLASH_API="http://127.0.0.1:9090"
CLASH_SECRET="${CLASH_SECRET}"

# 检查 curl 是否安装
if ! command -v curl &> /dev/null; then
    echo "错误: curl 未安装，请先安装 curl"
    exit 1
fi

# 检查 jq 是否安装
if ! command -v jq &> /dev/null; then
    echo "错误: jq 未安装，请先安装 jq"
    exit 1
fi

# 检查 Clash 是否运行
if ! curl -s -m 3 "${CLASH_API}" > /dev/null; then
    echo "错误: Clash 未运行或无法访问"
    exit 1
fi

# 构建请求头
HEADERS=()
if [ -n "${CLASH_SECRET}" ]; then
    HEADERS+=(-H "Authorization: Bearer ${CLASH_SECRET}")
fi

echo "正在获取所有代理节点..."
# 获取所有代理节点
PROXIES=$(curl -s "${HEADERS[@]}" "${CLASH_API}/proxies" | jq -r '.proxies | to_entries[] | select(.value.type != "Direct" and .value.type != "Reject" and .value.type != "Selector" and .value.type != "URLTest") | .key')

if [ -z "${PROXIES}" ]; then
    echo "未找到可用的代理节点"
    exit 1
fi

echo "开始测试延迟..."
echo "----------------------------------------"
printf "%-40s %s\n" "节点名称" "延迟"
echo "----------------------------------------"

# 测试每个节点的延迟
while IFS= read -r proxy; do
    # 测试延迟
    RESULT=$(curl -s "${HEADERS[@]}" -X GET "${CLASH_API}/proxies/${proxy}/delay" -G --data-urlencode "timeout=5000" --data-urlencode "url=http://www.gstatic.com/generate_204")
    DELAY=$(echo "${RESULT}" | jq -r '.delay')
    
    if [ "${DELAY}" = "null" ]; then
        printf "%-40s %s\n" "${proxy}" "超时"
    else
        printf "%-40s %dms\n" "${proxy}" "${DELAY}"
    fi
done <<< "${PROXIES}"

echo "----------------------------------------" 