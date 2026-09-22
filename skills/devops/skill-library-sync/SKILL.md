---
name: skill-library-sync
description: 四工具(Hermes/Claude/Codex/WorkBuddy)共享统一技能库并定期双向交换。
version: 1.0.0
author: Hermes Agent (for 徐爱军/盈信)
license: Proprietary
metadata:
  hermes:
    tags: [skill, sync, codex, claude, workbuddy, 技能库, 补长补短]
    category: devops
---

# Skill Library Sync（统一技能库 · 四工具共享 + 双向交换）

## When to Use
- 在任何一台工具里新增/修改了技能，想让另外几台工具（Hermes/Claude Code/Codex/WorkBuddy）也用上时。
- 想把某工具自创的技能（如 WorkBuddy 的财经/新闻/搜索强项）回捞分享给其他工具时。
- 检查四个工具的技能是否一致、或技能丢失/对不上时。

本机四款 agent——**Hermes / Claude Code / Codex / WorkBuddy**——原生读取同一种
"Agent Skills" 格式（`<技能名>/SKILL.md`，YAML frontmatter 必须含 `name`+`description`，
可选 `scripts/ references/ templates/ assets/` 子目录）。因此可维护**一个统一技能库**，
分发给四个工具，并周期回捞各工具自创的技能（补长补短）。

## 关键路径（本机 2026-09 定稿）

| 角色 | 路径 |
|---|---|
| 统一技能库（canonical，Windows 原生，git 仓库） | `C:\Users\Administrator\skill-library\`（WSL=`/mnt/c/Users/Administrator/skill-library/`） |
| 库内技能包 | `<库>/skills/<技能名>/` |
| 清单（谁、装到哪些工具） | `<库>/manifest.json` |
| 管理脚本 | `/home/administrator/skill-library-ops/skilllib.py` |
| 定时交换脚本 | `/home/administrator/skill-library-ops/exchange.sh` + `~/.hermes/scripts/skill-exchange.sh` |
| Hermes 技能 | `~/.hermes/skills/<分类>/<技能名>/`（有分类嵌套） |
| Claude Code 技能 | `/mnt/c/Users/Administrator/.claude/skills/<技能名>/`（Windows 侧 npm 装的 claude） |
| Codex 技能 | `~/.codex/skills/<技能名>/`（WSL 侧 npm 装的 codex） |
| WorkBuddy 技能 | `/mnt/c/Users/Administrator/.workbuddy/skills/<技能名>/`（Windows 侧） |

GitHub 远程：`git@github.com:jsxuaijun-art/skill-library.git`（SSH，需先网页建空仓库；
`GIT_SSH_COMMAND="ssh -o ConnectTimeout=15"` 防国内卡死）。

## 命令

```bash
cd /home/administrator/skill-library-ops
python3 skilllib.py import-from-hermes --list   # 从 ~/.hermes/skills 收纳可移植技能
python3 skilllib.py install [--force]           # 库 → 四个工具（非破坏，冲突跳过）
python3 skilllib.py verify                      # 四工具×技能全量矩阵，非0=有缺
python3 skilllib.py collect-foreign             # 回捞工具自创技能进库（补长补短）
python3 skilllib.py git-sync [--push]           # 提交库 repo（--push 推到 GitHub）
python3 skilllib.py exchange [--push]           # collect + git + install + verify 全链路
bash exchange.sh                                # 带日志落盘的等价脚本
```

免 LLM 定时任务（已建，每周日 23:00，`--no-agent --script`）：
```bash
hermes cron list          # d662d391de3f [active] skill-exchange
hermes cron run d662d391de3f   # 手动触发下次 tick；hermes cron tick 强制跑
hermes cron runs d662d391de3f  # 看执行结果
```
手动双击：`C:\Users\Administrator\Desktop\skill-exchange.bat`（CRLF+chcp 65001，调 exchange.sh）。

## Procedure — 往统一库加新技能 / 同步

1. **入库**：把新技能 SKILL.md 放进 `<库>/skills/<技能名>/`，并在 `manifest.json` 的 `skills[]`
   加 `{"name":..., "source_home_cat":"<分类或空>", "targets":["hermes","claude","codex","workbuddy"]}`；
   或直接改 Hermes 侧后再 `import-from-hermes`。
2. **分发**：`python3 skilllib.py install`
3. **验证**：`python3 skilllib.py verify` → 四个工具都 `ALL OK`（任一 MISS 即 exit≠0）
4. **备份**：`python3 skilllib.py git-sync --push`（或依赖每周 cron 自动做）
5. **跨机**：目标机 `git clone/pull` 同一 skill-library repo，跑 `install` 即全量铺开。

## Pitfalls

- **collect-foreign 门禁**：默认只收 `agent_created` / 作者=徐爱军|jsxuaijun-art / 含中文 的技能，
  并跳过 `in_hermes_only`（gstack、hermes-*、kanban、wsl-* 等 Hermes 专属）——否则会把整个
  gstack 包/平台技能目录拖进库（曾误收 46 个 gstack，靠清空 manifest+lib 重建修复）。
- **Codex 的技能可能是"分类容器"**（`apple/ github/ mcp/` 下有子技能、根无 SKILL.md）：
  `is_category_container` 判定后保留不动，verify 记 `native-category(等效覆盖)`，不算失败。
- **非破坏安装**：目标工具已有同名技能且与库不同 → 默认跳过（`--force` 才覆盖），保护工具原生版本，
  例如 codex 自有 `wechat-publish`、claude 自有 `codex` 与库冲突至今保留为 tool-native。
- **Hermes 根级技能别写进嵌套 `skills/skills/`**：source_home_cat 为空（`""`）表示 Hermes 根目录；
  否则 `install` 会错建 `~/.hermes/skills/skills/<名>/` 副本。
- **格式零转换**：四个工具都是标准 SKILL.md，无需翻译。若某工具跟格式严格（Claude 需 name+description），
  缺 field 会被 verify 抓出。WorkBuddy 额外容忍 `display_name/allowed-tools/description_zh/visibility` 等富字段。
- **hermes cron CLI 曾缺 `reasoning_effort` 形参**（CLI 传了但 create_job 不收）→ 任何 `cron create` 报错；
  已在 `cron/jobs.py` create_job 加 `reasoning_effort` 形参并存进 job dict 修复。

## Verification

```bash
cd /home/administrator/skill-library-ops
python3 skilllib.py verify   # 期望四行 "N/N skills valid" + VERDICT: ALL OK，exit 0
git -C /mnt/c/Users/Administrator/skill-library status   # 工作树干净=已提交
hermes cron status           # 调度器在跑
```