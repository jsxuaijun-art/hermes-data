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
GET /health → {"status":"ok", "service":"wecom-bot", ...}
```

### 企微自建应用回调
```
GET  /wecom → URL验证 (msg_signature + echostr)
POST /wecom → 消息回调 (加密XML → 解密 → AI回复 → 加密返回)
```

### 企微智能机器人回调
```
GET  /smartrobot → URL验证
POST /smartrobot → 消息回调 (加密XML only — NOT plain JSON)
```

### 主动推送端点
```
POST /push  Content-Type: application/json
{"msgtype":"text","text":{"content":"Hello"}}
# 或
{"msgtype":"markdown","markdown":{"content":"# 标题\n内容"}}
```

## 机器人类型辨析（重要）

### 智能机器人（已有的）
- 能力: **只能回复@消息**，不能主动发消息
- 回调地址: `https://callback.yingxinkuaiji.com/smartrobot`
- BOTID + Secret: 用于回调鉴权，不是 API 调用凭证

### 自定义Webhook机器人（需要新建）
- 创建: 企微群 → ⋮ → 群机器人 → 添加 → 自定义Webhook
- Webhook URL: `https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=XXXXX`
- 能力: **只能主动发消息**，不能接收消息

### 两种推送途径
| 途径 | 配置难度 | 能力 |
|------|---------|------|
| 自定义Webhook机器人 | 1分钟，群设置里添加 | ✅ 主动推送，❌ 不能回复 |
| 应用自建API | 需要应用Secret | ✅ 可推送可回复，但需要应用级别权限 |

### API 验证
```bash
# 验证自定义Webhook
curl -s -X POST "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=XXXXX" \
  -H "Content-Type: application/json" \
  -d '{"msgtype":"text","text":{"content":"test"}}'
# errcode: 0 = success, 93000 = invalid webhook url
```

## 环境变量
| 变量 | 用途 |
|------|------|
| `WECOM_CORP_ID` | 企业微信企业ID |
| `WECOM_TOKEN` | 自建应用Token |
| `WECOM_AES_KEY` | 自建应用AES Key |
| `SMARTROBOT_TOKEN` | 智能机器人Token |
| `SMARTROBOT_AES_KEY` | 智能机器人AES Key |
| `OPENAI_API_KEY` | DeepSeek API Key |
| `OPENAI_BASE_URL` | `https://api.deepseek.com/v1` |
| `AI_MODEL` | `deepseek-chat` |
| `WECOM_WEBHOOK_KEY` | 企微群自定义Webhook Key |

## 关键坑点
1. `/smartrobot` 不接受明文JSON — 必须通过企微回调协议发加密XML
2. 推送消息必须用 `/push`，不要试图复用 `/smartrobot`
3. 没有 Webhook Key 时，消息只接收不转发 (`errcode: -1`)
4. 修改 app.py 后必须 `systemctl restart wecom-bot`
