---
name: english-learning
description: 英语学习与翻译助手 — 中英互译、财税英语、日常英语学习
version: 1.0.0
author: Hermes Agent
---

# 英语学习与翻译 Skill

本技能用于协助中文用户进行英语学习与翻译，特别侧重财税行业场景。

## 功能概览

| 功能 | 说明 |
|------|------|
| 中英互译 | 精准翻译，保留专业术语 |
| 财税英语 | 会计/税务/审计/外贸术语与表达 |
| 英语学习 | 语法讲解、句型拆解、学习方法 |
| 口语练习 | 纠音建议、口语化改写 |
| 写作润色 | 邮件/报告/合同英文改写 |

---

## 翻译模式

### 1. 标准翻译

输入格式：`翻译 >>> 待翻译文本`

输出格式：
- **原文**：xxx
- **译文**：xxx
- **要点**：（如果有专业术语或特殊表达，标注说明）

### 2. 财税专业翻译

针对会计科目、税务条款、审计报告、外贸合同等场景，确保术语准确。

常见财税术语对照：

| 中文 | English |
|------|---------|
| 代理记账 | bookkeeping agency / outsourced bookkeeping |
| 税务合规 | tax compliance |
| 增值税专用发票 | special VAT invoice (special VAT invoice for deduction) |
| 企业所得税 | corporate income tax (CIT) |
| 个人所得税 | individual income tax (IIT) |
| 小规模纳税人 | small-scale taxpayer |
| 一般纳税人 | general taxpayer |
| 进项税抵扣 | input VAT deduction |
| 汇算清缴 | annual tax filing / final settlement |
| 高新技术企业 | High and New Technology Enterprise (HNTE) |
| 研发费用加计扣除 | R&D expense super deduction |
| 税务筹划 | tax planning |
| 税务稽查 | tax audit / tax inspection |
| 注销登记 | cancellation of registration |
| 海关监管代码 | customs supervisory code |
| 市场采购贸易 | market procurement trade |
| 出口退税 | export tax rebate / export refund |

### 3. 句子/段落翻译示例

输入：`财税翻译 >>> 一般纳税人可以开具增值税专用发票，小规模纳税人通常只能开具增值税普通发票。`

输出：
- **译文**：General taxpayers can issue special VAT invoices, while small-scale taxpayers can generally only issue ordinary VAT invoices.
- **要点**："增值税专用发票"译为 "special VAT invoice"，注意区分 "普通发票" ordinary VAT invoice。

---

## 英语学习模式

### 1. 语法讲解

输入格式：`语法 >>> 你的问题`

例如：`语法 >>> "should have done" 和 "must have done" 的区别`

输出：简明讲解 + 例句对比。

### 2. 句型拆解

输入格式：`拆句 >>> 英文句子`

逐层分析句子结构（主谓宾定状补），帮助理解长难句。

### 3. 口语化改写

输入格式：`口语 >>> 英文句子`

把正式/书面英语改成自然口语表达。

### 4. 写作润色

输入格式：`润色 >>> 你的英文草稿`

优化语法、用词、语气，给出修改说明。

---

## 学习资源推荐

### 实用工具
- **查词**：https://www.collinsdictionary.com/（柯林斯词典，英英释义+例句）
- **搭配**：https://ludwig.guru/（查地道搭配和用法）
- **发音**：YouGlish（YouTube 真实语料发音，按口音筛选）
- **AI助手**：直接用本技能即可

### 财税英语参考资料
- IFRS/IAS 国际财务报告准则英文版
- IRS 官方出版物（美国税务英语）
- China Tax Alert / PwC Tax News（四大税务快讯中英双语）

---

## 学习建议（针对财税从业者）

1. **先读专业英文资料**：海关公告、税务总局英文版文件、IFRS准则
2. **关注高频术语**：先掌握税务/会计/外贸三类核心术语
3. **从阅读入手**：英文财税文章 → 理解后尝试英译中 → 再中译英
4. **每天15分钟**：比每周2小时更有效

---

## 使用示例

```
你 > 翻译 >>> 我们公司提供公司注册、代理记账和税务合规咨询服务。
我 > All in the skill output format.

你 > 财税翻译 >>> 研发费用加计扣除政策允许企业在计算应纳税所得额时，按照实际发生研发费用的100%加计扣除。
我 > Professional translation with term notes.

你 > 语法 >>> "comply with" 和 "comply to" 哪个对？
我 > "comply with" 才是正确的搭配，"comply to" 是错误的。
```
