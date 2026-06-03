# Hermes 数据同步 - 办公室电脑配置指南

## 前提条件
- 办公室电脑已安装 WSL2 + Ubuntu 22.04 + Hermes Agent
- 有 GitHub 账号：jsxuaijun-art
- GitHub Token：YOUR_GITHUB_TOKEN_HERE（到 https://github.com/settings/tokens 创建）

## 第一步：在办公室电脑克隆数据仓库

打开 PowerShell 或 Windows Terminal，执行：

```powershell
cd C:\Users\Admin
git clone https://YOUR_GITHUB_TOKEN_HERE@github.com/jsxuaijun-art/hermes-data.git hermes-sync
```

## 第二步：把数据拷贝到 Hermes 目录

```powershell
wsl -d Ubuntu-22.04 -- bash -c "
  cp -f /mnt/c/Users/Admin/hermes-sync/SOUL.md /root/.hermes/
  cp -f /mnt/c/Users/Admin/hermes-sync/SOUL_Pro.md /root/.hermes/
  cp -f /mnt/c/Users/Admin/hermes-sync/SOUL_Edu.md /root/.hermes/
  mkdir -p /root/.hermes/memories
  cp -rf /mnt/c/Users/Admin/hermes-sync/memories/* /root/.hermes/memories/
  mkdir -p /root/.hermes/skills
  cp -rf /mnt/c/Users/Admin/hermes-sync/skills/* /root/.hermes/skills/
  cp -f /mnt/c/Users/Admin/hermes-sync/config.yaml /root/.hermes/
  echo 'Hermes data done!'
"
```

## 第三步：把 Claw memory 拷贝到工作区

```powershell
robocopy "C:\Users\Admin\hermes-sync\claw-memory" "C:\Users\Admin\WorkBuddy\20260424224200\.workbuddy\memory" /MIR /R:3 /W:1
```

## 第四步：创建同步脚本（放桌面）

### 推送脚本：`Hermes同步-推送.bat`
```
@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════
echo    Hermes+Claw 数据同步 - 推送到云端
echo ═══════════════════════════════════════
echo.
echo [1/3] 从 WSL 拷贝 Hermes 数据...
wsl -d Ubuntu-22.04 -- bash -c "cp -f /root/.hermes/SOUL.md /root/.hermes/SOUL_Pro.md /root/.hermes/SOUL_Edu.md /mnt/c/Users/Admin/hermes-sync/ 2>/dev/null; cp -rf /root/.hermes/memories/* /mnt/c/Users/Admin/hermes-sync/memories/ 2>/dev/null; cp -rf /root/.hermes/skills/* /mnt/c/Users/Admin/hermes-sync/skills/ 2>/dev/null; cp -f /root/.hermes/config.yaml /mnt/c/Users/Admin/hermes-sync/ 2>/dev/null; echo 'Copy done'"
echo.
echo [2/3] 拷贝 Claw memory...
robocopy "C:\Users\Admin\WorkBuddy\20260424224200\.workbuddy\memory" "C:\Users\Admin\hermes-sync\claw-memory" /MIR /R:3 /W:1 >nul
echo 提交并推送...
wsl -d Ubuntu-22.04 -- bash -c "cd /mnt/c/Users/Admin/hermes-sync && git add -A && (git diff --cached --quiet || git commit -m 'sync $(date +%Y-%m-%d)') && git pull --rebase origin main && git push origin main"
echo.
echo [3/3] 完成!
echo.
echo ✓ Hermes + Claw 数据已同步到 GitHub
echo.
pause
```

### 拉取脚本：`Hermes同步-拉取.bat`
```
@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════
echo    Hermes+Claw 数据同步 - 从云端拉取
echo ═══════════════════════════════════════
echo.
echo [1/3] 从 GitHub 拉取最新数据...
wsl -d Ubuntu-22.04 -- bash -c "cd /mnt/c/Users/Admin/hermes-sync && git pull origin main"
echo.
echo [2/3] 拷贝到 WSL Hermes 目录...
wsl -d Ubuntu-22.04 -- bash -c "cp -f /mnt/c/Users/Admin/hermes-sync/SOUL.md /mnt/c/Users/Admin/hermes-sync/SOUL_Pro.md /mnt/c/Users/Admin/hermes-sync/SOUL_Edu.md /root/.hermes/ 2>/dev/null; mkdir -p /root/.hermes/memories && cp -rf /mnt/c/Users/Admin/hermes-sync/memories/* /root/.hermes/memories/ 2>/dev/null; mkdir -p /root/.hermes/skills && cp -rf /mnt/c/Users/Admin/hermes-sync/skills/* /root/.hermes/skills/ 2>/dev/null; cp -f /mnt/c/Users/Admin/hermes-sync/config.yaml /root/.hermes/ 2>/dev/null; echo 'Copy done'"
echo.
echo 拷贝 Claw memory 到工作区...
robocopy "C:\Users\Admin\hermes-sync\claw-memory" "C:\Users\Admin\WorkBuddy\20260424224200\.workbuddy\memory" /MIR /R:3 /W:1 >nul
echo.
echo [3/3] 完成!
echo.
echo ✓ Hermes + Claw 数据已从 GitHub 同步到本地
echo.
pause
```

## 日常使用流程

```
家里电脑用完 Hermes
    ↓ 双击「Hermes同步-推送.bat」
GitHub 云端（自动同步）
    ↓ 到办公室后双击「Hermes同步-拉取.bat」
办公室电脑 Hermes（数据已同步）
    ↓
办公室用完 Hermes
    ↓ 双击「Hermes同步-推送.bat」
GitHub 云端（自动同步）
    ↓ 回家后双击「Hermes同步-拉取.bat」
家里电脑 Hermes（数据已同步）
```

## 注意事项

1. **两台电脑不要同时编辑同一文件**，否则会产生冲突
2. **建议每次换电脑前先推送，换电脑后先拉取**
3. **Token 过期了**需要去 https://github.com/settings/tokens 重新生成
4. **不同步的内容**：.env（API Key）、sessions.db（会话记录）、logs
5. 如果遇到冲突，执行 `git stash` 暂存本地修改，然后 `git pull`，再手动合并
