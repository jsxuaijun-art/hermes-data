# Changelog

格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## [0.2.0] - 2026-05-01

### Added
- **Codex CLI 平台支持**：新增 `codex/` 子目录，含：
  - `codex/agents-md-startup-fragment.md`：用户复制到 `~/.codex/AGENTS.md` 第 1 节的 startup 指令片段
  - `codex/README.md`：codex 用户安装指南 + 与 CC 版差异表
- `install.sh` / `install.ps1` 新增 `codex` 子参数：打印 codex 安装步骤（同 CC 部分的 manual print 模式，不自动改 AGENTS.md）
- README / README.zh-CN 新增 "Install for Codex CLI" 章节 + Codex platform badge

### Changed
- README hero 描述由 "for Claude Code" 改为 "for Claude Code and Codex CLI"
- README "## Install" 章节标题改为 "## Install for Claude Code"（区分两平台）

### Notes
- **Codex 与 CC 触发差异**：CC 走 SessionStart hook 自动跑；codex 没有 hook，靠主 agent 看到 AGENTS.md 第 1 节指令后自觉执行 → 强度略弱（模型可能某次漏跑），优势是无需配置 hook
- **Hermes 平台支持暂留 TODO**：Hermes 没有公开的 SessionStart 类机制，等用户提供 Hermes startup 注入细节后做 v0.3.0
- **完全向后兼容**：v0.1.x 用户升级到 v0.2.0，CC 部分零变更（hook 脚本 / templates / install 流程全保持原样）

## [0.1.1] - 2026-05-01

### Added
- `scripts/validate.sh`：本地结构 / JSON / shell syntax / ShellCheck 验证
- `tests/test-session-start.sh`：smoke test 覆盖 REQUIRED / SKIP / 配置异常 fallback
- `uninstall.ps1` / `uninstall.sh`：手动 print uninstall 步骤（不动用户数据）
- README hero section（badges + 一行 git clone）

### Changed
- README / README.zh-CN 双语 README hero 重设计

## [0.1.0] - 2026-04-20

### Added
- 初版 skill：`SKILL.md` + `hooks/session-start.sh` + `templates/MEMORY.md` + `templates/reminders.md` + `config.example.json` + `install.{sh,ps1}`
- ShellCheck CI workflow + Issue 模板

[0.2.0]: https://github.com/moyunliuyin/claude-memory-reminder/releases/tag/v0.2.0
[0.1.1]: https://github.com/moyunliuyin/claude-memory-reminder/releases/tag/v0.1.1
[0.1.0]: https://github.com/moyunliuyin/claude-memory-reminder/releases/tag/v0.1.0
