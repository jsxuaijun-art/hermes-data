---
name: scripts/verify-crawler-env
description: 爬虫环境验证脚本 — Playwright + Scrapy + Requests/BS4 核心 + DrissionPage/scrapling/curl_cffi/curl-impersonate 拓展
---

#!/usr/bin/env python3
"""
爬虫环境验证脚本 — 检测核心工具（Playwright + Scrapy + Requests/BS4）
及拓展工具（DrissionPage + scrapling + curl_cffi + curl-impersonate）

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
        return None
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


def check_curl_cffi():
    """验证 curl_cffi（可选拓展 — Python TLS 指纹伪装）"""
    try:
        import curl_cffi
        from curl_cffi import requests
        ver = getattr(curl_cffi, '__version__', 'OK')
        r = requests.get("https://httpbin.org/headers", impersonate="chrome110", timeout=10)
        ok = "✅" if r.status_code < 500 else "⚠️"
        print(f"  {ok} curl_cffi {ver} (httpbin status: {r.status_code})")
        return True
    except ImportError:
        print("  ⏭️   curl_cffi 未安装（可选拓展 — pip install curl_cffi）")
        return None
    except Exception as e:
        print(f"  ⚠️   curl_cffi 异常: {e}")
        return None


def check_curl_impersonate_binary():
    """验证 curl-impersonate 系统二进制（可选拓展）"""
    try:
        result = subprocess.run(
            ["curl-impersonate-chrome", "--version"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            ver = result.stdout.strip().split('\n')[0]
            print(f"  ✅ curl-impersonate-chrome {ver}")
            # 快速测试：访问一个 URL
            test = subprocess.run(
                ["curl-impersonate-chrome", "-sI", "--max-time", "5", "https://httpbin.org/headers"],
                capture_output=True, text=True, timeout=10
            )
            if test.returncode == 0:
                print(f"     快速测试通过 (HTTP {test.stdout.split()[1] if test.stdout else 'N/A'})")
            else:
                print(f"     ⚠️  快速测试失败: {test.stderr.strip()[:80]}")
            return True
        else:
            print(f"  ❌ curl-impersonate-chrome 返回异常: {result.stderr.strip()}")
            return False
    except FileNotFoundError:
        print("  ⏭️   curl-impersonate-chrome 未安装（可选系统工具）")
        return None
    except Exception as e:
        print(f"  ⚠️   curl-impersonate-chrome 检查异常: {e}")
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
        ("curl_cffi", check_curl_cffi()),
        ("curl-impersonate 系统二进制", check_curl_impersonate_binary()),
    ]

    print("=" * 52)
    core_passed = sum(1 for _, ok in core_results if ok)
    core_total = len(core_results)
    extra_installed = sum(1 for _, ok in extra_results if ok is True)
    extra_checked = sum(1 for _, ok in extra_results if ok is not None)

    if core_passed == core_total:
        print(f"  ✅ 核心全部通过 ({core_passed}/{core_total}) — 环境就绪")
    else:
        print(f"  ⚠️  核心 {core_passed}/{core_total} 通过 — 需修复以上失败项")

    if extra_installed > 0:
        print(f"  ✅ 拓展工具 {extra_installed}/{len(extra_results)} 已安装")
    else:
        print(f"  ℹ️  拓展工具 ({len(extra_results)}) 均未安装，按需安装")

    return 0 if core_passed == core_total else 1


if __name__ == "__main__":
    sys.exit(main())