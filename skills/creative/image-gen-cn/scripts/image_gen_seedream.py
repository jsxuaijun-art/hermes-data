#!/usr/bin/env python3
"""
AI 生图 — 豆包 Seedream 5.0 Pro，经电信中转平台 aigw.telecomjs.com (OpenAI 兼容 /images/generations)。

环境变量（~/.hermes/.env）：
  SEEDREAM_API_KEY   https://aigw.telecomjs.com/v1 的 key
  SEEDREAM_BASE_URL  默认 https://aigw.telecomjs.com/v1

用法：
  python3 image_gen_seedream.py --prompt "..." --out /tmp/x.png
  python3 image_gen_seedream.py --model doubao-seedream-5.0-pro-0724 \
      --size 1440x2560 --prompt "..." --out /tmp/x.png
"""
import argparse, json, os, sys, urllib.request, urllib.error

ENV_FILE = os.path.expanduser("~/.hermes/.env")


def load_env():
    if not os.path.exists(ENV_FILE):
        return
    with open(ENV_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k and k not in os.environ:
                os.environ[k] = v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="doubao-seedream-5.0-pro-0724")
    ap.add_argument("--size", default="1280x1280")
    ap.add_argument("--n", type=int, default=1)
    args = ap.parse_args()

    load_env()
    key = os.environ.get("SEEDREAM_API_KEY")
    base = os.environ.get("SEEDREAM_BASE_URL", "https://aigw.telecomjs.com/v1").rstrip("/")
    if not key:
        sys.exit("SEEDREAM_API_KEY 未设置")

    payload = {"model": args.model, "prompt": args.prompt, "n": args.n, "size": args.size}
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    req = urllib.request.Request(base + "/images/generations",
                                 data=json.dumps(payload).encode(),
                                 headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=240) as r:
        data = json.loads(r.read().decode())

    items = data.get("data", [])
    if not items:
        sys.exit("接口无 data，原始响应: " + json.dumps(data)[:300])

    for i, item in enumerate(items):
        b64 = item.get("b64_json")
        url = item.get("url")
        out = args.out if i == 0 else args.out.replace(".png", f"_{i}.png")
        if b64:
            import base64
            raw = b64.split(",", 1)[1] if "," in b64 and b64.split(",")[0].endswith(";base64") else b64
            with open(out, "wb") as f:
                f.write(base64.b64decode(raw))
        elif url:
            dreq = urllib.request.Request(url)
            # 部分网关需要带鉴权下载，先裸试
            try:
                with urllib.request.urlopen(dreq, timeout=120) as r:
                    raw = r.read()
            except urllib.error.HTTPError:
                dreq = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}"})
                with urllib.request.urlopen(dreq, timeout=120) as r:
                    raw = r.read()
            with open(out, "wb") as f:
                f.write(raw)
        else:
            sys.exit("条目无 url / b64_json: " + json.dumps(item)[:300])
        print(f"OK saved {out} ({os.path.getsize(out)} bytes)")


if __name__ == "__main__":
    main()