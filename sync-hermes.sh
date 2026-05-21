#!/bin/bash
# Hermes 记忆+技能 双向同步脚本
# 先启动代理（Clash等），再运行此脚本

set -e

REPO_DIR="/mnt/c/Users/Administrator/Desktop/HermesAgent"
HERMES_DIR="$HOME/.hermes"

cd "$REPO_DIR"

echo "=== 从本机 Hermes 复制最新数据 ==="
cp "$HERMES_DIR/memories/MEMORY.md" "$REPO_DIR/memories/" 2>/dev/null || true
cp "$HERMES_DIR/memories/USER.md" "$REPO_DIR/memories/" 2>/dev/null || true
cp "$HERMES_DIR/SOUL.md" "$REPO_DIR/" 2>/dev/null || true
rsync -a --delete "$HERMES_DIR/skills/" "$REPO_DIR/skills/" 2>/dev/null || true

echo "=== 推送到 GitHub ==="
git add -A
if ! git diff --cached --quiet; then
    git commit -m "sync: Hermes memories & skills $(date '+%Y-%m-%d %H:%M')"
    git push origin main 2>/dev/null || git push origin master 2>/dev/null
    echo "推送完成"
else
    echo "无变更，跳过"
fi

echo "=== 从 GitHub 拉取云端最新数据 ==="
git fetch origin
git reset --hard origin/main 2>/dev/null || git reset --hard origin/master 2>/dev/null

echo "=== 将云端数据写回本机 Hermes ==="
cp "$REPO_DIR/memories/MEMORY.md" "$HERMES_DIR/memories/" 2>/dev/null || true
cp "$REPO_DIR/memories/USER.md" "$HERMES_DIR/memories/" 2>/dev/null || true
cp "$REPO_DIR/SOUL.md" "$HERMES_DIR/" 2>/dev/null || true
rsync -a --delete "$REPO_DIR/skills/" "$HERMES_DIR/skills/" 2>/dev/null || true

echo "同步完成"
