#!/bin/bash
# Hermes Sync - Push to GitHub (v5 — reset FIRST, then copy; fixes stale-tracked-file bug)
# WSL user: administrator | Distro: Ubuntu
# 修复要点：旧版先 cp 再 `git reset --hard origin/main`，会把刚拷贝进来的
#          已跟踪文件（如 SKILL.md）改动冲掉 → 只有新增文件能上传、改动永远慢一代。
#          现改为 fetch+reset 先执行，再拷贝本地数据，最后 add/commit/push。

SYNC_DIR="/mnt/c/Users/Admin/hermes-sync"
cd "$SYNC_DIR" || exit 1

echo "[1/4] Sync to GitHub latest (fetch+reset)..."
git fetch origin main
if [ $? -ne 0 ]; then
  echo ">> FETCH FAILED (network?). Aborting."
  exit 1
fi
git reset --hard origin/main

echo "[2/4] Copy Hermes data from WSL to Windows..."
cp -f /home/administrator/.hermes/SOUL.md /home/administrator/.hermes/SOUL_Pro.md /home/administrator/.hermes/SOUL_Edu.md . 2>/dev/null
cp -rf /home/administrator/.hermes/memories/* memories/ 2>/dev/null
mkdir -p skills && cp -rf /home/administrator/.hermes/skills/* skills/ 2>/dev/null
cp -f /home/administrator/.hermes/config.yaml . 2>/dev/null
cp -f /home/administrator/.hermes/sync-push.sh "$SYNC_DIR/sync-push.sh" 2>/dev/null

echo "[3/4] Stage + commit..."
git add -A 2>/dev/null
git commit -m "sync $(date '+%Y-%m-%d_%H:%M')" 2>/dev/null || echo "(nothing to commit)"

echo "[4/4] Push..."
git push origin main

if [ $? -eq 0 ]; then
  echo ">> Push succeeded!"
else
  echo ">> Push failed even after reset. Trying force-push (lease)..."
  git push --force-with-lease origin main
  if [ $? -eq 0 ]; then
    echo ">> Force-push succeeded! (divergence resolved)"
  else
    echo ">> Force-push also failed. Manual fix needed:"
    echo ">>   cd /mnt/c/Users/Admin/hermes-sync"
    echo ">>   git fetch origin main && git reset --hard origin/main && git push origin main"
    exit 1
  fi
fi

echo ""
echo "============================================"
echo "  Sync complete (local data always saved)"
echo "============================================"
