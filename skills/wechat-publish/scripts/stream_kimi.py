#!/usr/bin/env python3
"""Streaming chat caller for long-form 公众号/文案 generation.

铁律：第三方网关（telecom aigw）非流式调用有 ~90s 响应上限，长稿会中途断 →
写长文必须 stream=true 直连，不要用 delegate_task（走非流式，易整体失败）。

Usage:
    stream_kimi.py <prompt_file> <out_file> [model]

Env (从 ~/.hermes/.env 加载，勿内联写死密钥):
    TELECOM_BASE_URL   e.g. https://aigw.telecomjs.com/v1
    TELECOM_KIMI_KEY   API key

模型路由：公众号长文 → kimi-k3（默认）；短文案 → Doubao-Seed-2.1-Pro（改 model）。
写稿禁用 deepseek-v4-flash。

典型调用：
    set -a; . ~/.hermes/.env; set +a
    python3 stream_kimi.py /tmp/prompt.md /tmp/body.md kimi-k3
"""
import os, sys, json, urllib.request

prompt_file, out_file = sys.argv[1], sys.argv[2]
model = sys.argv[3] if len(sys.argv) > 3 else "kimi-k3"

base = os.environ["TELECOM_BASE_URL"].rstrip("/")
key = os.environ["TELECOM_KIMI_KEY"]
prompt = open(prompt_file, encoding="utf-8").read()

payload = {
    "model": model,
    "stream": True,
    "temperature": 0.7,
    "messages": [
        {"role": "system", "content": "你是一位深耕财税内容多年的资深公众号主笔，文风务实、有分寸、善用场景与对比，绝不编造政策与数据。"},
        {"role": "user", "content": prompt},
    ],
}
req = urllib.request.Request(
    base + "/chat/completions",
    data=json.dumps(payload).encode(),
    headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
)
buf = []
with urllib.request.urlopen(req, timeout=600) as r:
    for raw in r:
        line = raw.decode("utf-8", "ignore").strip()
        if not line.startswith("data:"):
            continue
        data = line[5:].strip()
        if data == "[DONE]":
            break
        try:
            obj = json.loads(data)
            delta = obj["choices"][0]["delta"].get("content") or ""
        except Exception:
            continue
        if delta:
            buf.append(delta)
            sys.stderr.write(delta)
            sys.stderr.flush()
text = "".join(buf)
open(out_file, "w", encoding="utf-8").write(text)
print(f"\n[OK] {len(text)} chars -> {out_file}")
