---
name: claude-code-deepseek-proxy
description: 通过 anthropic-proxy 翻译层让 Claude Code 使用 DeepSeek V4 Flash 模型
---

# Claude Code + DeepSeek V4 Flash 代理方案（已完整验证）

## 架构

```
┌─────────────────────────────┐
│    nvm bin claude wrapper   │  ← 包装脚本（硬 SET 环境变量，防污染）
│ export ANTHROPIC_BASE_URL=:3000 │
│ export ANTHROPIC_API_KEY=placeholder │
└──────────┬──────────────────┘
           │ exec claude.real
           ▼
Claude Code (Anthropic Messages API)
           │ ANTHROPIC_BASE_URL=http://localhost:3000
           ▼
     anthropic-proxy (端口3000)         ← 3个 patch 已打
           │ 翻译 Anthropic ↔ OpenAI
           ▼
     DeepSeek API (OpenAI 格式)
     api.deepseek.com/v1/chat/completions
```

## 前提条件

- Node.js v18+（通过 nvm 安装，本机 v24.16.0）
- Claude Code 已全局安装：`npm install -g @anthropic-ai/claude-code`
- DeepSeek API key 存在 `~/.hermes/.env` 中

## ⚡ 起步（一步到位）

### 日常工作流

```bash
# 1. 打开 WSL 终端 → 代理自动启动（无需手动操作）
# 2. 直接敲 claude
claude -p "写一个 Hello World"
# 或进入交互模式
claude
```

**自动启动机制：** `.bashrc` 在终端打开时自动运行 `/home/dmin/.local/bin/deepseek-proxy-daemon.sh`，该脚本：
- 检查 PID 文件 + 端口 3000（双重防重复）
- 未运行时：静默启动到后台，日志写 `/tmp/deepseek-proxy.log`
- 已在运行：什么都不做（第二个终端不重复启动）
- 后台进程独立于终端生命周期（nohup 启动），关终端不会杀死代理

**验证代理在运行：**
```bash
curl -s --max-time 2 http://localhost:3000/  # 应返回 200
cat /tmp/deepseek-proxy.log | tail -3        # 查看最新日志
```

**手动启/停：**
```bash
# 启动（一般不手动，.bashrc 自动处理）
/home/dmin/start-deepseek-proxy.sh

# 停止
kill $(cat /tmp/deepseek-proxy.pid 2>/dev/null) 2>/dev/null
```

### 手动启动（备选方案，仅当自动启动失效时）

```bash
cd /home/dmin/.npm/_npx/7fa4a753cadbb396/node_modules/anthropic-proxy
source ~/.hermes/.env && \
ANTHROPIC_PROXY_BASE_URL=https://api.deepseek.com \
ANTHROPIC_PROXY_API_KEY="$DEEPSEEK_API_KEY" \
COMPLETION_MODEL=deepseek-chat \
REASONING_MODEL=deepseek-chat \
PORT=3000 \
node index.js
```

## 最终方案：nvm bin 内嵌包装脚本（最可靠）

**核心思想：** 不依赖 alias、不依赖 shell 函数、不依赖 PATH 顺序——直接在 nvm bin 目录里用一个包装脚本替换原始 `claude` 软链，确保每次敲 `claude` 都走代理，100% 不被任何环境因素绕过。

### 实现方式

```bash
# 原始：claude -> ../lib/node_modules/@anthropic-ai/claude-code/bin/claude.exe（软链）
# 改造后：
#   claude       → 包装脚本（设置环境变量，exec 原始二进制）
#   claude.real  → ../lib/node_modules/@anthropic-ai/claude-code/bin/claude.exe（原始软链备份）
```

关键文件路径：
- `/home/dmin/.nvm/versions/node/v24.16.0/bin/claude` — 包装脚本
- `/home/dmin/.nvm/versions/node/v24.16.0/bin/claude.real` — 原始二进制

### 包装脚本内容

```bash
#!/bin/bash
export ANTHROPIC_API_KEY=sk-placeholder
export ANTHROPIC_BASE_URL=http://localhost:3000
exec /home/dmin/.nvm/versions/node/v24.16.0/bin/claude.real "$@"
```

`export`（而不是命令前缀）是故意的——`exec` 不支持 `VAR=value exec cmd` 语法，必须先用 `export` 写进环境。

### 方案对比

| 方式                        | 可靠性             | 依赖                 | 优先级           |
|-----------------------------|--------------------|----------------------|------------------|
| ✅ **nvm bin 包装脚本**     | **100% 铁壳子**     | 无                   | PATH 第一优先    |
| ⚠️ alias                    | 终端特定           | .bashrc 被来源       | 交互 shell 中高  |
| ❌ wrapper 在 ~/.local/bin  | 取决于 PATH 顺序   | nvm 排前面时失效     | 中等             |
| ❌ shell 函数               | 受启动顺序影响     | 函数定义可能被覆盖   | 理论上最高       |

**历史教训：** alias 方案在 `bash -i` 测试中完美运行，但在用户的特定终端（SHLVL=2，原因不明）中 alias 和 nvm 函数都未加载——导致 `ANTHROPIC_BASE_URL` 直接读取了 Windows 继承的旧值（`:4000`），Claude Code 直连 Anthropic 服务器失败。**nvm bin 包装脚本不受 shell 启动流程影响，是目前最优解。**

## 代理的3个必要 Patch（已应用，记录备查）

antropric-proxy 的 `index.js` 有3个兼容性问题，已手动修复：

| # | 问题 | 症状 | 修复 |
|---|------|------|------|
| 1 | 缺 `HEAD /` 路由 | 交互模式报 "Failed to connect to api.anthropic.com" | 添加 fastify.head('/') 和 fastify.get('/') 返回 200 |
| 2 | Tool call 格式嵌套错误 | DeepSeek 返回 "missing field name" | 改为标准 OpenAI tool_calls 格式：`id`, `type: 'function'`, `function: {name, arguments: "..."}` |
| 3 | Tool result 缺 `name` 字段 | 同上错误（`messages[N]: missing field name`） | 从之前assistant消息中搜索对应的 tool_use_id，获取 tool name 填入 |

**⚠️ 注意：** 如果重装 `@anthropic-ai/claude-code` 或 `npx anthropic-proxy`，npx 缓存可能被重新下载导致 patch 丢失。此时需要重新打 patch。

## 日常启动检查清单

```bash
# 1. 代理是否在线？
curl -s --max-time 3 http://localhost:3000/  # 应返回 200

# 2. claude 实际执行的是哪个？
type claude  # 应显示二进制路径，如 "/home/dmin/.nvm/versions/node/v24.16.0/bin/claude"
             # 不应该显示 alias 或软链

# 3. 包装脚本是否生效？
which claude && claude -p "ping" 2>&1 | head -1
# 如果返回内容（而非"Unable to connect"），说明包装脚本正确覆盖了环境变量

# 4. 是否有 Windows 继承的环境变量污染？
env | grep ANTHROPIC  # 如果有且不是 http://localhost:3000，需要清理 Windows 系统变量
```

## 验证代理是否在线

```bash
curl -s --max-time 5 http://localhost:3000/v1/messages \
  -X POST -H "Content-Type: application/json" \
  -d '{"model":"test","max_tokens":5,"messages":[{"role":"user","content":"hi"}]}'
# 正常返回 → DeepSeek 回复，格式是 Anthropic Messages API
```

## 常见问题 FAQ

### Claude Code 和 Codex CLI 是同一个东西吗？

**不是。** 两者的核心区别：

| 维度 | Claude Code (Anthropic) | Codex CLI (OpenAI) |
|------|------------------------|-------------------|
| 开发商 | Anthropic | OpenAI |
| 原生模型 | Claude 系列（Sonnet/Opus/Haiku） | GPT-4o / o3 / o4-mini |
| API 格式 | Anthropic Messages API（专有格式） | OpenAI Chat API |
| 第三方模型 | 不支持（需翻译代理） | 不支持（需翻译代理） |
| 共性的功能 | 都是自主编码 CLI，可以读写文件、跑命令、管理 git、多轮对话 |

你的目标是 Claude Code（Anthropic 出品），不是 Codex CLI。两者没有冲突，可以同时存在。

### 忘加 ANTHROPIC_BASE_URL 或 Windows 环境变量污染

如果直接敲 `claude` 没加 `ANTHROPIC_BASE_URL=http://localhost:3000`，Claude Code 会尝试连 Anthropic 官方服务器：

```
Unable to connect to Anthropic services
Failed to connect to api.anthropic.com: ERR_BAD_REQUEST
Note: Claude Code might not be available in your country.
```

**这个错误是误导性的**——跟国家无关，只是因为没用代理。

**⚠️ 但更隐蔽的根因常常是：Windows 系统环境变量继承。**
即使你设置了 alias 或包装脚本，Windows 系统环境变量 `ANTHROPIC_BASE_URL` 会在 WSL 终端启动时被自动继承，覆盖包装脚本设置的值。

**典型案例（本次会话）：**
- 用户 WSL 中 `env | grep ANTHROPIC` 显示 `ANTHROPIC_BASE_URL=http://localhost:4000/v1`
- 这个值来自 Windows 系统环境变量（已废弃的旧代理端口）
- 虽然包装脚本 `export ANTHROPIC_BASE_URL=http://localhost:3000` 写在文件里，但如果脚本没有被触发（比如忘了重启终端），Windows 继承的值会生效
- 导致 Claude Code 连 `localhost:4000`（旧代理已关闭），报 `ERR_BAD_REQUEST`

**验证：**
```bash
env | grep ANTHROPIC_BASE_URL
# 正常应显示 http://localhost:3000（被包装脚本覆盖后）
# 如果显示其他值（如 :4000、:3001），说明 Windows 系统变量污染
```

**修复：** 在 Windows 系统环境变量中删除 `ANTHROPIC_BASE_URL`（需重启 WSL 终端）。

### 代理没启动就敲 claude

claude 会连 localhost:3000 失败，卡住或报 connection refused。先检查代理是否在运行。

### 缺 ANTHROPIC_API_KEY → "Not logged in"

即使走代理，Claude Code 仍然要求 `ANTHROPIC_API_KEY` 环境变量存在才能启动。代理不校验这个 key 的真实性，所以用假的占位符即可：

```bash
ANTHROPIC_API_KEY=sk-placeholder ANTHROPIC_BASE_URL=http://localhost:3000 claude
```

包装脚本里必须同时包含两个变量。只设 `ANTHROPIC_BASE_URL` 不设 `ANTHROPIC_API_KEY`，Claude Code 会报：
```
Not logged in · Please run /login
```
然后退出。这不是代理的问题，是 Claude Code 本身的认证检查。

### `which claude` 和 `type claude` 结果不一致

bash 会缓存命令路径。**`which claude` 只查 PATH，`type claude` 查 PATH + hash 缓存 + 函数/别名。** 两者结果不一致 → 说明有问题。

**常见场景：**
- `which claude` → `/home/dmin/.local/bin/claude`（包装脚本）
- `type claude` → `/home/dmin/.nvm/versions/node/v24.16.0/bin/claude`（nvm 原版）

**原因：** nvm 的 bin 目录在 PATH 中排在 `~/.local/bin` 前面。

**最佳修复：nvm-bin-wrapper** （将 nvm bin 目录下的 `claude` 软链替换为包装脚本）——文件总在 PATH 头部的 nvm bin 目录里，不需要依赖 PATH 顺序、alias 加载或 shell 函数。详见"最终方案"章节。

**次选修复：** 确保 PATH 添加放在 `.bashrc` 最后一行（在 nvm 初始化之后）：

```bash
# 正确：PATH 添加必须在 .bashrc 末尾
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

**快速诊断技巧：**
```bash
type claude           # 到底执行的是哪个？
which claude          # PATH 找到的是哪个？
hash -r && type claude  # 清缓存后再看
env | grep ANTHROPIC  # 环境变量是否有冲突（如 .venv-hermes 的 4000 端口）
```

### DeepSeek 不需要国际联网

DeepSeek 是国产服务，`api.deepseek.com` 国内直连。只有**首次安装** Claude Code 和 npx 拉包时才需要走代理访问 GitHub/npm。日常使用不需要挂梯子。

### Python 虚拟环境提示符

终端前面出现 `(.venv-hermes)` 是正常的 Python 虚拟环境提示，是 Hermes Agent 创建的环境。不影响 Claude Code 使用。

## 网络依赖速查

| 操作 | 联网？ | 国际？ |
|------|--------|--------|
| 启动代理 (npx) | 已缓存 → 不连 | - |
| 首次安装 Claude Code | 是 | 是 (GitHub/npm) |
| 打开 Claude Code CLI | 不 (本地加载) | - |
| 输入问题/写代码 | 是 → api.deepseek.com | 不 (国内直连) |
| 执行命令/读写文件 | 不 (纯本地) | - |
