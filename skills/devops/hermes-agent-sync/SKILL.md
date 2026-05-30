---
name: hermes-agent-sync
category: devops
description: Cross-machine Hermes Agent data sync via GitHub — bidirectional sync of SOUL.md, memories, skills, config between WSL ~/.hermes/ and Windows, backed by a private GitHub repo. Includes push/pull script generation and path-mismatch troubleshooting.
triggers:
  - User asks to sync Hermes Agent data across computers
  - User mentions multi-machine setup (办公室/家里)
  - User wants to back up or restore Hermes Agent configuration
  - User's sync scripts aren't working (path mismatch, permissions, timeout)
---

# Hermes Agent 跨电脑数据同步

## 架构概览

```
┌─────────────┐     git push/pull      ┌─────────────┐
│  办公室电脑   │  ◄──────────────►      │  家里电脑    │
│  (本机)      │       GitHub 云端       │  (远程)      │
│             │     (私有仓库)            │             │
│ WSL ~/.hermes│                        │ WSL ~/.hermes│
│     ↕       │                        │     ↕       │
│ Windows 桌面  │                        │ Windows 桌面 │
│ sync目录     │                        │ sync目录     │
└─────────────┘                        └─────────────┘
```

## 同步的文件与规则

### 同步（双向）
| 文件/目录 | 说明 |
|-----------|------|
| `SOUL.md` | AI 身份定义（核心） |
| `SOUL_Pro.md` | Pro 版身份（如适用） |
| `SOUL_Edu.md` | Edu 版身份（如适用） |
| `config.yaml` | Hermes Agent 配置 |
| `memories/` | 记忆文件（MEMORY.md, USER.md 等） |
| `skills/` | 自定义技能包 |

### 不同步（保留本地）
- `.env` — API Keys（每台电脑不同）
- `sessions/` — 会话历史 JSON 文件（增长快，每天 ~200~500KB）
- `state.db` — 会话搜索索引 SQLite DB（随 sessions 同步增长）
- `*.db-shm`, `*.db-wal` — SQLite 辅助文件
- `logs/` — 日志
- `caches/` — 缓存
- `checkpoints/` — 检查点

> ⚠️ **为什么不同步 sessions？** 三个月后 sessions 目录可达 50~100MB，git 存二进制大文件效率极低，每次 push 上传整个文件。核心"训练成果"（SOUL.md + memories + skills）一共才 ~120KB，重装后 1 分钟恢复，会话历史只是锦上添花。

## 常见问题 FAQ

### Q: 电脑重装系统了，之前投喂 Hermes 的所有数据还在吗？

**在。** 数据存在 GitHub 私有仓库里，不是本地。重装后：
1. 装 WSL + Hermes Agent（5 分钟）
2. `git clone git@github.com:<Owner>/<Repo>.git`（1 分钟）
3. 把 SOUL.md + memories + skills + config.yaml 复制到 `~/.hermes/`（1 分钟）

然后 Hermes 就是之前投喂完的状态——公司信息、案例、偏好、技能包全在。

**真正丢失的是：**
- `sessions/`（历史聊天记录）→ 不同步，重装后看不到之前的对话
- `.env`（API Key）→ 不同步，但从 DeepSeek/OpenAI 后台重新查就行

**所以核心原则：放心训练，GitHub 兜底。**

## 前置条件

### 1. SSH Key 设置（用于 git push/pull）
```powershell
# 检查 Windows 侧是否有 SSH Key
ls C:\Users\<WindowsUser>\.ssh\

# 如果没有，生成一个新的
ssh-keygen -t ed25519 -C "your-github-email"

# 复制公钥到 GitHub：https://github.com/settings/keys

# 复制到 WSL（关键步骤！）
wsl -d <DistroName> -- bash -c "
  mkdir -p ~/.ssh
  cp /mnt/c/Users/<WindowsUser>/.ssh/id_ed25519 ~/.ssh/
  cp /mnt/c/Users/<WindowsUser>/.ssh/id_ed25519.pub ~/.ssh/
  cp /mnt/c/Users/<WindowsUser>/.ssh/known_hosts ~/.ssh/ 2>/dev/null
  chmod 600 ~/.ssh/id_ed25519
  echo 'SSH key copied to WSL'
"

# 验证连接
wsl -d <DistroName> -- ssh -T git@github.com
# 预期输出: "Hi <username>! You've successfully authenticated"
```

> ⚠️ **常见坑**: 即使 Windows 侧有 SSH Key，WSL 侧默认没有。必须手动复制到 `~/.ssh/` 并设置 `chmod 600`，否则 `git push` 会报 `Host key verification failed`。

### 2. 确认环境信息
```powershell
# 查看 WSL 发行版名称（用于替换 <DistroName>）
wsl -l -v

# 查看 Windows 用户名（用于替换 <WindowsUser>）
dir C:\Users\
```

**注意替换以下变量：**
| 变量 | 说明 | 本机值示例 |
|------|------|-----------|
| `<DistroName>` | WSL 发行版名 | `Ubuntu-22.04` 或 `Ubuntu` |
| `<WindowsUser>` | Windows 用户名 | `Admin` 或 `Administrator` |
| `<Owner>` | GitHub 用户名 | `jsxuaijun-art` |
| `<Repo>` | 同步仓库名 | `hermes-data` |

## 初始设置流程

### 1. 创建 GitHub 私有仓库
```bash
# 在 GitHub 上创建私有仓库，如 <Owner>/<Repo>
```

### 2. 在每台电脑上克隆
```powershell
cd C:\Users\<WindowsUser>\Desktop
git clone git@github.com:<Owner>/<Repo>.git HermesAgent
```

### 3. 初始填充方向（关键决策）
根据实际情况选择方向：

**情况 A：WSL 是全新的，同步目录有完整数据 → 从同步目录填充 WSL**
```bash
wsl -d <DistroName> -- bash -c "
  cp -f /mnt/c/Users/<WindowsUser>/Desktop/HermesAgent/SOUL*.md ~/.hermes/
  cp -f /mnt/c/Users/<WindowsUser>/Desktop/HermesAgent/config.yaml ~/.hermes/
  mkdir -p ~/.hermes/memories
  cp -f /mnt/c/Users/<WindowsUser>/Desktop/HermesAgent/memories/*.md ~/.hermes/memories/
  mkdir -p ~/.hermes/skills
  cp -rf /mnt/c/Users/<WindowsUser>/Desktop/HermesAgent/skills/* ~/.hermes/skills/
"
```

**情况 B：WSL 有最新数据，同步目录是旧的 → 从 WSL 推送到同步目录**
```bash
wsl -d <DistroName> -- bash -c "
  cp -f ~/.hermes/SOUL*.md /mnt/c/Users/<WindowsUser>/Desktop/HermesAgent/
  cp -f ~/.hermes/config.yaml /mnt/c/Users/<WindowsUser>/Desktop/HermesAgent/
  cp -f ~/.hermes/memories/MEMORY.md ~/.hermes/memories/USER.md /mnt/c/Users/<WindowsUser>/Desktop/HermesAgent/memories/
"
```

### 4. 推送到 GitHub
```powershell
cd /d C:\Users\<WindowsUser>\Desktop\HermesAgent
git add -A
git commit -m "初始同步"
wsl -d <DistroName> -- bash -c "cd /mnt/c/Users/<WindowsUser>/Desktop/HermesAgent && git push origin main"
```

## 日常同步操作

### 推送（本机→GitHub）
```powershell
# Step 1: 从 WSL 复制到 Windows 同步目录
wsl -d <DistroName> -- bash -c "
  cp -f ~/.hermes/SOUL*.md /mnt/c/Users/<WindowsUser>/Desktop/HermesAgent/ 2>/dev/null
  cp -rf ~/.hermes/memories/*.md /mnt/c/Users/<WindowsUser>/Desktop/HermesAgent/memories/ 2>/dev/null
  cp -rf ~/.hermes/skills/* /mnt/c/Users/<WindowsUser>/Desktop/HermesAgent/skills/ 2>/dev/null
  cp -f ~/.hermes/config.yaml /mnt/c/Users/<WindowsUser>/Desktop/HermesAgent/ 2>/dev/null
"

# Step 2: 在 Windows 侧 git 提交并推送
cd /d C:\Users\<WindowsUser>\Desktop\HermesAgent
git add -A
git commit -m "同步 %date:~0,10% %time:~0,5%"
wsl -d <DistroName> -- bash -c "cd /mnt/c/Users/<WindowsUser>/Desktop/HermesAgent && git push origin main"
```

### 拉取（GitHub→本机）
```powershell
# Step 1: 从 GitHub 拉取最新数据
cd /d C:\Users\<WindowsUser>\Desktop\HermesAgent
wsl -d <DistroName> -- bash -c "cd /mnt/c/Users/<WindowsUser>/Desktop/HermesAgent && git pull origin main"

# Step 2: 复制到 WSL
wsl -d <DistroName> -- bash -c "
  cp -f /mnt/c/Users/<WindowsUser>/Desktop/HermesAgent/SOUL*.md ~/.hermes/ 2>/dev/null
  mkdir -p ~/.hermes/memories
  cp -rf /mnt/c/Users/<WindowsUser>/Desktop/HermesAgent/memories/*.md ~/.hermes/memories/ 2>/dev/null
  mkdir -p ~/.hermes/skills
  cp -rf /mnt/c/Users/<WindowsUser>/Desktop/HermesAgent/skills/* ~/.hermes/skills/ 2>/dev/null
  cp -f /mnt/c/Users/<WindowsUser>/Desktop/HermesAgent/config.yaml ~/.hermes/ 2>/dev/null
"
```

## 生成桌面 .bat 脚本

参考 `references/batch-scripts.md` 获取完整的推送/拉取 .bat 脚本模板。关键注意事项：
- **WSL 发行版名称**：用 `wsl -l -v` 查看实际名称
- **Windows 用户名**：用 `dir C:\Users\` 查看，脚本中路径必须匹配
- **桌面路径重定向**：桌面可能被重定向到 `D:\360MoveData\Users\<User>\Desktop\`，用 `dir /b Desktop` 确认
- **编码**：`.bat` 文件必须用 `chcp 65001 >nul` 启用 UTF-8 支持
- **静默错误**：用 `2>/dev/null` 处理 WSL 中可能不存在的文件

## 踩坑记录 / Pitfalls

### SSH Key
- **Windows 有 Key 但 WSL 没有**：即使 Windows 侧 `~/.ssh/` 有 Key，WSL 侧是独立的，必须显式复制过去并 `chmod 600`
- **known_hosts**：首次连接 GitHub 需要 `ssh -T -o StrictHostKeyChecking=accept-new git@github.com`

### Batch 脚本编码
- **中文/特殊字符在 .bat 中会乱码**：`write_file` 写入的文件默认 UTF-8 无 BOM，cmd.exe 会把它当 GBK 解析。中文、边框字符（═┌┐等）会被解析为乱码导致命令被拆碎报错
- **解决方案1（推荐）**：.bat 文件全用纯英文 + 简单符号（`=` `-`），彻底绕开编码问题
- **解决方案2**：用 Python 写入文件时加 BOM 头 `b'\xef\xbb\xbf'`，保存为 UTF-8 with BOM
- **测试方法**：从 WSL 里 `cmd.exe /c xxx.bat` 不一定能正确运行（UNC 路径问题），最好双击桌面文件测试

### 路径与网络
- **Windows 用户名不一致**：`Admin` vs `Administrator` —— 不同电脑可能不同
- **WSL 发行版名不一致**：`Ubuntu` vs `Ubuntu-22.04` vs `Ubuntu-24.04`，用 `wsl -l -v` 确认
- **桌面重定向（OneDrive / 360MoveData）**：桌面可能实际位于 `D:\\360MoveData\\Users\\<User>\\Desktop\\` 或 `D:\\OneDrive\\Desktop\\` 而非 `C:\\Users\\<User>\\Desktop\\`。用 `dir /b Desktop` 确认实际路径，或 `find /mnt -name "HermesAgent" -type d` 全局搜索同步目录。同步目录的 .bat 脚本路径必须与 WSL 中的 `/mnt/` 挂载路径一致。
- **Windows 直连 GitHub 超时**：必须通过 WSL 执行 git push/pull（SSH 方式）
- **raw.githubusercontent.com 超时**：API (`api.github.com`) 更可靠，内容 CDN 和 API 走不同路由
- **ghproxy.net 代理**：在中国网络环境下，用 `ghproxy.net/https://github.com/...` 作为下载代理

### 编码问题（高频踩坑）

- **write_file 写入 .bat 文件是 UTF-8 without BOM**：WSL 侧用 `write_file`、`cp`、`echo` 创建的 .bat 文件默认 UTF-8 无 BOM。Windows cmd.exe 启动时按 ANSI/GBK (CP936) 解析，中文字符和 Unicode 边框符号（═┌┐╔╗╚╝）会变成乱码碎片，导致整行命令失效。
- **解决方案**：纯英文 + 简单符号（- = / _）最可靠；如需中文必须加 UTF-8 BOM（`\xEF\xBB\xBF`）头。
- **参考**：`references/batch-scripts.md` 有完整模板和编码方案对比。

### 数据一致性
- **config.yaml 以 WSL 侧为准**：WSL 运行中使用的配置是最新版，推送时覆盖同步目录
- **不要覆盖 .env**：每台电脑 API Key 不同，同步脚本必须排除 `.env`
- **skills 冲突**：如果两台电脑都修改了同一技能文件，手动解决 git merge 冲突
- **skills 合并策略**：用 `cp -rf` 会覆盖 WSL 自动生成的技能，注意保留

### .gitignore 排除顺序（高频踩坑）
`.gitignore` 中**排除规则（`*`）在前，白名单规则（`!xxx`）在后**。如果先 `!sessions.db` 后 `*.db`，后写的 `*.db` 会覆盖前面的 `!sessions.db`，导致 sessions.db 仍被排除。**正确顺序：先 `*.db` 再 `!sessions.db`**。

```gitignore
# ✓ 正确
*.db
!sessions.db   # 放在 *.db 之后才生效

# ✗ 错误
!sessions.db   # 放在前面没用
*.db            # 这个覆盖了上面的白名单
```

同理，如果顶层有 `*` 全排除，所有白名单 `!xxx` 必须在 `*` 之后。

### 首次部署
- **填充方向**：WSL 数据不全时，先**从同步目录拉到 WSL**，而不是从 WSL 推
- **SOUL 通配符**：用 `SOUL*.md` 避免逐文件复制（SOUL_Pro.md / SOUL_Edu.md 可能不存在）
- **memories 精确同步**：只同步 MEMORY.md 和 USER.md，排除 `*.lock` 文件
- **git push 前检视**：先 `git status` 确认变更内容，再 `git commit`