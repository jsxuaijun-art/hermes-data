#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tax policy monitor - State Taxation Administration"""
from scrapling.fetchers import Fetcher
from datetime import datetime
import re, sys

BASE_URL = "https://www.chinatax.gov.cn"
LIST_URL = BASE_URL + "/chinatax/n810341/n810755/index.html"
MAX_ITEMS = 30

def fetch_policy_list():
    p = Fetcher.get(LIST_URL)
    list_area = p.css("div.common_list")
    if not list_area:
        print("No list area found")
        return []
    links = list_area[0].css("a")
    policies = []
    for a in links:
        text = a.text.strip() if a.text else ""
        href = a.attrib.get("href", "")
        if not text or len(text) < 8:
            continue
        if not href.startswith("/"):
            continue
        full_url = BASE_URL + href
        ym = re.search(r"20\d{2}年", text)
        date = ym.group(0) if ym else ""
        policies.append({"title": text.strip(), "url": full_url, "date": date})
    return policies

def main():
    print("=" * 60)
    print("  国家税务总局 . 最新政策文件监控")
    print("  抓取时间: " + datetime.now().strftime("%Y-%m-%d %H:%M"))
    print("=" * 60)
    policies = fetch_policy_list()
    if not policies:
        print("No policies found")
        return
    print()
    print("共获取 " + str(len(policies)) + " 条政策文件")
    print("-" * 60)
    for i, p in enumerate(policies[:MAX_ITEMS], 1):
        title = p["title"]
        url = p["url"]
        date_str = "[" + p["date"] + "] " if p["date"] else ""
        print(str(i).rjust(2) + ". " + date_str + title)
        print("    " + url)
        print()
    print("-" * 60)
    print("采集完成，共 " + str(len(policies)) + " 条")

if __name__ == "__main__":
    main()