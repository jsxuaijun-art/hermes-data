---
name: skill-library-consolidation
description: 合并重叠skill为类级母skill。说整合/合并/话术skill整合时用。
version: 1.0.0
author: Hermes Agent
license: MIT
category: productivity
tags: [skill, skill-management, consolidation, 技能整合, 合并]
trigger: 用户说"整合skill""合并skill""把几个skill并成一个""话术skill整合"或类似表述；或当前库里有多个明显重叠的skill需要归并。
metadata:
  hermes:
    tags: [skill, skill-management, consolidation, 技能整合, 合并]
    related_skills: [memory-management, hermes-agent-skill-authoring]
---

# Skill 库整合（多skill → 母skill）操作规程

把多个重叠的 skill 归并成一个类级母skill，源 skill 删除、只保留含其它子系统的伞skill做跳转。2026-09 实操验证：5 个话术 skill → `communication/sales-communication`（触发词：话术/沟通/沟通建议）。

## When to Use

- 多个 skill 覆盖同一类工作（如 5 个都管销售话术）
- 用户要求"话术/沟通/沟通建议"任一触发即调用同一个母skill
- 一个伞skill 里混着要合并的子系统 + 要保留的其它子系统

## 步骤

1. **盘清单** — 枚举候选 skill 完整文件树（SKILL.md + references/ + templates/ + scripts/），用 `search_files (target='files')` 逐个列。缺失文件不会出现在 skill_view 的 linked_files 里，必须走磁盘。
2. **定边界（先问用户）** — 明确哪些子系统合并、哪些保留独立。本库定例：短视频/朋友圈/公众号等「内容创作」保留独立不并入；财税咨询/GEO 留在 yingxin 伞skill。
3. **建母skill** — 类级名字 + 用户确认的触发词，写统一的分阶段框架 SKILL.md（如新客线1-4 + 存量线5-9）。
4. **迁 references** — 把源 skill 的**每一个** reference 复制进母skill 按阶段分子目录；源 SKILL.md 正文也另存为 reference，正文不丢。
5. **⚠ 删除前核验（最容易丢文件）** — 删源 skill 前逐文件比对源 references 清单 vs 母skill 已收清单。实操教训：enterprise-diagnostic 的 `us-eu-textile-export-certification.md`(7.5KB) 第一批漏拷差点随源删掉。宁可多拷边角文件，不可漏。
6. **伞skill 改造** — 源 skill 含不并入子系统时保留它：已并入部分整段替换为「指向母skill 的跳转」（触发词、阶段映射、references 路径），删掉已迁文件的引用表行。
7. **清理** — 话术类已迁文件删除；**操作性文件**（凭据/文件清单/交付渠道如 `企业微信配置.md`）移到伞skill references 根保留，别删。
8. **删源 skill** — 先 grep 伞skill 确认无指向已删文件的残留引用，再 rm -rf。
9. **验证** — skill_view 母skill（linked_files 识别、触发词生效）+ 确认被删 skill 消失 + 伞skill 加载跳转正常。

详细步骤与速查表见 `references/skill-consolidation-procedure.md`。

## 外部素材整合：通用模块模式

把外部素材（客户发来的话术 docx/pdf、第三方培训材料）融进母skill 时：**若内容横跨多个阶段、不属于任何单一阶段，不要硬塞进某个阶段**——单独立一个「通用模块/通用话术模块」目录，SKILL.md 里专节声明「跨阶段 · 任何场景可调用」。定位区分：通用模块=现成脚本，阶段=战略打法；先定阶段策略，再从通用模块挑话术填空。

**去品牌化铁律**：外部培训材料（如"起业云"代账培训）里的产品名/系统名/广告/联系方式一律剥离，话术适配成自己的公司口径（身份锚点/资质/年限），核心方法论保留。读者会顺着材料里的品牌名找到别家，等于给竞品导流。

## 整合结果跨设备同步（GitHub）

整合后要推到 GitHub 让其它电脑用。要点（详细命令见 `references/cross-device-sync-after-consolidation.md`）：

1. 同步夹 skills 的 rsync **去 --delete**——被整合删除的源 skill 目录在同步夹里原样保留，git 不认为被删。**必须先手动 `rm -rf` 同步夹里的这些目录**，git 才会记录删除；新母skill 由 rsync 自动加入。
2. sync_guard 的「缺失阻断」会因「git 有、本机缺被整合 skill」中止推送——这是**故意的删除**，按脚本提示 `export SYNC_GUARD_BYPASS=1` 放行（脚本明文支持故意删除场景）。
3. git 会把内容相同的搬迁识别成 **rename**（旧 SKILL.md → 母skill references/xx），`git show --stat` 看到 rename 属正常。
4. 验证删除是否真进 HEAD：**勿用 `git ls-files <路径>`**（对不存在路径也返回退出码 0，空输出照样成功，会误判"仍在"）。用 `git cat-file -e HEAD:<路径>`（存在才退出 0）。
5. 验证远端：`git ls-remote origin main` 的 sha == 本地 HEAD sha，再告诉用户"已上 GitHub"；目标机跑「拉取.bat」即可获得整合结果（旧 skill 一并消失，正是想要的效果）。

## 坑

- **并行执行读过期状态**：rm -rf 后在同一批并行调用里跑存在性检查，可能读到删除前的旧状态，误以为"文件被神秘恢复"（本次 3 个已删 skill 显示"仍存在"且 mtime 是旧时间戳 = 从未真删，是并行竞态）。**破坏性操作的存在性验证必须放独立的串行后续命令**，等几秒单独查一次。
- **引用断链**：删源 skill 后，其它 skill 里指向它的引用会断。合并完全局 grep 旧 skill 名，把指向改到母skill。
- **删源前务必保底**：reference 文件是内容资产，删 skill 前先确认全部复制进母skill；不确定就再多拷一遍，别省这一步。
- **`git ls-files` 退出码陷阱**：`git ls-files <路径>` 对不存在的路径也返回退出码 0（空输出），用它验证"是否已从 git 移除"会误判"仍在"。改用 `git cat-file -e HEAD:<路径>` 或 `git ls-tree HEAD -- <路径>`。

## 验证

- `skills_list` 里母skill 以触发词为 description 开头出现
- `find` 母skill references 文件数与源 skill 之和一致（无漏拷）
- 被删 skill 目录不存在，伞skill 的 SKILL.md 无指向已删文件的残留路径
