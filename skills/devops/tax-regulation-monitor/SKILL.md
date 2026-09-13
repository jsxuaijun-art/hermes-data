---
name: tax-regulation-monitor
description: 巡查中国税收法规变化（新发/废止/修订），防引用过时法规致失误。说"查新规/更新税政/法规时效核验"时用。
triggers:
  - 巡查税务法规 / 税政更新 / 有没有新规 / 法规时效核验
  - 税法修订 / 税收规范性文件废止 / 新公告施行
  - 引用法规前核验现行性
---

# 税务法规巡查 Monitor

## 目标
**定期全网检索，确认中国税收法律法规是否变化**（新法出台、新条例/制度/规定施行、旧文件废止/失效），避免在税务工作中引用错误法规造成严重失误。与 tax-audit-response 的「数字纪律」配合——凡引用法规/文号/数字，先核验现行性。

## 检索方法（用 anysearch CLI）

入口：anysearch skill。命令在 `/home/dmin/.hermes/skills/anysearch/scripts/anysearch_cli.py`，匿名可用（限速较低）。

```bash
# 通用搜索（freshness 按需：day/week/month/year）
python3 /home/dmin/.hermes/skills/anysearch/scripts/anysearch_cli.py search "国家税务总局 公告 2026 新发布" --max_results 8 --freshness month

# 批量并行（多主题一次查）
python3 /home/dmin/.hermes/skills/anysearch/scripts/anysearch_cli.py batch_search --queries '[{"query":"国家税务总局 新公告 施行","max_results":5,"freshness":"month"},{"query":"财政部 税务总局 公告 2026","max_results":5,"freshness":"month"}]'
```

## 查询主题清单（一次巡查覆盖这些）

依 tax-audit-response 相关，巡查以下高频风险类别的变动：
1. **tax-audit-response 用到的规则**：虚开/逃税刑事门槛、追征期、滞纳金率、罚款倍数、小型微利优惠、税前扣除凭证、发票管理、股权转让个税、研发加计、业务招待费、股东借款
2. **新法/新条例**：如《增值税法》(2026)、征管法修订草案、新的税收条例/规章
3. **规范性文件废止**：国家税务总局公告"失效废止部分税务规范性文件目录"（重点：清理批次，如2026年第18号废止136件）
4. **政策文件时效**：财税〔20XX〕X号 是否被替代/延期

## 巡查动作顺序

1. **查"是否新发布/新施行"**：`国家税务总局 公告 新发布`＋`施行日期`（权威官文用 fgk.chinatax.gov.cn 域名）
2. **查"是否废止/失效"**：国家税务总局公告《关于公布失效废止的部分税务规范性文件目录》（最关键——防止引用已废止文件）
3. **逐项对照 tax-audit-response 的待核/引用的文号**：把 skill 里标的「待核」和已引用的关键文号拉出来，逐个搜现行性
4. **核对数字口径**：刑事门槛（法释2024-4号）、小微税率、滞纳金率、加计比例等——确认是否仍现行，有无新解释

## 强调：用官方权威源
- 政务/法律条文检索，anysearch 可直抓权威官文（文号+施行日期）。优先 `fgk.chinatax.gov.cn`、各省税务局官网、`gov.cn`。
- 二手解读站（keceyun 等）只作线索，不作文书引用依据。

## 交付与存档（三路交付）
每次巡查产出一份变更简报，**三路同步交付**：
1. **vault 存档**：`/mnt/d/obsidian-vault/50-Skills/tax-audit-response/法规巡查/YYYY-MM-DD-税政变动简报.md`（工作量基准，长期留档）
2. **桌面提醒**：另存一份到 `C:/Users/Admin/Desktop/`（如 `本月税政变动简报-YYYY-MM.md`），并在简报开头注明「请查看本月税政有无变化」——方便用户在 Windows 桌面直接看到
3. **同步 WorkBuddy**：撰写一份给 WorkBuddy 的同步简报，写入 `/mnt/d/obsidian-vault/50-Skills/` 下（如 `WorkBuddy税政巡查同步-YYYY-MM.md`），供其读取（源码共享，改一处两边生效）

简报须列：新发布（文号+施行日+要点）、废止/失效（文号+替代文件）、待核项结论、对 tax-audit-response 的影响。
若发现影响 tax-audit-response 的变动（如某文号被废止、刑事门槛变化），**更新 02/04 对应表述并在 SKILL.md 版本记录加一行**，标「vX.Y 因法规巡查更新：...」。

## 谁触发
- 定期：由 cron 任务自动触发（**每月一次**，每月 1 号（`0 9 1 * *`），deliver local）。
- 临时：用户说"查新规""更新税政"时手动跑（同样按三路交付）。

## cron 执行注意（实测坑 · 本机环境）
管理本 skill 的 cron 任务时：
- `hermes cron create/remove` 会触发安全确认门；命令在限时内未获前台确认即返回 `BLOCKED: Command timed out without user response`，此时**不要重试、不要换写法、不要用其他命令达成同一目的**。
- **删除与创建分开执行**，绝不合并成一条命令（合并必超时被拦，实测 2026-09）。
- 删除旧任务在用户明确确认后通常可成功；**创建新任务即使会话内已获用户口头授权，仍可能单条被拦**——这是门控机制，不是命令写错。被拦后的正确动作：把精确命令原文交给用户，请其在前台执行或再次明确授权。
- 操作 cron 前先 `hermes cron list` 看现有任务，避免命名冲突或重复建设（本机已有销售/邮箱等其他 cron）。
- 三路交付的每份简报结构，见 `templates/月报交付三件套-模板.md`（vault 详细版 / 桌面提醒简版 / WorkBuddy 同步简报六段式）。

## 与 tax-audit-response 协作
- 这是 tax-audit-response 的外部"时效雷达"。tax-audit-response 引用法规前若不确定，应标「待核」并交本 skill（或 WorkBuddy）核验。
- 本 skill 巡查发现的变动，回写到 tax-audit-response 源码，两边同步生效。