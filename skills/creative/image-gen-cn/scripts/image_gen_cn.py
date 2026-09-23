#!/usr/bin/env python3
"""
国内可用的 AI 生图脚本 — 多 provider 通用封装。

主推：通义万相 (DashScope / wanx)  — 阿里云，免费额度，中文效果好
备用：硅基流动 (SiliconFlow)       — 有免费 FLUX 模型

用法：
  python3 image_gen_cn.py --provider dashscope --prompt "..." --out /tmp/x.png
  python3 image_gen_cn.py --provider siliconflow --prompt "..." --out /tmp/x.png

环境变量：
  DASHSCOPE_API_KEY     通义万相 key (https://bailian.console.aliyun.com/)
  SILICONFLOW_API_KEY   硅基流动 key (https://cloud.siliconflow.cn/)

也支持从 ~/.hermes/.env 读取（Hermes 常规做法）。
"""

import argparse, base64, json, os, re, sys, time, urllib.request, urllib.error

ENV_FILE = os.path.expanduser("~/.hermes/.env")

def load_env():
    """读取 ~/.hermes/.env 注入 os.environ（不覆盖已存在值）"""
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

def http_json(url, payload, headers, timeout=120):
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"),
                                 headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def save_b64(data, out):
    """data 可能是纯 b64 或 data:image/png;base64,... 前缀"""
    if "," in data and data.split(",")[0].endswith(";base64"):
        data = data.split(",", 1)[1]
    with open(out, "wb") as f:
        f.write(base64.b64decode(data))
    print(f"OK saved {out} ({os.path.getsize(out)} bytes)")

# ---------------- 通义万相 (DashScope / wanx) ----------------
def gen_dashscope(prompt, out, size="1024*1024", model="wanx2.1-t2i-turbo", n=1):
    key = os.environ.get("DASHSCOPE_API_KEY")
    if not key:
        raise RuntimeError("DASHSCOPE_API_KEY 未设置")
    create_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable",
    }
    body = {"model": model, "input": {"prompt": prompt},
            "parameters": {"size": size, "n": n}}
    r = http_json(create_url, body, headers)
    task_id = r.get("output", {}).get("task_id")
    if not task_id:
        raise RuntimeError(f"通义万相创建任务失败: {r}")

    status_url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
    h2 = {"Authorization": f"Bearer {key}"}
    for _ in range(60):  # 最多等 ~5 分钟
        time.sleep(5)
        s = http_json(status_url, {}, h2, timeout=30)
        st = s.get("output", {}).get("task_status", "")
        if st == "SUCCEEDED":
            results = s.get("output", {}).get("results", [])
            if results:
                # wanx 返回的是 url，下载到本地
                url = results[0].get("url")
                _download(url, out)
                return
            raise RuntimeError(f"任务成功但无结果: {s}")
        if st in ("FAILED", "CANCELED"):
            raise RuntimeError(f"通义万相任务{st}: {s.get('output', {})}")
    raise RuntimeError("通义万相任务超时")

def _download(url, out):
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=120) as r:
        data = r.read()
    with open(out, "wb") as f:
        f.write(data)
    print(f"OK saved {out} ({len(data)} bytes)")

# ---------------- 硅基流动 (SiliconFlow) ----------------
def gen_siliconflow(prompt, out, size="1024x1024", model="black-forest-labs/FLUX.1-schnell"):
    key = os.environ.get("SILICONFLOW_API_KEY")
    if not key:
        raise RuntimeError("SILICONFLOW_API_KEY 未设置")
    url = "https://api.siliconflow.cn/v1/images/generations"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    body = {"model": model, "prompt": prompt, "image_size": size,
            "num_inference_steps": 4}
    r = http_json(url, body, headers)
    if "images" in r:
        # siliconflow 返回 url 或 b64_json
        url_img = r["images"][0].get("url")
        if url_img:
            _download(url_img, out)
            return
        b64 = r["images"][0].get("b64_json")
        if b64:
            save_b64(b64, out)
            return
    raise RuntimeError(f"硅基流动失败: {r}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--provider", choices=["dashscope", "siliconflow"], default="dashscope")
    p.add_argument("--prompt", required=True)
    p.add_argument("--out", default="/tmp/gen.png")
    p.add_argument("--size", default=None)
    args = p.parse_args()
    load_env()
    if args.provider == "dashscope":
        gen_dashscope(args.prompt, args.out, args.size or "1024*1024")
    else:
        gen_siliconflow(args.prompt, args.out, args.size or "1024x1024")

if __name__ == "__main__":
    main()
