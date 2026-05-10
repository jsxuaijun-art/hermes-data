---
name: hermes-data-sync
description: Cross-PC data sync for Hermes Agent (SOUL.md, memories, skills, config) via GitHub private repo. Covers WSL shell scripts, Windows .bat wrappers, dual-git engine retry for China network conditions, merge conflict resolution, and GitHub push protection.
---

# Hermes Data Sync (跨电脑同步)

**Last updated**: 2026-05-09 — Major rewrite: architecture changed from "Windows cmd does all git" to "WSL shell scripts drive everything, Windows git.exe handles network". Added dual-engine retry pattern.

## When to Use

- User works on multiple PCs (home + office) with Hermes Agent
- Need to sync SOUL.md, memories/, skills/, config.yaml between PCs
- Setting up or troubleshooting the sync scripts
- Resolving merge conflicts from divergent edits on two PCs
- Repairing git history after leaked secrets or broken rebase states

## Architecture (v2 — current)

```
Windows Desktop
  └─ Hermes同步-推送.bat  (4 lines, pure ASCII)
       │  "wsl -d Ubuntu-22.04 -- bash ~/.hermes/sync-push.sh"
       │
       ▼
WSL ~/.hermes/sync-push.sh  (drives everything)
       │
       ├─ [1/4] cp  WSL→Windows (local, instant)
       ├─ [2/4] cp  Claw→Windows (local, instant)
       ├─ [3/4] git add+commit   (local, instant)
       └─ [4/4] git push  ─┬─ Windows git.exe  (fast, uses Windows network stack)
                            └─ WSL git          (fallback, slower)
                                 (retries 5x each, alternating)
```

**Key design decision**: ALL logic lives in WSL shell scripts (`sync-push.sh`, `sync-pull.sh`). The `.bat` files are thin wrappers (4 lines each, pure ASCII, any encoding works). Network operations use **Windows git.exe** (`/mnt/c/Program Files/Git/bin/git.exe`) with **WSL git as fallback** — because from China, Windows git.exe uses the Windows network stack (proxy/VPN) and is substantially faster to GitHub.

**Sync directory**: `C:\Users\Admin\hermes-sync\` (cloned from `jsxuaijun-art/hermes-data`)
**Git remote**: `https://github.com/jsxuaijun-art/hermes-data.git`
**WSL user**: `dmin` (NOT root). Home = `/home/dmin/`
**Windows git.exe**: `/mnt/c/Program Files/Git/bin/git.exe`

> ⚠️ CRITICAL: The correct WSL home path MUST be used in all scripts. Using `/root/.hermes/` silently writes to the wrong location.

## 推送脚本 (`Hermes同步-推送.bat` + `sync-push.sh`)

### .bat 文件 (桌面, 4行纯 ASCII)

```batch
@echo off
chcp 65001 >nul
wsl -d Ubuntu-22.04 -- bash /home/dmin/.hermes/sync-push.sh
pause
```

Minimal — no encoding issues possible. Just triggers the WSL script.

### WSL 脚本 (`~/.hermes/sync-push.sh`)

Path: `/home/dmin/.hermes/sync-push.sh`

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

## 拉取脚本 (`Hermes同步-拉取.bat` + `sync-pull.sh`)

### .bat 文件 (桌面)

```batch
@echo off
chcp 65001 >nul
wsl -d Ubuntu-22.04 -- bash /home/dmin/.hermes/sync-pull.sh
pause
```

### WSL 脚本 (`~/.hermes/sync-pull.sh`)

```bash
#!/bin/bash
# Hermes Sync - Pull from GitHub (dual-git engine with retry)

SYNC_DIR="/mnt/c/Users/Admin/hermes-sync"
SYNC_DIR_WIN="C:/Users/Admin/hermes-sync"
GIT_WIN="/mnt/c/Program Files/Git/bin/git.exe"

cd "$SYNC_DIR" || exit 1

echo "[1/4] Git pull from GitHub..."

pull_retry() {
  for i in 1 2 3; do
    echo ">> [Windows git.exe] Attempt $i/3..."
    if "$GIT_WIN" -C "$SYNC_DIR_WIN" pull origin main --rebase 2>/dev/null; then
      echo ">> Pull successful!"
      return 0
    fi
    sleep $((i * 3))
  done
  return 1
}

pull_retry || {
  for i in 1 2 3; do
    echo ">> [WSL git] Attempt $i/3..."
    if git -c http.proxy= pull origin main --rebase 2>/dev/null; then
      echo ">> Pull successful!"
      break
    fi
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

## Voice Command Shortcuts (在 Hermes Agent 对话中)

用户可以直接对 Hermes Agent 说快捷指令：

### 推送github
```bash
cd /mnt/c/Users/Admin/hermes-sync && \
cp /home/dmin/.hermes/config.yaml SOUL.md SOUL_Pro.md SOUL_Edu.md . && \
cp /home/dmin/.hermes/memories/* memories/ && \
git add -A && git commit -m "sync $(date +%Y-%m-%d)" && \
/mnt/c/Program\ Files/Git/bin/git.exe -C "C:/Users/Admin/hermes-sync" push origin main
```

### 拉取github
```bash
cd /mnt/c/Users/Admin/hermes-sync && \
/mnt/c/Program\ Files/Git/bin/git.exe -C "C:/Users/Admin/hermes-sync" pull origin main && \
cp SOUL.md SOUL_Pro.md SOUL_Edu.md /home/dmin/.hermes/ && \
cp memories/* /home/dmin/.hermes/memories/ && \
cp config.yaml /home/dmin/.hermes/
```

## ⚠️ Pitfalls

### 0. ⚠️ 架构演进史（理解为什么这么设计）

| 版本 | 架构 | 问题 | 结局 |
|------|------|------|------|
| v0 | Windows cmd 做 git + WSL 拷文件 | cmd 中文编码 + `cd /d` 盘符问题 → 乱码报错 | 废弃 |
| v1 | 全部 git 在 WSL 内执行（`wsl -- bash -c` 包裹整段） | 从中国连 GitHub 超慢（Proxy 不镜像到 WSL2 NAT），大 push 总是超时 | 废弃 |
| **v2 (当前)** | **WSL shell 脚本驱动 + Windows git.exe 做网络操作** | 稳定运行 ✅ | 当前 |

### 1. 🔴 CRITICAL: WSL GitHub 网络慢（从中国访问）

**症状**: `git push` 超时（90s-300s）/ `GnuTLS recv error` / `Failed to connect to github.com port 443`

**原因**: 从中国直接 HTTPS 连 GitHub 丢包率高、延迟大。WSL2 NAT 模式下代理不镜像，WSL 原生 git 直连 GitHub 不稳定。

**根本解决方案**: 用 **Windows git.exe** 做网络操作。它走 Windows 网络栈，能用上用户 Windows 上的代理/VPN/路由优化：
```bash
# 快
/mnt/c/Program\ Files/Git/bin/git.exe -C "C:/Users/Admin/hermes-sync" push origin main

# 慢（从中国）
git push origin main
```
Windows git.exe 通常在 3-30 秒内完成推送，WSL git 可能 5 分钟超时。

**如果双引擎都失败**: 网络临时断连，脚本依然保存了本地数据（拷贝步骤已完成），稍后再跑即可。

### 2. 🔴 .bat 文件写入规则（WSL → Windows 桌面）

`.bat` 文件必须满足以下条件：
- **CRLF 换行符** (`\r\n`)，不能用 LF（`\n`）
- **纯 ASCII**（不要中文、线框字符 `═╔╗╚╝┌┐└┘├┤┼` 等）
- **编码**: ASCII 最安全，UTF-8 with BOM 可能在某些系统出问题

**写入方法**: 用 Python 二进制写，不要用 `write_file`：
```python
lines = [
    '@echo off',
    'chcp 65001 >nul',
    'wsl -d Ubuntu-22.04 -- bash /home/dmin/.hermes/sync-push.sh',
    'pause',
]
content = '\r\n'.join(lines) + '\r\n'
with open('/mnt/c/Users/Admin/Desktop/Hermes同步-推送.bat', 'wb') as f:
    f.write(content.encode('ascii'))
```

**验证**: `xxd /path/to/bat | head -5` → 每行结尾应为 `0d 0a`
```bash
# 正确
00000000: 4065 6368 6f20 6f66 660d 0a63 6863 7020  @echo off..chcp
# 错误（缺 0d）
00000000: 4065 6368 6f20 6f66 660a 6368 6370 3020  @echo off.chcp
```

### 3. 编码乱码症状快速诊断

| 错误症状 | 最可能根因 | 修复 |
|---------|-----------|------|
| `'?GitHub'` / `'愨晲鈺...'` / `'鏁版嵁...'` | LF 换行符或 UTF-8 BOM | 检查 CRLF → 用 Python 重写 |
| `'L' 不是内部或外部命令` | 中文/线框字符被 GBK 解析为命令 | 去所有非 ASCII 字符 |
| `系统找不到指定的路径` | `cd /d` 盘符不切或路径不存在 | 用 WSL 脚本代替 cmd cd |
| `Hermes done` 等 WSL 输出被当命令执行 | WSL bash 输出回流到 cmd 解析 | .bat 只做触发器，WSL 脚本做全部工作 |

### 4. git push rejected (non-fast-forward)

- Remote has commits you don't have locally (another PC pushed)
- **Fix**: The script handles this via `fetch → rebase/merge → push` sequence
- If manual intervention needed: `git pull --rebase origin main && git push`

### 5. Merge conflicts in shared config files

- Common conflict files: `README.md`, `memories/MEMORY.md`, `memories/USER.md`, skill files
- These files get edited on both PCs independently
- **Resolution**: Merge both sides — keep all info. MEMORY.md and USER.md are additive, not mutually exclusive.
- For skill files with same content but different line endings (CRLF vs LF): take either side
- Script attempts auto-merge via `rebase origin/main || merge origin/main --no-edit`

### 6. GitHub Push Protection (secret scanning)

- If a GitHub Token or API key leaks into a commit, push is blocked
- Symptom: `remote: error: GH013: Repository rule violations found`
- **Fix options**:
  - A) Allow the specific secret via GitHub's unblock URL (safe if token already revoked)
  - B) `git rebase -i --rebase-merges` to edit out the secret, then `git push --force`
- **Prevention**: Never store tokens in synced files like claw_memories/ or MEMORY.md

### 7. `git rebase --rebase-merges` required for history with merge commits

- Plain `git rebase -i <base>` FLATTENS merge commits, dropping the merge structure
- Correct: `git rebase -i --rebase-merges <base>` — preserves merge topology
- **Error sign**: Rebase appears to skip commits or produces a linear history missing merged content

### 8. Cleanup leftover `.git/rebase-merge` / `.git/rebase-apply`

- Interrupted rebase leaves these directories; next rebase fails
- **Fix**: `rm -rf /mnt/c/Users/Admin/hermes-sync/.git/rebase-merge`

### 9. WSL proxy warning

- `wsl: 检测到 localhost 代理配置，但未镜像到 WSL` — harmless, ignore
- Only matters if you need proxy in WSL; our scripts work around it via Windows git.exe

### 10. SOUL 版本漂移 (WSL vs Git 不一致)

- WSL 的 SOUL.md 可能与 Git 仓库版本不同
- **Symptom**: 推送上去了，但实际 WSL 跑的不是你要的 SOUL
- **Fix**: 同步后运行验证（对比 Git 仓库和 WSL 的文件）

### 11. 🔴 WSL 路径写错 (最隐蔽的 Bug)

- 脚本中 WSL 路径写错成 `/root/.hermes/` 时，cp 命令静默失败
- **Symptom**: 同步提示 ✓ 完成，但 Hermes 启动时的 SOUL 是英文默认版
- **Fix**: 确保脚本中路径为 `/home/dmin/`

### 12. `.bat` 测试必须在 Windows 资源管理器双击

| 测试方式 | 是否可靠 | 原因 |
|---------|---------|------|
| **Windows 资源管理器双击** | ✅ 唯一可靠 | 真正的 cmd.exe 环境 |
| WSL 内 `cmd.exe /c script.bat` | ❌ 不可靠 | UNC 路径问题，行为不同 |
| 看代码推理 | ❌ 不可靠 | 编码/换行符问题只在执行时暴露 |

## 同步范围

| 同步 | 不同步 |
|------|--------|
| SOUL.md, SOUL_Pro.md, SOUL_Edu.md | .env（API Key，每台电脑独立） |
| config.yaml | sessions.db（太大） |
| memories/* | state.db |
| skills/* | logs/, checkpoints/ |
| claw_memories/ (WSL Claw) | .hermes_history, auth.json |

## Reference Files

- `references/sync-scripts.md` — 脚本完整内容和历史演进
- `references/crlf-bat-write.md` — .bat 文件写入规范
- `references/cross-pc-paths.md` — 多电脑路径差异
- `references/sync-verification.md` — 同步后验证命令
- `references/git-history-repair.md` — 历史修复（泄漏密钥、rebase 损坏）
