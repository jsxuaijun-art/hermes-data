@echo off
chcp 65001 >nul
echo 正在创建桌面快捷方式...
cd /d "%~dp0"
wscript.exe create_shortcut.vbs
pause
