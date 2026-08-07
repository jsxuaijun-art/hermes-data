# Windows 侧 Hermes 升级实录（2026.8.7，v0.15.1 → v0.20.0）

## 背景

用户 WSL 与 Windows 两侧各有一套 Hermes。WSL 侧升级完成后，Windows 侧（
`C:\Users\Administrator\.hermes\hermes-agent\`）仍是旧版，且 gateway 可能从 Windows 侧跑，
需要同步升级。

## Windows 侧环境事实（本次实测）

- 安装目录：`C:\Users\Administrator\.hermes\hermes-agent\`（**纯源码目录**，无用户数据混入）
- git remote 是官方源 SSH：`git@github.com:NousResearch/hermes-agent.git`（SSH 走不通时可无视，直接用 tarball 覆盖）
- **用户数据全在 `C:\Users\Administrator\.hermes\` 主目录**（SOUL.md、config.yaml、memories/、skills/、cron/），
  hermes-agent 目录可整体覆盖源码，无 rsync 排除清单负担
- venv 是 **uv 创建的**（`venv/pyvenv.cfg` 里 `uv = 0.11.16`，home 指向
  `C:\Users\Administrator\AppData\Roaming\uv\python\cpython-3.11-...`）
  → **uv venv 没有 pip.exe**，必须用 `uv pip install`
- Python 3.11.15（满足 v0.20 要求）

## ⚠️ 三个致命的执行层陷阱（本次踩坑）

### 陷阱 1：cmd.exe 从 WSL 调用必失败（UNC 路径）

从 WSL 里跑 `cmd.exe /c "cd /d C:\... && ..."` 会输出乱码警告
`'\\wsl.localhost\Ubuntu\home\administrator\hermes-agent' 不是内部或外部命令`，
后续命令根本不执行。根因：WSL 的 CWD 是 UNC 路径（`\\wsl.localhost\...`），cmd.exe 拒绝以 UNC 为当前目录。

**不要用 cmd.exe。** 用 `powershell.exe` + `Start-Process`（见下）。

### 陷阱 2：WSL interop 直接调 Windows .exe 会挂起/无输出

```bash
# ❌ 直接跑 .exe：要么超时（exit 124），要么 exit 0 但无任何 stdout
/mnt/c/Users/Administrator/.hermes/hermes-agent/venv/Scripts/hermes.exe --version
# ❌ powershell 内联 -c 带引号代码：Start-Process 的 -ArgumentList 引号解析会坏
```

**✅ 可靠模式：脚本落盘 + Start-Process + 结果写文件，再回 WSL 读文件**

```bash
# 1. WSL 侧写 .py 脚本（Windows 可见路径）
#    脚本内容：subprocess.run 调目标 exe，把 stdout/stderr 写进 txt 文件
```

```python
# run_hermes.py（放 C:\Users\Administrator\.hermes\ 下）
import subprocess
r = subprocess.run(
    [r"C:\Users\Administrator\.hermes\hermes-agent\venv\Scripts\hermes.exe", "--version"],
    capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=90
)
with open(r"C:\Users\Administrator\.hermes\result.txt", "w", encoding="utf-8") as f:
    f.write("EXIT: " + str(r.returncode) + "\n" + (r.stdout or "") + "\n" + (r.stderr or ""))
```

```bash
# 2. powershell 执行该脚本
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "
\$venv = 'C:\Users\Administrator\.hermes\hermes-agent\venv\Scripts\python.exe'
\$script = 'C:\Users\Administrator\.hermes\run_hermes.py'
\$p = Start-Process -FilePath \$venv -ArgumentList \$script -Wait -NoNewWindow -PassThru
Write-Output ('exit: ' + \$p.ExitCode)"

# 3. 回 WSL 读结果文件
cat /mnt/c/Users/Administrator/.hermes/result.txt
```

要点：
- **永远用脚本文件（.py 或 .ps1）代替内联代码** —— Start-Process -ArgumentList 传内联代码引号必坏
- **python 直接写文件代替 stdout 重定向** —— -RedirectStandardOutput 有时空文件
- Start-Process 传参格式：`-FilePath <exe> -ArgumentList <script_path> -Wait -NoNewWindow -PassThru`

### 陷阱 3：中文 Windows 输出 GBK 编码

Windows 中文系统默认 GBK，subprocess 读 stdout 不指定编码会 `UnicodeDecodeError: 'gbk' codec`。
必须 `encoding="utf-8", errors="replace"`。

## 升级步骤（验证可行）

### 1. 同步源码（tarball 已由 WSL 侧下载并解压到 /tmp）

```bash
cd /mnt/c/Users/Administrator/.hermes/hermes-agent
rsync -a \
  --exclude='.git/' --exclude='venv/' --exclude='node_modules/' \
  --exclude='hermes_agent.egg-info/' --exclude='__pycache__/' \
  --exclude='log.txt' --exclude='sqlite_leak_fix.png' \
  /tmp/hermes-agent-2026.8.3/ .
grep -m1 '^version' pyproject.toml   # → version = "0.20.0"
```

### 2. 装依赖（uv，无 pip.exe）

```bash
# uv 在 Windows 侧：/mnt/c/Users/Administrator/.local/bin/uv.exe
/mnt/c/Users/Administrator/.local/bin/uv.exe pip install -e "C:\Users\Administrator\.hermes\hermes-agent" \
  --python "C:\Users\Administrator\.hermes\hermes-agent\venv\Scripts\python.exe" \
  --index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

注意：uv.exe 从 WSL 调用可能**静默 exit 0 但不做任何事**（editable 记录仍是旧版本号）。
验证方式：看 site-packages 里 dist-info 的 mtime / Version，或直接跑 hermes.exe --version 看结果文件。

### 3. venv 损坏时重建（本次遇到）

症状：`venv\Scripts\python.exe` 跑任何东西都是 `ExitCode: -1073741515`（= 0xC0000135 STATUS_DLL_NOT_FOUND）。
基础 uv python（AppData\Roaming\uv\python\...）正常，venv 的 python.exe 引用的 DLL 找不到了。
修复 = 重建 venv：

```bash
mv venv venv.old   # 备份（确认新 venv 可用后可删）
/mnt/c/Users/Administrator/.local/bin/uv.exe venv "C:\Users\Administrator\.hermes\hermes-agent\venv" --python 3.11
# → Using CPython 3.11.15
# 再执行步骤 2 的 uv pip install
```

### 4. config migrate + 验证

```bash
# 同「脚本落盘 + Start-Process + 读文件」模式跑：
hermes.exe config migrate
hermes.exe config check   # → Config version: 33 ✓
hermes.exe --version      # → Hermes Agent v0.20.0 (2026.8.3) | Python: 3.11.15 | OpenAI SDK: 2.24.0
```

## 快速诊断速查

| 现象 | 判定 |
|------|------|
| cmd.exe 输出 UNC 乱码警告 | 换 powershell.exe，别修 cmd |
| .exe 直接跑 exit 0 无输出 / 超时 124 | WSL interop 管道问题，走脚本落盘模式 |
| Start-Process 报 ParameterBindingValidationError | -ArgumentList 内联代码引号坏，改脚本文件 |
| python.exe 全挂 `-1073741515` | venv 损坏（DLL 找不到），uv 重建 venv |
| UnicodeDecodeError gbk | subprocess 加 encoding="utf-8", errors="replace" |
| uv pip 静默 exit 0 但没装 | 验证 site-packages dist-info / 结果文件，必要时重建 venv 重装 |
