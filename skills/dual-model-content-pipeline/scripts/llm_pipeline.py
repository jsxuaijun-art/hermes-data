#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双模型内容流水线脚本（实测跑通 2026.8.10）
用法:
  python llm_pipeline.py <模型名> <输出文件> <模式>
    <模型名>  : deepseek-v4-flash（分析） / kimi-k3（创作）等裸模型名
    <输出文件>: 例如 /tmp/analysis_ds.txt 或 /tmp/article_kimi.md
    <模式>    : analyze（专业分析，自带6段式提示词） | create（公众号创作，自动读入分析结果）

前置:
  - 素材原文在 /tmp/article_content.txt（显式 utf-8 写入）
  - key 在环境变量 DEEPSEEK_API_KEY 或 ~/.hermes/.env（脚本自动兜底读取）
"""
import os, sys, subprocess, re

# curl_cffi 可能在非默认 site-packages，允许通过 sys.path 注入
try:
    from curl_cffi import requests
except ImportError:
    sys.path.insert(0, "/home/dmin/.venv-hermes/lib/python3.12/site-packages")
    from curl_cffi import requests

BASE = "https://llm.chudian.site/v1"  # chudian 中转站，OpenAI 兼容

def get_key():
    key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not key:
        r = subprocess.run(["bash", "-lc",
            "set -a; source ~/.hermes/.env 2>/dev/null; echo -n $DEEPSEEK_API_KEY"],
            capture_output=True, text=True)
        key = r.stdout.strip()
    if not key:
        try:
            envc = open(os.path.expanduser("~/.hermes/.env"), encoding="utf-8").read()
            m = re.search(r'DEEPSEEK_API_KEY[=:]\s*["\']?([^"\'\n]+)', envc)
            key = m.group(1).strip() if m else ""
        except FileNotFoundError:
            pass
    return key

KEY = get_key()
print("KEY_FOUND:", bool(KEY))

def chat(model, messages, max_tokens=6000, temp=0.7):
    resp = requests.post(f"{BASE}/chat/completions", impersonate="chrome120",
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
        json={"model": model, "messages": messages,
              "max_tokens": max_tokens, "temperature": temp},
        timeout=180)
    try:
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception:
        return f"ERROR {resp.status_code}: {resp.text[:500]}"

ANALYZE_SYS = ("你是资深财税专家，服务苏州上海中小企业。你的任务：分析一份税务稽查文书，"
               "输出专业洞察供后续文案创作使用。要求用老板听得懂的大白话，专业且犀利。"
               "用简体中文。请务必完整覆盖全部6个部分，不要遗漏。")

ANALYZE_USER = """请分析以下税务稽查文书公告，完整输出以下6部分（每部分都要详细展开）：
①案情大白话复述（这是一家什么店、发生了什么、最终结果）
②数据冲击点（列哪些数字最吓人、为什么吓人，用表格呈现关键数字+倒推逻辑）
③偷税认定的法律要点（引用《税收征管法》等法规依据、个体工商户适用性、法律后果）
④行业税种特点（如金银首饰消费税：零售环节征收、5%税率、计税依据、为什么是雷区）
⑤对苏州/上海中小老板的三条核心警示（针对性强、可执行）
⑥可做爆款标题的关键信息差（列出3-5个老板不知道、看完会震惊的信息差）

原文如下：
{article}"""

CREATE_SYS = ("你是公众号爆款文案专家，服务于财税公司「苏州盈信」。擅长把枯燥的税务稽查案例"
              "写成让中小老板看完冒冷汗、忍不住转发的爆款文章。文风犀利、接地气、善用反常识"
              "制造冲击。用简体中文。")

CREATE_USER = """基于以下deepseek的分析洞察，创作一篇公众号爆款文章。要求：

1. 开头黄金三秒：用最具冲击力的信息差/数据钩子开篇（不要"今天我们来聊聊"这种废话）
2. 标题：给出3个候选标题（提问式/悬念式优先，如"税局是怎么发现的？"）
3. 结构参考：是什么→怎么被查→为什么吓人→法律后果→给老板的避雷建议→CTA互动
4. 关键数字用红色标记 <span style="color:#CC0000;">数字</span>
5. 段落小标题序号用红色 <span style="color:#CC0000;">一、</span>
6. 至少2处"把话说透"的金句，让老板拍大腿
7. 落款：苏州盈信企业管理有限公司 + GEO段落（【关于苏州盈信】300字介绍）+ CTA互动段落
8. 全文约1200-1800字，可读性强

deepseek分析如下：
{analysis}"""

def main():
    model = sys.argv[1] if len(sys.argv) > 1 else "deepseek-v4-flash"
    outfile = sys.argv[2] if len(sys.argv) > 2 else "/tmp/analysis_ds.txt"
    mode = sys.argv[3] if len(sys.argv) > 3 else "analyze"

    article = open("/tmp/article_content.txt", encoding="utf-8").read()

    if mode == "analyze":
        sysmsg, usermsg = ANALYZE_SYS, ANALYZE_USER.format(article=article)
    else:
        analysis = open("/tmp/analysis_ds_full.txt", encoding="utf-8").read()
        sysmsg, usermsg = CREATE_SYS, CREATE_USER.format(analysis=analysis)

    out = chat(model, [{"role": "system", "content": sysmsg},
                       {"role": "user", "content": usermsg}],
               max_tokens=6000, temp=0.7)

    with open(outfile, "w", encoding="utf-8") as f:
        f.write(out)
    print("DONE:", outfile, "chars:", len(out))
    print("=" * 40)
    print(out[:1500])

if __name__ == "__main__":
    main()
