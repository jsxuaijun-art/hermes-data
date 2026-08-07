# 企业微信 Hermes Gateway 运维实战手册

## 适用场景

阿里云 ECS 上 Hermes Gateway 企业微信（WeCom）机器人不工作、报 401、无响应时的排查和修复。

---

## 故障模式速查

| 症状 | 大概率根因 | 修复动作 |
|------|-----------|---------|
| 401 API Key Invalid | Gateway 配置不全（缺 CorpID）+ 进程重启后配对丢失 | 补 `.env` 三要素 + 重启 | 
| "shutdown" warning | `--replace` 触发进程重启 | 等自动恢复，或手动 restart |
| 机器人不回复消息 | WeCom 连接断开 | 检查 gateway_state.json 的 wecom.state |
| `/approve always` 后还拦 | 安全扫描感知配置没持久化 | 重新 `/approve always` 一次 |
| pairing data not found | 配对已丢，但可能是正常状态（Webhook 模式不走 pairing） | 先检查 gateway_state.json 的 wecom.state |

---

## 完整恢复流程

### 第 1 步：快速健康检查

```bash
sshpass -p 'yx168168/*-' ssh root@47.103.27.171 "bash /root/.hermes/scripts/hermes_config_audit.sh"
```

扫出 0 错误 0 警告 → 去第 4 步验证
有错误 → 继续

### 第 2 步：检查企业微信三要素

```bash
sshpass -p 'yx168168/*-' ssh root@47.103.27.171 "grep WECOM /root/.hermes/.env"
```

必须同时存在且不为空：

- `WECOM_BOT_ID` — 企业微信应用的 AgentId
- `WECOM_SECRET` — 企业微信应用的 Secret
- `WECOM_CORP_ID` — 企业微信的企业 ID

**常见缺失项**：`WECOM_CORP_ID`（上次故障就是缺这个）

企业 ID 获取方式：登录 https://work.weixin.qq.com/wework_admin/frame#apps → 我的企业 → 企业信息 → 企业ID

### 第 3 步：修复并重启 Gateway

```bash
# 补上缺失的配置项
sshpass -p 'yx168168/*-' ssh root@47.103.27.171 "echo 'WECOM_CORP_ID=wwc7fc356cf7297e7f' >> /root/.hermes/.env"

# 或替换已有项（如果已存在但值不对）
sshpass -p 'yx168168/*-' ssh root@47.103.27.171 "sed -i 's/WECOM_CORP_ID=.*/WECOM_CORP_ID=wwc7fc356cf7297e7f/' /root/.hermes/.env"

# 重启 Gateway
sshpass -p 'yx168168/*-' ssh root@47.103.27.171 "systemctl restart hermes-gateway.service"

# 等待 3 秒，检查连接状态
sleep 3
sshpass -p 'yx168168/*-' ssh root@47.103.27.171 "cat /root/.hermes/gateway_state.json | python3 -c \"import sys,json; d=json.load(sys.stdin); print('wecom:', d.get('platforms',{}).get('wecom',{}).get('state'))\""
```

期望输出：`wecom: connected`

### 第 4 步：在企业微信验证

给 Hermes 机器人发一条消息，确认能正常回复。

如果第一次通知时被安全扫描拦截 → 回复 `/approve always` 永久放行。

---

## Gateway 进程重启机制

Gateway 启动参数含 `--replace`，意味着：

1. 检测到已有关联进程 → 杀掉旧进程 → 启动新进程
2. 触发条件：WeCom WebSocket 断连后重连时
3. 旧进程被干掉时，如果用户正在提问 → 用户侧看到 "shutdown" 警告
4. 新进程启动后如果配置不全 → 连不上企业微信

**关键理解**：`--replace` 不是 bug，是 Hermes 的设计——保证同一时刻只有一个 Gateway 进程在跑。但配对的丢失和配置不全才是需要防范的。

---

## 三层防护体系

### 第一层：systemd 自动重启（已默认启用）

- `Restart=always`
- `RestartSec=5`
- 进程挂了后 5 秒自动拉起来
- 配置路径：`/etc/systemd/system/hermes-gateway.service`

### 第二层：健康巡检 cron（2026.5.27 部署）

- 每 30 分钟执行 `/root/.hermes/scripts/hermes_health_check.sh`
- 检查 Gateway 进程和 wecom 连接状态
- 发现掉线自动重启
- 日志：`/var/log/hermes-health-check.log`

### 第三层：配置审计（按需执行）

- 手动执行：`bash /root/.hermes/scripts/hermes_config_audit.sh`
- 检查项：5 个关键环境变量、系统服务状态、磁盘/内存、关键目录、备份覆盖

---

## 备份保护

`.env` 已加入阿里云推送脚本的备份清单（2026.5.27）：

```bash
# /root/.hermes/sync-push-cloud.sh 中
cp -f /root/.hermes/.env "$SYNC_DIR/env" 2>/dev/null || true
```

这意味着 `.env` 里的三要素（CorpID、Secret、BotId）会每30分钟自动推到 GitHub。即使阿里云磁盘被重置，也可以从 GitHub 恢复。

---

## 安全扫描特殊情况

企业微信群内执行 `curl wttr.in/...` 查天气时会被 Hermes 安全扫描拦截，原因：

1. **Schemeless URL** — `wttr.in/` 没有 `https://` 前缀
2. **Non-ASCII characters** — 中文参数（体感/湿度）和 Emoji（💧🌬️）
3. **Variation selector** — Emoji 序列包含变体选择器

**解决方案**：用户在企业微信群里发 `/approve always` 永久放行。这不是配置问题，不需要服务端干预。

---

## 历史故障记录

### 2026.5.27 — 企业微信 401 故障

- **现象**：机器人报 401 API Key Invalid
- **根因**：`.env` 缺少 `WECOM_CORP_ID`（企业ID），Gateway 进程 `--replace` 重启后无法认证
- **修复**：补 CorpID + 重启 Gateway
- **教训**：备份没覆盖 `.env`，配置丢失后恢复成本高
- **产出的永久性方案**：配置审计脚本、健康巡检 cron、`.env` 备份覆盖
