#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把排版主题 CSS 内联进已发布草稿并回写（draft/update）。

为什么需要：wenyan publish 的 -c 自定义主题在本机版本不会内联样式（render/publish 回读
均 0 个 style 块、标题纯 <h2>），微信又剥离 <style>，导致 02 刘润等风格预览里完全不生效。

用法：
    python3 inline_theme.py <media_id> [css路径]
    # css 默认 /etc/wenyan/themes/02-liurun-honglan.css

要点：
  - token 用 cgi-bin/stable_token（force:false），不要用 cgi-bin/token，否则会顶掉
    wenyan serve 的缓存 token，publish 报 40001。
  - 容器级选择器（.rich_media_content { ... }）不做内联，否则会给每个元素塞一堆重复声明。
  - 跑完必须看回读校验：颜色命中数、img 数（正文图+二维码，缺一张就是 lxml 或微信丢了图）。
"""
import json, re, sys, urllib.request

ENVF = "/etc/wenyan/.env"
MEDIA_ID = sys.argv[1]
CSS = sys.argv[2] if len(sys.argv) > 2 else "/etc/wenyan/themes/02-liurun-honglan.css"


def env(k):
    for line in open(ENVF, encoding="utf-8", errors="ignore"):
        line = line.strip()
        if line.startswith(k + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def api(url, payload=None):
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8", "ignore"))


token = api("https://api.weixin.qq.com/cgi-bin/stable_token",
            {"grant_type": "client_credential", "appid": env("WECHAT_APP_ID"),
             "secret": env("WECHAT_APP_SECRET"), "force": False})["access_token"]

d = api("https://api.weixin.qq.com/cgi-bin/draft/get?access_token=" + token, {"media_id": MEDIA_ID})
art = d["news_item"][0]
html = art["content"]
print("原正文长度:", len(html), "| 原 inline style 数:", len(re.findall(r'style="', html)))

css = open(CSS, encoding="utf-8").read()
css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
rules = []
for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
    decls = [p.replace("!important", "").strip() for p in body.split(";") if ":" in p]
    if not decls:
        continue
    for one in sel.split(","):
        one = one.replace(".rich_media_content", "").strip()
        if not one:            # 容器级规则不内联
            continue
        m = re.match(r"^([a-zA-Z][\w-]*)?((?:\.[\w-]+)*)$", one)
        if m:
            rules.append((m.group(1), [c for c in (m.group(2) or "").split(".") if c], decls))
print("可用样式规则:", len(rules))

from lxml import html as LH
root = LH.fromstring("<div id='__root__'>" + html + "</div>")
applied = 0
for el in root.iter():
    if not isinstance(el.tag, str):
        continue
    tag = el.tag.lower()
    cls = (el.get("class") or "").split()
    toadd = []
    for rtag, rcls, decls in rules:
        if rtag and rtag != tag:
            continue
        if rcls and any(c not in cls for c in rcls):
            continue
        toadd.extend(decls)
    if toadd:
        old = (el.get("style") or "").strip().rstrip(";")
        el.set("style", (old + ";" if old else "") + ";".join(toadd))
        applied += 1
new_html = "".join(LH.tostring(c, encoding="unicode") for c in root)
print("应用样式的元素数:", applied,
      "| img 前后:", len(re.findall(r"<img", html)), "->", len(re.findall(r"<img", new_html)))

payload = {"media_id": MEDIA_ID, "index": 0, "articles": {
    "title": art["title"], "author": art.get("author", ""), "digest": art.get("digest", ""),
    "content": new_html, "content_source_url": art.get("content_source_url", ""),
    "thumb_media_id": art["thumb_media_id"], "need_open_comment": 1, "only_fans_can_comment": 0}}
print("update 结果:", api("https://api.weixin.qq.com/cgi-bin/draft/update?access_token=" + token, payload))

h2 = api("https://api.weixin.qq.com/cgi-bin/draft/get?access_token=" + token,
         {"media_id": MEDIA_ID})["news_item"][0]["content"]
print("回读 inline:", len(re.findall(r'style="', h2)),
      "| 蓝色:", len(re.findall(r"color:\s*#0052FF", h2, re.I)),
      "| 红色:", len(re.findall(r"color:\s*#FF2941", h2, re.I)),
      "| 图片数:", len(re.findall(r"<img", h2)))
m = re.search(r"<h2[^>]*>", h2)
print("h2 片段:", m.group(0)[:180] if m else None)
