#!/usr/bin/env python3
"""
Hermes 爬虫工具集 — 环境验证脚本
验证 DrissionPage + scrapling + curl_cffi + Playwright 全部就绪

用法: 在 Hermes 主环境下 python scripts/test-scrapling.py
"""

import importlib
import sys

PKGS = [
    ("DrissionPage", "DrissionPage", "多线程/多标签浏览器自动化"),
    ("scrapling", "scrapling", "自适应智能爬虫（55K+ Stars）"),
    ("curl_cffi", "curl_cffi", "TLS 指纹模拟（curl-impersonate Python 版）"),
    ("playwright", "playwright", "微软浏览器自动化框架"),
]

print("=" * 55)
print("  Hermes 爬虫工具集 — 环境验证")
print("=" * 55)

all_ok = True
for pkg_name, mod_name, desc in PKGS:
    try:
        ver = importlib.metadata.version(pkg_name)
        print(f"  ✅ {pkg_name:15s} v{ver:<12s} {desc}")
    except ImportError:
        print(f"  ❌ {pkg_name:15s} {'未安装':<14s} {desc}")
        all_ok = False
    except importlib.metadata.PackageNotFoundError:
        print(f"  ❌ {pkg_name:15s} {'未安装':<14s} {desc}")
        all_ok = False

# 额外检查：DrissionPage 的 Chromium 页面能否导入
print()
print("  🔍 深度模块导入测试...")
try:
    from DrissionPage import ChromiumPage
    print(f"  ✅ DrissionPage.ChromiumPage   — 浏览器控制引擎可用")
except Exception as e:
    print(f"  ⚠️  ChromiumPage 导入失败: {e}")

try:
    from scrapling.fetchers import Fetcher, StealthyFetcher
    print(f"  ✅ scrapling.Fetcher/StealthyFetcher — 爬虫引擎可用")
except Exception as e:
    print(f"  ⚠️  scrapling 导入失败: {e}")

try:
    from curl_cffi import requests as curl_requests
    r = curl_requests.get("https://httpbin.org/headers", impersonate="chrome110")
    print(f"  ✅ curl_cffi (impersonate=chrome110) — TLS 指纹模拟可用 (HTTP {r.status_code})")
except Exception as e:
    print(f"  ⚠️  curl_cffi 测试失败: {e}")

try:
    from playwright.sync_api import sync_playwright
    print(f"  ✅ playwright.sync_api — 浏览器自动化框架可用")
except Exception as e:
    print(f"  ⚠️  playwright 导入失败: {e}")

print()
if all_ok:
    print("=" * 55)
    print("  ✅ 全部正常，可以开始编写爬虫脚本了！")
    print("=" * 55)
else:
    print("  ⚠️  部分工具未安装，请运行: bash scrapling/setup.sh")
    sys.exit(1)