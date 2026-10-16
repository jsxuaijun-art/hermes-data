---
name: doc-skill-reconciliation
description: 核对源文档是否已融入skill,补独有内容后清理源稿。
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [skill-library, document, cleanup, reconciliation]
    related_skills: [book-to-skill, skill-library-consolidation, skill-library-sync]
trigger: 用户给本地/桌面文件（docx/zip/md 等）问"是否已利用过""是不是旧版本""要不要删除"，或要求把某文档核对/比对进 skill 库。关键词「用过了吗」「旧的删不删」「是否已融合」「导入过没有」也触发。
category: productivity
---

# 源文档 → Skill 核对归档

用户经常把资料源稿放在桌面（D:\OneDrive\Desktop），先让 agent 做成 skill，之后又会拿同款/旧版文件问"是否已经利用过了、要不要删除"。本 skill 是这套「核对 → 补漏 → 清理」的审计流程：**先证明内容 100% 已进 skill，才允许删源稿**。直接删 = 可能丢独有内容。

## When to Use

- 用户给一个文档/压缩包，问"是否已利用过 / 是否旧版本 / 要不要删除"
- 用户给一个文档，要求"核对是否已融入 skill"
- 桌面上有来源文档要回收清理，需要先审计

## Prerequisites

- WSL 路径换算：`D:\OneDrive\Desktop\xxx.docx` → `/mnt/d/OneDrive/Desktop/xxx.docx`（OneDrive 桌面路径常用 `/mnt/d/OneDrive/Desktop/`）
- read_file 能自动转换 docx/xlsx 为文本，可直接读
- Hermes 终端会话的 cwd 可能卡在**上一轮已删除的目录**（如 /tmp/sph_inspect），导致所有 shell 命令报 `cd: ... No such file or directory` / Exit 126——不要尝试 cd 修复，**给 terminal 命令加 `workdir` 参数**绕过

## How to Run

按顺序执行，每步都是防丢内容的闸门：

1. **定位 + 读取源文档**：用 `search_files`(target='files') 确认文件存在，read_file 提取全文（docx 自动转文本）。发现是 zip 先用 `unzip -l` 看内容。
2. **找到对应已装 skill**：在 `~/.hermes/skills/` 下按分类搜索（`find ~/.hermes/skills -maxdepth 2 -iname "*关键词*"`）。注意两类位置都可能存在：
   - 活动版：`~/.hermes/skills/<分类>/<name>/`
   - 归档版：`~/.hermes/skills/.archive/<name>/`（curator 移走的旧副本，**可能与活动版完全相同**）
3. **章节级粗比对**：`grep -nE '^#|^##' SKILL.md` 列章节，与源文档的章节标题对照，确定"整体已融合"的初步结论。
4. **关键词级精比对（关键步骤）**：只对照章节标题会漏。用 `grep -c` 检查**专属术语**（法定文号、专有名词、独有章节名），例如本次案例：`资产损失`=0 才暴露 docx 有 45 行「资产损失税前扣除·证据链」从未融合。规则：
   - ✅ 选专属词：法规名（"资产损失所得税税前扣除"）、文号（"25号公告"）、独有术语
   - ❌ 别用通用词：`证据`、`注销`、`流程`——已装版出现不代表独有章节进了
   - 每项核出 ≥1 才算"该块已融合"；0 次 = 该块独有内容，必须补
5. **活动版 vs 归档版 diff**：`diff` 确认两版关系（本次两版完全相同，都缺独有块，证明任何 skill 版本都没用过它）。
6. **漏则先补，再验证**：把独有内容 patch 进**活动版** SKILL.md → `skill_view(name)` 验证 `readiness_status: available` 且新章节在内 → 才进入删除。
7. **内容 100% 归档后才删源稿**：`rm -f` 后重查文件确认不存在（search_files 或目录列举应找不到该文件）。
8. **.archive 旧副本保持原样**：归档版是历史快照，不手动同步、不修改。

## 变体：结构化方法论增量（大部分已融入，但有一整块新方法论）

当源文档**大部分已融入**（骨架重合，如 SPIN 问需求/问痛点已在），但其中一整块**结构化方法论**所有专属词全 0 命中（案例见下：学习销售.docx 的 ③问出预算 ④问出顾虑 ⑤引导决策·展望未来 提问三大原则 真诚利他·价值共生三要点，全部 0），处置**不是删稿、也不是整篇重融**，而是把价值增量补进目标 reference：

1. 用专属词逐个核出**哪些子块 0 命中** = 真正未融入的价值增量（一词一子块，别拿整章标题糊弄）。
2. 把这块作为**结构化新章节 patch 进目标 skill 的 reference**（弹药库文件，不塞进 SKILL.md 正文）。开头标注来源 + 核心心法，子块用步骤/编号/话术框呈现，让模型调用时能直接照做。
3. **同步同源副本**：同一 reference 可能在多个 skill 下各有一份（Pitfall 7），`diff` 另一副本 → 同样 patch，保持字节一致。
4. **在目标 SKILL.md 挂引用**：在对应阶段/章节加一行指针（`references/<file>.md「小节名」`），否则模型调话术时永远命中不到新内容——挂引用这步最容易漏，等于白补。
5. 全部落地、skill_view 可加载后，源文档的独有内容才算完整迁移 → 此时才可删稿。

## Quick Reference

```bash
# 定位源文档（onedrive 桌面）
ls -la "/mnt/d/OneDrive/Desktop/<文件>"
# 找已装 skill（含归档副本）
find ~/.hermes/skills -maxdepth 2 -iname "*关键词*"
# 章节粗比对
grep -nE '^#|^##' ~/.hermes/skills/<分类>/<name>/SKILL.md
# 专属术语精查（0 = 该块从未融合）
grep -c "<专属术语>" ~/.hermes/skills/<分类>/<name>/SKILL.md
# 活动版 vs 归档版
diff ~/.hermes/skills/.archive/<name>/SKILL.md ~/.hermes/skills/<分类>/<name>/SKILL.md
# 补漏后验证
skill_view(name)   # 看 readiness_status + 新章节
# 确认 100% 归档后删除
rm -f "<文件>" && ls "<文件>"   # 期望 No such file
```

## Pitfalls

1. **直接删源稿 = 丢内容**：必须在关键词核查、补漏、验证三步全过之后才删。本例 docx 有 45 行证据链对照表是任何 skill 版本都没有的，直接删就永久丢失。
2. **章节标题对照会漏检**：已装 SKILL.md 与源稿章节基本同名，但源稿深处可能藏着未融合的独立板块。必须落到专属术语 grep。
3. **通用关键词误判**：`证据链` 在已装版出现 1 次（别处引用），并不代表 docx 的「资产损失·证据链」对照表进了。一词一核，词要对准板块本身。
4. **归档版 ≠ 活动版已覆盖**：curator 归档的旧副本要和活动版一起查、diff 确认。只查活动版会误判"归档版里有"。
5. **终端 cwd 卡死在已删目录**：上轮删过 /tmp 目录后，本会话所有 shell 命令报 `cd: No such file or directory`。修法是 terminal 命令加 `workdir` 参数，不是 cd。删除源稿后同样注意。
6. **删除要留证**：`rm` 之后必须重查一次确认文件不存在（search_files 找不到），不能只信 rm 的静默成功。

## Verification

- 源文档每一节都能在活动版 SKILL.md 找到对应（专属词 grep ≥1）
- 补漏后 `skill_view` 返回 `readiness_status: available` 且新章节可见
- 删除后确认文件已不存在（search_files 找不到）
- 向用户汇报时明确三件事：是否已利用、哪些是独有内容已补、删除是否已执行

## 案例记录（2026-09-29）

`D:\OneDrive\Desktop\公司注销全流程手册（完整skill）v2.docx` → 大部分已融合成 `tax-planning/company-deregistration`，但关键词核查发现「资产损失税前扣除·证据链」（2011年25号办法 + 7类损失内外部证据对照表 + 税局从严现实警示）从未进入任何 skill 版本 → patch 补进活动版 → skill_view 验证 → 删除 docx。活动版与 .archive 归档版 diff 完全相同（均为缺漏版本）。