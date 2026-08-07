#!/usr/bin/env bash
# ============================================================
# sync_guard.sh — Hermes 同步「防误删」保护闸 (v2: 删除检测 + 一致性检测)
# 2026-08-07 固化。
#   ① 删除检测：commit 前拦截「删除 skill 文件」的提交
#   ② 一致性检测（v2 新增，防"本机有但仓库没跟踪"被遗漏/误删，如 yuanbao 案例）
# 用法（在 hermes_push.sh 里 git add 之后、commit 之前调用）：
#   bash <同步夹>/scripts/sync_guard.sh <同步夹路径> <本机~/.hermes路径>
#   返回 0 = 安全，可继续；返回 1 = 检测到删除/缺失，中止
# ============================================================

set -u
WHITELIST_RE='(\.gitignore|__pycache__/|\.pyc$|\.DS_Store$|.*\.tar\.gz$|.*\.tar$)'
# 顶层非 skill 目录（.开头的隐藏元数据、非SKILL.md的顶层杂项），一致性检测跳过
SKIP_TOPDIR_RE='^\.[^/]*$'   # .archive, .curator, .git, .hub 等隐藏目录
# 一致性检测只检查真正含 SKILL.md 的 skill 目录（含顶层直接 skill 和无 SKILL.md 的假目录都跳过）

repo="${1:?用法: sync_guard.sh <同步夹路径> [<本机hermes根路径>]}"
hermes_root="${2:-}"

if [ ! -d "$repo/.git" ]; then
  echo "[sync_guard][ERROR] $repo 不是有效 git 仓库，跳过保护（但这很反常，请检查）"
  exit 0
fi
cd "$repo" || exit 1

BLOCKED=0

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

# ---------- ② 一致性检测（v2）: 本机有、git 未跟踪的 skill ----------
if [ -n "$hermes_root" ] && [ -d "$hermes_root/skills" ]; then
  # 列出本机所有含 SKILL.md 的 skill 相对路径（skills/<...>/SKILL.md 或顶层 skill/SKILL.md）
  # 与 git 已跟踪列表对比，找出"本机有但仓库没跟踪"的
  LOCAL_SKILLS=$(cd "$hermes_root/skills" 2>/dev/null && find . -name SKILL.md -type f 2>/dev/null | sed 's#^\./##' | sort)
  TRACKED_SKILLS=$(git ls-files skills/ 2>/dev/null | grep 'SKILL.md$' | sed 's#^skills/##' | sort)
  MISSING=$(comm -23 <(echo "$LOCAL_SKILLS") <(echo "$TRACKED_SKILLS") | grep -vE "$SKIP_TOPDIR_RE")
  if [ -n "$MISSING" ]; then
    echo ""
    echo "======================================================================"
    echo "[sync_guard 🟡] 本机 ~/.hermes/skills 里【存在但 git 未跟踪】的 skill："
    echo "======================================================================"
    echo "$MISSING" | sed 's#^#   ⚠ /#; s#/SKILL\.md$##'
    echo "  （这些 skill 若这次不推上去，别的电脑拉取不到，且可能在某次 add -A 被当删除）"
    echo "  处理：确认是有效 skill 就保留并推送；若是废弃目录则从本机删除。"
    # 一致性缺失仅是提醒(push 前仍会处理)，不强制 blocker，避免误挡正常新增
    # （新增未 add 时这里会列出，是预期的"本次即将新增"）
  fi
fi

# ---------- 汇总 ----------
if [ "$BLOCKED" = "1" ]; then
  echo ""
  echo "======================================================================"
  echo "本次有删除需确认。若【确实要删】：export SYNC_GUARD_BYPASS=1 再跑。"
  echo "======================================================================"
  if [ "${SYNC_GUARD_BYPASS:-0}" = "1" ]; then
    echo "[sync_guard] SYNC_GUARD_BYPASS=1，放行。"
    exit 0
  fi
  exit 1
fi
exit 0
