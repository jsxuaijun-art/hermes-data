# 办公室电脑 .bat 脚本实例

以下是办公室电脑（Windows用户 Administration，WSL Ubuntu 24.04.4）的实测 .bat 脚本。纯 ASCII，无中文/边框字符，避免编码乱码问题。

## 拉取脚本 (Hermes同步-拉取.bat)

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
echo [OK]
echo.
echo [2/3] Copying to WSL ~/.hermes/ ...
wsl -d Ubuntu -- bash -c "mkdir -p ~/.hermes/memories ~/.hermes/skills; cp -f /mnt/c/Users/Administrator/Desktop/HermesAgent/SOUL*.md ~/.hermes/ 2>/dev/null; cp -f /mnt/c/Users/Administrator/Desktop/HermesAgent/config.yaml ~/.hermes/ 2>/dev/null; cp -f /mnt/c/Users/Administrator/Desktop/HermesAgent/memories/*.md ~/.hermes/memories/ 2>/dev/null; cp -rf /mnt/c/Users/Administrator/Desktop/HermesAgent/skills/* ~/.hermes/skills/ 2>/dev/null; echo 'WSL OK'"
if %errorlevel% neq 0 (
  echo [ERROR] WSL copy failed
  pause
  exit /b 1
)
echo [OK]
echo.
echo [3/3] Done!
echo.
echo -----------------------------------------------
echo  GitHub data synced to this machine.
echo  Hermes is now ready with latest data.
echo -----------------------------------------------
echo.
pause
```

## 推送脚本 (Hermes同步-推送.bat)

```batch
@echo off
chcp 65001 >nul
cls
echo.
echo ===============================================
echo   Hermes Sync - PUSH  [办公室电脑]
echo   WSL -> Local -> GitHub
echo ===============================================
echo.
echo [1/4] Copying from WSL ~/.hermes/ to desktop...
wsl -d Ubuntu -- bash -c "cp -f ~/.hermes/SOUL*.md /mnt/c/Users/Administrator/Desktop/HermesAgent/ 2>/dev/null; cp -f ~/.hermes/config.yaml /mnt/c/Users/Administrator/Desktop/HermesAgent/ 2>/dev/null; cp -f ~/.hermes/memories/*.md /mnt/c/Users/Administrator/Desktop/HermesAgent/memories/ 2>/dev/null; cp -rf ~/.hermes/skills/* /mnt/c/Users/Administrator/Desktop/HermesAgent/skills/ 2>/dev/null; echo 'WSL OK'"
if %errorlevel% neq 0 (
  echo [ERROR] WSL copy failed
  pause
  exit /b 1
)
echo [OK]
echo.
echo [2/4] Committing to Git...
cd /d C:\Users\Administrator\Desktop\HermesAgent
git add -A
git commit -m "sync %date:~0,10% %time:~0,5%" >nul 2>&1
echo [OK]
echo.
echo [3/4] Pushing to GitHub...
wsl -d Ubuntu -- bash -c "cd /mnt/c/Users/Administrator/Desktop/HermesAgent && git push origin main"
if %errorlevel% neq 0 (
  echo [ERROR] Push failed, check network or VPN
  pause
  exit /b 1
)
echo [OK]
echo.
echo [4/4] Done!
echo.
echo -----------------------------------------------
echo  Data pushed to GitHub successfully.
echo  Other machines: run PULL to get latest.
echo -----------------------------------------------
echo.
pause
```

## 生成其他电脑脚本时需替换的参数

| 参数 | 办公室电脑 | 江敏笔记本 |
|------|-----------|-----------|
| WSL 发行版 | `Ubuntu` | `Ubuntu22.04` |
| Windows 用户 | `Administrator` | `jiangmin` |
| 桌面同步目录 | `C:\Users\Administrator\Desktop\HermesAgent` | `C:\Users\jiangmin\Desktop\CLAW` |
| 设备名（标题） | `[办公室电脑]` | `[江敏笔记本]` |
