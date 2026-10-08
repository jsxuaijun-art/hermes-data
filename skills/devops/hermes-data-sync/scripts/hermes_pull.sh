#!/usr/bin/env bash
# ============================================================
# hermes_pull.sh — 跨机通用的 Hermes 拉取全流程(WSL 内执行)
# 2026-08-07 固化. 由 Hermes同步-拉取.bat 调用, .bat 只做:
#    wsl -d Ubuntu -- bash ~/.hermes/skills/devops/hermes-data-sync/scripts/hermes_pull.sh
# 流程: 探测同步夹 → git fetch+reset → rsync 同步夹→WSL ~/.hermes/
# ============================================================

set -u
SKILL_DIR="$HOME/.hermes/skills/devops/hermes-data-sync"
PATH_SCRIPT="$SKILL_DIR/scripts/hermes_sync_path.sh"

# --- 0) 探测同步夹 ---
eval "$(bash "$PATH_SCRIPT" 2>/dev/null)"
if [ -z "${HERMES_SYNC_DIR:-}" ] || [ ! -d "$HERMES_SYNC_DIR/.git" ]; then
  echo "[ERROR] Could not detect Hermes sync dir."
  exit 2
fi
echo "[path] Sync dir = $HERMES_SYNC_DIR"

# --- 1) git fetch + reset (对齐远端) ---
echo "[1] git fetch + reset ..."
cd "$HERMES_SYNC_DIR" || { echo "[ERROR] cd failed"; exit 2; }
git fetch origin main
if [ $? -ne 0 ]; then
  echo "[ERROR] git fetch failed - check network."
  exit 2
fi
git reset --hard origin/main
echo "[OK]"

# --- 2) rsync 同步夹 -> WSL ~/.hermes/ (skills 去 --delete) ---
echo "[2] rsync sync dir -> WSL ..."
mkdir -p ~/.hermes/memories ~/.hermes/skills
rsync -a "$HERMES_SYNC_DIR"/SOUL*.md ~/.hermes/ 2>/dev/null
rsync -a "$HERMES_SYNC_DIR"/config.yaml ~/.hermes/ 2>/dev/null
rsync -a "$HERMES_SYNC_DIR"/memories/ ~/.hermes/memories/ 2>/dev/null
rsync -a "$HERMES_SYNC_DIR"/skills/ ~/.hermes/skills/ 2>/dev/null
echo "[OK]"

echo "[VERIFY]"
echo -n "  wechat-publish: " && grep 'version:' ~/.hermes/skills/wechat-publish/SKILL.md 2>/dev/null || echo '(not found)'
echo -n "  short-video:    " && grep 'version:' ~/.hermes/skills/social-media/short-video-copywriting/SKILL.md 2>/dev/null || echo '(not found)'

echo "[DONE] Hermes synced from GitHub."
