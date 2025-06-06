# Clash for Linux - 统一管理版本

> 所有修改和文档均由 AI 生成

此项目是通过使用开源项目[clash（已跑路）](https://github.com/Dreamacro/clash)作为核心程序，再结合脚本实现简单的代理功能。<br>

基于 [clash-for-linux-backup](https://github.com/Elegycloud/clash-for-linux-backup) 项目的易用性改进版本，提供统一的命令行管理界面。

## ✨ 新特性

- 🚀 **一键操作**: 统一的 `clash` 命令管理所有功能
- 🔧 **自动配置**: 智能检测依赖和自动配置管理
- 📊 **状态监控**: 实时显示服务状态、端口状态、API 状态
- 🎯 **配置向导**: 交互式订阅地址配置和验证
- 🎨 **友好界面**: 彩色输出和清晰的错误提示
- 📡 **智能节点显示**: 显示实际连接的具体节点和延迟信息

## 🚀 快速开始

### 1. 安装统一管理命令

```bash
# 运行安装向导
bash install.sh

# 或者直接使用当前目录
chmod +x clash
```

### 2. 配置订阅地址

```bash
# 运行配置向导
clash config
```

### 3. 启动服务

```bash
# 一键启动 Clash 并开启系统代理
clash start
```

### 4. 开关式切换代理

```bash
# 直接使用clash命令切换代理开关（推荐使用）
clash

# 输出示例：
# 📡 当前节点: 香港 08 | 专线 | 延迟: 886ms
```

### 5. 查看状态

```bash
# 查看详细运行状态
clash status
```

## 📋 命令列表

| 命令            | 功能     | 说明                          |
| --------------- | -------- | ----------------------------- |
| `clash`         | 智能切换 | 自动开启/关闭代理（推荐）     |
| `clash start`   | 启动服务 | 一键启动 Clash 并开启系统代理 |
| `clash stop`    | 停止服务 | 停止 Clash 并关闭系统代理     |
| `clash restart` | 重启服务 | 重启 Clash 服务               |
| `clash status`  | 查看状态 | 显示详细运行状态              |
| `clash config`  | 配置向导 | 设置订阅地址等配置            |
| `clash test`    | 延迟测试 | 测试所有节点延迟              |
| `clash select`  | 节点选择 | 选择代理节点和模式            |
| `clash on`      | 开启代理 | 开启系统代理                  |
| `clash off`     | 关闭代理 | 关闭系统代理                  |
| `clash help`    | 帮助信息 | 显示详细帮助                  |

## 💡 使用示例

### 首次使用

```bash
# 1. 安装命令
bash install.sh

# 2. 配置订阅
clash config

# 3. 启动服务
clash start
```

### 日常使用

```bash
# 智能切换代理（最常用）
clash
# 📡 当前节点: 香港 08 | 专线 | 延迟: 886ms

# 查看状态
clash status

# 测试延迟
clash test

# 选择节点
clash select

# 重启服务
clash restart
```

### 代理控制

```bash
# 开启代理
clash on

# 关闭代理
clash off

# 智能切换（推荐）
clash
```

## 🔧 依赖要求

### 必需依赖

- `curl` - 网络请求
- `wget` - 文件下载

### 可选依赖

- `jq` - JSON 处理 (延迟测试和节点选择功能需要)

### 安装依赖

```bash
# Ubuntu/Debian
sudo apt-get install curl wget jq

# CentOS/RHEL
sudo yum install curl wget jq

# Alpine
sudo apk add curl wget jq
```

## 📁 项目结构

```
clash-for-linux-backup/
├── clash              # 统一管理命令 (新增)
├── install.sh         # 安装脚本 (新增)
├── start.sh           # 原启动脚本
├── restart.sh         # 原重启脚本
├── shutdown.sh        # 原停止脚本
├── .env               # 环境配置文件
├── bin/               # Clash 二进制文件
├── conf/              # 配置文件目录
├── scripts/           # 原脚本工具集
├── tools/             # 工具目录
└── dashboard/         # Web 控制面板
```

## 🌐 端口配置

- **HTTP 代理**: 7890
- **SOCKS5 代理**: 7891
- **Redir 代理**: 7892
- **API/Dashboard**: 9090

访问 Dashboard: `http://你的IP:9090/ui`

## ❓ 常见问题

### Q: 如何更换订阅地址？

```bash
clash config
```

### Q: 如何查看当前状态？

```bash
clash status
```

### Q: 延迟测试功能不可用？

确保安装了 `jq` 工具：

```bash
sudo apt-get install jq  # Ubuntu/Debian
sudo yum install jq      # CentOS/RHEL
```

### Q: 需要 sudo 权限吗？

启动和停止服务需要 sudo 权限，其他操作不需要。

### Q: 如何卸载？

```bash
# 删除全局命令 (如果使用了全局安装)
sudo rm /usr/local/bin/clash

# 删除项目目录
rm -rf clash-for-linux-backup
```

## 🔄 兼容性

- ✅ 完全兼容原有脚本和配置
- ✅ 支持原有的手动操作方式
- ✅ 不影响现有的 .env 配置和工作流程

## 📝 更新日志

### v0.1.0 (2025-06-06)

- ✨ 新增智能节点信息显示
  - 显示实际连接的具体节点，而不是"♻️ 自动选择"
  - 节点信息和延迟信息合并到一行显示
  - 格式：`📡 当前节点: [节点名] | 延迟: [延迟值]`
- 🔧 优化代理切换功能
  - `clash` 命令现在只切换代理开关，不重启服务
  - 使用状态文件持久化代理状态
  - 提升响应速度和用户体验
- 📁 整理项目文件结构
  - 将脚本文件移动到 `scripts/` 目录
  - 修复路径引用问题
  - 保持向后兼容性

### v0.1.1 (2025-06-06)

- ✨ 新增统一管理命令 `clash`
- ✨ 新增安装向导 `install.sh`
- ✨ 新增配置向导功能
- ✨ 新增状态监控功能
- ✨ 新增自动依赖检测
- ✨ 新增智能配置管理
- 🎨 优化用户界面和错误提示

## 📄 许可证

本项目基于原 clash-for-linux-backup 项目进行易用性改进，遵循相同的开源许可证。

## 🙏 致谢

感谢 [Elegycloud](https://github.com/Elegycloud) 提供的原始项目和所有贡献者的努力。

# 多语言

- [English Documentation (README_en)](README_en.md)

---

# 项目介绍

此项目是通过使用开源项目[clash（已跑路）](https://github.com/Dreamacro/clash)作为核心程序，再结合脚本实现简单的代理功能。<br>
clash 核心备份仓库[Clash-backup](https://github.com/Elegycloud/clash-for-linux-backup)

主要是为了解决我们在服务器上下载 GitHub 等一些国外资源速度慢的问题。

# 免责声明

1.本项目使用 GNU 通用公共许可证（GPL）v3.0 进行许可。您可以查看本仓库 LICENSE 进行了解

2.本项目的原作者保留所有知识产权。作为使用者，您需遵守 GPL v3.0 的要求，并承担因使用本项目而产生的任何风险。

3.本项目所提供的内容不提供任何明示或暗示的保证。在法律允许的范围内，原作者概不负责，不论是直接的、间接的、特殊的、偶然的或后果性的损害。

4.本项目与仓库的创建者和维护者完全无关，仅作为备份仓库，任何因使用本项目而引起的纠纷、争议或损失，与仓库的作者和维护者完全无关。

5.对于使用本项目所导致的任何纠纷或争议，使用者必须遵守自己国家的法律法规，并且需自行解决因使用本项目而产生的任何法律法规问题。

# 题外话

由于作者已经跑路，当前仓库仅进行备份，若有侵犯您的权利，请提交 issues 我会看到并删除仓库<br>

（2024/06/07 留：）其次就是，issue 我没有时间回，很抱歉，欢迎各位来一起维护和解决这个仓库的问题！<br>

clash for linux 备份(备份号：202311091510)。
若喜欢本项目，请点个小星星！
<br>

# 使用须知

- 运行本项目建议使用 root 用户，或者使用 sudo 提权。
- 使用过程中如遇到问题，请优先查已有的 [issues](https://github.com/Elegycloud/clash-for-linux-backup/issues)。
- 在进行 issues 提交前，请替换提交内容中是敏感信息（例如：订阅地址）。
- 本项目是基于 [clash（已跑路）](https://github.com/Dreamacro/clash) 、[yacd](https://github.com/haishanh/yacd) 进行的配置整合，关于 clash、yacd 的详细配置请去原项目查看。
- 此项目不提供任何订阅信息，请自行准备 Clash 订阅地址。
- 运行前请手动更改`.env`文件中的`CLASH_URL`变量值，否则无法正常运行。
- 当前在 RHEL 系列和 Debian,Kali Linux,ubuntu 以及 Linux 系统中测试过，其他系列可能需要适当修改脚本。
- 支持 x86_64/aarch64 平台
- 【注意：部分带有桌面端 Linux 系统的需要在浏览器设置代理！否则有可能无法使用！】
- 【若系统代理无法使用，但是想要系统代理，请修改尝试修改 start.sh 中的端口后执行环境变量命令！】
- 【还是无法使用请更换当前网络环境（也是其中一个因素！）】
- 【部分 Linux 系统会出现谷歌，twitter，youtube 等可能无法 ping 通，正常现象！】
  > **注意**：当你在使用此项目时，遇到任何无法独自解决的问题请优先前往 [Issues](https://github.com/Elegycloud/clash-for-linux-backup/issue) 寻找解决方法。由于空闲时间有限，后续将不再对 Issues 中 "已经解答"、"已有解决方案" 的问题进行重复性的回答。

<br>

# 使用教程

## 下载项目

下载项目

```bash
$ git clone https://github.com/Elegycloud/clash-for-linux-backup.git
```

进入到项目目录，编辑`.env`文件，修改变量`CLASH_URL`的值。

```bash
$ cd clash-for-linux
$ vim .env
```

> **注意：** `.env` 文件中的变量 `CLASH_SECRET` 为自定义 Clash Secret，值为空时，脚本将自动生成随机字符串。

<br>

## 启动程序

直接运行脚本文件`start.sh`

- 进入项目目录

```bash
$ cd clash-for-linux
```

- 运行启动脚本

```bash
$ sudo bash start.sh

正在检测订阅地址...
Clash订阅地址可访问！                                      [  OK  ]

正在下载Clash配置文件...
配置文件config.yaml下载成功！                              [  OK  ]

正在启动Clash服务...
服务启动成功！                                             [  OK  ]

Clash Dashboard 访问地址：http://<ip>:9090/ui
Secret：xxxxxxxxxxxxx

请执行以下命令加载环境变量: source /etc/profile.d/clash.sh

请执行以下命令开启系统代理: proxy_on

若要临时关闭系统代理，请执行: proxy_off

```

```bash
$ source /etc/profile.d/clash.sh
$ proxy_on
```

- 检查服务端口

```bash
$ netstat -tln | grep -E '9090|789.'
tcp        0      0 127.0.0.1:9090          0.0.0.0:*               LISTEN
tcp6       0      0 :::7890                 :::*                    LISTEN
tcp6       0      0 :::7891                 :::*                    LISTEN
tcp6       0      0 :::7892                 :::*                    LISTEN
```

- 检查环境变量

```bash
$ env | grep -E 'http_proxy|https_proxy'
http_proxy=http://127.0.0.1:7890
https_proxy=http://127.0.0.1:7890
```

以上步鄹如果正常，说明服务 clash 程序启动成功，现在就可以体验高速下载 github 资源了。

<br>

## 重启程序

如果需要对 Clash 配置进行修改，请修改 `conf/config.yaml` 文件。然后运行 `restart.sh` 脚本进行重启。

> **注意：**
> 重启脚本 `restart.sh` 不会更新订阅信息。

<br>

## 停止程序

- 进入项目目录

```bash
$ cd clash-for-linux
```

- 关闭服务

```bash
$ sudo bash shutdown.sh
```

服务关闭成功，请执行以下命令关闭系统代理：proxy_off

```bash
$ proxy_off
```

然后检查程序端口、进程以及环境变量`http_proxy|https_proxy`，若都没则说明服务正常关闭。

<br>

## Clash Dashboard

- 访问 Clash Dashboard

通过浏览器访问 `start.sh` 执行成功后输出的地址，例如：http://192.168.0.1:9090/ui

- 登录管理界面

在`API Base URL`一栏中输入：http://\<ip\>:9090 ，在`Secret(optional)`一栏中输入启动成功后输出的 Secret。

点击 Add 并选择刚刚输入的管理界面地址，之后便可在浏览器上进行一些配置。

- 更多教程

此 Clash Dashboard 使用的是[yacd](https://github.com/haishanh/yacd)项目，详细使用方法请移步到 yacd 上查询。

<br>

## 终端界面选择代理节点

部分用户无法通过浏览器使用 Clash Dashboard 进行节点选择、代理模式修改等操作，为了方便用户可以在 Linux 终端进行操作，下面提供了一个功能简单的脚本以便用户可以临时通过终端界面进行配置。

脚本存放位置：`scripts/clash_proxy-selector.sh`

> **注意：**
>
> 使用脚本前，需要修改脚本中的 **Secret** 变量值为上述启动脚本输出的值，或者与 `.env` 文件中定义的 **CLASH_SECRET** 变量值保持一致。

<br>

# 常见问题

1. 部分 Linux 系统默认的 shell `/bin/sh` 被更改为 `dash`，运行脚本会出现报错（报错内容一般会有 `-en [ OK ]`）。建议使用 `bash xxx.sh` 运行脚本。

2. 部分用户在 UI 界面找不到代理节点，基本上是因为厂商提供的 clash 配置文件是经过 base64 编码的，且配置文件格式不符合 clash 配置标准。

   目前此项目已集成自动识别和转换 clash 配置文件的功能。如果依然无法使用，则需要通过自建或者第三方平台（不推荐，有泄露风险）对订阅地址转换。

3. 程序日志中出现`error: unsupported rule type RULE-SET`报错，解决方法查看官方[WIKI](https://github.com/Dreamacro/clash/wiki/FAQ#error-unsupported-rule-type-rule-set)

## 命令说明

在加载环境变量后（`source /etc/profile.d/clash.sh`），可以使用以下命令：

- `clash_on` - 开启系统代理
- `clash_off` - 关闭系统代理
- `clash_test` - 测试所有代理节点的延迟（需要安装 jq）
- `clash_help` - 显示所有可用命令的帮助信息

> **注意：** 使用 `clash_test` 命令需要安装 `jq` 工具。在 Ubuntu/Debian 系统上可以通过 `sudo apt-get install jq` 安装；在 CentOS/RHEL 系统上可以通过 `sudo yum install jq` 安装。

## ⚙️ 配置说明

### 环境配置文件

首次使用需要配置订阅地址：

```bash
# 1. 复制配置模板
cp .env.example .env

# 2. 编辑配置文件
nano .env
```

配置文件示例：

```bash
# Clash 订阅地址 (必填)
export CLASH_URL='https://your-subscription-url-here'

# Clash Secret (可选，留空则自动获取)
export CLASH_SECRET=''

# 设置为1以跳过订阅检查和下载 (调试用)
SKIP_SUBSCRIPTION_CHECK=0
```

> ⚠️ **安全提醒**: `.env` 文件包含敏感信息，已被 `.gitignore` 忽略，不会上传到仓库

### 使用配置向导

```bash
# 交互式配置向导
clash config
```
