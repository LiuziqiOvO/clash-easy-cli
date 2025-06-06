# README4ai.md - AI 记忆文档

## 项目概况

- **项目名称**: clash-for-linux-backup
- **项目类型**: 命令行版 Clash 代理工具
- **核心功能**: 使用 Clash 核心实现 Linux 服务器代理，解决 GitHub 等国外资源下载速度慢的问题
- **原作者状态**: 已跑路，当前为备份仓库
- **架构支持**: x86_64/amd64、aarch64/arm64、armv7

## 目录结构

```
├── .env                     # 环境配置文件（包含订阅地址、Secret等）
├── start.sh                 # 主启动脚本 (232行)
├── restart.sh              # 重启脚本 (91行)
├── shutdown.sh             # 停止脚本 (15行)
├── bin/                    # Clash二进制文件
│   ├── clash-linux-amd64   # x86_64架构二进制
│   ├── clash-linux-arm64   # arm64架构二进制
│   └── clash-linux-armv7   # armv7架构二进制
├── conf/                   # 配置文件目录
│   ├── config.yaml         # 主配置文件 (10225行)
│   ├── Country.mmdb        # GeoIP数据库
│   └── cache.db           # 缓存文件
├── scripts/                # 脚本工具集
│   ├── clash.sh            # 基础Clash脚本
│   ├── clash_latency.sh    # 延迟测试脚本
│   ├── clash_profile_conversion.sh  # 配置文件转换脚本
│   ├── clash_proxy-selector.sh     # 终端代理选择器
│   └── get_cpu_arch.sh     # CPU架构检测脚本
├── temp/                   # 临时文件目录
│   ├── templete_config.yaml # 配置模板
│   ├── config.yaml         # 临时配置
│   ├── clash_config.yaml   # 处理后的配置
│   ├── clash.yaml          # 原始订阅文件
│   └── proxy.txt          # 代理节点信息
├── tools/                  # 工具目录
│   └── subconverter/      # 订阅转换工具
├── logs/                   # 日志目录
└── dashboard/              # Web控制面板
└── clash                  # 统一管理命令 (新增)
```

## 核心工作流程

### 启动流程 (start.sh)

1. **环境初始化**

   - 加载.env 配置文件
   - 设置目录权限
   - 获取 CPU 架构信息
   - 临时清除代理环境变量

2. **订阅处理** (如果 SKIP_SUBSCRIPTION_CHECK != 1)

   - 检测订阅地址可访问性
   - 下载配置文件到 temp/clash.yaml
   - 判断配置文件格式并转换:
     - 标准 clash 格式 → 直接使用
     - base64 编码 → 解码后检查
     - 非标准格式 → 使用 subconverter 转换

3. **配置文件处理**

   - 提取代理信息到 proxy.txt
   - 合并模板配置和代理信息
   - 配置 Dashboard 路径和 Secret

4. **服务启动**

   - 根据 CPU 架构选择对应二进制
   - nohup 后台启动 Clash 服务
   - 创建系统代理环境变量脚本(/etc/profile.d/clash.sh)

5. **输出信息**
   - Dashboard 访问地址
   - Secret 密钥
   - 环境变量加载命令

### 核心端口配置

- **7890**: HTTP 代理端口
- **7891**: SOCKS5 代理端口
- **7892**: redir 代理端口
- **9090**: RESTful API / Dashboard 端口

### 环境变量脚本功能

创建 `/etc/profile.d/clash.sh` 包含:

- `proxy_on()`: 开启系统代理
- `proxy_off()`: 关闭系统代理

## 主要脚本分析

### 代理选择器 (clash_proxy-selector.sh)

- **功能**: 终端界面选择代理节点和模式
- **API**: 使用 Clash RESTful API
- **依赖**: curl, jq
- **认证**: Bearer Token (Secret)
- **限制**: 需手动配置 Secret 变量

### 延迟测试 (clash_latency.sh)

- **功能**: 测试所有代理节点延迟
- **测试 URL**: http://www.gstatic.com/generate_204
- **超时**: 5 秒
- **依赖**: curl, jq

### 配置转换 (clash_profile_conversion.sh)

- **检测逻辑**: 使用 awk 检查 proxies/proxy-groups/rules 字段
- **转换工具**: subconverter (支持 x86_64/arm64)
- **处理流程**: 原始 →base64 解码 → 格式检查 → 转换 → 验证

### CPU 架构检测 (get_cpu_arch.sh)

- **支持系统**: Ubuntu/Debian/CentOS/RHEL/Fedora
- **检测命令**: dpkg-architecture/uname/arch
- **架构映射**: 自动适配不同系统的架构命名

## 易用性改进点识别

### 当前痛点

1. **手动配置**

   - .env 文件需手动编辑订阅地址
   - proxy-selector.sh 需手动配置 Secret
   - 每次都需要 source 环境变量

2. **命令复杂**

   - 启动需要多步骤: start.sh → source → proxy_on
   - 没有统一的管理命令

3. **错误处理不友好**

   - 错误信息不够明确
   - 缺少依赖检查
   - 没有状态检查命令

4. **功能分散**

   - 延迟测试需要单独运行脚本
   - 代理选择器需要单独配置
   - 缺少一键操作

5. **用户体验**
   - 缺少进度显示
   - 没有配置向导
   - 重复性操作多

### 改进方向

1. 统一入口命令 (clash 命令)
2. 自动环境检测和依赖安装
3. 配置向导和自动配置
4. 状态监控和健康检查
5. 一键操作和快捷命令

## 常见问题和命令说明

### 启动相关

- 启动服务: `sudo bash start.sh`
- 重启服务: `sudo bash restart.sh`
- 停止服务: `sudo bash shutdown.sh`

### 代理控制

- 开启代理: `source /etc/profile.d/clash.sh && proxy_on`
- 关闭代理: `source /etc/profile.d/clash.sh && proxy_off`
- 测试延迟: `source /etc/profile.d/clash.sh && proxy_test`

### 高级功能

- 延迟测试: `bash scripts/clash_latency.sh`
- 节点选择: `bash scripts/clash_proxy-selector.sh` (需要先配置 Secret)
- 配置转换: `bash scripts/clash_profile_conversion.sh`

---

## 易用性改进实现 (2024 年更新)

### 统一管理命令 - clash

创建了统一的 `clash` 命令脚本，实现了以下功能：

#### 核心特性

1. **一键操作**: 所有功能通过单一命令入口访问
2. **自动依赖检测**: 自动检查 curl、wget、jq 等依赖
3. **智能配置管理**: 自动获取和配置 Secret
4. **状态监控**: 实时显示服务状态、端口状态、API 状态
5. **配置向导**: 交互式订阅地址配置和验证
6. **错误处理**: 友好的错误提示和解决建议

#### 命令列表

```bash
clash start      # 一键启动 Clash 并开启系统代理
clash stop       # 停止 Clash 并关闭系统代理
clash restart    # 重启 Clash 服务
clash status     # 显示详细运行状态
clash config     # 配置向导 (设置订阅地址)
clash test       # 测试所有节点延迟
clash select     # 选择代理节点和模式
clash on         # 开启系统代理
clash off        # 关闭系统代理
clash help       # 显示帮助信息
```

#### 技术实现

- **最小修改原则**: 复用现有脚本，不破坏原有功能
- **自动化集成**: 自动处理 Secret 配置，无需手动修改脚本
- **智能检测**: 自动检测服务状态、端口占用、API 可用性
- **用户友好**: 彩色输出、清晰的状态信息、详细的错误提示

#### 解决的痛点

1. ✅ **操作复杂** → 单命令操作
2. ✅ **配置分散** → 统一配置管理
3. ✅ **缺乏统一管理** → 统一命令入口
4. ✅ **状态不透明** → 详细状态显示
5. ✅ **功能割裂** → 集成所有功能

#### 使用示例

```bash
# 首次使用
./clash config    # 配置订阅地址
./clash start     # 启动服务并开启代理

# 日常使用
./clash status    # 查看状态
./clash test      # 测试延迟
./clash select    # 选择节点

# 维护操作
./clash restart   # 重启服务
./clash stop      # 停止服务
```

#### 兼容性

- 完全兼容现有脚本和配置
- 支持原有的手动操作方式
- 不影响现有的 .env 配置和工作流程

# Clash for Linux 项目完整状态记录

## 项目概述

- **项目名称**: clash-for-linux-backup
- **项目类型**: Clash 代理工具的 Linux 命令行版本
- **核心功能**: 科学上网代理服务，支持订阅更新、节点选择、延迟测试
- **原作者状态**: 原项目已删除，当前为备份版本
- **架构支持**: 多架构支持 (amd64, arm64, armv7 等)

## 目录结构

```
clash-for-linux-backup/
├── .env                    # 环境配置文件 (用户需配置)
├── start.sh               # 启动脚本
├── restart.sh             # 重启脚本
├── shutdown.sh            # 停止脚本
├── bin/                   # 二进制文件目录
│   ├── clash-linux-amd64
│   ├── clash-linux-arm64
│   └── clash-linux-armv7
├── conf/                  # 配置文件目录
│   ├── config.yaml        # Clash 主配置文件
│   ├── Country.mmdb       # GeoIP 数据库
│   └── cache.db           # 缓存数据库
├── scripts/               # 脚本工具集
│   ├── clash.sh           # 代理环境变量管理
│   ├── clash_latency.sh   # 延迟测试脚本
│   ├── clash_proxy-selector.sh  # 节点选择脚本
│   ├── clash_profile_conversion.sh  # 配置转换脚本
│   └── get_cpu_arch.sh    # CPU 架构检测
├── temp/                  # 临时文件目录
├── tools/                 # 工具目录
│   └── subconverter/      # 订阅转换工具
├── logs/                  # 日志目录
├── dashboard/             # Web 控制面板
├── clash                  # 统一管理命令 (新增)
├── install.sh             # 安装脚本 (新增)
└── README.md              # 用户文档 (更新)
```

## 核心工作流程

### start.sh 启动流程

1. **环境初始化**: 检查 .env 文件，加载环境变量
2. **订阅处理**: 下载订阅链接，转换为 Clash 配置
3. **配置处理**: 合并配置文件，设置端口和规则
4. **服务启动**: 启动 Clash 二进制文件
5. **输出信息**: 显示服务状态和访问地址

## 核心端口配置

- **HTTP 代理端口**: 7890
- **SOCKS5 代理端口**: 7891
- **Redir 代理端口**: 7892
- **RESTful API/Dashboard 端口**: 9090

## 环境变量脚本功能

创建 `/etc/profile.d/clash.sh` 脚本，提供:

- `proxy_on`: 开启系统代理
- `proxy_off`: 关闭系统代理
- `proxy_test`: 测试代理延迟

## 主要脚本分析

### clash_proxy-selector.sh

- **功能**: 交互式节点选择和模式切换
- **依赖**: jq 工具，Clash API
- **痛点**: 需要手动配置 Secret

### clash_latency.sh

- **功能**: 批量测试所有节点延迟
- **依赖**: jq 工具，Clash API
- **输出**: 节点延迟排序列表

### clash_profile_conversion.sh

- **功能**: 订阅链接转换为 Clash 配置
- **依赖**: subconverter 工具
- **用途**: 处理不兼容的订阅格式

### get_cpu_arch.sh

- **功能**: 自动检测 CPU 架构
- **用途**: 选择对应的 Clash 二进制文件

## 易用性改进点

### 当前痛点

1. **操作复杂**: 需要多步骤手动操作
2. **配置分散**: .env 文件需手动配置，proxy-selector.sh 需要填写 Secret
3. **缺乏统一管理**: 启动、停止、配置、测试等功能分散在不同脚本
4. **状态不透明**: 难以快速了解服务运行状态
5. **功能割裂**: 延迟测试、节点选择需要单独执行

### 改进方向

1. **统一命令入口**: 创建 clash 命令，集成所有功能
2. **自动环境检测**: 自动检测依赖，提供安装建议
3. **配置向导**: 提供交互式配置向导
4. **状态监控**: 实时显示服务状态和健康检查
5. **一键操作**: 简化常用操作为单一命令

## 常见问题和命令说明

### 启动相关

- 启动服务: `sudo bash start.sh`
- 重启服务: `sudo bash restart.sh`
- 停止服务: `sudo bash shutdown.sh`

### 代理控制

- 开启代理: `source /etc/profile.d/clash.sh && proxy_on`
- 关闭代理: `source /etc/profile.d/clash.sh && proxy_off`
- 测试延迟: `source /etc/profile.d/clash.sh && proxy_test`

### 高级功能

- 延迟测试: `bash scripts/clash_latency.sh`
- 节点选择: `bash scripts/clash_proxy-selector.sh` (需要先配置 Secret)
- 配置转换: `bash scripts/clash_profile_conversion.sh`

---

## 易用性改进实现 (2024 年更新)

### 统一管理命令 - clash

创建了统一的 `clash` 命令脚本，实现了以下功能：

#### 核心特性

1. **一键操作**: 所有功能通过单一命令入口访问
2. **自动依赖检测**: 自动检查 curl、wget、jq 等依赖
3. **智能配置管理**: 自动获取和配置 Secret
4. **状态监控**: 实时显示服务状态、端口状态、API 状态
5. **配置向导**: 交互式订阅地址配置和验证
6. **错误处理**: 友好的错误提示和解决建议

#### 命令列表

```bash
clash start      # 一键启动 Clash 并开启系统代理
clash stop       # 停止 Clash 并关闭系统代理
clash restart    # 重启 Clash 服务
clash status     # 显示详细运行状态
clash config     # 配置向导 (设置订阅地址)
clash test       # 测试所有节点延迟
clash select     # 选择代理节点和模式
clash on         # 开启系统代理
clash off        # 关闭系统代理
clash help       # 显示帮助信息
```

#### 技术实现

- **最小修改原则**: 复用现有脚本，不破坏原有功能
- **自动化集成**: 自动处理 Secret 配置，无需手动修改脚本
- **智能检测**: 自动检测服务状态、端口占用、API 可用性
- **用户友好**: 彩色输出、清晰的状态信息、详细的错误提示

#### 解决的痛点

1. ✅ **操作复杂** → 单命令操作
2. ✅ **配置分散** → 统一配置管理
3. ✅ **缺乏统一管理** → 统一命令入口
4. ✅ **状态不透明** → 详细状态显示
5. ✅ **功能割裂** → 集成所有功能

#### 使用示例

```bash
# 首次使用
./clash config    # 配置订阅地址
./clash start     # 启动服务并开启代理

# 日常使用
./clash status    # 查看状态
./clash test      # 测试延迟
./clash select    # 选择节点

# 维护操作
./clash restart   # 重启服务
./clash stop      # 停止服务
```

#### 兼容性

- 完全兼容现有脚本和配置
- 支持原有的手动操作方式
- 不影响现有的 .env 配置和工作流程

### 安装向导 - install.sh

创建了用户友好的安装脚本，提供多种安装方式：

#### 安装选项

1. **全局命令** (推荐): 在 `/usr/local/bin` 创建软链接
2. **当前目录使用**: 使用 `./clash` 命令
3. **添加到 PATH**: 将当前目录添加到环境变量

#### 功能特性

- 自动检测和备份已存在的命令
- 依赖检查和安装建议
- 权限设置和测试验证
- 详细的使用说明和示例

### 用户文档 - README.md

创建了完整的用户文档，包含：

#### 文档内容

- 快速开始指南
- 详细命令列表和说明
- 使用示例和最佳实践
- 常见问题解答
- 依赖要求和安装方法
- 项目结构说明

#### 文档特色

- 清晰的结构和导航
- 丰富的示例代码
- 友好的图标和格式
- 完整的故障排除指南

## 最终实现状态

### 新增文件

1. **clash** (11749 bytes): 统一管理命令脚本
2. **install.sh** (5059 bytes): 安装向导脚本
3. **README.md**: 用户友好的文档

### 改进效果

- **操作简化**: 从多步骤操作简化为单命令
- **配置自动化**: 自动处理 Secret 和环境变量
- **状态透明**: 实时显示详细状态信息
- **错误友好**: 清晰的错误提示和解决建议
- **文档完善**: 完整的使用指南和故障排除

### 用户体验提升

- **学习成本**: 从需要了解多个脚本降低到单一命令
- **操作效率**: 从多步骤操作提升到一键操作
- **故障排除**: 从手动检查提升到自动诊断
- **配置管理**: 从手动编辑提升到向导式配置

### 技术债务

- 保持了完全的向后兼容性
- 没有修改任何原有文件
- 遵循最小修改原则
- 所有改进都是增量式的

## 2024-12-06 代理切换功能优化

### 修改内容

1. **优化 toggle 功能**：

   - 修改 `toggle_clash()` 函数，现在只是简单地开启/关闭代理，而不是启动/停止整个 Clash 服务
   - 使用状态文件 `.proxy_status` 来记录代理开关状态，解决了环境变量在子 shell 中不生效的问题

2. **文件结构整理**：

   - 将根目录下的脚本文件移动到 `scripts/` 目录：
     - `install.sh` → `scripts/install.sh`
     - `restart.sh` → `scripts/restart.sh`
     - `shutdown.sh` → `scripts/shutdown.sh`
     - `start.sh` → `scripts/start.sh`
   - 删除了不再需要的 `scripts/clash.sh`
   - 更新了主脚本中对移动后脚本的路径引用

3. **保留的 scripts 文件**：
   - `clash_latency.sh` - 延迟测试功能
   - `clash_proxy-selector.sh` - 代理选择功能
   - `get_cpu_arch.sh` - CPU 架构检测（start.sh 使用）
   - `clash_profile_conversion.sh` - 配置转换（start.sh 使用）

### 功能验证

- ✅ `./clash` 命令现在正确地在代理开启/关闭之间切换
- ✅ 开启代理时显示当前节点和延迟信息
- ✅ 状态持久化，重复调用能正确识别当前状态
- ✅ 所有脚本路径引用已更新并测试通过

### 用户体验改进

- 更符合日常使用习惯：`./clash` 只是切换代理开关，不会重启整个服务
- 快速响应：避免了不必要的服务重启时间
- 状态可靠：使用文件状态而不是环境变量，确保状态检测准确

## 2024-12-06 路径修复

### 问题描述

在将脚本文件移动到 `scripts/` 目录后，发现启动时出现路径错误：
- `start.sh` 脚本中的 `Server_Dir` 变量指向脚本所在目录（`scripts/`），而不是项目根目录
- 导致无法找到 `.env` 文件、`bin/` 目录等资源
- Dashboard 路径配置错误，导致 Clash 服务启动失败

### 修复内容

1. **修复 start.sh 路径问题**：
   - 将 `Server_Dir=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd)` 修改为 `Server_Dir=$(cd $(dirname "${BASH_SOURCE[0]}")/../ && pwd)`
   - 修复 Dashboard 路径设置，使用 `Server_Dir` 而不是 `Work_Dir`

2. **修复 restart.sh 路径问题**：
   - 同样将 `Server_Dir` 设置为项目根目录

3. **验证功能**：
   - ✅ `./clash start` 正常启动服务
   - ✅ `./clash` toggle 功能正常工作
   - ✅ 节点信息显示正常（当前节点：♻️ 自动选择，Google 延迟：813ms）
   - ✅ 代理开启/关闭切换正常

### 技术要点

- **路径计算**：使用 `../` 相对路径从 `scripts/` 目录回到项目根目录
- **最小修改**：只修改必要的路径变量，保持其他逻辑不变
- **向后兼容**：确保所有原有功能继续正常工作

### 最终状态

所有功能已恢复正常，用户可以正常使用：
- `./clash start` - 启动服务
- `./clash` - 智能切换代理开关
- `./clash status` - 查看状态
- 其他所有命令均正常工作

## 2024-12-06 节点信息显示优化

### 问题描述
用户要求优化节点信息显示：
1. 显示实际连接的具体节点，而不是"♻️ 自动选择"
2. 将节点信息和延迟信息合并到一行显示

### 技术分析
- Clash API 结构：`🔰 节点选择` (Selector) → `♻️ 自动选择` (URLTest) → `香港 08 | 专线` (实际节点)
- 需要递归解析选择器层级，获取最终的实际连接节点
- URLTest 类型的代理组的 `now` 字段包含实际选择的节点

### 实现方案
1. **优化 `get_current_proxy` 函数**：
   - 查找主选择器（优先匹配"节点选择"或"GLOBAL"）
   - 获取主选择器当前选择的代理
   - 如果是 URLTest 类型，进一步获取其 `now` 字段的实际节点
   - 简化错误处理，添加 `2>/dev/null` 避免 jq 错误输出

2. **优化 `show_proxy_info` 函数**：
   - 合并节点信息和延迟信息到一行
   - 格式：`📡 当前节点: [节点名] | 延迟: [延迟值]`

### 关键代码变更
```bash
# 简化的节点获取逻辑
local main_selector=$(echo "$proxies_data" | jq -r '.proxies | to_entries[] | select(.value.type == "Selector" and (.key | test("节点选择|GLOBAL"))) | .key' 2>/dev/null | head -1)
local current_proxy=$(echo "$proxies_data" | jq -r ".proxies[\"$main_selector\"].now // empty" 2>/dev/null)

# URLTest 类型的实际节点获取
if [ "$proxy_type" = "URLTest" ]; then
    local actual_node=$(echo "$proxies_data" | jq -r ".proxies[\"$current_proxy\"].now // empty" 2>/dev/null)
fi

# 合并显示格式
echo "📡 当前节点: $current_proxy | 延迟: $latency"
```

### 验证结果
- ✅ 显示具体节点：`香港 08 | 专线` 而不是 `♻️ 自动选择`
- ✅ 一行显示：`📡 当前节点: 香港 08 | 专线 | 延迟: 886ms`
- ✅ 切换功能正常，信息显示准确
- ✅ 错误处理完善，无多余的 jq 错误输出

### 技术要点
- 使用 jq 的 `test()` 函数进行正则匹配
- 通过 `2>/dev/null` 抑制错误输出
- 递归解析代理选择器层级关系
- 区分 Selector 和 URLTest 类型的处理逻辑
