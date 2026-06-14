# 盈信财税情报日报 — 阿里云全栈部署实录

## 架构

```
阿里云 (47.103.27.171)
├── Hermes Gateway (systemd) → cron周一三五09:05
│   └── cron job: 766017656bde
│       ├── script: cron/unified_tax_loader.py
│       ├── prompt模版: cron/daily_tax_intelligence.md
│       │                cron/weekly_tax_deep_dive.md
│       └── 产出: ~/tax_intel/daily/YYYY-MM-DD.md
│                ~/tax_intel/weekly/YYYY-Www.md
│
├── WeCom Bot Flask (wecom-bot.service, gunicorn :8800)
│   ├── GET /smartrobot → 企微智能机器人回调
│   ├── POST /push      → 接收cron推送消息
│   ├── POST /webhook   → /push 的别名
│   └── .env → 含 DEEPSEEK_API_KEY / WECOM_WEBHOOK_KEY
│
├── Nginx (:443, certbot)
│   └── callback.yingxinkuaiji.com → proxy_pass :8800
│
└── WeCom群自定义Webhook机器人
    └── key=41872151-7e41-410f-b006-a0db3f6f4e30
```

## 推送数据流

```
cron触发 → Hermes AI 搜5+来源生成报告
  → 保存到 ~/tax_intel/daily/YYYY-MM-DD.md
  → 执行推送指令: python3 /opt/wecom-bot/push_report.py <file> markdown
    → POST https://callback.yingxinkuaiji.com/push
      → Flask路由 handle_push()
        → 企微API: https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx
          → 群内"财税情报日报"机器人发出消息
```

## 关键文件路径

| 文件 | 路径（阿里云） |
|------|---------------|
| Loader脚本 | `/root/.hermes/cron/unified_tax_loader.py` |
| 每日模版 | `/root/.hermes/cron/daily_tax_intelligence.md` |
| 周度模版 | `/root/.hermes/cron/weekly_tax_deep_dive.md` |
| 推送脚本 | `/opt/wecom-bot/push_report.py` |
| Flask应用 | `/opt/wecom-bot/app.py` |
| 环境变量 | `/opt/wecom-bot/.env` |
| Hermes配置 | `/root/.hermes/config.yaml` |
| Hermes Key | `/root/.hermes/.env` |
| cron job定义 | `/root/.hermes/cron/jobs.json` |
| GitHub同步 | `jsxuaijun-art/hermes-data.git` → `cron/` 目录 |

## Provider配置

Hermes v0.15.1 阿里云上的provider配置在 `config.yaml`:
```yaml
model:
  default: deepseek-v4-flash
  provider: deepseek
  base_url: https://api.deepseek.com/v1
```
API Key来自 `.env` 文件中的 `DEEPSEEK_API_KEY` 环境变量。

## 关键注意事项

### API Key更新
- 不要用 `sed` 更新 `.env` 中的API Key（`.`通配符、`$`展开都会导致失败）
- 用Python写文件：读→替换行→写
- 更新后必须重启服务：`systemctl restart hermes-gateway wecom-bot`

### Gateway配置
- cron job定义在 `jobs.json` 而非通过CLI创建（v0.15.1 CLI有参数解析bug）
- 手动修改 `jobs.json` 后必须重启Gateway才能生效
- 格式必须是 `{"jobs": [...]}` 对象包裹，不能是裸数组

### WeComBot 推送端点
- 接收 text 和 markdown 两种格式
- 先返回 `received, webhook not configured`（Webhook Key为空时）
- 配置 `WECOM_WEBHOOK_KEY` 后自动转发到企微群

### 定时任务日程
- 周一三五 09:05 CST
- 周一：每日监控 + 周度分析（含机会雷达+月度战略）
- 周三/周五：仅每日监控
- 非推送日不执行

### 报告内容质量保障
- 模板要求 AI 搜索至少5个来源，每个来源至少2条信息
- 所有信息必须标注来源URL
- 产出包含：热点摘要、案例拆解、风险提醒、内容营销选题（视频号/抖音/小红书）、客户咨询切入口
