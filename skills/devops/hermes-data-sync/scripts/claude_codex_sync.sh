#!/usr/bin/env bash
# ============================================================
# claude_codex_sync.sh — Claude Code + Codex 的同步+推送 (WSL内执行)
# 2026-08-07 固化. 由 Hermes同步-推送.bat 调用, 消除 .bat 内联转义/括号问题。
# 用法: bash claude_codex_sync.sh   (同时处理 Claude 和 Codex)
# ============================================================

set -u

# --- Claude Code: WSL -> Windows -> push ---
CLAUDE_SYNC="/mnt/c/Users/Administrator/Desktop/ClaudeCode-Sync"
# 兼容 home 机(Admin路径): 若不存在, 探测
if [ ! -d "$CLAUDE_SYNC/.git" ]; then
  for c in "/mnt/c/Users/Admin/ClaudeCode-Sync" "/mnt/c/Users/Administrator/ClaudeCode-Sync"; do
    [ -d "$c/.git" ] && CLAUDE_SYNC="$c" && break
  done
fi

echo "[Claude] Syncing WSL -> Windows ..."
mkdir -p "$CLAUDE_SYNC"
rsync -a ~/.claude/settings.json "$CLAUDE_SYNC/" 2>/dev/null
rsync -a --delete ~/.claude/agents/ "$CLAUDE_SYNC/agents/" 2>/dev/null
rsync -a ~/.claude/CLAUDE.md "$CLAUDE_SYNC/" 2>/dev/null
echo "[Claude] Pushing ..."
cd "$CLAUDE_SYNC" || echo "[Claude] WARN: cd failed"
git stash 2>/dev/null
git pull --rebase origin main 2>&1
git stash pop 2>/dev/null
git add -A
if git diff --cached --quiet; then echo "[Claude] SKIP nothing to commit"; else git commit -m 'sync' 2>/dev/null; git push origin main 2>&1; fi
echo "[Claude] DONE"

# --- Codex Code: WSL -> Windows -> push ---
CODEX_SYNC="/mnt/c/Users/Administrator/Desktop/CodexCode-Sync"
if [ ! -d "$CODEX_SYNC/.git" ]; then
  for c in "/mnt/c/Users/Admin/CodexCode-Sync" "/mnt/c/Users/Administrator/CodexCode-Sync"; do
    [ -d "$c/.git" ] && CODEX_SYNC="$c" && break
  done
fi

echo "[Codex] Syncing WSL -> Windows ..."
mkdir -p "$CODEX_SYNC"
rsync -a ~/.codex/config.toml "$CODEX_SYNC/" 2>/dev/null
rsync -a ~/.codex/model_catalog.json "$CODEX_SYNC/" 2>/dev/null
rsync -a ~/.codex/installation_id "$CODEX_SYNC/" 2>/dev/null
rsync -a ~/.codex/version.json "$CODEX_SYNC/" 2>/dev/null
rsync -a --delete ~/.codex/rules/ "$CODEX_SYNC/rules/" 2>/dev/null
rsync -a --delete ~/.codex/skills/ "$CODEX_SYNC/skills/" 2>/dev/null
echo "[Codex] Pushing ..."
cd "$CODEX_SYNC" || echo "[Codex] WARN: cd failed"
git stash 2>/dev/null
git pull --rebase origin main 2>&1
git stash pop 2>/dev/null
git add -A
if git diff --cached --quiet; then echo "[Codex] SKIP nothing to commit"; else git commit -m 'sync' 2>/dev/null; git push origin main 2>&1; fi
echo "[Codex] DONE"

echo "[DONE] Claude + Codex pushed."
