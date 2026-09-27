#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""未知 sk- key 的平台识别探针（401 报文指纹法）

用法:
    python3 probe-unknown-key.py sk-xxxxxxxx            # 探测单个 key
    python3 probe-unknown-key.py                        # 从 ~/.hermes/.env 读 DEEPSEEK_API_KEY 探测

原理: 主流平台对无效 key 的 401 报文文案各不相同且有签名特征
（chudian 会直接告诉你它要什么格式、火山方舟说 format incorrect、
DeepSeek 回显 key 尾号、智谱说令牌过期）。逐平台探测后按指纹归类：
    - 某个平台报「格式错误/无效」之外的特定文案 → 很可能属于该平台（值错或格式错）
    - 全平台都拒 → key 是渠道/中转购买的，无权自动推断 base_url → 直接问用户
判定后不要继续猜域名，问题转给用户要 base_url（见 SKILL.md §3.x.4）。

避免：把「探不到」写进结论当失败常态；探测本身是识别手段，识别不出就转人工。
"""
import json
import sys
import urllib.error
import urllib.request

KEY = sys.argv[1] if len(sys.argv) > 1 else ""
if not KEY:
    try:
        with open("/home/dmin/.hermes/.env") as f:
            for line in f:
                if line.startswith("DEEPSEEK_API_KEY="):
                    KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
    except OSError:
        pass
if not KEY:
    print("用法: probe-unknown-key.py <sk-...> 或确保 ~/.hermes/.env 有 DEEPSEEK_API_KEY")
    sys.exit(2)

print(f"key: {KEY[:6]}...{KEY[-4:]} (长度 {len(KEY)})")

# (平台名, 端点, 探测用模型ID) —— 模型名写该平台常用/一定存在的；
# 若平台已能解析 key，模型名错会返回「模型不存在」而非 key 错，可区分。
PLATFORMS = [
    ("chudian中转",      "https://llm.chudian.site/v1/chat/completions",            "kimi-k3"),
    ("火山方舟ARK",      "https://ark.cn-beijing.volces.com/api/v3/chat/completions", "doubao-seed-2.1-pro"),
    ("阿里百炼",         "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions", "qwen-plus"),
    ("DeepSeek官方",     "https://api.deepseek.com/chat/completions",                "deepseek-chat"),
    ("Kimi/Moonshot",    "https://api.moonshot.cn/v1/chat/completions",              "moonshot-v1-8k"),
    ("硅基流动",         "https://api.siliconflow.cn/v1/chat/completions",          "deepseek-ai/DeepSeek-V3"),
    ("智谱GLM",          "https://open.bigmodel.cn/api/paas/v4/chat/completions",   "glm-4-plus"),
    ("阶跃星辰",         "https://api.stepfun.com/v1/chat/completions",              "step-2-16k"),
]

def probe(name, url, model):
    body = json.dumps({"model": model,
                       "messages": [{"role": "user", "content": "hi"}],
                       "max_tokens": 5}).encode()
    req = urllib.request.Request(url, data=body,
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode())
            print(f"✅ {name}: KEY 有效! 服务端 model={data.get('model')}")
            return "有效"
    except urllib.error.HTTPError as e:
        raw = e.read().decode(errors="replace")[:220].replace("\n", " ")
        print(f"❌ {name} HTTP {e.code}: {raw}")
        return str(e.code)
    except Exception as e:
        print(f"⚠️  {name}: {e} (网络/超时，不代表 key 无效)")
        return "network"

print()
results = {}
for name, url, model in PLATFORMS:
    results[name] = probe(name, url, model)

print()
hits = [n for n, r in results.items() if r == "有效"]
print("总结:", f"key 属于 {hits}" if hits else
      "全部拒绝 → 极大概率是渠道/中转购买的 key，无权推断 base_url，"
      "请用户提供平台名/API调用地址（base_url），勿继续猜域名。")