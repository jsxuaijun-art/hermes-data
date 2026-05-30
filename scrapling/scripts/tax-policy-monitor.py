#!/usr/bin/env python3
"""
国家税务总局 - 最新政策文件采集脚本
====================================
功能：抓取税务总局最新文件列表，输出标题、链接、发布日期
用法：source ~/scrapling-env/bin/activate && python scripts/tax-policy-monitor.py

输出格式：
  [日期] 标题
  链接: https://...

可搭配 Hermes cron 实现每日自动监控（推送到企业微信）
"""

from scrapling.fetchers import Fetcher
from datetime import datetime
import re
import sys

# ====== 配置区 ======
BASE_URL = "https://www.chinatax.gov.cn"
LIST_URL = BASE_URL + "/chinatax/n810341/n810755/index.html"
MAX_ITEMS = 30          # 最多显示多少条


def fetch_policy_list():
    """抓取最新文件列表"""
    print(f"📡 正在抓取: {LIST_URL}")
    p = Fetcher.get(LIST_URL)
    
    # 定位列表区域
    list_area = p.css("div.common_list")
    if not list_area:
        print("❌ 未找到政策列表区域，页面结构可能已变更")
        return []
    
    links = list_area[0].css("a")
    
    policies = []
    for a in links:
        text = a.text.strip() if a.text else ""
        href = a.attrib.get("href", "")
        
        # 过滤掉导航链接和空文本
        skip_words = ["最新文件", "首页", "上一页", "下一页", "尾页", "末页"]
        if not text or text in skip_words:
            continue
        
        # 补全相对链接
        if href.startswith("/"):
            full_url = BASE_URL + href
        elif href.startswith("http"):
            full_url = href
        else:
            continue
        
        # 尝试从URL或文本中提取日期
        date = extract_date(text, href)
        
        policies.append({
            "title": text.strip(),
            "url": full_url,
            "date": date,
        })
    
    return policies


def extract_date(text, href):
    """从标题或URL中提取日期"""
    # 尝试从文本中提取年份
    year_match = re.search(r"20\d{2}年", text)
    if year_match:
        return year_match.group(0)
    
    # 尝试从URL的c数字编号中推断（不准确，仅作参考）
    id_match = re.search(r"c(\d{10})", href)
    if id_match:
        # 编号通常是时间戳格式
        return "（含时间戳）"
    
    return ""


def fetch_detail(policy):
    """抓取政策详情页的发布日期"""
    try:
        p = Fetcher.get(policy["url"])
        
        # 常见发布日期位置
        date_selectors = [
            "span[class*=date]", "span[class*=time]",
            "div[class*=date]", "div[class*=time]",
            "p[class*=date]", "p[class*=time]",
            "em[class*=date]", "em[class*=time]",
            "div.bt",           # 税务总局页面常用的顶部信息栏
            "div.info",
        ]
        
        for sel in date_selectors:
            elements = p.css(sel)
            for el in elements:
                date_text = el.text.strip() if el.text else ""
                if re.search(r"20\d{2}", date_text):
                    # 只保留日期部分
                    date_match = re.search(r"20\d{2}[-年]\d{1,2}[-月]\d{1,2}[日号]?", date_text)
                    if date_match:
                        return date_match.group(0)
                    return date_text[:30]
        
        return ""
    except Exception as e:
        return ""


def main():
    print("=" * 60)
    print("  国家税务总局 · 最新政策文件监控")
    print(f"  抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    # 抓取列表
    policies = fetch_policy_list()
    
    if not policies:
        print("⚠️ 未获取到政策列表")
        sys.exit(1)
    
    print(f"\n📋 共获取 {len(policies)} 条政策文件")
    print("-" * 60)
    
    # 打印列表
    for i, p in enumerate(policies[:MAX_ITEMS], 1):
        date_str = f"[{p['date']}] " if p['date'] else ""
        print(f"{i:2d}. {date_str}{p['title']}")
        print(f"    {p['url']}")
        print()
    
    # 统计
    print("-" * 60)
    print(f"✅ 采集完成，共 {len(policies)} 条")
    print(f"💡 提示: 搭配 Hermes cron 可实现每日自动监控")


if __name__ == "__main__":
    main()
