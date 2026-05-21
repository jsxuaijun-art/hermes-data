@echo off
chcp 65001 >nul
echo ========================================
echo   苏州盈信 - 合规文书生成器
echo ========================================
echo.

set SCRIPT_DIR=%~dp0
set SKILL_DIR=%SCRIPT_DIR%..\
set PY_SCRIPT=%SCRIPT_DIR%generate_compliance_docs.py

if not exist "%PY_SCRIPT%" (
    echo [错误] 找不到脚本文件: %PY_SCRIPT%
    echo.
    echo 请检查文件是否存在。
    pause
    exit /b 1
)

echo 正在启动文书生成程序...
echo.
python "%PY_SCRIPT%"
if %errorlevel% neq 0 (
    echo.
    echo [提示] 运行出错。可能原因：
    echo   1. 未安装 Python（需要安装 Python 3）
    echo   2. Python 不在系统 PATH 中
    echo.
    echo 若未安装 Python，请访问 https://www.python.org/downloads/ 下载安装
    echo 安装时请勾选 "Add Python to PATH"
)
pause
