# Hermes 同步脚本 (推送/拉取)

这两个 .bat 文件放在桌面：`D:\360MoveData\Users\Admin\Desktop\`

- `Hermes同步-推送.bat` — 本地 → GitHub
- `Hermes同步-拉取.bat` — GitHub → 本地

## 关键设计原则

1. **全部 git 操作在 WSL 内执行** — 用 `wsl -d Ubuntu-22.04 -- bash -c "..."` 包裹，避免 Windows cmd 盘符切换、中文编码、CRLF 等问题
2. **中文 commit message 用 Linux date** — `date +%Y-%m-%d` 代替 `%date%`，避免 cmd 把"同步"两个字当命令名解析
3. **空提交保护** — `(git diff --cached --quiet || git commit ...)` 避免没改动时产生空提交
4. **每次推送前 pull --rebase** — 防止 non-fast-forward 拒绝
5. **用 `$WSL_HOME` 变量** — 避免硬编码 `/root/.hermes/` 这种错误路径，两台电脑只改变量值即可复用

## ⚠️ 头号 Bug：WSL 路径写错

```diff
- 错误: wsl -d Ubuntu-22.04 -- bash -c "cp /root/.hermes/SOUL.md ..."
+ 正确: wsl -d Ubuntu-22.04 -- bash -c "WSL_HOME=/home/dmin; cp $WSL_HOME/.hermes/SOUL.md ..."
```

如果写成 `/root/.hermes/`，cp 命令**静默失败**（`2>/dev/null` 吞掉了错误提示脚本，看起来"完成"了，实际什么都没拷贝）。

## ⚠️ 二号 Bug：CRLF 换行符（比编码问题更致命）

```diff
- 错误: 用 write_file 写 .bat → 生成 LF 换行，cmd 无法解析
+ 正确: 用 Python 以二进制模式写，显式指定 \r\n
```

**症状**: 文件内容在 WSL 里 `cat` 看着完全正确，但 cmd 运行时各种乱码错误。即使把中文全部改成英文，错误依然一样。

**原因**: cmd.exe 只能解析 CRLF（`\r\n`）换行的 .bat 文件。`write_file` 工具默认写 Unix LF（`\n`），导致整文件被当一行解析。

**唯一可靠的方法 — Python 二进制写入:**

```python
lines = [
    '@echo off',
    'chcp 65001 >nul',
    'echo [1/4] Step one...',
    '# ... 更多命令 ...',
    'pause',
]
content = '\r\n'.join(lines) + '\r\n'
with open('/mnt/c/Users/Admin/Desktop/script.bat', 'wb') as f:
    f.write(content.encode('ascii'))
```

关键点：
- `'wb'` — 二进制写模式
- `'\r\n'.join(lines)` — 显式 CRLF
- `encode('ascii')` — 不存中文，纯 ASCII 最安全
- 不可用 `write_file` — 它永远生成 LF 换行

## 推送脚本 (`Hermes同步-推送.bat`)

```batch
@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════
echo    数据同步 - 推送到 GitHub
echo ═══════════════════════════════════════
echo.

echo [1/4] 从 WSL 拷贝 Hermes 数据...
wsl -d Ubuntu-22.04 -- bash -c "WSL_HOME=/home/dmin; cp -f $WSL_HOME/.hermes/SOUL.md $WSL_HOME/.hermes/SOUL_Pro.md $WSL_HOME/.hermes/SOUL_Edu.md /mnt/c/Users/Admin/hermes-sync/ 2>/dev/null; cp -rf $WSL_HOME/.hermes/memories/* /mnt/c/Users/Admin/hermes-sync/memories/ 2>/dev/null; cp -rf $WSL_HOME/.hermes/skills/* /mnt/c/Users/Admin/hermes-sync/skills/ 2>/dev/null; cp -f $WSL_HOME/.hermes/config.yaml /mnt/c/Users/Admin/hermes-sync/ 2>/dev/null; echo Hermes done"
echo.

echo [2/4] 拷贝 Claw memory...
wsl -d Ubuntu-22.04 -- bash -c "cp -f /home/dmin/.claw.yaml /home/dmin/.claw/config.yaml /mnt/c/Users/Admin/hermes-sync/ 2>/dev/null; cp -rf /home/dmin/.claw/memories/* /mnt/c/Users/Admin/hermes-sync/claw_memories/ 2>/dev/null; echo Claw done"
echo Claw done
echo.

echo [3/4] 提交并推送到 GitHub...
wsl -d Ubuntu-22.04 -- bash -c "cd /mnt/c/Users/Admin/hermes-sync && git add -A && (git diff --cached --quiet || git commit -m 'sync $(date +%%Y-%%m-%%d)') && git pull --rebase origin main && git push origin main"
echo.

echo [4/4] 完成!
echo.
echo ✓ Hermes 数据 + Claw memory 已同步到 GitHub
echo.
pause
```

注意：bat 文件中的 `%%Y`、`%%m`、`%%d` 是 Windows cmd 环境下对 `%` 的转义写法。cmd 会把 `%%` 解析为单个 `%`，传到 WSL 后就变成 Linux 的 `date +%Y-%m-%d`。

## 拉取脚本 (`Hermes同步-拉取.bat`)

```batch
@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════
echo    数据同步 - 从 GitHub 拉取
echo ═══════════════════════════════════════
echo.

echo [1/4] 从 GitHub 拉取最新数据...
wsl -d Ubuntu-22.04 -- bash -c "cd /mnt/c/Users/Admin/hermes-sync && git pull origin main"
echo.

echo [2/4] 拷贝到 WSL Hermes 目录...
wsl -d Ubuntu-22.04 -- bash -c "WSL_HOME=/home/dmin; cp -f /mnt/c/Users/Admin/hermes-sync/SOUL.md /mnt/c/Users/Admin/hermes-sync/SOUL_Pro.md /mnt/c/Users/Admin/hermes-sync/SOUL_Edu.md $WSL_HOME/.hermes/ 2>/dev/null; mkdir -p $WSL_HOME/.hermes/memories && cp -rf /mnt/c/Users/Admin/hermes-sync/memories/* $WSL_HOME/.hermes/memories/ 2>/dev/null; mkdir -p $WSL_HOME/.hermes/skills && cp -rf /mnt/c/Users/Admin/hermes-sync/skills/* $WSL_HOME/.hermes/skills/ 2>/dev/null; cp -f /mnt/c/Users/Admin/hermes-sync/config.yaml $WSL_HOME/.hermes/ 2>/dev/null; echo Hermes done"
echo.

echo [3/4] 拷贝 Claw memory 到本地...
wsl -d Ubuntu-22.04 -- bash -c "mkdir -p /home/dmin/.claw && cp -f /mnt/c/Users/Admin/hermes-sync/.claw.yaml /mnt/c/Users/Admin/hermes-sync/config.yaml /home/dmin/.claw/ 2>/dev/null; mkdir -p /home/dmin/.claw/memories && cp -rf /mnt/c/Users/Admin/hermes-sync/claw_memories/* /home/dmin/.claw/memories/ 2>/dev/null; echo Claw done"
echo Claw done
echo.

echo [4/4] 完成!
echo.
echo ✓ GitHub 数据已同步到 Hermes + Claw
echo.
pause
```

## 首次设置（办公室电脑）

办公室电脑需额外配置：
1. Git remote auth（Token 或 SSH key）
2. WorkBuddy 路径可能不同（检查 Claw memory 位置）
3. WSL home 路径确认：`echo $HOME` 确认后再写变量

## 已知限制

- WSL NAT 模式下的代理警告：`wsl: localhost 代理配置但未镜像到 WSL` — 可忽略
- WorkBuddy 的路径 `20260424224200` 是时间戳，更新后需改 .bat 中的路径
