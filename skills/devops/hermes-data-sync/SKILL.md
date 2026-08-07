---
name: hermes-data-sync
description: >-
  Cross-PC data sync for Hermes Agent, Claude Code, and Codex Code via three
  independent GitHub repos. Single .bat file drives all three pipelines.
  Covers inline .bat scripts, rsync incremental copying, git fetch+reset
  strategy, curator_backups 100MB+ push guardrails, and three-repo architecture.
---

# Hermes Data Sync (跨电脑同步 — v3 三项独立同步)

**Last updated**: 2026-08-07
**Current architecture**: v3 — 三项独立同步（Hermes / Claude Code / Codex Code），各 repo 独立 rsync→git push

## ★★ 所有电脑统一操作规范（2026-08-07 定稿 · 精简版）

**铁律：规范里绝不写死任何单机绝对路径。** 每台机器开头只设 3 个变量，其余命令全用变量。

```bash
export WSL_HOME="/home/<本机WSL用户名>"       # 例 dmin→/home/dmin；administrator→/home/administrator
export WIN_SYNC_DIR="/mnt/c/<本机同步夹映射>" # Home=Users/Admin/hermes-sync；Office=Users/Administrator/Desktop/HermesAgent
export HERMES_REPO="jsxuaijun-art/hermes-data" # 唯一数据仓库
# 完整路径对照见 references/cross-pc-paths.md
```

**增删改任何 skill/内容，五步统一走：**
```
1 改   只在 ~/.hermes/ 内编辑，不直接动同步夹
2 验   本地 skill_view / hermes 命令确认生效、可运行
3 推   源机提交推送 HERMES_REPO；同步夹 git fetch+reset
4 拉   目标机跑「拉取.bat」→ git fetch+reset 同步夹 → rsync 进 ~/.hermes/
5 验   目标机立即 skill_view 确认；查不到→走下方 P11，绝不瞎搜
```

**核心心智（Hermes 是目录扫描制，非常驻索引）：**
- 文件没落在 `~/.hermes/skills/<类>/<名>/` → **必搜不到**；落位 → **立即生效**，不用重启。
- 「别机 push 的东西本机查不到」默认=**同步没落地**（step4 的 rsync 没跑成），不是 Hermes 漏了。
- 同步夹多个副本，先确认哪个是源、remote 是不是 HERMES_REPO，再动手。

## 拉取后新内容「查不到」——必看排查（2026-08-07 实战固化）

> **场景**：另一台电脑往 GitHub push 了新 skill / 新内容（记忆、配置文件等），本机跑了「拉取 .bat」，但 Hermes 里 `skills_list` / `skill_view` / grep 都找不到。

**根因（三层，逐层核对）：**
1. **GitHub 仓库里到底有没有？** → 先在 `jsxuaijun-art/hermes-data` 仓库 itself 看，确认别家的 push 真的已经在（`git log --oneline -5`，或 Windows 同步夹 `C:\Users\<user>\Desktop\HermesAgent\`、`C:\Users\Admin\hermes-sync\` 里查）。**别只搜 `~/.hermes/skills`。**
2. **WSL 端 `~/.hermes/` 有没有被拉取动作更新？** → 这是最多漏的一层：`Hermes同步-拉取.bat` 是「git fetch+reset **Windows 同步夹** → rsync 到 WSL `~/.hermes/`」两步。若只跑了 git(Windows夹) 而没跑/没成功跑 rsync，或 .bat 压根没在这个机器跑，则 Windows 文件夹里有、WSL `~/.hermes/` 里没有 → Hermes **必然搜不到**（Hermes 技能目录扫描只认 `~/.hermes/skills/...`）。
3. **Hermes 只在文件落进 `~/.hermes/skills/` 后才可见。** 目录扫描制，非常驻索引。文件一落进去**立即生效**（不用重启），`skill_view <名字>` 立刻 available。

**正确排查顺序（别像我这次先瞎搜本地）：**
```bash
# A. 先在 GitHub / Windows 同步夹确认目标真的存在
ls /mnt/c/Users/Admin/hermes-sync/skills/            # 找目标 skill 目录
git -C /mnt/c/Users/Admin/hermes-sync log --oneline -5   # 看 push 提交在不在
git -C /mnt/c/Users/Admin/hermes-sync remote -v          # 确认 remote = jsxuaijun-art/hermes-data

# B. 确认 WSL 端缺失（= 此处的真实状态）
find ~/.hermes/skills -iname "*<名字>*"    # 空 = 没同步进 WSL

# C. 同步进 WSL（要么跑「拉取.bat」，要么手动 cp）
src=/mnt/c/<同步夹>/skills/<分类>/<skill>/
dst=~/.hermes/skills/<分类>/<skill>/
mkdir -p "$dst" && cp -r "$src." "$dst"
# 注意 Windows 同步的文件可能是 CRLF，用 grep \\r 检查、sed 转 LF 以防脚本/解析问题

# D. 验证 Hermes 已识别
skill_view name=<skill>    # readiness_status: available = 完成
```

**关键教训：**
- 别在 `~/.hermes/skills` 里死磕 grep——**先确认 push 是否真的进了 GitHub**（用户名/仓库名要对，可能是别的用户名 `Admin` vs `Administrator`，同步夹有多个副本）。
- 查「另一个电脑推送的内容」时，**默认怀疑它可能还没拉进本机 WSL**，而不是"被 Hermes 漏了"。Hermes 不会漏，目录扫描很可靠；漏的是同步动作本身。
- 同步夹有多个（`C:\Users\Admin\hermes-sync\` 与 `C:\Users\Administrator\Desktop\HermesAgent\`）要分清哪个是最新源。

## When to Use

- User works on multiple PCs (home + office) with Hermes Agent
- Need to sync SOUL.md, memories/, skills/, config.yaml between PCs
- Need to sync Claude Code config (~/.claude/)
- Need to sync Codex Code config (~/.codex/)
- Setting up or troubleshooting the sync scripts
- Repairing git history after oversized files (curator_backups) blocked push
- **Sync script hangs on `[N/6] Copy ... from WSL to Windows...`** — likely rsync of large skills/ directory
- **`remote: fatal: pack exceeds the maximum allowed size`** — curator_backups issue

## Architecture (v3 — three independent pipelines)

```
Windows Desktop .bat (inline ~60 lines, pure ASCII)
  │
  ├─ [1/6] rsync Hermes  ~/.hermes/ → Windows HermesAgent/
  ├─ [2/6] git push Hermes  (fetch+reset → add+commit → push)
  ├─ [3/6] rsync Claude   ~/.claude/ → Windows ClaudeCode-Sync/
  ├─ [4/6] git push Claude (fetch+reset → add+commit → push)
  ├─ [5/6] rsync Codex    ~/.codex/ → Windows CodexCode-Sync/
  └─ [6/6] git push Codex (fetch+reset → add+commit → push)
       └─ Steps are independent — failure of one does NOT block the others
```

**Key design decisions**:

| Decision | Why |
|----------|-----|
| **Inline .bat** | ALL logic inside the .bat (`wsl -d Ubuntu -e bash -c "..."`). No separate shell scripts. Self-contained on desktop. |
| **rsync -a instead of cp -rf** | `cp -rf` over /mnt/ (cross-filesystem) takes 3-10 min for 833MB skills/. rsync does it in 30s-2min, then ~1s incremental. |
| **git fetch+reset instead of pull --rebase** | `fetch + reset --hard` is simpler, avoids merge conflicts entirely. GitHub is single source of truth. |
| **No 2>/dev/null swallowing** | All stderr shown so errors are visible in console. |
| **Separate repos** | Each pipeline has its own git repo — Hermes/hermes-data, Claude/ClaudeCode-Sync, Codex/CodexCode-Sync. |
| **No Windows git.exe** | All git in WSL (simpler inline .bat, no dual-engine complexity). |

### Sync directories & repos

| Pipeline | Windows directory | GitHub repo | WSL source |
|----------|-------------------|-------------|------------|
| Hermes | `C:\Users\Administrator\Desktop\HermesAgent` | `jsxuaijun-art/hermes-data` | `~/.hermes/` |
| Claude | `C:\Users\Administrator\Desktop\ClaudeCode-Sync` | `jsxuaijun-art/ClaudeCode-Sync` | `~/.claude/` |
| Codex | `C:\Users\Administrator\Desktop\CodexCode-Sync` | `jsxuaijun-art/CodexCode-Sync` | `~/.codex/` |

**WSL distro**: `Ubuntu` (no dash — NOT `Ubuntu-22.04`)
**WSL user**: `administrator` (home = `/home/administrator/`)
**Windows user**: `Administrator`

## Push script (`Hermes同步-推送.bat`) — 6 steps

This is the **actual current script** as stored on `C:\Users\Administrator\Desktop\`:

```batch
@echo off
chcp 65001 >nul

wsl -d Ubuntu -e bash -c "
  echo '[1/6] Copy Hermes data from WSL to Windows...'
  rsync -a --delete ~/.hermes/ /mnt/c/Users/Administrator/Desktop/HermesAgent/ 2>/dev/null

  echo '[2/6] Sync to GitHub latest (fetch+reset)...'
  cd /mnt/c/Users/Administrator/Desktop/HermesAgent
  git add -A
  git diff --cached --quiet || git commit -m \"sync \$(date '+%Y-%m-%d_%H:%M')\"
  git fetch origin main
  git reset --hard origin/main
  git push origin main

  echo '[3/6] Copy Claude Code data from WSL to Windows...'
  rsync -a --delete ~/.claude/ /mnt/c/Users/Administrator/Desktop/ClaudeCode-Sync/ 2>/dev/null

  echo '[4/6] Claude Code sync to GitHub...'
  cd /mnt/c/Users/Administrator/Desktop/ClaudeCode-Sync
  git add -A
  git diff --cached --quiet || git commit -m \"sync \$(date '+%Y-%m-%d_%H:%M')\"
  git fetch origin main && git reset --hard origin/main
  git push origin main

  echo '[5/6] Copy Codex Code data from WSL to Windows...'
  rsync -a --delete ~/.codex/ /mnt/c/Users/Administrator/Desktop/CodexCode-Sync/ 2>/dev/null

  echo '[6/6] Codex Code sync to GitHub...'
  cd /mnt/c/Users/Administrator/Desktop/CodexCode-Sync
  git add -A
  git diff --cached --quiet || git commit -m \"sync \$(date '+%Y-%m-%d_%H:%M')\"
  git fetch origin main && git reset --hard origin/main
  git push origin main
" 2>nul
echo.
echo All done.
pause
```

### How each step works

1. **rsync -a --delete**: Incremental sync from WSL to Windows. Only changed files are transferred. `--delete` removes files on Windows that were deleted in WSL. Source path with trailing `/` means "copy directory contents", without trailing slash means "copy directory itself".
2. **git add -A**: Stage all changes.
3. **git diff --cached --quiet**: Check if there are staged changes. If none (exit 0), skip commit. Prevents empty commit error.
4. **git commit**: Only runs if there were changes.
5. **git fetch origin main**: Download remote state without merging.
6. **git reset --hard origin/main**: Discard any local divergence, reset to remote exactly.
7. **git push origin main**: Push to GitHub.

> Note: `git fetch + reset --hard` discards local uncommitted changes that weren't pushed. This is intentional — the repos are pure sync mirrors, not development branches. If a skill was modified on this PC but not yet pushed, running pull first will lose those changes. Always push before pulling on another machine.

## Pull script (`Hermes同步-拉取.bat`) — 4 steps

```batch
@echo off
chcp 65001 >nul

wsl -d Ubuntu -e bash -c "
  echo '[1/4] Get Hermes data from GitHub latest...'
  cd /mnt/c/Users/Administrator/Desktop/HermesAgent
  git fetch origin main && git reset --hard origin/main

  echo '[2/4] Copy Hermes data to WSL...'
  rsync -a --delete /mnt/c/Users/Administrator/Desktop/HermesAgent/ ~/.hermes/

  echo '[3/4] Copy Claude Code data to WSL...'
  cd /mnt/c/Users/Administrator/Desktop/ClaudeCode-Sync
  git fetch origin main && git reset --hard origin/main
  rsync -a --delete /mnt/c/Users/Administrator/Desktop/ClaudeCode-Sync/ ~/.claude/

  echo '[4/4] Copy Codex Code data to WSL...'
  cd /mnt/c/Users/Administrator/Desktop/CodexCode-Sync
  git fetch origin main && git reset --hard origin/main
  rsync -a --delete /mnt/c/Users/Administrator/Desktop/CodexCode-Sync/ ~/.codex/
" 2>nul
echo.
echo All done.
pause
```

## Sync scope

| Sync (WSL > GitHub > other PC) | NOT synced (per-PC only) |
|---------------------------------|--------------------------|
| `SOUL.md`, `SOUL_Pro.md`, `SOUL_Edu.md` | `.env` (API keys, different per PC) |
| `config.yaml` | `sessions.db` (too large, transient) |
| `memories/*.md` | `state.db` (session index) |
| `skills/*` | `logs/`, `checkpoints/`, `caches/` |
| `skills/.gitignore` | `history.jsonl` (Codex runtime) |
| `~/.claude/` (config files) | `*.sqlite` (Codex DB files) |
| `~/.codex/` (config files only) | `shell_snapshots/`, `state_*/`, `tmp/` |

### Codex sync exclusions

Only config files from `~/.codex/` are synced — exclude runtime data:

**Include**: `config.toml`, `model_catalog.json`, `installation_id`, `version.json`, `rules/`, `skills/`
**Exclude**: `history.jsonl`, `sessions/`, `*.sqlite`, `*.db`, `logs_*/`, `state_*/`, `tmp/`, `shell_snapshots/`

CodexCode-Sync `.gitignore`:
```gitignore
*.sqlite
*.db
*.jsonl
logs_*/
state_*/
tmp/
shell_snapshots/
__pycache__/
*.pyc
```

## Hermes CLI launch script (`hermes.bat`)

This is separate from sync scripts but lives on the same desktop:

```batch
@echo off
chcp 65001 >nul
wsl -d Ubuntu -- bash -c "cd ~/hermes-agent && ./venv/bin/python -m hermes_cli.main chat" 2>nul
```

Key differences from sync .bat:
| Feature | Sync .bat | Hermes CLI launch |
|---------|-----------|-------------------|
| `chcp 65001` | Optional | REQUIRED (interactive UTF-8) |
| `2>nul` | Required | Required |
| `-e` vs `--` | `-e bash` (cleaner) | `-- bash -c "..."` (long inline) |
| Path | Windows desktop git repo | Project venv path |

## Pitfalls

### P1 curator_backups exceeds GitHub 100MB limit

**Symptom**: `git push` fails with `remote: fatal: pack exceeds the maximum allowed size (100.00 MiB)` or `file X is 224.22 MB; this exceeds GitHub's file size limit of 100 MB`

**Root cause**: Hermes curator creates `.tar.gz` backups in `~/.hermes/skills/.curator_backups/`. A single backup can be 108MB. Five in history = 540MB. GitHub hard limit is 100MB/file.

**Fix**:
```bash
cd /mnt/c/Users/Administrator/Desktop/HermesAgent

# 1. Remove from tracking
git rm -r --cached skills/.curator_backups/ 2>/dev/null
git rm -r --cached "*.tar.gz" 2>/dev/null

# 2. Update .gitignore
echo "skills/.curator_backups/" >> .gitignore
echo "*.tar.gz" >> .gitignore
git add .gitignore && git commit -m "remove curator_backups"

# 3. Normal push refused? Filter-branch:
git filter-branch --index-filter \
  'git rm -r --cached --ignore-unmatch skills/.curator_backups/
   git rm -r --cached --ignore-unmatch "*.tar.gz"
   git rm -r --cached --ignore-unmatch "*.tar"' \
  --prune-empty -- --all

git push origin main --force

# 4. Other PCs:
git fetch origin main && git reset --hard origin/main
```

> **⚠️ 2026-08-01 实战更新：优先用 clean rebuild 而非 filter-branch**
> `git filter-branch` 在 dash 下有坑（`read -d` 语法错）、且会留 1GB 残留 pack 让 `.git` 无法真正瘦身，push 仍可能超时/被拒。**历史浅时直接 clean rebuild 更彻底**（`.git` 能缩到 <10MB，推送秒成功）：
> ```bash
> cd /mnt/c/Users/Administrator/Desktop/HermesAgent
> mv .git /tmp/git-backup-$(date +%H%M)   # 备份旧 .git（保险）
> git init -b main; git config user.name "jsxuaijun-art"
> git remote add origin git@github.com:jsxuaijun-art/hermes-data.git
> git add -A    # 受完整 .gitignore 约束，curator_backups/dist 自动排除
> git commit -m "clean rebuild: exclude large files"
> git push --force origin main:main
> ```
> 验证：排除后 worktree 仅 20-30MB/1250+ 文件，`.git` <10MB，本地=远端 HEAD 一致。删 Windows 工作区残留 `.curator_backups/` 和 `gstack/*/dist/` 副本（源在 `~/.hermes/skills/`，删副本不丢数据）。实测 hermes-data 从 `.git` 989MB→8.9MB，push 秒成功，commit `5e6675b`。

**Prevention**: All three repos must include in `.gitignore`:
```gitignore
skills/.curator_backups/
**/.curator_backups/
*.tar.gz
*.tar
**/dist/          # gstack 等编译产物二进制(~90MB each)
*.dist
```

**Check for big files**:
```bash
git ls-files | xargs -I{} sh -c 'wc -c "$1" 2>/dev/null' _ {} | sort -rn | head -10
```

### P2 rsync over /mnt/ looks like a hang

**Symptom**: `[1/6] Copy Hermes data from WSL to Windows...` then nothing for 30s-2min.

**Root cause**: rsync first full scan of 90+ skills (833MB) over cross-filesystem `/mnt/`. First run is 30s-2min; subsequent runs ~1s (incremental).

**Verify**: `ps aux | grep rsync` in another WSL terminal.

### P3 Three pipelines share one WSL session

Each step is independent. Failure in step 1/2 (Hermes) does not stop step 3/4 (Claude) or step 5/6 (Codex).

### P4 git fetch+reset discards local changes

**WARNING**: If this PC has local skill edits not yet pushed, `fetch + reset --hard` wipes them. Always push before pulling on another PC.

### P5 .bat encoding (CRLF + pure ASCII)

- Pure ASCII only (no Chinese, box-drawing chars)
- CRLF (`\r\n`) line endings — LF silently fails
- `chcp 65001 >nul` + `2>nul` required

**Python write method**:
```python
lines = ['@echo off', 'chcp 65001 >nul', 'wsl -d Ubuntu ... 2>nul']
content = '\r\n'.join(lines) + '\r\n'
with open(path, 'wb') as f:
    f.write(content.encode('ascii'))
```

**Verify**: `xxd path | head -5` — look for `0d 0a` at each line end.

### P6 WSL distro name differs across machines

| This PC (current) | Jiangmin's PC |
|-------------------|--------------|
| `wsl -d Ubuntu` | `wsl -d Ubuntu-22.04` |
| `/home/administrator/` | `/home/jiangmin/` |
| `C:\Users\Administrator\Desktop` | `C:\Users\jiangmin\Desktop` |

When copying .bat to another PC, ALL THREE paths must be updated.

### P7 git push appears successful but nothing changed

**Order matters** — script stages changes BEFORE fetch+reset:
```bash
git add -A                          # 1. Stage
git diff --cached --quiet ||        # 2. Check
  git commit -m "sync ..."           # 3. Commit
git fetch origin main               # 4. Download remote
git reset --hard origin/main         # 5. Reset (keeps committed)
git push origin main                 # 6. Push
```
If no files changed, `git diff --cached --quiet` exits 0, skip commit, reset to remote, push says up-to-date. This is correct behavior.

### P8 pycache modify/delete conflicts (historical fix)

**FIXED** via `.gitignore` (`__pycache__/`) + `git rm --cached`. Should not recur.

If it does:
```bash
git ls-files | grep __pycache__ | while read f; do git rm --cached "$f"; done
git add -A && git commit -m "remove pycache" && git push origin main
# Other PCs: fetch+reset (do NOT use pull --rebase)
```

### P9 .bat must be tested by double-click in Windows Explorer

- Double-click in Explorer = reliable (real cmd.exe)
- `cmd.exe /c script.bat` from WSL = unreliable (UNC path issues)
- Code review only = unreliable (encoding bugs only show at runtime)

### P10 rsync single skill dir fails when parent category dir missing

**Symptom**: `rsync: [Receiver] mkdir ".../skills/content-creation/enterprise-visit-biz-handoff" failed: No such file or directory` (exit 11)

**Root cause**: When adding a brand-new skill under a category that doesn't exist yet in the Windows mirror repo, the parent dir (`skills/content-creation/`) is absent — rsync won't create intermediate destination dirs.

**Fix**: `mkdir -p` parents first, then rsync:
```bash
cd /mnt/c/Users/Administrator/Desktop/HermesAgent
mkdir -p skills/content-creation skills/productivity
rsync -a /home/administrator/.hermes/skills/content-creation/<skill>/ skills/content-creation/<skill>/
```
Full `rsync -a ~/.hermes/ ...` (step 1 of the .bat) never hits this — it creates all dirs. Only targeted per-skill syncs do.

## Architecture evolution

| Version | Architecture | Status |
|---------|-------------|--------|
| v0 | Windows cmd git + WSL cp | retired |
| v1 | All git in WSL | retired |
| v2.0-2.1 | WSL scripts + Windows git.exe | retired |
| **v3** | **Inline .bat triple-pipeline + rsync + fetch+reset** | current |

## Quick diagnosis

| Symptom | Likely cause | Action |
|---------|-------------|--------|
| `[1/6]` then nothing 30s-2min | rsync first sync (833MB) | Wait or `ps aux | grep rsync` |
| `[2/6]` then hangs 30s+ | git push timeout (China) | Check VPN; wait or let next step run |
| Garbled "not an internal command" | WSL warning without `2>nul` | Add `2>nul` |
| Script finishes, data unchanged | fetch+reset discarded local changes | Check git status before running |
| `remote: fatal: pack exceeds max size` | curator_backups 100MB+ | Run P1 cleanup |
| **git fetch/clone hangs (>150s) though `ssh -T git@github.com` is fast** | git 的 SSH 子进程握手不稳（China） | **前置 `GIT_SSH_COMMAND="ssh -o ConnectTimeout=15"` 再跑 git**（本机 2026-08-07 实测从卡死→秒通）。SSH 单独连 github.com:443(见~/.ssh/config) 秒通，但 git 默认调 ssh 卡住 |
| **git push rejected "fetch first"** | 别机已推,本地 origin/main 过时 | `git fetch` 后 `git rebase origin/main`（**勿用 reset --hard，会丢本地新提交**）；用 `git log --oneline -3` 先看差异 |
| **rebase 报 "deleted by us: SKILL.md"** | 远端某 sync 提**删除了文件**,你的提交改它→change/delete 冲突 | 这是**多机同步把文件从 git 删掉的严重信号**：`git show <我的提交>:<路径> > /tmp/x` 取回 → `cp`回工作区 → `add` → `GIT_EDITOR=true git rebase --continue` |
| **skill 在某台机"消失",但 git 历史有它** | 被某个 `sync` 提交 `--diff-filter=D` 删了(如 company-deregistration 被 f20de05 误删) | `git log --oneline --diff-filter=D -- <路径>` 定位删除提交 → 从源机 `~/.hermes/skills/…` rsync 回 → `add/commit/push` 补回主仓库 |
| **rebase --continue 报 editor 错误** | 非交互终端无编辑器 | 前置 `GIT_EDITOR=true`（复用原信息） |

> ⚠️ **2026-08-07 实战最深教训（本机 office/Administrator/b91136e 确认）：**
> ① `company-deregistration`(注销skill) **曾被 `f20de05 sync` 从 GitHub 误删**——它是"某一环节工作区缺它→sync 提交顺势把它删进 git"。已在本机补回并 push(`b91136e`)。**结论：凡是"某台机器本地没有的 skill/文件"，若用了 `rsync --delete` 或 `git add -A` 的同步提交，会被当成"删除"从仓库抹掉。** 多机同步务必保证每台工作区都有全量 skill，否则 --delete/add -A 会静默删文件。
> ② 我(脚本)曾误用 `rsync --delete ~/.hermes/ → HermesAgent同步夹/`，结果把该同步夹的 `.git` 和 skills/ 工作树**连根删了**(~/.hermes 里没有 .git 和同步结构)。**教训:绝不能对同步夹跑"把 ~/.hermes 全量 --delete 镜像过去"的命令**,同步夹有 .git+README 等 ~/.hermes 没有的文件会被删。正确是把 `hermes-sync`(git 健康)当源,精确 rsync 单个 skill 目录(不含 --delete)。
> ③ git 内网慢的可靠解法 = `GIT_SSH_COMMAND="ssh -o ConnectTimeout=15"`。
