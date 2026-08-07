#!/usr/bin/env bash
# ============================================================
# sync_guard.sh — Hermes 同步「防误删」保护闸
# 2026-08-07 由 office 机实战教训固化（company-deregistration 曾被 f20de05 误删）
#
# 作用：在「推送.bat」每次 git commit 前拦截「删除技能文件」的提交。
# 原因：多机同步时，某台机 ~/.hermes/skills 若缺某个 skill（没拉全），
#       上次推送会把它当"删除"commit 进 GitHub，导致技能在仓库里被抹掉。
#       本脚本保证：本次相对 HEAD 的删除 ≤ 白名单，否则中止推送并告警。
#
# 用法：在 git add -A 之后、commit 之前调用：
#       bash ~/.hermes/scripts/sync_guard.sh <sync_dir>
#       返回 0 = 安全，可继续 commit/push
#       返回 1 = 有非白名单删除，中止（不 commit 不 push）
# ============================================================

# 可接受的删除白名单（.bat 自身、运行时文件、gitignore 类），替换为 ^ 前缀精确匹配
# 常见 Git 默认忽略文件永远允许删（它们不该进仓库）
WHITELIST_RE='(\.gitignore|__pycache__/|\.pyc$|\.DS_Store$|.*\.tar\.gz$|.*\.tar$)'

repo="${1:?用法: sync_guard.sh <同步夹路径>}"

if [ ! -d "$repo/.git" ]; then
  echo "[sync_guard][ERROR] $repo 不是有效 git 仓库，跳过保护（但这很反常，请检查）"
  # 非 git 仓库无法判断，放行但告警
  exit 0
fi

cd "$repo" || exit 1

# 找出本次被 git 暂存的「删除」条目（relative paths）
# git diff --cached --name-status: A=新增 M=修改 D=删除 R=重命名(orig)
DELETED=$(git diff --cached --name-status 2>/dev/null | awk '$1=="D"{print $2}' | grep -vE "$WHITELIST_RE")

if [ -z "$DELETED" ]; then
  # 无删除，安全放行
  exit 0
fi

echo ""
echo "======================================================================"
echo "[sync_guard 🔴] 检测到本次推送会【删除】以下未在白名单内的文件："
echo "======================================================================"
echo "$DELETED" | sed 's/^/   ✗ /'
echo ""
echo "这可能是『某台电脑的 ~/.hermes/skills 缺此文件→本次同步把它当删除提交』"
echo "= 会导致技能被静默从 GitHub 仓库抹掉（历史上 company-deregistration 就这样丢过）。"
echo ""
echo "请在确认删除前检查："
echo "  1. 源机 ~/.hermes/skills 里该文件是否真的被有意删除？"
echo "  2. 还是只是这一台机器没拉取到？（若是→先跑「拉取.bat」补齐，勿推送）"
echo ""
echo "若【确实要删除】，可临时绕过："
echo "   export SYNC_GUARD_BYPASS=1  再跑推送即可。"
echo "======================================================================"
echo ""

if [ "${SYNC_GUARD_BYPASS:-0}" = "1" ]; then
  echo "[sync_guard] SYNC_GUARD_BYPASS=1，放行删除（你已明确确认）。"
  exit 0
fi

exit 1
