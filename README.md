# Clash for Linux：在命令行中清晰快速地使用代理

> 绝大多数修改和文档均由 AI（Claude4.0）生成

此项目是通过使用开源项目[clash（已跑路）](https://github.com/Dreamacro/clash)作为核心程序，再结合脚本实现简单的代理功能。<br>

基于 [clash-for-linux-backup](https://github.com/Elegycloud/clash-for-linux-backup) 项目的易用性改进版本，提供统一的命令行管理界面。

主要是为了解决我们在服务器上下载 GitHub 等一些国外资源速度慢的问题。

感谢原始项目和所有贡献者的努力。🙏 

<img width="529" height="279" alt="image" src="https://github.com/user-attachments/assets/1958ff0d-f5eb-4519-b7b6-3a8f40eb5e5d" />

<img width="601" height="567" alt="image" src="https://github.com/user-attachments/assets/e0749ca4-bec1-47ea-8bcc-5deccdcd7f59" />

## 🚀 快速开始

### 方式一：使用 Python 版本（推荐）

#### 1. 安装依赖

```bash
# 安装 Poetry（如果未安装）
curl -sSL https://install.python-poetry.org | python3 -

# 安装项目依赖
poetry install

# 或使用 pip 安装
pip install -e .
```

#### 2. 配置订阅地址

```bash
# 运行配置向导
clash-cli config
```

#### 3. 启动服务

```bash
# 一键启动 Clash 并开启系统代理
clash-cli start
```

#### 4. 智能切换代理

```bash
# 直接使用 clash-cli 命令切换代理开关（推荐使用）
clash-cli

# 输出示例：
# 📡 当前节点: 香港 08 | 专线 | 延迟: 886ms
```

#### 5. 查看状态

```bash
# 查看详细运行状态
clash-cli status
```

### 方式二：使用原 Shell 版本

```bash
# 运行安装向导
bash install.sh

# 配置订阅地址
./clash config

# 启动服务
./clash start
```

## 📋 Python 版本命令列表

| 命令                | 功能     | 说明                          |
| ------------------- | -------- | ----------------------------- |
| `clash-cli`         | 智能切换 | 自动开启/关闭代理（推荐）     |
| `clash-cli start`   | 启动服务 | 一键启动 Clash 并开启系统代理 |
| `clash-cli stop`    | 停止服务 | 停止 Clash 并关闭系统代理     |
| `clash-cli restart` | 重启服务 | 重启 Clash 服务               |
| `clash-cli status`  | 查看状态 | 显示详细运行状态              |
| `clash-cli config`  | 配置向导 | 设置订阅地址等配置            |
| `clash-cli test`    | 延迟测试 | 测试所有节点延迟              |
| `clash-cli on`      | 开启代理 | 开启系统代理                  |
| `clash-cli off`     | 关闭代理 | 关闭系统代理                  |



## 💡 使用示例

### Python 版本日常使用

```bash
# 智能切换代理（最常用）
clash-cli
# 📡 当前节点: 香港 08 | 专线 | 延迟: 886ms

# 查看状态（美观的表格显示）
clash-cli status

# 测试延迟（并发测试，速度快）
clash-cli test

# 重启服务（带进度显示）
clash-cli restart
```

### 配置管理

```bash
# 交互式配置向导
clash-cli config

# 使用环境变量覆盖配置
export CLASH_CLI_HTTP_PORT=7890
export CLASH_CLI_LOG_LEVEL=debug
```

## 🔧 依赖要求

### Python 版本要求

- Python 3.8+

### 系统依赖

- `curl` - 网络请求（延迟测试需要）
- `wget` - 文件下载（可选）

### Python 依赖

通过 Poetry 自动安装：

- `click` - CLI 框架
- `httpx` - 异步 HTTP 客户端
- `pydantic` - 数据验证
- `rich` - 美观输出
- `psutil` - 进程管理
- `loguru` - 日志系统
- `pyyaml` - YAML 处理

## 🌐 端口配置

- **HTTP 代理**: 7890
- **SOCKS5 代理**: 7891
- **Redir 代理**: 7892
- **API/Dashboard**: 9090

访问 Dashboard: `http://你的IP:9090/ui`


## 🔄 兼容性

- ✅ 重用现有的 Clash 二进制文件和 subconverter
- ✅ 保持相同的目录结构和端口配置


## 📝 更新日志

### Python v1.0.0 (2025-07-17)

- ✨ 使用 Python 完全重构
- 🏗️ 现代化的模块化架构设计
- ⚡ 异步 IO 提升性能
- 🎨 Rich 库美化用户界面
- 🔒 Pydantic 数据验证
- 🧪 支持单元测试
- 📦 Poetry 依赖管理




# 致谢与声明

本项目参考 [clash-for-linux-backup](https://github.com/Elegycloud/clash-for-linux-backup) 项目进行 Python 重构，参考其架构和功能，进行了升级和优化。原项目作者及社区为本项目提供了宝贵的基础和灵感，在此致以诚挚感谢。

本工具仅供科研、学习或合规网络加速用途，严禁用于任何违法犯罪活动。用户在使用本项目时，必须遵守所在国家和地区的法律法规。因使用本工具进行违法犯罪活动、或因被黑客入侵等造成的任何损失、法律责任，均由用户自行承担，开发者及维护者不承担任何直接或间接责任。

本项目遵循 GNU 通用公共许可证（GPL）v3.0，详细条款请参见 LICENSE 文件。<br>

> 本项目为开源重构版本，所有代码和文档均由 AI 及社区协作生成，欢迎共同维护和改进。<br>
> 如有侵权或其他问题，请提交 issue 或联系维护者。


