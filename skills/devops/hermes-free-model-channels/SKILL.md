---
name: hermes-free-model-channels
category: devops
description: Hermes 免费/零key模型渠道接入与 fallback_model 自动切换链配置。
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [model, free, fallback, opencode, provider, config]
    related_skills: [llm-provider-and-key-management]
triggers:
  - 免费模型 / 免费渠道 / 白嫖 / zero-key / keyless
  - opencode-free / opencode zen / fallback / 兜底模型 / 自动切换
  - 主模型挂了自动切 / 免费兜底 / 5个免费模型
---

# Hermes 免费/零key模型渠道 + 自动切换链

## 概述

用户想让 Hermes「免费渠道都配上，一个不行自动切下一家」时，本 skill 给出**实测验证过**的零key免费渠道接入方法、免费模型识别原则、以及 `fallback_model` 自动切换链的配置语法。所有结论均经 2026.8.27 实弹请求验证（中国网络、直连、无需代理）。

**核心原则：免费模型可用性一律以「Hermes 内部解析 + 实弹请求」为准，绝不照抄外部文档的模型清单。**

## When to Use（何时使用）

- 用户要求配置免费模型、免费渠道、白嫖渠道、自动兜底/fallback。
- 用户提到「听说有免费模型可用」「5个免费模型」等传闻，需要核实真伪。
- 主模型（如 deepseek）不稳，要加自动切换的备用链。

## 唯一实测可用的零key免费渠道：opencode-free

- Provider 名 **`opencode-free`**（Hermes 内置，无需任何 key、无需 .env、中国网络直连可用）。
- **唯一实测全链路可用的免费模型 = `laguna-s-2.1-free`**（Hermes 源码 `plugins/model-providers/opencode-free/__init__.py` 的 `default_aux_model`）。配免费层永远用它。
- 其他候选模型（Docker OpenCode Zen 文档的 `deepseek-v4-flash-free`/`qwen3.6-plus-free`/`minimax-m3-free`/`big-pickle`、OpenCode 官方的 `x-preview-f-free` Ox Alpha）**实测全部失败**（`Model is unavailable` / `Model is not supported` / `Endpoint is unavailable`）。外部文档是二手信息。
- `/v1/models` 能列出全部付费目录（Claude/GPT/Gemini/Grok 全系列）**不代表免费可用**——那些要 key。别被目录误导。

## 零key请求头机制（缺一不可/多一不可）

```bash
curl -sS -X POST "https://opencode.ai/zen/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: " \
  -H "HTTP-Referer: https://hermes-agent.nousresearch.com" \
  -H "X-Title: Hermes Agent" \
  -H "User-Agent: HermesAgent/0.20.5" \
  -d '{"model":"laguna-s-2.1-free","messages":[{"role":"user","content":"回复两个字：在线"}],"max_tokens":200}'
```

- `Authorization` 头**必须存在但为空**：缺失 → 401；填任意值 → 401。这是免费层识别匿名请求的方式（源码 `opencode_zen_free_headers()` 返回 `{'Authorization': ''}`）。
- 生产配置不要手工拼头：Hermes 的 `hermes_cli/models.py::opencode_zen_free_runtime()` / `opencode_zen_free_headers()` 会正确构造全部头。

## 验证方法（必须实弹，不能只看 /models）

1. 裸 curl 探 `/v1/models` 只证明端点通，不证明模型可用。
2. 用 Hermes 自身解析链验证（比 AIAgent.chat 干净）：

```python
from hermes_cli.models import opencode_zen_free_runtime, opencode_zen_free_headers
from openai import OpenAI
rt = opencode_zen_free_runtime("opencode-free", "laguna-s-2.1-free")
# rt = {'provider': 'opencode-free', 'api_mode': 'chat_completions',
#       'base_url': 'https://opencode.ai/zen/v1', 'api_key': 'opencode-zen-free-keyless',
#       'default_headers': {'Authorization': '', ...}}
client = OpenAI(api_key="no-key-required", base_url=rt["base_url"],
                default_headers=opencode_zen_free_headers())
r = client.chat.completions.create(model="laguna-s-2.1-free", messages=[{"role":"user","content":"回复两个字：明白"}])
# choices[0].message.content 非空 = 链路通（实测返回「明白」）
```

- 注意：`AIAgent(provider="opencode-free", ...).chat()` 可能静默空返或被 aux 初始化干扰，别用它当验证工具。

## fallback_model 自动切换链配置

`fallback_model` 是 config.yaml **顶层根键**（在 `_EXTRA_KNOWN_ROOT_KEYS` 白名单，不在 DEFAULT_CONFIG，属合法可选键）。值可以是单个 dict 或 dict 列表（链，按顺序逐个尝试，前一个失败自动切下一个）：

```yaml
fallback_model:
  - provider: opencode-free
    model: laguna-s-2.1-free   # 主模型 deepseek 报错/不可用 → 自动切免费兜底
```

- 主模型保持 `model.default`（如 deepseek-v4-flash）不变，fallback_model 只做兜底。
- 其他免费渠道（OpenRouter `:free`、NVIDIA NIM、HuggingFace、Novita）**全部要注册拿各自 key**，.env 没有就没法凭空配上；拿到 key 后按同一 dict 格式追加进链（顺序即优先级）。
- 免费层服务端有波动（同模型偶发 `unavailable`），配置后仍需实测兜底是否真能出内容；对用户诚实说明「当前真正零key可用的只有这一条」。

## 改 config.yaml 两坑（实测踩过）

1. **`yaml.dump` 写回会丢光原文件所有注释**——用户 config 注释宝贵，优先「精确定位、插入整块」的方式保注释；确需 dump 时先告知会丢注释。
2. **CLI 下直接改写 `~/.hermes/config.yaml` 可能触发审批拦截**（命令 BLOCKED、等用户确认，超时即中止）。先备份（`cp config.yaml config.yaml.bak.$(date +%Y%m%d_%H%M%S)`），改完重读验证；被拦就明说方案、等用户「继续」，不要重试同一条命令。

## 快速参考

- 免费 provider 名：`opencode-free`
- 免费模型：`laguna-s-2.1-free`（唯一实测可用）
- 免费端点：`https://opencode.ai/zen/v1`
- 源码定位点：`hermes_cli/models.py`（`opencode_zen_free_runtime`/`opencode_zen_free_headers`/`is_opencode_zen_free_model`）、`plugins/model-providers/opencode-free/__init__.py`
- 实测探针与失败记录全文：`references/opencode-free-channel.md`

## 相关

- 与 `llm-provider-and-key-management`（user-owned，多 provider 切换/别名/源码核验方法论）互补：那个管「多平台多 key 切换」，本 skill 管「零key免费层 + fallback 自动切换」。