# Claude Code + DeepSeek V4 Flash 代理方案（已完整验证）

这是 WSL 环境下通过 anthropic-proxy 翻译层让 Claude Code 使用 DeepSeek V4 Flash 模型的完整方案。已在用户环境下完整部署验证。

## 架构

```
Claude Code (Anthropic Messages API)
    │ ANTHROPIC_BASE_URL=http://localhost:3000
    ▼
anthropic-proxy (端口3000)  ← 3个必要 patch 已打
    │ 翻译 Anthropic ↔ OpenAI
    ▼
DeepSeek API (OpenAI 格式) api.deepseek.com/v1/chat/completions
```

## 关键路径

- **代理脚本：** `/home/dmin/.local/bin/deepseek-proxy-daemon.sh` — `.bashrc` 自动启动
- **nvm 包装脚本：** `/home/dmin/.nvm/versions/node/v24.16.0/bin/claude` — 硬 SET 环境变量，防污染
- **原始二进制备份：** `/home/dmin/.nvm/versions/node/v24.16.0/bin/claude.real`
- **日志：** `/tmp/deepseek-proxy.log`

## 自动启动机制

`.bashrc` 中通过 `deepseek-proxy-daemon.sh` 自动启动代理：
- 检查 PID 文件 + 端口 3000（双重防重复）
- 未运行时：静默启动到后台
- 已在运行：不重复启动
- nohup 启动，关终端不杀死代理

## 代理的 3 个必要 Patch（anthropic-proxy index.js）

| # | 问题 | 修复 |
|---|------|------|
| 1 | 缺 `HEAD /` 路由 | 添加 fastify.head('/') 和 fastify.get('/') 返回 200 |
| 2 | Tool call 格式嵌套错误 | 改为标准 OpenAI tool_calls 格式：`id`, `type: 'function'`, `function: {name, arguments}` |
| 3 | Tool result 缺 `name` 字段 | 从之前 assistant 消息中搜索对应的 tool_use_id，获取 tool name 填入 |

**注意：** 重装 `@anthropic-ai/claude-code` 或 `npx anthropic-proxy` 后 patch 会丢失。

## 常见问题

### Windows 环境变量污染
WSL 终端启动时继承 Windows 系统环境变量 `ANTHROPIC_BASE_URL`（可能指向旧端口），覆盖包装脚本设置的值。修复：在 Windows 系统环境变量中删除 `ANTHROPIC_BASE_URL`。

### `which claude` 和 `type claude` 不一致
bash 缓存问题。nvm bin 包装脚本是唯一可靠方案——文件总在 PATH 头部的 nvm bin 目录中。

### 验证命令
```bash
curl -s --max-time 3 http://localhost:3000/           # 代理是否在线
type claude                                            # 实际执行路径
env | grep ANTHROPIC                                   # 环境变量检查
curl -s --max-time 5 http://localhost:3000/v1/messages \  # 完整功能测试
  -X POST -H "Content-Type: application/json" \
  -d '{"model":"test","max_tokens":5,"messages":[{"role":"user","content":"hi"}]}'
```

### 网络依赖速查
| 操作 | 联网？ | 国际？ |
|------|--------|--------|
| 启动代理 | 已缓存→不连 | - |
| 首次安装 Claude Code | 是 | 是 (GitHub/npm) |
| 使用 Claude Code CLI | 是→api.deepseek.com | 不（国内直连） |
| 执行命令/读写文件 | 不（纯本地） | - |

### 历史教训
- alias 方案在 SHLVL=2 的特定终端中失效（alias 和 nvm 函数未加载）
- **nvm bin 包装脚本不受 shell 启动流程影响，是最终稳定方案**
