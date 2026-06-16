# WeCom 机器人身份诊断 — 谁在回答？

> 创建: 2026.6.3 — 现场实录：用户发现企业微信机器人自称"WorkBuddy Claw"而非Hermes

## 适用场景

企业微信机器人自报身份异常（Claw/Hermes/WorkBuddy/答非所问），或怀疑有两套系统同时运行。

## 诊断流程（从外到内）

### 第1步 — 问它自己（最快）

直接在企业微信里提问：

> "你究竟是WorkBuddy的机器人还是Hermes的机器人？"

**参照解读：**

| 回答 | 判定 |
|------|------|
| "我是WorkBuddy的Claw 🦾" | **Windows WorkBuddy** 在提供服务 |
| "我是Hermes Agent" | **云端 Hermes Gateway** 在服务，但需检查 SOUL.md 版本 |
| "我是盈信财税助手" 或自定义身份 | **云端 Hermes Gateway** 服务中，且已加载完整 SOUL.md |
| 无响应 | 两套系统都可能不在线 → 走常规gateway故障排查 |

### 第2步 — 检查云端 Gateway 是否运行

```bash
# SSH 登录云端
sshpass -p 'yx168168/*-' ssh root@47.103.27.171

# 三连查
systemctl status hermes-gateway.service 2>/dev/null && echo "service 存在" || echo "无 systemd 服务"
ss -tlnp | grep 8645    # wecom_callback 端口
cat /root/.hermes/gateway_state.json | python3 -c "import sys,json; d=json.load(sys.stdin); print('wecom state:', d.get('platforms',{}).get('wecom',{}).get('state'))"
```

**三连全空** → 云端 Gateway 不在运行，WeCom 一定由 Windows WorkBuddy 服务。

### 第3步 — 检查 Windows WorkBuddy 进程

```bash
# 从 WSL 查询（通过 /mnt/c 挂载或 wmic）
/mnt/c/Windows/System32/cmd.exe /c "tasklist | findstr /i workbuddy"
# 或
cat /proc/$(pgrep -f 'WorkBuddy')/status 2>/dev/null
```

**有进程** → WorkBuddy 在运行，占用了 WeCom 连接。

### 第4步 — 检查 DNSS

```bash
dig wecom.yingxinkuaiji.com +short
```

确认域名指向哪台服务器。当前配置（2026.6.3）指向 `47.103.27.171`（阿里云ECS）。

### 第5步 — 核对 SOUL.md 版本（云端）

```bash
# root 用户的 Hermes（gateway 使用）
cat /root/.hermes/SOUL.md | head -5
# 期望输出：完整的 "你是 Hermes Agent，一个以结果为导向的专业AI助手" 版本
# 如果只看到 "<!-- Edit this file to customize..." 默认模板 → SOUL.md 未同步

# dmin 用户的 Hermes（CLI 使用）
cat /home/dmin/.hermes/SOUL.md | head -5
```

**注意**：云端存在两套 Hermes 实例（root + dmin 两个用户），各自有独立的SOUL.md。Gateway 读取 root 用户（`/root/.hermes/`）的配置。即使 dmin 的 SOUL.md 是完整版，root 的仍是默认模板的话，机器人依然以默认身份回答。

## 典型案例（2026.6.3 现场）

| 检查项 | 结果 | 结论 |
|--------|------|------|
| 机器人自报名 | "我是WorkBuddy的Claw" | **Windows WorkBuddy 在线** |
| 云端 systemd 服务 | 不存在 | 云端 Gateway 未部署/未启用 |
| 云端 8645 端口 | 无监听 | wecom_callback 未运行 |
| Windows WorkBuddy.exe | 8 个进程，334MB+ | 正在运行 |
| 域名解析 | → 47.103.27.171 | 但云端无服务接收流量 |

**根本原因**：计划中的"云端 Hermes 接管企业微信"未完成。WorkBuddy 一直开机运行，持续占用 WeCom 连接。

## 接管操作（从WorkBuddy切换到云端Hermes）

### 前置确认

```bash
# 云端 Gateway 配置完整
ssh root@47.103.27.171
grep WECOM /root/.hermes/.env
# 必须看到：WECOM_BOT_ID / WECOM_SECRET / WECOM_CORP_ID

# SOUL.md 已同步（不是默认模板）
head -3 /root/.hermes/SOUL.md
```

### 执行接管

1. **云端** — 启动 Hermes Gateway
```bash
# 如果有 systemd 服务
systemctl start hermes-gateway.service
# 如果没有，通过 hermes CLI 启动
hermes gateway start
```

2. **Windows** — 关闭 WorkBuddy
```cmd
# Windows 命令提示符
taskkill /f /im WorkBuddy.exe
```
或从任务栏退出 WorkBuddy。

3. **验证** — 等 30 秒后问机器人"你是谁"
```text
预期：云端 Hermes + 完整 SOUL.md → 回答为自定义身份
实际：如果仍是 Claw → WorkBuddy 未完全退出
```

## 补充（2026.6.3 更新）: WSL Manager 架构与Claw混淆解决

即使 WorkBuddy 已关闭、云端 Gateway 正常运行，用户仍可能在企微看到"它刚才说自己是Claw"的困惑。

**WSL Manager 的机制**：`pre_gateway_dispatch` hook **不改变机器人身份**，只注入 `[☁ 云端处理中]` / `[💻 本机 xxx 处理中]` 前缀。机器人始终说"我是 Hermes Agent"。

**如果用户说"它刚才说自己是Claw"**，排查方向：
1. WorkBuddy 是否真的关了？（`tasklist | findstr /i workbuddy` 确认）
2. 是不是在聊历史消息？之前的 Claw 回复是旧的聊天记录
3. 直接问一条新消息 + 看消息前缀：`[☁` 或 `[💻` 说明是 Hermes 在处理

详见 `references/wsl-manager-architecture.md`（本skill的新增参考文件）。