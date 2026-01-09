# Replay Version Checker

🔍 自动检查 [Replay](https://www.weights.com/replay) 应用的版本更新工具

## ✨ 功能特性

- ✅ 直接访问官方更新服务器(与 Replay 应用完全相同)
- ✅ 同时检查多个平台(macOS ARM/Intel、Windows)
- ✅ 版本变化时自动创建 GitHub Issue 通知
- ✅ 支持 GitHub Actions 定时运行
- ✅ 智能网络错误处理和自动重试
- ✅ 多源备份自动切换

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

**特点**:
- 直接访问官方更新服务器
- 同时检查所有平台版本
- 自动检测版本变化
- 平台自适应识别
- 获取完整版本信息(版本号、发布日期、SHA512、下载链接)
- 支持 GitHub Actions 集成

**支持的平台**:
- ✅ macOS Apple Silicon (ARM64)
- ✅ macOS Intel (x64)
- ✅ Windows
- ⚠️ Linux (由于使用 Cloudflare R2 签名 URL，目前无法自动检查)

## 📖 使用说明

### GitHub Actions 自动运行

项目已配置自动化工作流:

- **定时检查**: 每天 UTC 10:00 (北京时间 18:00)
- **手动触发**: Actions 页面点击 "Run workflow"
- **版本通知**: 发现新版本自动创建 Issue

### 本地开发

```bash
# 克隆仓库
git clone <your-repo-url>
cd replay-version-checker

# 安装依赖
pip install -r requirements.txt

# 运行检查
python3 check_all_platforms.py
```

## 📁 项目结构

```
├── check_all_platforms.py       # ⭐ 主检查脚本
├── requirements.txt             # Python 依赖
├── README.md                    # 本文档
├── ANALYSIS.md                 # 技术分析文档
└── .github/workflows/          # GitHub Actions 配置
```

### 自动生成的文件

- `all_platforms_versions.json` - 所有平台版本信息

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

如果遇到网络问题:

1. **检查网络连接**: 确保能访问 `weights.com` 和 Cloudflare R2
2. **代理设置**: 如果使用代理,确保正确配置
3. **防火墙**: 检查防火墙是否阻止了连接

### GitHub Actions 权限问题

如果 Actions 无法创建 Issue 或提交代码:

1. 检查仓库的 Actions 权限设置
2. 确保 Workflow 有 `contents: write` 和 `issues: write` 权限

## 自定义扩展

### 添加通知方式

在 `.github/workflows/check-version.yml` 的最后一步,你可以添加:

- 邮件通知
- Slack/Discord 消息
- 微信/钉钉机器人
- Telegram Bot

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request!

---

Made with ❤️ for Replay users