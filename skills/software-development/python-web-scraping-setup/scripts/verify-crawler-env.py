#!/usr/bin/env python3
"""
爬虫环境验证脚本 — 检测核心工具（Playwright + Scrapy + Requests/BS4）及拓展工具（DrissionPage + scrapling）

用法：
    python3 scripts/verify-crawler-env.py

返回码：0 = 核心全部通过, 1 = 核心有失败项
"""

import subprocess
import sys


def check_requests_bs4():
    """验证 Requests + BeautifulSoup"""
    try:
        import requests
        from bs4 import BeautifulSoup

        r = requests.get("https://www.baidu.com", timeout=5)
        soup = BeautifulSoup(r.text, "lxml")
        title = soup.title.text.strip()
        print(f"  ✅ Requests {requests.__version__} + BS4 OK (title: {title[:20]})")
        return True
    except Exception as e:
        print(f"  ❌ Requests/BS4 失败: {e}")
        return False


def check_scrapy():
    """验证 Scrapy CLI"""
    try:
        result = subprocess.run(
            ["scrapy", "version"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            ver = result.stdout.strip()
            print(f"  ✅ Scrapy {ver} OK")
            return True
        else:
            print(f"  ❌ Scrapy CLI 报错: {result.stderr.strip()}")
            return False
    except FileNotFoundError:
        print("  ❌ scrapy 命令未找到")
        return False
    except Exception as e:
        print(f"  ❌ Scrapy 检查异常: {e}")
        return False


def check_playwright():
    """验证 Playwright + Chromium 浏览器"""
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://www.baidu.com")
            title = page.title()
            browser.close()
        print(f"  ✅ Playwright OK (chromium, title: {title[:20]})")
        return True
    except ImportError:
        print("  ❌ playwright Python 包未安装")
        return False
    except Exception as e:
        msg = str(e)
        if "Executable doesn't exist" in msg:
            print("  ❌ Playwright 浏览器二进制文件未安装 (需运行: playwright install chromium)")
        elif "cannot open shared object file" in msg:
            print("  ❌ 系统依赖缺失 (需安装: libasound2, libgtk-3-0 等)")
        else:
            print(f"  ❌ Playwright 启动失败: {msg}")
        return False


def check_drissionpage():
    """验证 DrissionPage（可选拓展）"""
    try:
        import DrissionPage
        print(f"  ✅ DrissionPage {getattr(DrissionPage, '__version__', 'OK')}")
        return True
    except ImportError:
        print("  ⏭️   DrissionPage 未安装（可选拓展）")
        return None  # None = 跳过，不计入核心结果
    except Exception as e:
        print(f"  ⚠️   DrissionPage 异常: {e}")
        return None


def check_scrapling():
    """验证 scrapling（可选拓展）"""
    try:
        import scrapling
        print(f"  ✅ scrapling {getattr(scrapling, '__version__', 'OK')}")
        return True
    except ImportError:
        print("  ⏭️   scrapling 未安装（可选拓展）")
        return None
    except Exception as e:
        print(f"  ⚠️   scrapling 异常: {e}")
        return None


def main():
    print("=" * 52)
    print("  爬虫工具 — 环境验证（核心 + 拓展）")
    print("=" * 52)

    core_results = [
        ("Requests + BeautifulSoup", check_requests_bs4()),
        ("Scrapy", check_scrapy()),
        ("Playwright", check_playwright()),
    ]

    extra_results = [
        ("DrissionPage", check_drissionpage()),
        ("scrapling", check_scrapling()),
    ]

    print("=" * 52)
    core_passed = sum(1 for _, ok in core_results if ok)
    core_total = len(core_results)
    extra_installed = sum(1 for _, ok in extra_results if ok is True)
    extra_total = sum(1 for _, ok in extra_results if ok is not None)

    if core_passed == core_total:
        if extra_installed == 0 and extra_total == 0:
            print(f"  ✅ 核心全部通过 ({core_passed}/{core_total}) — 环境就绪")
            print(f"  ℹ️  拓展工具 (2) 均未安装，按需安装")
        else:
            print(f"  ✅ 核心全部通过 ({core_passed}/{core_total}) — 环境就绪")
            print(f"  ✅ 拓展工具 {extra_installed}/2 已安装")
        return 0
    else:
        print(f"  ⚠️  核心 {core_passed}/{core_total} 通过 — 需修复以上失败项")
        return 1


if __name__ == "__main__":
    sys.exit(main())