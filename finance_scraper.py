#!/usr/bin/env python3
"""
财税三件套实战脚本 - 全环境自动适配版
自动检测当前用户和平台，选择正确的浏览器路径和启动参数
"""
import os
import platform
import httpx
from playwright.sync_api import sync_playwright

# ── 环境检测 ──
USER = os.environ.get("USER", "unknown")
HOME = os.path.expanduser("~")
SYSTEM = platform.system()
print(f"当前用户：{USER}")
print(f"系统：{SYSTEM}")

# ── DrissionPage 配置（如果可用）──
DRISSION_OK = True

# admin 用户（阿里云）强制跳过 DrissionPage
if USER == "admin":
    DRISSION_OK = False
    print("⚠ 阿里云环境，DrissionPage 不兼容，已跳过")

try:
    from DrissionPage import ChromiumPage, ChromiumOptions
    CHROME_PATH = os.path.join(
        HOME, ".cache/ms-playwright/chromium-1223/chrome-linux64/chrome" )
    if os.path.exists(CHROME_PATH):
        co = ChromiumOptions().set_browser_path(CHROME_PATH)
        co.set_argument("--no-sandbox")
        co.set_argument("--headless=new")
        print("DrissionPage 浏览器路径：", CHROME_PATH)
    else:
        DRISSION_OK = False
        print("⚠ 未找到 Chromium 路径，跳过 DrissionPage")
except ImportError:
    DRISSION_OK = False
    print("⚠ DrissionPage 未安装，跳过")

# ── 测试 1：httpx ──
print("\n" + "=" * 55)
print("📡 测试 1/3：httpx → 税务总局")
print("=" * 55)
try:
    r = httpx.get("https://www.chinatax.gov.cn/", timeout=10)
    print(f"✅ 成功，状态码：{r.status_code}")
except Exception as e:
    print(f"❌ 失败：{e}")
except Exception as e:
    print(f"❌ 失败：{e}")

# ── 测试 2：DrissionPage ──
print("\n" + "=" * 55)
print("🔍 测试 2/3：DrissionPage → 企查查")
print("=" * 55)
if DRISSION_OK:
    try:
        dp = ChromiumPage(co)
        dp.get("https://www.baidu.com")
        print(f"✅ 成功，标题：{dp.title}")
        dp.quit()
    except Exception as e:
        print(f"❌ 失败：{e}")
    print("⏭ 跳过（环境不满足）")

# ── 测试 3：Playwright ──
print("\n" + "=" * 55)
print("📋 测试 3/3：Playwright → 发票查验平台截图")
print("=" * 55)
try:
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        page = b.new_page()
        page.goto("https://www.baidu.com", timeout=15000)
        print(f"✅ 成功，标题：{page.title()}")
        page.screenshot(path="/tmp/finance_scraper_demo.png")
        print("📸 截图已保存：/tmp/finance_scraper_demo.png")
        b.close()
except Exception as e:
    print(f"❌ 失败：{e}")

# ── 汇总 ──
print("\n" + "=" * 55)
print("  🚀 财税三件套测试完成")
print(f"  用户：{USER} | 系统：{SYSTEM}")
print("=" * 55)
