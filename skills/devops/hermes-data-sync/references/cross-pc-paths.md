# Cross-PC Path Reference

## ⚠️ 关键差异：WSL 用户名

家里和办公室两边的 WSL 用户名、home 路径**不同**。.bat 脚本中的 WSL 路径必须对应正确，否则 cp 命令静默失败。

## 家里电脑 (Home PC)

| Item | Path |
|------|------|
| Windows username | `Admin` |
| WSL distribution | `Ubuntu-22.04` |
| WSL username | `dmin` (NOT `admin`; NOT root) |
| WSL home | `/home/dmin/` |
| WSL ~/.hermes | `/home/dmin/.hermes/` |
| Sync directory | `C:\Users\Admin\hermes-sync\` |
| WSL path to sync dir | `/mnt/c/Users/Admin/hermes-sync/` |
| Desktop scripts | `D:\360MoveData\Users\Admin\Desktop\Hermes同步-推送.bat`, `Hermes同步-拉取.bat` |
| Hermes venv (WSL) | `/home/dmin/hermes-venv/bin/hermes` (shebang broken; use PowerShell to launch) |
| Hermes venv (WSL, alt) | `/home/dmin/venv/bin/hermes` (shebang broken; use PowerShell to launch) |
| PowerShell Hermes | Via PowerShell 7.6.1 — runs in Windows Python, not WSL Python |
| WorkBuddy memory | `C:\Users\Admin\WorkBuddy\20260424224200\.workbuddy\memory\` |

### 路径验证 commands

```bash
# 在 WSL 内检查
echo $HOME          # 应输出 /home/dmin
whoami              # 应输出 dmin
stat ~/.hermes/SOUL.md  # 确认所有者是 dmin
ls -la /root/.hermes 2>/dev/null && echo "⚠️ /root/.hermes 存在！同步脚本可能写错位置" || echo "✅ /root/.hermes 不存在（正确）"
```

## 办公室电脑 (Office PC)

| Item | Path |
|------|------|
| Windows username | `Administrator` |
| WSL distribution | `Ubuntu` (24.04) |
| WSL username | (unconfirmed — likely `administrator`) |
| WSL home | `/home/administrator/` (likely) |
| Sync directory | `C:\Users\Administrator\Desktop\HermesAgent\` |
| WSL path to sync dir | `/mnt/c/Users/Administrator/Desktop/HermesAgent/` |

## Key Differences Affecting .bat Scripts

- WSL distribution name: `Ubuntu-22.04` (home) vs `Ubuntu` (office)
- Windows username: `Admin` (home) vs `Administrator` (office)
- WSL username: `dmin` (home) vs likely `administrator` (office)
- WSL home path: `/home/dmin/` (home) vs `/home/administrator/` (office)
- Sync directory: `hermes-sync\` (home) vs `HermesAgent\` (office)
- Token auth (home) vs SSH key auth (office) for git

> 💡 Tip: Use a `$WSL_HOME` variable at the top of .bat scripts so both PCs can reuse the same template with just the variable changed.
