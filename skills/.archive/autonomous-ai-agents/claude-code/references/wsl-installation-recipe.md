# WSL Installation Recipe — Claude Code + DeepSeek (Final Working Setup)

## Environment (Verified)

| Item | Value |
|------|-------|
| OS | WSL2 Ubuntu 22.04.5 LTS (kernel 6.6.114.1-microsoft-standard-WSL2) |
| Host | Windows 11, user `Admin`, desktop on `/mnt/c/Users/Admin/Desktop/` |
| WSL user | `dmin` (UID 1000), home `/home/dmin/` |
| Proxy (install only) | `http://172.23.96.1:7890` (Windows Clash proxy) |
| Claude Code version | v2.1.148 |
| Node.js | v24.16.0 (installed via nvm v0.40.4) |
| Proxy layer | `anthropic-proxy` (maxnowack/anthropic-proxy, patched for API key support) |
| Underlying model | DeepSeek V4 Flash via `api.deepseek.com` |
| Daily internet | NOT required (DeepSeek is domestic, anthropic-proxy runs locally) |

## Pre-Existing State

- Claude Code was already installed on Windows (`C:\Users\Admin\AppData\Roaming\npm\node_modules\@anthropic-ai\claude-code\`) — discovered during nvm install when it warned about existing global npm packages. This was ignored in favor of the WSL installation.
- DeepSeek API key existed in `~/.hermes/.env`: `DEEPSEEK_API_KEY=sk-xxx` (full key redacted)
- Hermes Agent runs DeepSeek V4 Flash natively (venv at `.venv-hermes`)

## Installation Steps That Worked

### Step 1: Set proxy for GitHub/npm downloads
```bash
export http_proxy="http://172.23.96.1:7890"
export https_proxy="http://172.23.96.1:7890"
```

### Step 2: Install nvm
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.4/install.sh | bash
# Reload
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
```

### Step 3: Install Node.js LTS + Claude Code
```bash
nvm install 24
npm install -g @anthropic-ai/claude-code
claude --version   # → 2.1.148
```

### Step 4: Install anthropic-proxy (the translation layer)
```bash
# First install (proxy needed for npm/github)
npx anthropic-proxy   # Downloads and immediately exits (no API key configured yet)

# Locate the installed proxy
find ~/.npm/_npx -name "index.js" -path "*anthropic-proxy*"
```

### Step 5: Patch the proxy for API key support
Edit `~/.npm/_npx/<hash>/node_modules/anthropic-proxy/index.js`:

**Patch 1** (line 7 or similar — `let key` assignment):
```
- let key = OPENROUTER_API_KEY;
+ let key = process.env.ANTHROPIC_PROXY_API_KEY || OPENROUTER_API_KEY || null;
```

### Patch 2 (line ~162 or similar — `Authorization` header condition):
```js
- if (key) {
+ if (key && key !== 'sk-placeholder') {
```

### Patch 3: HEAD / + GET / Routes (REQUIRED for interactive mode)

Add these routes right after the `fastify` initialization (after `const fastify = Fastify({...})`):

```js
fastify.head("/", async (req, reply) => {
  reply.code(200).send("OK")
})
fastify.get("/", async (req, reply) => {
  reply.send({status: "ok", service: "anthropic-proxy"})
})
```

Without this patch, `claude -p "hi"` works but `claude` (interactive mode) fails with:
```
Unable to connect to Anthropic services
Failed to connect to api.anthropic.com: ERR_BAD_REQUEST
```

The interactive TUI sends a `HEAD /` health-check request before any API calls. Without this route, the request falls through to the real Anthropic API and fails.

### Verify All Patches Are Applied
```bash
grep -n "ANTHROPIC_PROXY_API_KEY\|sk-placeholder\|fastify\.head\|fastify\.get" \
  ~/.npm/_npx/*/node_modules/anthropic-proxy/index.js
```

Expected output (3 lines):
```bash
let key = process.env.ANTHROPIC_PROXY_API_KEY || OPENROUTER_API_KEY || null;
if (key && key !== 'sk-placeholder') {
fastify.head("/", async (req, reply) => {
fastify.get("/", async (req, reply) => {
```

### Step 6: Start the proxy
```bash
ANTHROPIC_PROXY_BASE_URL=https://api.deepseek.com \
ANTHROPIC_PROXY_API_KEY=sk-e413574cdfdc470baa2f9a3283bee570 \
COMPLETION_MODEL=deepseek-chat \
PORT=3000 \
npx anthropic-proxy &
```

Or use the startup script `~/start-deepseek-proxy.sh`:
```bash
#!/bin/bash
source ~/.hermes/.env  # Contains DEEPSEEK_API_KEY
export ANTHROPIC_PROXY_BASE_URL=https://api.deepseek.com
export ANTHROPIC_PROXY_API_KEY=$DEEPSEEK_API_KEY
export COMPLETION_MODEL=deepseek-chat
export PORT=3000
exec npx anthropic-proxy
```

### Step 7: Create a wrapper script for Claude Code
Create `/home/dmin/.local/bin/claude`:
```bash
#!/bin/bash
ANTHROPIC_API_KEY=sk-placeholder ANTHROPIC_BASE_URL=http://localhost:3000 exec /home/dmin/.nvm/versions/node/v24.16.0/bin/claude "$@"
```

Make executable: `chmod +x /home/dmin/.local/bin/claude`

### Step 8: Add PATH to .bashrc
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

### Step 9: Test
```bash
# Direct test of proxy
curl -s --max-time 15 -X POST http://localhost:3000/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: sk-placeholder" \
  -H "anthropic-version: 2023-06-01" \
  -d '{"model":"deepseek-chat","max_tokens":50,"messages":[{"role":"user","content":"Say hi in 3 words"}]}'

# Test via wrapper
hash -r && claude -p "Say hi in 3 words"
# → Expected: "Hi there!" or similar
```

## Architecture

```
┌─────────────────┐        Anthropic Messages API        ┌──────────────────┐
│  Claude Code     │ ──────────────────────────────────▶ │ anthropic-proxy  │
│  (v2.1.148)      │ ◀────────────────────────────────── │ (port 3000)      │
│  "thinks" it     │                                      │ Translates fmt   │
│  talks to        │                                      └───────┬──────────┘
│  Anthropic       │                                              │
└─────────────────────────────────────────────────────────────────┤
                                                    OpenAI Chat Completions API
                                                              │
                                                              ▼
                                                   ┌──────────────────┐
                                                   │ api.deepseek.com │
                                                   │ (DeepSeek V4     │
                                                   │  Flash)          │
                                                   └──────────────────┘
```

## Daily Usage

```bash
# 1. Start proxy (if not running)
~/start-deepseek-proxy.sh &

# 2. Launch Claude Code
claude   # → Interactive TUI, uses DeepSeek model
# or
claude -p "task description" --max-turns 10
```

**No internet required for daily use** — DeepSeek (api.deepseek.com) is a domestic Chinese service.

## Proxy Lifecycle

### After Reboot: Full Restart Workflow
```bash
# 1. Check if proxy patches survived (npx cache may have been cleared)
head -20 ~/.npm/_npx/*/node_modules/anthropic-proxy/index.js
# Look for: fastify.head("/", ...
# If missing → re-install and re-patch (see Step 5)

# 2. Start proxy
source ~/.hermes/.env && \
ANTHROPIC_PROXY_BASE_URL=https://api.deepseek.com \
ANTHROPIC_PROXY_API_KEY="$DEEPSEEK_API_KEY" \
COMPLETION_MODEL=deepseek-chat \
PORT=3000 \
npx anthropic-proxy &

# 3. Verify
sleep 4 && curl -s http://localhost:3000/
# Expected: {"status":"ok","service":"anthropic-proxy"}

# 4. Use Claude Code
claude  # Interactive mode should work now
```

### Proxy Not Running Check
```bash
ps aux | grep anthropic-proxy | grep -v grep
# If empty: restart
```

## Current State (2026-05-22)

**Fully working.** Both `-p` mode and interactive TUI work with DeepSeek V4 Flash through anthropic-proxy.

The last missing piece was the `HEAD /` health-check route (Patch 3), without which interactive mode silently failed. All three patches now applied and stable.

Usage:
```bash
# Start proxy (one terminal)
nohup ~/start-deepseek-proxy.sh &

# In another terminal (or same, after ensuring proxy is running):
source ~/.bashrc
claude                 # → Interactive TUI with DeepSeek
claude -p "hello"      # → Single-query mode
```

### ❗ Wrapper Script vs Shell Function (CRITICAL — Learned 2026-05-22)

The wrapper script approach (Step 7) has a fatal flaw with nvm: **nvm's `bin/` directory is added to the FRONT of PATH**, so `~/.local/bin/claude` is always shadowed. `which claude` returns the nvm binary, not the wrapper. Shell hash caching makes this worse — even after `hash -r`, the nvm binary takes priority.

**DO NOT use wrapper scripts with nvm. Use a shell function instead.**

**Replace Steps 7-8 with this single `.bashrc` entry:**

```bash
# Add this to ~/.bashrc (single line):
claude() { ANTHROPIC_API_KEY=sk-placeholder ANTHROPIC_BASE_URL=http://localhost:3000 /home/dmin/.nvm/versions/node/v24.16.0/bin/claude "$@"; }
```

**Why shell functions win:**
- Override PATH lookups unconditionally (no shadowing possible)
- Immune to bash hash caching
- No file permission or symlink issues
- Variables in the function body are local and override inherited env vars

### Pitfall 1: Shell hash cache
After updating any `claude` configuration, `claude` in an existing terminal may still reference the old binary. Fix:
```bash
hash -r
# Or open a brand new terminal
```

### Pitfall 2: `.venv-hermes` environment variable conflict
Hermes Agent's virtual environment sets `ANTHROPIC_BASE_URL=http://localhost:4000/v1`. If you run `claude` inside the `.venv-hermes` terminal, this variable OVERRIDES the wrapper script's `ANTHROPIC_BASE_URL=http://localhost:3000`.

**Symptoms:** Claude Code tries to connect to `api.anthropic.com` despite wrapper script being correctly configured. `which claude` shows the wrapper, but `env | grep ANTHROPIC` shows port 4000.

**Fix:** Either:
- Exit the virtual environment: `deactivate`
- Start a brand new terminal session (not inside `.venv-hermes`)
- Or explicitly unset: `unset ANTHROPIC_BASE_URL` before running `claude`

### Pitfall 3: `ANTHROPIC_API_KEY` must exist (even fake)
Claude Code v2.1.148 refuses to start without `ANTHROPIC_API_KEY` set, even when using a proxy. The wrapper script uses a placeholder `sk-placeholder` — the proxy ignores it (thanks to Patch 2).

### Pitfall 5: Terminal paste breaks multiline commands with quotes

When users copy-paste multi-line commands with double quotes, the WSL terminal may split at visual line breaks (even if the command appears as one line in the response). Broken alias fragments (e.g., half of an `alias claude="..."` declaration) get written to `.bashrc` and corrupt the file.

**Symptoms:** 
- `.bashrc` has dangling quote fragments
- `source ~/.bashrc` fails with `unexpected EOF while looking for matching`
- The `alias` or function is truncated or missing parts

**Fix:**
```bash
# Remove broken alias line
sed -i '/alias claude=/d' ~/.bashrc  
# Remove dangling fragments (partial lines with paths)
sed -i '/^  \/home\/dmin\/\.nvm/d' ~/.bashrc
source ~/.bashrc
```

**Prevention:**
- Never use multi-line commands in response text (keep as single physical line)
- Prefer single quotes ('...') over double quotes ("...") to avoid escape confusion
- Better yet: write to files directly via the agent terminal tool rather than asking users to paste

### Pitfall 4: Proxy not running
Always check before running Claude Code:
```bash
ps aux | grep anthropic-proxy | grep -v grep
# If nothing, restart: ~/start-deepseek-proxy.sh &
```

## Dead Ends Recorded for Reference

These approaches were tried and failed, documented to prevent re-exploration:

### Dead End A: LiteLLM Proxy
- LiteLLM v1.85.1 installed, config created for DeepSeek
- LiteLLM exposes `/v1/messages` (Anthropic format) but route handling is broken with non-Anthropic models
- URL path duplication issue: `/v1/v1/chat/completions`
- `ANTHROPIC_BASE_URL` pointing at LiteLLM → Claude Code still reaches api.anthropic.com
- Conclusion: LiteLLM's Anthropic endpoint handler is designed for LiteLLM-managed models, not as a generic translation layer

### Dead End B: `ANTHROPIC_BASE_URL` alone (no proxy)
- Setting `ANTHROPIC_BASE_URL=http://localhost:4000` without a `provider:openai` settings flag → Claude Code ignores it
- **But** with `--settings '{"provider":"openai"}'` flag, it DOES work with anthropic-proxy (not LiteLLM)

### Dead End C: OpenCode fork
- [OpenCode](https://opencode.ai) is an open-source fork that supports OpenAI-compatible APIs natively
- Not a dead end per se — it IS a viable alternative — but the user chose to stay with official Claude Code + proxy

## Key Insight

The user's real goal was "an autonomous coding agent CLI that uses DeepSeek V4 Flash." The brand name "Claude Code" was a means, not the end. The anthropic-proxy bridge achieved this with the official Anthropic CLI, at the cost of a small translation layer and two source patches.

**The `ANTHROPIC_BASE_URL` + `provider:openai` combo works** — but ONLY with a proxy that properly translates Anthropic Messages API to OpenAI Chat Completions format. anthropic-proxy does this correctly; LiteLLM's Anthropic endpoint does not.
