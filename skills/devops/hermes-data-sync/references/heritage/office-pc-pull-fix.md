# Session Reference: 办公室电脑拉取脚本修复 (2026-05-11)

## 背景

办公室电脑（WSL Ubuntu, Administrator 用户）的 `Hermes同步-拉取.bat` 使用了 `git pull origin main`，但本地仓库 `skills/` 目录有 30 个未提交的改动（上次推送网络失败留下的脏文件），导致 pull 失败：

```
error: Your local changes to the following files would be overwritten by merge:
        skills/apple/DESCRIPTION.md
        skills/apple/apple-notes/SKILL.md
        ...
Please commit your changes or stash them before you merge.
Aborting
```

## 办公室电脑环境

| 项目 | 值 |
|------|-----|
| WSL 发行版 | Ubuntu (no version suffix in wsl config) |
| WSL 用户名 | administrator |
| Windows 用户名 | Administrator |
| 同步仓库路径 | `/mnt/c/Users/Administrator/Desktop/HermesAgent/` |
| .bat 路径 | `/mnt/c/Users/Administrator/Desktop/Hermes同步-拉取.bat` |
| 架构风格 | **内联型**（非标准 v2.1 的 sync-pull.sh 模式） |

## 修复前脚本

```batch
@echo off
chcp 65001 >nul
cls
echo.
echo ===============================================
echo   Hermes Sync - PULL  [办公室电脑]
echo   GitHub -> Local -> WSL
echo ===============================================
echo.
echo [1/3] Pulling latest data from GitHub...
wsl -d Ubuntu -- bash -c "cd /mnt/c/Users/Administrator/Desktop/HermesAgent && git pull origin main"
if %errorlevel% neq 0 (
  echo [ERROR] Pull failed, check network or VPN
  pause
  exit /b 1
)
...
```

## 修复步骤

1. **手动恢复**：进入仓库 `cd /mnt/c/Users/Administrator/Desktop/HermesAgent`，执行：

```bash
git stash push -m "local skills changes before pull $(date)"
git pull origin main
git stash drop
```

2. **复制到 WSL**：然后手动执行脚本的步骤 2：

```bash
mkdir -p ~/.hermes/memories ~/.hermes/skills
cp -f HermesAgent/SOUL*.md ~/.hermes/
cp -f HermesAgent/config.yaml ~/.hermes/
cp -f HermesAgent/memories/*.md ~/.hermes/memories/
cp -rf HermesAgent/skills/* ~/.hermes/skills/
```

3. **修改脚本**：将 `git pull origin main` 改为 `git fetch origin main && git reset --hard origin/main`

## 修复后脚本

```batch
@echo off
chcp 65001 >nul
cls
echo.
echo ===============================================
echo   Hermes Sync - PULL  [办公室电脑]
echo   GitHub -> Local -> WSL
echo ===============================================
echo.
echo [1/3] Fetching latest data from GitHub...
wsl -d Ubuntu -- bash -c "cd /mnt/c/Users/Administrator/Desktop/HermesAgent && git fetch origin main && git reset --hard origin/main"
if %errorlevel% neq 0 (
  echo [ERROR] Fetch failed, check network or VPN
  pause
  exit /b 1
)
echo [OK]
...
```

## 验证方法

同步后检查关键文件一致性：

```bash
# 检查仓库头
cd /mnt/c/Users/Administrator/Desktop/HermesAgent && git log --oneline -1

# 对比 SOUL.md 
diff <(md5sum HermesAgent/SOUL.md | cut -d' ' -f1) <(md5sum ~/.hermes/SOUL.md | cut -d' ' -f1)

# 检查新增技能是否到位
ls ~/.hermes/skills/devops/hermes-data-sync/SKILL.md

# 检查 WSL skills 数量
ls -d ~/.hermes/skills/*/ | wc -l
```

## 核心教训

- `git pull` 遇到 dirty working tree 必死，无论是否加 `--rebase`
- `git fetch origin main && git reset --hard origin/main` 更健壮——无条件同步到远程最新
- 这个仓库是镜像中转站，不是开发分支，`reset --hard` 完全适合
- 如果确实需要保留本地改动，先用 `git stash` 保护再处理
- 多台电脑可能有不同架构风格的 .bat 文件（标准型 vs 内联型），修复方法相同但修改位置不同
