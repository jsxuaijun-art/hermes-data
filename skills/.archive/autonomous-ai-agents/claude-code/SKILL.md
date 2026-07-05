---
name: claude-code
description: "Delegate coding to Claude Code CLI (features, PRs)."
version: 2.3.0
author: Hermes Agent + Teknium
license: MIT
metadata:
  hermes:
    tags: [Coding-Agent, Claude, Anthropic, Code-Review, Refactoring, PTY, Automation]
    related_skills: [codex, hermes-agent, opencode]
---

# Claude Code — Hermes Orchestration Guide

**Support files:**
- `references/wsl-installation-recipe.md` — Proven WSL install steps, proxy setup, DeepSeek workaround notes (recorded 2026-05-22)

Delegate coding tasks to [Claude Code](https://code.claude.com/docs/en/cli-reference) (Anthropic's autonomous coding agent CLI) via the Hermes terminal. Claude Code v2.x can read files, write code, run shell commands, spawn subagents, and manage git workflows autonomously.

## Installation

### Prerequisites

- **Node.js v18+** required (v24 LTS recommended). Use `nvm` to manage Node versions.
- **npm** bundled with Node.js.

### Install Claude Code

```bash
npm install -g @anthropic-ai/claude-code
```

Verify installation:

```bash
claude --version     # Expected output: 2.x.x (Claude Code)
which claude         # Should show a path under your nvm directory or /usr/local
```

### WSL / Linux Installation via nvm (Recommended for controlled environments)

On WSL/Linux, use nvm for Node.js version management to avoid version conflicts:

```bash
# 1. Check proxy (if behind corporate firewall):
#    Test proxy first; common proxy: http://172.23.96.1:7890
curl -s --max-time 5 -x http://<proxy-ip>:<port> https://raw.githubusercontent.com/...

# 2. Install nvm:
#    Option A — via install script (requires proxy for raw.githubusercontent.com):
export http_proxy="http://<proxy>:<port>"
export https_proxy="http://<proxy>:<port>"
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.4/install.sh | bash

#    Option B — git clone (alternative if raw.githubusercontent.com is slow):
git clone --depth=1 https://github.com/nvm-sh/nvm.git ~/.nvm

# 3. Load nvm and install Node:
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm install 24       # Installs latest LTS (v24.x as of 2026)

# 4. Install Claude Code:
npm install -g @anthropic-ai/claude-code

# 5. Verify:
nvm use 24 && claude --version
```

**Proxy tips for restricted environments:**
- Always set `http_proxy`/`https_proxy` environment variables before npm/git operations
- npm has its own proxy setting: `npm config set proxy http://<proxy>:<port>`
- For curl: use `-x` flag or env variables
- After initial setup, node/npm/claude commands usually do NOT need the proxy for normal operation

### Windows / macOS

```bash
# macOS (Homebrew):
brew install nvm
nvm install 24
nvm use 24
npm install -g @anthropic-ai/claude-code

# Windows: install via nvm-windows or download Node installer directly from nodejs.org
npm install -g @anthropic-ai/claude-code
```

### Interactive Mode vs Print Mode Discrepancy (CRITICAL)

Claude Code's **interactive mode** (`claude` with no `-p` flag) performs additional startup checks that `-p` mode skips. This causes a **split failure mode** when using a proxy:

| Mode | Startup checks | Works with proxy? |
|------|---------------|-------------------|
| `-p "task"` | POST /v1/messages only | ✅ Always works |
| Interactive (`claude`) | HEAD / + POST /v1/messages | ❌ Fails without HEAD route |

**Symptom:** `claude -p "hello"` works perfectly, but `claude` (interactive) gives "Unable to connect to Anthropic services / ERR_BAD_REQUEST - Failed to connect to api.anthropic.com"

**Root Cause:** The interactive TUI sends a `HEAD /` health-check request before any message API calls. The proxy (anthropic-proxy) doesn't handle this route natively, so it falls through to the real `api.anthropic.com` and fails.

**Fix:** Add `HEAD /` and `GET /` routes to the proxy (see "Patch 3: HEAD / + GET / routes" below).

### Auth Setup

- **OAuth (default):** run `claude` once — opens browser login for Pro/Max subscriptions
- **API key:** set `ANTHROPIC_API_KEY=sk-ant-...` in environment
- **Console auth:** `claude auth login --console` (API key billing)
- **SSO auth:** `claude auth login --sso` (Enterprise)
- **Check status:** `claude auth status` (JSON) or `claude auth status --text`
- **Health check:** `claude doctor` — checks auto-updater and installation health
- **Version check:** `claude --version` (requires v2.x+)
- **Update:** `claude update` or `claude upgrade`

### Cross-Platform Detection

When orchestrating Claude Code, detect the environment to avoid proxy/auth surprises:

```bash
uname -a        # Check if running in WSL
env | grep -i proxy   # Check proxy env vars
claude --version      # Confirm installed
claude auth status --text  # Check auth state
```

## Model Provider Limitations (CRITICAL)

### What Claude Code Supports Natively

| Provider | Status | How |
|----------|--------|-----|
| **Anthropic API** | ✅ Native | Default, uses ANTHROPIC_API_KEY or OAuth |
| **AWS Bedrock** | ✅ Supported | Via `--bare` mode, uses AWS credentials |
| **GCP Vertex AI** | ✅ Supported | Via `--bare` mode, uses GCP credentials |
| **Anthropic Foundry** | ✅ Supported | Via `--bare` mode, enterprise offering |
| **OpenAI-compatible (DeepSeek, etc.)** | ❌ NOT supported | No native provider flag for OpenAI-compatible APIs |

### Why DeepSeek / OpenAI-Compatible APIs Won't Work Directly (Without a Proxy)

Claude Code communicates with Anthropic's **Messages API** (a proprietary format with tool-use and extended thinking baked in). DeepSeek (and other OpenAI-compatible providers) speak the **OpenAI Chat Completions API** format. These two protocols are structurally different.

**Signs of this limitation:**
- `claude --model` only accepts Claude model names (`sonnet`, `opus`, `haiku`, `claude-sonnet-4-6`, etc.)
- No `--provider` or `--endpoint` flag exists in the CLI (confirmed via `claude --help`)
- `--bare` mode help confirms: "3P providers (Bedrock/Vertex/Foundry) use their own credentials" — no mention of OpenAI-compatible providers

### Workaround: anthropic-proxy Translation Layer (RECOMMENDED — PROVEN TO WORK)

Use `maxnowack/anthropic-proxy` — a lightweight Node.js proxy that translates Anthropic Messages API ↔ OpenAI Chat API format, then point Claude Code at it via `ANTHROPIC_BASE_URL`.

**Key findings (verified 2026-05-22):**
- `ANTHROPIC_BASE_URL` **IS recognized** by Claude Code when combined with `--settings '{"provider":"openai"}'`
- Works in both interactive mode and `--bare` mode
- `--bare` mode requires `--settings '{"provider":"openai"}'` and `--model "deepseek-chat"` flags
- Interactive mode needs only `ANTHROPIC_BASE_URL` env var

```bash
# 1. Install (npx auto-caches after first run)
npx anthropic-proxy  # First download, then exits because no ANTHROPIC_PROXY_BASE_URL set

# 2. Patch: add ANTHROPIC_PROXY_API_KEY env var support (see references)
#    Edit ~/.npm/_npx/<hash>/node_modules/anthropic-proxy/index.js
#    Line 7:  key = ANTHROPIC_PROXY_API_KEY || (requiresApiKey ? OPENROUTER_API_KEY : null)
#    Line 162: if (key) { headers['Authorization'] = ... }

# 3. Start proxy
ANTHROPIC_PROXY_BASE_URL=https://api.deepseek.com \
ANTHROPIC_PROXY_API_KEY=sk-xxx \
COMPLETION_MODEL=deepseek-chat \
PORT=3000 \
npx anthropic-proxy

# 4. Use Claude Code pointing at proxy
ANTHROPIC_BASE_URL=http://localhost:3000 claude

# Or for single-command mode:
ANTHROPIC_BASE_URL=http://localhost:3000 claude --bare -p "task" \
  --settings '{"provider":"openai"}' --model "deepseek-chat"
```

**Important caveats:**
- The proxy source needs a 2-line patch to add `ANTHROPIC_PROXY_API_KEY` env var support (upstream PR pending)
- **Patch 3 also required for interactive mode:** The proxy needs `HEAD /` and `GET /` route handlers (see `references/wsl-installation-recipe.md` for exact code)
- `ANTHROPIC_PROXY_BASE_URL` must NOT include `/v1` (proxy appends `/v1/chat/completions` internally)
- Tool-use (file editing, bash) in `--bare` mode may have degraded translation — test before production use
- Extended thinking / chain-of-thought may not work correctly
- Some Claude Code features (MCP, subagents, hooks) are untested with this setup
- Not officially supported by Anthropic — use at your own risk

**Detailed setup guide:** See `devops/claude-code-deepseek-proxy` skill.
**Proxy patch notes:** `devops/claude-code-deepseek-proxy → references/proxy-patch-notes.md`

### Proxy Lifecycle Management

#### Start proxy with npx (first time or after npx cache clear)

When `npx anthropic-proxy` runs, it re-downloads the package if not cached, which **loses all patches**. Always check and re-patch after first run:

```bash
# 1. Let npx download/cache the package
npx anthropic-proxy --help
# 2. Verify it was cached
ls ~/.npm/_npx/*/node_modules/anthropic-proxy/index.js
# 3. Apply all patches (see references/wsl-installation-recipe.md for exact code)
# 4. Start
```

#### Start proxy (after patched — Hermes orchestration)

Use `terminal(background=true)` — not nohup/& — when Hermes orchestrates the proxy:

```python
terminal(command="source ~/.hermes/.env && ANTHROPIC_PROXY_BASE_URL=https://api.deepseek.com ANTHROPIC_PROXY_API_KEY=\"$DEEPSEEK_API_KEY\" COMPLETION_MODEL=deepseek-chat REASONING_MODEL=deepseek-chat PORT=3000 npx anthropic-proxy", background=True)
```

Wait 3-4 seconds, then verify:

```python
terminal(command="sleep 4 && curl -s --max-time 3 -o /dev/null -w '%{http_code}' http://localhost:3000/", timeout=10)
# → Expected: 200
```

#### Start proxy (manual — user terminal)

```bash
source ~/.hermes/.env && \
ANTHROPIC_PROXY_BASE_URL=https://api.deepseek.com \
ANTHROPIC_PROXY_API_KEY="$DEEPSEEK_API_KEY" \
COMPLETION_MODEL=deepseek-chat \
PORT=3000 \
npx anthropic-proxy
```

Or using the startup script:

```bash
~/start-deepseek-proxy.sh
# Or in background:
nohup ~/start-deepseek-proxy.sh &
```

#### Stop proxy

```bash
kill $(ps aux | grep "anthropic-proxy" | grep -v grep | awk '{print $2}')
```

### Shell Function Approach (MOST RELIABLE for nvm setups)

**Problem:** Wrapper scripts at `~/.local/bin/claude` are shadowed by nvm's bin directory in PATH. Aliases break when paste splits across lines. Neither are reliable.

**Solution:** Shell function in `.bashrc` — overrides PATH unconditionally, immune to hash caching:

```bash
# Add to ~/.bashrc (single line):
claude() { ANTHROPIC_API_KEY=sk-placeholder ANTHROPIC_BASE_URL=http://localhost:3000 /home/dmin/.nvm/versions/node/v24.16.0/bin/claude "$@"; }
```

**How it works:**
- Shell functions take priority over PATH lookups in bash
- `ANTHROPIC_API_KEY` and `ANTHROPIC_BASE_URL` are set as command-prefix env vars, overriding any inherited values
- The function body executes with `exec`, replacing the current shell context with the raw Claude Code binary
- After reloading `.bashrc`, `type claude` shows `claude is a function` rather than a path

**Comparison:**

| Method | Reliability | nvm-safe | Paste-safe | Notes |
|--------|-------------|----------|------------|-------|
| Wrapper script (`~/.local/bin/claude`) | ❌ | ❌ | ✅ | Shadowed by nvm PATH |
| Alias (`alias claude=...`) | ⚠️ | ✅ | ❌ | Breaks on multiline paste |
| **Shell function** (`claude() { ... }`) | ✅ | ✅ | ✅ | Recommended |

### Moving from Wrapper Script to Shell Function (if you already set up the wrapper)

```bash
# 1. Remove the wrapper's PATH addition from .bashrc
sed -i '/PATH.*local.bin.*PATH/d' ~/.bashrc

# 2. Add the shell function (single line)
echo 'claude() { ANTHROPIC_API_KEY=sk-placeholder ANTHROPIC_BASE_URL=http://localhost:3000 /home/dmin/.nvm/versions/node/v24.16.0/bin/claude "$@"; }' >> ~/.bashrc

# 3. Keep the wrapper script as a fallback (won't hurt)

# 4. Reload
source ~/.bashrc
```

For full third-party model support without a proxy, use [OpenCode](https://opencode.ai) — a provider-agnostic open-source fork with native OpenAI-compatible API support:

```bash
npm install -g opencode-ai@latest
opencode run 'Your task' --model deepseek/deepseek-chat
```

See `opencode` skill for full orchestration instructions.

## Two Orchestration Modes

Hermes interacts with Claude Code in two fundamentally different ways. Choose based on the task.

### Mode 1: Print Mode (`-p`) — Non-Interactive (PREFERRED for most tasks)

Print mode runs a one-shot task, returns the result, and exits. No PTY needed. No interactive prompts. This is the cleanest integration path.

```
terminal(command="claude -p 'Add error handling to all API calls in src/' --allowedTools 'Read,Edit' --max-turns 10", workdir="/path/to/project", timeout=120)
```

**When to use print mode:**
- One-shot coding tasks (fix a bug, add a feature, refactor)
- CI/CD automation and scripting
- Structured data extraction with `--json-schema`
- Piped input processing (`cat file | claude -p "analyze this"`)
- Any task where you don't need multi-turn conversation

**Print mode skips ALL interactive dialogs** — no workspace trust prompt, no permission confirmations. This makes it ideal for automation.

### Mode 2: Interactive PTY via tmux — Multi-Turn Sessions

Interactive mode gives you a full conversational REPL where you can send follow-up prompts, use slash commands, and watch Claude work in real time. **Requires tmux orchestration.**

```
# Start a tmux session
terminal(command="tmux new-session -d -s claude-work -x 140 -y 40")

# Launch Claude Code inside it
terminal(command="tmux send-keys -t claude-work 'cd /path/to/project && claude' Enter")

# Wait for startup, then send your task
# (after ~3-5 seconds for the welcome screen)
terminal(command="sleep 5 && tmux send-keys -t claude-work 'Refactor the auth module to use JWT tokens' Enter")

# Monitor progress by capturing the pane
terminal(command="sleep 15 && tmux capture-pane -t claude-work -p -S -50")

# Send follow-up tasks
terminal(command="tmux send-keys -t claude-work 'Now add unit tests for the new JWT code' Enter")

# Exit when done
terminal(command="tmux send-keys -t claude-work '/exit' Enter")
```

**When to use interactive mode:**
- Multi-turn iterative work (refactor → review → fix → test cycle)
- Tasks requiring human-in-the-loop decisions
- Exploratory coding sessions
- When you need to use Claude's slash commands (`/compact`, `/review`, `/model`)

## PTY Dialog Handling (CRITICAL for Interactive Mode)

Claude Code presents up to two confirmation dialogs on first launch. You MUST handle these via tmux send-keys:

### Dialog 1: Workspace Trust (first visit to a directory)
```
❯ 1. Yes, I trust this folder    ← DEFAULT (just press Enter)
  2. No, exit
```
**Handling:** `tmux send-keys -t <session> Enter` — default selection is correct.

### Dialog 2: Bypass Permissions Warning (only with --dangerously-skip-permissions)
```
❯ 1. No, exit                    ← DEFAULT (WRONG choice!)
  2. Yes, I accept
```
**Handling:** Must navigate DOWN first, then Enter:
```
tmux send-keys -t <session> Down && sleep 0.3 && tmux send-keys -t <session> Enter
```

### Robust Dialog Handling Pattern
```
# Launch with permissions bypass
terminal(command="tmux send-keys -t claude-work 'claude --dangerously-skip-permissions \"your task\"' Enter")

# Handle trust dialog (Enter for default "Yes")
terminal(command="sleep 4 && tmux send-keys -t claude-work Enter")

# Handle permissions dialog (Down then Enter for "Yes, I accept")
terminal(command="sleep 3 && tmux send-keys -t claude-work Down && sleep 0.3 && tmux send-keys -t claude-work Enter")

# Now wait for Claude to work
terminal(command="sleep 15 && tmux capture-pane -t claude-work -p -S -60")
```

**Note:** After the first trust acceptance for a directory, the trust dialog won't appear again. Only the permissions dialog recurs each time you use `--dangerously-skip-permissions`.

## CLI Subcommands

| Subcommand | Purpose |
|------------|---------|
| `claude` | Start interactive REPL |
| `claude "query"` | Start REPL with initial prompt |
| `claude -p "query"` | Print mode (non-interactive, exits when done) |
| `cat file \| claude -p "query"` | Pipe content as stdin context |
| `claude -c` | Continue the most recent conversation in this directory |
| `claude -r "id"` | Resume a specific session by ID or name |
| `claude auth login` | Sign in (add `--console` for API billing, `--sso` for Enterprise) |
| `claude auth status` | Check login status (returns JSON; `--text` for human-readable) |
| `claude mcp add <name> -- <cmd>` | Add an MCP server |
| `claude mcp list` | List configured MCP servers |
| `claude mcp remove <name>` | Remove an MCP server |
| `claude agents` | List configured agents |
| `claude doctor` | Run health checks on installation and auto-updater |
| `claude update` / `claude upgrade` | Update Claude Code to latest version |
| `claude remote-control` | Start server to control Claude from claude.ai or mobile app |
| `claude install [target]` | Install native build (stable, latest, or specific version) |
| `claude setup-token` | Set up long-lived auth token (requires subscription) |
| `claude plugin` / `claude plugins` | Manage Claude Code plugins |
| `claude auto-mode` | Inspect auto mode classifier configuration |

## Print Mode Deep Dive

### Structured JSON Output
```
terminal(command="claude -p 'Analyze auth.py for security issues' --output-format json --max-turns 5", workdir="/project", timeout=120)
```

Returns a JSON object with:
```json
{
  "type": "result",
  "subtype": "success",
  "result": "The analysis text...",
  "session_id": "75e2167f-...",
  "num_turns": 3,
  "total_cost_usd": 0.0787,
  "duration_ms": 10276,
  "stop_reason": "end_turn",
  "terminal_reason": "completed",
  "usage": { "input_tokens": 5, "output_tokens": 603, ... },
  "modelUsage": { "claude-sonnet-4-6": { "costUSD": 0.078, "contextWindow": 200000 } }
}
```

**Key fields:** `session_id` for resumption, `num_turns` for agentic loop count, `total_cost_usd` for spend tracking, `subtype` for success/error detection (`success`, `error_max_turns`, `error_budget`).

### Streaming JSON Output
For real-time token streaming, use `stream-json` with `--verbose`:
```
terminal(command="claude -p 'Write a summary' --output-format stream-json --verbose --include-partial-messages", timeout=60)
```

Returns newline-delimited JSON events. Filter with jq for live text:
```
claude -p "Explain X" --output-format stream-json --verbose --include-partial-messages | \
  jq -rj 'select(.type == "stream_event" and .event.delta.type? == "text_delta") | .event.delta.text'
```

Stream events include `system/api_retry` with `attempt`, `max_retries`, and `error` fields (e.g., `rate_limit`, `billing_error`).

### Bidirectional Streaming
For real-time input AND output streaming:
```
claude -p "task" --input-format stream-json --output-format stream-json --replay-user-messages
```
`--replay-user-messages` re-emits user messages on stdout for acknowledgment.

### Piped Input
```
# Pipe a file for analysis
terminal(command="cat src/auth.py | claude -p 'Review this code for bugs' --max-turns 1", timeout=60)

# Pipe multiple files
terminal(command="cat src/*.py | claude -p 'Find all TODO comments' --max-turns 1", timeout=60)

# Pipe command output
terminal(command="git diff HEAD~3 | claude -p 'Summarize these changes' --max-turns 1", timeout=60)
```

### JSON Schema for Structured Extraction
```
terminal(command="claude -p 'List all functions in src/' --output-format json --json-schema '{\"type\":\"object\",\"properties\":{\"functions\":{\"type\":\"array\",\"items\":{\"type\":\"string\"}}},\"required\":[\"functions\"]}' --max-turns 5", workdir="/project", timeout=90)
```

Parse `structured_output` from the JSON result. Claude validates output against the schema before returning.

### Session Continuation
```
# Start a task
terminal(command="claude -p 'Start refactoring the database layer' --output-format json --max-turns 10 > /tmp/session.json", workdir="/project", timeout=180)

# Resume with session ID
terminal(command="claude -p 'Continue and add connection pooling' --resume $(cat /tmp/session.json | python3 -c 'import json,sys; print(json.load(sys.stdin)[\"session_id\"])') --max-turns 5", workdir="/project", timeout=120)

# Or resume the most recent session in the same directory
terminal(command="claude -p 'What did you do last time?' --continue --max-turns 1", workdir="/project", timeout=30)

# Fork a session (new ID, keeps history)
terminal(command="claude -p 'Try a different approach' --resume <id> --fork-session --max-turns 10", workdir="/project", timeout=120)
```

### Bare Mode for CI/Scripting
```
terminal(command="claude --bare -p 'Run all tests and report failures' --allowedTools 'Read,Bash' --max-turns 10", workdir="/project", timeout=180)
```

`--bare` skips hooks, plugins, MCP discovery, and CLAUDE.md loading. Fastest startup. Requires `ANTHROPIC_API_KEY` (skips OAuth).

To selectively load context in bare mode:
| To load | Flag |
|---------|------|
| System prompt additions | `--append-system-prompt "text"` or `--append-system-prompt-file path` |
| Settings | `--settings <file-or-json>` |
| MCP servers | `--mcp-config <file-or-json>` |
| Custom agents | `--agents '<json>'` |

### Fallback Model for Overload
```
terminal(command="claude -p 'task' --fallback-model haiku --max-turns 5", timeout=90)
```
Automatically falls back to the specified model when the default is overloaded (print mode only).

## Complete CLI Flags Reference

### Session & Environment
| Flag | Effect |
|------|--------|
| `-p, --print` | Non-interactive one-shot mode (exits when done) |
| `-c, --continue` | Resume most recent conversation in current directory |
| `-r, --resume <id>` | Resume specific session by ID or name (interactive picker if no ID) |
| `--fork-session` | When resuming, create new session ID instead of reusing original |
| `--session-id <uuid>` | Use a specific UUID for the conversation |
| `--no-session-persistence` | Don't save session to disk (print mode only) |
| `--add-dir <paths...>` | Grant Claude access to additional working directories |
| `-w, --worktree [name]` | Run in an isolated git worktree at `.claude/worktrees/<name>` |
| `--tmux` | Create a tmux session for the worktree (requires `--worktree`) |
| `--ide` | Auto-connect to a valid IDE on startup |
| `--chrome` / `--no-chrome` | Enable/disable Chrome browser integration for web testing |
| `--from-pr [number]` | Resume session linked to a specific GitHub PR |
| `--file <specs...>` | File resources to download at startup (format: `file_id:relative_path`) |

### Model & Performance
| Flag | Effect |
|------|--------|
| `--model <alias>` | Model selection: `sonnet`, `opus`, `haiku`, or full name like `claude-sonnet-4-6` |
| `--effort <level>` | Reasoning depth: `low`, `medium`, `high`, `max`, `auto` | Both |
| `--max-turns <n>` | Limit agentic loops (print mode only; prevents runaway) |
| `--max-budget-usd <n>` | Cap API spend in dollars (print mode only) |
| `--fallback-model <model>` | Auto-fallback when default model is overloaded (print mode only) |
| `--betas <betas...>` | Beta headers to include in API requests (API key users only) |

### Permission & Safety
| Flag | Effect |
|------|--------|
| `--dangerously-skip-permissions` | Auto-approve ALL tool use (file writes, bash, network, etc.) |
| `--allow-dangerously-skip-permissions` | Enable bypass as an *option* without enabling it by default |
| `--permission-mode <mode>` | `default`, `acceptEdits`, `plan`, `auto`, `dontAsk`, `bypassPermissions` |
| `--allowedTools <tools...>` | Whitelist specific tools (comma or space-separated) |
| `--disallowedTools <tools...>` | Blacklist specific tools |
| `--tools <tools...>` | Override built-in tool set (`""` = none, `"default"` = all, or tool names) |

### Output & Input Format
| Flag | Effect |
|------|--------|
| `--output-format <fmt>` | `text` (default), `json` (single result object), `stream-json` (newline-delimited) |
| `--input-format <fmt>` | `text` (default) or `stream-json` (real-time streaming input) |
| `--json-schema <schema>` | Force structured JSON output matching a schema |
| `--verbose` | Full turn-by-turn output |
| `--include-partial-messages` | Include partial message chunks as they arrive (stream-json + print) |
| `--replay-user-messages` | Re-emit user messages on stdout (stream-json bidirectional) |

### System Prompt & Context
| Flag | Effect |
|------|--------|
| `--append-system-prompt <text>` | **Add** to the default system prompt (preserves built-in capabilities) |
| `--append-system-prompt-file <path>` | **Add** file contents to the default system prompt |
| `--system-prompt <text>` | **Replace** the entire system prompt (use --append instead usually) |
| `--system-prompt-file <path>` | **Replace** the system prompt with file contents |
| `--bare` | Skip hooks, plugins, MCP discovery, CLAUDE.md, OAuth (fastest startup) |
| `--agents '<json>'` | Define custom subagents dynamically as JSON |
| `--mcp-config <path>` | Load MCP servers from JSON file (repeatable) |
| `--strict-mcp-config` | Only use MCP servers from `--mcp-config`, ignoring all other MCP configs |
| `--settings <file-or-json>` | Load additional settings from a JSON file or inline JSON |
| `--setting-sources <sources>` | Comma-separated sources to load: `user`, `project`, `local` |
| `--plugin-dir <paths...>` | Load plugins from directories for this session only |
| `--disable-slash-commands` | Disable all skills/slash commands |

### Debugging
| Flag | Effect |
|------|--------|
| `-d, --debug [filter]` | Enable debug logging with optional category filter (e.g., `"api,hooks"`, `"!1p,!file"`) |
| `--debug-file <path>` | Write debug logs to file (implicitly enables debug mode) |

### Agent Teams
| Flag | Effect |
|------|--------|
| `--teammate-mode <mode>` | How agent teams display: `auto`, `in-process`, or `tmux` |
| `--brief` | Enable `SendUserMessage` tool for agent-to-user communication |

### Tool Name Syntax for --allowedTools / --disallowedTools
```
Read                    # All file reading
Edit                    # File editing (existing files)
Write                   # File creation (new files)
Bash                    # All shell commands
Bash(git *)             # Only git commands
Bash(git commit *)      # Only git commit commands
Bash(npm run lint:*)    # Pattern matching with wildcards
WebSearch               # Web search capability
WebFetch                # Web page fetching
mcp__<server>__<tool>   # Specific MCP tool
```

## Settings & Configuration

### Settings Hierarchy (highest to lowest priority)
1. **CLI flags** — override everything
2. **Local project:** `.claude/settings.local.json` (personal, gitignored)
3. **Project:** `.claude/settings.json` (shared, git-tracked)
4. **User:** `~/.claude/settings.json` (global)

### Permissions in Settings
```json
{
  "permissions": {
    "allow": ["Bash(npm run lint:*)", "WebSearch", "Read"],
    "ask": ["Write(*.ts)", "Bash(git push*)"],
    "deny": ["Read(.env)", "Bash(rm -rf *)"]
  }
}
```

### Memory Files (CLAUDE.md) Hierarchy
1. **Global:** `~/.claude/CLAUDE.md` — applies to all projects
2. **Project:** `./CLAUDE.md` — project-specific context (git-tracked)
3. **Local:** `.claude/CLAUDE.local.md` — personal project overrides (gitignored)

Use the `#` prefix in interactive mode to quickly add to memory: `# Always use 2-space indentation`.

## Interactive Session: Slash Commands

### Session & Context
| Command | Purpose |
|---------|---------|
| `/help` | Show all commands (including custom and MCP commands) |
| `/compact [focus]` | Compress context to save tokens; CLAUDE.md survives compaction. E.g., `/compact focus on auth logic` |
| `/clear` | Wipe conversation history for a fresh start |
| `/context` | Visualize context usage as a colored grid with optimization tips |
| `/cost` | View token usage with per-model and cache-hit breakdowns |
| `/resume` | Switch to or resume a different session |
| `/rewind` | Revert to a previous checkpoint in conversation or code |
| `/btw <question>` | Ask a side question without adding to context cost |
| `/status` | Show version, connectivity, and session info |
| `/todos` | List tracked action items from the conversation |
| `/exit` or `Ctrl+D` | End session |

### Development & Review
| Command | Purpose |
|---------|---------|
| `/review` | Request code review of current changes |
| `/security-review` | Perform security analysis of current changes |
| `/plan [description]` | Enter Plan mode with auto-start for task planning |
| `/loop [interval]` | Schedule recurring tasks within the session |
| `/batch` | Auto-create worktrees for large parallel changes (5-30 worktrees) |

### Configuration & Tools
| Command | Purpose |
|---------|---------|
| `/model [model]` | Switch models mid-session (use arrow keys to adjust effort) |
| `/effort [level]` | Set reasoning effort: `low`, `medium`, `high`, `max`, or `auto` |
| `/init` | Create a CLAUDE.md file for project memory |
| `/memory` | Open CLAUDE.md for editing |
| `/config` | Open interactive settings configuration |
| `/permissions` | View/update tool permissions |
| `/agents` | Manage specialized subagents |
| `/mcp` | Interactive UI to manage MCP servers |
| `/add-dir` | Add additional working directories (useful for monorepos) |
| `/usage` | Show plan limits and rate limit status |
| `/voice` | Enable push-to-talk voice mode (20 languages; hold Space to record, release to send) |
| `/release-notes` | Interactive picker for version release notes |

### Custom Slash Commands
Create `.claude/commands/<name>.md` (project-shared) or `~/.claude/commands/<name>.md` (personal):

```markdown
# .claude/commands/deploy.md
Run the deploy pipeline:
1. Run all tests
2. Build the Docker image
3. Push to registry
4. Update the $ARGUMENTS environment (default: staging)
```

Usage: `/deploy production` — `$ARGUMENTS` is replaced with the user's input.

### Skills (Natural Language Invocation)
Unlike slash commands (manually invoked), skills in `.claude/skills/` are markdown guides that Claude invokes automatically via natural language when the task matches:

```markdown
# .claude/skills/database-migration.md
When asked to create or modify database migrations:
1. Use Alembic for migration generation
2. Always create a rollback function
3. Test migrations against a local database copy
```

## Interactive Session: Keyboard Shortcuts

### General Controls
| Key | Action |
|-----|--------|
| `Ctrl+C` | Cancel current input or generation |
| `Ctrl+D` | Exit session |
| `Ctrl+R` | Reverse search command history |
| `Ctrl+B` | Background a running task |
| `Ctrl+V` | Paste image into conversation |
| `Ctrl+O` | Transcript mode — see Claude's thinking process |
| `Ctrl+G` or `Ctrl+X Ctrl+E` | Open prompt in external editor |
| `Esc Esc` | Rewind conversation or code state / summarize |

### Mode Toggles
| Key | Action |
|-----|--------|
| `Shift+Tab` | Cycle permission modes (Normal → Auto-Accept → Plan) |
| `Alt+P` | Switch model |
| `Alt+T` | Toggle thinking mode |
| `Alt+O` | Toggle Fast Mode |

### Multiline Input
| Key | Action |
|-----|--------|
| `\` + `Enter` | Quick newline |
| `Shift+Enter` | Newline (alternative) |
| `Ctrl+J` | Newline (alternative) |

### Input Prefixes
| Prefix | Action |
|--------|--------|
| `!` | Execute bash directly, bypassing AI (e.g., `!npm test`). Use `!` alone to toggle shell mode. |
| `@` | Reference files/directories with autocomplete (e.g., `@./src/api/`) |
| `#` | Quick add to CLAUDE.md memory (e.g., `# Use 2-space indentation`) |
| `/` | Slash commands |

### Pro Tip: "ultrathink"
Use the keyword "ultrathink" in your prompt for maximum reasoning effort on a specific turn. This triggers the deepest thinking mode regardless of the current `/effort` setting.

## PR Review Pattern

### Quick Review (Print Mode)
```
terminal(command="cd /path/to/repo && git diff main...feature-branch | claude -p 'Review this diff for bugs, security issues, and style problems. Be thorough.' --max-turns 1", timeout=60)
```

### Deep Review (Interactive + Worktree)
```
terminal(command="tmux new-session -d -s review -x 140 -y 40")
terminal(command="tmux send-keys -t review 'cd /path/to/repo && claude -w pr-review' Enter")
terminal(command="sleep 5 && tmux send-keys -t review Enter")  # Trust dialog
terminal(command="sleep 2 && tmux send-keys -t review 'Review all changes vs main. Check for bugs, security issues, race conditions, and missing tests.' Enter")
terminal(command="sleep 30 && tmux capture-pane -t review -p -S -60")
```

### PR Review from Number
```
terminal(command="claude -p 'Review this PR thoroughly' --from-pr 42 --max-turns 10", workdir="/path/to/repo", timeout=120)
```

### Claude Worktree with tmux
```
terminal(command="claude -w feature-x --tmux", workdir="/path/to/repo")
```
Creates an isolated git worktree at `.claude/worktrees/feature-x` AND a tmux session for it. Uses iTerm2 native panes when available; add `--tmux=classic` for traditional tmux.

## Parallel Claude Instances

Run multiple independent Claude tasks simultaneously:

```
# Task 1: Fix backend
terminal(command="tmux new-session -d -s task1 -x 140 -y 40 && tmux send-keys -t task1 'cd ~/project && claude -p \"Fix the auth bug in src/auth.py\" --allowedTools \"Read,Edit\" --max-turns 10' Enter")

# Task 2: Write tests
terminal(command="tmux new-session -d -s task2 -x 140 -y 40 && tmux send-keys -t task2 'cd ~/project && claude -p \"Write integration tests for the API endpoints\" --allowedTools \"Read,Write,Bash\" --max-turns 15' Enter")

# Task 3: Update docs
terminal(command="tmux new-session -d -s task3 -x 140 -y 40 && tmux send-keys -t task3 'cd ~/project && claude -p \"Update README.md with the new API endpoints\" --allowedTools \"Read,Edit\" --max-turns 5' Enter")

# Monitor all
terminal(command="sleep 30 && for s in task1 task2 task3; do echo '=== '$s' ==='; tmux capture-pane -t $s -p -S -5 2>/dev/null; done")
```

## CLAUDE.md — Project Context File

Claude Code auto-loads `CLAUDE.md` from the project root. Use it to persist project context:

```markdown
# Project: My API

## Architecture
- FastAPI backend with SQLAlchemy ORM
- PostgreSQL database, Redis cache
- pytest for testing with 90% coverage target

## Key Commands
- `make test` — run full test suite
- `make lint` — ruff + mypy
- `make dev` — start dev server on :8000

## Code Standards
- Type hints on all public functions
- Docstrings in Google style
- 2-space indentation for YAML, 4-space for Python
- No wildcard imports
```

**Be specific.** Instead of "Write good code", use "Use 2-space indentation for JS" or "Name test files with `.test.ts` suffix." Specific instructions save correction cycles.

### Rules Directory (Modular CLAUDE.md)
For projects with many rules, use the rules directory instead of one massive CLAUDE.md:
- **Project rules:** `.claude/rules/*.md` — team-shared, git-tracked
- **User rules:** `~/.claude/rules/*.md` — personal, global

Each `.md` file in the rules directory is loaded as additional context. This is cleaner than cramming everything into a single CLAUDE.md.

### Auto-Memory
Claude automatically stores learned project context in `~/.claude/projects/<project>/memory/`.
- **Limit:** 25KB or 200 lines per project
- This is separate from CLAUDE.md — it's Claude's own notes about the project, accumulated across sessions

## Custom Subagents

Define specialized agents in `.claude/agents/` (project), `~/.claude/agents/` (personal), or via `--agents` CLI flag (session):

### Agent Location Priority
1. `.claude/agents/` — project-level, team-shared
2. `--agents` CLI flag — session-specific, dynamic
3. `~/.claude/agents/` — user-level, personal

### Creating an Agent
```markdown
# .claude/agents/security-reviewer.md
---
name: security-reviewer
description: Security-focused code review
model: opus
tools: [Read, Bash]
---
You are a senior security engineer. Review code for:
- Injection vulnerabilities (SQL, XSS, command injection)
- Authentication/authorization flaws
- Secrets in code
- Unsafe deserialization
```

Invoke via: `@security-reviewer review the auth module`

### Dynamic Agents via CLI
```
terminal(command="claude --agents '{\"reviewer\": {\"description\": \"Reviews code\", \"prompt\": \"You are a code reviewer focused on performance\"}}' -p 'Use @reviewer to check auth.py'", timeout=120)
```

Claude can orchestrate multiple agents: "Use @db-expert to optimize queries, then @security to audit the changes."

## Hooks — Automation on Events

Configure in `.claude/settings.json` (project) or `~/.claude/settings.json` (global):

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write(*.py)",
      "hooks": [{"type": "command", "command": "ruff check --fix $CLAUDE_FILE_PATHS"}]
    }],
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{"type": "command", "command": "if echo \"$CLAUDE_TOOL_INPUT\" | grep -q 'rm -rf'; then echo 'Blocked!' && exit 2; fi"}]
    }],
    "Stop": [{
      "hooks": [{"type": "command", "command": "echo 'Claude finished a response' >> /tmp/claude-activity.log"}]
    }]
  }
}
```

### All 8 Hook Types
| Hook | When it fires | Common use |
|------|--------------|------------|
| `UserPromptSubmit` | Before Claude processes a user prompt | Input validation, logging |
| `PreToolUse` | Before tool execution | Security gates, block dangerous commands (exit 2 = block) |
| `PostToolUse` | After a tool finishes | Auto-format code, run linters |
| `Notification` | On permission requests or input waits | Desktop notifications, alerts |
| `Stop` | When Claude finishes a response | Completion logging, status updates |
| `SubagentStop` | When a subagent completes | Agent orchestration |
| `PreCompact` | Before context memory is cleared | Backup session transcripts |
| `SessionStart` | When a session begins | Load dev context (e.g., `git status`) |

### Hook Environment Variables
| Variable | Content |
|----------|---------|
| `CLAUDE_PROJECT_DIR` | Current project path |
| `CLAUDE_FILE_PATHS` | Files being modified |
| `CLAUDE_TOOL_INPUT` | Tool parameters as JSON |

### Security Hook Examples
```json
{
  "PreToolUse": [{
    "matcher": "Bash",
    "hooks": [{"type": "command", "command": "if echo \"$CLAUDE_TOOL_INPUT\" | grep -qE 'rm -rf|git push.*--force|:(){ :|:& };:'; then echo 'Dangerous command blocked!' && exit 2; fi"}]
  }]
}
```

## MCP Integration

Add external tool servers for databases, APIs, and services:

```
# GitHub integration
terminal(command="claude mcp add -s user github -- npx @modelcontextprotocol/server-github", timeout=30)

# PostgreSQL queries
terminal(command="claude mcp add -s local postgres -- npx @anthropic-ai/server-postgres --connection-string postgresql://localhost/mydb", timeout=30)

# Puppeteer for web testing
terminal(command="claude mcp add puppeteer -- npx @anthropic-ai/server-puppeteer", timeout=30)
```

### MCP Scopes
| Flag | Scope | Storage |
|------|-------|---------|
| `-s user` | Global (all projects) | `~/.claude.json` |
| `-s local` | This project (personal) | `.claude/settings.local.json` (gitignored) |
| `-s project` | This project (team-shared) | `.claude/settings.json` (git-tracked) |

### MCP in Print/CI Mode
```
terminal(command="claude --bare -p 'Query database' --mcp-config mcp-servers.json --strict-mcp-config", timeout=60)
```
`--strict-mcp-config` ignores all MCP servers except those from `--mcp-config`.

Reference MCP resources in chat: `@github:issue://123`

### MCP Limits & Tuning
- **Tool descriptions:** 2KB cap per server for tool descriptions and server instructions
- **Result size:** Default capped; use `maxResultSizeChars` annotation to allow up to **500K** characters for large outputs
- **Output tokens:** `export MAX_MCP_OUTPUT_TOKENS=50000` — cap output from MCP servers to prevent context flooding
- **Transports:** `stdio` (local process), `http` (remote), `sse` (server-sent events)

## Monitoring Interactive Sessions

### Reading the TUI Status
```
# Periodic capture to check if Claude is still working or waiting for input
terminal(command="tmux capture-pane -t dev -p -S -10")
```

Look for these indicators:
- `❯` at bottom = waiting for your input (Claude is done or asking a question)
- `●` lines = Claude is actively using tools (reading, writing, running commands)
- `⏵⏵ bypass permissions on` = status bar showing permissions mode
- `◐ medium · /effort` = current effort level in status bar
- `ctrl+o to expand` = tool output was truncated (can be expanded interactively)

### Context Window Health
Use `/context` in interactive mode to see a colored grid of context usage. Key thresholds:
- **< 70%** — Normal operation, full precision
- **70-85%** — Precision starts dropping, consider `/compact`
- **> 85%** — Hallucination risk spikes significantly, use `/compact` or `/clear`

## Environment Variables

| Variable | Effect |
|----------|--------|
| `ANTHROPIC_API_KEY` | API key for authentication (alternative to OAuth) |
| `CLAUDE_CODE_EFFORT_LEVEL` | Default effort: `low`, `medium`, `high`, `max`, or `auto` |
| `MAX_THINKING_TOKENS` | Cap thinking tokens (set to `0` to disable thinking entirely) |
| `MAX_MCP_OUTPUT_TOKENS` | Cap output from MCP servers (default varies; set e.g., `50000`) |
| `CLAUDE_CODE_NO_FLICKER=1` | Enable alt-screen rendering to eliminate terminal flicker |
| `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` | Strip credentials from sub-processes for security |

## Cost & Performance Tips

1. **Use `--max-turns`** in print mode to prevent runaway loops. Start with 5-10 for most tasks.
2. **Use `--max-budget-usd`** for cost caps. Note: minimum ~$0.05 for system prompt cache creation.
3. **Use `--effort low`** for simple tasks (faster, cheaper). `high` or `max` for complex reasoning.
4. **Use `--bare`** for CI/scripting to skip plugin/hook discovery overhead.
5. **Use `--allowedTools`** to restrict to only what's needed (e.g., `Read` only for reviews).
6. **Use `/compact`** in interactive sessions when context gets large.
7. **Pipe input** instead of having Claude read files when you just need analysis of known content.
8. **Use `--model haiku`** for simple tasks (cheaper) and `--model opus` for complex multi-step work.
9. **Use `--fallback-model haiku`** in print mode to gracefully handle model overload.
10. **Start new sessions for distinct tasks** — sessions last 5 hours; fresh context is more efficient.
11. **Use `--no-session-persistence`** in CI to avoid accumulating saved sessions on disk.

## Pitfalls & Gotchas

1. **Interactive mode REQUIRES tmux** — Claude Code is a full TUI app. Using `pty=true` alone in Hermes terminal works but tmux gives you `capture-pane` for monitoring and `send-keys` for input, which is essential for orchestration.
2. **`--dangerously-skip-permissions` dialog defaults to "No, exit"** — you must send Down then Enter to accept. Print mode (`-p`) skips this entirely.
3. **`--max-budget-usd` minimum is ~$0.05** — system prompt cache creation alone costs this much. Setting lower will error immediately.
4. **`--max-turns` is print-mode only** — ignored in interactive sessions.
5. **Claude may use `python` instead of `python3`** — on systems without a `python` symlink, Claude's bash commands will fail on first try but it self-corrects.
6. **Session resumption requires same directory** — `--continue` finds the most recent session for the current working directory.
7. **`--json-schema` needs enough `--max-turns`** — Claude must read files before producing structured output, which takes multiple turns.
8. **Trust dialog only appears once per directory** — first-time only, then cached.
9. **Background tmux sessions persist** — always clean up with `tmux kill-session -t <name>` when done.
10. **Slash commands (like `/commit`) only work in interactive mode** — in `-p` mode, describe the task in natural language instead.
11. **`--bare` skips OAuth** — requires `ANTHROPIC_API_KEY` env var or an `apiKeyHelper` in settings.
13. **Model provider limitation is a hard constraint** — Claude Code only supports Anthropic's API (plus Bedrock/Vertex/Foundry as cloud providers). It does NOT support OpenAI-compatible APIs (DeepSeek, Groq, Together, etc.) natively. There is no `--provider` or `--endpoint` flag. Workaround exists via `anthropic-proxy` (see "Workaround: anthropic-proxy" section above) but has feature limitations. For full third-party model support, use OpenCode instead.
14. **`ANTHROPIC_BASE_URL` IS supported with `--settings '{"provider":"openai"}'`** — though commonly claimed otherwise, `ANTHROPIC_BASE_URL` is recognized by Claude Code when combined with `provider: openai` in settings. Tested 2026-05-22: `ANTHROPIC_BASE_URL=http://localhost:3000 claude --bare -p "hi" --settings '{"provider":"openai"}' --model "deepseek-chat"` worked. Without `provider:openai`, `ANTHROPIC_BASE_URL` is ignored.
15. **Auth is required even in `--bare` mode** — `--bare` says it "skips OAuth" but still requires `ANTHROPIC_API_KEY` or `apiKeyHelper` in settings. Without valid auth, Claude Code returns "Not logged in" and exits. **Exception:** With a proxy that ignores the key (like anthropic-proxy), a fake placeholder works: `ANTHROPIC_API_KEY=sk-placeholder` — the env var just needs to exist.
16. **PATH ordering shadows wrapper scripts** — When using nvm, `$NVM_DIR/versions/node/*/bin/` is added to the **front** of PATH. This means any wrapper script at `~/.local/bin/claude` is ALWAYS shadowed by nvm's bin dir. `which claude` returns the nvm binary, NOT the wrapper. **Don't rely on wrapper scripts at `~/.local/bin/` with nvm.** Use a shell function instead (see "Shell Function Approach" below).

17. **Shell functions beat wrapper scripts for nvm setups** — A shell function defined in `.bashrc` overrides PATH lookups unconditionally, with no hash caching issues. The correct pattern:
    ```bash
    claude() { ANTHROPIC_API_KEY=sk-placeholder ANTHROPIC_BASE_URL=http://localhost:3000 /full/path/to/nvm/bin/claude "$@"; }
    ```
    This is the MOST RELIABLE method tested (verified 2026-05-22). Shell functions are immune to `hash` caching, PATH ordering, and typo-based issues.

18. **Terminal paste breaks multiline commands with quotes** — When users copy-paste multi-line commands with double quotes, the terminal may split at line breaks (even if the command visually appears as one line in the output). Broken alias fragments get written to `.bashrc` and corrupt the file. **Fix:** Write changes directly via the terminal tool instead of asking users to paste. If users must paste, use single-line commands with single quotes only — never multi-line or double-quote-heavy commands.

19. **Hermes `.venv-hermes` environment variable conflict** — Hermes Agent's virtual environment sets `ANTHROPIC_BASE_URL=http://localhost:4000/v1` (its own proxy for DeepSeek). If you run `claude` inside a terminal where `.venv-hermes` is active, this variable OVERRIDES any wrapper script's `ANTHROPIC_BASE_URL` setting, because shell env vars inherited into `exec` take precedence. **Symptoms:** `which claude` points correctly, but Claude Code still tries to reach `api.anthropic.com`. `env | grep ANTHROPIC` reveals the 4000 port. **Fix:** `deactivate` the venv, open a terminal without `.venv-hermes`, or `unset ANTHROPIC_BASE_URL` before running `claude`.

20. **Interactive mode vs print mode: split failure** — If `claude -p "hi"` works but `claude` (interactive) fails, the proxy likely lacks a `HEAD /` endpoint. This is the #1 differentiator — the interactive TUI does a health check that `-p` mode skips. Add `fastify.head("/", ...)` and `fastify.get("/", ...)` routes to the proxy.

21. **Proxy restart loses patches** — When `npx anthropic-proxy` runs, it checks `~/.npm/_npx/` for a cached version. If the cache was cleared (e.g., npm cache clean, node version change, or first install), npx re-downloads the package from npm. All source patches are lost on re-download. **Workflow:** Check that patches are still in place each time the proxy restarts unexpectedly. Use `grep -c "fastify.head"` on the proxy index.js to verify.

22. **Proxy must be running before Claude Code starts** — Claude Code does NOT retry the initial health check. If the proxy isn't ready when Claude Code sends its startup requests, it fails immediately. Always start the proxy 3-4 seconds before launching `claude`.

## Rules for Hermes Agents

1. **Prefer print mode (`-p`) for single tasks** — cleaner, no dialog handling, structured output
2. **Use tmux for multi-turn interactive work** — the only reliable way to orchestrate the TUI
3. **Always set `workdir`** — keep Claude focused on the right project directory
4. **Set `--max-turns` in print mode** — prevents infinite loops and runaway costs
5. **Monitor tmux sessions** — use `tmux capture-pane -t <session> -p -S -50` to check progress
6. **Look for the `❯` prompt** — indicates Claude is waiting for input (done or asking a question)
7. **Clean up tmux sessions** — kill them when done to avoid resource leaks
8. **Report results to user** — after completion, summarize what Claude did and what changed
9. **Don't kill slow sessions** — Claude may be doing multi-step work; check progress instead
10. **Use `--allowedTools`** — restrict capabilities to what the task actually needs
