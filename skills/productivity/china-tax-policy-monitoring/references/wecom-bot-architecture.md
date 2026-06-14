# 企业微信智能机器人服务架构（阿里云）

## 概述

阿里云服务器（47.103.27.171）上运行一个 Flask 企业微信智能机器人服务，为苏州盈信企业管理有限公司的企微群提供 AI 客服能力 + 财税情报日报推送通道。

## 服务信息

| 项目 | 值 |
|------|------|
| 域名 | callback.yingxinkuaiji.com → 47.103.27.171 |
| 端口 | 8800 (gunicorn), 443 (nginx SSL) |
| 代码 | `/opt/wecom-bot/app.py` |
| 配置 | `/opt/wecom-bot/.env` |
| 日志 | `/var/log/wecom-bot/access.log`, `/var/log/wecom-bot/error.log` |
| 进程 | gunicorn -w 2 -b 127.0.0.1:8800 |
| 守护 | `wecom-bot.service` (systemd) |

## 端点一览

### Health Check

```
GET /health
→ {"status":"ok", "service":"wecom-bot", "ai_configured":true, "model":"deepseek-chat", "working_time":true}
```

### 企微自建应用回调

```
GET  /wecom → URL验证 (msg_signature + echostr)
POST /wecom → 消息回调 (加密XML → 解密 → AI回复 → 加密返回)
```

使用 `WECOM_TOKEN`, `WECOM_AES_KEY`, `WECOM_CORP_ID` 配置。

### 企微智能机器人回调

```
GET  /smartrobot → URL验证 (自定义解密，跳过CorpID校验)
POST /smartrobot → 消息回调 (同上，但用 SMARTROBOT_TOKEN/SMARTROBOT_AES_KEY)
```

> ⚠️ `/smartrobot` 仅处理加密XML（企微回调协议）。**不接受明文JSON POST到 `/smartrobot`**，会返回500。

### 主动推送端点

```
POST /push
Content-Type: application/json

{"msgtype":"text","text":{"content":"Hello"}}
# 或
{"msgtype":"markdown","markdown":{"content":"# 标题\n内容"}}
```

当前状态：未配置Webhook Key时，消息被接收但不转发到企微群。

### 兼容端点

```
POST /webhook → 别名，同 /push
```

## 环境变量

| 变量 | 用途 |
|------|------|
| `WECOM_CORP_ID` | 企业微信企业ID (`wwc7fc356cf7297e7f`) |
| `WECOM_TOKEN` | 自建应用Token |
| `WECOM_AES_KEY` | 自建应用AES Key |
| `SMARTROBOT_TOKEN` | 智能机器人Token |
| `SMARTROBOT_AES_KEY` | 智能机器人AES Key |
| `OPENAI_API_KEY` | DeepSeek API Key |
| `OPENAI_BASE_URL` | `https://api.deepseek.com/v1` |
| `AI_MODEL` | `deepseek-chat` |
| `AI_SYSTEM_PROMPT` | 系统提示词（财税顾问） |
| `WECOM_WEBHOOK_KEY` | 企微群自定义Webhook Key（未配置） |

## 工作时间逻辑

服务内置工作时间判断：
- 工作时间（周一至周五 08:30–17:30，非节假日）：AI回复
- 非工作时间/节假日：自动回复话术（说明工作时间，提供紧急电话）

节假日判断依赖 `chinese-calendar` 库。

## 推送脚本

路径：`/opt/wecom-bot/push_report.py`

用途：Hermes cron 生成日报后，由agent调用此脚本将报告内容POST到 `/push` 端点。

```python
from push_report import push_report
result = push_report(report_content, msgtype="markdown")
# result = {"errcode":0,"errmsg":"received, webhook not configured"} 或成功后的 {"errcode":0,"errmsg":"ok"}
```

## 重启命令

```bash
systemctl restart wecom-bot
systemctl status wecom-bot
```

## Nginx配置

/etc/nginx/sites-enabled/callback 将 callback.yingxinkuaiji.com 全部代理到 :8800。

## 关键坑点

1. `/smartrobot` 不接受明文JSON —— 必须通过企微回调协议发加密XML
2. 推送消息必须用 `/push`，不要试图复用 `/smartrobot`
3. 没有 Webhook Key（WECOM_WEBHOOK_KEY）时，消息只接收不转发
4. 修改 app.py 后必须 `systemctl restart wecom-bot` 生效

## 机器人类型辨析（重要）

企微群机器人有**两种不同类别**，容易混淆：

### 智能机器人（已有的）
- 机器人链接: `https://work.weixin.qq.com/wework_admin/common/openBotProfile/<ID>`
- 回调地址: `https://callback.yingxinkuaiji.com/smartrobot`
- Token / AES Key: 用于加解密回调 XML
- 能力: **只能回复@消息**，不能主动发消息
- BOTID + Secret: 用于回调鉴权，不是 API 调用凭证

### 自定义Webhook机器人（需要新建）
- 创建路径: 企微群 → 右上角 ⋮ → 群机器人 → 添加 → 自定义Webhook
- Webhook URL: `https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=XXXXX`
- 参数: 仅一个 UUID 格式的 key
- 能力: **只能主动发消息**，不能接收消息
- errcode 93000: 表示 webhook URL 无效（key 格式不对或机器人不存在）

### API 调用验证

```
# 验证自定义Webhook（正确格式）
curl -s -X POST "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=XXXXX" \
  -H "Content-Type: application/json" \
  -d '{"msgtype":"text","text":{"content":"test"}}'

# 返回值：
# 正确 → {"errcode":0,"errmsg":"ok"}
# 无效 → {"errcode":93000,"errmsg":"invalid webhook url"}
```

### 两种推送途径

| 途径 | 配置难度 | 能力 |
|------|---------|------|
| 自定义Webhook机器人 | 1分钟，群设置里添加 | ✅ 主动推送，❌ 不能回复 |
| 应用自建API | 需要应用Secret，写代码 | ✅ 可推送可回复，但需要应用级别权限 |

当前架构使用**自定义Webhook机器人**作为日报推送通道。

## 相关参考

- 企业微信智能机器人回调API文档：`https://developer.work.weixin.qq.com/document/path/99110`
- 企微自定义Webhook机器人：群设置 → 群机器人 → 添加 → 自定义
