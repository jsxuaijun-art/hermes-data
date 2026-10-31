#!/usr/bin/env bash
set -u

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
STATUS=0

require_file() {
    if [ ! -f "$ROOT_DIR/$1" ]; then
        printf 'missing: %s\n' "$1"
        STATUS=1
    fi
}

for file in \
    SKILL.md \
    README.md \
    README.zh-CN.md \
    hooks/session-start.sh \
    install.sh \
    install.ps1 \
    uninstall.sh \
    uninstall.ps1 \
    config.example.json \
    templates/MEMORY.md \
    templates/reminders.md
do
    require_file "$file"
done

if command -v python >/dev/null 2>&1; then
    python -m json.tool "$ROOT_DIR/config.example.json" >/dev/null || STATUS=1
elif command -v python3 >/dev/null 2>&1; then
    python3 -m json.tool "$ROOT_DIR/config.example.json" >/dev/null || STATUS=1
else
    printf 'skip: python not found, cannot validate config.example.json\n'
fi

for script in hooks/session-start.sh install.sh uninstall.sh scripts/validate.sh tests/test-session-start.sh; do
    if [ -f "$ROOT_DIR/$script" ]; then
        bash -n "$ROOT_DIR/$script" || STATUS=1
    fi
done

if command -v shellcheck >/dev/null 2>&1; then
    shellcheck "$ROOT_DIR/hooks/session-start.sh" "$ROOT_DIR/install.sh" "$ROOT_DIR/uninstall.sh" "$ROOT_DIR/scripts/validate.sh" "$ROOT_DIR/tests/test-session-start.sh" || STATUS=1
else
    printf 'skip: shellcheck not found\n'
fi

exit "$STATUS"
