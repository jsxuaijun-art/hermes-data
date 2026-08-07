# Git 连接诊断方法论（Git Connectivity Diagnostics）

**场景**: `git fetch/clone/push` 超时 / 断连 / 报 `fetch-pack: unexpected disconnect while reading sideband packet`

**适用于**: 从中国大陆访问 GitHub 时数据层被干扰的排查

---

## 诊断流程（按顺序）

### 第 1 层：确认 SSH 认证是否正常

```bash
ssh -T git@github.com
# 正常 → "Hi <user>! You've successfully authenticated..."
# 失败 → 密钥/权限问题（非网络层）
```

SSH 能连不代表 git 能传数据——认证和数据传输是两码事。

### 第 2 层：确认 DNS 和 TCP 连通

```bash
ping -c 3 github.com          # 看延迟和丢包
curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "https://github.com"
# 200 = TCP/HTTP层通，000 = 完全不可达
nslookup github.com           # 检查 DNS 解析
```

### 第 3 层：抓 Git 协议包（关键步骤）

```bash
# 注意：timeout 不支持前缀环境变量，需要用 export 分开写
export GIT_TRACE_PACKET=1
timeout 15 git ls-remote origin 2>&1
# 或
export GIT_TRACE_PACKET=1
timeout 15 git fetch origin main 2>&1
```

**关键信号解读**：

| 协议阶段 | 正常输出 | 失败输出 |
|---------|---------|---------|
| 版本协商 | `packet: fetch< version 2` | 无输出 → SSH 或 DNS 问题 |
| 引用列表 | `packet: fetch< refs/heads/main` | 无输出 → 认证问题 |
| **packfile 传输** | `packet: fetch< packfile` → `sideband< PACK ...` | **`unexpected disconnect while reading sideband packet`** |

**`unexpected disconnect while reading sideband packet`** = 手完成功、数据传输被拦截。这不是临时网络波动——是深度包检测（DPI）针对 Git 协议数据流的主动阻断。

### 第 4 层：测试替代传输通道

逐一测试，观察哪个能过 packfile 阶段：

```bash
# 测试 1: SSH 走 443 端口（GitHub 官方支持）
ssh -T -p 443 git@ssh.github.com
# 成功后再试 git fetch（绕开端口 22 的限制）
git remote set-url origin ssh://git@ssh.github.com:443/jsxuaijun-art/hermes-data.git
timeout 30 git fetch origin main

# 测试 2: 走 Windows git.exe（利用 Windows 网络栈）
"/mnt/c/Program Files/Git/bin/git.exe" fetch origin main

# 测试 3: 换各种镜像
urls=(
  "https://ghproxy.com/https://github.com/"
  "https://gitclone.com/github.com/"
  "https://hub.gitmirror.com/?q=https://github.com/"
)
for mirror in "${urls[@]}"; do
  url="${mirror}jsxuaijun-art/hermes-data.git"
  echo "Trying: $url"
  timeout 10 git ls-remote "$url" 2>&1 | head -2
done

# 测试 4: 直接 git:// 协议（偶尔不同端口策略）
git ls-remote git://github.com/jsxuaijun-art/hermes-data.git 2>&1
```

### 第 5 层：寻找本地代理/梯子

```bash
# 检查常见代理工具端口
for port in 7890 10809 1080 1087 1088 8118 8888 3128 8080; do
  result=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 2 http://127.0.0.1:$port 2>/dev/null)
  [ "$result" != "000" ] && echo "Port $port → HTTP $result"
done

# 检查 Windows 是否有代理工具
ls /mnt/c/Users/Admin/AppData/Local/clash* /mnt/c/Users/Admin/AppData/Roaming/clash* \
   /mnt/c/Users/Admin/AppData/Local/v2ray* /mnt/c/Users/Admin/AppData/Roaming/v2ray* \
   /mnt/c/Users/Admin/AppData/Local/Proxifier 2>/dev/null
```

## 失败模式速查表

| 症状 | 最可能根因 | 最终结论 |
|------|-----------|---------|
| SSH 握手 < 1s，git fetch 超时 | GFW 深度包检测 | **需要代理/梯子**，改端口/镜像不可能解决 |
| SSH 不通 | 防火墙出站规则（公司网） | 改 SSH 端口 443 或 HTTPS |
| HTTPS 通但 clone 慢 | 跨国带宽不足 | 用 Windows git.exe 或设代理 |
| curl 返回 `curl: (35) TCP connection reset` | 连接被 RST | 用代理 |
| `GnuTLS recv error (-110)` | TLS 连接中断 | 用 Windows git.exe |
| `Failed to connect to github.com port 443: Timed out` | DNS 或路由问题 | 检查 DNS / 切换备线 |

## 核心结论（来自实践）

- **SSH 认证成功 ≠ Git 数据传输成功**。认证通道和数据通道可能被不同策略对待。
- **三种传输方式都失败**（SSH 22、SSH 443、HTTPS）→ 几乎 100% 是协议层阻断，而非端口或 DNS 问题。
- **不能靠循环重试解决**: 如果 `GIT_TRACE_PACKET=1` 在 3 次测试中都停在 `sideband< PACK ...`，重试 100 次也没用。
- **最终方案是借助代理/梯子**（或使用阿里云等内地服务器的自动同步）。
- **Windows git.exe 利用 Windows 网络栈**，如果 Windows 上有系统代理（TUN 模式），走 Windows git.exe 通常能通。
