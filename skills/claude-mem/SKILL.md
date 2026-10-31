---
name: claude-memory-reminder
description: |
  Persistent tiered memory and reminder notebook for Claude Code.
  On every session start, runs memory boundary check, verified refresh (monthly), and pattern extraction (twice monthly). Multi-window dedup via an 8h cooldown stamp. Recognizes natural language in chat to auto-add/complete/cancel reminders.
  为 Claude Code 提供持久化分级记忆与提醒记事本。每次会话启动自动触发边界检查、verified 月度复查、月度模式提取；多窗口去重；识别对话中的用户意图自动增删改提醒条目。
---

# Claude Code Memory & Reminder Skill

## When to trigger / 触发场景

- User says "remember X" / "remind me Y" / "提醒我 X" / "X 月 Y 日 Z" → auto-write to `reminders.md`
- User says "X done / finished / sorted" / "搞定了/做完了/完成了 X" → mark that reminder as `done`
- User says "cancel X" / "X 不做了/取消/算了" → delete that reminder
- Session start (SessionStart hook injects `[session-start] Today/Now`) → run Startup Protocol

## Files / 关键文件

| File | Purpose |
|------|---------|
| `hooks/session-start.sh` | Hook; outputs `Today`/`Now` + `REQUIRED`/`SKIP` based on cooldown |
| `templates/MEMORY.md` | Memory rule skeleton (tiering, Startup Protocol, Reminders management) |
| `templates/reminders.md` | Reminder notebook skeleton |
| `config.example.json` | User-overridable parameters (cooldown/timeouts/trigger days) |
| `scripts/validate.sh` | Local structure, JSON, shell syntax, and optional ShellCheck validation |
| `tests/test-session-start.sh` | Local smoke test for REQUIRED/SKIP cooldown behavior |

## Core rules / 核心规则

### Tiering — importance × recency
| Importance | Meaning |
|------------|---------|
| `[H]` | high — active configs, commands, infra |
| `[M]` | mid — lessons, conclusions, non-critical configs |
| `[L]` | low — one-off tasks, already-archived items |

Importance **overrides** recency: `[H]` stays in "vivid" tier even past 30 days; `[L]` can drop out early.

### Scheduled triggers
- **Every month 1st** → verified refresh (列所有 `[H]` 让用户确认 still-in-use)
- **Every month 15th + last day** → pattern extraction (recurring topics → `patterns.md`)
- **Every session start** → boundary check (条目跨 7/30 天线时建议 move/archive)

### Reminders
- `[due: YYYY-MM-DD]` / `[due: YYYY-MM-DD][earliest:HH:MM]` / `[due: on-demand][created:YYYY-MM-DD]` / `[due: daily-until-done]`
- 14 天 on-demand 未 done → `❓` 问询
- done / expired / cancelled → archive per tier rules

### Multi-window dedup
First session in cooldown window → full report and writes a stamp file. Subsequent sessions within `cooldown_hours` (default 8) → `SKIP` output; Claude answers directly without running checks.

## Install

See `README.md` / `README.zh-CN.md`.

## Local validation

```bash
bash scripts/validate.sh
bash tests/test-session-start.sh
```

## Config (all optional)

```json
{
  "cooldown_hours": 8,
  "ondemand_timeout_days": 14,
  "verified_refresh_day": 1,
  "extract_days": [15, "last"],
  "boundary_days": { "vivid": 7, "distilled": 30 }
}
```

## Zero-dependency constraint / 零依赖

The hook script uses only POSIX `bash` + `grep` + `date`. `jq` is **not** required — `cooldown_hours` is parsed via regex. All other config fields are interpreted by Claude directly reading the JSON.

## Limitations / 限制

This skill injects structured startup/reminder context; it cannot force model compliance. Cooldown is local and file-based, so deleting the stamp file makes the next session run the full report again.
