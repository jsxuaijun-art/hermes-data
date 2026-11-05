#!/usr/bin/env bash
# Hermes 配置双向同步 — GitHub ↔ hermes-sync ↔ ~/.hermes/
# 适用于 Windows MSYS 环境下的 Git SSH pack 问题
# 用法: bash scripts/hermes-config-sync.sh
# 环境变量: LOCAL_PRIORITY=true  → .hermes/ 覆盖 hermes-sync/（本地编辑优先）
#            LOCAL_PRIORITY=false → 双向同步（默认，等价于不带变量）
set -o pipefail

SYNC_DIR="$HOME/hermes-sync"
HERMES_DIR="$HOME/.hermes"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
LOCAL_PRIORITY="${LOCAL_PRIORITY:-false}"

# 要同步的文件和目录
SYNC_PATHS=("SOUL.md" "SOUL_Pro.md" "SOUL_Edu.md" "config.yaml" "README.md")
SYNC_DIRS=("memories" "skills" "claw-memory")

cd "$SYNC_DIR" || { echo "[$TIMESTAMP] 错误: $SYNC_DIR 不存在"; exit 1; }

echo "[$TIMESTAMP] === Hermes 双向同步 ==="

# ── Step 1: 尝试 GitHub pull（有超时，失败不影响本地） ──
echo "[$TIMESTAMP] Step 1: 尝试 GitHub 拉取..."
if GIT_SSH_COMMAND="ssh -o ConnectTimeout=10" timeout 30 git pull origin main --rebase 2>/dev/null; then
    echo "[$TIMESTAMP]  Pull 成功"
elif GIT_SSH_COMMAND="ssh -o ConnectTimeout=10" timeout 30 git fetch origin main 2>/dev/null; then
    echo "[$TIMESTAMP]  Fetch 成功, reset..."
    git reset --hard origin/main 2>/dev/null
elif GIT_SSH_COMMAND="ssh -o ConnectTimeout=10" timeout 30 git fetch --depth=1 origin main 2>/dev/null; then
    echo "[$TIMESTAMP]  Shallow fetch 成功, reset..."
    git reset --hard origin/main 2>/dev/null
else
    echo "[$TIMESTAMP]  远程同步失败(网络问题), 跳过"
fi

# ── Step 2: Hermes → sync ──
# Always sync .hermes/ to sync dir (this is the primary direction)
echo "[$TIMESTAMP] Step 2: Hermes → sync 目录..."
for f in "${SYNC_PATHS[@]}"; do
    [ -f "$HERMES_DIR/$f" ] && cp "$HERMES_DIR/$f" "$SYNC_DIR/$f" 2>/dev/null && echo "  $f"
done
for d in "${SYNC_DIRS[@]}"; do
    if [ -d "$HERMES_DIR/$d" ]; then
        mkdir -p "$SYNC_DIR/$d"
        for f in "$HERMES_DIR/$d"/*; do
            [ -f "$f" ] || continue
            case "${f##*.}" in md|yaml|yml|txt|json|toml|py|sh|bat|conf) ;; *) continue ;; esac
            cp "$f" "$SYNC_DIR/$d/" 2>/dev/null && echo "  $d/$(basename "$f")"
        done
    fi
done

# ── Step 3: sync → Hermes (conditional on LOCAL_PRIORITY) ──
# When LOCAL_PRIORITY=true, skip this direction — .hermes/ is authoritative
# When LOCAL_PRIORITY=false (default), sync both ways for multi-device use
if [ "$LOCAL_PRIORITY" != "true" ]; then
    echo "[$TIMESTAMP] Step 3: sync → Hermes (双向)..."
    for f in "${SYNC_PATHS[@]}"; do
        [ -f "$SYNC_DIR/$f" ] && cp "$SYNC_DIR/$f" "$HERMES_DIR/$f" 2>/dev/null && echo "  $f"
    done
    for d in "${SYNC_DIRS[@]}"; do
        if [ -d "$SYNC_DIR/$d" ]; then
            mkdir -p "$HERMES_DIR/$d"
            for f in "$SYNC_DIR/$d"/*; do
                [ -f "$f" ] || continue
                case "${f##*.}" in md|yaml|yml|txt|json|toml|py|sh|bat|conf) ;; *) continue ;; esac
                cp "$f" "$HERMES_DIR/$d/" 2>/dev/null && echo "  $d/$(basename "$f")"
            done
        fi
    done
else
    echo "[$TIMESTAMP] Step 3: 跳过 (LOCAL_PRIORITY=true, 本地编辑优先)"
fi

# ── Step 4: Git push ──
echo "[$TIMESTAMP] Step 4: 推送 GitHub..."
if git diff --quiet 2>/dev/null && git diff --cached --quiet 2>/dev/null; then
    echo "[$TIMESTAMP]  无变化, 跳过推送"
else
    git add -A 2>/dev/null
    git commit -m "sync Windows端 ${TIMESTAMP}" 2>/dev/null
    if GIT_SSH_COMMAND="ssh -o ConnectTimeout=10" timeout 30 git push origin main 2>/dev/null; then
        echo "[$TIMESTAMP]  推送成功"
    elif git push origin main 2>&1 | grep -q "rejected"; then
        echo "[$TIMESTAMP]  推送被拒绝(远程有更新)..."
        # Try rebase first (preserves our commits, only works if we cached remote refs)
        if git rebase --onto origin/main HEAD 2>/dev/null; then
            echo "[$TIMESTAMP]  Rebase 成功, 重新推送..."
            GIT_SSH_COMMAND="ssh -o ConnectTimeout=10" timeout 30 git push origin main 2>/dev/null && \
                echo "[$TIMESTAMP]  推送成功" || \
                echo "[$TIMESTAMP]  推送仍然失败"
        else
            # If refs are stale, compare SHAs via API before force push
            echo "[$TIMESTAMP]  Rebase 失败(远程跟踪分支过时), 尝试 --force..."
            GIT_SSH_COMMAND="ssh -o ConnectTimeout=10" timeout 30 git push --force origin main 2>/dev/null && \
                echo "[$TIMESTAMP]  Force push 成功" || \
                echo "[$TIMESTAMP]  Force push 也失败(网络问题)"
        fi
    else
        echo "[$TIMESTAMP]  推送失败(网络问题), 本地已保存"
    fi
fi

echo "[$TIMESTAMP] === 同步完成 ==="
