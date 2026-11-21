#!/usr/bin/env python3
"""
苏州政策监控 — anysearch 定时搜索 → 素材库去重入库 → 新文号即 NEW。
城市破播（short-video-city-breakout）的政策第一手抓取脚本。
2026.9 实测：6 路关键词 9.5 秒抓 29 个唯一政策源，含文号/日期/官方 URL。

用法：python3 sz_policy_monitor.py
素材库：<HERMES_HOME>/city-breakout/sz_policy_lib.json
待徐总定 cron 频率+推送渠道后，用 hermes cron 挂起；未挂载前每次会话手动跑一次。
"""
import subprocess, json, os, re, datetime, pathlib

# 素材库（HERMES_HOME 感知，profile 兼容）
LIB = pathlib.Path(os.environ.get("HERMES_HOME", str(pathlib.Path.home() / ".hermes"))) / "city-breakout" / "sz_policy_lib.json"
ANYSEARCH = os.environ.get("ANYSEARCH_CLI", str(pathlib.Path.home() / ".hermes/skills/anysearch/scripts/anysearch_cli.py"))
# WSL Hermes venv（与 anysearch 依赖同环境）
PY = os.environ.get("HERMES_PY", "/home/administrator/hermes-agent/venv/bin/python3")

# 监控关键词队列（每个 = 一个城市破播子模块方向；新增政策方向在此追加）
QUERIES = [
    "苏州 优惠政策 补贴 2026",
    "苏州 低空经济 实施方案",
    "苏州 营商环境 举措",
    "苏州 企业开办 一件事 名称核准",
    "苏州 外商投资 利润再投资",
    "苏州 创新创业 领军人才 补贴",
]


def load_lib():
    if LIB.exists():
        return json.loads(LIB.read_text(encoding="utf-8"))
    return {"seen": {}, "items": []}


def search(q, max_results=5):
    cmd = [PY, ANYSEARCH, "batch_search", "--queries",
           json.dumps([{"query": q, "max_results": max_results}])]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        return r.stdout
    except Exception as e:
        return f"ERROR {e}"


def parse_results(text):
    """从 anysearch 纯文本输出里抽出 (标题, URL, 摘要, 日期)。"""
    items = []
    blocks = re.split(r"### \d+\.\s*", text)
    for b in blocks[1:]:
        lines = [l.strip() for l in b.splitlines() if l.strip()]
        if not lines:
            continue
        title = lines[0].replace("**", "").strip()
        url, date = "", ""
        for l in lines:
            m = re.match(r"^- \*\*URL\*\*: (.+)$", l)
            if m:
                url = m.group(1).strip()
            if "date:" in l.lower():
                dm = re.search(r"date:\s*([\w\-\s]+)", l)
                if dm:
                    date = dm.group(1).strip()
        if title and url:
            items.append({"title": title, "url": url, "date": date})
    return items


def key_of(title, url):
    """去重键：文号优先（〔20XX〕N），否则截断标题（前20字）。"""
    hao = re.search(r"〔\d{4}〕\s*\d+", title)
    if hao:
        return f"wj:{hao.group(0)}"
    return f"url:{title[:20]}"


def run():
    lib = load_lib()
    new_found, total = [], 0
    for q in QUERIES:
        out = search(q)
        items = parse_results(out)
        total += len(items)
        for it in items:
            k = key_of(it["title"], it["url"])
            if k not in lib["seen"]:
                lib["seen"][k] = {"q": q, "first_seen": datetime.datetime.now().isoformat()}
                it["query"] = q
                lib["items"].append(it)
                new_found.append(it)
        print(f"[{q}] -> {len(items)} 条，去重后已收 {len(lib['seen'])} 个唯一源")
    LIB.parent.mkdir(parents=True, exist_ok=True)
    LIB.write_text(json.dumps(lib, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n采购入库: 本次新发现 {len(new_found)} 条 / 累积唯一源 {len(lib['seen'])}")
    for it in new_found[:10]:
        print(f"  NEW: {it['title'][:40]} | {it['url'][:60]}")


if __name__ == "__main__":
    run()