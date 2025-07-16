#!/bin/bash

# Clash for Linux 安装脚本
# 用于设置统一管理命令和环境

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 获取脚本目录
SCRIPT_DIR=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd)
CLASH_SCRIPT="$SCRIPT_DIR/clash"

echo "==================== Clash for Linux 安装向导 ===================="
log_info "当前目录: $SCRIPT_DIR"

# 检查clash脚本是否存在
if [ ! -f "$CLASH_SCRIPT" ]; then
    log_error "未找到 clash 管理脚本"
    exit 1
fi

# 确保clash脚本有执行权限
chmod +x "$CLASH_SCRIPT"
log_info "已设置 clash 脚本执行权限"

# 选择安装方式
echo ""
echo "请选择安装方式:"
echo "1) 创建全局命令  - 在 /usr/local/bin 创建软链接"
echo "2) 仅在当前目录使用 - 使用 ./clash 命令"
echo "3) 添加到 PATH - 将当前目录添加到 PATH 环境变量"
echo ""
read -p "请选择 (1-3): " choice

case $choice in
    1)
        # 创建全局软链接
        log_info "正在创建全局命令..."
        
        if [ -L "/usr/local/bin/clash" ]; then
            log_warn "发现已存在的 clash 命令，正在备份..."
            sudo mv "/usr/local/bin/clash" "/usr/local/bin/clash.bak.$(date +%Y%m%d_%H%M%S)"
        fi
        
        if sudo ln -sf "$CLASH_SCRIPT" "/usr/local/bin/clash"; then
            log_info "全局命令创建成功！"
            log_info "现在可以在任何位置使用 'clash' 命令"
            
            # 测试命令
            if command -v clash &> /dev/null; then
                log_info "命令测试成功"
                echo ""
                echo "使用示例:"
                echo "  clash help     # 查看帮助"
                echo "  clash config   # 配置订阅地址"
                echo "  clash start    # 启动服务"
            else
                log_warn "命令测试失败，可能需要重新加载 PATH"
                log_info "请执行: hash -r 或重新打开终端"
            fi
        else
            log_error "创建全局命令失败，可能需要 sudo 权限"
            exit 1
        fi
        ;;
        
    2)
        # 仅在当前目录使用
        log_info "已配置为当前目录使用"
        echo ""
        echo "使用方法:"
        echo "  ./clash help     # 查看帮助"
        echo "  ./clash config   # 配置订阅地址"
        echo "  ./clash start    # 启动服务"
        ;;
        
    3)
        # 添加到PATH
        log_info "正在添加到 PATH 环境变量..."
        
        # 检查是否已在PATH中
        if echo "$PATH" | grep -q "$SCRIPT_DIR"; then
            log_warn "当前目录已在 PATH 中"
        else
            # 检测当前使用的 shell 并添加到相应配置文件
            current_shell=$(basename "$SHELL")
            
            case "$current_shell" in
                "zsh")
                    # 添加到 .zshrc
                    echo "" >> ~/.zshrc
                    echo "# Clash for Linux PATH" >> ~/.zshrc
                    echo "export PATH=\"$SCRIPT_DIR:\$PATH\"" >> ~/.zshrc
                    log_info "已添加到 ~/.zshrc (zsh)"
                    ;;
                "bash")
                    # 添加到 .bashrc
                    echo "" >> ~/.bashrc
                    echo "# Clash for Linux PATH" >> ~/.bashrc
                    echo "export PATH=\"$SCRIPT_DIR:\$PATH\"" >> ~/.bashrc
                    log_info "已添加到 ~/.bashrc (bash)"
                    ;;
                *)
                    # 默认添加到 .bashrc 和 .zshrc
                    echo "" >> ~/.bashrc
                    echo "# Clash for Linux PATH" >> ~/.bashrc
                    echo "export PATH=\"$SCRIPT_DIR:\$PATH\"" >> ~/.bashrc
                    
                    if [ -f ~/.zshrc ]; then
                        echo "" >> ~/.zshrc
                        echo "# Clash for Linux PATH" >> ~/.zshrc
                        echo "export PATH=\"$SCRIPT_DIR:\$PATH\"" >> ~/.zshrc
                        log_info "已添加到 ~/.bashrc 和 ~/.zshrc"
                    else
                        log_info "已添加到 ~/.bashrc"
                    fi
                    ;;
            esac
            
            # 添加到当前会话
            export PATH="$SCRIPT_DIR:$PATH"
            log_info "已添加到当前会话 PATH"
        fi
        
        echo ""
        echo "使用方法:"
        echo "  clash help     # 查看帮助"
        echo "  clash config   # 配置订阅地址"
        echo "  clash start    # 启动服务"
        echo ""
        log_info "注意: 新终端会话需要重新加载配置文件或重新登录"
        ;;
        
    *)
        log_error "无效选择"
        exit 1
        ;;
esac

echo ""
echo "==================== 依赖检查 ===================="

# 检查必需依赖
missing_deps=()
for cmd in curl wget; do
    if ! command -v $cmd &> /dev/null; then
        missing_deps+=($cmd)
    fi
done

if [ ${#missing_deps[@]} -ne 0 ]; then
    log_error "缺少必需的依赖: ${missing_deps[*]}"
    echo ""
    echo "安装方法:"
    echo "  Ubuntu/Debian: sudo apt-get install ${missing_deps[*]}"
    echo "  CentOS/RHEL:   sudo yum install ${missing_deps[*]}"
    echo "  Alpine:        sudo apk add ${missing_deps[*]}"
else
    log_info "必需依赖检查通过"
fi

# 检查可选依赖
if ! command -v jq &> /dev/null; then
    log_warn "jq 未安装，延迟测试和节点选择功能将不可用"
    echo ""
    echo "安装 jq (可选):"
    echo "  Ubuntu/Debian: sudo apt-get install jq"
    echo "  CentOS/RHEL:   sudo yum install jq"
    echo "  Alpine:        sudo apk add jq"
else
    log_info "可选依赖 jq 已安装"
fi

echo ""
echo "==================== 安装完成 ===================="
log_info "Clash for Linux 统一管理工具安装完成！"
echo ""
echo "下一步:"
echo "1. 运行配置向导: clash config"
echo "2. 启动服务: clash start"
echo "3. 查看状态: clash status"
echo ""
log_info "更多帮助请运行: clash help"
echo "==================================================" 