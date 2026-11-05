# AI 机器人（WebSocket）模式诊断实录（2026-09）

企业微信「AI 机器人」模式（Hermes gateway `wecom` 平台）接通实录。
本模式只需 `bot_id` + `secret`（后台「AI 机器人」创建获得），无 CorpID/AgentId/回调。
对照 shebang：`hermes-agent` 内置参考 `references/wecom-gateway.md` 为权威。

## 1. .env 凭证格式体检（不碰值）

```bash
cd /home/dmin/.hermes && python3 - <<'EOF'
for line in open(".env", encoding="utf-8", errors="replace"):
    line=line.rstrip("\n")
    if not line or line.startswith("#") or "=" not in line: continue
    k,v=line.split("=",1); v=v.strip().strip('"').strip("'")
    has_nonascii=any(ord(c)>127 for c in v)
    nonascii_chars=sorted({repr(c) for c in v if ord(c)>127})
    print(f"{k}: len={len(v)} ascii_only={not has_nonascii} nonascii={nonascii_chars}")
EOF
```

判定（2026-09 实测）：
- `WECOM_BOT_ID: len=35 ascii_only=True` → 正常 ✅
- `WECOM_SECRET: len=7 ascii_only=False nonascii=["'新'"]` → 损坏 ❌
  - 正常 secret 40+ 位纯字母数字；位数个位+含汉字 = 从别人消息/PDF/富文本误复制
- 凭证损坏**无法本地修复**——必须回后台重取；不碰值、不猜值
- 用户常给 corp_id（如 `wwc7fc...`，自建应用模式用）冒充 AI 机器人凭证——格式体检立刻分辨
- 用户给的 Bot ID 也可能看似 32 位十六进制（那是 openBotProfile 链接里的 ID）——真正的 WECOM_BOT_ID 是 `aib...` 开头的 35 位

## 2. systemd service 是否加载 .env（本会话的元凶）

```bash
cat ~/.config/systemd/user/hermes-gateway.service
# 本机实测只有 ExecStart + Environment(PATH/VIRTUAL_ENV/HERMES_HOME)，无 EnvironmentFile
# → gateway 进程读不到 .env 里的 WECOM_SECRET/WECOM_BOT_ID

# 运行中进程验证（0 = 没加载）
PID=$(systemctl --user show -p MainPID --value hermes-gateway)
tr '\0' '\n' < /proc/$PID/environ 2>/dev/null | grep -c WECOM
```

参考文档说 `hermes gateway install` 会带 EnvironmentFile，但**本机实测缺失**——以实际 service 文件为准。

**修复**（本会话 2026-09-13 实测成功）：
在 service 文件的 `Environment=` 行后追加：
```
EnvironmentFile=/home/dmin/.hermes/.env
```
再 `systemctl --user daemon-reload && systemctl --user restart hermes-gateway`。

## 3. config.yaml 平台配置（用 hermes config set）

```bash
# 检查：NONE → 任何平台都没配
python3 -c "import yaml; d=yaml.safe_load(open('/home/dmin/.hermes/config.yaml')); print(d.get('gateway',{}).get('platforms'))"

# 启用（2026-09-13 实测：这些命令成功且 config.yaml 写出正确）
hermes config set gateway.platforms.wecom.enabled true
hermes config set gateway.platforms.wecom.extra.dm_policy open
hermes config set gateway.platforms.wecom.extra.group_policy open
hermes config set gateway.platforms.wecom.extra.bot_id <bot_id>
```
secret 只需在 .env（WECOM_SECRET），config 里只有 bot_id 即可。改 config 前先备份 `.env` / `config.yaml` / service 文件（时间戳后缀），可回滚。

## 4. 验证成功标志（本会话实测）

重启后日志（journalctl --user -u hermes-gateway 或 ~/.hermes/logs/gateway.log）：
```
Connecting to wecom...
[Wecom] Connected to wss://openws.work.weixin.qq.com
✓ wecom connected
```
看到 `✓ wecom connected` 即 WebSocket 通道接通。

### errcode 语义（重要，勿误判）
- `853000 invalid bot_id or secret` → AI 机器人凭证错误（2026-09-12 旧日志里的 `invalid bot_id or secret ... errcode=853000` 就是坏凭证导致的——不是环境问题）
- `40001 invalid credential` 出现在 **wecom_callback**（自建应用回调模式）条目下 → 那是 corp 凭证问题，与 wecom（AI机器人）通道无关，别误判成失败
- `wecom_callback` 平台即使 config 里没配也可能被默认代启，报 40001 是外观噪音，可忽略

### wecom_callback 自动启用的根因（2026-09-13 确认，勿再踩 config=false 的坑）

`wecom_callback` 是**代码级自动启用**，不是 config 开关能关掉的：

- 源码位置：`hermes-agent/gateway/config.py` ~L1314-1326 —— `if os.getenv("WECOM_CALLBACK_CORP_ID") and os.getenv("WECOM_CALLBACK_CORP_SECRET"): ... enabled = True`（还读 AGENT_ID/TOKEN/ENCODING_AES_KEY/HOST=0.0.0.0/PORT=8645）
- 即：**只要启动 gateway 的进程环境里存在 `WECOM_CALLBACK_CORP_ID` + `WECOM_CALLBACK_CORP_SECRET` 这两个变量，它就被强制启用**——无论 config.yaml 写 `gateway.platforms.wecom_callback.enabled: false`（实测：config set false 后重启，它照样监听 8645 并刷 40001）
- **正确关闭方式**：从注入源清掉/置空这两个 env 变量（.env、Windows 侧 WorkBuddy/自建应用部署的启动脚本、systemd Environment 等），而不是改 config.yaml
- 它监听 `0.0.0.0:8645/wecom/callback`，是自建应用 HTTP 回调模式，与 wecom（AI机器人 WebSocket）通道互不抢占；只要没有可用 corp 凭证它只是每次启动刷一条 40001 噪音，**不影响 AI 机器人对话功能**，非必需时可接受留着

## 5. 开通前必查项

- [ ] 用户提供正确的 Bot ID + Secret（后台：应用管理 → AI 机器人；客户端路径：工作台 → 智能机器人 → 创建机器人 → API 模式/手动创建）
- [ ] 区分：群机器人 Webhook（单向 URL）≠ AI 机器人（双向，可@回复）；corp_id（自建应用）≠ Bot ID
- [ ] Windows 侧无 WorkBuddy/Claw 连同一机器人（避免抢答；见 hermes-agent references/wecom-multi-bot-conflict.md）
- [ ] service 补 EnvironmentFile（或把凭证写进 config）——最易漏的一步
- [ ] 最后让用户在企业微信里 @ 机器人试发消息，确认能收到回复（端到端验证）

## 实际凭证/配置备忘（2026-09-13 本机）
- `.env`：`WECOM_BOT_ID`（35位 aib 开头）+ `WECOM_SECRET`（43位纯字母数字）+ `GATEWAY_ALLOW_ALL_USERS=true`
- `config.yaml`：`gateway.platforms.wecom` 已启用
- systemd：`~/.config/systemd/user/hermes-gateway.service` 已加 EnvironmentFile
- 备份：`.env`、`config.yaml`、service 均有时间戳备份
- Bot 资料页：`https://work.weixin.qq.com/wework_admin/common/openBotProfile/<id>`