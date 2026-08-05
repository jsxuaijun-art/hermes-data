---
name: llm-endpoint-model-verification
description: 验证第三方中转 LLM API 端点是否真的在提供声称的模型（识别张冠李戴/偷梁换柱/阉割版）。多信号探测：识图指纹、同平台对照、自报身份、知识截止、上下文长度、官方交叉验证。
category: mlops
triggers:
  - 模型是不是真的 / 阉割版 / 张冠李戴 / 偷梁换柱 / 被换了模型
  - 中转 API / relay / 第三方平台 / llm.chudian.site
  - 怀疑模型不是最新版 / 版本验证 / 模型身份
  - api key 买到的模型不对 / 不支持识图 / 能力对不上
  - 验证模型端点 / model endpoint / impersonation
---

# LLM 端点模型身份验证

用户在第三方中转平台买"新模型"，可能实为**旧模型改名售卖**（张冠李戴 / 偷梁换柱）或**阉割版**（本应支持的能力被砍）。本技能提供一套多信号探测法，判定端点到底给的是不是声称的模型。

## 触发场景

- 用户怀疑中转 API 给的模型不是最新/不是真身（如 V4 买成 V3）
- 模型能力对不上宣传（如不支持识图、上下文太短）
- 需要硬证据找客服对质/退款

## ⚠️ 表格规范

本技能内部用 Markdown 表格仅为可读性参考；**交付给用户的对比表一律用 workbuddy-output 的 `make_grid_table` 生成带 ├──┤ 网格线的 ASCII 表**（右竖线对齐），禁止手写 `|---|` 管道表或纯空格表。

## 判定信号（任一命中即为假/阉割）

| 信号 | 测试方法 | 假模型表象 |
|------|----------|------------|
| 识图指纹 | 生成一张带随机数字/文字的图片发过去 | 平台静态拒绝 `模型不支持 image 输入`（HTTP 4xx） |
| 同平台对照 | 同一张图发给平台其他模型 | 其他模型能识图、该模型拒收 → 平台有通道，是模型本身旧/不带视觉 |
| 自报身份 | 直接问"你是谁 / 最新版本 / 知识截止" | 会老实交代旧版本名 + 旧知识截止（新模型的发布旧版不知道） |
| 上下文长度 | 问"你的 context length" | 报旧版长度（如 V3 报 128K，真 V4 为 1M） |
| 官方交叉 | web 查该版本官方发布日期与真实能力 | 自报信息与官方严重不符 |

### ⚡ 现役模型即被疑端点时的"工作中实弹验证"（2026.8.5）

若被怀疑的端点**正是当前驱动 Hermes 的模型**（agent 主模型或 aux 视觉模型），不需要单独搭测试台本——直接在日常真实任务里让图像工具走它，失败即当场实锤：

- 调 `vision_analyze`（或其他走辅助视觉模型的图片分析）→ 若报 `模型 'xxx' 不支持 image 输入` HTTP 400，等于在工作流里复现了「识图指纹」信号，且无需造测试图。
- 这类失败同时解释 / 印证主结论：同一个假端点既是聊天鉴定的对象，也是让辅助识图功能瘫痪的元凶。
- 价值：遇到"某个图像功能莫名 4xx"时，反向怀疑"驱动它的模型是不是被偷换了" → 与该技能联动排查，而不是当孤立 bug。

## 核心逻辑

**用识图做"版本指纹"是最快判别** —— 旧版模型普遍纯文本、新版普遍带视觉（如 V3→V4、GPT4→GPT4o），发图一测便知。但必须**追加同平台对照**：证明平台识图通道是通的，把锅钉死在"端点配的模型本身是旧版"，防止平台反咬"你这割了识图"。

三重闭环：
1. 目标模型拒图（改名前缀证据）
2. 同平台其他模型能读（平台通道健全，排除"平台阉割"）
3. 模型自报版本/截止/上下文与官方不符（实锤改名）

三者同中 → 大结局：旧模型 + 改名 = 欺诈式张冠李戴，比单纯阉割更恶劣。

## 验证脚本骨架

```python
import json, urllib.request, urllib.error

# 从 ~/.hermes/.env 读 base_url + api_key（chudian 等中转）

def ask(q, model="deepseek-v4-flash", max_tokens=400):
    payload = {"model": model, "messages":[{"role":"user","content":q}],
               "max_tokens":max_tokens, "temperature":0}
    req = urllib.request.Request(base_url.rstrip("/")+"/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Authorization":f"Bearer {api_key}","Content-Type":"application/json"},
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())["choices"][0]["message"].get("content","")
    except urllib.error.HTTPError as e:
        return f"[HTTP {e.code}] {e.read().decode()[:200]}"   # 关键：image 拒绝会在这里暴露

# 测试集（逐条打）
# 1. 识图：生成带 SECRET 7391 / SIGNAL 4182 的图，走 image_url data URL
# 2. 对照：同图换 qwen3.7-plus / kimi-k3 等
# 3. 自报："请介绍你连接的模型，何时发布、你的知识截止、上下文长度"
# 4. 官方：Bing 搜 "{model} 发布日期 多模态 上下文" 比对
```

参考真实实现：`/tmp/fingerprint.py`（ask() 函数 + 一问一打的知识截止探针）。

可直接运行的脚本：`scripts/fingerprint_probe.py`（本技能自带）。用法：
```
python3 fingerprint_probe.py --model deepseek-v4-flash --env ~/.hermes/.env
```
自动读 .env、生成带随机数字的测试图、发识图 + 同平台对照 + 自报问询，逐条打印结果。可用 `--controls qwen3.7-plus,kimi-k3` 指定对照模型，`--skip-image` 跳过图片测试。

## 交付格式

- 用 workbuddy-output 的 `make_grid_table` 出对比表（验证项 / 测试结果 / 结论）
- 每项标注 ✅/✗
- 给可执行下一步：对质退换（拿证据找客服）、临时替代（平台能识图的其他模型）、官方渠道
- 主动提议整理成 Word .docx 放桌面（用户偏好），供甩给客服

## 2026.8.5 实测案例（chudian.site deepseek-v4-flash）

- `deepseek-v4-flash` 发图被拒：400 "模型不支持 image 输入"
- 同平台 `qwen3.7-plus` / `kimi-k3` 均正确读出图中数字 → 平台识图通道通
- 问身份 → 自称 DeepSeek-V3-0324，知识截止 2025年5月，上下文 128K
- 官方：V4-Flash 2026-04-24 发布，1M 上下文 → 实为重命名旧模型
- 结论：不是"阉割识图"，是根本没给 V4，用 V3 改名卖
