#!/usr/bin/env bash
# uninstall.sh - Prints manual uninstall steps

cat <<'EOF'
===========================================
 Claude Memory & Reminder Skill - Uninstall
===========================================

Run the following manually:

  # 1. Remove the hook script
  rm -f ~/.claude/hooks/session-start.sh

  # 2. Remove the cooldown stamp file
  rm -f ~/.claude/memory/.last-reminded

  # 3. Edit ~/.claude/settings.json and remove the "hooks" block
  #    (or just the "SessionStart" entry if you have other hooks)

  # 4. (Optional) Delete this skill directory
  #    rm -rf ~/.claude/skills/claude-memory-reminder

Your MEMORY.md / reminders.md files stay untouched - they are your data.

EOF
