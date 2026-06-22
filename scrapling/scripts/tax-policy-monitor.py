python
    #!/usr/bin/env python3
    -- coding: utf-8 --
    """
    税务政策监控 - 国家税务总局 (Obsidian 集成版)
    """

    from scrapling.fetchers import Fetcher
    from datetime import datetime
    import re, os

    ===== 配置 =====
    OBSIDIAN_VAULT = "/mnt/d/ObsidianVault"
    POLICY_DIR = os.path.join(OBSIDIAN_VAULT, "02-政策法规")
    BASE_URL = "https://www.chinatax.gov.cn"
    LIST_URL = BASE_URL + "/chinatax/n810341/n810755/index.html"
    MAX_ITEMS = 30


    def slugify(title):
        name = re.sub(r'[\\/:*?"<>|]', '', title)
        name = re.sub(r'\s+', '_', name)
        return name[:80]


    def is_duplicate(title):
        if not os.path.exists(POLICY_DIR):
            return False
        for f in os.listdir(POLICY_DIR):
            if f.endswith('.md') and title[:20] in f:
                return True
        return False


    def save_to_obsidian(policy):
        os.makedirs(POLICY_DIR, exist_ok=True)
        title = policy['title']
        url = policy['url']
        date = policy['date']
        if date:
            date_prefix = date.replace('年', '').replace('月', '').replace('日', '')
        else:
            date_prefix = datetime.now().strftime('%Y%m%d')
        filename = f"{date_prefix}_{slugify(title)[:60]}.md"
        filepath = os.path.join(POLICY_DIR, filename)
        if os.path.exists(filepath):
            return False
        note = f"""---
    title: {title}
    source: {url}
    date: {date or '未知'}
    fetched: {datetime.now().strftime('%Y-%m-%d %H:%M')}
    tags: [政策法规, 税务总局]


    {title}

    > 🔗 原文: {url}
    > 📅 发布时间: {date or '未知'}



    摘要

    <!-- 待补充 -->

    对我司客户的影响

    - [ ]

    行动项

    - [ ] 通知相关客户
    - [ ] 更新知识库

    相关链接

    - [[相关客户]]
    """
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(note)
        return True


    def fetch_policy_list():
        p = Fetcher.get(LIST_URL)
        list_area = p.css("div.common_list")
        if not list_area:
            print("未找到政策列表区域")
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
        print("  国家税务总局 · 最新政策监控 → Obsidian")
        print(f"  抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("=" * 60)

        policies = fetch_policy_list()
        if not policies:
            print("\n未获取到政策")
            return

        print(f"\n共获取 {len(policies)} 条政策")

        new_count = 0
        skip_count = 0
        for i, p in enumerate(policies[:MAX_ITEMS], 1):
            title = p["title"]
            date_str = f"[{p['date']}] " if p['date'] else ""
            print(f"  {i:2d}. {date_str}{title[:55]}...")
            if is_duplicate(title):
                skip_count += 1
                print(f"       -> 跳过（已存在）")
            else:
                if save_to_obsidian(p):
                    new_count += 1
                    print(f"       -> 已保存到 Obsidian")
                else:
                    skip_count += 1
                    print(f"       -> 跳过")

        print("-" * 60)
        print(f"新增: {new_count} 条 | 跳过: {skip_count} 条")
        print("完成")


    if name == "main":
        main()
