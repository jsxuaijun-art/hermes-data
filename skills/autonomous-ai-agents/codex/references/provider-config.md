# codex-bridge Provider Configuration Reference

> 第三方聚合平台 + 自定义 endpoint 配置档案。
> 适用于 API key 不走官方 DeepSeek/Mimo，而是通过兼容层转发的情况。

## 当前配置（2026.6.5）

| Key | Value |
|-----|-------|
| API Key | `sk-ag-4fe1e7d229cd3bd5ced354c8e5397e3a`（阿里云百炼格式，走第三方） |
| DeepSeek Base URL | `https://llm.chudian.site/v1` |
| 桥端口 | localhost:4000 |
| 暴露模型 | deepseek-v4-pro, deepseek-v4-flash, deepseek-chat, mimo-v2.5-pro |

## .env 文件结构

```env
# ~/codex-bridge/.env
PROXY_AUTH_KEY="Ac0oiONbbZRIpmW3HqrJm8tI5M_jr1fI"
DEEPSEEK_API_KEY="sk-ag-4fe1e7d229cd3bd5ced354c8e5397e3a"
DEEPSEEK_BASE_URL="https://llm.chudian.site/v1"
MIMO_API_KEY="sk-ag-4fe1e7d229cd3bd5ced354c8e5397e3a"
PROXY_PORT=4000
DEEPSEEK_MODELS="deepseek-v4-pro,deepseek-v4-flash,deepseek-chat"
MIMO_MODELS="mimo-v2.5-pro"
```

## 坑：`source .env` + `nohup` 环境变量丢失

### 问题

```bash
# ❌ 这种写法在 nohup 子进程中会丢变量
set -a
source .env
set +a
nohup node proxy.mjs &
# → 子进程读不到 DEEPSEEK_BASE_URL
```

根源：`set -a` 标记后续赋值的变量为 export，但 `source .env` 中如果出现空行或特殊字符可能导致部分变量无法导出。`nohup` 子进程继承的是 export 过的变量，漏掉一个就寄。

### 修复

```bash
# ✅ 逐行读取 + 显式 export，兼容性最好
while IFS='=' read -r key val || [ -n "$key" ]; do
    case "$key" in
        ''|#*) continue ;;
    esac
    val="${val%\"}"
    val="${val#\"}"
    export "$key=$val"
done < .env
```

详见 `~/codex-bridge/start.sh`（已用此模式）。

## 验证

```bash
# 1) 检查桥端点和模型
curl -H "Authorization: Bearer $CODEX_PROXY_KEY" localhost:4000/v1/models

# 2) 真实对话测试
curl -X POST localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer $CODEX_PROXY_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-v4-flash","messages":[{"role":"user","content":"你好"}],"stream":false}'

# 期望: {"choices":[{"message":{"content":"你好！😊"}}]}
```

## 模型列表（chudian.site 实际可用）

| 模型 | 类别 |
|------|------|
| deepseek-v3.2 | 对话 |
| deepseek-v4-flash | 对话 |
| deepseek-v4-pro | 对话 |
| doubao-seed-2.0-code | 代码 |
| doubao-seed-2.0-lite | 对话 |
| doubao-seed-2.0-pro | 对话 |
| glm-4.7 | 对话 |
| glm-5 | 对话 |
| glm-5.1 | 对话 |
| kimi-k2.5 | 对话 |
| kimi-k2.6 | 对话 |
| mimo-v2.5 | 对话 |
| mimo-v2.5-pro | 对话 |
| minimax-m2.5 | 对话 |
| minimax-m2.7 | 对话 |
| minimax-m2.7-highspeed | 快 |
| minimax-m3 | 对话 |
| qwen3.5-plus | 对话 |
| qwen3.6-plus | 对话 |