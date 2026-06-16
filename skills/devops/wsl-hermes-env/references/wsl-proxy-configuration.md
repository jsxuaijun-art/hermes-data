# WSL 代理配置 — 从 Windows Clash 到 WSL 全链路

> 场景：WSL 内所有 CLI 工具（Codex、Hermes、pip、curl、git、npm）需要走 Windows 上的代理（Clash/V2Ray 等）
> 关键原则：**WSL 不能用 `127.0.0.1` 当 Windows 代理地址**——那是 WSL 自己的 localhost

---

## 架构概要

```
Windows (Clash/CordCCore) → 0.0.0.0:7890 (HTTP)
    ↑                         ↓
WSL 通过 Windows IP 访问 ← 自动检测 WIN_IP
```

---

## 标准配置流程

### 第一步：检测 Windows 代理

```bash
# 查 Windows 系统代理设置
powershell.exe -Command \
  "Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings' | \
   Select-Object ProxyServer, ProxyEnable"

# 查哪个进程占了 7890 端口
powershell.exe -Command \
  "Get-Process -Id (Get-NetTCPConnection -LocalPort 7890 -ErrorAction SilentlyContinue).OwningProcess | \
   Select-Object ProcessName, Id"

# 常见代理端口
for port in 7890 7891 10808 10809 8080 8123 9090; do
    powershell.exe -Command "netstat -an | findstr ':$port '" 2>/dev/null | head -1
done
```

**典型结果**：`CordCCore`（Clash Verge Rev 核心进程）占用 `0.0.0.0:7890`

### 第二步：确认 WSL → Windows 网络可达

```bash
# 获取 Windows 宿主 IP（默认网关）
WIN_IP=$(ip route show default | awk '{print $3}')
echo "Windows 宿主 IP: $WIN_IP"

# 测试端口开放
timeout 3 bash -c "echo > /dev/tcp/${WIN_IP}/7890" 2>/dev/null && echo "端口开放" || echo "不通"

# 测试 HTTP 代理连通性
curl -s --max-time 5 -x "http://${WIN_IP}:7890" https://www.google.com -o /dev/null -w "Google: %{http_code}\n"
curl -s --max-time 5 -x "http://${WIN_IP}:7890" https://www.baidu.com -o /dev/null -w "Baidu: %{http_code}\n"
```

⚠️ 如果 HTTP 通但 SOCKS5 不通 → 正常。Clash 的 mixed port 优先走 HTTP。

**如果端口连不上** → Windows Clash 没有开启「允许局域网连接」，去 Clash Verge Rev 设置里勾上。

### 第三步：配置代理脚本（`~/.hermes/proxy.sh`）

```bash
# 文件: ~/.hermes/proxy.sh
#!/bin/bash
# WSL 代理配置 — 自动检测 Windows 宿主 IP

export WIN_IP=$(ip route show default | awk '{print $3}')
export HTTP_PROXY="http://${WIN_IP}:7890"
export HTTPS_PROXY="http://${WIN_IP}:7890"
export http_proxy="http://${WIN_IP}:7890"
export https_proxy="http://${WIN_IP}:7890"
export NO_PROXY="localhost,127.0.0.1,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,*.local,*.lan"
export no_proxy="localhost,127.0.0.1,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,*.local,*.lan"

echo "[proxy] WIN_IP=$WIN_IP:7890 (HTTP/HTTPS)"
```

### 第四步：追加到 `~/.bashrc`

```bash
# 写入 .bashrc
echo '' >> ~/.bashrc
echo '# ===== WSL 代理配置 =====' >> ~/.bashrc
echo 'if [ -f ~/.hermes/proxy.sh ]; then' >> ~/.bashrc
echo '    source ~/.hermes/proxy.sh' >> ~/.bashrc
echo 'fi' >> ~/.bashrc
echo '# ===== 代理配置结束 =====' >> ~/.bashrc
```

### 第五步：Git 代理

```bash
git config --global http.proxy "http://172.23.96.1:7890"
git config --global https.proxy "http://172.23.96.1:7890"
```

⚠️ **Git 代理的 IP 不自动检测**——因为 `git config --global` 存的是静态值。如果 Clash 端口变化或切换网络需要手动改。

### 第六步：验证全链路

```bash
# 立即生效
source ~/.hermes/proxy.sh

# 验证环境变量
echo "HTTP_PROXY=$HTTP_PROXY"
echo "HTTPS_PROXY=$HTTPS_PROXY"

# 验证网络
curl -s --max-time 5 https://www.google.com -o /dev/null -w "Google: HTTP %{http_code}\n"
curl -s --max-time 5 https://www.baidu.com -o /dev/null -w "Baidu: HTTP %{http_code}\n"
curl -s --max-time 5 https://pypi.org -o /dev/null -w "PyPI: HTTP %{http_code}\n"

# 验证 pip
pip install --dry-run requests 2>&1 | tail -3

# 验证工具（Codex 等）
codex doctor 2>&1 | grep -E "(proxy|connectivity)" | head -5
```

---

## 典型问题排查

### 问题 1：Codex 报 "Model metadata not found"

**现象**：Codex 启动时显示：
```
Model metadata for `deepseek-chat` not found. Defaulting to fallback metadata...
```

**根因**：Codex 启动时需要联网获取模型元数据（上下文窗口、工具支持等信息）。WSL 没配代理时出不去。

**修复**：按上述标准流程配好代理后重启 Codex。代理让 Codex 能联网拉取元数据。

**备选方案**（如果代理也不通）：配置 `model_catalog_json` 绕开联网检测：
```toml
# config.toml
model_catalog_json = "/home/dmin/.codex/model_catalog.json"
```
然后创建模型元数据文件（格式见 Codex CLI 文档）。

### 问题 2：WSL 网络正常但代理端口连不上

**可能原因**：
- Clash 没开「允许局域网连接」
- Clash 绑定到了 `127.0.0.1` 而不是 `0.0.0.0`
- Windows 防火墙拦了

**检查**：
```powershell
# Windows 上查监听地址
netstat -ano | findstr :7890
# 应该显示 0.0.0.0:7890 而不是 127.0.0.1:7890
```

### 问题 3：`codex doctor` 报 "reachability ... 404"

**现象**：`codex doctor` 显示：
```
✗ reachability provider base URL route returned 404
    deepseek API base URL http://127.0.0.1:11435/v1 reachable (HTTP 404)
```

**根因**：Codex 的 reachability 探测会向 `base_url` 发一个特定的 probe 请求。如果你的 `base_url` 指向本地中转代理（如 `127.0.0.1:11435`），这个中转只转发标准 chat/completions 请求，不处理 Codex 的 probe，返回 404。

**影响**：这只是 doctor 检查的"不完美"，不影响实际使用。Codex 仍然能正常调用 API 完成代码任务。