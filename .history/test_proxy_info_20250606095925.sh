#!/bin/bash

# 设置脚本目录
SCRIPT_DIR="/home/liuziqi/lzq/Tool/clash-for-linux-backup"

# 日志函数
log_info() {
    echo -e "\033[32m[INFO]\033[0m $1"
}

log_warn() {
    echo -e "\033[33m[WARN]\033[0m $1"
}

log_error() {
    echo -e "\033[31m[ERROR]\033[0m $1"
}

# 获取Secret
get_secret() {
    if [ -f "$SCRIPT_DIR/.env" ]; then
        source "$SCRIPT_DIR/.env"
        if [ -n "$CLASH_SECRET" ]; then
            echo "$CLASH_SECRET"
        else
            # 从配置文件中读取
            if [ -f "$SCRIPT_DIR/conf/config.yaml" ]; then
                grep "^secret:" "$SCRIPT_DIR/conf/config.yaml" | awk '{print $2}' | tr -d "'"
            fi
        fi
    fi
}

# 检查Clash API是否可用
check_clash_api() {
    local secret=$(get_secret)
    local headers=()
    if [ -n "$secret" ]; then
        headers=(-H "Authorization: Bearer $secret")
    fi
    
    if curl -s -m 3 "${headers[@]}" "http://127.0.0.1:9090" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# 获取当前代理节点信息
get_current_proxy() {
    local secret=$(get_secret)
    local headers=()
    if [ -n "$secret" ]; then
        headers=(-H "Authorization: Bearer $secret")
    fi
    
    # 获取所有代理信息
    local proxies_info=$(curl -s -m 5 "${headers[@]}" "http://127.0.0.1:9090/proxies" 2>/dev/null)
    
    if [ -n "$proxies_info" ] && command -v jq &> /dev/null; then
        # 首先查找主要的选择器代理组
        local main_selector=$(echo "$proxies_info" | jq -r '
            .proxies | 
            to_entries[] | 
            select(.value.type == "Selector" and (.key | test("节点选择|GLOBAL"))) | 
            .key
        ' 2>/dev/null | head -1)
        
        if [ -n "$main_selector" ] && [ "$main_selector" != "null" ]; then
            local current_proxy=$(echo "$proxies_info" | jq -r ".proxies.\"$main_selector\".now // empty" 2>/dev/null)
            
            # 递归查找实际使用的节点
            local final_proxy="$current_proxy"
            local max_depth=5  # 防止无限递归
            local depth=0
            
            while [ $depth -lt $max_depth ] && [ -n "$final_proxy" ] && [ "$final_proxy" != "null" ]; do
                local proxy_info=$(echo "$proxies_info" | jq -r ".proxies.\"$final_proxy\"" 2>/dev/null)
                
                if [ "$proxy_info" = "null" ] || [ -z "$proxy_info" ]; then
                    break
                fi
                
                local proxy_type=$(echo "$proxy_info" | jq -r '.type // empty' 2>/dev/null)
                local next_proxy=$(echo "$proxy_info" | jq -r '.now // empty' 2>/dev/null)
                
                # 如果是选择器类型且有 now 字段，继续查找
                if [ "$proxy_type" = "Selector" ] && [ -n "$next_proxy" ] && [ "$next_proxy" != "null" ]; then
                    final_proxy="$next_proxy"
                    depth=$((depth + 1))
                else
                    break
                fi
            done
            
            if [ -n "$final_proxy" ] && [ "$final_proxy" != "null" ]; then
                echo "$final_proxy"
            else
                echo "未知节点"
            fi
        else
            echo "未知节点"
        fi
    else
        echo "未知节点"
    fi
}

# 测试 Google 延迟
test_google_latency() {
    local start_time=$(date +%s%3N)
    local http_code
    
    # 通过代理测试 Google 连接
    if [ -n "$http_proxy" ]; then
        http_code=$(curl -o /dev/null -s -m 10 -w "%{http_code}" --proxy "$http_proxy" "http://www.google.com/generate_204" 2>/dev/null)
    else
        http_code=$(curl -o /dev/null -s -m 10 -w "%{http_code}" "http://www.google.com/generate_204" 2>/dev/null)
    fi
    
    local end_time=$(date +%s%3N)
    local latency=$((end_time - start_time))
    
    if [ "$http_code" = "204" ] || [ "$http_code" = "200" ]; then
        echo "${latency}ms"
    else
        echo "超时"
    fi
}

# 显示代理信息
show_proxy_info() {
    if check_clash_api; then
        local current_proxy=$(get_current_proxy)
        local latency=$(test_google_latency)
        
        echo ""
        log_info "当前节点: $current_proxy"
        log_info "Google 延迟: $latency"
        echo ""
    else
        log_error "Clash API 不可用"
    fi
}

# 执行测试
show_proxy_info 