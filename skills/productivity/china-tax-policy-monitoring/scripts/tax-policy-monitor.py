#!/usr/bin/env python3
"""
国家税务总局 - 最新政策文件采集脚本
功能：抓取税务总局最新文件列表
用法：source ~/scrapling-env/bin/activate && python scripts/tax-policy-monitor.py
"""
from scrapling.fetchers import Fetcher
from datetime import datetime
import re
import sys

BASE_URL = "https://www.chinatax.gov.cn"
LIST_URL = BASE_URL + "/chinatax/n810341/n810755/index.html"
MAX_ITEMS = 30

def fetch_policy_list():
    print(f"📡 正在抓取: {LIST_URL}")
    p = Fetcher.get(LIST_URL)
    list_area = p.css("div.common_list")
    if not list_area:
        print("❌ 未找到政策列表区域")
        return []
    links = list_area[0].css("a")
    policies = []
    for a in links:
        text = a.text.strip() if a.text else ""
        href = a.attrib.get("href", "")
        skip_words = ["最新文件", "首页", "上一页", "下一页", "尾页", "末页"]
        if not text or text in skip_words:
            continue
        full_url = (BASE_URL + href) if href.startswith("/") else href
        date = ""
        year_match = re.search(r"20\d{2}年", text)
        if year_match:
            date = year_match.group(0)
        policies.append({"title": text.strip(), "url": full_url, "date": date})
    return policies

def main():
    print("=" * 60)
    print("  国家税务总局 · 最新政策文件监控")
    print(f"  抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    policies = fetch_policy_list()
    if not policies:
        print("⚠️ 未获取到政策列表")
        sys.exit(1)
    print(f"\n📋 共获取 {len(policies)} 条政策文件")
    print("-" * 60)
    for i, p in enumerate(policies[:MAX_ITEMS], 1):
        date_str = f"[{p['date']}] " if p['date'] else ""
        print(f"{i:2d}. {date_str}{p['title']}")
        print(f"    {p['url']}")
        print()
    print("-" * 60)
    print(f"✅ 采集完成，共 {len(policies)} 条")

if __name__ == "__main__":
    main()
