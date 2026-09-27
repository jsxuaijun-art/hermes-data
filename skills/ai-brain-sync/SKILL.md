---
name: ai-brain-sync
description: 在 WorkBuddy / Hermes / Codex / Claude Code 四台 AI 之间、以及多台电脑之间同步技能、记忆与规则。当用户提到"同步"、"另一台电脑"、"换电脑"、"家里电脑和公司电脑"、"技能没同步过去"、"记忆同步"、"ai-brain-sync"、"四个工具共享"时使用。
category: infrastructure
triggers:
  - 同步
  - 另一台电脑
  - 换电脑
  - 技能没同步
  - 记忆同步
  - ai-brain-sync
---

# ai-brain-sync

单一真源在 GitHub 私有仓库，任何一端新增的技能、记忆、规则都会流向其他所有端。

## 仓库位置

| 平台 | 路径 |
|---|---|
| Windows | `D:\ai-brain-sync` |
| WSL / Linux | `/mnt/d/ai-brain-sync` |
| 远程 | `git@github.com:jsxuaijun-art/ai-brain-sync.git`（Private，走 SSH） |

## 同步命令

```powershell
# Windows：完整双向同步（推荐）
powershell -NoProfile -ExecutionPolicy Bypass -File D:\ai-brain-sync\scripts\sync.ps1

# 只拉取（新电脑首次接入用这个）
powershell -NoProfile -ExecutionPolicy Bypass -File D:\ai-brain-sync\scripts\sync.ps1 -Direction pull

# 只上传（本机改了技能或记忆后）
powershell -NoProfile -ExecutionPolicy Bypass -File D:\ai-brain-sync\scripts\sync.ps1 -Direction push

# 预演，不动任何文件
powershell -NoProfile -ExecutionPolicy Bypass -File D:\ai-brain-sync\scripts\sync.ps1 -DryRun
```

```bash
# WSL / Linux
bash /mnt/d/ai-brain-sync/scripts/sync.sh
bash /mnt/d/ai-brain-sync/scripts/sync.sh pull
bash /mnt/d/ai-brain-sync/scripts/sync.sh push
```

图形方式：双击 `D:\ai-brain-sync\一键同步.bat`

## 目录结构与同步方向

| 目录 | 内容 | 方向 |
|---|---|---|
| `core/` | USER / SOUL / IDENTITY / MEMORY | 人格类中枢→本机；MEMORY 双向 |
| `skills/` | 自研业务技能（唯一真源） | 双向合并，新者胜 |
| `rules/` | CLAUDE.md / AGENTS.md | 中枢→本机 |
| `memory/<tool>/` | 各端日志归档 | 本机→中枢，只上传 |
| `devices/<hostname>/` | 本机覆盖层 | 本机专属 |
| `config/skill-sync-list.txt` | 参与同步的技能白名单 | — |

## 各端落点

| 工具 | 技能 | 记忆 / 规则 |
|---|---|---|
| WorkBuddy | `~/.workbuddy/skills/` | `~/.workbuddy/MEMORY.md` |
| Claude Code | `~/.claude/skills/` | `~/.claude/CLAUDE.md` |
| Codex | `~/.codex/skills/` | `~/.codex/AGENTS.md` |
| Hermes | `~/.hermes/skills/` | `~/.hermes/claw-memory/MEMORY.md` |

## 改技能的正确姿势

1. 正常在本机改（任何一端都行）
2. 跑一次 `push`
3. 其他电脑开机时自动 `pull`，或手动跑一次

**不要**直接改 `rules/CLAUDE.md`、`rules/AGENTS.md` 的本机副本——下次同步会被中枢覆盖。要改就改中枢仓库里的那份。

## 冲突处理

比较修改时间，**新者胜**；被覆盖的一方自动留档到 `devices/<hostname>/conflicts/<时间戳>/`，任何时候都能找回。绝不静默覆盖。

## 安全红线

每次提交前自动扫描密钥，命中即中止（退出码 2）。
**绝不入库**：`.env`、`auth.json`、`mcp.json`、API key、客户资料、合同、账套。

被拦下时，正确做法是把文件加进 `.gitignore`，**不要**强行提交。

## 新电脑接入

```bash
git clone git@github.com:jsxuaijun-art/ai-brain-sync.git D:\ai-brain-sync
powershell -File D:\ai-brain-sync\scripts\sync.ps1 -Direction pull
```

然后双击 `注册开机自动同步.bat` 打开自动拉取。

## 已知限制

- WSL2 下 HTTPS git push 会失败（CGNAT + stdin 转发），**统一走 SSH**
- `schtasks` 在部分受管环境会被安全策略拦截；此时开机自动拉取靠启动文件夹里的 `autopull-silent.vbs`
- Hermes 自带的 gstack 等框架技能不在同步白名单内，各端自行维护
