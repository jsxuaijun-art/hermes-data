#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""模型端点身份指纹探测。
用法：python3 fingerprint_probe.py [模型名] [--key-file ~/.hermes/.env]
多信号验证第三方中转 API 是否真的在提供声称的模型：
1. 识图指纹（发带随机数字的图）
2. 同平台对照（换 qwen/kimi 等对照模型）
3. 自报身份（版本 / 知识截止 / 上下文长度）
结果逐条打印，配合 workbuddy-output 表格交付。
参考真实案例：chudian.site 的 deepseek-v4-flash 被验出实为 V3-0324 改名。
"""
import json, os, sys, base64, io, argparse
import subprocess, urllib.request, urllib.error

def load_creds(env_path):
    """从 .env 读 base_url + api_key（兼容 DEEPSEEK_BASE_URL / DEEPSEEK_API_KEY）。"""
    base_url = "https://llm.chudian.site/v1"
    api_key = None
    if os.path.exists(env_path):
        for line in open(env_path):
            line = line.strip()
            if line.startswith("DEEPSEEK_API_KEY="):
                api_key = line.split("=",1)[1].strip().strip('"').strip("'")
            if line.startswith("DEEPSEEK_BASE_URL="):
                base_url = line.split("=",1)[1].strip().strip('"').strip("'")
    if not api_key:
        print("⚠️ 未在 env 找到 DEEPSEEK_API_KEY，请用 --key 或环境变量提供")
    return base_url, api_key

def make_test_image():
    """生成带随机数字的测试图，返回 data URL。数字随机避免模型蒙对/读缓存。"""
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        # 用纯 python 生成简笔图（同色块），或返回 None 提示
        return None
    import random
    a = random.randint(1000,9999); b = random.randint(1000,9999)
    img = Image.new("RGB", (400,120), "white")
    d = ImageDraw.Draw(img)
    d.text((20,35), f"SECRET {a} / SIGNAL {b}", fill="black")
    buf = io.BytesIO(); img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{b64}", f"SECRET {a} / SIGNAL {b}"

def ask(base_url, api_key, model, content, max_tokens=300):
    """content 可为 str 或 [{type,text|image_url,...}] 消息。返回文本或错误。"""
    msgs = ([{"role":"user","content":content}] if isinstance(content,str)
            else [{"role":"user","content":content}])
    payload = {"model":model, "messages":msgs, "max_tokens":max_tokens, "temperature":0}
    req = urllib.request.Request(base_url.rstrip("/")+"/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Authorization":f"Bearer {api_key}","Content-Type":"application/json"},
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())["choices"][0]["message"].get("content","")
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:200]
        return f"[HTTP {e.code}] {body}"
    except Exception as e:
        return f"[ERR] {e}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="deepseek-v4-flash")
    ap.add_argument("--env", default=os.path.expanduser("~/.hermes/.env"))
    ap.add_argument("--controls", default="qwen3.7-plus,kimi-k3",
                    help="同平台对照模型，逗号分隔")
    ap.add_argument("--skip-image", action="store_true")
    args = ap.parse_args()
    base_url, api_key = load_creds(args.env)

    print(f"=== 端点点模型验证: {args.model} @ {base_url} ===\n")

    # 1. 识图指纹
    if not args.skip_image:
        img, expect = make_test_image()
        if img is None:
            print("[识图] ⚠️ 无 PIL，跳过图片测试（pip install pillow 可启用）")
        else:
            content = [{"type":"image_url","image_url":{"url":img}},
                       {"type":"text","text":"图中数字是什么？逐字读出 SECRET 和 SIGNAL 后的数字"}]
            r = ask(base_url, api_key, args.model, content)
            ok = expect.split(" / ")[0] in r and expect.split(" / ")[1] in r
            print(f"[识图] {args.model}: {'✅ 读对' if ok else '✗ 拒收/读错'} -> {r[:120]}")
            # 2. 同平台对照
            for c in [x for x in args.controls.split(",") if x and x != args.model]:
                rc = ask(base_url, api_key, c, content)
                okc = expect.split(" / ")[0] in rc and expect.split(" / ")[1] in rc
                print(f"[对照] {c}: {'✅ 能读图' if okc else '✗ 拒收/读错'} -> {rc[:120]}")

    # 3. 自报身份
    print("\n[身份] 开始自报问询...")
    for q in ["请介绍你连接的模型：何时发布？是什么版本？",
              "你的最新训练知识截止到什么时候？",
              "你的上下文长度（context length）是多少？"]:
        print(f"  Q: {q}")
        print(f"  A: {ask(base_url, api_key, args.model, q)[:300]}\n")

    print("=== 完成。比对：识图✗+对照✅+自报旧版 => 实为重命名旧模型 ===")

if __name__ == "__main__":
    main()
