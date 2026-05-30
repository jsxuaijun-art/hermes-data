# .bat 同步脚本模板与编码注意事项

## 脚本模板

### 拉取脚本 (pull.bat)

```batch
@echo off
chcp 65001 >nul
cls
echo.
echo ===============================================
echo    Hermes Sync - Pull from GitHub
echo ===============================================
echo.
echo [1/3] Pulling latest data from GitHub...
wsl -d <DistroName> -- bash -c "cd /mnt/c/Users/<WindowsUser>/Desktop/HermesAgent && git pull origin main"
if %errorlevel% neq 0 (
  echo [ERROR] Pull failed, check network
  pause
  exit /b 1
)
echo [OK]
echo.
echo [2/3] Copying to WSL ~/.hermes/ ...
wsl -d <DistroName> -- bash -c "cp -f /mnt/c/Users/<WindowsUser>/Desktop/HermesAgent/SOUL*.md ~/.hermes/ 2>/dev/null; cp -f /mnt/c/Users/<WindowsUser>/Desktop/HermesAgent/config.yaml ~/.hermes/ 2>/dev/null; mkdir -p ~/.hermes/memories; cp -f /mnt/c/Users/<WindowsUser>/Desktop/HermesAgent/memories/*.md ~/.hermes/memories/ 2>/dev/null; mkdir -p ~/.hermes/skills; cp -rf /mnt/c/Users/<WindowsUser>/Desktop/HermesAgent/skills/* ~/.hermes/skills/ 2>/dev/null; echo 'WSL OK'"
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
echo  You can now start Hermes with latest data.
echo -----------------------------------------------
echo.
pause
```

### 推送脚本 (push.bat)

```batch
@echo off
chcp 65001 >nul
cls
echo.
echo ===============================================
echo    Hermes Sync - Push to GitHub
echo ===============================================
echo.
echo [1/4] Copying from WSL ~/.hermes/ to desktop...
wsl -d <DistroName> -- bash -c "cp -f ~/.hermes/SOUL*.md /mnt/c/Users/<WindowsUser>/Desktop/HermesAgent/ 2>/dev/null; cp -f ~/.hermes/config.yaml /mnt/c/Users/<WindowsUser>/Desktop/HermesAgent/ 2>/dev/null; cp -f ~/.hermes/memories/*.md /mnt/c/Users/<WindowsUser>/Desktop/HermesAgent/memories/ 2>/dev/null; cp -rf ~/.hermes/skills/* /mnt/c/Users/<WindowsUser>/Desktop/HermesAgent/skills/ 2>/dev/null; echo 'WSL OK'"
if %errorlevel% neq 0 (
  echo [ERROR] WSL copy failed
  pause
  exit /b 1
)
echo [OK]
echo.
echo [2/4] Committing to Git...
cd /d C:\Users\<WindowsUser>\Desktop\HermesAgent
git add -A
git commit -m "sync %date:~0,10% %time:~0,5%" >nul 2>&1
echo [OK]
echo.
echo [3/4] Pushing to GitHub...
wsl -d <DistroName> -- bash -c "cd /mnt/c/Users/<WindowsUser>/Desktop/HermesAgent && git push origin main"
if %errorlevel% neq 0 (
  echo [ERROR] Push failed, check network
  pause
  exit /b 1
)
echo [OK]
echo.
echo [4/4] Done!
echo.
echo -----------------------------------------------
echo  Data pushed to GitHub successfully.
echo  At home, double-click the PULL script to sync.
echo -----------------------------------------------
echo.
pause
```

## ⚠️ 编码问题（踩坑核心）

**问题现象：** 双击 .bat 文件后出现大量乱码错误，如：

```
'tHub' 不是内部或外部命令
'鎴?echo.' 不是内部或外部命令
'攢鈹€鈹€鈹€...echo' 不是内部或外部命令
```

**根因：** 用 `write_file` 工具或 `cp` 从 WSL 写入 Windows 桌面的 .bat 文件，保存为 **UTF-8 without BOM**。但 cmd.exe 启动时以 ANSI/GBK (CP936) 解析文件，包含中文字符或 Unicode 边框符号（═┌┐╔╗╚╝）的行会被解析成乱码碎片，导致整行失效。

**解决方案（二选一）：**

### 方案 A：纯英文 + 简单符号（推荐，最可靠）
- 所有 echo 内容只用纯 ASCII：英文 + 数字 + 符号（- = / _ 等）
- 不用中文字符
- 不用边框字符（═ ┌ ┐ └ ┘ ═ ║ ╔ ╗ ╚ ╝ 等）
- 保存为 UTF-8 without BOM 照样正常工作

### 方案 B：UTF-8 with BOM（保留中文）
- 文件开头必须有 3 字节 BOM：`\xEF\xBB\xBF`
- 从 WSL 写入时需要用 Python 或 `printf` 先写 BOM 再写内容
- 示例（Python）：
```python
bom = b'\xef\xbb\xbf'
content = '你的中文脚本内容...'
with open('script.bat', 'wb') as f:
    f.write(bom + content.encode('utf-8'))
```
- cmd.exe 看到 BOM 后自动切换 UTF-8 模式，中文字符正常显示

### 不推荐的做法
- ❌ UTF-8 without BOM + 中文/特殊符号 → 乱码
- ❌ ANSI/GBK 编码 + `chcp 65001` → chcp 执行前就已乱码
