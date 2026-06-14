#!/usr/bin/env python3
"""
财税情报推送模块 - 由cron任务或Hermes agent调用
读取报告文件并POST到企微推送端点
"""
import json
import urllib.request
import urllib.error
import sys

PUSH_URL = "https://callback.yingxinkuaiji.com/push"

def push_report(report_content, msgtype="markdown"):
    """推送报告到企微群
    Args:
        report_content: 报告内容 (string)
        msgtype: markdown 或 text
    Returns:
        dict with errcode and errmsg
    """
    # 截断（企微markdown上限4096字节，text上限2048字节）
    max_len = 4000 if msgtype == "markdown" else 2000
    if len(report_content) > max_len:
        report_content = report_content[:max_len] + "\n\n...（内容过长已截断，完整版请查看归档）"

    payload = json.dumps({
        "msgtype": msgtype,
        msgtype: {"content": report_content}
    }).encode("utf-8")

    req = urllib.request.Request(
        PUSH_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = resp.read().decode()
            return json.loads(result)
    except urllib.error.HTTPError as e:
        return {"errcode": e.code, "errmsg": e.read().decode()}
    except Exception as e:
        return {"errcode": -1, "errmsg": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python3 {sys.argv[0]} <report_file> [msgtype=markdown]")
        sys.exit(1)

    filepath = sys.argv[1]
    msgtype = sys.argv[2] if len(sys.argv) > 2 else "markdown"

    if filepath == "/dev/stdin":
        content = sys.stdin.read()
    else:
        with open(filepath, "r") as f:
            content = f.read()

    result = push_report(content, msgtype)
    print(json.dumps(result))
    sys.exit(0 if result.get("errcode") == 0 else 1)
