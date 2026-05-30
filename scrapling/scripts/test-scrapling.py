#!/usr/bin/env python3
"""
Scrapling 环境验证脚本
运行方式: source ~/scrapling-env/bin/activate && python scripts/test-scrapling.py
"""
from scrapling.fetchers import Fetcher, StealthyFetcher
import importlib

print("═" * 50)
print("  Scrapling 环境验证")
print("═" * 50)

# 版本信息
print(f"\n📦 Scrapling:  v{importlib.metadata.version('scrapling')}")
print(f"📦 Playwright: v{importlib.metadata.version('playwright')}")

# 基础导入测试
print("\n🔍 模块导入测试:")
print(f"  Fetcher         ✅  基础 HTTP 请求")
print(f"  StealthyFetcher ✅  隐身浏览器自动化")
print(f"  Fetcher 类方法: {[m for m in dir(Fetcher) if not m.startswith('_')][:10]}...")

print("\n✅ 全部正常！")
print("═" * 50)
print("可以开始编写爬虫脚本了。")
print("示例: 税务政策监控、同行分析、定价采集等")
