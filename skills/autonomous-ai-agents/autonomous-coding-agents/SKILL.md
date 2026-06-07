---
name: autonomous-coding-agents
description: "Delegate coding to external autonomous coding agents (Claude Code, Codex CLI, OpenCode) via Hermes terminal — implement features, review PRs, refactor code, and run batch fixes through any supported CLI coding agent."
version: 1.0.0
author: Hermes Skill Curator
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [coding-agents, claude-code, codex, opencode, orchestration, autonomous-coding, delegation]
    related_skills: [hermes-agent, kanban, subagent-driven-development]
---

# Autonomous Coding Agents — Hermes Orchestration Guide

Delegate coding tasks to external autonomous coding agent CLIs: **Claude Code** (Anthropic), **Codex CLI** (OpenAI), and **OpenCode** (open-source / provider-agnostic). Each has its own install, auth, and flag set, but the Hermes orchestration pattern is the same.

## When to use this skill

Use any of these agent CLIs when:
- User asks to delegate a coding task to an external AI coding agent
- Building features, refactoring, PR reviews, or batch issue fixing
- You need parallel work across multiple issues/worktrees
- Claude Code, Codex, or OpenCode are explicitly requested

## Prerequisites (all agents)

- **Git repository** — all three agents refuse to run outside a git directory. Use `mktemp -d && git init` for scratch work.
- **PTY mode** — interactive TUI sessions require `pty=true`. One-shot modes (`-p`, `exec`, `run`) do NOT need pty.
- **CLI installed** — see the per-agent installation section below.

## Common Orchestration Patterns

These patterns work for all three agents. See each agent's section for exact CLI syntax.

### One-Shot Task

```bash
# Claude Code (preferred for single tasks)
claude -p "Add retry logic to API calls" --allowedTools "Read,Edit" --max-turns 10

# Codex CLI
codex exec "Add dark mode toggle to settings"

# OpenCode
opencode run "Add retry logic to API calls and update tests"
```

### Interactive Multi-Turn (requires tmux for Claude Code, background PTY for OpenCode/Codex)

```bash
# Start agent
tmux new-session -d -s coding-agent -x 140 -y 40
tmux send-keys -t coding-agent 'cd ~/project && claude' Enter

# Handle dialogs, send prompts
tmux send-keys -t coding-agent 'Refactor the auth module to use JWT' Enter

# Monitor
sleep 30 && tmux capture-pane -t coding-agent -p -S -50

# Clean up
tmux kill-session -t coding-agent
```

### Parallel Work (Issue Batching)

```bash
# Create worktrees
git worktree add -b fix/issue-78 /tmp/issue-78 main

# Launch agents in parallel
# (one terminal call per agent, background=true)
terminal(command="claude -p 'Fix issue #78' --allowedTools 'Read,Edit,Write,Bash' --max-turns 10", workdir="/tmp/issue-78")

# After all complete, push and create PRs, then clean up
git worktree remove /tmp/issue-78
```

### PR Review

```bash
# Simple diff review
git diff main...feature | claude -p "Review this diff for bugs and security issues" --max-turns 1

# Or using agent's PR subcommand
opencode pr 42
```

## Per-Agent Installation & Setup

### Claude Code (Anthropic)

**Install:** `npm install -g @anthropic-ai/claude-code`

**Auth options:**
- OAuth: run `claude` once to log in
- API key: set `ANTHROPIC_API_KEY`
- Console: `claude auth login --console`

**Version check:** `claude --version` (requires v2.x+)

**Health check:** `claude doctor`

**Two modes:**
1. **Print mode (`-p`):** one-shot, no PTY needed, returns JSON. Use `--output-format json` for structured results.
2. **Interactive:** full TUI via tmux. Required for multi-turn work with slash commands.

**Key flags:**
| Flag | Effect |
|------|--------|
| `-p "task"` | Print mode (one-shot, exits when done) |
| `--max-turns <n>` | Cap agentic loops (print mode only) |
| `--allowedTools "Read,Edit"` | Whitelist specific tools |
| `--dangerously-skip-permissions` | Auto-approve ALL tool use |
| `--output-format json` | Structured JSON result |
| `--model sonnet\|opus\|haiku` | Model selection |
| `--bare` | Skip hooks/plugins/MCP/OAuth (fastest) |
| `--continue` / `--resume <id>` | Continue/resume a session |
| `--from-pr <number>` | Resume session linked to a GitHub PR |

**Dialog handling (interactive mode):**
- Trust dialog: press Enter (default "Yes")
- Permissions dialog: DOWN then Enter

**Key pitfalls:**
- Interactive mode REQUIRES tmux for reliable monitoring
- `--max-budget-usd` minimum ~$0.05
- `--json-schema` needs enough `--max-turns` to read files first
- Background tmux sessions persist — always clean up

### Codex CLI (OpenAI)

**Install:** `npm install -g @openai/codex`

**Auth:** Either `OPENAI_API_KEY` env var or Codex OAuth (`~/.codex/auth.json`)

**One-shot:** `codex exec "prompt"`

**Key flags:**
| Flag | Effect |
|------|--------|
| `exec "prompt"` | One-shot execution, exits when done |
| `--full-auto` | Sandboxed, auto-approves file changes |
| `--yolo` | No sandbox, no approvals (fastest) |

**PR review pattern:** clone to temp dir, checkout PR, run `codex review --base origin/main`

**Key pitfall:** Always use `pty=true` — Codex is an interactive TUI app and hangs without a PTY.

### OpenCode (open-source, provider-agnostic)

**Install:** `npm i -g opencode-ai@latest` or `brew install anomalyco/tap/opencode`

**Auth:** `opencode auth login` or set provider env vars (`OPENROUTER_API_KEY`, etc.)

**One-shot:** `opencode run 'prompt'` (NO pty needed)

**Interactive:** `opencode` with `background=true, pty=true`, then `process(action="submit")` for input

**Key flags:**
| Flag | Effect |
|------|--------|
| `run 'prompt'` | One-shot execution and exit |
| `-c / --continue` | Continue last session |
| `-s <id>` | Continue specific session |
| `--model provider/model` | Force specific model |
| `-f <path>` | Attach file to message |
| `--thinking` | Show model thinking blocks |

**Exit interactive:** Ctrl+C (`\x03`) — do NOT use `/exit` (opens agent selector instead).

**Key pitfall:** Shell PATH may resolve wrong binary — use `which -a opencode` to check.

## Agent Comparison

| Feature | Claude Code | Codex CLI | OpenCode |
|---------|-------------|-----------|----------|
| **One-shot (no pty)** | `-p "task"` | `exec "task"` | `run "task"` |
| **Structured JSON output** | `--output-format json` | Partial | `--format json` |
| **PR review** | `git diff \| claude -p ...` | `codex review` | `opencode pr <n>` |
| **Interactive TUI** | tmux orchestration | pty=true | pty=true |
| **Model control** | `--model sonnet/opus/haiku` | Single model | `--model provider/model` |
| **Scratch work** | `mktemp -d && git init` | `mktemp -d && git init` | `mktemp -d && git init` |
| **Git required** | Yes | Yes | Yes |
| **Provider** | Anthropic only | OpenAI only | Any (OpenRouter, etc.) |
| **Windows support** | Yes | Yes | Yes |

## Monitoring & Lifecycle

- **One-shot:** terminal returns when done. JSON output includes `session_id`, `num_turns`, `total_cost_usd`.
- **Interactive (tmux):** use `tmux capture-pane -t <session> -p -S -50` to check progress. Look for `❯` prompt (waiting for input) vs `●` lines (actively working).
- **Background process:** use `process(action="poll")`, `process(action="log")`, `process(action="kill")`.

## Known Pitfalls

1. **All agents** require a git repository — use `mktemp -d && git init` for scratch projects.
2. **Shared workdir + parallel agents** will collide — always use separate worktrees or temp dirs.
3. **Context degradation** — Claude Code quality drops above 70% context. Use `/compact` or fresh sessions.
4. **Cost tracking** — Claude Code's `--output-format json` includes `total_cost_usd`. OpenCode has `opencode stats`. Codex has no built-in cost reporting.
5. **Always clean up** — kill tmux sessions and remove worktrees when done to avoid resource leaks.
6. **Slash commands** (`/review`, `/compact`) only work in interactive mode, never in one-shot mode.
