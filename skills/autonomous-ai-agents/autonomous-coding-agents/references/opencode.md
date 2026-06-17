# OpenCode CLI — Quick Reference

Open-source, provider-agnostic AI coding agent.

## Installation

```bash
npm i -g opencode-ai@latest   # or brew install anomalyco/tap/opencode
opencode auth login
```

## Commands

| Flag | Effect |
|------|--------|
| `run 'prompt'` | One-shot execution and exit (NO pty needed) |
| `-c / --continue` | Continue last session |
| `-s <id>` | Continue specific session |
| `--model provider/model` | Force specific model |
| `-f <path>` | Attach file to message |
| `--thinking` | Show model thinking blocks |
| `--format json` | Machine-readable output |

## One-Shot (no pty needed)

```bash
opencode run 'Add retry logic to API calls and update tests'
opencode run 'Review this config' -f config.yaml -f .env.example
opencode run 'Refactor auth module' --model openrouter/anthropic/claude-sonnet-4
```

## Interactive (background, pty=true)

```bash
terminal(command="opencode", workdir="~/project", background=true, pty=true)
process(action="submit", session_id="<id>", data="Implement OAuth refresh flow")
process(action="poll", session_id="<id>")
```

Exit: `process(action="write", data="\x03")` — NEVER use `/exit`.

## PR Review

```bash
opencode pr 42
```

## Session & Cost

```bash
opencode session list
opencode stats
opencode stats --days 7 --models anthropic/claude-sonnet-4
```

## Key Pitfalls

- `opencode run` does NOT need pty (it's non-interactive). Only the TUI needs pty.
- `/exit` is NOT a valid command — opens agent selector instead. Use Ctrl+C.
- PATH mismatch can select wrong binary. Check with `which -a opencode`.
- Enter may need to be pressed twice to submit in TUI.
