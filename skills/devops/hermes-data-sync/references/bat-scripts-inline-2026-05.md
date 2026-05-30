# Inline .bat Scripts (2026-05 实际使用版)

当前用户无 `~/.hermes/sync-push.sh` / `sync-pull.sh`，所有逻辑内置在 .bat 中。
WSL 用户名: `administrator`，主仓库: `C:\Users\Administrator\Desktop\HermesAgent`

## Hermes同步-拉取.bat

```batch
@echo off
echo ===============================================
echo   Hermes Sync - PULL from GitHub
echo ===============================================
echo.

echo [1/3] Pulling latest data from GitHub...
wsl -d Ubuntu -- bash -c "cd /mnt/c/Users/Administrator/Desktop/HermesAgent && git fetch origin main && git reset --hard origin/main"
if %errorlevel% neq 0 (
  echo [ERROR] Pull failed, check network
  pause
  exit /b 1
)
echo.

echo [2/3] Copying to WSL ~/.hermes/...
wsl -d Ubuntu -- bash -c "mkdir -p ~/.hermes/memories ~/.hermes/skills; cp -f /mnt/c/Users/Administrator/Desktop/HermesAgent/SOUL*.md ~/.hermes/ 2>/dev/null; cp -f /mnt/c/Users/Administrator/Desktop/HermesAgent/config.yaml ~/.hermes/ 2>/dev/null; cp -f /mnt/c/Users/Administrator/Desktop/HermesAgent/memories/*.md ~/.hermes/memories/ 2>/dev/null; cp -rf /mnt/c/Users/Administrator/Desktop/HermesAgent/skills/* ~/.hermes/skills/ 2>/dev/null"
echo [HERMES] -> WSL    [OK]
echo.

echo [3/3] Copying Claude Code data...
wsl -d Ubuntu -- bash -c "mkdir -p ~/.claude; cp -f /mnt/c/Users/Administrator/Desktop/ClaudeCode-Sync/settings.json ~/.claude/ 2>/dev/null; cp -rf /mnt/c/Users/Administrator/Desktop/ClaudeCode-Sync/agents ~/.claude/ 2>/dev/null; cp -f /mnt/c/Users/Administrator/Desktop/ClaudeCode-Sync/CLAUDE.md ~/.claude/ 2>/dev/null"
echo [CLAUDE] -> WSL    [OK]
echo.

echo ===============================================
echo   DONE. Hermes + Claude Code synced.
echo ===============================================
pause
```

## Hermes同步-推送.bat

```batch
@echo off
echo ===============================================
echo   Hermes Sync - PUSH to GitHub
echo ===============================================
echo.

echo [1/4] Copying Hermes from WSL...
wsl -d Ubuntu -- bash -c "cp -f ~/.hermes/SOUL*.md /mnt/c/Users/Administrator/Desktop/HermesAgent/ 2>/dev/null; cp -f ~/.hermes/config.yaml /mnt/c/Users/Administrator/Desktop/HermesAgent/ 2>/dev/null; cp -f ~/.hermes/memories/*.md /mnt/c/Users/Administrator/Desktop/HermesAgent/memories/ 2>/dev/null; cp -rf ~/.hermes/skills/* /mnt/c/Users/Administrator/Desktop/HermesAgent/skills/ 2>/dev/null"
if %errorlevel% neq 0 (
  echo [WARN] Hermes copy had issues, continuing...
)
echo.

echo [2/4] Pushing Hermes to GitHub...
wsl -d Ubuntu -- bash -c "
  cd /mnt/c/Users/Administrator/Desktop/HermesAgent && \
  git add -A && \
  git diff --cached --quiet || git commit -m \"sync %date:~0,10% %time:~0,5%\" && \
  git push origin main
"
if %errorlevel% neq 0 (
  echo [ERROR] Hermes push failed (network?), retrying...
  timeout /t 5 /nobreak >nul
  wsl -d Ubuntu -- bash -c "cd /mnt/c/Users/Administrator/Desktop/HermesAgent && git push origin main"
  if %errorlevel% neq 0 (
    echo [ERROR] Push still failed. Run manually later.
    pause
    exit /b 1
  )
)
echo [HERMES] -> GitHub    [OK]
echo.

echo [3/4] Copying Claude Code from WSL...
wsl -d Ubuntu -- bash -c "mkdir -p /mnt/c/Users/Administrator/Desktop/ClaudeCode-Sync; cp -f ~/.claude/settings.json /mnt/c/Users/Administrator/Desktop/ClaudeCode-Sync/ 2>/dev/null; cp -rf ~/.claude/agents /mnt/c/Users/Administrator/Desktop/ClaudeCode-Sync/ 2>/dev/null; cp -f ~/.claude/CLAUDE.md /mnt/c/Users/Administrator/Desktop/ClaudeCode-Sync/ 2>/dev/null"
if %errorlevel% neq 0 (
  echo [WARN] Claude Code copy had issues, continuing...
)
echo.

echo [4/4] Pushing Claude Code to GitHub...
wsl -d Ubuntu -- bash -c "
  cd /mnt/c/Users/Administrator/Desktop/ClaudeCode-Sync && \
  git add -A && \
  git diff --cached --quiet || git commit -m \"sync %date:~0,10% %time:~0,5%\" && \
  git push origin main
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

## 关键差异 vs 文档标准版

| 特征 | 文档标准版 (v2.1) | 用户实际版 (inline) |
|------|-------------------|---------------------|
| 脚本位置 | `~/.hermes/sync-push.sh` | `.bat` 内联 |
| .bat 行数 | 4行 | 30~60行 |
| 双引擎重试 | Windows git.exe → WSL git fallback | 纯 WSL SSH，失败 retry 一次 |
| 支持字符 | 纯 ASCII | 含 emoji/线框字符 |
| Claude Code | 不含 | 含（Hermes + Claude 同步一体） |
| 用户路径 | `Admin` | `Administrator` |
| 拉取方式 | `git pull --rebase` → retry | `git fetch + git reset --hard` |

## 多电脑用户名差异

- 办公室电脑（当前台）: WSL 用户名 `administrator`，文件在 `C:\Users\Administrator\Desktop\`
- 家里电脑: WSL 用户名可能不同（需确认），脚本中的路径需同步修改
- 修正方式: 修改 `.bat` 中所有 `Administrator` 为家里电脑的实际用户名
