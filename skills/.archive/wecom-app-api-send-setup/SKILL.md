---
name: wecom-app-api-send-setup
title: 企业微信自建应用 API 发送打通与排障
description: Use when 企微发消息报错/更新Secret/配置回调或可信IP. 覆盖发送前置条件与排障。
category: devops
tags: [企微, 企业微信, 自建应用, 可信IP, 回调, API, 排障]
triggers:
  - 企微报错 / 企微发消息失败
  - 更新企微Secret / AgentId / 凭证
  - 配置企微接收消息回调 / 企业可信IP
  - 企微API / 企微发送 / 企业微信推送
---

# 企业微信自建应用 API 发送打通与排障

打通企微自建应用「主动发消息」的完整前置条件与排障流程。适用于任意自建应用（营销号推送、通知等）。

## 发送前置条件链（顺序不能反，2026.9 实测）

新自建应用要能 `message/send` + `media/upload`，必须先满足两条前置：

1. **接收消息服务器URL（回调）必须先配**——否则「企业可信IP」配置入口根本不开放（控制台提示"请先设置可信域名或接收消息服务器URL"）。这条卡住了很多次。
2. **企业可信IP**：应用详情 → 开发者接口 → 企业可信IP → 加入当前调用方公网IP。

完整控制台操作路径见 `references/wecom-callback-infra.md`。

## 报错对照（gettoken 成功 ≠ 能发送）

| 错误码 | 含义 | 处理 |
|--------|------|------|
| `40001 invalid credential` | CorpID/Secret 不匹配（密钥被轮换 / 应用被删） | 停下，先引导更新凭证，不硬发 |
| `60020 not allow to access from your ip` | 可信IP 未配或已变 | 去后台企业可信IP加当前公网IP（`curl -s ifconfig.me`） |
| `60002` | 接收人 userid 不对 | 核对接收人 userid |

**重点**：`gettoken` 只需要 CorpID+Secret 有效即可成功，**不需要可信IP**；但 `message/send`、`media/upload` **需要可信IP**。所以「token 拿到了」不等于「能发」，报 60020 是正常的中间态。

家庭宽带公网IP是动态的，断网重连会变——重连后若报 60020，去后台把新 IP 换掉即可，不是凭证失效。

## 凭证轮换流程（应用重建/密钥更新）

1. 用户提供新 AgentId + Secret（或 CorpID 变了也要改）
2. 先 `gettoken` 连通性测试——**只取 token，不发任何消息**
3. token 有效后，把新 Secret/AgentId **全量替换**写进依赖此凭证的技能（Secret 和 AgentId 会在技能中出现多处，用 replace_all，勿只改一处）
4. 若调用方 IP 报 60020，引导用户先把回调+可信IP 配好（见 references）
5. **仍须用户明示"发送"才调 send**（见下）

## 发送必须人工确认（2026.9.5 用户明确）

企微发送是**对外动作**，无论技术是否就绪，**任何 message/send 都必须在发送前得到用户明确批示**。绝不自动推送、绝不"勿问确认"直接发。

标准流程：先生成好文案+配图并交付审阅 → 用户说"发送/一起发/可以发" → 才调 API。用户只说"先备好/拟好/生成"时只交付不发送。

## 现成回调基础设施（复用，勿另起炉灶）

盈信已在阿里云 ECS `47.103.27.171` 配好一套回调：域名 `callback.yingxinkuaiji.com`（Let's Encrypt）、nginx 把 `/wecom/callback` 代理到 `127.0.0.1:8800`（`/opt/wecom-bot` 的 hermes_bridge.py）。Token/AESKey/完整配置值都在：
**`references/wecom-callback-infra.md`**

新 Agent 配「接收消息」时直接复用这套三件套（URL/Token/EncodingAESKey，加密方式选**安全模式**），即可通过验签，无需再搭回调服务器。

## 排障：控制台提示「openapi回调地址请求不通过」

三种已实锤的根因，按此顺序排查（详细命令在 `references/wecom-callback-infra.md`）：
1. nginx 把 `/wecom/callback` 重写成 `/wecom` → 后端 404。curl 直接打后端确认路径。
2. sites-enabled 残留旧备份抢同一域名（reload 报 `conflicting server name` 是信号）。
3. **最常见的真病根**：wechatpy `WeChatCrypto.check_signature(self, signature, timestamp, nonce, echo_str)` —— 参数顺序是 `(签名, 时间戳, nonce, echostr)`。老代码误写成别序会导致验签永不通过，看 hermes_bridge.py 里的调用顺序，改对后 `systemctl restart wecom-bridge.service`。

**验证不需要等控制台**：跑 `scripts/verify_wecom_callback.py <Token> <AESKey> <CorpID> <URL>`，它会按安全模式构造一次真实的 GET 验签请求，回包 == 明文 echostr 即通过（不通过可放心去修，别反复让用户点保存）。

## AI 机器人（WebSocket）模式凭证排障（2026-09 实测）

AI 机器人模式（双向对话、群内@回复）凭证与自建应用不同：只要 `bot_id` + `secret` 两个，无 CorpID/AgentId/回调。接通前先做**格式体检**（不碰值，只检查格式，防止无效重试）：

1. **.env 变量格式检查**（只输出长度/ASCII 特征，不打印值）：
   - `WECOM_BOT_ID`：约 35 位纯 ASCII（`aib...` 开头）→ 正常
   - `WECOM_SECRET`：**40+ 位纯字母数字**；若长度只有个位数或混入中文字符（如「新」）＝从富文本/消息里误复制，凭证必坏，须回企微后台重新复制
   - 判据：`has_space` / `nonascii` 任一为真 → 可疑
2. **systemd 服务未必加载 .env**：`hermes gateway install` 生成的 service 有时只带 ExecStart+PATH、**没有 EnvironmentFile** → gateway 进程读不到 WECOM_*。验证：`systemctl --user show -p MainPID --value hermes-gateway` → `tr '\0' '\n' < /proc/<PID>/environ | grep -c WECOM`（0 = 没加载）
3. **config.yaml 无 platforms 节**：`gateway.platforms` 为 NONE 时等于没配任何平台，需要 `enabled: true` + `extra.bot_id/secret`（或等价环境变量方案）
4. **群机器人(Webhook) ≠ AI 机器人**：用户给的是 URL 那种是单向推送、不能双向对话；要的是后台「AI 机器人」的 Bot ID + Secret。用户常混淆：给 corp_id/应用 AgentId（自建应用回调模式的）≠ AI 机器人凭证——按上面格式体检立刻能分辨
5. **多机器抢答**：接通前确认 Windows 侧无 WorkBuddy/Claw 连同一机器人（参考 hermes-agent references/wecom-multi-bot-conflict.md）

### ✅ 已实测的完整接通路径（2026-09-13 成功）

凭证格式正常后，三步接通（每步都可独立验证）：

```bash
# ① 写 .env（只替换那两行，不破坏其他键）—— 值不打印
# ② config.yaml 启用 wecom 平台（用 hermes config set，别手改 yaml）
hermes config set gateway.platforms.wecom.enabled true
hermes config set gateway.platforms.wecom.extra.dm_policy open
hermes config set gateway.platforms.wecom.extra.group_policy open
hermes config set gateway.platforms.wecom.extra.bot_id <bot_id>   # secret 留在 .env，config 只需 bot_id
# ③ systemd service 补 EnvironmentFile（关键！否则 gateway 读不到 .env 的 secret）
#   在 ~/.config/systemd/user/hermes-gateway.service 的 Environment 行后加：
#     EnvironmentFile=/home/dmin/.hermes/.env
systemctl --user daemon-reload && systemctl --user restart hermes-gateway
```

**验证成功标志**（journalctl / gateway.log）：
```
[Wecom] Connected to wss://openws.work.weixin.qq.com
✓ wecom connected
```
看到这两行即接通。若只看到 `wecom_callback` 的 `40001 invalid credential` 报错——那是自建应用回调模式在用旧的 corp 凭证报错，**不影响** wecom（AI机器人 WebSocket）通道，属外观噪音可忽略。⚠️ 它由 `WECOM_CALLBACK_CORP_ID`+`WECOM_CALLBACK_CORP_SECRET` 环境变量在代码里强制自启（gateway/config.py），**config.yaml 写 enabled:false 关不掉**；要根治只能清除注入源 env（.env / Windows 侧启动脚本），详见 references/wecom-ai-bot-mode-diagnostics.md。

### 接通后的用户侧验证（必做，区分「真机器人」与「旧Webhook」）

日志连通 ≠ 用户能对话，必须让用户在企业微信客户端实测：

1. **方式一（最简单）**：在企微客户端搜索/通讯录找到该机器人（如 yingxin_inner），**直接私聊发一句话**（如「你是谁」），收到 Hermes 自我介绍回复 = 真通了
2. **方式二**：在群里 **@机器人名 + 一句话**，能在群内回复 = 通过
3. **判定**：收到回复 ✅ 接通成功；发出去没反应/提示「机器人未接入」⚠️ = 这个 bot 大概率是**旧的 Webhook 群机器人**（单向推送、不能对话），不是刚配的 AI 机器人——回去核对 Bot ID 对应的到底是哪个机器人（openBotProfile 链接里的机器人名 vs 用户心目的名字）

**「可对话」才是最终验收标准**——gateway 日志显示 connected 只能证明 WebSocket 通了，不代表用户侧能收到回复。

**errcode 语义（WebSocket 模式）**：
- `853000 invalid bot_id or secret` → AI 机器人凭证错误（含旧日志里 2026-09-12 的 `invalid bot_id or secret ... errcode=853000` 就是凭证坏时的报错）
- `40001 invalid credential`（出现在 wecom_callback 条目下）→ 是自建应用 corp 凭证的问题，与 wecom 通道无关，别误判成 AI 机器人失败

详细诊断命令与完整实录见 `references/wecom-ai-bot-mode-diagnostics.md`。

## 关联技能

- **wechat-moments-marketing** — 朋友圈/营销号文案的企微推送流程（含发送模板、配图），触发「朋友圈」用那个
- **wecom-external-service** — 企微 AI 服务规范（回复风格/时间感知/非财税流程），偏行为层
- 本技能偏**基础设施/排障层**：报错、回调、可信IP、凭证轮换
