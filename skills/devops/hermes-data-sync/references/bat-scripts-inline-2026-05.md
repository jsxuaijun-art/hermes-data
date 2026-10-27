# Inline .bat Scripts (2026-05 → 2026-07 实际使用版)

当前用户无 `~/.hermes/sync-push.sh` / `sync-pull.sh`，所有逻辑内置在 .bat 中。
WSL 用户名: `administrator`，WSL 发行版: `Ubuntu` (无短横线)，主仓库: `C:\\Users\\Administrator\\Desktop\\HermesAgent`

> **⚠️ 2026-07-28 关键修复**: 推送脚本原使用 `cp -rf ~/.hermes/skills/*` 全量拷贝 90 skills (833MB)，跨 WSL→/mnt/c/ 极慢，看起来像卡死在[1/4]。已升级为 `rsync -a` 增量同步。拉取脚本同步升级。详见 pitfall "全量 cp 跨 WSL→/mnt/c/ 拷贝 800MB+ skills 极慢"。

## Hermes同步-拉取.bat (v2, 2026-07-28)

```batch
@echo off
chcp 65001 >nul
echo ===============================================
echo   Hermes Sync - PULL from GitHub
echo ===============================================
echo.

echo [1/3] Pull latest data from GitHub (fetch+reset)...
wsl -d Ubuntu -- bash -c "cd /mnt/c/Users/Administrator/Desktop/HermesAgent && git fetch origin main && git reset --hard origin/main"
if %errorlevel% neq 0 (
  echo [ERROR] Pull failed, check network
  pause
  exit /b 1
)
echo [OK]

echo [2/3] Sync to WSL ~/.hermes/ (rsync)...
wsl -d Ubuntu -- bash -c "
  mkdir -p ~/.hermes/memories ~/.hermes/skills
  rsync -a /mnt/c/Users/Administrator/Desktop/HermesAgent/SOUL*.md ~/.hermes/ 2>/dev/null
  rsync -a /mnt/c/Users/Administrator/Desktop/HermesAgent/config.yaml ~/.hermes/ 2>/dev/null
  rsync -a /mnt/c/Users/Administrator/Desktop/HermesAgent/memories/ ~/.hermes/memories/ 2>/dev/null
  rsync -a --delete /mnt/c/Users/Administrator/Desktop/HermesAgent/skills/ ~/.hermes/skills/ 2>/dev/null
"
if %errorlevel% neq 0 (
  echo [WARN] rsync had issues, continuing...
)
echo [HERMES] -> WSL    [OK]
echo.

echo [3/3] Sync Claude Code data...
wsl -d Ubuntu -- bash -c "
  mkdir -p ~/.claude
  rsync -a /mnt/c/Users/Administrator/Desktop/ClaudeCode-Sync/settings.json ~/.claude/ 2>/dev/null
  rsync -a --delete /mnt/c/Users/Administrator/Desktop/ClaudeCode-Sync/agents/ ~/.claude/agents/ 2>/dev/null
  rsync -a /mnt/c/Users/Administrator/Desktop/ClaudeCode-Sync/CLAUDE.md ~/.claude/ 2>/dev/null
"
if %errorlevel% neq 0 (
  echo [WARN] Claude Code sync had issues, continuing...
)
echo [CLAUDE] -> WSL    [OK]
echo.

echo ===============================================
echo   DONE. Hermes + Claude Code synced.
echo ===============================================
pause
```

## Hermes同步-推送.bat (v2, 2026-07-28)

```batch
@echo off
chcp 65001 >nul
echo ===============================================
echo   Hermes Sync - PUSH to GitHub
echo ===============================================
echo.

echo [1/4] Sync Hermes from WSL to Windows (rsync)...
wsl -d Ubuntu -- bash -c "
  mkdir -p /mnt/c/Users/Administrator/Desktop/HermesAgent/memories
  mkdir -p /mnt/c/Users/Administrator/Desktop/HermesAgent/skills
  rsync -a --info=progress2 ~/.hermes/SOUL*.md /mnt/c/Users/Administrator/Desktop/HermesAgent/ 2>/dev/null
  rsync -a ~/.hermes/config.yaml /mnt/c/Users/Administrator/Desktop/HermesAgent/ 2>/dev/null
  rsync -a ~/.hermes/memories/ /mnt/c/Users/Administrator/Desktop/HermesAgent/memories/ 2>/dev/null
  rsync -a --delete ~/.hermes/skills/ /mnt/c/Users/Administrator/Desktop/HermesAgent/skills/ 2>/dev/null
"
if %errorlevel% neq 0 (
  echo [WARN] rsync had issues, continuing...
)
echo [OK]

echo [2/4] Push Hermes to GitHub...
wsl -d Ubuntu -- bash -c "
  cd /mnt/c/Users/Administrator/Desktop/HermesAgent
  git add -A
  if git diff --cached --quiet; then
    echo '[SKIP] nothing to commit'
  else
    git commit -m \"sync $(date +'%Y-%m-%d %H:%M')\"
    git push origin main
  fi
"
if %errorlevel% neq 0 (
  echo [RETRY] Push failed, retrying...
  timeout /t 3 /nobreak >nul
  wsl -d Ubuntu -- bash -c "cd /mnt/c/Users/Administrator/Desktop/HermesAgent && git push origin main"
  if %errorlevel% neq 0 (
    echo [ERROR] Push still failed. Run manually.
    pause
    exit /b 1
  )
)
echo [HERMES] -> GitHub    [OK]
echo.

echo [3/4] Sync Claude Code from WSL to Windows...
wsl -d Ubuntu -- bash -c "
  mkdir -p /mnt/c/Users/Administrator/Desktop/ClaudeCode-Sync
  rsync -a ~/.claude/settings.json /mnt/c/Users/Administrator/Desktop/ClaudeCode-Sync/ 2>/dev/null
  rsync -a --delete ~/.claude/agents/ /mnt/c/Users/Administrator/Desktop/ClaudeCode-Sync/agents/ 2>/dev/null
  rsync -a ~/.claude/CLAUDE.md /mnt/c/Users/Administrator/Desktop/ClaudeCode-Sync/ 2>/dev/null
"
if %errorlevel% neq 0 (
  echo [WARN] Claude Code sync had issues, continuing...
)
echo [OK]

echo [4/4] Push Claude Code to GitHub...
wsl -d Ubuntu -- bash -c "
  cd /mnt/c/Users/Administrator/Desktop/ClaudeCode-Sync
  git add -A
  if git diff --cached --quiet; then
    echo '[SKIP] nothing to commit'
  else
    git commit -m \"sync $(date +'%Y-%m-%d %H:%M')\"
    git push origin main
  fi
"
if %errorlevel% neq 0 (
  echo [WARN] Claude Code push had issues, continuing...
)
echo [CLAUDE] -> GitHub    [OK]
echo.

echo ===============================================
echo   DONE. Hermes + Claude Code pushed.
echo ===============================================
pause
```

## v1 → v2 改进要点 (2026-07-28)

| 问题 | v1 (旧版) | v2 (新版) |
|------|-----------|-----------|
| 拷贝慢 | `cp -rf ~/.hermes/skills/*` 全量拷贝 833MB，卡死在[1/4] | `rsync -a --delete` 增量同步，只传变更文件，首次有 `--info=progress2` 进度显示 |
| 空提交 | 没变更也会 commit（空的） | `git diff --cached --quiet` 检测无变更时跳过 commit |
| 编码支持 | 无 `chcp 65001`，emoji/线框符在中文 Windows 会乱码 | 加 `chcp 65001 >nul` 启用 UTF-8 |
| 拉取拷贝 | `cp -rf` 全量 | `rsync -a --delete` 增量，确保 WSL 侧删除已移除的文件 |
| Claude 拉取 | `cp -rf` 无 `--delete` | `rsync -a --delete` 一致处理 |

## 关键差异 vs 文档标准版 (v2.1 thin wrapper)

| 特征 | 文档标准版 (v2.1) | 用户实际版 (inline) |
|------|-------------------|---------------------|
| 脚本位置 | `~/.hermes/sync-push.sh` | `.bat` 内联 |
| .bat 行数 | 4行 | ~90行 (含完整逻辑) |
| 双引擎重试 | Windows git.exe → WSL git fallback | 纯 WSL git，失败 retry 一次 |
| 同步策略 | cp 全量 (mk 版)，rsync 增量 (doc 版) | rsync -a (v2 起) |
| Claude Code | 不含 | 含（Hermes + Claude 同步一体） |
| 用户路径 | `Admin` | `Administrator` |
| WSL 发行版 | `Ubuntu-22.04` (带短横线) | `Ubuntu` (无短横线) |
| 拉取方式 | `git pull --rebase` → retry | `git fetch + git reset --hard` (无条件同步) |
| 推送空提交 | 可能产生空提交 | `git diff --cached --quiet` 跳过空提交 |
| 拷贝工具 | `cp -rf` | `rsync -a` |

## 多电脑用户名差异

- 办公室电脑（当前台）: WSL 用户名 `administrator`，WSL 发行版 `Ubuntu`，文件在 `C:\\Users\\Administrator\\Desktop\\`
- 家里电脑: WSL 用户名可能不同（江敏笔记本是 `dmin`/`jiangmin`，发行版 `Ubuntu-22.04`），脚本中的路径需同步修改
- 修正方式: 修改 `.bat` 中所有 `Administrator`、`Ubuntu` 为家里电脑的实际值
