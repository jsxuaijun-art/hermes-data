#!/usr/bin/env bash
# SessionStart hook for claude-memory-reminder skill
# - Reads cooldown_hours from config.json via regex (no jq dependency)
# - First session in cooldown window: outputs REQUIRED (full check trigger)
# - Subsequent sessions within cooldown: outputs SKIP (saves ~300-500 tokens/window)

# Locate config: env override > skill-relative config.json > config.example.json
SKILL_DIR="${CMR_SKILL_DIR:-$HOME/.claude/skills/claude-memory-reminder}"
CONFIG_FILE="${CMR_CONFIG:-$SKILL_DIR/config.json}"
[ ! -f "$CONFIG_FILE" ] && CONFIG_FILE="$SKILL_DIR/config.example.json"

STAMP_FILE="${CMR_STAMP:-$HOME/.claude/memory/.last-reminded}"

# Zero-dependency regex parse of cooldown_hours (default 8)
COOLDOWN_HOURS=$(grep -oE '"cooldown_hours"[[:space:]]*:[[:space:]]*[0-9]+' "$CONFIG_FILE" 2>/dev/null \
    | grep -oE '[0-9]+$' \
    || true)
case "$COOLDOWN_HOURS" in
    ""|*[!0-9]*) COOLDOWN_HOURS=8 ;;
esac
COOLDOWN_SEC=$((COOLDOWN_HOURS * 3600))

NOW=$(date +%s)
TODAY=$(date +%Y-%m-%d)
NOW_HM=$(date +%H:%M)

mkdir -p "$(dirname "$STAMP_FILE")"

if [ -f "$STAMP_FILE" ]; then
    LAST=$(cat "$STAMP_FILE" 2>/dev/null || echo 0)
    DIFF=$((NOW - LAST))
    if [ "$DIFF" -lt "$COOLDOWN_SEC" ]; then
        MIN=$((DIFF / 60))
        echo "[session-start] Today: $TODAY, Now: $NOW_HM. SKIP: memory check done by another CLI ${MIN} min ago (${COOLDOWN_HOURS}h cooldown). Skip tier/reminder report, answer user directly."
        exit 0
    fi
fi

echo "$NOW" > "$STAMP_FILE"
echo "[session-start] Today: $TODAY, Now: $NOW_HM. REQUIRED: run memory tier check (boundary/verified/extraction/reminders) and output report before answering user."
