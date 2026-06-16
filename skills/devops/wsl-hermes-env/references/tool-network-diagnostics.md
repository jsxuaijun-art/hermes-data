# WSL 工具外网连通性诊断手册

> 场景：Codex/Claude Code/Hermes 等 CLI 工具在 WSL 中报"DNS 封锁""网络不可达""模型元数据 fallback"等错误
> 关键规则：**WSL 的 DNS/网络问题和 Windows 宿主机的网络状态可能不同**

---

## 第一步：判断真实网络状态（不要信工具的报错）

工具的错误信息（如 Codex 报"DNS resolution failed"）可能是误导，需要手工验证：

```bash
# 1. 基本连通性测试
ping -c 2 8.8.8.8          # IP直达——通则网络层没被封锁
ping -c 2 baidu.com        # DNS+IP——通则DNS也没问题

# 2. HTTP可达性测试（区分网络封锁和认证拒绝）
curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 https://api.deepseek.com/v1
# 200=通, 401=通了但没认证(正常), 000=完全不通(被墙/代理问题)

# 3. 查看当前 DNS 配置
cat /etc/resolv.conf
# WSL2 默认 nameserver 10.255.255.254（NAT转发到Windows DNS）

# 4. 测试关键域名
for host in api.deepseek.com api.openai.com registry.npmjs.org github.com; do
    echo -n "$host → "
    curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 https://$host 2>&1
    echo ""
done
```

## 第二步：常见误判场景

### 场景A：Codex 报"DNS 封锁"但实际能上网

**根因排查**：Codex 启动时做多维度 reachability 检测，会同时探测：
1. 配置的 `model_providers.*.base_url`（如 `http://127.0.0.1:11435/v1`）
2. OpenAI 的 api.openai.com（即使没用 OpenAI，也会探测）

**如果 base_url 指向的本地代理返回 404** + **api.openai.com 被墙**，Codex 会输出"DNS 封锁"提示。但实际上你的 deepseek 可能是通的。

**修复优先级**：
1. 先查 base_url 指向的服务是否正常工作（本地代理/中转/直连）
2. 再查 api.openai.com 是否影响核心功能（通常不影响，只影响模型元数据探测）

### 场景B：curl 超时但 ping 能通

**现象**：ping 8.8.8.8 / baidu.com 正常，但 curl 到 api.openai.com 返回 000

**原因**：这是应用层封锁（TCP/HTTPS 阻断），不是 IP 层封锁。DNS 解析正常、ICMP 正常，但特定域的 HTTPS 被中断。

**对策**：这是中国网络环境对特定境外服务的常见封锁模式，无法在 WSL 本地解决。要么走代理，要么换用国内可达的 API 端点。

### 场景C: npm git 协议超时（Codex update 卡死）

**根因**：GitHub 的 HTTPS 数据传输在 WSL 下可能极慢（<100Kbps），而 SSH 反而快。

**修复**：将 git remote 从 HTTPS 改为 SSH：
```bash
git remote set-url origin git@github.com:jsxuaijun-art/hermes-data.git
```
完成后 `git push origin main` 应能从 300s 降到 60s 内。

## 第三步：多工具快速诊断脚本

```bash
#!/bin/bash
echo "=== 网络状态诊断 ==="
echo "DNS: $(grep nameserver /etc/resolv.conf | head -1)"
echo "IP连通: $(ping -c 1 -W 3 8.8.8.8 2>&1 | grep -o '1 received' || echo '不通')"
echo "--- HTTP可达性 ---"
for url in \
    "https://api.deepseek.com/v1|DeepSeek" \
    "https://api.openai.com/v1|OpenAI" \
    "http://127.0.0.1:11435/v1|本地代理" \
    "https://registry.npmjs.org/|npm"; do
    target="${url%%|*}"
    label="${url##*|}"
    code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "$target" 2>/dev/null)
    echo "  $label → $code ($target)"
done
echo "--- WSL身份 ---"
grep -qi microsoft /proc/version && echo "WSL环境" || echo "非WSL"
echo "--- 环境变量检查 ---"
env | grep -E '(proxy|PROXY|API_KEY)' | head -5 || echo "(无代理/API_KEY环境变量)"
```

## 第四步：针对性修复

| 诊断结果 | 修复方案 |
|---------|---------|
| api.deepseek.com 通（401），本地代理 404 | 修复/重建本地代理中转服务，或直连 api.deepseek.com 并去掉 base_url 中转 |
| api.openai.com 不通（000） | 不影响 deepseek 使用。如需要 OpenAI：用 Clash 代理或换可达的 API |
| 所有 HTTPS 都 000 | 网络可能完全被阻断。检查 Windows 端网络，或重启 WSL: `wsl --shutdown` |
| ping 通但 curl 超时 | 特定域被封，不影响 deepseek/阿里云等国内可达服务 |
| curl 通但 Codex 报 DNS 封锁 | 确认 model provider 的 base_url 配置正确，代理 404 才是真问题 |

## 第五步：彻底验证

```bash
# 验证配置的 provider 是否真正可用
curl -s -w "\nHTTP:%{http_code}" https://api.deepseek.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $(echo $DEEPSEEK_API_KEY)" \
  -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"ping"}],"max_tokens":1}'
# 期望输出: {"choices":[{"finish_reason":"length",...}]} HTTP:200
```
