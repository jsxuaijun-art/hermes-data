#!/bin/bash
# ============================================
# DSH 盈信技能 四机同步脚本（家里/笔记本/办公室/老婆笔记本）
# 把 DeepSeek Harness 的 skills 纳入现有 hermes-data git 体系
#
# 用法:
#   bash ~/.hermes/sync-dsh.sh push    # 本机 .dsh/skills → 仓库 dsh-skills → git push
#   bash ~/.hermes/sync-dsh.sh pull    # 从仓库 dsh-skills 拉回 → 覆盖本机 .dsh/skills
#   bash ~/.hermes/sync-dsh.sh both    # 先 pull 合并远端，再 push 本机（默认，推荐下班前跑）
#
# 约定（沿用 hermes-data）:
#   - 禁止强推；先 fetch/pull --rebase 防冲突
#   - .dsh/skills 只放业务知识，不放真实客户/凭证
#   - 覆盖前会把本机旧版留档到 hermes-sync/dsh-skills-backup/<时间戳>/
# ============================================
set -e

REPO="/mnt/c/Users/Admin/hermes-sync"
DSH_SKILLS="/mnt/c/Users/Admin/.dsh/skills"
REPO_SKILLS="$REPO/dsh-skills"
BACKUP="$REPO/dsh-skills-backup/$(date '+%Y%m%d-%H%M%S')"

ACTION="${1:-both}"

echo "============================================"
echo " DSH 盈信技能同步  $(date '+%Y-%m-%d %H:%M')  动作=$ACTION"
echo "============================================"

# 1. 确保在 main 分支
cd "$REPO"
CUR=$(git rev-parse --abbrev-ref HEAD)
if [ "$CUR" != "main" ]; then
  echo ">>> 切回 main ..."
  git stash push -m "auto-stash before dsh-sync $(date '+%Y-%m-%d %H:%M')" 2>/dev/null || true
  git checkout main 2>/dev/null || { echo "❌ 切回 main 失败"; exit 1; }
fi

pull_side() {
  echo ">>> 从远端拉取（可等几分钟）..."
  timeout 300 git pull --rebase origin main 2>&1 || echo "   ⚠️ 拉取未完成，中止后续，勿强推"
  echo ">>> 把仓库 dsh-skills 同步回本机 .dsh/skills ..."
  if [ -d "$REPO_SKILLS" ]; then
    if [ -d "$DSH_SKILLS" ]; then
      mkdir -p "$BACKUP"
      cp -a "$DSH_SKILLS" "$BACKUP/" 2>/dev/null || true
      echo "   已留档本机旧版 → $BACKUP"
    fi
    mkdir -p "$DSH_SKILLS"
    rsync -a --delete "$REPO_SKILLS/" "$DSH_SKILLS/" 2>/dev/null || cp -rf "$REPO_SKILLS/." "$DSH_SKILLS/"
    echo "   ✅ 本机 .dsh/skills 已更新（重启 DSH 生效）"
  else
    echo "   ⚠️ 仓库无 dsh-skills 目录，跳过拉取"
  fi
}

push_side() {
  echo ">>> 把本机 .dsh/skills 复制进仓库 dsh-skills ..."
  if [ -d "$DSH_SKILLS" ]; then
    if [ -d "$REPO_SKILLS" ]; then cp -rf "$REPO_SKILLS" "$BACKUP-remote/" 2>/dev/null || true; fi
    mkdir -p "$REPO_SKILLS"
    rsync -a --delete "$DSH_SKILLS/" "$REPO_SKILLS/" 2>/dev/null || cp -rf "$DSH_SKILLS/." "$REPO_SKILLS/"
    echo "   ✅ 已同步进仓库 dsh-skills"
  fi
  echo ">>> 提交并推送 ..."
  git add -A
  if git diff --cached --quiet; then
    echo "   无变更，无需推送"
  else
    git commit -m "dsh skills sync $(date '+%a %Y/%m/%d %H:%M')"
    timeout 300 git pull --rebase origin main 2>&1 || echo "   ⚠️ 拉取未完成"
    git push origin main 2>&1 || { echo "   ❌ 推送被拒（远端有新提交）。禁止强推，请手动 git fetch origin main && git merge origin/main 后重推"; exit 1; }
    echo "   ✅ 推送成功"
  fi
}

case "$ACTION" in
  push) pull_side; push_side ;;
  pull) pull_side ;;
  both) pull_side; push_side ;;
  *) echo "未知动作: $ACTION (可用 push/pull/both)"; exit 1 ;;
esac

echo "============================================"
echo " 完成"
echo "============================================"
