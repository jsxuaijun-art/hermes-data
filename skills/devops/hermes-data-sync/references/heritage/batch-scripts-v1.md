# .bat 同步脚本模板与编码注意事项

> ⚠️ **重要更新（2026-05-10）：** 模板已从「cmd 做全部逻辑」改为「WSL 脚本做全部逻辑，.bat 仅做触发器」。关键改动：去掉了 `chcp 65001`、改用 `-e` 代替 `--`、增加 `2>nul` 吞 WSL stderr。详见下文"V2.1 最终架构"。
>
> ⚠️ **2026-05-11 补充：** 发现 `hermes.bat`（Hermes CLI 启动脚本）未应用 `2>nul` 防护。已在线修复。

## V2.1 最终架构（当前标准）

```
Windows 桌面 .bat（4行纯ASCII）
    │  wsl -d <DistroName> -e bash ~/.hermes/sync-push.sh 2>nul
    ▼
WSL ~/.hermes/sync-push.sh（驱动全部逻辑）
    ├─ cp 数据（本地，瞬间完成）
    ├─ git add+commit（本地，瞬间完成）
    └─ git push  ─┬─ Windows git.exe（走Windows网络栈，快）
                   └─ WSL git（备选引擎，重试5次）
```

**核心设计原则：** 所有逻辑都在 WSL shell 脚本里。.bat 只做一件事——触发 WSL 脚本。

### 推送脚本模板（桌面 .bat）

```batch
@echo off
wsl -d Ubuntu-22.04 -e bash /home/dmin/.hermes/sync-push.sh 2>nul
echo.
echo Hermes push completed.
pause
```

### 拉取脚本模板（桌面 .bat）

```batch
@echo off
wsl -d Ubuntu-22.04 -e bash /home/dmin/.hermes/sync-pull.sh 2>nul
echo.
echo Hermes pull completed.
pause
```

### Hermes CLI 启动脚本模板（桌面 hermes.bat）

⚠️ **此文件之前缺失 `2>nul` 防护，已于 2026-05-11 修复。**

```batch
@echo off
chcp 65001 >nul
wsl -d Ubuntu-22.04 -- bash -c "cd /mnt/c/Users/Admin/WorkBuddy/20260424224200/hermes-agent-official && ./venv/bin/python -m hermes_cli.main chat" 2>nul
```

**与同步脚本的关键区别：**
| 特征 | 同步脚本 | Hermes CLI 启动 |
|------|---------|----------------|
| 用途 | 纯触发器 | 交互式 CLI 会话 |
| `chcp 65001` | ❌ 不需要 | ✅ 保留（确保 UTF-8 终端） |
| `2>nul` | ✅ 必须 | ✅ 必须（吞 WSL 代理警告） |
| `--` vs `-e` | `-e` 更稳 | `--` 保留（兼容长命令） |
| 命令格式 | `-e bash 脚本路径` | `-- bash -c "内联命令"` |

### 对应的 WSL 脚本（`~/.hermes/sync-push.sh`）

```bash
#!/bin/bash
# Hermes Sync - Push to GitHub (hybrid dual-engine)

SYNC_DIR="/mnt/c/Users/<WindowsUser>/hermes-sync"
SYNC_DIR_WIN="C:/Users/<WindowsUser>/hermes-sync"
GIT_WIN="/mnt/c/Program Files/Git/bin/git.exe"

cd "$SYNC_DIR" || exit 1

echo "[1/4] Copy Hermes data from WSL to Windows..."
cp -f /home/dmin/.hermes/SOUL.md /home/dmin/.hermes/SOUL_Pro.md /home/dmin/.hermes/SOUL_Edu.md . 2>/dev/null
cp -rf /home/dmin/.hermes/memories/* memories/ 2>/dev/null
mkdir -p skills && cp -rf /home/dmin/.hermes/skills/* skills/ 2>/dev/null
cp -f /home/dmin/.hermes/config.yaml . 2>/dev/null

echo "[2/4] Copy Claw data from WSL to Windows..."
cp -f /home/dmin/.claw.yaml /home/dmin/.claw/config.yaml . 2>/dev/null
cp -rf /home/dmin/.claw/memories/* claw_memories/ 2>/dev/null

echo "[3/4] Git add + commit..."
git add -A
git commit -m "sync $(date '+%Y-%m-%d_%H:%M')" 2>/dev/null || echo "(nothing to commit)"

echo "[4/4] Git push (2 engines, up to 10 retries)..."
# (push_win + push_wsl functions — see hermes-data-sync skill for full code)
```

### 对应的 WSL 脚本（`~/.hermes/sync-pull.sh`）

```bash
#!/bin/bash
# Hermes Sync - Pull from GitHub (dual-git engine with retry)

SYNC_DIR="/mnt/c/Users/<WindowsUser>/hermes-sync"
SYNC_DIR_WIN="C:/Users/<WindowsUser>/hermes-sync"
GIT_WIN="/mnt/c/Program Files/Git/bin/git.exe"

cd "$SYNC_DIR" || exit 1

echo "[1/4] Git pull from GitHub..."
# (pull_retry + copy logic — see hermes-data-sync skill for full code)
```

> 完整脚本代码见 `hermes-data-sync` 技能（实际部署的、经过测试的版本）。

---

## ⚠️ 编码问题（踩坑实录）

### V1 问题：cmd 直接做 git 操作

**症状：** cmd 执行 `git push` 时，中文路径/提交信息被 GBK 解析为乱码，部分命令失败。

**根因：** cmd.exe 默认编码 GBK (CP936)，而 git 输出/输入是 UTF-8。

### V2 问题：WSL bash 输出回流到 cmd 产生乱码幽灵命令

**症状（这就是你看到的）：**
```
'姝?-' 不是内部或外部命令
'?GitHub' 不是内部或外部命令
'愨晲鈺愨晲鈺echo' 不是内部或外部命令
'鏁版嵁...' 不是内部或外部命令
'L' 不是内部或外部命令
'礉' / '/4]' / '鉁?GitHub' 不是内部或外部命令
```

**根因链：**
1. `wsl` 命令启动时检测到 Windows 代理 → 向 **stderr** 输出中文警告：`wsl: 检测到 localhost 代理配置，但未镜像到 WSL。NAT 模式下的 WSL 不支持 localhost 代理。`
2. 这个 UTF-8 中文文本经过 cmd.exe 回显 → 被 GBK 解码 → 变成乱码字符
3. cmd.exe 把每个乱码片段都当作**命令**去执行 → 弹出一堆报错

**修复方案（V2.1）：**

| 改动 | 说明 |
|------|------|
| `2>nul` | 吞掉 WSL 的 stderr（即代理警告），阻止它回流到 cmd.exe |
| `-e` 代替 `--` | 更简洁的 WSL 命令执行方式（同步脚本用，CLI 启动脚本保留 `--`） |
| 去掉 `chcp 65001` | 不需要——.bat 纯 ASCII 不涉及编码切换（CLI 启动脚本保留） |
| .bat 保持在`<10行` | 只做触发器，全部逻辑放 WSL 脚本 |

**关键规则：**
- `2>nul` 只吞 stderr（警告信息），stdout（`echo` 语句输出）正常显示
- .bat 保持纯 ASCII，不要中文、emoji、线框字符（═ ╔ ╗ ╚ ╝ ┌ ┐ └ ┘）
- 不要在 .bat 里写长内联 bash 命令（如 `wsl -- bash -c "长命令1; 长命令2; ..."`），改由 WSL 脚本驱动
- ⚡ 例外：`hermes.bat`（CLI 启动）保留 `chcp 65001` 和 `-- bash -c "..."`，因为它是交互式终端，但**必须加 `2>nul`**

### 编码诊断速查表

| 错误症状 | 根因 | 修复 |
|---------|------|------|
| `'?GitHub'` / `'愨晲鈺...'` / `'鏁版嵁...'` | WSL stderr 中文回流到 cmd | `.bat` 加 `2>nul` |
| `'L' 不是内部或外部命令` | 中文/线框字符被 GBK 解析为命令 | 去所有非 ASCII 字符 |
| `系统找不到指定的路径` | cd 路径不存在或盘符不切 | WSL 脚本处理路径，不用 cmd cd |
| `'Hermes done' 当做命令执行` | WSL 脚本的 stdout 被 cmd 误解析 | 用 `-e` 代替 `--` |

---

## 最佳实践总结

1. **.bat 纯触发器**：4行纯ASCII，不要做任何复杂操作
2. **逻辑放 WSL**：所有 cp/git/retry 逻辑在 shell 脚本里实现
3. **`2>nul` 是必须的**：任何 .bat 触发 WSL 命令都要加，除非确定 WSL 不会输出任何 stderr
4. **`hermes.bat` 特殊处理**：保留 `chcp 65001` 和 `-- bash -c "..."`，但必须加 `2>nul`
5. **Windows git.exe 做网络操作**：从中国访问 GitHub，Windows git.exe 比 WSL git 快 10-100 倍
6. **双引擎容错**：Windows git.exe 失败→WSL git 重试→提示手动处理

## 参考

- 已部署的完整脚本：`hermes-data-sync` 技能（包含 push/pull 双引擎完整代码 + 13 个踩坑记录）
- 架构演进史：`hermes-data-sync` SKILL.md 中的 v0→v1→v2.1 对比表
- Hermes CLI 启动文件：`D:\360MoveData\Users\Admin\Desktop\Hermes Agent\hermes.bat`
