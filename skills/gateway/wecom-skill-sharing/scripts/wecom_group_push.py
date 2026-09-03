#!/usr/bin/env python3
"""推送 markdown 摘要 + 多个文件到企微群机器人（实测跑通 2026.8.11，errcode 0）。

用法:
  python3 wecom_group_push.py --key <WEBHOOK_KEY> \
      --markdown "**📋 标题** 摘要正文" \
      --file /path/手册.docx --file /path/安装包.zip

说明:
  - 每个 --file 独立走 upload_media(type=file) -> media_id -> send file 消息
  - markdown 仅支持企微子集（标题/加粗/列表/引用，不支持表格）
  - 文件消息一次只发一个文件
  - webhook 只能单向推送，不能接收消息（交互式问答请走 AI 机器人）
"""
import argparse
import os
import sys

import requests

SEND_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send"
UPLOAD_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media"


def _check(rj: dict, what: str) -> None:
    if rj.get("errcode") != 0:
        print(f"失败({what}): {rj}")
        sys.exit(1)


def send_markdown(key: str, content: str) -> None:
    r = requests.post(
        f"{SEND_URL}?key={key}",
        json={"msgtype": "markdown", "markdown": {"content": content}},
        timeout=15,
    )
    _check(r.json(), "markdown")
    print("markdown 摘要: ok")


def push_file(key: str, path: str) -> None:
    fname = os.path.basename(path)
    with open(path, "rb") as f:
        r = requests.post(
            f"{UPLOAD_URL}?key={key}&type=file",
            files={"media": (fname, f, "application/octet-stream")},
            timeout=30,
        )
    up = r.json()
    _check(up, f"上传 {fname}")
    r2 = requests.post(
        f"{SEND_URL}?key={key}",
        json={"msgtype": "file", "file": {"media_id": up["media_id"]}},
        timeout=15,
    )
    _check(r2.json(), f"发送 {fname}")
    print(f"文件: {fname} ok")


def main() -> None:
    ap = argparse.ArgumentParser(description="推送 markdown + 文件到企微群机器人")
    ap.add_argument("--key", required=True, help="群机器人 webhook key")
    ap.add_argument("--markdown", default="", help="markdown 摘要内容")
    ap.add_argument("--file", action="append", default=[], help="要推送的文件（可多次）")
    a = ap.parse_args()

    if a.markdown:
        send_markdown(a.key, a.markdown)
    if not a.file:
        print("提示: 未指定 --file，只发了摘要。")
    for f in a.file:
        if not os.path.exists(f):
            print(f"失败: 文件不存在 {f}")
            sys.exit(1)
        push_file(a.key, f)
    print("=== 全部完成 ===")


if __name__ == "__main__":
    main()
