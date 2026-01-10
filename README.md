# Replay Version Checker

🔍 自动检查 [Replay](https://www.weights.com/replay) 应用的版本更新工具

## ✨ 功能特性

- ✅ 直接访问官方更新服务器（与 Replay 应用完全相同的 API）
- ✅ 同时检查多个平台（macOS ARM/Intel、Windows）
- ✅ 智能版本比较算法（支持各种版本号格式）
- ✅ 版本变化时自动创建 GitHub Issue 通知
- ✅ 支持 GitHub Actions 定时运行
- ✅ 智能网络错误处理和自动重试（3 次重试，2 秒间隔）
- ✅ 开发模式支持（通过 `DEV_MODE` 环境变量）
- ✅ 完整版本信息（版本号、发布日期、SHA512、直接下载链接）

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行脚本

```bash
python3 check_all_platforms.py
```

## 📦 核心功能

### check_all_platforms.py

通过逆向分析 Replay v8.6.0 的 app.asar 文件，完全复现了官方的更新检查机制。

**核心特性**:
- 🔗 直接访问官方更新服务器（与 Replay 应用完全相同的 API）
- 🌍 同时检查所有平台版本（并行请求）
- 🔄 智能版本变化检测和比对
- 📊 获取完整版本信息（版本号、发布日期、SHA512、下载链接）
- 🔁 自动重试机制（网络错误自动重试 3 次）
- 🤖 GitHub Actions 集成（自动创建 Issue 通知）
- 🧪 开发模式支持（通过 `DEV_MODE` 环境变量）

**支持的平台**:
- ✅ macOS Apple Silicon (ARM64) - `https://updates-mac-arm64.weights.com`
- ✅ macOS Intel (x64) - `https://updates-mac-x64.weights.com`
- ✅ Windows - `https://updates-windows.weights.com`
- ⚠️ Linux - 由于使用 Cloudflare R2 签名 URL，需要 AWS 签名认证，目前无法自动检查

## 📖 使用说明

### 本地运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 正常模式运行（实际检查版本）
python3 check_all_platforms.py

# 3. 开发模式运行（跳过版本检查，用于测试）
DEV_MODE=true python3 check_all_platforms.py
```

**工作流程**:
1. 从各平台的更新服务器获取最新的 YAML 配置文件
2. 解析版本信息（版本号、发布日期、下载链接、SHA512 校验值）
3. 与历史版本比较，检测更新
4. 将结果保存到 `all_platforms_versions.json`
5. 在 GitHub Actions 中运行时，如有更新会自动创建 Issue

### GitHub Actions 自动运行

项目已配置自动化工作流:

- **定时检查**: 每 4 小时运行一次
- **手动触发**: Actions 页面点击 "Run workflow"
- **版本通知**: 发现新版本自动创建 Issue + 飞书通知
- **自动提交**: 版本文件更新后自动提交到仓库

### 配置通知

#### 1. GitHub Issue 通知

默认开启，无需配置。发现新版本会自动创建 Issue，标签为 `version-update`。

#### 2. 飞书机器人通知

**步骤一：创建飞书群机器人**

1. 打开飞书群聊，点击右上角 `···` → `设置`
2. 选择 `群机器人` → `添加机器人`
3. 选择 `自定义机器人`
4. 配置机器人信息：
   - 名称：`Replay 版本通知` (可自定义)
   - 描述：`自动通知 Replay 应用版本更新` (可自定义)
5. 点击 `添加`，复制生成的 **Webhook 地址**
   - 格式类似：`https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxxxx`

**步骤二：配置 GitHub Secrets**

1. 打开你的 GitHub 仓库
2. 点击 `Settings` → `Secrets and variables` → `Actions`
3. 点击 `New repository secret`
4. 填写 Secret 信息：
   - **Name**: `FEISHU_WEBHOOK_URL`
   - **Secret**: 粘贴刚才复制的 Webhook 地址
5. 点击 `Add secret` 保存

**步骤三：测试通知**

配置完成后，你可以：
1. 手动触发 GitHub Actions 工作流测试
2. 或等待定时任务自动运行
3. 如果检测到版本更新，飞书群会收到通知

**通知内容包含**:
- 📱 各平台版本变化对比 (如：8.5.3 → 8.6.0)
- 📥 官网下载和直接下载链接
- ⏰ 检测时间（北京时间 UTC+8）
- 🔗 查看详情按钮（跳转到 GitHub Actions 运行日志）

## 📁 项目结构

```
├── check_all_platforms.py       # ⭐ 主检查脚本（约 316 行）
│   ├── PLATFORMS               # 平台配置（macOS ARM/Intel, Windows）
│   ├── fetch_platform_version()  # 获取单个平台版本
│   ├── compare_versions()      # 智能版本比较算法
│   ├── is_network_error()      # 网络错误识别
│   └── main()                  # 主流程控制
├── requirements.txt             # Python 依赖（requests, pyyaml）
├── README.md                    # 本文档
├── .gitignore                   # Git 忽略配置
└── .github/workflows/          # GitHub Actions 配置
    └── check-version.yml       # 自动检查工作流
```

### 自动生成的文件

- `all_platforms_versions.json` - 所有平台版本信息（含完整历史记录）

## GitHub Actions 配置

### 手动触发检查

1. 进入仓库的 **Actions** 标签页
2. 选择 **Check Replay Version** 工作流
3. 点击 **Run workflow** 按钮

### 修改检查频率

编辑 `.github/workflows/check-version.yml` 文件中的 cron 表达式:

```yaml
schedule:
  - cron: '0 10 * * *'  # 每天 UTC 10:00
```

常用 cron 表达式:
- `0 */6 * * *` - 每 6 小时运行一次
- `0 0 * * *` - 每天 UTC 00:00 运行
- `0 0 * * 1` - 每周一运行

### 权限设置

确保 GitHub Actions 有权限创建 Issue 和提交代码:

1. 进入仓库 **Settings** > **Actions** > **General**
2. 在 **Workflow permissions** 部分选择:
   - ✅ Read and write permissions
   - ✅ Allow GitHub Actions to create and approve pull requests

## 📊 版本信息文件示例

### all_platforms_versions.json

脚本运行后会生成包含所有平台版本信息的 JSON 文件：

```json
{
  "check_time": "2026-01-10T00:42:40.824690",
  "platforms": {
    "mac-arm64": {
      "version": "8.6.0",
      "platform": "macOS Apple Silicon",
      "platform_key": "mac-arm64",
      "source_url": "https://updates-mac-arm64.weights.com/latest-mac.yml",
      "download_param": "mac",
      "release_date": "2026-01-05T11:38:40.614Z",
      "download_path": "Replay-arm64-8.6.0.zip",
      "full_download_url": "https://updates-mac-arm64.weights.com/Replay-arm64-8.6.0.zip",
      "sha512": "pKL8oEy1GXBHaIOF..."
    },
    "mac-x64": {
      "version": "8.6.0",
      "platform": "macOS Intel",
      "platform_key": "mac-x64",
      "source_url": "https://updates-mac-x64.weights.com/latest-mac.yml",
      "download_param": "mac_x64",
      "release_date": "2026-01-05T11:38:32.176Z",
      "download_path": "Replay-x64-8.6.0.zip",
      "full_download_url": "https://updates-mac-x64.weights.com/Replay-x64-8.6.0.zip",
      "sha512": "1KmUUacQdmTzVace..."
    },
    "windows": {
      "version": "8.6.0",
      "platform": "Windows",
      "platform_key": "windows",
      "source_url": "https://updates-windows.weights.com/latest.yml",
      "download_param": "windows",
      "release_date": "2026-01-05T11:34:16.383Z",
      "download_path": "Replay-8.6.0-installer.exe",
      "full_download_url": "https://updates-windows.weights.com/Replay-8.6.0-installer.exe",
      "sha512": "2r1A4ZcIQNLUJFcm..."
    }
  }
}
```

> **注意**:
> - Linux 平台使用 Cloudflare R2 签名 URL，需要 AWS 签名认证，目前无法通过简单的 YAML 文件自动检查
> - 如果某个平台检查失败，它将不会出现在输出文件中

## 技术栈

- **Python 3.11+**
- **requests**: HTTP 请求库
- **pyyaml**: YAML 文件解析
- **GitHub Actions**: 自动化运行

## 故障排查

### 网络连接失败

脚本内置智能重试机制，如果遇到网络问题:

1. **自动重试**: 网络错误会自动重试 3 次，每次间隔 2 秒
2. **错误识别**: 自动识别 connection、timeout、network 等网络错误
3. **检查网络**: 确保能访问 `weights.com` 域名
4. **代理设置**: 如使用代理，确保正确配置环境变量
5. **防火墙**: 检查防火墙是否阻止了 HTTPS 连接

**常见网络错误类型**:
- Connection errors (连接失败)
- Timeout errors (请求超时)
- Network unreachable (网络不可达)
- Connection refused/reset (连接被拒绝/重置)

### GitHub Actions 权限问题

如果 Actions 无法创建 Issue 或提交代码:

1. 检查仓库的 Actions 权限设置
2. 确保 Workflow 有 `contents: write` 和 `issues: write` 权限
3. 验证 `GITHUB_TOKEN` 有足够的权限

### 版本检测问题

如果版本比较不准确:

- 脚本使用智能版本比较算法，支持 `8.6.0`、`8.6.0-beta` 等格式
- 自动标准化版本号并补齐长度
- 支持检测版本升级、降级和不变三种状态

### 飞书通知问题

如果飞书通知发送失败:

1. **检查 Webhook URL**: 确保 `FEISHU_WEBHOOK_URL` 配置正确
2. **机器人权限**: 确认机器人已添加到目标群组
3. **查看日志**: 在 GitHub Actions 运行日志中查看详细错误信息
4. **测试 Webhook**: 可以使用 curl 命令测试 Webhook 是否可用

```bash
curl -X POST "YOUR_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"msg_type":"text","content":{"text":"测试消息"}}'
```

## 自定义扩展

### 修改重试配置

在 [check_all_platforms.py](check_all_platforms.py) 中修改重试参数:

```python
MAX_RETRIES = 3      # 最大重试次数
RETRY_DELAY = 2      # 重试间隔（秒）
DEV_MODE = os.getenv('DEV_MODE', 'false').lower() == 'true'  # 开发模式
```

### 添加其他通知方式

项目已内置飞书通知。如需添加其他通知渠道，可在 [.github/workflows/check-version.yml](.github/workflows/check-version.yml) 的 `Send Feishu notification` 步骤后添加新的通知步骤。

**支持的通知方式**:
- ✅ **GitHub Issue** - 已内置
- ✅ **飞书机器人** - 已内置，需配置 `FEISHU_WEBHOOK_URL`
- 📧 **邮件通知** - 可使用 [action-send-mail](https://github.com/dawidd6/action-send-mail)
- 💬 **Slack** - 可使用 [slack-github-action](https://github.com/slackapi/slack-github-action)
- 🤖 **Discord** - 可使用 [discord-webhook-notify](https://github.com/marketplace/actions/discord-webhook-notify)
- 📱 **微信/钉钉** - 类似飞书，使用 Webhook
- 📨 **Telegram** - 可使用 [telegram-action](https://github.com/appleboy/telegram-action)

**示例：添加 Telegram 通知**

在 workflow 中添加新的步骤：

```yaml
- name: Send Telegram notification
  if: steps.version_check.outputs.has_updates == 'true'
  uses: appleboy/telegram-action@master
  with:
    to: ${{ secrets.TELEGRAM_CHAT_ID }}
    token: ${{ secrets.TELEGRAM_BOT_TOKEN }}
    message: |
      🎉 Replay 新版本发布！

      ${{ steps.version_check.outputs.updated_platforms }}
```

### 自定义版本比较逻辑

修改 [check_all_platforms.py](check_all_platforms.py) 中的 `compare_versions()` 函数来自定义版本比较逻辑。

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request!

---

Made with ❤️ for Replay users