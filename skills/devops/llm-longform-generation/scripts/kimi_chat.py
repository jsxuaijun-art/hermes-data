#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""图文混合 OpenAI 兼容调用器（kimi 等支持 vision 的模型）。

在 deepseek 主会话里后台调 kimi 处理含图工作（营业执照/财报/协议/截图等图片材料）。

为什么：deepseek-v4-flash 主模型不能读图；kimi-k3 实测支持 image_url 输入（2026-10 验证通过，
能准确识别图中文字）。公众号/股权转让等含图任务交给 kimi，按本机模型分工纪律执行。

用法：
    python3 kimi_chat.py --text "读取这些图，提取信息" \
        --images /tmp/a.png,/tmp/b.jpg \
        --out /tmp/result.txt \
        [--model kimi-k3] [--key-env TELECOM_KIMI_KEY] \
        [--system /tmp/system.txt] [--temperature 0.3] [--timeout 300]

- --text    用户文字指令（必填 或 用 --brief 从文件读）
- --images  逗号分隔的本地图片路径（可选，1-N 张）
- --out     输出文件
- --key-env 环境变量名（默认 TELECOM_KIMI_KEY），脚本从 env 或 ~/.hermes/.env 取真值
- 每次调用前务必做一次真实探测确认 key/model 可用（防 503 降级/通道失效）

密钥只通过环境变量名传入，绝不内联。
"""
import argparse, base64, json, mimetypes, os, sys, urllib.error, urllib.request
from pathlib import Path


def load_env_file():
    envf = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")) / ".env"
    if envf.exists():
        for line in envf.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def file_to_data_url(path: str) -> str:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    mime = mimetypes.guess_type(path)[0] or "image/png"
    b64 = base64.b64encode(p.read_bytes()).decode()
    return f"data:{mime};base64,{b64}"


def build_content(text: str, images) -> list:
    content = [{"type": "text", "text": text}]
    for img in images:
        content.append({"type": "image_url", "image_url": {"url": file_to_data_url(img)}})
    return content


def call(base_url, model, api_key, messages, temperature, timeout):
    url = base_url.rstrip("/") + "/chat/completions"
    body = json.dumps({
        "model": model, "messages": messages,
        "stream": False, "temperature": temperature,
        "max_tokens": 4000,
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": f"Bearer {api_key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--text", help="user text instruction (or use --brief)")
    p.add_argument("--brief", help="file with the user text instruction")
    p.add_argument("--images", help="comma-separated local image paths")
    p.add_argument("--out", required=True)
    p.add_argument("--model", default="kimi-k3")
    p.add_argument("--key-env", default="TELECOM_KIMI_KEY")
    p.add_argument("--base-url", default="https://aigw.telecomjs.com/v1")
    p.add_argument("--system", help="optional system prompt file")
    p.add_argument("--temperature", type=float, default=0.3)
    p.add_argument("--timeout", type=int, default=300)
    a = p.parse_args()

    load_env_file()
    api_key = os.environ.get(a.key_env, "")
    if not api_key:
        print(f"ERROR: {a.key_env} not set", file=sys.stderr); return 1

    if a.brief:
        text = Path(a.brief).read_text(encoding="utf-8")
    else:
        text = a.text or ""
    if not text.strip():
        print("ERROR: need --text or --brief", file=sys.stderr); return 1

    images = [x.strip() for x in (a.images or "").split(",") if x.strip()]
    messages = []
    if a.system:
        messages.append({"role": "system", "content": Path(a.system).read_text(encoding="utf-8")})
    messages.append({"role": "user", "content": build_content(text, images)})

    try:
        d = call(a.base_url, a.model, api_key, messages, a.temperature, a.timeout)
    except urllib.error.HTTPError as e:
        print(f"ERROR: HTTP {e.code} — {e.read().decode('utf-8','ignore')[:400]}", file=sys.stderr); return 1

    msg = d["choices"][0]["message"]
    out = msg.get("content") or ""
    if not out.strip():
        print("ERROR: empty content — check vision support / channel", file=sys.stderr); return 1
    Path(a.out).write_text(out, encoding="utf-8")
    print(f"=== saved: {a.out} ({len(out)} chars) ===", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
