# Codex CLI — Quick Reference

OpenAI's autonomous coding agent CLI.

## Installation

```bash
npm install -g @openai/codex
```

Auth: `OPENAI_API_KEY` env var or Codex OAuth (`~/.codex/auth.json`).

## Commands

| Flag | Effect |
|------|--------|
| `exec "prompt"` | One-shot execution and exit |
| `--full-auto` | Sandboxed, auto-approves file changes |
| `--yolo` | No sandbox, no approvals (fastest) |

## One-Shot

```bash
codex exec "Add dark mode toggle to settings"
```

## Background Mode (Long Tasks)

```bash
terminal(command="codex exec --full-auto 'Refactor the auth module'", workdir="~/project", background=true, pty=true)
# Monitor with process(action="poll"|"log")
# Send input: process(action="submit", data="yes")
```

## PR Review

Clone to temp dir:
```bash
REVIEW=$(mktemp -d)
git clone https://github.com/user/repo.git $REVIEW
cd $REVIEW && gh pr checkout 42
codex review --base origin/main
```

## Key Pitfalls

- **Always use `pty=true`** for interactive TUI sessions
- **Git repo required** — use `mktemp -d && git init` for scratch work
- **Scratch work:** `cd $(mktemp -d) && git init && codex exec 'Build a snake game'`
