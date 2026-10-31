# Memory & Reminder for Codex CLI

Codex 没有 SessionStart hook，所以 memory-reminder 在 codex 上的形态是**主 agent 主动执行的 startup 指令**。本目录提供 codex 用户需要的两件东西：

1. `agents-md-startup-fragment.md` — 复制到你 `~/.codex/AGENTS.md` 第 1 节
2. 仓内 `templates/MEMORY.md` + `templates/reminders.md` — 复制到 `~/.codex/memories/`（或 `<project>/memory/` 若你想按项目分）

## 安装步骤

### 1. 复制 startup 指令到 AGENTS.md

打开 `codex/agents-md-startup-fragment.md`，把里面的 startup 指令段塞到你 `~/.codex/AGENTS.md` 第 1 节 "Session Startup"。如果你 AGENTS.md 还没第 1 节，整段插入即可。

### 2. 复制模板到 codex memories 目录

```bash
mkdir -p ~/.codex/memories
cp ../templates/MEMORY.md ~/.codex/memories/MEMORY.md
cp ../templates/reminders.md ~/.codex/memories/reminders.md
```

按你需求填好 `MEMORY.md` 顶部的 User Info / Preferences。

### 3. 重启 codex 会话

下次开 codex 会话，主 agent 看到 AGENTS.md 第 1 节指令后会**主动执行**：

- 读 `~/.codex/memories/MEMORY.md` 和 `reminders.md`
- 检查 8h cooldown stamp `~/.codex/memories/.last-reminded`
- 在 cooldown 内 → 输出一句 `SKIP`，直接答你的问题
- 否则 → 输出完整分级报告（边界 / verified / extraction / reminders）后才答

## 与 Claude Code 版的差异

| 维度 | CC | Codex |
|------|----|----|
| 触发机制 | SessionStart hook (bash) | AGENTS.md 第 1 节指令（主 agent 主动执行）|
| stamp 文件 | hook 自动写 | codex 主 agent 用 Bash 工具自检写 |
| 多窗口去重 | hook 在执行前判断 | 主 agent 在响应首轮前判断 |
| 强度 | 强（hook 一定跑） | 中（依赖主 agent 自觉，模型可能漏）|

> Codex 没有 hook → 8h cooldown 等机制依赖主 agent 自觉执行 AGENTS.md 指令。如果发现某天没跑 startup 报告，可能是模型那次"懒"了；CC 的 hook 不会有这种风险。

## 关闭

把 AGENTS.md 第 1 节的 startup 指令段删除即可。`~/.codex/memories/` 数据文件保留。
