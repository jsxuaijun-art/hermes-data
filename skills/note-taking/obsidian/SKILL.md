---
name: obsidian
description: Read, search, create, and edit notes in the Obsidian vault.
platforms: [linux, macos, windows]
---

# Obsidian Vault (第二知识库)

Use this skill for filesystem-first Obsidian vault work: reading notes, listing notes, searching note files, creating notes, appending content, adding wikilinks, and running the dual-channel sync (GitHub + Obsidian backup).

## Vault architecture (双库模型 — 2026-08 确立)

Obsidian 知识库是 Hermes 的**第二知识库**（第一是 `~/.hermes/` 内存 + hermes-data GitHub 仓库），跨 Codex/Hermes/Claude Code/WorkBuddy 多助手共享。采用**两个 vault + 一个 git 引擎**：

```
[D盘 /mnt/d/obsidian-vault]   ← Obsidian 桌面端实时读写的主库(人类+各助手日常使用)
        │  rsync (D盘→WSL, --delete, 引擎镜像)
        ▼
[WSL ~/hermes-agent/obsidian-vault]  ← git 同步引擎(原生文件系统)
        │  git commit + fetch + push → GitHub jsxuaijun-art/obsidian-vault
        ▼
[GitHub obsidian-vault]        ← 云端备份 / 跨设备拉取源
```

- **D盘 vault** = Obsidian 桌面端实际打开、人类和所有 AI 助手日常读写的主库。
- **WSL vault** (`OBSIDIAN_VAULT_PATH`, 见 `~/.hermes/.env`) = 从 D盘 单向 rsync 过来的 git 引擎镜像。不要在 D盘 上直接跑 git rebase/merge（9pfs 跨文件系统会卡死或用分钟级超时，见 Pitfalls）。
- **Hermes-Only 快照区** `_AI-Private/Hermes-Only/` 存放 Hermes 人设/记忆/技能快照，由 `~/.hermes/scripts/hermes_only_snapshot.sh` 生成。

### 统一同步脚本

```bash
~/.hermes/scripts/obsidian_sync.sh            # 完整双通道: 快照→rsync→git→push
~/.hermes/scripts/obsidian_sync.sh snapshot   # 只做 Hermes-Only 快照 + rsync
~/.hermes/scripts/obsidian_sync.sh push       # 只做 git commit + push
```

Hermes 文件更新后，除了推 `hermes-data` GitHub 仓库，还要跑 `obsidian_sync.sh` 备份到 Obsidian 并推 `obsidian-vault` 仓库。

> 双库架构的完整落地记录（合并过程、脚本内容、git 对齐序列、cron 待办）见 `references/dual-vault-sync-setup.md`。

### 目录结构

根目录为**共享区**（人类 + 所有助手可读写）：`公司运营/`（价格销售沟通/账务税务/商事登记工商/客户管理/催收/案例库/税务法规数据库/SOP/培训资料等）、`短视频平台运营/`（抖音/视频号/小红书/通用技巧）、`健康档案/`（默认仅 WorkBuddy+Claude Code 读写）、`素材库/`、`templates/`、`📥 随手记/`（统一素材入口）。

`_AI-Private/` 为 AI 助手"私藏区"：
- `_AI-Private/<助手>-Only/`（如 `Hermes-Only/`）— 该助手独享的人设/记忆/技能快照
- `_AI-Private/Shared-AI/` — 多个 AI 共用但人类不必看的运行配置/索引

口诀：**"给人看的"放根区；"给助手私藏的"放 `_AI-Private/<助手>-Only`；给多个助手共用但不给人类看的放 `_AI-Private/Shared-AI`。**

## Vault path

D 盘主库绝对路径：`/mnt/d/obsidian-vault/`（Obsidian 桌面端打开的就是这个）。
WSL git 引擎路径：`/home/administrator/hermes-agent/obsidian-vault/`（即 `OBSIDIAN_VAULT_PATH`）。

File tools do not expand shell variables. Always resolve the vault path first and pass a concrete absolute path.

> 注意：D盘 vault 和 WSL vault 在正常情况下内容应一致（D盘→WSL 单向 rsync）。不要以 WSL vault 为准反过来覆盖 D盘——D盘是 Obsidian 实时编辑的主库。

## Read a note

Use `read_file` with the resolved absolute path to the note.

## List notes

Use `search_files` with `target: "files"` and the resolved vault path.

- To list all markdown notes, use `pattern: "*.md"` under the vault path.
- To list a subfolder, search under that subfolder's absolute path.

## Search

Use `search_files` for both filename and content searches.

- For filenames, use `search_files` with `target: "files"` and a filename `pattern`.
- For note contents, use `search_files` with `target: "content"`, the content regex as `pattern`, and `file_glob: "*.md"`.

## Create a note

Use `write_file` with the resolved absolute path. Include any wiki links to related notes.
Always add frontmatter with relevant tags, e.g.:
```yaml
---
tags: [抖音, 运营规则, 短视频]
---
```

## Append to a note

Use `read_file` to see the current content, then `write_file` with the updated content.

## Wikilinks

Obsidian links notes with `[[Note Name]]` syntax. When creating notes, use these to link related content.

## Pitfalls

### P1 不要在 D盘(/mnt/d, 9pfs) 上直接做 git rebase/merge
`/mnt/d` 是跨文件系统(9pfs)。在其上直接 `git rebase`/`git merge` 会卡死或用分钟级超时（`[Command timed out after 180s]`），循环 continue 也无法推进。**解法**：D盘只当 Obsidian 实时文件库，所有 git 版本控制统一放 WSL 原生文件系统引擎（`~/hermes-agent/obsidian-vault`），经 `obsidian_sync.sh` 单向 rsync 后在其上 commit/fetch/push。

### P2 跨文件系统复制用 rsync，不用 cp -a
`cp -a /mnt/d/... backup` 复制大量带 `.git` 的目录会超时中断（`[Command timed out after 180s]`，进程被杀）。**解法**：一律用 `rsync -a --delete --size-only --exclude=.git` 做增量备份/合并，秒级完成。备份用 `--size-only` 避免 9pfs 时间戳抖动导致全量重拷。

### P3 rsync --delete 方向要正确
同步方向必须是 **D盘(主库) → WSL(引擎)**。若反过来用 WSL vault 覆盖 D盘，会冲掉 Obsidian 上人类最新的实时编辑。`--delete` 保留目标单独存在的 `.git`（因为 D盘→WSL 时排除 `.git/`，WSL 的 git 历史得以保留）。

### P4 双库 git 历史分叉 / "refusing to merge unrelated histories"
D盘 vault 和 WSL vault 可能各自有 git 历史且 remote 指向不同仓库（如 D盘曾指向不存在的 `obsidian-knowledge-base`）。处理：先 `git remote set-url origin git@github.com:jsxuaijun-art/obsidian-vault.git` 统一远端，再在 **WSL 引擎**里 `git fetch origin` → `git rebase origin/main`（保留 GitHub init 历史，把本地提交叠加其上）。

### P5 rebase 的 add/add 冲突与 .gitignore
rebase 到主库时 `.gitignore` 常出 add/add 或 content 冲突（两边都加了 .gitignore）。解法：直接 `write_file` 覆盖成干净合并版，`git add .gitignore`，再 continue。若是弹出编辑器要提交信息，用 `export GIT_EDITOR=true` 自动接受默认信息，避免非终端的 "problem with the editor 'editor'" 错误。

### P6 分支名混乱（master vs main）
本地 WSL vault 默认分支可能是 `master`，GitHub 上是 `main`。`git push origin main` 会报 `src refspec main does not match any`。先看 `git branch` / `git log` 确认分支名与 HEAD，再决定 rebase/改 HEAD。不要乱用 `git symbolic-ref HEAD refs/heads/main`——会在没有该分支时让历史"丢失"（HEAD 指向空分支），可用 reflog 找回。

### P7 网络限制（China）—— 先排查 P12 仓库超大，再归因于网络

`git push`/`ls-remote` 到 GitHub 在 China 常超时。但**先按 P12 排除「仓库超大」这个更常见的根因**（`du -sh .git`、找 >20M 文件），确认仓库不大、只是网络慢再用 rsync/ssh remote（`git@github.com:...` 比 https 稳）。推送失败**不阻塞**脚本其余步骤。可稍后开 VPN 手动重跑。诊断看 `hermes-data-sync` skill 的 P4/quick-diagnosis。

### P8 每周复盘：当日记不存在时用 session_search 重建
每周复盘规范说「汇总一周日记」，但新搭建的 vault 初始可能没有日记文件。此时：
- 用 `session_search(limit=10, sort='newest')` 获取过去 7 天的活跃会话
- 再用 `session_search(query=...)` 按主题补充搜索（公众号、税务、抖音、试卷等）
- 检查 parent 会话（parent_session_id 字段）—— 长会话可能跨多天，需逐条 scroll 提取关键决策
- 交叉验证 WorkBuddy-Only/daily/ 目录下的文件（如果有共享日记）
- 不要因为无日记文件就跳过复盘——session_search 是可靠的回溯手段

### P9 同步验证：无 terminal 工具时通过 .git 文件直接验证
当 session 中没有 `terminal` 工具可用时（如 cron 任务中 execute_code 无 subprocess 权限），仍可通过文件读取验证 git 同步状态：
- 本地 HEAD：`read_file('.git/HEAD')` → `ref: refs/heads/main`
- 本地 commit：`read_file('.git/refs/heads/main')` → 40 位 hex hash
- 远端跟踪：`read_file('.git/refs/remotes/origin/main')` → 40 位 hex hash（与本地 HEAD 一致即推送成功）
- 推送历史：`read_file('.git/logs/refs/remotes/origin/main')` → 最后一行 `update by push` 表示成功
- 远端 ref：`read_file('.git/FETCH_HEAD')` → 显示上次 fetch 的远端 HEAD（不含 push 后的更新）
- 验证：本地 HEAD hash == 远端跟踪 hash → 同步一致 ✅

### P10 cron 调度的 5 段标准式（不是 7 段）—— 每日/每周知识库归档
建每日 12:28 / 每周一 12:28 归档 cron 时，用 **5 段 cron**（分 时 日 月 周）：
- `28 12 * * *` = 每天 12:28
- `28 12 * * 1` = 每周一 12:28

**陷阱**：写错成 7 段 `0 12 28 * * *`（秒 分 时 日）会被解析成「每月 28 号 12:00」，不报错但完全错误。创建后必须核对 `next_run_at`（应显示次日/次周同一时刻）。已建任务用 `cronjob action=list` 查出 job_id 后 `action=remove` 重建。

### P11 快照脚本首跑放后台（不要前台等结果）
`hermes_only_snapshot.sh` 首次会全量 rsync 253 个技能到 Hermes-Only 区，前台 `timeout 60` 会超时。**用 `terminal(background=true)` + `notify_on_complete=true` 或直接 `cronjob` 触发**，别在前台等它。rsync 偶发 `cannot delete non-empty directory: <skill>`（include/exclude 模式下）是无害警告，内容已就位，不用处理。

### P12 push 通不过的根因常是「仓库超大」，不是网络（先查这个再怪 GitHub）
`git push` 超时不一定是 China 网络——本 vault 曾因混入**大二进制/大 PDF** 把 `.git` 撑到 1.8GB，导致任何 push 都 15+ 分钟传不完、永远 `REAL_EXIT=124`。诊断顺序：
1. `du -sh .git` 看对象库；`find <vault> -type f -size +20M` 找大文件。
2. 典型罪魁：`_AI-Private/*-Only/skills/*/dist/*`（gstack 等 Go 编译产物，94MB+）、`公司运营/.../销售推介/*.pdf`（13-140MB）、图片/视频原始素材。
3. 根治：`.gitignore` 排除 `dist/`、`*.exe`、大 `*.pdf`，并 `git rm --cached` 已跟踪的大文件（工作区文件保留）。同步脚本 `hermes_only_snapshot.sh` 的 skills rsync 也要加 `--exclude='dist/' --exclude='*.exe'`，否则下次快照又把 dist 加回来。
4. 移出大文件后若 `.git` 历史对象仍残留（`filter-branch`/`filter-repo`），可重建干净仓库（孤儿分支或重 init）。

### P13 每日归档 cron 任务：subagent 同步后必须 parent 自行验证 HEAD 一致性

**场景**：每日归档 cron 任务中，创建日记/更新索引后调用 `obsidian_sync.sh` 时，可能委托给 subagent 执行同步。

**陷阱**：subagent 自报告 `exit=0` 和「推送成功」**不可靠**。本 session 实战中，subagent 声称推送成功，但 parent 验证后发现：
- 本地 HEAD `0bb4297`，远端 HEAD `02c50e8`（不匹配）
- 远端有 2 个来自其他助手（Codex 等）的每周复盘提交
- 本地新创建的日记文件和索引更新尚未被 subagent 的提交覆盖

**根因**：
1. **subagent 自报告不可靠**：subagent 可能把脚本的 `exit=0`（脚本本身无错误）误读为「push 成功」，但实际 push 可能因远端领先而被拒绝（脚本内部静默处理了失败）
2. **远端已被其他助手领先**：另一个助手在本地 cron 运行期间向 GitHub 推了新提交，导致 `git push` 报 `[rejected] (fetch first)`
3. **新文件可能未提交**：subagent 的 git 状态与 parent 不同步，新创建的日记文件可能未被 subagent 的 `git add -A` 捕捉

**解法**：parent 在 subagent 同步后必须自行验证 + 修复：

```bash
cd /home/administrator/hermes-agent/obsidian-vault
# 1. 验证
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git ls-remote origin main | awk '{print $1}')
if [ "$LOCAL" != "$REMOTE" ]; then
  echo "HEAD MISMATCH: local=$LOCAL remote=$REMOTE"
  # 2. 检查并提交本地修改
  git status --short
  git add -A && git commit -m "daily: YYYY-MM-DD 归档"
  # 3. fetch 远端最新状态
  git fetch origin
  # 4. 查看远端领先了哪些提交
  git log --oneline HEAD..origin/main
  # 5. rebase（日记文件通常不与其他助手工作交集，无冲突）
  git rebase origin/main
  # 6. 推送
  git push origin main
  # 7. 再次验证
  echo "new local=$(git rev-parse HEAD) vs remote=$(git ls-remote origin main | awk '{print $1}')"
fi
```

**典型场景**：远端领先的提交通常是其他助手（如 Codex）的每周复盘/归档，与日记文件所在路径不重叠，rebase 通常顺利通过。本 session 实战中本地 `0bb4297` → 远端 `02c50e8`（2 个每周复盘提交），rebase 无冲突，推送后 HEAD `d5e582e` 一致。

**WorkBuddy 领先 7 提交的 add/add 冲突实战（2026-08-06）**：远端被其他助手（WorkBuddy 自己的每日/每周归档）领先了 7 个提交，`git rebase origin/main` 时在**非 Hermes 文件**上出 add/add 冲突：
```
CONFLICT (add/add): .workbuddy/automations/automation-*/memory.md
CONFLICT (add/add): .workbuddy/memory/2026-08-03.md / 2026-08-06.md
CONFLICT (add/add): _AI-Private/WorkBuddy-Only/daily/2026-08-02/05/06.md
CONFLICT (add/add): _AI-Private/WorkBuddy-Only/weekly/2026-W32.md
```
**根因**：Hermes 引擎 rsync 镜像会把 WorkBuddy-Only 区一并拉到本地，本地 sync 提交"顺带"带着这些文件的旧快照，与远端 WorkBuddy 新提交撞车。

**解法（保持远端 WorkBuddy 版本为权威）**：
```bash
cd /home/administrator/hermes-agent/obsidian-vault
git fetch origin && git rebase origin/main
# 冲突文件全部是 WorkBuddy 属文件（不是 Hermes 内容），rebase 期间 --ours=被 rebase 到的 origin/main
git diff --name-only --diff-filter=U          # 列出冲突文件
for f in .workbuddy ' _AI-Private/WorkBuddy-Only/...'; do git checkout --ours -- "$f"; done
git add -u && git add .workbuddy _AI-Private/WorkBuddy-Only
GIT_EDITOR=true git rebase --continue         # 接受默认提交信息，避免 dumb terminal editor 报错
git push origin main
# 验证
[ "$(git rev-parse HEAD)" = "$(git ls-remote origin main | awk '{print $1}')" ] && echo SYNCED
```
判断依据：冲突涉及 **`--ours`（保留 rebase 目标=远端新版本）**。Hermes 的日记/索引文件在冲突之外，rebase 后自动保留。若冲突出现在 Hermes-Only 自主文件，才需人工判断合并。**应判断"冲突文件属于谁"**：非本助手（WorkBuddy/其他助手-Only）的文件一律 `--ours` 取远端，本助手自主文件才逐条合并。

**注意**：subagent 委托同步时，上述验证逻辑必须在 parent 用 `execute_code` 中通过 `subprocess` 执行，不能再次委托给 subagent。`obsidian_sync.sh` 脚本本身无问题，问题是 subagent 自报告不可靠。
