#!/bin/bash
# ============================================
# WSL 手动推送脚本（下班前执行）
# 先拉后推，拉取超时则 force push（WSL端始终最新）
# 安全加固：自动切回 main 分支，防止推到错误分支
# ============================================
# 用法: bash ~/.hermes/sync-push-wsl.sh
set -e

SYNC_DIR="/mnt/c/Users/Admin/hermes-sync"
HERMES_DIR="/home/dmin/.hermes"

echo "============================================"
echo " WSL → GitHub 推送  $(date '+%Y-%m-%d %H:%M')"
echo "============================================"

# ===== 分支安全守卫 =====
cd "$SYNC_DIR"
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "⚠️  当前分支: $CURRENT_BRANCH（非 main）"
    echo ">>> 自动暂存改动并切回 main ..."
    git stash push -m "auto-stash before branch switch $(date '+%Y-%m-%d %H:%M')" 2>/dev/null || true
    git checkout main 2>/dev/null || { echo "❌ 切回 main 失败，终止"; exit 1; }
    echo "✅ 已切回 main 分支"
fi

# 1. 复制最新数据
echo ">>> 复制 ~/.hermes/ 数据到 $SYNC_DIR ..."
cp -f "$HERMES_DIR/SOUL.md" "$SYNC_DIR/SOUL.md" 2>/dev/null || true
cp -f "$HERMES_DIR/SOUL_Pro.md" "$SYNC_DIR/SOUL_Pro.md" 2>/dev/null || true
cp -f "$HERMES_DIR/SOUL_Edu.md" "$SYNC_DIR/SOUL_Edu.md" 2>/dev/null || true
cp -f "$HERMES_DIR/config.yaml" "$SYNC_DIR/config.yaml" 2>/dev/null || true
# 同步同步脚本本身，让另一台电脑也能拿到更新
cp -f "$HERMES_DIR/sync-push-wsl.sh" "$SYNC_DIR/sync-push-wsl.sh" 2>/dev/null || true
cp -f "$HERMES_DIR/sync-pull-wsl.sh" "$SYNC_DIR/sync-pull-wsl.sh" 2>/dev/null || true
rsync -a --delete "$HERMES_DIR/memories/" "$SYNC_DIR/memories/" 2>/dev/null || true
rsync -a --delete "$HERMES_DIR/skills/" "$SYNC_DIR/skills/" 2>/dev/null || true
echo "   ✅ 数据复制完成"

# 2. 提交
cd "$SYNC_DIR"
git add -A
if git diff --cached --quiet; then
    echo "   无变更，跳过推送"
    echo "============================================"
    echo " 完成（无需推送）"
    echo "============================================"
    exit 0
fi

git commit -m "sync WSL端 $(date '+%a %Y/%m/%d %H:%M')"

# 3. 尝试 git pull --rebase（实测此仓库 fetch 需 3 分钟，给足超时）
echo ">>> 尝试拉取远程变更（可等几分钟）..."
timeout 300 git pull --rebase origin main 2>&1 || echo "   ⚠️ 拉取未完成，先中止，别强推！"

# 4. 推送（严禁 force push —— 会覆盖远端其他电脑的提交）
echo ">>> 推送到 GitHub ..."
if git push origin main 2>&1; then
    echo "   ✅ 推送成功"
else
    echo "   ❌ 推送被拒（远端有新提交）。禁止强推！请手动合并后重推："
    echo "      cd /mnt/c/Users/Admin/hermes-sync"
    echo "      git fetch origin main && git merge origin/main"
    echo "      git push origin main"
    exit 1
fi

echo "============================================"
echo " 完成"
echo "============================================"
