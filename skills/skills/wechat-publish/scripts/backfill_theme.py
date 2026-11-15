#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""给已有草稿补内联排版（修复历史上 -c 主题没生效的旧稿）。

与 inline_theme.py 的区别：
  1) 批量：一次传多个 media_id
  2) 先把正文里残留的字面 **xxx** 修成 <strong>xxx</strong>（markdown 没渲染的 bug）
  3) >28 字的 <strong> 不染红——02 刘润 CSS 会把所有 strong 变红，旧稿里有整句加粗（导语/金句），
     整段红字反而难读，这类保持黑色加粗
  4) 改动前把原始 article JSON 备份到 /root/draft_backup/<media_id>.json，可回滚

用法：
    python3 backfill_theme.py <media_id> [<media_id> ...] [--css /etc/wenyan/themes/02-liurun-honglan.css]

校验：末尾打印 文字一致 / 图片数 / 蓝红命中 / inline 数。
文字一致必须先把 &nbsp; 与 \\xa0 归一化再比，否则 lxml 会把 &nbsp; 转成 \\xa0 造成假失败。
"""
import json, os, re, sys, urllib.request
from lxml import html as LH

ENVF = "/etc/wenyan/.env"
BACKUP_DIR = "/root/draft_backup"
LONG_BOLD = 28

args = [a for a in sys.argv[1:] if not a.startswith("--")]
CSS = "/etc/wenyan/themes/02-liurun-honglan.css"
if "--css" in sys.argv:
    CSS = sys.argv[sys.argv.index("--css") + 1]
    args = [a for a in args if a != CSS]


def env(k):
    for line in open(ENVF, encoding="utf-8", errors="ignore"):
        line = line.strip()
        if line.startswith(k + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def api(url, payload=None):
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode("utf-8", "ignore"))


tok = api("https://api.weixin.qq.com/cgi-bin/stable_token",
          {"grant_type": "client_credential", "appid": env("WECHAT_APP_ID"),
           "secret": env("WECHAT_APP_SECRET"), "force": False})["access_token"]

css = re.sub(r"/\*.*?\*/", "", open(CSS, encoding="utf-8").read(), flags=re.S)
rules = []
for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
    decls = [p.replace("!important", "").strip() for p in body.split(";") if ":" in p]
    if not decls:
        continue
    for one in sel.split(","):
        one = one.replace(".rich_media_content", "").strip()
        if not one:
            continue
        m = re.match(r"^([a-zA-Z][\w-]*)?((?:\.[\w-]+)*)$", one)
        if m:
            rules.append((m.group(1), [c for c in (m.group(2) or "").split(".") if c], decls))


def plain(h):
    return re.sub(r"<[^>]+>", "", h).replace("&nbsp;", " ").replace("\xa0", " ")


os.makedirs(BACKUP_DIR, exist_ok=True)
for mid in args:
    art = api("https://api.weixin.qq.com/cgi-bin/draft/get?access_token=" + tok,
              {"media_id": mid})["news_item"][0]
    h0 = art["content"]
    json.dump(art, open(os.path.join(BACKUP_DIR, mid + ".json"), "w"), ensure_ascii=False)

    star = [0]
    def rep(m):
        star[0] += 1
        return "<strong>" + m.group(1) + "</strong>"
    h1 = re.sub(r"\*\*([^*<>]{1,60}?)\*\*", rep, h0)

    root = LH.fromstring("<div id='__root__'>" + h1 + "</div>")
    applied = skipped = 0
    for el in root.iter():
        if not isinstance(el.tag, str):
            continue
        tag = el.tag.lower()
        cls = (el.get("class") or "").split()
        txtlen = len((el.text_content() or "").strip())
        toadd = []
        for rtag, rcls, decls in rules:
            if rtag and rtag != tag:
                continue
            if rcls and any(c not in cls for c in rcls):
                continue
            if tag == "strong" and txtlen > LONG_BOLD:
                keep = [d for d in decls if not d.lower().startswith("color")]
                if len(keep) != len(decls):
                    skipped += 1
                decls = keep
            toadd.extend(decls)
        if toadd:
            old = (el.get("style") or "").strip().rstrip(";")
            el.set("style", (old + ";" if old else "") + ";".join(toadd))
            applied += 1
    h2 = "".join(LH.tostring(c, encoding="unicode") for c in root)

    payload = {"media_id": mid, "index": 0, "articles": {
        "title": art["title"], "author": art.get("author", ""), "digest": art.get("digest", ""),
        "content": h2, "content_source_url": art.get("content_source_url", ""),
        "thumb_media_id": art["thumb_media_id"],
        "need_open_comment": art.get("need_open_comment", 1),
        "only_fans_can_comment": art.get("only_fans_can_comment", 0)}}
    r = api("https://api.weixin.qq.com/cgi-bin/draft/update?access_token=" + tok, payload)

    v = api("https://api.weixin.qq.com/cgi-bin/draft/get?access_token=" + tok,
            {"media_id": mid})["news_item"][0]["content"]
    print("=" * 22, art["title"][:24])
    print("  update:", r.get("errmsg"), "| 星号修复:", star[0], "| 应用元素:", applied,
          "| 长加粗跳红:", skipped)
    print("  文字一致:", re.sub(r"\s+", "", plain(h0).replace("**", "")) == re.sub(r"\s+", "", plain(v)),
          "| 图片:", (h0.count("<img"), v.count("<img")),
          "| 蓝:", len(re.findall(r"color:\s*#0052FF", v, re.I)),
          "| 红:", len(re.findall(r"color:\s*#FF2941", v, re.I)),
          "| inline:", len(re.findall(r'style="', v)))
