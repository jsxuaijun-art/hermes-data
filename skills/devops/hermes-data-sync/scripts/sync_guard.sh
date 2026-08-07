#!/usr/bin/env bash
# ============================================================
# sync_guard.sh — Hermes 同步「防误删」保护闸 (v3: 三道防线)
# 2026-08-07 固化。(v3 新增最关键的㊂：阻断"推送机技能不全把远端skill当删除")
#   ① 删除检测    ：commit 前拦截「删除 skill 文件」的提交(当前 staged)
#   ② 一致性提醒  ：本机有、但 git 未跟踪的 skill(提醒,不阻断)
#   ③ 缺失阻断(关键)：git/远端有、但本机 ~/.hermes/skills 缺失的 skill → 阻断!
#                    防止"这台机器技能不全→add -A 把远端 skill 当删除推没"。
#                    (company-deregistration 两次被 f20de05 / 0e0f1e5 误删都是这个原因)
# 用法（在 hermes_push.sh 里 git add 之后、commit 之前调用，须传 + <本机~/.hermes路径>）：
#   bash <同步夹>/scripts/sync_guard.sh <同步夹路径> <本机~/.hermes路径>
#   返回 0 = 安全，可继续；返回 1 = 有删除/缺失，中止（需 SYNC_GUARD_BYPASS=1 强制）
# ============================================================

set -u
WHITELIST_RE='(\.gitignore|__pycache__/|\.pyc$|\.DS_Store$|.*\.tar\.gz$|.*\.tar$)'
SKIP_TOPDIR_RE='^\.[^/]*$'   # .archive, .curator_backups, .git, .hub 等隐藏目录
# 删除检测/缺失检测里允许忽略的特定文件（如某些 skill 的引用副本），避免误报
EXTRA_IGNORE_RE='(hermes-data-sync-extraction\.md|references/)$'

repo="${1:?用法: sync_guard.sh <同步夹路径> [<本机hermes根路径, 必填以启用㊂缺失阻断>]}"
hermes_root="${2:-}"

if [ ! -d "$repo/.git" ]; then
  echo "[sync_guard][ERROR] $repo 不是有效 git 仓库，跳过保护（但这很反常，请检查）"
  exit 0
fi
cd "$repo" || exit 1

BLOCKED=0
MISSING_BLOCK_MSG=""

# ---------- ① 删除检测：本次 staged 删除 ----------
DELETED=$(git diff --cached --name-status 2>/dev/null | awk '$1=="D"{print $2}' | grep -vE "$WHITELIST_RE")
if [ -n "$DELETED" ]; then
  echo ""
  echo "======================================================================"
  echo "[sync_guard 🔴] 本次推送会【删除】以下未在白名单文件："
  echo "======================================================================"
  echo "$DELETED" | sed 's/^/   ✗ /'
  echo "  （多为: 某台机 ~/.hermes/skills 缺此文件→被当删除提交）"
  BLOCKED=1
fi

# ---------- ② 一致性提醒：本机有、git 未跟踪（仅提醒，不阻断） ----------
if [ -n "$hermes_root" ] && [ -d "$hermes_root/skills" ]; then
  LOCAL_SKILLS=$(cd "$hermes_root/skills" 2>/dev/null && find . -name SKILL.md -type f 2>/dev/null | sed 's#^\./##' | sort)
  TRACKED_SKILLS=$(git ls-files skills/ 2>/dev/null | grep 'SKILL.md$' | sed 's#^skills/##' | sort)
  MISSING_NEW=$(comm -23 <(echo "$LOCAL_SKILLS") <(echo "$TRACKED_SKILLS") | grep -vE "$SKIP_TOPDIR_RE" | grep -vE "$EXTRA_IGNORE_RE")
  if [ -n "$MISSING_NEW" ]; then
    echo ""
    echo "======================================================================"
    echo "[sync_guard 🟡] 本机 ~/.hermes/skills 里【存在但 git 未跟踪】的 skill："
    echo "======================================================================"
    echo "$MISSING_NEW" | sed 's#^#   ⚠ /#; s#/SKILL\.md$##'
    echo "  （这些 skill 若这次不推上去，别的电脑拉取不到——通常是本次要新增的，确认是有效 skill 就放心推送）"
  fi
fi

# ---------- ㊂ 缺失阻断（关键）：git/远端有、但本机缺 → 阻断 ----------
if [ -n "$hermes_root" ] && [ -d "$hermes_root/skills" ]; then
  LOCAL_SKILLS2=$(cd "$hermes_root/skills" 2>/dev/null && find . -name SKILL.md -type f 2>/dev/null | sed 's#^\./##' | sort)
  TRACKED_SKILLS2=$(git ls-files skills/ 2>/dev/null | grep 'SKILL.md$' | sed 's#^skills/##' | sort)
  # comm -13 = 只在 TRACKED(远端)有、LOCAL(本机)没有的 → 这台机缺的 skill
  # 排除 .archive/(curator归档副本,可再生,不必强制在本机) 和隐藏目录
  MISSING_FROM_LOCAL=$(comm -13 <(echo "$LOCAL_SKILLS2") <(echo "$TRACKED_SKILLS2") | grep -vE "$SKIP_TOPDIR_RE" | grep -vE '^\.archive/')
  if [ -n "$MISSING_FROM_LOCAL" ]; then
    BLOCKED=1
    MISSING_BLOCK_MSG="$MISSING_FROM_LOCAL"
  fi
fi

# ---------- 汇总 ----------
if [ "$BLOCKED" = "1" ]; then
  echo ""
  echo "======================================================================"
  echo "[sync_guard 🔴🔴] 推送已中止 —— 检测到风险，防止 skill 被误删进 GitHub"
  echo "======================================================================"
  echo "① 本次 staged 删除:";   echo "$DELETED" | sed 's/^/   ✗ /'
  echo "① 本机缺失(远端有、本机~/.hermes/skills没有)的 skill:"
  echo "$MISSING_BLOCK_MSG" | sed 's#^#   ✗ /#; s#/SKILL\.md$##' | sed 's/^   ✗ $//'
  echo ""
  echo "【原因】这台机器技能集不全(缺上面列出的 skill)。若现在 push，git add -A"
  echo "       会把它们当'删除'提交，导致技能从 GitHub 仓库被抹掉。"
  echo "       历史上 company-deregistration 就因此被删过两次(f20de05/0e0f1e5)。"
  echo ""
  echo "【正确做法】先补全再推：在这台机器跑一遍「拉取.bat」拉到全部 skill，"
  echo "        然后再推送。勿跳过！"
  echo ""
  echo "【若你确要强制推送】(有风险，会导致远端删除缺失 skill)："
  echo "        export SYNC_GUARD_BYPASS=1  再跑"
  echo "======================================================================"
  if [ "${SYNC_GUARD_BYPASS:-0}" = "1" ]; then
    echo "[sync_guard] SYNC_GUARD_BYPASS=1，放行（风险自负）。"
    exit 0
  fi
  exit 1
fi
echo "[sync_guard] ✅ 无删除、无缺失，安全推送。"
exit 0
