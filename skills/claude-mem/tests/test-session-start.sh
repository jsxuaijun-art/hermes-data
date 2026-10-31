#!/usr/bin/env bash
set -u

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

run_hook() {
    HOME="$TMP_DIR/home" \
    CMR_SKILL_DIR="$ROOT_DIR" \
    CMR_CONFIG="$1" \
    CMR_STAMP="$TMP_DIR/stamp" \
    bash "$ROOT_DIR/hooks/session-start.sh"
}

mkdir -p "$TMP_DIR/home"
GOOD_CONFIG="$TMP_DIR/config.json"
BAD_CONFIG="$TMP_DIR/bad-config.json"

printf '{ "cooldown_hours": 8 }\n' > "$GOOD_CONFIG"
printf '{ "cooldown_hours": "bad" }\n' > "$BAD_CONFIG"

FIRST_OUTPUT="$(run_hook "$GOOD_CONFIG")"
case "$FIRST_OUTPUT" in
    *REQUIRED*) ;;
    *) printf 'expected REQUIRED on first run, got: %s\n' "$FIRST_OUTPUT"; exit 1 ;;
esac

SECOND_OUTPUT="$(run_hook "$GOOD_CONFIG")"
case "$SECOND_OUTPUT" in
    *SKIP*) ;;
    *) printf 'expected SKIP on cooldown hit, got: %s\n' "$SECOND_OUTPUT"; exit 1 ;;
esac

rm -f "$TMP_DIR/stamp"
BAD_OUTPUT="$(run_hook "$BAD_CONFIG")"
case "$BAD_OUTPUT" in
    *REQUIRED*) ;;
    *) printf 'expected REQUIRED with malformed config fallback, got: %s\n' "$BAD_OUTPUT"; exit 1 ;;
esac
