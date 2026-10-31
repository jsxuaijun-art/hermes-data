# Claude Code Memory (Template)

> Generated from the `claude-memory-reminder` skill.
> Fill in your own info and preferences below, then delete these instructions.

## User Info
- OS:
- Username:
- Primary language:

## Preferences
<!-- e.g. "Code style rules defined in: ~/.claude/CLAUDE.md" -->
<!-- e.g. links to your per-topic feedback files -->

## Memory Policy

### Startup Protocol
- Every session, the SessionStart hook (`~/.claude/hooks/session-start.sh`) injects one of:
  - `[session-start] Today: YYYY-MM-DD, Now: HH:MM. REQUIRED: ...` → run full checks
  - `[session-start] Today: YYYY-MM-DD, Now: HH:MM. SKIP: ...` → **skip all checks**, answer user directly (another CLI did the work within cooldown)
- **On REQUIRED: first-turn reply MUST start with the tier-check report**, containing:
  1. Boundary status today (any entry crossing 7 / 30-day line → suggest move/archive)
  2. If today is **`verified_refresh_day`** (default: 1st of month) → full `[H]` verified refresh (list and ask user to confirm still-in-use)
  3. If today is in **`extract_days`** (default: 15th + last day of month) → trigger pattern extraction → `patterns.md` / `user_interaction_patterns.md`
  4. **Read `reminders.md`**: today-due (⚠️), overdue (🔴), upcoming within 3 days (📅), on-demand persistent; on-demand older than **`ondemand_timeout_days`** (default 14) without `done` → add ❓ "still on your list?"; if entry has `[earliest:HH:MM]` and current `Now < earliest` → keep silent (not yet due). Archive `done` / `expired` per tier rules.
  5. Suggested actions; if everything is fine, a one-liner "tiering OK, no adjustment needed".
- Only AFTER the report, address the user's actual question.

### Importance tiers (H / M / L)
| Tag | Meaning | Examples |
|-----|---------|----------|
| **[H]** | high — active configs, core commands, infra | API tokens, relay endpoints, infra paths |
| **[M]** | mid — lessons, non-critical configs, analyses | incidents, billing rules, habit analysis |
| **[L]** | low — one-off tasks, archived items | acceptance records, resolved old bugs |

**Importance overrides recency**: `[H]` stays in "vivid" past 30 days; `[L]` may drop early.

### Recency tiers
| Tier | Window | Handling |
|------|--------|----------|
| **Vivid** | within `boundary_days.vivid` (default 7) + ALL `[H]` | full detail, actively linked in context |
| **Distilled** | between vivid and distilled (default 7–30) for `[M]` | compressed one-liner |
| **Archive / Forget** | past `boundary_days.distilled` for `[M]`/`[L]` | archive per judgement or delete |

### verified field
- Only `[H]` config-type entries need `✓verified:YYYY-MM-DD`
- Monthly on `verified_refresh_day` → full review; user confirms still-in-use → update date to today

### 30-day+ judgement
**Keep (archive to `archive.md`)**:
- Configs / paths / architectural decisions still in use
- User-declared preferences / habits
- Unresolved issues (mark status)

**Forget (delete)**:
- One-off tasks (install, test, homework)
- Configs superseded by newer entries
- Debugging breadcrumbs (keep conclusion only)
- Intermediate steps of already-resolved issues

### Format
- Prefix: `[YYYY-MM-DD][H/M/L]`
- `[H]` configs end with `✓verified:YYYY-MM-DD`
- Vivid: multi-line with context
- Distilled: one-liner
- Archive: grouped by topic in `archive.md`

### Periodic maintenance
- On each day in `extract_days` (default 15th + last day of month), scan Recent Memory:
  1. Recurring topics → `patterns.md`
  2. User habits & preferences → `user_interaction_patterns.md` (+ Preferences above)
  3. High-frequency functions → `patterns.md`
- Last-day detection: if "tomorrow = 1st of next month" then today is the last.

### Reminders management
- User intent recognition (auto-write to `reminders.md`):
  - **Add**: "remind me X" / "记得提醒我 X" → `on-demand` · "X on YYYY-MM-DD" / "X 月 Y 日 Z" → dated · "daily until done" → `daily-until-done`
  - **Complete** (method-A strong signals): "X done / finished / sorted / wrapped up" / "搞定/做完/完成/处理完/弄好/解决/办好/结了 X" → mark `done`
  - **Cancel**: "cancel X / drop X" / "X 不做了/取消/算了/跳过" → delete
- Archive: `done` / `expired` / cancelled → per tier rules (`[L]` delete / `[M]` keep if reference value)
- Multi-window dedup: `cooldown_hours` (default 8) controls the skip window

## Topic Index
<!-- Reverse index, e.g. -->
<!-- | Topic | Related entries | -->
<!-- | #infra | YYYY-MM-DD item A [H], ... | -->

## Recent Memory

### Vivid (within 7 days + all [H])
<!-- [YYYY-MM-DD][H/M/L] content ... ✓verified:YYYY-MM-DD -->

### Distilled (7–30 days)
<!-- [YYYY-MM-DD][M] one-line summary ... -->

### Long-term
See `archive.md`.
