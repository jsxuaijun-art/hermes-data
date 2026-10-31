<div align="right">

[English](README.md) | **中文**

</div>

<div align="center">

# Claude Code 分级记忆与记事本 Skill

**为 [Claude Code](https://claude.com/claude-code) 和 [OpenAI Codex CLI](https://github.com/openai/codex) 提供持久化分级记忆与提醒记事本。**

会话启动时自动整理记忆边界、在对话里用人话增删提醒，不再让 Claude 每次把你当陌生人。

[![ShellCheck](https://github.com/moyunliuyin/claude-memory-reminder/actions/workflows/shellcheck.yml/badge.svg)](https://github.com/moyunliuyin/claude-memory-reminder/actions/workflows/shellcheck.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/moyunliuyin/claude-memory-reminder)](https://github.com/moyunliuyin/claude-memory-reminder/releases)
[![Platforms](https://img.shields.io/badge/platforms-Claude%20Code%20%7C%20Codex%20CLI-blueviolet)](#安装到-codex-cli)

```bash
git clone https://github.com/moyunliuyin/claude-memory-reminder ~/.claude/skills/claude-memory-reminder
```

</div>

---

## 功能

- **分级记忆** — 重要度 (H/M/L) × 时效 (鲜明/精炼/归档)；常用配置过 30 天仍在鲜明区，一次性琐事尽早淘汰
- **周期触发** — 每天边界检查；每月 1 号做 `verified` 复查；每月 15 号 + 最后一天提取模式
- **记事本** — 对话里人话增删："5 月 10 号提醒我 X"、"X 搞定了"；支持 `[earliest:HH:MM]` 的时间段锁
- **多窗口去重** — 时间戳锁（默认 8 小时），同时开多个 CLI 窗口只报告一次，每多一个窗口省 ~300-500 tokens
- **运行时零依赖** — hook 脚本只用 `bash` + `grep` + `date`。本地验证可选使用 Python 和 ShellCheck

## 工作原理

每次 Claude Code 会话通过 SessionStart hook 注入两种之一：

1. **REQUIRED** — cooldown 窗口内第一个会话 → Claude 先输出分级检查报告再回答你的问题
2. **SKIP** — 另一个窗口刚做过 → Claude 直接回答你的问题

报告逻辑由 `MEMORY.md` 里的规则（分级策略 + Startup Protocol）和 `reminders.md` 里的条目共同驱动。

## 安装到 Claude Code

### 1. 克隆仓库

```bash
git clone https://github.com/moyunliuyin/claude-memory-reminder ~/.claude/skills/claude-memory-reminder
```

（可放任意位置；hook 脚本通过 `CMR_SKILL_DIR` 环境变量支持自定义路径。）

### 2. 部署 hook 脚本

```bash
mkdir -p ~/.claude/hooks
cp ~/.claude/skills/claude-memory-reminder/hooks/session-start.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/session-start.sh
```

### 3. 把 hook 注册到 settings.json

在 `~/.claude/settings.json` 顶级对象里加入以下字段（和已有 key 合并）：

```json
"hooks": {
  "SessionStart": [
    {
      "hooks": [
        { "type": "command", "command": "bash ~/.claude/hooks/session-start.sh" }
      ]
    }
  ]
}
```

> 安装脚本只输出上面的 JSON 供你粘贴，**不会自动改你的 `settings.json`**，避免破坏已有配置。

### 4. 初始化项目记忆目录

```bash
TARGET="$HOME/.claude/projects/你的项目/memory"
mkdir -p "$TARGET"
cp ~/.claude/skills/claude-memory-reminder/templates/MEMORY.md "$TARGET/"
cp ~/.claude/skills/claude-memory-reminder/templates/reminders.md "$TARGET/"
```

按需填写 `MEMORY.md` 里的 User Info / Preferences 区。

### 5.（可选）自定义参数

```bash
cd ~/.claude/skills/claude-memory-reminder
cp config.example.json config.json
# 编辑 config.json
```

### 6. 验证

新开一个 Claude Code 对话，Claude 应该一上来就输出类似：

```
[session-start] Today: 2026-04-20, Now: 10:47. REQUIRED: ...
分级检查报告:
  边界: 无跨线条目
  verified: 全部在期
  提取: 今日不触发
  提醒 (2): ⚠️ 今日 - 年度体检; 🔁 常驻 - 试试新记忆系统
  建议: 无
```

## 安装到 Codex CLI

Codex 没有 SessionStart hook → memory-reminder 在 codex 上作为 AGENTS.md "Session Startup" 指令运行（主 agent 自觉执行）。

```bash
git clone https://github.com/moyunliuyin/claude-memory-reminder.git
cd claude-memory-reminder
bash install.sh codex
```

```powershell
git clone https://github.com/moyunliuyin/claude-memory-reminder.git
cd claude-memory-reminder
powershell -ExecutionPolicy Bypass -File .\install.ps1 -Target codex
```

安装脚本**只打印**手动步骤，**不会自动改你的 AGENTS.md**。

它会告诉你做这几件事：

1. 把 [`codex/agents-md-startup-fragment.md`](codex/agents-md-startup-fragment.md) 里的 `## 1. Session Startup` 段复制到你的 `~/.codex/AGENTS.md` 第 1 节
2. 复制模板到 codex memories 目录：

   ```bash
   mkdir -p ~/.codex/memories
   cp templates/MEMORY.md ~/.codex/memories/MEMORY.md
   cp templates/reminders.md ~/.codex/memories/reminders.md
   ```

3. 按需填写 MEMORY.md User Info / Preferences

完整指南和"CC vs Codex 差异表"见 [`codex/README.md`](codex/README.md)。

> **注意**：Codex 靠主 agent 每次会话自觉执行 AGENTS.md 指令，8h cooldown 是 best-effort（模型某次可能没跑）。Claude Code 的 hook 在这方面更严格。

## 本地验证

在仓库根目录运行：

```bash
bash scripts/validate.sh
bash tests/test-session-start.sh
```

`validate.sh` 会检查必需文件、JSON 语法、shell 语法，并在 ShellCheck 可用时运行它。session-start 测试覆盖首次 `REQUIRED`、冷却期 `SKIP`、异常配置 fallback。

## 使用

直接用人话对 Claude 讲就行：

| 你说 | 结果 |
|------|------|
| "2026 年 5 月 10 号提醒我 X" | 写入 `[due: 2026-05-10][active] X` |
| "记得提醒我 X" | 写入 `[due: on-demand][active][created:TODAY] X` |
| "5 月 10 号中午 12 点以后提醒我 X" | 写入 `[due: 2026-05-10][earliest:12:00][active] X` |
| "每天提醒我 X 直到搞定" | 写入 `[due: daily-until-done][active] X` |
| "X 搞定了" / "X 做完了" | 对应条目标 `done` |
| "X 不做了" / "取消 X" | 对应条目直接删除 |

## 配置

`config.json` 所有字段可选，默认值见 `config.example.json`：

```json
{
  "cooldown_hours": 8,
  "ondemand_timeout_days": 14,
  "verified_refresh_day": 1,
  "extract_days": [15, "last"],
  "boundary_days": { "vivid": 7, "distilled": 30 }
}
```

只有 `cooldown_hours` 由 hook 自己读取（正则提取）。其他字段 Claude 在执行 Startup Protocol 时自己读取 JSON。

## 卸载

卸载脚本只打印手动步骤，不会删除你的 `MEMORY.md` 或 `reminders.md` 数据：

```bash
bash uninstall.sh
# Windows PowerShell:
powershell -File uninstall.ps1
```

## 限制

这个 skill 负责注入结构化的启动/提醒上下文，但不能强制模型遵守。cooldown 是本地文件锁，删除 `~/.claude/memory/.last-reminded` 后下一次会话会重新触发完整报告。

## 路线图

- [ ] 可选的"疑似完成"启发式判断（方案 B）：扫过去对话事件推断软完成信号
- [ ] 多项目记忆分发
- [ ] 浏览 Recent Memory 的 Web UI

## License

MIT — 见 [LICENSE](LICENSE)。
