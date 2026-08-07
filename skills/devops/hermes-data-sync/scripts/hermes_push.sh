#!/usr/bin/env bash
# ============================================================
# hermes_push.sh — 跨机通用的 Hermes 推送全流程(WSL 内执行)
# 2026-08-07 固化. 由 Hermes同步-推送.bat 调用, .bat 只做:
#    wsl -d Ubuntu -- bash ~/.hermes/skills/devops/hermes-data-sync/scripts/hermes_push.sh
# 本脚本内部无 .bat 转义地狱, 变量正常。
# 流程: 探测同步夹 → rsync WSL→同步夹 → git pull/rebase → sync_guard防删 → commit → push
# ============================================================

set -u
SKILL_DIR="$HOME/.hermes/skills/devops/hermes-data-sync"
PATH_SCRIPT="$SKILL_DIR/scripts/hermes_sync_path.sh"
GUARD_SCRIPT="$SKILL_DIR/scripts/sync_guard.sh"

# --- 0) 探测同步夹 ---
eval "$(bash "$PATH_SCRIPT" 2>/dev/null)"
if [ -z "${HERMES_SYNC_DIR:-}" ] || [ ! -d "$HERMES_SYNC_DIR/.git" ]; then
  echo "[ERROR] Could not detect Hermes sync dir."
  exit 2
fi
echo "[path] Sync dir = $HERMES_SYNC_DIR"

# --- 1) rsync WSL -> 同步夹 (skills 去 --delete 防误删) ---
echo "[1] rsync WSL -> sync dir ..."
mkdir -p "$HERMES_SYNC_DIR/memories" "$HERMES_SYNC_DIR/skills"
rsync -a ~/.hermes/SOUL*.md "$HERMES_SYNC_DIR/" 2>/dev/null
rsync -a ~/.hermes/config.yaml "$HERMES_SYNC_DIR/" 2>/dev/null
rsync -a ~/.hermes/memories/ "$HERMES_SYNC_DIR/memories/" 2>/dev/null
rsync -a --exclude='.curator_backups/' --exclude='gstack/*/dist/' --exclude='*.tar.gz' --exclude='*.tar' \
  ~/.hermes/skills/ "$HERMES_SYNC_DIR/skills/" 2>/dev/null
echo "[OK]"

# --- 2) git pull --rebase (同步远端) ---
echo "[2] git pull --rebase ..."
cd "$HERMES_SYNC_DIR" || { echo "[ERROR] cd failed"; exit 2; }
git stash 2>/dev/null
git pull --rebase origin main 2>&1
# 自动解决 rebase 冲突(仅 __pycache__ 等噪音用 ours)
if [ -f .git/MERGE_MSG ] || [ -d .git/rebase-apply ] || [ -d .git/rebase-merge ]; then
  echo "[INFO] Auto-resolving rebase conflicts..."
  find . -path '*__pycache__*' -delete 2>/dev/null
  git checkout --ours -- . 2>/dev/null
  git rebase --skip 2>/dev/null || git rebase --abort 2>/dev/null
fi
git stash pop 2>/dev/null

# --- 3) stage + sync_guard 防误删闸 ---
git add -A
if ! bash "$GUARD_SCRIPT" "$HERMES_SYNC_DIR"; then
  echo "[sync_guard] DELETION DETECTED - PUSH ABORTED. If intentional: export SYNC_GUARD_BYPASS=1 and rerun."
  exit 1
fi

# --- 4) commit + push ---
if git diff --cached --quiet; then
  echo "[SKIP] nothing to commit"
else
  git commit -m 'sync'
  echo "[3] git push ..."
  git push origin main
  if [ $? -ne 0 ]; then
    echo "[RETRY] fetch+push once more ..."
    git fetch origin main && git rebase origin/main 2>/dev/null
    git push origin main
  fi
fi

echo "[DONE] Hermes pushed."
