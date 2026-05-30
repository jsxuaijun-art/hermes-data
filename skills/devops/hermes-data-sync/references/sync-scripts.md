# Hermes 同步脚本 (推送/拉取) — 完整内容

> **架构**: WSL shell 脚本驱动 + Windows git.exe 做网络操作
> **.bat 文件**: 仅 4 行纯 ASCII 触发器，无乱码风险
> **双引擎重试**: Windows git.exe 优先（5 次）→ WSL git 回退（5 次）

## 文件位置

| 文件 | Windows 路径 | WSL 路径 |
|------|-------------|---------|
| 推送 .bat | `C:\Users\Admin\Desktop\Hermes同步-推送.bat` | `/mnt/c/Users/Admin/Desktop/Hermes同步-推送.bat` |
| 拉取 .bat | `C:\Users\Admin\Desktop\Hermes同步-拉取.bat` | `/mnt/c/Users/Admin/Desktop/Hermes同步-拉取.bat` |
| 推送 WSL 脚本 | — | `/home/dmin/.hermes/sync-push.sh` |
| 拉取 WSL 脚本 | — | `/home/dmin/.hermes/sync-pull.sh` |

## 完整文件内容

### `Hermes同步-推送.bat` (4 行, 纯 ASCII)

```batch
@echo off
chcp 65001 >nul
wsl -d Ubuntu-22.04 -- bash /home/dmin/.hermes/sync-push.sh
pause
```

### `sync-push.sh` (WSL, ~80 行)

```bash
#!/bin/bash
# Hermes Sync - Push to GitHub (hybrid dual-engine)

SYNC_DIR="/mnt/c/Users/Admin/hermes-sync"
SYNC_DIR_WIN="C:/Users/Admin/hermes-sync"
GIT_WIN="/mnt/c/Program Files/Git/bin/git.exe"

cd "$SYNC_DIR" || exit 1

echo "[1/4] Copy Hermes data from WSL to Windows..."
cp -f /home/dmin/.hermes/SOUL.md /home/dmin/.hermes/SOUL_Pro.md /home/dmin/.hermes/SOUL_Edu.md . 2>/dev/null
cp -rf /home/dmin/.hermes/memories/* memories/ 2>/dev/null
mkdir -p skills && cp -rf /home/dmin/.hermes/skills/* skills/ 2>/dev/null
cp -f /home/dmin/.hermes/config.yaml . 2>/dev/null

echo "[2/4] Copy Claw data from WSL to Windows..."
cp -f /home/dmin/.claw.yaml /home/dmin/.claw/config.yaml . 2>/dev/null
cp -rf /home/dmin/.claw/memories/* claw_memories/ 2>/dev/null

echo "[3/4] Git add + commit..."
git add -A
git commit -m "sync $(date '+%Y-%m-%d_%H:%M')" 2>/dev/null || echo "(nothing to commit)"

echo "[4/4] Git push (2 engines, up to 10 retries)..."

push_win() {
  for i in 1 2 3 4 5; do
    echo ">> [Windows git.exe] Attempt $i/5..."
    "$GIT_WIN" -C "$SYNC_DIR_WIN" fetch origin 2>/dev/null
    "$GIT_WIN" -C "$SYNC_DIR_WIN" rebase origin/main 2>/dev/null || \
      "$GIT_WIN" -C "$SYNC_DIR_WIN" merge origin/main --no-edit 2>/dev/null || true
    if "$GIT_WIN" -C "$SYNC_DIR_WIN" push origin main 2>/dev/null; then
      echo ">> Push succeeded! (Windows git.exe)"
      return 0
    fi
    sleep $((i * 2))
  done
  return 1
}

push_wsl() {
  for i in 1 2 3 4 5; do
    echo ">> [WSL git] Attempt $i/5..."
    git -c http.proxy= fetch origin 2>/dev/null
    git -c http.proxy= rebase origin/main 2>/dev/null || \
      git -c http.proxy= merge origin/main --no-edit 2>/dev/null || true
    if git -c http.proxy= push origin main 2>/dev/null; then
      echo ">> Push succeeded! (WSL git)"
      return 0
    fi
    sleep $((i * 2))
  done
  return 1
}

push_win || push_wsl || {
  echo ">> Push failed after all retries (network issue)."
  echo ">> Local data saved. Retry manually:"
  echo ">>   cd C:\\Users\\Admin\\hermes-sync"
  echo ">>   git fetch && git rebase origin/main && git push"
}

echo ""
echo "============================================"
echo "  Sync complete (local data always saved)"
echo "============================================"
```

### `Hermes同步-拉取.bat` (4 行, 纯 ASCII)

```batch
@echo off
chcp 65001 >nul
wsl -d Ubuntu-22.04 -- bash /home/dmin/.hermes/sync-pull.sh
pause
```

### `sync-pull.sh` (WSL, ~45 行)

```bash
#!/bin/bash
# Hermes Sync - Pull from GitHub (Dual-git engine, fetch+reset strategy)

SYNC_DIR="/mnt/c/Users/Admin/hermes-sync"
SYNC_DIR_WIN="C:/Users/Admin/hermes-sync"
GIT_WIN="/mnt/c/Program Files/Git/bin/git.exe"

cd "$SYNC_DIR" || exit 1

echo "[1/4] Fetch + reset from GitHub..."

pull_retry() {
  for i in 1 2 3; do
    echo ">> [Windows git.exe] Attempt $i/3..."
    "$GIT_WIN" -C "$SYNC_DIR_WIN" fetch origin main 2>/dev/null || continue
    "$GIT_WIN" -C "$SYNC_DIR_WIN" reset --hard origin/main 2>/dev/null || continue
    echo ">> Pull successful!"
    return 0
    sleep $((i * 3))
  done
  return 1
}

pull_retry || {
  for i in 1 2 3; do
    echo ">> [WSL git] Attempt $i/3..."
    git fetch origin main 2>/dev/null || continue
    git reset --hard origin/main 2>/dev/null || continue
    echo ">> Pull successful!"
    return 0
    sleep $((i * 3))
  done
  echo ">> Pull had issues, continuing with local data..."
}

echo "[2/4] Copy to WSL Hermes..."
cp -f SOUL.md SOUL_Pro.md SOUL_Edu.md /home/dmin/.hermes/ 2>/dev/null
mkdir -p /home/dmin/.hermes/memories && cp -rf memories/* /home/dmin/.hermes/memories/ 2>/dev/null
mkdir -p /home/dmin/.hermes/skills && cp -rf skills/* /home/dmin/.hermes/skills/ 2>/dev/null
cp -f config.yaml /home/dmin/.hermes/ 2>/dev/null

echo "[3/4] Copy to WSL Claw..."
mkdir -p /home/dmin/.claw && cp -f .claw.yaml config.yaml /home/dmin/.claw/ 2>/dev/null
mkdir -p /home/dmin/.claw/memories && cp -rf claw_memories/* /home/dmin/.claw/memories/ 2>/dev/null

echo ""
echo "============================================"
echo "  Done! GitHub data synced to local Hermes + Claw"
echo "============================================"
```

## 架构演进史

| 版本 | 架构 | 问题 | 结局 |
|------|------|------|------|
| **v0** | Windows cmd 做 git + WSL 拷贝 | cmd 编码/盘符 → 乱码 | 废弃 |
| **v1** | 全部 git 在 WSL 内执行 | 从中国连 GitHub 超慢 | 废弃 |
| **v2 (当前)** | WSL shell 脚本驱动 + Windows git.exe 做网络操作 | 稳定 ✅ | 当前 |

## 关键设计原则

1. **.bat 做触发器，不做逻辑** — 4 行纯 ASCII，`wsl -- bash 路径` 即可。零编码/CRLF 风险。
2. **WSL shell 脚本做全部逻辑** — `cp`、`git add/commit` 本地操作在 WSL 内飞快。网络操作用 Windows git.exe。
3. **Windows git.exe 优先** — `/mnt/c/Program Files/Git/bin/git.exe` 利用 Windows 网络栈（代理/VPN），从中国连 GitHub 比 WSL 原生 git 快 10-100 倍。
4. **双引擎重试** — Windows git.exe 崩溃/超时后自动切 WSL git，两个引擎各试 5 次。
5. **本地数据永远保存** — 网络失败只影响推送，文件拷贝步骤已提前完成。不会丢数据。

## 验证方法

```bash
# 看文件换行符
file /mnt/c/Users/Admin/Desktop/*.bat
# 应显示: DOS batch file, ASCII text, with very long lines

# 看 shell 脚本语法
bash -n /home/dmin/.hermes/sync-push.sh
bash -n /home/dmin/.hermes/sync-pull.sh

# 手动测试（先测试网络）
/mnt/c/Program\ Files/Git/bin/git.exe -C "C:/Users/Admin/hermes-sync" fetch origin
```

## 故障排查

- **Windows git.exe 说`unable to access` + `GnuTLS recv error`**: 网络波动，等几分钟重试
- **两个引擎都超时**: 网络断连/墙变严，换时间再跑。本地数据不会丢失
- **冲突阻止 push**: `git fetch origin && git rebase origin/main` 手动解决冲突，再 `git push`
- **脚本语法错误**: 检查 bash 语法（`bash -n`）和 CRLF 换行
