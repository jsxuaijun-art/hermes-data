# Hermes Agent 技能触发机制

## 为什么这个文件重要

book-to-skill 的核心产出是 **可被 AI Agent 自动调用的 Skill**。要写出真正好用的 Skill，必须先理解 Hermes Agent 在运行时**如何决定加载哪个技能**。

## 三层触发机制

### ① /斜杠命令（用户手动）
```
/skill-name
```
- 用户主动输入，100% 触发
- 适合用户明确知道要调用哪个技能的场景
- 技能名要**简短、易记、无歧义**

### ② 语义匹配（AI 自动判断）
- 每轮对话开始前，系统将**所有技能的 description 字段**注入到 AI 的 system prompt 中
- AI 的指令是：**"扫描下面所有技能，如果与当前任务相关，必须加载"**
- 这是 **LLM 级别的语义匹配**，不是简单的关键词匹配
- 用户说"拿不定主意"、AI 也能匹配到 `making-decisions` 技能，无需固化的触发词

### ③ trigger / description 字段提示
```
description: >
  Use when facing a significant decision, evaluating options,
  or stuck between choices. Triggers on 'should I', 'I don't know
  whether to', 'I'm torn between', or 'help me decide'.
```
- `description` / `trigger` 是写给 **AI 看的提示词**
- 帮助 AI 更快、更准确地判断何时加载该技能
- 示例触发词不是系统级的硬规则，是**语义匹配的参考锚点**

## 对 book-to-skill 的工程启示

### 写 description 的原则

| 原则 | 好例子 | 差例子 |
|------|--------|--------|
| 描述场景而非关键词 | `Use when user isn't sure about signing a client contract and needs to evaluate pros/cons.` | `Triggers on 'should I', 'contract', 'sign'` |
| 覆盖变体表达 | 把最常见的几种提问方式列出来作为触发词参考 | 只写一个触发词 |
| 不要过于宽泛 | `Use when choosing between service package tiers for a client.` | `Use when user needs help` |
| 不要过于狭窄 | `Use when debating whether to raise prices for existing clients.` | `Use when user says exactly 'should I raise prices for client Wang'` |

### 触发词 vs 语义匹配权衡

- **触发词是示例**：它们给 AI 提供了语义锚点，帮助匹配相似表达
- **过于具体的触发词反而有害**：会让 AI 只在恰好命中时才加载，错过语义相近但措辞不同的场景
- **最佳实践**：3-5 个覆盖最典型场景的示例触发词，配合一段场景描述

### 何时用子技能（related_skills）

当主技能的某个步骤本身就是一个复杂方法论时：
```
metadata:
  hermes:
    related_skills: [reality-testing-decisions, decision-tripwires]
```
- 主技能负责**诊断场景 + 路由**
- 子技能负责**具体执行**
- AI 会自动检查 related_skills 并决定是否调度

## 常见误解

| 误解 | 真相 |
|------|------|
| 技能需要确切的触发词才能激活 | AI 通过**语义理解**判断，不是机械的关键词匹配 |
| 描述越长越好 | 太长稀释关键信息。**150 字以内**，把核心触发场景说清即可 |
| 触发词越多覆盖越广 | 5 个典型触发词就够了，重要的是场景描述 |
| 必须用 / 斜杠命令调用 | 斜杠命令只是触发方式之一，**正常对话就能自动触发** |

## 参考

- Hermes Agent 官方文档: https://hermes-agent.nousresearch.com/docs/user-guide/features/skills
- Skills System 概述: Skills are on-demand knowledge documents the agent can load when needed. They follow a progressive disclosure pattern.
- 系统提示中的强制指令: "Before replying, scan the skills below. If a skill matches or is even partially relevant to your task, you MUST load it with skill_view(name) and follow its instructions."
