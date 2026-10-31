#!/usr/bin/env bash
# install.sh - Prints setup instructions (no automatic modifications)

set -u

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET="${1:-claude}"

case "$TARGET" in
  claude|cc)
    cat <<EOF
===========================================
 Claude Memory & Reminder Skill — Installer (Claude Code)
===========================================

This script only prints manual steps. It will NOT modify your
~/.claude/settings.json automatically (to avoid breaking other config).

Skill location: $SKILL_DIR

-------------------------------------------
Step 1. Deploy the hook script
-------------------------------------------

  mkdir -p ~/.claude/hooks
  cp "$SKILL_DIR/hooks/session-start.sh" ~/.claude/hooks/
  chmod +x ~/.claude/hooks/session-start.sh

-------------------------------------------
Step 2. Register the hook in ~/.claude/settings.json
-------------------------------------------

Add this block under the top-level object (merge with existing keys):

  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          { "type": "command", "command": "bash ~/.claude/hooks/session-start.sh" }
        ]
      }
    ]
  }

If you already have a "hooks" key, merge SessionStart into its array.

-------------------------------------------
Step 3. Initialize a project's memory folder
-------------------------------------------

  TARGET="\$HOME/.claude/projects/YOUR-PROJECT/memory"
  mkdir -p "\$TARGET"
  cp "$SKILL_DIR/templates/MEMORY.md" "\$TARGET/"
  cp "$SKILL_DIR/templates/reminders.md" "\$TARGET/"

Then fill in User Info / Preferences in MEMORY.md.

-------------------------------------------
Step 4. (Optional) Customize parameters
-------------------------------------------

  cp "$SKILL_DIR/config.example.json" "$SKILL_DIR/config.json"
  # Edit config.json:
  #   cooldown_hours, ondemand_timeout_days, verified_refresh_day,
  #   extract_days, boundary_days

-------------------------------------------
Step 5. Verify
-------------------------------------------

Start a new Claude Code session. Claude should print a tier-check report
before answering your first message.

EOF
    ;;
  codex)
    cat <<EOF
===========================================
 Memory & Reminder — Installer (Codex CLI)
===========================================

Codex has NO SessionStart hook, so this skill works as an AGENTS.md
"Session Startup" instruction that the main agent executes itself.

Skill location: $SKILL_DIR

-------------------------------------------
Step 1. Add the startup fragment to AGENTS.md
-------------------------------------------

Open this file:

  $SKILL_DIR/codex/agents-md-startup-fragment.md

Copy its '## 1. Session Startup' block into your ~/.codex/AGENTS.md
section 1. If your AGENTS.md does not have a section 1 yet, insert
the entire block.

-------------------------------------------
Step 2. Deploy memory templates
-------------------------------------------

  mkdir -p ~/.codex/memories
  cp "$SKILL_DIR/templates/MEMORY.md" ~/.codex/memories/MEMORY.md
  cp "$SKILL_DIR/templates/reminders.md" ~/.codex/memories/reminders.md

Fill in MEMORY.md User Info / Preferences blocks.

-------------------------------------------
Step 3. Verify
-------------------------------------------

Start a new codex session. The main agent should:
  - First time (no stamp): print full tier-check REQUIRED report
  - Within 8h: print one-line SKIP and answer directly
  - After 8h: REQUIRED again

See $SKILL_DIR/codex/README.md for full details and the difference
matrix vs Claude Code.

EOF
    ;;
  hermes)
    cat <<EOF
Hermes platform support is not yet implemented (TODO for v0.3.0).
Hermes lacks a public SessionStart hook mechanism. If you have details
on how to inject a startup instruction in your Hermes deployment,
please open an issue at:

  https://github.com/moyunliuyin/claude-memory-reminder/issues

EOF
    exit 1
    ;;
  *)
    echo "Usage: $0 [claude|codex|hermes]" >&2
    echo "  claude   -> Claude Code installer (default)" >&2
    echo "  codex    -> Codex CLI installer (AGENTS.md fragment + templates)" >&2
    echo "  hermes   -> Not yet implemented (TODO v0.3.0)" >&2
    exit 1
    ;;
esac
