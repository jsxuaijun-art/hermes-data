# 企业微信机器人云端部署拓扑指南

> 2026.6.23 实战记录

## 核心事实

**企微AI机器人 WebSocket 通道是独占连接** — 同一时间只能有一个gateway实例连接到同一个机器人（bot ID）。第二个连接会被平台强制断开（Connected → Disconnected 间隔1-2秒）。

这意味着：WSL和云端不能同时连接同一个yingxin_inner机器人。

## 推荐拓扑：云端7×24常驻

### 架构

```
┌─────────────────────┐     ┌──────────────────────┐
│  阿里云 ECS ☁️       │     │  WSL 本地 🖥️         │
│  47.103.27.171      │     │                      │
│                     │     │  wecom.enabled: false │
│  wecom.enabled: true │     │  (不连接企微)          │
│  └→ yingxin_inner   │     │  api_server: enabled  │
│  7×24 在线          │     │  CLI正常使用           │
│  agent处理客户消息   │     │                      │
└─────────────────────┘     └──────────────────────┘
         ↕ WebSocket                    ↕ SSH/API
    ┌──────────────┐             
    │ 企业微信平台   │
    │ yingxin_inner │
    └──────────────┘
```

### 配置

**云端（阿里云）** — `/root/.hermes/config.yaml`:
```yaml
platforms:
  wecom:
    enabled: true    # 连接企微机器人
  api_server:
    enabled: true    # 可选，需要设 API_SERVER_KEY
```

**WSL本地** — `/home/dmin/.hermes/config.yaml`:
```yaml
platforms:
  wecom:
    enabled: false   # 关闭，避免抢连接
  api_server:
    enabled: true    # 留用于本地调试
```

### 切换流程（如需反向）

WSL想临时接管机器人时：
```bash
# 1. WSL本地启用wecom
# 手动改 config.yaml: wecom.enabled → true
# 2. 重启WSL gateway
systemctl --user restart hermes-gateway.service
# 3. 云端自动断开，WSL接管
# 4. 用完切回来:
#   ssh到云端 systemctl restart hermes-gateway.service
#   WSL改回 wecom.enabled: false → 重启gateway
```

### 优势
- 7×24小时稳定在线，客户随时能@到
- WSL自由调试、开发，不干扰生产
- 零切换延迟，无需心跳检测

## 常见运维问题

### 云端gateway重启卡死

**现象**：`systemctl restart` 后 stuck 在 `deactivating (stop-sigterm)` 超过1分钟

**根因**：旧进程有挂起的API调用（tool_executor的terminal pending_approval），不响应SIGTERM

**解决**：
```bash
# 先查PID
systemctl status hermes-gateway.service
# 强杀
kill -9 <PID>
# systemd Restart=always 会自动拉起新进程
```

### 云端api_server拒绝启动

**现象**：日志报 `[Api_Server] Refusing to start: API_SERVER_KEY is required`

**原因**：新版本Hermes要求api_server必须配密钥，即使绑定127.0.0.1

**影响**：不影响wecom消息收发（wecom是独立通道）

**修复**：在`.env`或config.yaml中设置`API_SERVER_KEY`

### WSL端api_server仅警告（不拒绝）

**现象同，但不会挂掉**：`WARNING gateway.platforms.api_server: ⚠️ No API key configured`

**原因**：WSL运行的是较旧版本的Hermes，对新版要求不严格

## 版本差异注意

- 阿里云端 Hermes 版本较新，config.yaml结构更严格
- WSL端 Hermes 版本较旧，部分配置宽松
- 同步 config.yaml 时注意云端有额外字段要求