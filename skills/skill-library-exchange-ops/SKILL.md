---
name: skill-library-exchange-ops
description: 共享技能库被还原/多副本不一致时，做 from-canonical 还原与 md5 核验。
version: 1.2.0
author: Hermes Agent
license: MIT
category: devops
tags: [skill-library, skill-exchange, sync, 技能库, 一致性, md5]
metadata:
  hermes:
    tags: [skill-library, skill-exchange, sync, 技能库, 一致性, md5]
    category: devops
---

# Shared Skill-Library Exchange Ops（共享技能库交换/一致性/还原）

四工具（Hermes / Claude Code / Codex / WorkBuddy）共享同一技能库的**交换机制、反向覆盖陷阱、多副本一致性校验与 from-canonical 还原**。解决"What happened to my skill edits?"这一类问题。

> 本 skill 是 curator 自持的运维操作层。用户自有、但覆盖同一领域的技能（`skill-library-sync`、`hermes-data-sync`、`wsl-hermes-env`、`cron-job-ops`、`skill-library-consolidation`）是 user-owned（created_by=None），**autonomous curator 无权改写它们**——需要时向用户推荐 `hermes curator adopt <name>`。注意：SKILL.md frontmatter 写 `author: Hermes Agent` 不等于 curator-managed，是否可改以 created_by 实测为准。

## When to Use

- 在 `~/.hermes/skills/` 改过 skill，后来发现内容被还原成旧版 / md5 对不上。
- 需要改一个共享 skill，想先知道**哪些动作会覆盖本机改动**。
- 校验本地源 / skill-library / hermes-data 仓库三处一致性。
- 交付涉及四工具共享的 skill 改动，需要正确的同步→推送→核验顺序。
- 改了 skill 却「像没生效」，或裸名 `skill_view` 报 `Ambiguous` —— 同名多副本字母序遮蔽（见「二号陷阱」）。

## 架构与权威源

```
skill-library (canonical，扁平 skills/<name>)   ← 权威
  管理器: ~/skill-library-ops/{skilllib.py, exchange.sh}
  cron:  skill-exchange = "0 23 * * 0" --script ~/.hermes/scripts/skill-exchange.sh --no-agent
  exchange 流水线: collect-foreign → git-sync → install → verify
     其中 install = lib → 四工具本地 skill 目录（含 ~/.hermes/skills/），只新增、不覆盖
hermes-data 仓库:  /mnt/c/Users/Admin/hermes-sync  (git@github.com:jsxuaijun-art/hermes-data)
  推送:  ~/.hermes/sync-push.sh  (先 fetch+reset 再拷贝本地)
  拉取:  devops/hermes-data-sync/scripts/hermes_pull.sh 与 ~/.hermes/sync-pull.sh
         → rsync -a <同步夹>/skills/ ~/.hermes/skills/   ← 会覆盖本机同名文件（保留 mtime）
```

**关键认知**：
- 权威是 **skill-library**（canonical）；本机 `~/.hermes/skills/` 只是**工作副本**，会被拉取动作覆盖。
- `skill-exchange` cron 的 `install` 是**非破坏性**的：只把 lib 里**新增**的 skill 写回本机；本机已有但内容不同的一律 **SKIP（记 conflict）不覆盖**（除非显式 `--force`）。实测日志 `wrote 16 new | 24 conflicts(SKIP)`。因此它**不是**「改本机 skill 被还原」的元凶。
- **⚠️ 「活动路径」不能靠猜——同名多副本时 Hermes 按路径字母序取第一个加载**（`agent/skill_commands.py`：`iter_skill_index_files` 末尾 `for path in sorted(matches): yield ...`，随后 `scan_skill_commands` 里 `if name in seen_names: continue`）。**谁路径字典序小谁胜出。**
  - 本机同时存在「顶层扁平 `~/.hermes/skills/<名>/`」与「分类嵌套 `~/.hermes/skills/<类>/<名>/`」时，扁平版常在字母序上胜出（`short-video-copywriting` < `social-media/short-video-copywriting`，h<o）→ **扁平遗留旧版遮蔽嵌套正确版，改嵌套版根本不生效**（2026-10-20 实测：改完 skill_view 看着对，实际加载的是扁平旧版）。
  - 老版本本 skill 断言的「活动路径是嵌套的」**不成立**，已推翻。**必须实测**，见下方 `scan_skill_commands()` 判活动路径 + `references/same-name-shadowing-2026-10-20.md`。
- **hermes-data 仓库里的 `skills/<名>` 扁平副本和 `skills/.archive/` 是历史残留**，不是权威内容 —— 核验 md5 时别被它们误导。

## ⚠️ 头号陷阱：本机 skill 改动被「拉取脚本」的 rsync 覆盖（2026-10-20 实测，根因已二次修正）

**症状**：在 `~/.hermes/skills/` 改完 skill 后，本机文件变回旧版——新增内容消失、**mtime 退回旧日期**，但 skill-library / git remote 仍是别的版本。

**根因（首轮曾误判为 skill-exchange cron，二次深挖后修正）**：真正覆盖本机的是 **hermes-data 的拉取路径** ——
`devops/hermes-data-sync/scripts/hermes_pull.sh` 与 `~/.hermes/sync-pull.sh` 都执行 `rsync -a <同步夹>/skills/ ~/.hermes/skills/`，从 GitHub 版本**覆盖本机同名文件**（`rsync -a` 保留 mtime，正是 mtime 回退的原因）。
**不是** `skilllib.py install` —— 它 SKIP 冲突、不覆盖。

**如何区分（判定要点）**：
- 本机文件 **mtime 被"还原"成旧日期** → 拉取脚本的 `rsync -a` 特征（保留源 mtime）。
- 只有 lib 有、本机没有的新 skill 被写入，本机已有的冲突全部 SKIP → install 特征。

**预防铁律**：
1. **改任何共享 skill，必须当轮把正确版本同步进 skill-library 并 commit+push**，同时 push hermes-data；绝不依赖本机副本持久。
2. 本机 `~/.hermes/skills/` **不是持久存储**——任何时候跑 `拉取.bat` / sync-pull 都会用它覆盖同名文件。
3. 改完做三处一致性核验（见下）。

## ⚠️ 二号陷阱：同名多副本「字母序遮蔽」（2026-10-20 实测）

**症状**：`skill_view` / 文件内容看着是你改的正确版，但**运行时加载的是另一个旧副本** → 你的改动像没生效；或裸名报 `Ambiguous`。

**根因**：同名 skill 有多份时，Hermes 取 `sorted(paths)` 里**字典序最小**的那份。顶层扁平 `~/.hermes/skills/<名>/` 与分类嵌套 `~/.hermes/skills/<类>/<名>/` 并存时，扁平版常赢 → 遮蔽嵌套版。全库实测：**95 个 skill 同名多副本、28 个内容不一致、约 20 个「实际加载的是旧版」**。

**判活动路径（唯一可靠方法，勿猜）**：

```python
# 在 <repo>/venv/bin/python 下跑（HERMES_HOME 指向本机 ~/.hermes）
import os; os.environ.setdefault("HERMES_HOME", os.path.expanduser("~/.hermes"))
from agent.skill_commands import scan_skill_commands
c = scan_skill_commands()
print(c["/short-video-copywriting"]["skill_md_path"])   # ← 真正加载的那份
```

**修复（非破坏，已实测）**：把**最新/权威版内容写进实际加载的那个路径**，并同步 canonical（skill-library）+ hermes-data 对应扁平路径；改前先 `shutil.copyfile` 备份旧加载版到 `skills` 目录**之外**（如 `~/skill-dupes-backup/<时间戳>/`，放 `skills/` 内会被当新 skill 扫到）。修复后**重跑上面的 `scan_skill_commands()` 复核**，勿只信文件系统。

> 完整实测数据、批量修复脚本与「阻挡-20 个」清单见 `references/same-name-shadowing-2026-10-20.md`。

**结构性隐患（未根治）**：只要「顶层扁平遗留副本」还在，每次 skilllib 只装嵌套版 → 遮蔽会复发。根治=消除双份并存（清掉扁平遗留副本，保留备份），需用户点头，勿擅自删。

## 三处一致性核验（md5）

```python
import hashlib, os
def md5(p): return hashlib.md5(open(p,'rb').read()).hexdigest()[:8]
# canonical 正确版本
lib = "/mnt/c/Users/Administrator/skill-library/skills"
# 本机"活动路径"—— 由 scan_skill_commands() 实测得出，可能是扁平也可能是嵌套
local = "/home/administrator/.hermes/skills"
# hermes-data 仓库
hd = "/mnt/c/Users/Admin/hermes-sync/skills"
```
- 对每个改过的 skill：`md5(lib/<名>/SKILL.md) == md5(local<活动路径>/SKILL.md) == md5(hd 对应路径/SKILL.md)`。
- **活动路径以 `scan_skill_commands()` 实测为准**（同名多副本时可能是扁平版）；扁平/归档副本不一致不算异常。
- git 侧核验：`git status -sb`（local==origin/main 无 ahead/behind）、skill-library `git log origin/main..HEAD` 为空。

## from-canonical 还原步骤（已实测有效）

> 完整事件实录、判定要点与可执行恢复脚本见 `references/reverse-overwrite-recovery-2026-10-20.md`。

1. 确认 skill-library 里是对版本（含你的新内容）。
2. 用 `shutil.copyfile` 从 lib 拷回本机每个目标路径（含 `wechat-publish` 双层副本）。
3. md5 逐份比对通过后，**重跑 `~/.hermes/sync-push.sh`** —— 首次 push 时本机可能已是旧版，会把旧内容推进 hermes-data；必须重推补回正确版本。
4. 终验：local == skill-library == hermes-data(嵌套路径 md5) == 双 remote。

## 改共享 skill 的标准作业顺序（防回归）

```
① scan_skill_commands() 判该 skill 的"活动路径"(可能是扁平,不是嵌套!) → 改真正加载的那份
→ ② 立即 copyfile 同步进 skill-library(canonical) + hermes-data 对应扁平路径 → commit+push skill-library
→ bash ~/.hermes/sync-push.sh(hermes-data) → ③ 重跑 scan_skill_commands() 复核加载版
→ ④ 三处 md5 核验 → ⑤ git local==remote 核验
```

⚠️ 第①步不可省：同名多副本时"活动路径"未必是嵌套版（可能是顶层扁平旧版），改错副本 = 改动不生效。第③步用 `scan_skill_commands()` 实测而非看文件。

⚠️ 中途**不要**跑 `拉取.bat` / `sync-pull.sh`（会把还没推的本机改动冲掉）。要拉别机的新内容，先确保本机改动已 push。

## Pitfalls

- `author: Hermes Agent` frontmatter 不代表 curator-managed；`created_by=None` 即为 user-owned，autonomous 写入必被拒。实测 `cron-job-ops`、`skill-library-consolidation` 都是 frontmatter 像 agent 写、实际 user-owned。
- hermes-data 仓库与本机都存在多个同名 skill 的扁平/嵌套/归档副本。**搜 md5 / 改 skill 时，一律先用 `scan_skill_commands()` 确认"活动路径"，别想当然认定是嵌套版** ——同名多副本时按路径字典序取第一个，扁平版可能胜出并遮蔽嵌套版。
- `skill-exchange` 是 `--no-agent --script` cron，有真实文件系统写副作用，但**只新增不覆盖**；真正会覆盖本机已改文件的是 hermes-data 的**拉取脚本 `rsync -a`**（`hermes_pull.sh` / `~/.hermes/sync-pull.sh`）。
- 别对同步夹跑「把 ~/.hermes 全量 --delete 镜像过去」——同步夹有 .git 等 ~/.hermes 没有的文件会被删。详见 `hermes-data-sync`（user-owned）P11。
- 备份被遮蔽的旧加载版时，**别把备份目录建在 `~/.hermes/skills/` 内** —— 里面有 SKILL.md 就会被扫描当新 skill，制造新的副本。放 `~/skill-dupes-backup/` 之类目录。
- 「`skill_view` 读到的内容对」**不等于**「运行加载的就是那份」。同名多副本时两者可能不同 —— 判活动路径只认 `scan_skill_commands()`。

## Verification

- [ ] **`scan_skill_commands()` 实测加载版 = 本轮改过的那份**（同名多副本时最关键的一条；只看文件不算数）。
- [ ] 改过的每个 skill：lib / local 活动路径 / hermes-data 三处 md5 一致。
- [ ] skill-library 与 hermes-data 两仓库 `git status -sb` 均 local==origin/main。
- [ ] 确认本轮没有跑过 `拉取.bat` / sync-pull（或确认拉取发生在本机改动 push 之后）。

## Related

- `skill-library-sync`（devops, USER-OWNED — `hermes curator adopt` 后可改）：四工具共享技能库 + 双向交换机制的主文档。
- `hermes-data-sync`（devops, USER-OWNED）：跨机同步脚本、P1-P11 陷阱、sync_guard，以及 `hermes_pull.sh` 的 `rsync -a` 覆盖路径。
- `cron-job-ops`（devops, USER-OWNED）：cron 机械层（`--no-agent --script` 副作用、catch-up 补跑）。
- `wsl-hermes-env`（devops, USER-OWNED）：WSL 环境 / 三端同步 / 文件系统陷阱。
- `skill-library-consolidation`（productivity, USER-OWNED）：skill 整合与跨设备同步要点。
