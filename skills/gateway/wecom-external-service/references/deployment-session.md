# 外部群机器人部署实录（2026.5.10）

## 环境

- 江姐：苏州盈信企业管理有限公司创始人/高级会计师
- Hermes Agent 运行在 WSL2 Ubuntu 22.04
- Hermes 路径：`/mnt/c/Users/Admin/WorkBuddy/20260424224200/hermes-agent-official`
- 已有：默认 profile 运行内部群 AI 机器人（WebSocket 模式）
- 新增：external profile 运行外部客户群 AI 机器人（WebSocket 模式）

## 操作步骤摘要

### 1. 创建外部 AI 机器人在企微管理后台

1. 登录 https://work.weixin.qq.com/wework_admin → 应用管理 → AI机器人
2. 点击"创建新AI机器人"，填写名称（建议：盈信智能助手）
3. 创建后获取 Bot ID 和 Secret

### 2. 创建外部 Profile

```bash
cd ~/hermes-agent-official

# 列出已有 profile
.venv/bin/python -m hermes_cli.main profile list

# 创建 external profile（从 default 克隆）
.venv/bin/python -m hermes_cli.main profile create external --clone

# 克隆完成后控制台显示：87 bundled skills synced.
```

### 3. 配置外部 Profile

**config.yaml** (`~/.hermes/profiles/external/config.yaml`)

将 platforms 段从：
```yaml
platforms:
  wecom_callback:
    enabled: true
  wecom:
    enabled: true
```
改为：
```yaml
platforms:
  wecom:
    enabled: true
    extra:
      bot_id: "新BotID"
      secret: "新Secret"
      group_policy: "open"
      dm_policy: "open"
```

**说明**：凭证写入 `extra` 段而非 `.env`，因为 `hermes gateway run` 不自动加载 `.env`。

**.env** (`~/.hermes/profiles/external/.env`)

仅保留以下变量，移除所有无关项（尤其 `WECOM_CALLBACK_*`）：
- `DEEPSEEK_API_KEY`
- `HERMES_MAX_ITERATIONS`
- `FAL_KEY`
- `TAVILY_API_KEY`
- `OPENROUTER_API_KEY`
- `WECOM_BOT_ID` = 新BotID
- `WECOM_SECRET` = 新Secret
- `GATEWAY_ALLOW_ALL_USERS=true`
- `WECOM_HOME_CHANNEL=XuAiJun`

**SOUL.md** (`~/.hermes/profiles/external/SOUL.md`)

替换为行为规则内容（身份定位 + 时间感知回复 + 数据安全边界 + 人员识别规则 + 部署指南 + 踩坑记录 + 多场景扩展策略）。

### 4. 启动 Gateway

```bash
# 注意：因 terminal 工具限制，使用 background=true 启动
.venv/bin/python -m hermes_cli.main -p external gateway run
```

### 5. 验证连接

```bash
cat ~/.hermes/profiles/external/logs/gateway.log | grep -E "wecom|connect|error"
```

期望输出关键信息：
```
✓ wecom connected
[Wecom] Connected to wss://openws.work.weixin.qq.com
Gateway running with 1 platform(s)
```

### 6. 将机器人拉入群

⚠️ **注意**：2026.5.10 研究发现，AI机器人（WebSocket模式）**不支持外部群**，详见本文件末尾的「关键发现」一节。

选项A：如果部署目标是内部群 → 企微客户端打开内部群 → 右上角··· → 添加成员 → 搜索机器人名称 → 勾选确认。

选项B：如果部署目标是外部群 → 需要改用「自建应用+回调模式」，本技能 SKILL.md 的「替代架构」一节有详细方案对比。

## 踩坑记录

### 坑1：wecom_callback 反复重试

即使 config.yaml 中删除了 `wecom_callback` 平台，gateway 日志仍显示：
```
Connecting to wecom_callback...
[WecomCallback] Port 8645 already in use
```

**原因**：网关自动发现/加载所有已注册平台模块，不完全依赖 config 配置。
**解决**：无需处理。外部群只需要 WebSocket 模式，callback 失败不影响功能。

如果希望消除日志噪音，可进一步排查环境变量 `WECOM_CALLBACK_*` 或平台模块注册逻辑。

### 坑2：凭证放 .env 不生效

`.env` 文件中的 `WECOM_BOT_ID` / `WECOM_SECRET` 在 `hermes gateway run` 启动时**不会被自动加载**。
systemd service 模式下才加载 `.env`。

**解决**：凭证写入 `config.yaml` 的 `platforms.wecom.extra` 字段。

### 坑3：双 Gateway 端口冲突

内部 `default` profile 的 gateway 已经占用了 callback 端口 8645。外部 profile 启动时 callback 端口冲突。

**解决**：外部 profile 只使用 WebSocket 模式（`platforms.wecom`），callback 错误可忽略。

## 后续维护

- 内部群 gateway（default profile）正常运行，进程 PID 为系统常驻
- 外部群 gateway（external profile）需通过 `.venv/bin/python -m hermes_cli.main -p external gateway run` 单独管理
- 外部群重启后需重新确认 WebSocket 连接状态
- 每月评估场景 B/C/D 的启用时机
