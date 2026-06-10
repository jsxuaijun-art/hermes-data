#!/usr/bin/env python3
import httpx
from playwright.sync_api import sync_playwright

print("=" * 55)
print("  财税三件套实战脚本（阿里云版）")
print("=" * 55)

print("\n📡 httpx 测试")
try:
    r = httpx.get("https://www.chinatax.gov.cn/", timeout=10)
    print(f"✅ 成功，状态码：{r.status_code}")
except Exception as e:
    print(f"❌ 失败：{e}")

print("\n📋 Playwright 测试")
try:
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        page = b.new_page()
        page.goto("https://www.baidu.com", timeout=15000)
        print(f"✅ 成功，标题：{page.title()}")
        b.close()
except Exception as e:
    print(f"❌ 失败：{e}")

print("\n✅ 全部演示完成")
