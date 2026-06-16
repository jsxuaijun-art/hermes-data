# Claude Code — Detailed CLI Reference

All the detailed CLI flags, subcommands, and patterns for Claude Code orchestration.

## Installation & Auth

```bash
npm install -g @anthropic-ai/claude-code
claude auth login --console          # API key billing
claude auth login --sso              # Enterprise SSO
claude doctor                         # health check
```

## Print Mode (`-p`) — Non-Interactive (PREFERRED)

```bash
claude -p "Add error handling to all API calls in src/" --allowedTools "Read,Edit" --max-turns 10
```

### Structured JSON Output
```bash
claude -p "Analyze auth.py" --output-format json --max-turns 5
```

Returns: `session_id`, `num_turns`, `total_cost_usd`, `subtype` (success/error).

### Piped Input
```bash
cat src/auth.py | claude -p "Review this code for bugs" --max-turns 1
git diff HEAD~3 | claude -p "Summarize these changes" --max-turns 1
```

### JSON Schema
```bash
claude -p "List all functions" --output-format json \
  --json-schema '{"type":"object","properties":{"functions":{"type":"array","items":{"type":"string"}}},"required":["functions"]}'
```

### Session Continuation
```bash
claude -p "Continue" --resume <session-id> --max-turns 5
claude -p "Resume last" --continue --max-turns 1
```

### Bare Mode (CI/Scripting)
```bash
claude --bare -p "Run all tests" --allowedTools "Read,Bash" --max-turns 10
```

## Key CLI Flags

| Flag | Effect |
|------|--------|
| `-p, --print` | Non-interactive one-shot |
| `-c, --continue` | Resume most recent session |
| `-r, --resume <id>` | Resume specific session |
| `--fork-session` | Create new session ID when resuming |
| `--model sonnet\|opus\|haiku` | Model selection |
| `--effort low\|medium\|high\|max\|auto` | Reasoning depth |
| `--max-turns <n>` | Cap agentic loops (print mode only) |
| `--max-budget-usd <n>` | Cap API spend (print mode) |
| `--dangerously-skip-permissions` | Auto-approve ALL tool use |
| `--allowedTools "Read,Edit"` | Whitelist specific tools |
| `--output-format text\|json\|stream-json` | Output format |
| `--bare` | Skip hooks, plugns, MCP, OAuth |
| `--from-pr <number>` | Resume linked to a PR |
| `--worktree [name]` | Isolated git worktree |

## Allowed Tools Syntax
```
Read                     # All file reading
Edit                     # File editing (existing files)
Write                    # File creation (new files)
Bash                     # All shell commands
Bash(git *)              # Only git commands
WebSearch                # Web search capability
```

## Interactive Mode (via tmux)

```bash
# Start session
tmux new-session -d -s claude-work -x 140 -y 40
tmux send-keys -t claude-work 'cd /project && claude' Enter

# Dialog handling: trust (Enter), permissions (Down+Enter)
sleep 5 && tmux send-keys -t claude-work Enter
sleep 3 && tmux send-keys -t claude-work Down && sleep 0.3 && tmux send-keys -t claude-work Enter

# Send task
tmux send-keys -t claude-work 'Refactor the auth module to use JWT tokens' Enter

# Monitor
tmux capture-pane -t claude-work -p -S -50

# Clean up
tmux kill-session -t claude-work
```

## Key Interactive Slash Commands
| Command | Purpose |
|---------|---------|
| `/compact [focus]` | Compress context to save tokens |
| `/clear` | Wipe conversation history |
| `/cost` | View token usage |
| `/review` | Request code review |
| `/plan` | Enter plan mode |
| `/model [model]` | Switch models |
| `/effort [level]` | Set reasoning effort |
| `/memory` | Open CLAUDE.md editing |
| `/exit` or Ctrl+D | End session |

## MCP Integration
```bash
claude mcp add -s user github -- npx @modelcontextprotocol/server-github
claude mcp add postgres -- npx @anthropic-ai/server-postgres --connection-string ...
claude mcp list
```

## Settings Hierarchy
1. CLI flags (highest)
2. `.claude/settings.local.json` (personal, gitignored)
3. `.claude/settings.json` (shared, git-tracked)
4. `~/.claude/settings.json` (global)

## CLAUDE.md
Auto-loaded from project root. Use for persistent project context.
```
~/.claude/CLAUDE.md                          # global, all projects
./CLAUDE.md                                   # project-specific
.claude/CLAUDE.local.md                       # personal overrides
.claude/rules/*.md                            # modular rules
```
