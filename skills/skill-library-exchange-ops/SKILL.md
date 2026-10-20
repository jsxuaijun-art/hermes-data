---
name: skill-library-exchange-ops
description: 共享技能库被还原/多副本不一致时，做 from-canonical 还原与 md5 核验。
version: 1.1.0
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
- **Hermes 活动路径是嵌套的** `~/.hermes/skills/<类>/<名>/`（如 `social-media/short-video-copywriting`、`productivity/wechat-moments-marketing`、`creative/de-ai-copywriting`、`wechat-publish` 及其 `skills/wechat-publish` 双层副本）。
- **hermes-data 仓库里的 `skills/<名>` 扁平副本和 `skills/.archive/` 是历史残留，不是活动路径** —— 核验 md5 时别被它们误导（存在旧版 md5 属正常，可忽略）。

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

## 三处一致性核验（md5）

```python
import hashlib, os
def md5(p): return hashlib.md5(open(p,'rb').read()).hexdigest()[:8]
# canonical 正确版本
lib = "/mnt/c/Users/Administrator/skill-library/skills"
# 本机活动路径（嵌套！）
local = "/home/administrator/.hermes/skills"
# hermes-data 仓库嵌套活动路径
hd = "/mnt/c/Users/Admin/hermes-sync/skills"
```
- 对每个改过的 skill：`md5(lib/<名>/SKILL.md) == md5(local/<类>/<名>/SKILL.md) == md5(hd/<类>/<名>/SKILL.md)`。
- 一律对**嵌套活动路径**做 md5；扁平/归档副本不一致不算异常。
- git 侧核验：`git status -sb`（local==origin/main 无 ahead/behind）、skill-library `git log origin/main..HEAD` 为空。

## from-canonical 还原步骤（已实测有效）

> 完整事件实录、判定要点与可执行恢复脚本见 `references/reverse-overwrite-recovery-2026-10-20.md`。

1. 确认 skill-library 里是对版本（含你的新内容）。
2. 用 `shutil.copyfile` 从 lib 拷回本机每个目标路径（含 `wechat-publish` 双层副本）。
3. md5 逐份比对通过后，**重跑 `~/.hermes/sync-push.sh`** —— 首次 push 时本机可能已是旧版，会把旧内容推进 hermes-data；必须重推补回正确版本。
4. 终验：local == skill-library == hermes-data(嵌套路径 md5) == 双 remote。

## 改共享 skill 的标准作业顺序（防回归）

```
改本机源(嵌套路径) → 立即 copyfile 同步进 skill-library → commit+push skill-library
→ bash ~/.hermes/sync-push.sh(hermes-data) → 三处 md5 核验 → git local==remote 核验
```

⚠️ 中途**不要**跑 `拉取.bat` / `sync-pull.sh`（会把还没推的本机改动冲掉）。要拉别机的新内容，先确保本机改动已 push。

## Pitfalls

- `author: Hermes Agent` frontmatter 不代表 curator-managed；`created_by=None` 即为 user-owned，autonomous 写入必被拒。实测 `cron-job-ops`、`skill-library-consolidation` 都是 frontmatter 像 agent 写、实际 user-owned。
- hermes-data 仓库存在多个同名 skill 的扁平/嵌套/归档副本，搜 md5 时务必限定到嵌套活动路径。
- `skill-exchange` 是 `--no-agent --script` cron，有真实文件系统写副作用，但**只新增不覆盖**；真正会覆盖本机已改文件的是 hermes-data 的**拉取脚本 `rsync -a`**（`hermes_pull.sh` / `~/.hermes/sync-pull.sh`）。
- 别对同步夹跑「把 ~/.hermes 全量 --delete 镜像过去」——同步夹有 .git 等 ~/.hermes 没有的文件会被删。详见 `hermes-data-sync`（user-owned）P11。

## Verification

- [ ] 改过的每个 skill：lib / local / hermes-data 嵌套路径三处 md5 一致。
- [ ] skill-library 与 hermes-data 两仓库 `git status -sb` 均 local==origin/main。
- [ ] 确认本轮没有跑过 `拉取.bat` / sync-pull（或确认拉取发生在本机改动 push 之后）。

## Related

- `skill-library-sync`（devops, USER-OWNED — `hermes curator adopt` 后可改）：四工具共享技能库 + 双向交换机制的主文档。
- `hermes-data-sync`（devops, USER-OWNED）：跨机同步脚本、P1-P11 陷阱、sync_guard，以及 `hermes_pull.sh` 的 `rsync -a` 覆盖路径。
- `cron-job-ops`（devops, USER-OWNED）：cron 机械层（`--no-agent --script` 副作用、catch-up 补跑）。
- `wsl-hermes-env`（devops, USER-OWNED）：WSL 环境 / 三端同步 / 文件系统陷阱。
- `skill-library-consolidation`（productivity, USER-OWNED）：skill 整合与跨设备同步要点。
