#!/usr/bin/env bash
# ============================================================
# claude_codex_pull.sh — 拉取: Windows同步夹 -> WSL (Claude+Codex)
# 2026-08-07 固化. 由 Hermes同步-拉取.bat 调用, 消除内联转义问题。
# ============================================================

set -u

# --- Claude: Windows -> WSL ---
CLAUDE_SYNC="/mnt/c/Users/Administrator/Desktop/ClaudeCode-Sync"
[ -d "/mnt/c/Users/Admin/ClaudeCode-Sync/.git" ] && CLAUDE_SYNC="/mnt/c/Users/Admin/ClaudeCode-Sync"
echo "[Claude] Windows -> WSL ..."
mkdir -p ~/.claude
rsync -a "$CLAUDE_SYNC/settings.json" ~/.claude/ 2>/dev/null
rsync -a --delete "$CLAUDE_SYNC/agents/" ~/.claude/agents/ 2>/dev/null
rsync -a "$CLAUDE_SYNC/CLAUDE.md" ~/.claude/ 2>/dev/null
echo "[Claude] DONE"

# --- Codex: Windows -> WSL ---
CODEX_SYNC="/mnt/c/Users/Administrator/Desktop/CodexCode-Sync"
[ -d "/mnt/c/Users/Admin/CodexCode-Sync/.git" ] && CODEX_SYNC="/mnt/c/Users/Admin/CodexCode-Sync"
echo "[Codex] Windows -> WSL ..."
mkdir -p ~/.codex/rules ~/.codex/skills
rsync -a "$CODEX_SYNC/config.toml" ~/.codex/ 2>/dev/null
rsync -a "$CODEX_SYNC/model_catalog.json" ~/.codex/ 2>/dev/null
rsync -a "$CODEX_SYNC/installation_id" ~/.codex/ 2>/dev/null
rsync -a "$CODEX_SYNC/version.json" ~/.codex/ 2>/dev/null
rsync -a --delete "$CODEX_SYNC/rules/" ~/.codex/rules/ 2>/dev/null
rsync -a --delete "$CODEX_SYNC/skills/" ~/.codex/skills/ 2>/dev/null
echo "[Codex] DONE"

echo "[DONE] Claude + Codex pulled."
