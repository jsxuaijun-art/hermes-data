# 企业微信 (WeCom) 网关配置

Hermes Agent 的企业微信网关有 **两种适配模式**，适用场景和凭证需求不同。

## 方式一：AI 机器人 WebSocket 模式 (`wecom`)

**平台名：** `wecom`  
**适配器文件：** `gateway/platforms/wecom.py`  
**协议：** 持久 WebSocket 连接（aibot_subscribe / aibot_send_msg）

### 凭据
- **bot_id** — 机器人 ID（WeCom 后台创建 AI 机器人时获得）
- **secret** — 机器人密钥
- **websocket_url** — WebSocket 地址（默认 `wss://openws.work.weixin.qq.com`）

### 配置示例
```yaml
gateway:
  platforms:
    wecom:
      enabled: true
      extra:
        bot_id: "your-bot-id"          # 或 WECOM_BOT_ID 环境变量
        secret: "your-secret"          # 或 WECOM_SECRET 环境变量
        websocket_url: "wss://openws.work.weixin.qq.com"  # 可选，有默认值
        dm_policy: "open"              # open | allowlist | disabled | pairing
        allow_from: ["user_id_1"]
        group_policy: "open"           # open | allowlist | disabled
        group_allow_from: ["group_id_1"]
        groups:
          group_id_1:
            allow_from: ["user_id_1"]
```

### 获取凭证方式

#### 方式 A：内置二维码扫码流程（推荐）

运行 `hermes gateway setup`（交互式），会展示二维码供用户在企业微信中扫码，扫码后自动获取 `bot_id` 和 `secret`。

建议先安装 QR 码渲染库以获得更好的终端显示效果：
```bash
pip install qrcode
```

#### 方式 B：手动创建（适用于扫码不可用时）

当用户无法看到终端 QR 码（如通过 SSH、CI/CD、或 agent 工具调用），或者不方便用手机扫码时，走此路线：

**在企业管理后台创建 AI 机器人：**
1. 打开 https://work.weixin.qq.com/wework_admin/ → 应用管理
2. 找到"AI 机器人"（或在"自建"区域）→ 创建 AI 机器人
3. 创建完成后，获取 **Bot ID** 和 **Secret**

**通过环境变量配置（无需修改 config.yaml）：**
```bash
export WECOM_BOT_ID="aibCgyqs_xxxxxxxxxxxxxxxxxxxx"
export WECOM_SECRET="qCB8YuT6xxxxxxxxxxxxxxxxxxxxxxxxxxx"
export GATEWAY_ALLOW_ALL_USERS="true"    # 必须！否则群成员 @机器人 会被拒绝
```

**验证配置是否正确：**
```bash
cd /path/to/hermes-agent
WECOM_BOT_ID="..." WECOM_SECRET="..." python3 -c "
from gateway.config import load_gateway_config
gw_cfg = load_gateway_config()
for p, cfg in gw_cfg.platforms.items():
    if cfg.enabled:
        print(f'✅ {p.value}: enabled, bot_id={cfg.extra.get(\"bot_id\",\"?\")}')
"
```
验证返回 `✅ wecom: enabled` 说明配置正确。

**重要：.env 文件不会被 gateway 自动加载。** 即使 `~/.hermes/.env` 中有 `WECOM_BOT_ID` 和 `WECOM_SECRET`，`hermes gateway run` 也不会读取。必须通过 `export` 显式设置环境变量，或在启动命令前设置：
```bash
export WECOM_BOT_ID="..." && export WECOM_SECRET="..." && export GATEWAY_ALLOW_ALL_USERS="true" && hermes gateway run
```

### 特点
- 不需要公网 IP
- 即连即用
- 双向通信（收发消息）— 群成员 @机器人 就能对话
- **注意区分：** 企业微信**群机器人（Webhook）** 和 **AI 机器人** 是不同的东西：
  - 群机器人（Webhook）：单向通道，只能往外推送消息，不能收消息，不能回复 @
  - AI 机器人（WebSocket）：双向通道，能收能发，群里 @它 会回复

### 互动式扫码配置流程

运行 `hermes gateway setup` 进入交互式配置向导：

```
hermes gateway setup
```

**导航方式：** 向导使用 curses 交互界面（↑↓ 箭头导航，Enter/空格选择）。但当通过管道（stdin pipe）输入时，会降级为数字选择模式：

```bash
# 数字选择模式（适用于自动化）
echo -e "12\n1" | hermes gateway setup
# 12 = WeCom (Enterprise WeChat)
# 1  = Scan QR code (recommended)
```

**QR 码显示：**
- 向导内置 QR 码渲染（ASCII art），扫码即可
- 如需更好的 QR 码支持：`pip install qrcode`（安装后自动使用）
- 扫码失败/不方便时，终端会同时显示一个 URL，可在手机企业微信中直接打开：
  ```
  https://work.weixin.qq.com/ai/qc/gen?source=hermes&scode=XXXXXXXX
  ```
- **注意：** scode 每次运行都不同，不能复用

**扫码后流程：**
1. 用户打开企业微信 → 扫 QR 码（或打开 URL）
2. 确认授权
3. 向导自动获取 bot_id 和 secret，写入 config.yaml
4. 提示是否安装 gateway 为系统服务

**超时处理：** 向导会等待扫码直到完成（无超时），所以用管道方式运行时务必加 `timeout`：

```bash
timeout 15 bash -c 'echo -e "12\n1" | hermes gateway setup' 2>&1 || true
```

---

## 方式二：自建应用回调模式 (`wecom_callback`)

**平台名：** `wecom_callback`  
**适配器文件：** `gateway/platforms/wecom_callback.py`  
**协议：** HTTP 回调（WeCom POST 加密 XML 到 HTTP 端点，通过 access-token 主动发送消息）

### 凭据
- **corp_id** — 企业 ID
- **corp_secret** — 应用 Secret
- **agent_id** — 应用 AgentId
- **token** — 回调 URL 配置时自定义的 Token
- **encoding_aes_key** — 回调 URL 配置时获取的 EncodingAESKey

### 配置示例
```yaml
gateway:
  platforms:
    wecom_callback:
      enabled: true
      extra:
        host: "0.0.0.0"               # HTTP 服务监听地址
        port: 8645                      # HTTP 服务端口
        path: "/wecom/callback"         # 回调路径
        # 支持多应用，方式一：单应用简写
        corp_id: "wwc7fc356cf7297e7f"
        corp_secret: "your-secret"
        agent_id: "1000036"
        token: "your-token"
        encoding_aes_key: "your-aes-key"
        # 方式二：多应用显式列表
        # apps:
        #   - name: "my-app"
        #     corp_id: "ww..."
        #     corp_secret: "..."
        #     agent_id: "1000036"
        #     token: "..."
        #     encoding_aes_key: "..."
```

### 特点
- 需要公网可达的 HTTP 端点（或使用内网穿透如 frp/ngrok）
- 需要在 WeCom 管理后台配置回调 URL
- 适合已有自建应用的企业场景
- 支持同时配置多个应用

### 配置回调 URL 步骤
1. 在 WeCom 管理后台 → 应用管理 → 自建应用 → 功能设置 → 配置开发后端
2. URL 填入 `http://<你的公网IP>:8645/wecom/callback`
3. Token 和 EncodingAESKey 随机生成，与配置中的值保持一致
4. 应用功能中开启"接收消息"
5. 在群聊中添加该应用机器人

---

## 常见问题

### .env 文件不生效，gateway 说"No messaging platforms enabled"

**根因：** `hermes gateway run` **不会自动加载** `~/.hermes/.env`。即使 `.env` 中有 `WECOM_BOT_ID` 和 `WECOM_SECRET`，gateway 进程也读不到。

**解决方案：** 启动前显式 export 环境变量：
```bash
export WECOM_BOT_ID="..."
export WECOM_SECRET="..."
export GATEWAY_ALLOW_ALL_USERS="true"
hermes gateway run
```

或者单行形式（适用于 background 启动）：
```bash
export WECOM_BOT_ID="..." && export WECOM_SECRET="..." && export GATEWAY_ALLOW_ALL_USERS="true" && hermes gateway run
```

### Gateway 启动后还是旧配置

先杀掉旧进程再重启：
```bash
pkill -f "hermes gateway" 2>/dev/null
sleep 1
echo "" > ~/.hermes/logs/gateway.log   # 清空日志方便定位
export WECOM_BOT_ID="..." && export WECOM_SECRET="..." && hermes gateway run
```

### 机器人连接成功但 @它 不回复

**根因：** 缺少 `GATEWAY_ALLOW_ALL_USERS=true`。Gateway 默认拒绝未授权用户，AI 机器人虽然连接上了 WebSocket，但来自群成员的 @ 消息会被网关丢弃。

**解决：** 启动前设置 `export GATEWAY_ALLOW_ALL_USERS="true"`，或配置平台级别的 `dm_policy: open` / `group_policy: open`。

### 群机器人（Webhook）vs AI 机器人 — 有什么区别？

| | 群机器人 (Webhook) | AI 机器人 (WebSocket) |
|---|---|---|
| 方向 | 单向（仅推送） | 双向（收发） |
| 回复 @ | ❌ 不能 | ✅ 能 |
| 配置方式 | 群设置 → 添加机器人 → 获得 URL | `hermes gateway setup` 扫码 |
| 公网 IP | 不需要 | 不需要 |
| 由谁创建 | 群成员在群设置中添加 | 企业微信管理后台或扫码授权 |
| 用途 | 推送通知、日报、告警 | 对话、问答、任务执行 |

**常见误解：** 用户可能在群里添加的是 Webhook 机器人（拿到一个 URL 那种），然后期待它能被 @ 并回复。需要向用户解释这是两回事，如果要双向对话需要配置 AI 机器人模式。

### `hermes` 命令不在 PATH 中怎么办？

在非交互式环境（后台进程、工具调用、Windows 启动脚本）中，`hermes` 可能不在 PATH 中。使用完整路径：

```bash
# 查找 hermes 可执行文件
find ~/.hermes -name "hermes" -type f 2>/dev/null
# 通常在：~/.hermes/venv/bin/hermes 或 ~/.hermes/.venv/bin/hermes

# 然后用完整路径运行
/home/administrator/hermes-agent/venv/bin/hermes gateway run
```

**常见场景：** 在 Hermes Agent 的 `terminal(background=true)` 工具中启动网关时，必须用完整路径，因为后台进程不会加载 `.bashrc`/`.bash_profile`。

### WSL + Windows 开机自动启动

当 Windows 重启后，WSL 实例可能尚未运行。需要以下设置确保网关开机后自动启动：

**前提：** `/etc/wsl.conf` 必须有 `systemd=true`：
```ini
[boot]
systemd=true
```

**步骤 1：安装为 systemd 用户服务**
```bash
hermes gateway install
```
该命令会自动执行：
- 创建 `~/.config/systemd/user/hermes-gateway.service`
- 启用服务（`systemctl --user enable`）
- 启用 linger（`loginctl enable-linger $USER`）确保断开 SSH 后服务仍运行

**步骤 2：创建 Windows 启动脚本**

将以下内容保存到 Windows 启动文件夹：

文件位置：`C:\Users\<用户名>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\hermes-gateway.bat`

```bat
@echo off
wsl -d <发行版名> systemctl --user start hermes-gateway
```

发行版名可通过 `wsl -l -v` 查看，通常是 `Ubuntu` 或 `Ubuntu-24.04`。

**注意：** .bat 文件名和内容必须为纯 ASCII，不能有中文或 Unicode 字符，否则在中文 Windows 上会乱码。

**步骤 3：验证**
```bash
systemctl --user status hermes-gateway
# → Active: active (running)
# → 日志中有: ✓ wecom connected
```

**完整启动链路：**
```
Windows 开机 → 用户登录 → 启动文件夹运行 .bat
  → wsl -d Ubuntu systemctl --user start hermes-gateway
  → WSL 启动 → systemd 启动 → 网关启动 → WeCom WebSocket 连接
  → 群里 @机器人 即可回复 ✅
```

### Gateway 安装为系统服务（systemd）

安装为 systemd 用户服务后，网关会随系统自动启动，WSL 重启后也无需手动拉起。

```bash
# 安装（创建 systemd service 文件并启用）
hermes gateway install

# 重新加载配置
systemctl --user daemon-reload

# 启动服务
systemctl --user start hermes-gateway

# 查看状态
systemctl --user status hermes-gateway
# 确认 Active: active (running) 表示成功

# 查看实时日志
journalctl --user -u hermes-gateway -f
```

**环境变量处理：** `hermes gateway install` 生成的 systemd service 文件会自动加载 `~/.hermes/.env` 中的变量（通过 `EnvironmentFile` 指令）。因此将凭证写入 `.env` 后，**服务模式下无需手动 export**。

**注意：** 先运行 `hermes gateway run`（前台）测试配置正确后，再切换为 systemd 服务模式。

**WSL 兼容性：** 确保 `/etc/wsl.conf` 中有 `systemd=true`，否则 systemd 服务在 WSL 上不会自动启动。

### 日志查看
```bash
grep -i "wecom" ~/.hermes/logs/gateway.log | tail -20
grep -i "wecom" ~/.hermes/logs/agent.log | tail -20
```

### 依赖检查
两种模式都依赖 `aiohttp` 和 `httpx`：
```bash
pip install aiohttp httpx
```

### 端口占用
如果端口被占用，更换 `port` 值后重启 gateway。

### iptables UDP 限制导致部分请求丢包
部分主机商可能会对新安装的 Linux 限制 UDP。如果 gateway
频繁断开重连，请先检查是否被上游防火墙拦截。
```bash
# 检查 UDP 包丢弃统计
netstat -s | grep -i "udp.*error"
```
