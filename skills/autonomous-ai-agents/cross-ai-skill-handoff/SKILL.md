---
name: cross-ai-skill-handoff
description: 当用户要把 skill 交给另一个 AI（WordBuddy/Codex 等）读取/完善时生成交接文档。
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [handoff, cross-ai, multi-ai, skill, wordbuddy, collaboration]
trigger: >
  用户说「把/让 WordBuddy（或 Codex / Claude / 其他 AI）也生成／完善／维护这个 skill」、
  「生成一个文件让 WordBuddy 读取」、或提到多 AI 协作维护同一项知识技能时触发；
  也包括返程回路：收到另一 AI 回传的修改/交接文件（如「传给Hermes-v2.2」）、
  或用户说「WorkBuddy 说得对吗 / 它改的东西落地了吗」时。
---

# Cross-AI Skill / Knowledge Handoff（跨 AI 技能交接）

用户同时使用多个 AI 助手（Hermes / WorkBuddy / Codex / Claude Code），它们围绕同一套 Obsidian 知识库（`/mnt/d/obsidian-vault/`）协同。当用户要求"让另一个 AI 也能生成或完善这个 skill"时，交付一份**结构化交接文档**，让那个 AI 读到后能独立产出或继续完善同一技能。

## When to Use（何时触发）

- 「生成一个文件，让 WordBuddy（其他AI）读取，让它也生成/完善这个 skill」
- 「把这个技能交接给 X AI 继续维护」
- 提到"多 AI 协作维护同一技能 / 知识库"
- 需要给另一 AI 交付一份可独立复用（非本次会话一次性）的技能交接文档

## ★ 关键环境事实

1. **vault 技能 = 软链直通**：`~/.hermes/skills/<category>/<skill>` 常是指向 `/mnt/d/obsidian-vault/50-Skills/<skill>` 的符号链接（例：`tax-audit-response`）。因此**直接改 vault 文件 = Hermes 立即可见**，无需额外同步步骤。
2. **触发词在 vault 的 SKILL.md frontmatter**：要让某个词（如「税务稽查」）自动唤起 skill，在 vault 版 SKILL.md 的 frontmatter 加 `triggers:` 列表即可；软链已把改动带给 Hermes。
3. **单字触发词会误伤**：如「检查」这类日常高频词，务必提示用户可能误触发，建议收窄为「税务检查/税务稽查/被查」等复合词。先给解决方案，说明理由，不替用户擅断。
4. 交付文件放 Windows 桌面 `/mnt/c/Users/Admin/Desktop/`（用户交付惯例），用中文文件名。

## 交接文档标准结构（templates/ 有模板）

按此 6 节组织 Handoff 文档，保证目标 AI 不看原 skill 也能上手：

1. **这是什么** —— 一句话定位 + 服务对象 + 使用场景
2. **位置与结构** —— 主目录绝对路径 + 子目录树（references/templates/cases）
3. **核心方法论** —— 灵魂部分：总纲、命门/关键变量、路径分叉、红线纪律。逐条给"这个 AI 必须理解的"要点
4. **当前版本与最近更新** —— 版本号、本次改了什么、整合过哪些外部资料（标注来源书目）
5. **给目标 AI 的建议** —— 尚未完成的方向（清单）、新条目必须遵守的结构（含每个案由/章节的标准格式）、时间敏感类内容如何处理
6. **调用方式** —— Hermes 这边如何自动触发（triggers），文档给另 AI 知悉

## 内容红线（必须写进交接文档，也约束 Hermes 自身）

- **严禁收录过时政策数字**：外部资料若含政策（税率/标准/时限），只吸收"方法 + 案例思路"，不收录落到具体数字的条文，除非明确以官方现行有效版本为准。引用条文一律标准官方文号。
- 交接对象（另一 AI）必须同步**红线纪律**：不隐匿、不编造、不代署名、涉刑立即提示专业人士。
- 交接文档本身不写入会话级拼凑内容——结构必须能被另一 AI 独立复用，不是本次会话的一次性产物。

## 工作流程

1. 确认被交接技能的主目录（在 vault 的 `50-Skills/<skill>/`）
2. 读取其 SKILL.md / 启动提示词 / references 结构，提炼"核心方法论"与"版本记录"
3. 按模板生成 handoff 文档 → 写到 Windows 桌面
4. 回复里给出桌面绝对路径 + 一句话说明给谁读
5. 若用户同时要求"注册自动触发"，则改 vault SKILL.md frontmatter 加 triggers（见环境事实 2）

## 返程回路：收到另一 AI 回传的修改/交接后（v1.1 新增）

多 AI 协作不是单向的——WorkBuddy 常会回传自己的修改（如「传给Hermes-v2.2」修正汇总）。处理流程：

1. **先核验、后采信（trust-but-verify）**：另一 AI 声称「已改动源码/已落地」，**Self-report 不是事实**。拿到回传文件后，必须重读共享源码对应段落，逐条确认真实落地（版本记录是否写入、量刑表/案由是否真的改在文件里），再决定接受与否。
2. **共享源码 = 单一事实源**：双方都改同一份 vault 文件（Hermes 软链 + WorkBuddy junction 都指向它），改一处两边可见，不存在「两份冲突副本」。核验就是读那同一份。
3. **版本记录表防冲突**：共享 SKILL.md 的维护节维护一张 `vN.N.N` 版本表（日期 | 版本 | 谁改了什么），双方各追加一行。既是落地凭据，也是核验锚点（找不到对应版本行 = 改动没落地）。
4. **分工与「待核」纪律**：文号有效性/数字现行版本这类**需联网核验**的，划给有核验能力的 AI（WorkBuddy）；**方法论证/案由扩充**由 Hermes 承担。自己写进共享源码的数字/文号，凡不能当场确认现行有效的，一律标「待核」并交给核验方确认后才算数——**不许从书或记忆里直接搬政策数字**。
5. **接受了就对用户明说**：用户问「WorkBuddy 说的是对的吗？」直接答「对 + 我已核验 + 已落地」，把核验依据（文号、版本行）点出来，而不是含糊带过。

## 支持文件

- `templates/cross-ai-skill-handoff.md` —— 交接文档骨架模板，复制后按 6 节填充。
