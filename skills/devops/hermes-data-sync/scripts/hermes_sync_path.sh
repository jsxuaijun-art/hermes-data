#!/usr/bin/env bash
# ============================================================
# hermes_sync_path.sh — 跨机通用:自动探测本机 Hermes 同步夹路径
# 2026-08-07 固化。目的:同一份 .bat 拷到任何电脑都能直接用,
#   无需手改路径(避免 P6 不同机器 Administrator/Admin、HermesAgent/hermes-sync 的差异)。
#
# 用法(在 WSL 内):
#   eval "$(bash <本脚本路径>)"
#   会导出:  WIN_USER / HERMES_SYNC_DIR / SYNC_REPO 三个变量
#   若找不到同步夹,打印告警,HERMES_SYNC_DIR 置为常用默认并置错误。
#
# 探测优先级(找到即停,验证 .git 存在 + remote 是 hermes-data):
#   1. C:\Users\<当前Windows用户>\Desktop\HermesAgent
#   2. C:\Users\Admin\hermes-sync        (home 机)
#   3. C:\Users\<当前Windows用户>\hermes-sync
#   4. 全域扫描 /mnt/c/Users/* / 下 remote 含 hermes-data 的 git 仓库
# ============================================================

# --- 取 Windows 用户名 (经 WSL 透传或探测) ---
if [ -n "$WSL_USER_NAME" ]; then
  WIN_USER="$WSL_USER_NAME"
else
  # 由 .bat 通过环境传入,或 fallback 探测
  WIN_USER="$USER"
fi

# 候选同步夹列表(按优先级)
CANDIDATES=""
add_cand() { CANDIDATES="$CANDIDATES $1"; }
add_cand "/mnt/c/Users/${WIN_USER}/Desktop/HermesAgent"
add_cand "/mnt/c/Users/Admin/hermes-sync"
add_cand "/mnt/c/Users/${WIN_USER}/hermes-sync"
add_cand "/mnt/c/Users/${WIN_USER}/Desktop/hermes-sync"

HERMES_SYNC_DIR=""
for c in $CANDIDATES; do
  if [ -d "$c/.git" ]; then
    # 校验 remote 是指向 hermes-data(防止误中 Claude/Codex/其他仓库)
    if git -C "$c" remote get-url origin 2>/dev/null | grep -qi "hermes-data"; then
      HERMES_SYNC_DIR="$c"
      break
    fi
  fi
done

if [ -z "$HERMES_SYNC_DIR" ]; then
  # 兜底:全域扫描 remote 含 hermes-data 的目录
  for d in /mnt/c/Users/*; do
    [ -d "$d" ] || continue
    for sub in "Desktop/HermesAgent" "hermes-sync" "Desktop/hermes-sync" "HermesAgent"; do
      c="$d/$sub"
      if [ -d "$c/.git" ] && git -C "$c" remote get-url origin 2>/dev/null | grep -qi "hermes-data"; then
        HERMES_SYNC_DIR="$c"; break 2
      fi
    done
  done
fi

if [ -z "$HERMES_SYNC_DIR" ]; then
  # 彻底找不到:给默认,并发出错误标记给 .bat 提示
  HERMES_SYNC_DIR="/mnt/c/Users/${WIN_USER}/Desktop/HermesAgent"
  echo "echo '[sync-path][ERROR] 找不到 hermes-data 同步夹(含.git),已用默认 $HERMES_SYNC_DIR'" >&2
fi

export WIN_USER HERMES_SYNC_DIR
echo "WIN_USER=${WIN_USER}"
echo "HERMES_SYNC_DIR=${HERMES_SYNC_DIR}"
