#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""奇云解析 + 多组请求头试下载（通用；重点解决抖音 CDN 403）

背景：奇云 /api/video 接口**同时支持抖音**（不止视频号），返回 code=200 与无水印直链。
但抖音直链（*.douyinvod.com）对 Referer/UA 敏感，带微信 Referer 会 403。
本脚本自动依次尝试多组请求头，首个成功即落盘。

用法：
  python3 download_any_qiyun.py <链接> <输出.mp4>
凭据：环境变量 QIYUN_APP_ID / QIYUN_APP_KEY（本机密钥文件已配）
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

# 清空本地代理，避免死代理拦截
for _k in ("HTTPS_PROXY", "HTTP_PROXY", "ALL_PROXY", "https_proxy", "http_proxy", "all_proxy"):
    os.environ.pop(_k, None)

APP_ID = os.environ.get("QIYUN_APP_ID", "")
APP_KEY = os.environ.get("QIYUN_APP_KEY", "")
if len(sys.argv) < 3:
    print("用法: python3 download_any_qiyun.py <链接> <输出.mp4>"); sys.exit(1)
url, out = sys.argv[1], sys.argv[2]
if not (APP_ID and APP_KEY):
    print("错误：未配置 QIYUN_APP_ID / QIYUN_APP_KEY"); sys.exit(1)

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0 Safari/537.36")

api = "https://qyapi.ipaybuy.cn/api/video?" + urllib.parse.urlencode(
    {"appId": APP_ID, "appKey": APP_KEY, "url": url})
with urllib.request.urlopen(urllib.request.Request(api, headers={"User-Agent": UA}), timeout=30) as r:
    res = json.loads(r.read().decode("utf-8"))
print("code:", res.get("code"), "| msg:", res.get("msg"))
d = res.get("data") or {}
print("标题:", d.get("title"))
link = d.get("mediaUrl") or d.get("video_url") or d.get("video_url_v2")
if str(res.get("code")) != "200" or not link:
    print("解析失败/无地址:", json.dumps(d, ensure_ascii=False)[:300]); sys.exit(1)

os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
# 依次尝试的请求头组合（抖音用 douyin Referer；视频号用微信 Referer 亦可）
referer = "https://www.douyin.com/" if "douyin" in url or "douyinvod" in link else "https://weixin.qq.com/"
tries = [
    ("对应平台 Referer", {"User-Agent": UA, "Referer": referer}),
    ("仅 UA", {"User-Agent": UA}),
    ("douyin Referer", {"User-Agent": UA, "Referer": "https://www.douyin.com/"}),
    ("Referer + Range", {"User-Agent": UA, "Referer": referer, "Range": "bytes=0-"}),
]
for name, hdr in tries:
    try:
        with urllib.request.urlopen(urllib.request.Request(link, headers=hdr), timeout=120) as r:
            data = r.read()
        if len(data) > 10000:
            with open(out, "wb") as f:
                f.write(data)
            print(f"下载成功[{name}] -> {out} ({len(data)} bytes)")
            sys.exit(0)
        print(f"  尝试[{name}]：内容过小 {len(data)}")
    except urllib.error.HTTPError as e:
        print(f"  尝试[{name}]：HTTP {e.code}")
    except Exception as e:
        print(f"  尝试[{name}]：{repr(e)[:120]}")
print("全部请求头组合均失败"); sys.exit(2)