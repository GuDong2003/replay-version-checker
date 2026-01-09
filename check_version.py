#!/usr/bin/env python3
"""
Replay Version Checker
检查 Replay 应用是否有新版本更新
"""

import re
import json
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup

REPLAY_URL = "https://www.weights.com/replay"
VERSION_FILE = "latest_version.json"

def fetch_page_content(url):
    """
    获取网页内容,使用浏览器 User-Agent
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0'
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"❌ 获取页面失败: {e}")
        return None

def extract_version(html_content):
    """
    从 HTML 内容中提取版本号
    尝试多种模式来匹配版本信息
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # 模式1: 查找包含 version 字样的文本
    version_patterns = [
        r'(?i)version\s*[:\-]?\s*(\d+\.\d+(?:\.\d+)?)',
        r'(?i)v(\d+\.\d+(?:\.\d+)?)',
        r'(?i)replay\s+(\d+\.\d+(?:\.\d+)?)',
        r'(\d+\.\d+\.\d+)',
    ]

    # 检查页面文本
    page_text = soup.get_text()
    for pattern in version_patterns:
        matches = re.findall(pattern, page_text)
        if matches:
            # 返回第一个匹配的版本号
            version = matches[0] if isinstance(matches[0], str) else matches[0][0]
            return version

    # 模式2: 查找下载链接中的版本号
    for link in soup.find_all('a', href=True):
        href = link['href']
        match = re.search(r'(\d+\.\d+\.\d+)', href)
        if match and ('download' in href.lower() or 'replay' in href.lower()):
            return match.group(1)

    # 模式3: 查找特定的 meta 标签或数据属性
    for meta in soup.find_all('meta'):
        content = meta.get('content', '')
        match = re.search(r'(\d+\.\d+\.\d+)', content)
        if match:
            return match.group(1)

    return None

def load_previous_version():
    """
    加载之前保存的版本信息
    """
    if os.path.exists(VERSION_FILE):
        try:
            with open(VERSION_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('version'), data.get('last_check')
        except Exception as e:
            print(f"⚠️  读取历史版本文件失败: {e}")
    return None, None

def save_current_version(version):
    """
    保存当前版本信息
    """
    data = {
        'version': version,
        'last_check': datetime.now().isoformat(),
        'url': REPLAY_URL
    }
    try:
        with open(VERSION_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ 版本信息已保存到 {VERSION_FILE}")
    except Exception as e:
        print(f"❌ 保存版本信息失败: {e}")

def compare_versions(v1, v2):
    """
    比较两个版本号
    返回: 1 如果 v1 > v2, -1 如果 v1 < v2, 0 如果相等
    """
    def normalize(v):
        return [int(x) for x in re.sub(r'[^0-9.]', '', v).split('.')]

    try:
        parts1 = normalize(v1)
        parts2 = normalize(v2)

        # 补齐长度
        max_len = max(len(parts1), len(parts2))
        parts1.extend([0] * (max_len - len(parts1)))
        parts2.extend([0] * (max_len - len(parts2)))

        for i in range(max_len):
            if parts1[i] > parts2[i]:
                return 1
            elif parts1[i] < parts2[i]:
                return -1
        return 0
    except Exception as e:
        print(f"⚠️  版本比较失败: {e}")
        return 0

def main():
    """
    主函数
    """
    print("=" * 50)
    print("🔍 Replay 版本检查工具")
    print("=" * 50)
    print(f"⏰ 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 检查网址: {REPLAY_URL}")
    print()

    # 获取网页内容
    print("📥 正在获取页面内容...")
    html_content = fetch_page_content(REPLAY_URL)

    if not html_content:
        print("❌ 无法获取页面内容,检查终止")
        return 1

    print(f"✅ 页面内容获取成功 (大小: {len(html_content)} 字节)")

    # 提取版本号
    print("🔍 正在提取版本号...")
    current_version = extract_version(html_content)

    if not current_version:
        print("❌ 无法从页面中提取版本号")
        print("💡 提示: 页面结构可能已更改,需要更新提取逻辑")
        return 1

    print(f"✅ 当前版本: {current_version}")

    # 加载历史版本
    previous_version, last_check = load_previous_version()

    if previous_version:
        print(f"📦 历史版本: {previous_version}")
        if last_check:
            print(f"🕐 上次检查: {last_check}")

        # 比较版本
        comparison = compare_versions(current_version, previous_version)

        if comparison > 0:
            print()
            print("🎉" * 25)
            print("🚀 发现新版本!")
            print(f"   旧版本: {previous_version}")
            print(f"   新版本: {current_version}")
            print(f"   下载地址: {REPLAY_URL}")
            print("🎉" * 25)

            # 保存新版本
            save_current_version(current_version)

            # 设置 GitHub Actions 输出
            if os.getenv('GITHUB_OUTPUT'):
                with open(os.getenv('GITHUB_OUTPUT'), 'a') as f:
                    f.write(f"new_version_available=true\n")
                    f.write(f"current_version={current_version}\n")
                    f.write(f"previous_version={previous_version}\n")

            return 0
        elif comparison < 0:
            print("⚠️  警告: 当前版本低于历史版本 (可能是页面提取错误)")
        else:
            print("✅ 版本未变化,无需更新")
    else:
        print("📝 首次检查,记录当前版本")
        save_current_version(current_version)

        # 设置 GitHub Actions 输出
        if os.getenv('GITHUB_OUTPUT'):
            with open(os.getenv('GITHUB_OUTPUT'), 'a') as f:
                f.write(f"new_version_available=false\n")
                f.write(f"current_version={current_version}\n")

    print()
    print("=" * 50)
    print("✅ 检查完成")
    print("=" * 50)

    return 0

if __name__ == "__main__":
    exit(main())