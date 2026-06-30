#!/bin/bash
# ============================================
# WSL 手动拉取脚本（上班时执行）
# 从 GitHub 拉取最新数据到 ~/.hermes/
# 安全加固：自动切回 main 分支
# 备用方案：如git pull超时，提示手动从Windows git bash拉取
# ============================================
# 用法: bash ~/.hermes/sync-pull-wsl.sh
set -e

SYNC_DIR="/mnt/c/Users/Admin/hermes-sync"
HERMES_DIR="/home/dmin/.hermes"

echo "============================================"
echo " GitHub → WSL 拉取  $(date '+%Y-%m-%d %H:%M')"
echo "============================================"

cd "$SYNC_DIR"

# ===== 分支安全守卫 =====
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "⚠️  当前分支: $CURRENT_BRANCH（非 main）"
    echo ">>> 自动暂存改动并切回 main ..."
    git stash push -m "auto-stash before branch switch $(date '+%Y-%m-%d %H:%M')" 2>/dev/null || true
    git checkout main 2>/dev/null || { echo "❌ 切回 main 失败，终止"; exit 1; }
    echo "✅ 已切回 main 分支"
fi

echo ">>> 从 GitHub 拉取最新数据 ..."
if git pull origin main 2>&1; then
    echo "   ✅ 拉取成功"
else
    echo "   ⚠️  git pull 失败（可能是网络问题）"
    echo "   请尝试在 Windows 的 git bash 中手工执行："
    echo "     cd D:\\360MoveData\\Users\\Admin\\Desktop\\hermes-sync"
    echo "     git pull origin main"
    echo "   或在 WSL 中手动运行："
    echo "     cd $SYNC_DIR && GIT_TRACE=1 git fetch origin main"
    echo ""
    echo "   然后重新运行本脚本继续同步到 ~/.hermes/"
    exit 1
fi

# 同步到 ~/.hermes/
echo ">>> 同步到 ~/.hermes/ ..."
cp -f "$SYNC_DIR/SOUL.md" "$HERMES_DIR/SOUL.md" 2>/dev/null || true
cp -f "$SYNC_DIR/SOUL_Pro.md" "$HERMES_DIR/SOUL_Pro.md" 2>/dev/null || true
cp -f "$SYNC_DIR/SOUL_Edu.md" "$HERMES_DIR/SOUL_Edu.md" 2>/dev/null || true
cp -f "$SYNC_DIR/config.yaml" "$HERMES_DIR/config.yaml" 2>/dev/null || true
# 同步同步脚本本身
cp -f "$SYNC_DIR/sync-push-wsl.sh" "$HERMES_DIR/sync-push-wsl.sh" 2>/dev/null || true
cp -f "$SYNC_DIR/sync-pull-wsl.sh" "$HERMES_DIR/sync-pull-wsl.sh" 2>/dev/null || true
rsync -a --delete "$SYNC_DIR/memories/" "$HERMES_DIR/memories/" 2>/dev/null || true
rsync -a --delete "$SYNC_DIR/skills/" "$HERMES_DIR/skills/" 2>/dev/null || true
echo "   ✅ 同步完成"

echo "============================================"
echo " 完成"
echo "============================================"
