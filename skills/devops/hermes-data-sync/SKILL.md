---
name: hermes-data-sync
description: Cross-PC data sync for Hermes Agent (SOUL.md, memories, skills, config) via GitHub private repo. Covers Windows .bat scripts, WSL integration, merge conflict resolution, and GitHub push protection.
---

# Hermes Data Sync (跨电脑同步)

**Last updated**: 2026-05-09 — Added WSL2 NAT proxy workaround, CRLF post-fix method, and new diagnostic patterns from garbled `'?GitHub'` symptom.

## When to Use
- User works on multiple PCs (home + office) with Hermes Agent
- Need to sync SOUL.md, memories/, skills/, config.yaml between PCs
- Setting up or troubleshooting the sync .bat scripts
- Resolving merge conflicts from divergent edits on two PCs
- Repairing git history after leaked secrets or broken rebase states

## Architecture

```
Windows cmd (git push/pull)                      Windows cmd (git pull)
     ↕ GitHub Cloud ↕                                  ↕
C:\Users\Admin\hermes-sync\                    C:\Users\Administrator\Desktop\HermesAgent\
     ↑ WSL cp to                                       ↑ WSL cp to
WSL ~/.hermes/                                  WSL ~/.hermes/
(dmin@Ubuntu-22.04)                             (administrator@Ubuntu)
```

**Key design decision**: ALL git operations run in **Windows cmd**, NOT in WSL. WSL is only used for file copying. This avoids the WSL2 NAT proxy problem (see pitfall below).

**Sync directory**: `C:\Users\Admin\hermes-sync\` (cloned from `jsxuaijun-art/hermes-data`)
**Git remote**: `https://github.com/jsxuaijun-art/hermes-data.git`
**WSL user** (home PC): `dmin` (NOT root; NOT admin). Home = `/home/dmin/`
**WSL ~/.hermes**: `/home/dmin/.hermes/` (home PC), NOT `/root/.hermes/`

> ⚠️ CRITICAL: The correct WSL home path MUST be used in all .bat scripts. Using `/root/.hermes/` silently writes to the wrong location.

## 推送脚本 (`Hermes同步-推送.bat`)

Path on desktop: `D:\360MoveData\Users\Admin\Desktop\Hermes同步-推送.bat`

**Architecture**: WSL copies files → Windows cmd does all git operations. This avoids WSL2 NAT proxy issues.

```batch
@echo off
chcp 65001 >nul
echo.
echo ==============================================
echo   Hermes Data Sync - Push to GitHub
echo ==============================================
echo.

echo [1/4] Copying Hermes data from WSL...
wsl -d Ubuntu-22.04 -- bash -c "WSL_HOME=/home/dmin; cp -f $WSL_HOME/.hermes/SOUL.md $WSL_HOME/.hermes/SOUL_Pro.md $WSL_HOME/.hermes/SOUL_Edu.md /mnt/c/Users/Admin/hermes-sync/ 2>/dev/null; cp -rf $WSL_HOME/.hermes/memories/* /mnt/c/Users/Admin/hermes-sync/memories/ 2>/dev/null; cp -rf $WSL_HOME/.hermes/skills/* /mnt/c/Users/Admin/hermes-sync/skills/ 2>/dev/null; cp -f $WSL_HOME/.hermes/config.yaml /mnt/c/Users/Admin/hermes-sync/ 2>/dev/null; echo Hermes done"

echo [2/4] Copying Claw memory...
wsl -d Ubuntu-22.04 -- bash -c "cp -f /home/dmin/.claw.yaml /home/dmin/.claw/config.yaml /mnt/c/Users/Admin/hermes-sync/ 2>/dev/null; cp -rf /home/dmin/.claw/memories/* /mnt/c/Users/Admin/hermes-sync/claw_memories/ 2>/dev/null; echo Claw done"
echo.

echo [3/4] Committing and pushing to GitHub...
cd /d C:\Users\Admin\hermes-sync
git add -A
git diff --cached --quiet || git commit -m "sync %date:~-10,4%-%date:~-4,2%-%date:~-2,2%"
git pull --rebase origin main
git push origin main
echo.

echo [4/4] Done!
echo.
echo ==============================================
echo   Hermes + Claw data synced to GitHub
echo ==============================================
echo.
pause
```

Note: `%date%` format on this PC produces `Sat 05/09/2026` → extracted as `2026-05-09`.

## 拉取脚本 (`Hermes同步-拉取.bat`)

Path on desktop: `D:\360MoveData\Users\Admin\Desktop\Hermes同步-拉取.bat`

Same architecture: Windows cmd for git, WSL for file copy.

```batch
@echo off
chcp 65001 >nul
echo.
echo ==============================================
echo   Hermes Data Sync - Pull from GitHub
echo ==============================================
echo.

echo [1/4] Pulling latest data from GitHub...
cd /d C:\Users\Admin\hermes-sync
git pull origin main
echo.

echo [2/4] Copying to WSL Hermes directory...
wsl -d Ubuntu-22.04 -- bash -c "WSL_HOME=/home/dmin; cp -f /mnt/c/Users/Admin/hermes-sync/SOUL.md /mnt/c/Users/Admin/hermes-sync/SOUL_Pro.md /mnt/c/Users/Admin/hermes-sync/SOUL_Edu.md $WSL_HOME/.hermes/ 2>/dev/null; mkdir -p $WSL_HOME/.hermes/memories && cp -rf /mnt/c/Users/Admin/hermes-sync/memories/* $WSL_HOME/.hermes/memories/ 2>/dev/null; mkdir -p $WSL_HOME/.hermes/skills && cp -rf /mnt/c/Users/Admin/hermes-sync/skills/* $WSL_HOME/.hermes/skills/ 2>/dev/null; cp -f /mnt/c/Users/Admin/hermes-sync/config.yaml $WSL_HOME/.hermes/ 2>/dev/null; echo Hermes done"

echo [3/4] Copying Claw memory to WSL...
wsl -d Ubuntu-22.04 -- bash -c "mkdir -p /home/dmin/.claw && cp -f /mnt/c/Users/Admin/hermes-sync/.claw.yaml /mnt/c/Users/Admin/hermes-sync/config.yaml /home/dmin/.claw/ 2>/dev/null; mkdir -p /home/dmin/.claw/memories && cp -rf /mnt/c/Users/Admin/hermes-sync/claw_memories/* /home/dmin/.claw/memories/ 2>/dev/null; echo Claw done"
echo.

echo [4/4] Done!
echo.
echo ==============================================
echo   GitHub data synced to Hermes + Claw
echo ==============================================
echo.
pause
```
```

## ⚠️ Pitfalls

### 1. cmd `cd` 不切盘符
- `cd C:\Users\Admin\hermes-sync` without `/d` DOES NOT switch drive when running from another drive
- **Current fix**: Do git operations in Windows cmd with `cd /d`, NOT inside WSL

### 1.5 🔍 快速诊断表：从错误症状反推根因

当用户反馈同步脚本报错时，先看**错误症状**，按表反查：

| 错误症状 | 最可能根因 | 修复动作 |
|---------|-----------|---------|
| `'同步' 不是内部或外部命令` / `'愨晲鈺...'` / `'鏁版嵁...'` | **CRLF 换行符问题**（LF 而非 CRLF），cmd 把多行当一行解析，中文字节被截成命令名 | 查文件换行符 → Python 重写为 CRLF + ASCII |
| `'?GitHub' 不是内部或外部命令` | **UTF-8 BOM 被当内容解析**。文件开头 `\xef\xbb\xbf` 变成行首字符，导致命令被截断 | 去掉 BOM（`awk 'NR==1{sub(/^\xef\xbb\xbf/,"")}1'`）或用纯 ASCII 重写 |
| `'L' 不是内部或外部命令` (或其它单个字母命令报错) | 中文注释/路径导致行断裂，cmd 把下一个字母当命令名执行 | 去掉所有非 ASCII 字符（中文、线框符号） |
| 同上错误，但文件已经 CRLF | 中文/线框字符（`═┌┐╔╗╚╝`）被 GBK 解析为乱码命令 | 去掉所有非 ASCII 字符，用纯英文 + 简单符号 |
| `'L' 不是内部或外部命令` | 路径中含中文，盘符切换语句断裂 | 去路径/命令中的中文，或用纯 ASCII 路径 |
| `'type' 或其它标准命令报错` | cmd 被乱码行搞坏了状态，重启 cmd 重试 | 先验证文件本身正确（`file *.bat` 显示 DOS batch），再双击运行 |
| `fatal: not a git repository (or any of the parent directories)` | cd 未切换到正确的同步目录（路径不对 或 cd 未跨盘符 `/d`） | 全放 WSL 内 git 操作：`wsl -- bash -c \"cd /mnt/c/... && git ...\"` |
| `fatal: not a git repository` + 后面又有 `To github.com...` | 脚本中有两个 git 命令，一个路径错、一个路径对 | 检查脚本中每个 git 命令的 cd 路径 |
| `! [rejected] main -> main (non-fast-forward)` | 远程有本地没有的提交（另一台电脑推过） | `git pull --rebase origin main` 再推 |
| `wsl: 检测到 localhost 代理配置...NAT 模式` | 仅警告，不影响 HTTPS git 操作 | 忽略 |
| 同步显示 ✓ 完成，但 Hermes 启动 SOUL 是英文默认版 | **WSL 路径写错**（`/root/` 而非 `/home/dmin/`），cp 静默失败 | 排查 .bat 中 WSL_HOME 变量值 |
| `Host key verification failed` | WSL 缺少 GitHub known_hosts | `ssh -o StrictHostKeyChecking=accept-new git@github.com` |

**诊断优先级**：看到乱码型错误 → 先查 CRLF（`file *.bat`）→ 再查编码 → 最后查路径。

### 2. 🔴 CRITICAL: CRLF 换行符（排在第一位的 Bat 文件 Bug）

**症状**: .bat 文件内容正确（无乱码、路径正确），但 cmd 仍然报错，且错误信息包含旧版文件的乱码字符（如 `'愨晲鈺...'`、`'鏁版嵁...'`）。即使反复修改内容，错误完全相同。

**根本原因**: 用 `write_file` 从 WSL 写入 Windows 文件系统时，写入的是 **LF 换行符（Unix 格式，`\n`）**。Windows cmd.exe **必须** 使用 **CRLF 换行符（Windows 格式，`\r\n`）** 才能正确解析 .bat 文件。LF 格式下，cmd 会把整文件当一行解析，导致各行首字符和中间的非英文字符被当命令名执行。

**验证方法**:
```bash
xxd /path/to/file.bat | head -5
# 正确: ...660d 0a63...  ← 0d 0a 是 CRLF
# 错误: ...660a 6368...   ← 0a 后面直接跟字符，缺 0d
# 或用 file 命令看换行符：
file *.bat
#    LF   → "ASCII text" 或 "UTF-8 (with BOM) text"
#    CRLF → "DOS batch file, ASCII text" 或 "DOS batch file, ..., UTF-8 text"
```

**修复方法**: 用 Python 以二进制模式写入，显式指定 `\r\n`：
```python
with open('/path/to/file.bat', 'wb') as f:
    f.write(('\r\n'.join(lines) + '\r\n').encode('ascii'))
```

⚠️ `write_file` 工具默认写 LF — 写 .bat 文件时绝对不要用。必须用 `execute_code` 跑 Python 写入。

### 2.5 🧪 .bat 测试方法：必须双击运行，WSL 内 cmd.exe 测不准

`.bat` 文件的测试方式直接影响诊断结论：

| 测试方式 | 是否可靠 | 原因 |
|---------|---------|------|
| **Windows Explorer 双击** | ✅ 唯一可靠 | 真正的 cmd.exe 运行环境，复现全部编码/路径问题 |
| WSL 内 `cmd.exe /c script.bat` | ❌ 不可靠 | UNC 路径问题可能导致 PATH、当前目录等行为不同 |
| WSL 内 `wsl -- bash -c "cd /mnt/... && cmd.exe /c script.bat"` | ❌ 不可靠 | 同上，且嵌套 shell 层数多 |
| 看代码推理 | ❌ 不可靠 | 编码/换行符问题只在执行时暴露，看代码看不出来 |

**正确流程**：
1. Python 生成 .bat（CRLF + ASCII）到 Windows 桌面
2. 告诉用户：**双击桌面的 .bat 文件运行测试**
3. 用户截图/贴报错回来，你根据诊断表反查

**不要**在 WSL 里 `cmd.exe /c xxx.bat` 测试后说"看起来好了"——实际双击可能完全不一样。

### 3. 中文编码乱码 (UTF-8 vs ASCII)

**症状**: cmd 把 .bat 里的中文读成乱码命令：
- `'同步' 不是内部或外部命令` — 中文字被当命令名解析
- `'愨晲鈺愨晲鈺...'` — UTF-8 字节被 GBK 解码后的经典乱码
- `'鏁版嵁...'` — 同上
- `'L' 不是内部或外部命令` — 路径中的中文乱码导致盘符切换语句断裂

**根本原因**: 两种可能，按排查顺序：
1. **先查换行符**（见上一条 pitfall #2）— 这是最常见的根本原因。换行符错误会导致所有中文行被错误截断和解析。
2. **编码问题本身** — .bat 文件虽然内容存为 UTF-8，但缺少 BOM。Windows cmd 在 `chcp 65001` 设置 UTF-8 代码页后，如果没有 BOM，可能仍用 GBK 解析。

**修复方法**（按优先级）：
1. **✅ 首选: 纯 ASCII + CRLF** — 所有 echo 用英文，不用中文和 Unicode 线框字符。这是唯一在**所有 Windows 系统上 100% 可靠**的方案。
   ```batch
   echo =============================================
   echo   Hermes Sync - Push to GitHub
   echo =============================================
   ```
2. **次选: UTF-8 with BOM + CRLF** — 在文件开头插入 BOM（`\xef\xbb\xbf`），同时确保 CRLF 换行。部分 Windows 系统仍可能失败。
3. **不推荐: GBK/ANSI 编码** — 可以避免 cmd 编码问题，但不支持某些 Unicode 线框字符。

**经验教训**: ⭐ 对于这台特定电脑，纯 ASCII + CRLF 是唯一稳定的方案。不要试图保留中文 echo 或线框字符。

**验证方法**:
```bash
file *.bat
# 纯 ASCII → "DOS batch file, ASCII text, with very long lines"
# UTF-8    → "DOS batch file, Unicode text, UTF-8 (with BOM) text"
```

### 3. git push rejected (non-fast-forward)
- Remote has commits you don't have locally (another PC pushed)
- **Fix**: Always `git pull --rebase origin main` before `git push`

### 4. Merge conflicts in shared config files
- Common conflict files: `README.md`, `memories/MEMORY.md`, `memories/USER.md`, skill files
- These files get edited on both PCs independently
- **Resolution**: Merge both sides — keep all info. MEMORY.md and USER.md are additive knowledge bases, not mutually exclusive.
- For skill files with same content but different line endings (CRLF vs LF): take either side

### 5. GitHub Push Protection (secret scanning)
- If a GitHub Token or API key leaks into a commit, push is blocked
- Symptom: `remote: error: GH013: Repository rule violations found`
- **Fix options**:
  - A) Allow the specific secret via GitHub's unblock URL (safe if token already revoked)
  - B) `git rebase -i --rebase-merges` to edit out the secret, then `git push --force`
- **Prevention**: Never store tokens in synced files like claw_memories/ or MEMORY.md

### 6. `git stash` times out on large repos
- With 900+ modified files (e.g., skills/ directory synced from GitHub), `git stash` times out even at 30s
- **Fix**: Use `git checkout -f main` to force-switch branch and discard working changes instead
- ⚠️ Only safe when changes are synced artifacts that will be regenerated, or already committed elsewhere

### 7. `git rebase --rebase-merges` required for history with merge commits
- Plain `git rebase -i <base>` FLATTENS merge commits, dropping the merge structure
- The correct command is `git rebase -i --rebase-merges <base>` — it preserves merge topology using `label`/`reset`/`merge` in the todo list
- **Error sign**: Rebase appears to skip commits or produces a linear history that's missing merged content

### 8. Cleanup leftover `.git/rebase-merge` and `.git/rebase-apply`
- An interrupted or timed-out rebase leaves `.git/rebase-merge/` directory
- Next rebase fails with: `fatal: It seems that there is already a rebase-merge directory`
- **Fix**: `rm -rf .git/rebase-merge`

### 9. WSL proxy warning
- `wsl: 检测到 localhost 代理配置，但未镜像到 WSL` — harmless, ignore
- Only matters for networking through proxy; git over HTTPS is fine

### 10. SOUL 版本漂移 (WSL vs Git 不一致)
- WSL 的 SOUL.md 可能与 Git 仓库版本不同（例如 WSL 被覆写为英文默认版，而 Git 存的是自定义中文版）
- **Symptom**: 推送上去了，但实际 WSL 跑的不是你要的 SOUL
- **Fix**: 同步后运行验证（见 `references/sync-verification.md`），如果发现差异，先执行拉取脚本还原 WSL 文件

### 11. 🔴 WSL 路径写错 (最隐蔽的 Bug)
- .bat 脚本中 WSL 路径写错成 `/root/.hermes/` 时，cp 命令静默失败（目标不存在但 `2>/dev/null` 掩藏了错误），所有同步操作实际上什么都没拷贝
- **Symptom**: 同步提示 ✓ 完成，但 Hermes 启动时的 SOUL 是英文默认版
- **Detection**: 对比 Git 仓库和 WSL 的文件（见验证脚本）
- **Fix**: 确保 .bat 中 `WSL_HOME` 设置为正确的 home 路径 (`/home/dmin/`), 并使用变量而非硬编码

### 12. WSL Hermes 可执行文件的 shebang 漂移
- `~/.hermes/bin/hermes` 或 `~/*venv*/bin/hermes` 的 shebang 可能指向已删除的 Windows Python 路径
- **Symptom**: `bash: /.../hermes: /mnt/c/.../python3: bad interpreter: No such file or directory`
- **Fix**: 编辑 shebang 行指向当前 WSL venv 中的 Python（例如 `#!/home/dmin/hermes-venv/bin/python3`）
- 注意：即使她本行修复了，如果 `hermes_cli` 模块未安装在 WSL Python 中，Hermes 仍只能从 Windows PowerShell 启动

## Voice Command Shortcuts (在 Hermes Agent 对话中)

用户可以直接对 Hermes Agent 说出快捷指令代替点 .bat 文件：

### 推送github（本地 → GitHub）

```bash
cd /mnt/c/Users/Admin/hermes-sync && \
cp /home/dmin/.hermes/config.yaml SOUL.md SOUL_Pro.md SOUL_Edu.md . && \
cp /home/dmin/.hermes/memories/* memories/ && \
git add -A && git commit -m "sync $(date +%Y-%m-%d)" && git push origin main
```

### 拉取github（GitHub → 本地）

```bash
cd /mnt/c/Users/Admin/hermes-sync && \
git pull origin main && \
cp SOUL.md SOUL_Pro.md SOUL_Edu.md /home/dmin/.hermes/ && \
cp memories/* /home/dmin/.hermes/memories/ && \
cp config.yaml /home/dmin/.hermes/
```

### 网络超时处理

WSL 连接 GitHub 偶尔出现间歇性超时（30s-90s）。策略：
1. **先测试连通性**：`ping -c 3 github.com` — 如果通但 git 超时，重试即可
2. **增加超时时间**：直接调用 `git push` 不带超时选项，默认等
3. **确认 DNS 可用但路由波动**：`ping` 返回 0% loss 但 `git push` 超时 → 重试 1-2 次即可
4. **持久不通**：检查代理设置（`echo $http_proxy`），或切换 WSL 到镜像网络模式

## Post-Sync Verification (同步后验证)

Always verify after sync — don't trust the "✓ 完成" message blindly. The most common failure mode is that the sync runs but WSL files are stale or wrong.

See `references/sync-verification.md` for detailed check commands.

## 同步范围

| 同步 | 不同步 |
|------|--------|
| SOUL.md, SOUL_Pro.md, SOUL_Edu.md | .env（API Key，每台电脑独立） |
| config.yaml | sessions.db（太大） |
| memories/* | state.db |
| skills/* | logs/, checkpoints/ |
| claw_memories/ (WSL Claw) | .hermes_history, auth.json |