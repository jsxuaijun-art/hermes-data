#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电信智云TokenHub 出稿脚本（含零成本内嵌核验）

特性：
  - 兼容 telecom providers 清单（telecom-doubao / telecom-kimi / telecom-deepseek-flash）
  - KEY 从环境变量或 ~/.hermes/.env 自动读取（TELECOM_* 变量）
  - 出稿的同时打印同一响应的 model 字段 → 一步核验"确实是这个模型生成"，零额外token
  - 支持模型名大小写敏感提示（电信端点大小写写错会报401）

用法:
  python telecom_create.py <provider> <模型名> <输出文件> [素材文件]
  # 例：python telecom_create.py telecom-doubao Doubao-Seed-2.1-Pro /tmp/db_out.txt 素材.txt
  # 例：python telecom_create.py telecom-kimi kimi-k3 /tmp/kimi_out.txt 素材.txt

依赖: 仅 Python 标准库（urllib），零第三方依赖。
"""
import os, sys, re, json, subprocess, urllib.request, urllib.error

BASE = "https://aigw.telecomjs.com/v1"  # 电信智云 TokenHub

# provider -> (env变量名, 默认模型名)
PROVIDERS = {
    "telecom-doubao":         ("TELECOM_DOUBAO_KEY", "Doubao-Seed-2.1-Pro"),
    "telecom-kimi":           ("TELECOM_KIMI_KEY", "kimi-k3"),
    "telecom-deepseek-flash": ("TELECOM_DEEPSEEK_FLASH_KEY", "deepseek-v4.1-flash-new"),
    "telecom-deepseek-pro":   ("TELECOM_DEEPSEEK_PRO_KEY", "deepseek-v4-pro"),
}

def get_key(env_var):
    key = os.environ.get(env_var, "").strip()
    if not key:
        try:
            envc = open(os.path.expanduser("~/.hermes/.env"), encoding="utf-8").read()
            m = re.search(rf'^{env_var}=["\']?([^"\'\n]+)', envc, re.MULTILINE)
            key = m.group(1).strip() if m else ""
        except FileNotFoundError:
            pass
    return key

def chat(provider, model, messages, max_tokens=3000, temp=0.8):
    env_var, _ = PROVIDERS.get(provider, (None, None))
    if not env_var:
        return None, f"ERROR: 未知 provider {provider}"
    key = get_key(env_var)
    if not key:
        return None, f"ERROR: 未找到 {env_var}（空key→401）"
    payload = json.dumps({"model": model, "messages": messages,
                          "max_tokens": max_tokens, "temperature": temp}).encode("utf-8")
    req = urllib.request.Request(f"{BASE}/chat/completions", data=payload,
        headers={"Authorization": f"Bearer {key}",
                 "Content-Type": "application/json"},
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            data = json.loads(r.read().decode("utf-8"))
        return data, None
    except urllib.error.HTTPError as e:
        return None, f"ERROR {e.code}: {e.read().decode('utf-8', 'replace')[:500]}"
    except Exception as e:
        return None, f"ERROR: {e}"

def main():
    if len(sys.argv) < 4:
        print(__doc__); sys.exit(1)
    provider, model, outfile = sys.argv[1], sys.argv[2], sys.argv[3]
    prompt_file = sys.argv[4] if len(sys.argv) > 4 else None
    if prompt_file and os.path.exists(prompt_file):
        user_prompt = open(prompt_file, encoding="utf-8").read().strip()
    else:
        user_prompt = "请创作一条范话题类爆款短视频口播文案，含标题三件套+8话题标签+完整文案+拍摄速查表。素材：" + (prompt_file or "")

    data, err = chat(provider, model,
                     [{"role": "system", "content": "你是顶级内容创作者，擅长范话题/爆款文案。"},
                      {"role": "user", "content": user_prompt}])
    if err:
        print(err); sys.exit(1)

    content = data["choices"][0]["message"]["content"]
    # ===== 零成本一步核验：读同一响应的 model 字段 =====
    echo_model = data.get("model")
    verify = "✅ 核验通过" if (echo_model or "").lower() == model.lower() else f"⚠️ 模型名不一致(请求{model}/回显{echo_model})"

    with open(outfile, "w", encoding="utf-8") as f:
        f.write(content)
    print("=" * 52)
    print(f"DONE: {outfile}  chars: {len(content)}")
    print(f"请求模型: {model}")
    print(f"服务器回显 model 字段: {echo_model}")
    print(f"模型核验: {verify}")
    print(f"provider: {provider}")
    print("=" * 52)
    print(content[:2000])

if __name__ == "__main__":
    main()