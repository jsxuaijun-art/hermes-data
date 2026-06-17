---
name: codex
description: Delegate coding tasks to OpenAI Codex CLI agent — includes codex-bridge setup for custom providers (DeepSeek, Mimo, etc.). Use for building features, refactoring, PR reviews, and batch issue fixing. Requires the codex CLI and a git repository.
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Coding-Agent, Codex, OpenAI, Code-Review, Refactoring]
    related_skills: [claude-code, hermes-agent]
---

# Codex CLI

Delegate coding tasks to [Codex](https://github.com/openai/codex) via the Hermes terminal. Codex is OpenAI's autonomous coding agent CLI.

## When to use

- Building features
- Refactoring
- PR reviews
- Batch issue fixing

Requires the codex CLI and a git repository.

## Prerequisites

- Codex installed: `npm install -g @openai/codex`
- OpenAI API key configured (or **codex-bridge** for custom providers — see below)
- **Must run inside a git repository** — Codex refuses to run outside one
- Use `pty=true` in terminal calls — Codex is an interactive terminal app

## Custom Provider Setup (codex-bridge)

Codex natively only talks to OpenAI. To connect it to **DeepSeek**, **Mimo**, or any OpenAI-compatible API, run a local proxy bridge:

### 1. Install codex-bridge

```bash
git clone https://github.com/anthropics/codex-bridge.git ~/codex-bridge
cd ~/codex-bridge && npm install
```

### 2. Configure the bridge

Create `~/codex-bridge/.env` with your provider keys:

```env
PROVIDER_URL=https://api.deepseek.com/beta
PROXY_AUTH_KEY=<generate-a-random-token>   # used for auth between Codex ↔ bridge
CODEX_API_KEY=<anything-placeholder-if-not-needed>
```

For custom providers (e.g. hosted OpenRouter-style endpoints), set `PROVIDER_URL` to your endpoint.

### 3. Set the auth key as env var

```bash
echo 'export CODEX_PROXY_KEY=<same-token-as-PROXY_AUTH_KEY>' >> ~/.bashrc
source ~/.bashrc
```

This must match `PROXY_AUTH_KEY` in the bridge `.env` — it's how Codex authenticates to the bridge.

### 4. Start the bridge

```bash
cd ~/codex-bridge
node proxy.mjs &
# Verify: curl -s localhost:4000/v1/models | head
```

Bridge serves on `localhost:4000` by default. Verify with:

```bash
curl -H "Authorization: Bearer $CODEX_PROXY_KEY" http://localhost:4000/v1/models
# Expect: {"object":"list","data":[{"id":"deepseek-chat",...}]}
```

### 5. Configure Codex to use the bridge

Create `~/.config/codex/config.toml`:

```toml
[[models]]
model = "deepseek-v4-flash"
provider = "openai"
baseURL = "http://localhost:4000/v1"

[[models]]
model = "deepseek-v4-pro"
provider = "openai"
baseURL = "http://localhost:4000/v1"

[[models]]
model = "deepseek-chat"
provider = "openai"
baseURL = "http://localhost:4000/v1"
```

Now `codex exec` will route through the bridge to your custom provider.

### Model Metadata Warning

Codex only ships built-in metadata for **official OpenAI models** (o3, gpt-4o, etc.). Custom models like `deepseek-v4-flash` will display:

```
Model metadata for `deepseek-v4-flash` not found. Defaulting to fallback metadata; this can degrade performance and cause issues.
```

**This is cosmetic** — Codex uses auto-detected fallback parameters. The model runs normally with no functional degradation. There is no way to suppress it without a Codex source code patch.

## Proxy Bridges (Non-OpenAI Models) — Protocol Details

When Codex connects through a proxy bridge (e.g. `ccswitch-deepseek`) to use non-OpenAI models like DeepSeek, two wire protocols interact:

- **Codex → proxy**: OpenAI `responses` API format (event-streamed)
- **proxy → provider**: `chat/completions` format

Known protocol mismatches (see `references/proxy-protocol-mismatches.md` for full details):

### 1. Missing assistant message before tool_calls (non-stream)

If DeepSeek returns `400: insufficient tool messages following tool_calls message`, the proxy's `buildNonStreamResponse` is likely emitting `function_call` items **without** a preceding `message` item. Codex needs both — fix: emit `{type: "message", role: "assistant"}` before any `function_call` items.

### 2. tool_choice format

Codex sends `{"type": "auto"}` but DeepSeek expects `"auto"` (string). Same for `"required"` and `"none"`. The proxy must translate the object form to strings.

### 3. role: "user" with tool_call_id (multi-turn crash)

Codex sends tool results as `{"role": "user", "tool_call_id": "..."}` (responses API format), but DeepSeek's chat/completions API requires `{"role": "tool", "tool_call_id": "..."}`. The proxy must detect this and rewrite the role. This only manifests on the **second turn** of a tool-use conversation — the first turn works fine, then subsequent multi-turn prompts fail with the same 400 as bug #1.

Start with **non-streaming** requests to verify JSON structure, then test streaming:

```bash
# Non-stream: verify output shape
curl -s http://127.0.0.1:11435/v1/responses -d '{"stream":false,...}'
# Expected: output[0] = message, output[1+] = function_call(s)

# Stream: check event types
curl -s -N http://127.0.0.1:11435/v1/responses -d '{"stream":true,...}' | grep -o '"type":"[^"]*"'
```

## Configuration

### Custom Model Registry (non-OpenAI providers)

When using a non-OpenAI model (e.g. `deepseek-chat`), Codex shows:
```
Model metadata for `deepseek-chat` not found. Defaulting to fallback metadata
```
This means Codex lacks the model's context window, truncation policy, and other parameters. **Fix: create a model catalog JSON and point config.toml to it.**

**Step 1 — Create `~/.codex/model_catalog.json`:**

```json
{
  "models": [
    {
      "slug": "deepseek-chat",
      "display_name": "DeepSeek Chat",
      "description": "DeepSeek V3 chat model",
      "default_reasoning_level": "medium",
      "supported_reasoning_levels": [
        {"effort": "low", "description": "Fast responses"},
        {"effort": "medium", "description": "Balanced speed and depth"},
        {"effort": "high", "description": "Deeper reasoning"}
      ],
      "shell_type": "shell_command",
      "visibility": "list",
      "supported_in_api": true,
      "priority": 10,
      "additional_speed_tiers": [],
      "service_tiers": [],
      "base_instructions": "",
      "supports_reasoning_summaries": false,
      "default_reasoning_summary": "none",
      "support_verbosity": false,
      "default_verbosity": "low",
      "apply_patch_tool_type": "freeform",
      "web_search_tool_type": "text_and_image",
      "truncation_policy": {"mode": "tokens", "limit": 8000},
      "supports_parallel_tool_calls": true,
      "supports_image_detail_original": false,
      "context_window": 65536,
      "max_context_window": 65536,
      "effective_context_window_percent": 90,
      "experimental_supported_tools": [],
      "input_modalities": ["text"],
      "supports_search_tool": false
    }
  ]
}
```
Keys `base_instructions` and all listed fields are **required** by Codex v0.134.0 — omitting them or setting `null` causes `failed to parse model_catalog_json`.

**Step 2 — Add to `~/.codex/config.toml`:**

```toml
model_catalog_json = "/home/dmin/.codex/model_catalog.json"
```

**Step 3 — Verify:**
```bash
codex debug models  # Should show your model in the list
codex doctor         # Config should show ✓ loaded
```

**Pitfalls:**
- Codex parses this JSON strictly. Missing fields (even optional-looking ones like `base_instructions`) cause parse failure.
- `null` values are not accepted for string fields — use `""` instead.
- The `--strict-config` flag is useful for debugging: `codex --strict-config -m deepseek-chat`
- If `codex debug models` outputs nothing, check stderr — the output goes to stdout but the file might be empty if parsing failed.

## One-Shot Tasks

```
terminal(command="codex exec 'Add dark mode toggle to settings'", workdir="~/project", pty=true)
```

For scratch work (Codex needs a git repo):
```
terminal(command="cd $(mktemp -d) && git init && codex exec 'Build a snake game in Python'", pty=true)
```

## Background Mode (Long Tasks)

```
# Start in background with PTY
terminal(command="codex exec --full-auto 'Refactor the auth module'", workdir="~/project", background=true, pty=true)
# Returns session_id

# Monitor progress
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# Send input if Codex asks a question
process(action="submit", session_id="<id>", data="yes")

# Kill if needed
process(action="kill", session_id="<id>")
```

## Key Flags

| Flag | Effect |
|------|--------|
| `exec "prompt"` | One-shot execution, exits when done |
| `--full-auto` | Sandboxed but auto-approves file changes in workspace |
| `--yolo` | No sandbox, no approvals (fastest, most dangerous) |

## PR Reviews

Clone to a temp directory for safe review:

```
terminal(command="REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && gh pr checkout 42 && codex review --base origin/main", pty=true)
```

## Parallel Issue Fixing with Worktrees

```
# Create worktrees
terminal(command="git worktree add -b fix/issue-78 /tmp/issue-78 main", workdir="~/project")
terminal(command="git worktree add -b fix/issue-99 /tmp/issue-99 main", workdir="~/project")

# Launch Codex in each
terminal(command="codex --yolo exec 'Fix issue #78: <description>. Commit when done.'", workdir="/tmp/issue-78", background=true, pty=true)
terminal(command="codex --yolo exec 'Fix issue #99: <description>. Commit when done.'", workdir="/tmp/issue-99", background=true, pty=true)

# Monitor
process(action="list")

# After completion, push and create PRs
terminal(command="cd /tmp/issue-78 && git push -u origin fix/issue-78")
terminal(command="gh pr create --repo user/repo --head fix/issue-78 --title 'fix: ...' --body '...'")

# Cleanup
terminal(command="git worktree remove /tmp/issue-78", workdir="~/project")
```

## Batch PR Reviews

```
# Fetch all PR refs
terminal(command="git fetch origin '+refs/pull/*/head:refs/remotes/origin/pr/*'", workdir="~/project")

# Review multiple PRs in parallel
terminal(command="codex exec 'Review PR #86. git diff origin/main...origin/pr/86'", workdir="~/project", background=true, pty=true)
terminal(command="codex exec 'Review PR #87. git diff origin/main...origin/pr/87'", workdir="~/project", background=true, pty=true)

# Post results
terminal(command="gh pr comment 86 --body '<review>'", workdir="~/project")
```

## WSL 重启后修复（2026.6.5）

重启后 Codex 报错 `401 Unauthorized` 或 `Missing CODEX_PROXY_KEY`，原因为：
1. **桥服务（proxy.mjs）不会随 WSL 自动重启**
2. **CODEX_PROXY_KEY 环境变量未持久化**

修复内容已写入 `~/.bashrc` 和 `~/codex-bridge/start.sh`：

```bash
# 打开任意 WSL 终端即可自动完成：
# 1）设置 CODEX_PROXY_KEY 环境变量
# 2）start.sh → 从 .env 读取 DEEPSEEK_BASE_URL / API Key → 启动桥
# 3）PID 记录在 /tmp/codex-bridge.pid，日志在 /tmp/codex-bridge.log
```

**关键配置：**
- `DEEPSEEK_BASE_URL=https://llm.chudian.site/v1`（第三方聚合平台，非官方 DeepSeek API）
- `DEEPSEEK_API_KEY=sk-ag-...`（阿里云百炼格式 key，走第三方兼容层）
- 如果 endpoint 变只改 `.env` 的 `DEEPSEEK_BASE_URL` 即可

手动测试：
```bash
curl -H "Authorization: Bearer $CODEX_PROXY_KEY" http://localhost:4000/v1/models
# → 返回模型列表即正常
```

## Pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| `Missing environment variable: CODEX_PROXY_KEY` | Bridge configured but env var not set | `echo 'export CODEX_PROXY_KEY=...' >> ~/.bashrc && source ~/.bashrc` |
| Bridge returns 401 on curl test | curl didn't send auth header | Add `-H "Authorization: Bearer $CODEX_PROXY_KEY"` |
| 重启后 Codex 报 401/auth 错误 | 桥服务未自动启动 + CODEX_PROXY_KEY 未加载 | 修复已在 ~/.bashrc 和 start.sh 中做好，开新终端即可。检查: `curl -H "Authorization: Bearer $CODEX_PROXY_KEY" localhost:4000/v1/models` |
| Codex hangs with no output | Missing `pty=true` | Codex is an interactive TUI — must use `pty=true` in terminal() |
| `Model metadata not found` | Custom provider, not OpenAI official | Cosmetic only — ignore, no functional impact |
| Bridge process died | Terminal session ended, `&` background got killed | Start with `nohup node proxy.mjs &` or Hermes `terminal(background=true)` |

## Rules

1. **Always use `pty=true`** — Codex is an interactive terminal app and hangs without a PTY
2. **Git repo required** — Codex won't run outside a git directory. Use `mktemp -d && git init` for scratch
3. **Use `exec` for one-shots** — `codex exec "prompt"` runs and exits cleanly
4. **`--full-auto` for building** — auto-approves changes within the sandbox
5. **Background for long tasks** — use `background=true` and monitor with `process` tool
6. **Don't interfere** — monitor with `poll`/`log`, be patient with long-running tasks
7. **Parallel is fine** — run multiple Codex processes at once for batch work

## China Network Considerations

When running Codex from mainland China with a non-OpenAI provider (e.g. DeepSeek):

- `api.openai.com` is blocked by the GFW — Codex's built-in reachability check will always fail against OpenAI, producing false "DNS blocked" warnings
- Use `startup_update_check = false` in `config.toml` to avoid update-probe timeouts
- Run `codex doctor` and inspect the `reachability` line — a 404 on your proxy bridge is a **real problem**; a timeout on OpenAI is **expected**
- The false "DNS blocked" message does **not** mean WSL itself can't reach the internet — verify separately with `curl` to `api.deepseek.com` and `registry.npmjs.org`

See `references/china-network-debug.md` for a complete layered diagnosis workflow, config recommendations, and a one-liner verification checklist.
