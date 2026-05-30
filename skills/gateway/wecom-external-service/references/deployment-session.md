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

---

## 会话日志：2026.5.11 — 方案A决策与执行计划

### 背景

上轮通过 WebSocket 模式部署了外部 profile，但发现 **AI机器人不支持外部群**。本轮重新审视方案选型。

### 三方案对比（2026.5.11）

| 方案 | 名称 | 成本 | 外部群支持 | 复杂度 |
|:--:|:--|:--:|:--:|:--:|
| A | 自建应用+回调模式 | ¥99/年（服务器）+ ¥30~50/年（域名） | ❌（仅内部群/DM） | ⭐⭐⭐ |
| B | 内部群+人工转发 | 零成本 | ✅（间接） | ⭐ |
| C | 单聊私信模式 | 零成本 | ✅（私聊通道） | ⭐ |

### 方案A完整实施步骤

**采购清单：**
- 轻量服务器 2核2G（阿里云/腾讯云 ¥68~99/年）
- 域名 .com/.cn（¥30~50/年）
- ICP备案（免费，需3~7工作日）

**8步执行计划：**

| 步骤 | 内容 | 预估耗时 | 依赖 |
|:--:|:--|:--:|:--:|
| ① | 买服务器 + 装 Ubuntu 22.04 | 1小时 | 无 |
| ② | 买域名 + DNS指向服务器IP | 1小时 | 步骤① |
| ③ | 提交ICP备案 | 3~7天 | 步骤② |
| ④ | Nginx + HTTPS配置 | 1小时 | 备案通过 |
| ⑤ | 企微后台创建自建应用+回调URL | 30分钟 | 步骤④ |
| ⑥ | Hermes Gateway配置 wecom_callback | 1小时 | 步骤⑤ |
| ⑦ | DM与群聊分流配置 | 30分钟 | 步骤⑥ |
| ⑧ | 端到端测试 | 1小时 | 步骤⑦ |

### 云厂商推荐

| 对比项 | 阿里云 | 腾讯云 |
|:--:|:--:|:--:|
| 配置 | 2核2G 200M峰值带宽 | 2核2G 3M固定带宽 |
| 硬盘 | 40GB ESSD | 50GB SSD |
| 流量 | 不限 | 300GB/月 |
| 新客价 | ¥68/年 | ¥68/年 |
| 续费价 | ~¥99/年 | ¥99/年 |

**推荐：阿里云轻量应用服务器（¥68/年，不限流量）**

### 当前进度（2026.5.12 更新）

- [x] 需求确认（外部群客户服务）
- [x] 方案选型（用户选择了方案A - 自建应用+回调模式）⚠️ 注意：方案A仍不支持外部群，仅解决延迟+免@问题
- [x] 执行计划输出
- [x] **步骤①：买服务器（已完成 ✅）**
  - 平台：阿里云 轻量应用服务器
  - 配置：2vCPU / 2GiB / 40GB ESSD / 200Mbps 峰值带宽 / 不限流量
  - 地域：华东2（上海）
  - 镜像：Ubuntu 22.04
  - 价格：¥79/年
  - 公网IP：47.103.27.171
  - SSH 连通性：已确认 ✅（Ubuntu 22.04, 5.15.0-142, 1.6G RAM, 40GB 可用35G）
- [ ] **步骤②：买域名 + DNS（进行中 🔄）**
  - 域名已有：yingxinkuaiji.com（西部数码）
  - 计划子域名：callback.yingxinkuaiji.com → 47.103.27.171
  - DNS记录待添加（西部数码字段：主机名=callback, 类型=A, 记录值=47.103.27.171, 线路=默认, 优先级留空）
- [ ] **步骤③：ICP备案（进行中 🔄 — 已发现备案号苏ICP备15030316号-1仍然活跃！）**
  - 备案号：苏ICP备15030316号-1
  - 主体：苏州盈信企业管理有限公司
  - 域名：yingxinkuaiji.com
  - 状态：活跃（2026-05-02 最后更新）
  - 结论：无需新备案，做"新增接入备案"即可，预计1~2天
  - 💡 关键发现：域名平台（西部数码）显示"删除" ≠ 工信部数据库删除。第三方查询（icplishi.com）证实备案仍在。
- [ ] 步骤④~⑧：配置到上线的后续步骤

### 关键提醒（2026.5.12 新增）

**方案A的核心矛盾仍未解决：** 自建应用回调模式**仍然无法加入外部群**。选择方案A的主要收益是：
- ✅ 消除串行延迟（DM与群聊分流到不同 agent 实例）
- ✅ 免@唤醒（回调模式收所有消息，网关自行过滤）
- ❌ 外部群依然收不到消息

这一限制在用户开始实施时**必须再次告知**，避免用户在步骤⑤~⑧完成后发现"还是不能放到外部群"而产生失望。
