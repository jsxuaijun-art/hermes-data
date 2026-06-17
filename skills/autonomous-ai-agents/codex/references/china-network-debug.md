# Codex 中国网络环境调试参考

> **场景：** 在中国大陆运行 Codex，使用非 OpenAI 底座（如 DeepSeek）
> **核心问题：** `api.openai.com` 被 GFW 阻断，Codex 内置 reachability 探测会报 DNS 封锁/超时
> **创建时间：** 2026.6.6

---

## 一、症状分类

| 症状 | Codex 输出 | 根因 |
|------|-----------|------|
| DNS封锁 | `Model metadata for X not found. Defaulting to fallback metadata` + 超时 | OpenAI 被墙，Codex 拿不到默认模型元数据 |
| 连接失败 | `provider base URL route returned 404` | 本地代理桥梁（如 `127.0.0.1:11435`）未正确实现 OpenAI Responses API |
| 更新检查超时 | `curl: (28) Operation timed out after 5000 milliseconds` | 同样是被墙，在检查最新版本 |

**关键判断：** "DNS 被封锁"这个错误信息可能**误导**。Codex 的 reachability 检测机制是：
1. 先连 `model_providers.X.base_url`（你配置的地址）
2. 再连 OpenAI API（硬编码，用于验证）

在中国网络下，第 2 步永远失败。**不能据此判断 WSL 全局网络不通。**

---

## 二、分层诊断流程

### 第 1 层：WSL 全局网络

```bash
# 检查 DNS 解析
cat /etc/resolv.conf
# 正常 WSL2 下应该是 nameserver 10.255.255.254（NAT 转发）

# 验证外网可达性
ping -c 2 8.8.8.8                    # ICMP 直连
ping -c 2 baidu.com                   # DNS 解析+ICMP
curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 https://api.deepseek.com/v1
curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 https://registry.npmjs.org
curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 https://api.openai.com/v1
```

**预期结果（中国网络）：**
- ✅ `api.deepseek.com` — **401**（通了，缺 key 认证）
- ✅ `registry.npmjs.org` — **200**
- ❌ `api.openai.com` — **000**（超时/被阻断）

### 第 2 层：本地代理桥梁

如果 `codex doctor` 报 `404`，说明代理桥梁没跑通：

```bash
# 测试代理桥梁是否启动
curl -s http://127.0.0.1:11435/v1 -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"hi"}]}'
# 预期：返回 404 表示代理没实现这个端点
# 预期：返回 200+JSON 表示代理正常

# 检查端口监听
ss -tlnp | grep 11435
```

### 第 3 层：Codex 配置

```bash
# 完整诊断
codex doctor

# 重点关注：
# 1. model_providers.deepseek.base_url — 是否指向正确的代理地址
# 2. reachability — 是否报 404
# 3. auth — DEEPSEEK_API_KEY 是否存在
# 4. updates — 更新检查超时（不影响使用）
```

---

## 三、常见问题及解决

### 3.1 「DNS 被封锁」但 WSL 实际能上网

**现象：**
- `codex doctor` 报网络问题
- 但 `curl api.deepseek.com` 能通

**结论：** 这是 false alarm。Codex 硬编码了 OpenAI 的 reachability 检测，在中国必败。
**处理：** 忽略此警告。不影响使用。

### 3.2 代理桥梁返回 404

**现象：**
```
deepseek API base URL    http://127.0.0.1:11435/v1 reachable (HTTP 404)
```

**根因：** 本地代理（如 ccswitch-deepseek）要么没启动，要么没实现 Responses API 端点。
**处理：** 检查代理进程是否运行。如果代理是单独的服务，需要先启动它再运行 Codex。

### 3.3 模型元数据警告

**现象：**
```
Model metadata for `deepseek-chat` not found. Defaulting to fallback metadata
```

**解决：** 创建 `model_catalog.json` 并配置到 `config.toml` 的 `model_catalog_json` 字段。
详见 reference 文件 `references/custom-model-catalog.md`。

### 3.4 Codex 更新检查超时

**现象：**
```
latest version probe     curl: (28) Operation timed out
```

**根因：** Codex 启动时默认检查更新，但 `update.openai.com` 被墙。
**解决：** 在 `config.toml` 中关闭：

```toml
# 关闭启动时更新检查
startup_update_check = false
```

---

## 四、config.toml 中国环境推荐配置

```toml
model = "deepseek-chat"
model_provider = "deepseek"

approval_policy = "on-request"
sandbox_mode = "workspace-write"
web_search = "disabled"

# 关闭更新检查（在中国网络下节省启动时间）
startup_update_check = false

# 自定义模型元数据（消除 fallback 警告）
model_catalog_json = "/home/dmin/.codex/model_catalog.json"

[model_providers.deepseek]
name = "DeepSeek"
base_url = "http://127.0.0.1:11435/v1"   # 本地代理地址
env_key = "DEEPSEEK_API_KEY"
wire_api = "responses"
requires_openai_auth = false
stream_idle_timeout_ms = 300000
```

---

## 五、快速验证清单

```bash
# 一键验证网络
echo "=== DNS ===" && cat /etc/resolv.conf | grep nameserver
echo "=== ICMP ===" && ping -c 1 8.8.8.8 -W 2 | grep -c "64 bytes"
echo "=== DeepSeek API ===" && curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 https://api.deepseek.com/v1
echo "=== OpenAI API ===" && curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 https://api.openai.com/v1
echo "=== npm ===" && curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 https://registry.npmjs.org
echo "=== 本地代理 ===" && curl -s -o /dev/null -w "%{http_code}" --connect-timeout 2 http://127.0.0.1:11435/v1
echo "=== Codex Doctor ===" && codex doctor --summary 2>&1 | head -3
```