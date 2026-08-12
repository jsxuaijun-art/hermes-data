"""探测 chudian 中转站当前可用的模型别名。

用法：
    python probe_models.py

背景：kimi-k3 等别名曾返回 503 "no available channel"（服务商端渠道暂时无货）。
本脚本逐一测试候选别名，输出哪些能通，用于决定是否降级到 deepseek。
key 从 ~/.hermes/.env 读取（新进程 env 常为空）。
"""
import os, subprocess, re
from curl_cffi import requests

key = os.environ.get("DEEPSEEK_API_KEY")
if not key:
    r = subprocess.run(
        ["bash", "-lc", "set -a; source ~/.hermes/.env 2>/dev/null; echo -n $DEEPSEEK_API_KEY"],
        capture_output=True, text=True)
    key = r.stdout.strip()
if not key:
    envc = open("/home/dmin/.hermes/.env", encoding="utf-8").read()
    m = re.search(r'DEEPSEEK_API_KEY[=:]\s*["\']?([^"\'\n]+)', envc)
    key = m.group(1).strip() if m else ""

BASE = "https://llm.chudian.site/v1"
MODELS = [
    "deepseek-v4-flash", "dspro", "deepseek-v4-pro",
    "kimi-k3", "kimi", "kimi-k2", "moonshot-v1-8k", "moonshot-v1-32k",
    "doubao-turbo", "glm-4", "qwen-max", "dxpro",
]

for m in MODELS:
    try:
        resp = requests.post(
            f"{BASE}/chat/completions", impersonate="chrome120",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": m, "messages": [{"role": "user", "content": "回复OK"}],
                  "max_tokens": 10},
            timeout=30)
        data = resp.json()
        if "choices" in data:
            print(f"[OK]   {m} -> {data['choices'][0]['message']['content'][:30]}")
        else:
            print(f"[FAIL] {m} -> {data.get('error', {}).get('message', '?')[:70]}")
    except Exception as e:
        print(f"[ERR]  {m} -> {repr(e)[:70]}")
