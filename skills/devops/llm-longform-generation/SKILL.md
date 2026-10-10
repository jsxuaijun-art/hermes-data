---
name: llm-longform-generation
description: 长文 LLM 出稿走流式直连，绕开网关非流式超时。
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    category: devops
    tags: [llm, streaming, gateway, longform, timeout, delegation]
    related_skills: [hermes-free-model-channels, llm-provider-and-key-management]
triggers:
  - 长文出稿超时 / 生成到一半断了 / 子代理写稿失败
  - 文案/文章/报告 出稿 / 长文生成 / 流式调用
  - 网关超时 / 90 秒超时 / 非流式超时 / stream=true
---

# LLM 长文出稿（流式直连）

## When to Use

任何**长文生成**任务（文案、口播稿、公众号文章、报告、方案）走第三方 OpenAI 兼容网关时使用本 skill。
典型触发：委派子代理写长稿结果整体超时无产出；或要一份超过几百字的成稿、怕调用中途断掉。

**不适用**：短问答、单轮工具调用、本地模型（llama.cpp/vLLM 自托管）——那些没有网关侧响应时长上限的问题。

## 核心规则

1. **长文一律走流式（`stream=true`）。** 非流式调用要求网关在响应时长上限内一次性返回全部内容；
   长稿生成耗时超过该上限就会被切断。流式则首字节很快回传、连接被持续保活，几千字也不受影响。
2. **拆小是次优解。** 把一份大任务拆成多次调用（如 A 稿一次、B 稿一次）能降低单次时长，
   但仍是碰运气；**流式才是根治**。两者可叠加使用。
3. **主会话只做编排/采集/验证**，成稿交给专门擅长的模型写（本机约定见下方"在用渠道"）。
   不要因为委派失败就自己在主会话里代写——那会破坏既定的模型分工纪律。
4. **密钥只从密钥文件/环境读**，绝不写进脚本正文、记忆或提交物（会随同步推到 GitHub）。

## 通用调用器

`scripts/stream_chat.py` — provider 无关的流式调用器，读 brief 文件、写 out 文件：

```bash
python3 scripts/stream_chat.py \
  --base-url https://aigw.telecomjs.com/v1 \
  --model Doubao-Seed-2.1-Pro \
  --key-env TELECOM_DOUBAO_KEY \
  --brief /tmp/brief.txt --out /tmp/draft.txt \
  [--system /tmp/system.txt] [--temperature 0.8] [--timeout 300]
```

- `--key-env` 给**环境变量名**，脚本自己从环境或 `~/.hermes/.env` 取真值 → 调用方不会碰到密钥明文。
- 逐行解析 SSE `data:` 帧，边收边打印，长任务可实时看到进度；`[DONE]` 结束。
- 适合直接改造成一次性任务脚本（把 brief 内联、out 指向桌面交付路径）。

## 在用渠道（本机，2026-10 实测）

| 用途 | 渠道 / 模型 | base_url | key 环境变量 |
|---|---|---|---|
| 短文案 / 短视频口播 | Doubao-Seed-2.1-Pro | `https://aigw.telecomjs.com/v1` | `TELECOM_DOUBAO_KEY` |
| 长文 / 文章 | kimi-k3 | `https://aigw.telecomjs.com/v1` | `TELECOM_KIMI_KEY` |

两条都实测支持流式；密钥在 `~/.hermes/.env`。渠道与 fallback 链的配置细节见
`hermes-free-model-channels`（user-owned）。

## Pitfalls

- **别把"非流式超时"当成"模型不可用"**：换模型通常没用，换调用方式（流式）才对症。判断方法——
  短问答能通、长稿才断，就是响应时长问题，不是链路问题。
- **委派失败要如实说明并换路子**，不要在对话里含糊过去；也不要把失败的那次当作"产出已交"。
- **SSE 解析要容错**：帧可能带空行、`data: [DONE]`、或非法 JSON 心跳，解析异常要 `continue` 而不是崩掉。
- **超时要给足**：`timeout` 是"读超时"，流式下应设 300s 量级，别用默认值。
- 长稿输出**落地成文件**再引用（`out` 路径），不要只依赖终端回显——便于核对字数与后续排版。

## Verification

1. 脚本退出码 0，且打印 `已保存: <path> (N 字)`，N 与预期量级相符（不是空文件、不是几十字）。
2. `read_file` 打开产物确认是完整成稿（有结尾，不是被截断在半句）。
3. 若产物要交付，再走一遍排版/落盘（如转 .docx）并核对交付路径存在。
