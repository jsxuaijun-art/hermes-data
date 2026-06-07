# WSL Manager 架构 — 完整实现参考

部署日期：2026.6.3
最后修改：2026.6.3

## 架构图

```
企微用户 → WeCom WebSocket
                ↓
          cloud gateway (阿里云 ECS, :5280)
                ↓
    pre_gateway_dispatch plugin hook
           (wsl-status-injector)
                ↓
    GET :18923/status → active_handler = ?
                ↓
    "cloud" → prefix "[☁ 云端处理中]"
    "wsl-*" → prefix "[💻 本机 xxx 处理中]"
                ↓
          Hermes Agent 正常处理 → 回复 + 前缀

WSL 启动流程：
  双击 hermes-wsl.bat 或 敲 hermes
    → hermes-wsl.sh 启动
      → 检查云端 API :18923 是否在线
      → 显示当前处理端
      → 询问用户选择 [1=本机/2=云端/3=不改变]
      → POST /claim → 注入前缀改
      → 进入 Hermes CLI
      → 退出时 trap 自动 POST /release
```

## 组件清单

| 组件 | 位置 | 类型 | 端口 | 职责 |
|------|------|------|------|------|
| `hermes-wsl-manager.service` | 阿里云 systemd | systemd service | TCP 18923 | 状态API |
| `wsl-status-injector` | `/root/.hermes/plugins/wsl-status-injector/` | Hermes 插件 | — | gateway hook |
| `hermes-wsl.sh` | WSL `~/.hermes/hermes-wsl.sh` | bash 脚本 | — | 启动入口 |
| `hermes-wsl.bat` | Windows 桌面 | bat 启动器 | — | 双击入口 |
| `wsl_state.json` | `/root/.hermes/wsl_state.json` | JSON 持久化 | — | 状态存储 |

## API 完整源码 (`/usr/local/bin/hermes_wsl_manager.py`)

```python
#!/usr/bin/env python3
"""
Hermes WSL Manager — 云端状态管理API
监听端口 18923
用于管理各台WSL的在线状态，控制企微消息路由

API:
  GET  /status          → 返回当前状态
  POST /claim           → WSL声明接管处理权
  POST /release         → WSL声明释放处理权
  GET  /active          → 返回当前活跃处理端
"""

import json
import os
import time
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

STATE_FILE = "/root/.hermes/wsl_state.json"

DEFAULT_STATE = {
    "active_handler": "cloud",
    "handlers": {},
    "updated_at": 0
}

def load_state():
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE) as f:
                return json.load(f)
    except Exception:
        pass
    return dict(DEFAULT_STATE)

def save_state(state):
    state["updated_at"] = int(time.time())
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

class Handler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def _read_body(self):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 0:
            return json.loads(self.rfile.read(content_length))
        return {}

    def do_GET(self):
        state = load_state()
        if self.path == "/status":
            self._send_json({
                "status": "ok",
                "active_handler": state["active_handler"],
                "handlers": state["handlers"],
                "updated_at": state["updated_at"]
            })
        elif self.path == "/active":
            self._send_json({
                "active_handler": state["active_handler"],
                "handler_info": state["handlers"].get(state["active_handler"])
            })
        elif self.path == "/health":
            self._send_json({"status": "ok"})
        else:
            self._send_json({"error": "not found"}, 404)

    def do_POST(self):
        state = load_state()
        try:
            body = self._read_body()
        except Exception:
            self._send_json({"error": "invalid json"}, 400)
            return

        handler_id = body.get("handler_id", "")
        hostname = body.get("hostname", "")
        password = body.get("password", "")

        # 简单鉴权
        if password != "yx168168/*-":
            self._send_json({"error": "unauthorized"}, 401)
            return

        if self.path == "/claim":
            if not handler_id:
                self._send_json({"error": "handler_id required"}, 400)
                return

            state["active_handler"] = handler_id
            state["handlers"][handler_id] = {
                "hostname": hostname,
                "claimed_at": int(time.time()),
                "last_heartbeat": int(time.time())
            }
            save_state(state)
            self._send_json({"status": "claimed", "active_handler": handler_id})

        elif self.path == "/release":
            if handler_id and handler_id == state["active_handler"]:
                state["active_handler"] = "cloud"
                if handler_id in state["handlers"]:
                    del state["handlers"][handler_id]
                save_state(state)
                self._send_json({"status": "released", "active_handler": "cloud"})
            else:
                self._send_json({"status": "no_change", "active_handler": state["active_handler"]})

        elif self.path == "/heartbeat":
            if handler_id and handler_id in state["handlers"]:
                state["handlers"][handler_id]["last_heartbeat"] = int(time.time())
                save_state(state)
                self._send_json({"status": "ok"})
            else:
                self._send_json({"status": "unknown_handler"})

        else:
            self._send_json({"error": "not found"}, 404)

    def log_message(self, format, *args):
        sys.stderr.write("[%s] %s - %s\n" % (self.log_date_time_string(), self.client_address[0], format % args))


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 18923
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Hermes WSL Manager API running on 0.0.0.0:{port}")
    server.serve_forever()
```

## Gateway Hook 插件完整源码 (`__init__.py`)

```python
"""
WSL Status Injector Plugin

在 WeCom 消息的 agent 开始处理之前，通过 pre_gateway_dispatch hook
检查当前活跃的处理端（WSL 本机 / 阿里云端），并在消息中注入状态前缀。
"""

import json
import logging
import urllib.request

logger = logging.getLogger("plugins.wsl-status-injector")

WSL_MGR_URL = "http://127.0.0.1:18923"


def _get_status() -> dict:
    """从 WSL Manager API 获取状态"""
    try:
        req = urllib.request.Request(f"{WSL_MGR_URL}/status", method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        logger.warning("API unavailable: %s", e)
        return {"active_handler": "cloud", "handlers": {}}


def _on_dispatch(**kwargs):
    """
    pre_gateway_dispatch plugin hook callback.
    只处理 WeCom 外部消息，注入状态前缀。
    
    返回值格式：
      None / {"action": "allow"}  → 继续正常处理
      {"action": "rewrite", "text": "..."} → 替换消息内容
      {"action": "skip", "reason": "..."} → 丢弃消息
    """
    event = kwargs.get("event")
    if event is None:
        return None

    source = getattr(event, "source", None)
    if source is None:
        return None

    # ⚠️ platform 是 Platform 枚举，不是字符串！必须比较 .value
    platform = getattr(source, "platform", None)
    platform_val = getattr(platform, "value", "") if platform else ""

    if platform_val != "wecom":
        return None

    # 跳过内部消息
    if getattr(event, "internal", False):
        return None

    text = getattr(event, "text", "")
    if not text or not isinstance(text, str):
        return None

    # 避免重复注入
    if text.startswith("[☁") or text.startswith("[💻"):
        return None

    status = _get_status()
    active = status.get("active_handler", "cloud")
    handlers = status.get("handlers", {})

    if active == "cloud":
        prefix = "[☁ 云端处理中]"
    else:
        handler_info = handlers.get(active, {})
        hostname = handler_info.get("hostname", active)
        prefix = f"[💻 本机 {hostname} 处理中]"

    modified = f"{prefix}\n{text}"
    logger.info("wecom msg: '%.40s...' → handler=%s", text, active)

    return {"action": "rewrite", "text": modified}


def register(ctx):
    """Hermes 插件入口"""
    ctx.register_hook("pre_gateway_dispatch", _on_dispatch)
    logger.info("wsl-status-injector registered")
```

## systemd 服务文件 (`/etc/systemd/system/hermes-wsl-manager.service`)

```ini
[Unit]
Description=Hermes WSL Manager - 云端WSL状态管理API
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /usr/local/bin/hermes_wsl_manager.py 18923
Restart=always
RestartSec=5
User=root
Group=root
WorkingDirectory=/tmp
StandardOutput=append:/var/log/hermes-wsl-manager.log
StandardError=append:/var/log/hermes-wsl-manager.log

[Install]
WantedBy=multi-user.target
```

## WSL 启动脚本 (`~/.hermes/hermes-wsl.sh`)

```bash
#!/bin/bash
CLOUD_IP="47.103.27.171"
CLOUD_PASS="yx168168/*-"
HOSTNAME=$(hostname)
HANDLER_ID="wsl-${HOSTNAME}"

# 工具函数：向云端API发POST（SSH嵌套引号逃逸）
cloud_post() {
    local path="$1" data="$2"
    sshpass -p "$CLOUD_PASS" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@$CLOUD_IP "
        printf '%s' '$data' | curl -s -X POST http://127.0.0.1:18923/$path \
            -H 'Content-Type: application/json' -d @-
    " 2>/dev/null
}

cloud_get() {
    sshpass -p "$CLOUD_PASS" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@$CLOUD_IP "
        curl -s http://127.0.0.1:18923/$1
    " 2>/dev/null
}

# 退出时自动释放
cleanup() {
    local json="{\"handler_id\":\"$HANDLER_ID\",\"password\":\"$CLOUD_PASS\"}"
    cloud_post "release" "$json" > /dev/null
    echo "☁  已归还至云端"
}
trap cleanup EXIT SIGTERM SIGINT

# ... 检查API、显示当前状态、询问用户选择、claim/release ...

# 关键：默认使用 printf '%s' + curl -d @- 避免JSON引号爆炸
# 关键：trap cleanup EXIT 确保退出时自动释放

cd "$HOME"
python3 -m hermes_cli.main chat
```

## Windows 桌面 bat (`hermes-wsl.bat`)

```bat
@echo off
chcp 65001 >nul
title Hermes Agent — WSL 启动器
wsl ~ -e bash -l ~/.hermes/hermes-wsl.sh
```

## 安装部署命令速查

```bash
# 1. 创建启动脚本
bash /root/hermes_wslmgr_start.sh

# 2. 安装 systemd 服务
cp /tmp/hermes-wsl-manager.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable hermes-wsl-manager
systemctl start hermes-wsl-manager

# 3. 安装插件
mkdir -p /root/.hermes/plugins/wsl-status-injector/
# 放入 plugin.yaml + __init__.py
hermes plugins enable wsl-status-injector
hermes gateway restart   # 重启才能加载插件

# 4. 验证
curl -s http://127.0.0.1:18923/health
hermes logs --lines 20 | grep -i "injector\|register"
systemctl is-active hermes-wsl-manager hermes-gateway
```

## 常见故障

### `active_handler` 没更新
→ 检查 `wsl_state.json` 文件权限
→ 检查 API 日志 `/var/log/hermes-wsl-manager.log`

### 前缀没注入
→ 检查 gateway 日志：插件是否 loaded（`grep injector`）
→ 检查 `_on_dispatch` 里 `platform_val` 是否为 `"wecom"`
→ 注意：枚举比较必须用 `.value`，不能用 `!= "wecom"` 直接比

### SSH 命令返回为空
→ 检查 `sshpass` 是否正确安装
→ 试着手动 SSH：`sshpass -p '密码' ssh root@IP 'echo hello'`
→ 检查 /root/.ssh/known_hosts 是否冲突

### API 端口被占用
```bash
lsof -ti:18923 | xargs kill -9
systemctl restart hermes-wsl-manager
```
