<div align="right">

**English** | [中文](README.zh-CN.md)

</div>

<div align="center">

# Claude Code Memory & Reminder Skill

**Persistent tiered memory & reminder notebook for [Claude Code](https://claude.com/claude-code) and [OpenAI Codex CLI](https://github.com/openai/codex).**

So your assistant actually remembers what matters and gently reminds you of things you promised yourself.

[![ShellCheck](https://github.com/moyunliuyin/claude-memory-reminder/actions/workflows/shellcheck.yml/badge.svg)](https://github.com/moyunliuyin/claude-memory-reminder/actions/workflows/shellcheck.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/moyunliuyin/claude-memory-reminder)](https://github.com/moyunliuyin/claude-memory-reminder/releases)
[![Platforms](https://img.shields.io/badge/platforms-Claude%20Code%20%7C%20Codex%20CLI-blueviolet)](#install-for-codex-cli)

```bash
git clone https://github.com/moyunliuyin/claude-memory-reminder ~/.claude/skills/claude-memory-reminder
```

</div>

---

## Features

- **Tiered memory** — importance (H/M/L) × recency (vivid/distilled/archive); important configs stay fresh past 30 days, one-off noise drops out early
- **Scheduled triggers** — daily boundary check; monthly `verified` refresh (default: 1st); twice-monthly pattern extraction (default: 15th + last day)
- **Reminder notebook** — add / complete / cancel via natural language in chat ("remind me to X on May 10", "X done"); supports `[earliest:HH:MM]` for time-of-day gating
- **Multi-window dedup** — a cooldown stamp (default 8h) prevents repeated reports across parallel CLI windows; saves ~300–500 tokens per extra window
- **Zero dependencies at runtime** — the hook script uses only `bash` + `grep` + `date`. Local validation can optionally use Python and ShellCheck

## How it works

Every Claude Code session runs a `SessionStart` hook that either:

1. **REQUIRED** — first window in the cooldown window → Claude runs a tier-check report (boundary / verified / extraction / reminders) before answering your question.
2. **SKIP** — another window already did the report recently → Claude answers directly without the overhead.

The report is driven by rules in `MEMORY.md` (a tier policy + Startup Protocol) and condition entries in `reminders.md`.

## Install for Claude Code

### 1. Clone

```bash
git clone https://github.com/moyunliuyin/claude-memory-reminder ~/.claude/skills/claude-memory-reminder
```

(Use any local path; the hook auto-locates config via `CMR_SKILL_DIR` env var if you pick a non-default location.)

### 2. Deploy the hook

```bash
mkdir -p ~/.claude/hooks
cp ~/.claude/skills/claude-memory-reminder/hooks/session-start.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/session-start.sh
```

### 3. Register the hook in settings

Add this block under the top-level object in `~/.claude/settings.json` (merge with your existing keys):

```json
"hooks": {
  "SessionStart": [
    {
      "hooks": [
        { "type": "command", "command": "bash ~/.claude/hooks/session-start.sh" }
      ]
    }
  ]
}
```

> The installer script only prints these instructions — it does **not** modify `settings.json` automatically, to avoid breaking your existing config.

### 4. Initialize your project memory

```bash
TARGET="$HOME/.claude/projects/YOUR-PROJECT/memory"
mkdir -p "$TARGET"
cp ~/.claude/skills/claude-memory-reminder/templates/MEMORY.md "$TARGET/"
cp ~/.claude/skills/claude-memory-reminder/templates/reminders.md "$TARGET/"
```

Fill in `MEMORY.md` User Info / Preferences blocks.

### 5. (Optional) Customize parameters

```bash
cd ~/.claude/skills/claude-memory-reminder
cp config.example.json config.json
# Edit config.json to taste
```

### 6. Verify

Open a new Claude Code session. You should see Claude start with a tier-check report like:

```
[session-start] Today: 2026-04-20, Now: 10:47. REQUIRED: ...
Tier check:
  Boundary: no entries crossing lines
  Verified: all in-date
  Extraction: not due today
  Reminders (2): ⚠️ Today - annual check-up; 🔁 on-demand - try new memory system
Suggested: none
```

## Install for Codex CLI

Codex has no SessionStart hook → memory-reminder runs as a manual AGENTS.md "Session Startup" instruction (the main agent self-executes).

```bash
git clone https://github.com/moyunliuyin/claude-memory-reminder.git
cd claude-memory-reminder
bash install.sh codex
```

```powershell
git clone https://github.com/moyunliuyin/claude-memory-reminder.git
cd claude-memory-reminder
powershell -ExecutionPolicy Bypass -File .\install.ps1 -Target codex
```

The installer **only prints** manual steps; it does NOT modify your AGENTS.md.

Manual steps it tells you to do:

1. Copy the `## 1. Session Startup` block from [`codex/agents-md-startup-fragment.md`](codex/agents-md-startup-fragment.md) into your `~/.codex/AGENTS.md` section 1
2. Copy templates to codex memories dir:

   ```bash
   mkdir -p ~/.codex/memories
   cp templates/MEMORY.md ~/.codex/memories/MEMORY.md
   cp templates/reminders.md ~/.codex/memories/reminders.md
   ```

3. Fill in MEMORY.md User Info / Preferences

See [`codex/README.md`](codex/README.md) for the full guide and the CC-vs-Codex difference matrix.

> **Note**: Codex relies on the main agent self-executing the AGENTS.md instruction every session. The 8h cooldown is best-effort (some sessions may skip if the model doesn't comply). Claude Code's hook is stricter in this regard.

## Local validation

Run these from the repository root:

```bash
bash scripts/validate.sh
bash tests/test-session-start.sh
```

`validate.sh` checks required files, JSON syntax, shell syntax, and ShellCheck when available. The session-start test covers first-run `REQUIRED`, cooldown `SKIP`, and malformed-config fallback.

## Usage

Just talk naturally. Claude recognizes intent and updates the files:

| You say | Result |
|---------|--------|
| "Remind me to X on 2026-05-10" | `[due: 2026-05-10][active] X` added |
| "Remind me to X" | `[due: on-demand][active][created:TODAY] X` added |
| "On May 10 after 12:00 remind me X" | `[due: 2026-05-10][earliest:12:00][active] X` added |
| "Daily remind me X until done" | `[due: daily-until-done][active] X` |
| "X done" / "X sorted" | That reminder marked `done` |
| "Cancel X" | That reminder deleted |

## Config

All fields in `config.json` are optional (defaults in `config.example.json`):

```json
{
  "cooldown_hours": 8,
  "ondemand_timeout_days": 14,
  "verified_refresh_day": 1,
  "extract_days": [15, "last"],
  "boundary_days": { "vivid": 7, "distilled": 30 }
}
```

Only `cooldown_hours` is read by the hook itself (via regex). All other fields are read by Claude directly from the JSON when it runs the Startup Protocol.

## Uninstall

The uninstall scripts only print manual steps and never delete your `MEMORY.md` or `reminders.md` data:

```bash
bash uninstall.sh
# Windows PowerShell:
powershell -File uninstall.ps1
```

## Limitations

This skill injects structured startup/reminder context; it cannot force model compliance. Cooldown is local and file-based, so deleting `~/.claude/memory/.last-reminded` makes the next session run the full report again.

## Roadmap

- [ ] Optional "suspect-done" heuristic (method B): scan past-conversation events for soft completion signals
- [ ] Multi-project memory fan-out
- [ ] Web UI for browsing Recent Memory

## License

MIT — see [LICENSE](LICENSE).
