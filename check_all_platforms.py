#!/usr/bin/env python3
"""
Replay 全平台版本检查工具
检查所有平台 (macOS x64, macOS ARM, Windows, Linux) 的版本更新
"""

import re
import json
import os
import time
from datetime import datetime, timezone, timedelta
import requests
import yaml

REPLAY_URL = "https://www.weights.com/replay"
VERSION_FILE = "all_platforms_versions.json"

# 更新源配置 (基于 app.asar 分析)
UPDATES_BASE_URL = "https://updates-{subdomain}.weights.com"

# 北京时间时区 (UTC+8)
BEIJING_TZ = timezone(timedelta(hours=8))

# 平台配置
PLATFORMS = {
    'mac-arm64': {
        'name': 'macOS Apple Silicon',
        'subdomain': 'mac-arm64',
        'yml_file': 'latest-mac.yml',
        'download_param': 'mac'
    },
    'mac-x64': {
        'name': 'macOS Intel',
        'subdomain': 'mac-x64',
        'yml_file': 'latest-mac.yml',
        'download_param': 'mac_x64'
    },
    'windows': {
        'name': 'Windows',
        'subdomain': 'windows',
        'yml_file': 'latest.yml',
        'download_param': 'windows'
    },
    'linux': {
        'name': 'Linux',
        'subdomain': 'linux',
        'yml_file': 'latest-linux.yml',
        'download_param': 'linux'
    }
}

# 配置选项
MAX_RETRIES = 3
RETRY_DELAY = 2
DEV_MODE = os.getenv('DEV_MODE', 'false').lower() == 'true'

def is_network_error(error):
    """判断是否为网络错误"""
    error_str = str(error).lower()
    network_errors = ['connection', 'timeout', 'network', 'unreachable', 'disconnected', 'refused', 'reset']
    return any(err in error_str for err in network_errors)

def fetch_platform_version(platform_key, config):
    """
    获取特定平台的版本信息
    """
    subdomain = config['subdomain']
    yml_filename = config['yml_file']
    yml_url = f"{UPDATES_BASE_URL.format(subdomain=subdomain)}/{yml_filename}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Replay/8.6.0',
        'Accept': 'text/yaml,application/yaml,text/plain,*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive'
    }

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(yml_url, headers=headers, timeout=30, allow_redirects=True)
            response.raise_for_status()

            yml_data = yaml.safe_load(response.text)

            if yml_data and 'version' in yml_data:
                version_info = {
                    'version': yml_data['version'],
                    'platform': config['name'],
                    'platform_key': platform_key,
                    'source_url': yml_url,
                    'download_param': config['download_param']
                }

                if 'releaseDate' in yml_data:
                    version_info['release_date'] = yml_data['releaseDate']
                if 'path' in yml_data:
                    version_info['download_path'] = yml_data['path']
                    base_url = yml_url.rsplit('/', 1)[0]
                    version_info['full_download_url'] = f"{base_url}/{yml_data['path']}"
                if 'sha512' in yml_data:
                    version_info['sha512'] = yml_data['sha512'][:16] + '...'

                return version_info, None

        except yaml.YAMLError as e:
            return None, f"YAML 解析错误: {e}"
        except requests.RequestException as e:
            if is_network_error(e):
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                else:
                    return None, "网络连接失败"
            else:
                return None, f"请求失败: {e}"

    return None, "达到最大重试次数"

def load_previous_versions():
    """加载之前保存的版本信息"""
    if os.path.exists(VERSION_FILE):
        try:
            with open(VERSION_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  读取历史版本文件失败: {e}")
    return None

def save_current_versions(versions_data):
    """保存当前版本信息"""
    try:
        with open(VERSION_FILE, 'w', encoding='utf-8') as f:
            json.dump(versions_data, f, indent=2, ensure_ascii=False)
        print(f"✅ 版本信息已保存到 {VERSION_FILE}")
    except Exception as e:
        print(f"❌ 保存版本信息失败: {e}")

def compare_versions(v1, v2):
    """比较两个版本号"""
    def normalize(v):
        return [int(x) for x in re.sub(r'[^0-9.]', '', v).split('.')]

    try:
        parts1 = normalize(v1)
        parts2 = normalize(v2)

        max_len = max(len(parts1), len(parts2))
        parts1.extend([0] * (max_len - len(parts1)))
        parts2.extend([0] * (max_len - len(parts2)))

        for i in range(max_len):
            if parts1[i] > parts2[i]:
                return 1
            elif parts1[i] < parts2[i]:
                return -1
        return 0
    except Exception:
        return 0

def main():
    """主函数"""
    print("=" * 70)
    print("🔍 Replay 全平台版本检查工具")
    print("=" * 70)
    beijing_time = datetime.now(BEIJING_TZ)
    print(f"⏰ 检查时间: {beijing_time.strftime('%Y-%m-%d %H:%M:%S')} (北京时间)")
    print(f"🌐 官网地址: {REPLAY_URL}")
    print()

    if DEV_MODE:
        print("ℹ️  开发模式已启用,跳过版本检查")
        return 0

    # 获取所有平台的版本信息
    print("📡 正在获取所有平台的版本信息...")
    print()

    current_versions = {
        'check_time': datetime.now(BEIJING_TZ).isoformat(),
        'platforms': {}
    }

    success_count = 0
    failed_platforms = []

    for platform_key, config in PLATFORMS.items():
        print(f"🔗 检查 {config['name']}...")
        version_info, error = fetch_platform_version(platform_key, config)

        if version_info:
            current_versions['platforms'][platform_key] = version_info
            print(f"   ✅ 版本: {version_info['version']}")
            if 'release_date' in version_info:
                print(f"   📅 日期: {version_info['release_date']}")
            if 'download_path' in version_info:
                print(f"   📦 文件: {version_info['download_path']}")
            success_count += 1
        else:
            failed_platforms.append((config['name'], error))
            print(f"   ❌ 失败: {error}")

        print()

    # 显示统计
    print("=" * 70)
    print(f"📊 检查完成: 成功 {success_count}/{len(PLATFORMS)} 个平台")
    print("=" * 70)
    print()

    if failed_platforms:
        print("⚠️  以下平台检查失败:")
        for platform_name, error in failed_platforms:
            print(f"   - {platform_name}: {error}")
        print()

    # 加载历史版本并比较
    previous_data = load_previous_versions()
    updated_platforms = []
    new_platforms = []

    # 构建最终要保存的版本数据（基于历史数据，只更新有新版本的平台）
    final_versions = {
        'check_time': previous_data.get('check_time', current_versions['check_time']) if previous_data else current_versions['check_time'],
        'platforms': dict(previous_data.get('platforms', {})) if previous_data else {}
    }

    if previous_data and 'platforms' in previous_data:
        print("🔄 版本变化检测:")
        print()

        for platform_key, current_info in current_versions['platforms'].items():
            current_version = current_info['version']
            platform_name = current_info['platform']

            if platform_key in previous_data['platforms']:
                previous_version = previous_data['platforms'][platform_key]['version']
                comparison = compare_versions(current_version, previous_version)

                if comparison > 0:
                    # 只有版本升级时才更新该平台的信息
                    final_versions['platforms'][platform_key] = current_info
                    updated_platforms.append({
                        'platform': platform_name,
                        'platform_key': platform_key,
                        'old_version': previous_version,
                        'new_version': current_version,
                        'download_url': current_info.get('full_download_url', ''),
                        'download_param': current_info.get('download_param', '')
                    })
                    print(f"🆕 {platform_name}: {previous_version} → {current_version}")
                elif comparison < 0:
                    # 版本回退，保留旧版本信息，不更新
                    print(f"⚠️  {platform_name}: 上游返回旧版本 {current_version}，保留现有版本 {previous_version}")
                else:
                    print(f"✅ {platform_name}: {current_version} (无变化)")
            else:
                # 新增平台
                final_versions['platforms'][platform_key] = current_info
                new_platforms.append(platform_name)
                print(f"🆕 {platform_name}: {current_version} (新增平台)")

        print()

        # 显示更新摘要
        if updated_platforms or new_platforms:
            # 只有在有真正更新时才更新 check_time
            final_versions['check_time'] = current_versions['check_time']

            print("=" * 70)
            print("🎉 发现更新!")
            print("=" * 70)

            if updated_platforms:
                print()
                print("📦 已更新的平台:")
                for info in updated_platforms:
                    print(f"\n   {info['platform']}:")
                    print(f"   • 版本: {info['old_version']} → {info['new_version']}")
                    if info['download_url']:
                        print(f"   • 直接下载: {info['download_url']}")
                    print(f"   • 官网下载: {REPLAY_URL}?platform={info['download_param']}")

            if new_platforms:
                print()
                print("🆕 新增平台:")
                for platform in new_platforms:
                    print(f"   • {platform}")

            print()

            # GitHub Actions 输出
            if os.getenv('GITHUB_OUTPUT'):
                with open(os.getenv('GITHUB_OUTPUT'), 'a') as f:
                    f.write(f"has_updates=true\n")
                    f.write(f"updated_count={len(updated_platforms)}\n")

                    # 生成更新摘要
                    if updated_platforms:
                        platforms_list = ', '.join([p['platform'] for p in updated_platforms])
                        f.write(f"updated_platforms={platforms_list}\n")

                        # 详细信息
                        updates_json = json.dumps(updated_platforms, ensure_ascii=False)
                        f.write(f"updates_json={updates_json}\n")
        else:
            print("✅ 所有平台版本均无变化")
            print()

            if os.getenv('GITHUB_OUTPUT'):
                with open(os.getenv('GITHUB_OUTPUT'), 'a') as f:
                    f.write(f"has_updates=false\n")
                    f.write(f"updated_count=0\n")
    else:
        # 首次运行，使用当前获取的所有版本信息
        final_versions = current_versions
        print("📝 首次检查,记录所有平台的当前版本")
        print()

        if os.getenv('GITHUB_OUTPUT'):
            with open(os.getenv('GITHUB_OUTPUT'), 'a') as f:
                f.write(f"has_updates=false\n")
                f.write(f"is_first_run=true\n")

    # 保存最终版本数据（只包含真正更新的内容）
    save_current_versions(final_versions)

    print("=" * 70)
    print("✅ 全平台检查完成")
    print("=" * 70)

    return 0

if __name__ == "__main__":
    exit(main())