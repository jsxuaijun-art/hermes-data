---
name: china-tax-policy-advisory
description: "Use when answering Chinese tax-law questions: cite exact 文号."
---

# 中国财税政策咨询与研究

Answers Chinese tax/accounting policy questions the way this user's 财税 practice needs them: a defensible **结论第一**, the **文号条款** that back it, **实务风险提示**, and a ready **deliverable**. This is advisory work for SME clients — credibility rests on citable 文号, and honesty about compliance red lines matters more than giving the "favorable" answer.

## Procedure

1. **Identify the fact-pattern first** — misclassifying it changes the rule. Verify: 纳税主体类型 (居民企业 vs 合伙企业 vs 个体工商户 vs 个人), 征收方式 (查账 vs 核定), 收入性质 (销售货物 / 劳务 / 股息红利 / 股权转让), 核算口径 (小企业会计准则 vs 企业会计准则). E.g. a limited company's share of a partnership's profit follows 财税〔2008〕159号 先分后税; a dividend from a resident company follows 实施条例第十七条 — two different answers.

2. **Research and pin the exact 文号** — every substantive claim gets a citable 文号 (财税〔2009〕57号, 国家税务总局公告2011年第25号, 税收征管法第35条, 国家税务总局令第35号…). An answer without one is not done. Prefer 国家税务总局政策法规库 (fgk.chinatax.gov.cn) and provincial/municipal 税务局 pages; treat third-party AMP/marketing pages as leads only. Run several parallel searches; one failed backend (caj/keenable/Exa) should not stop you — retry with different query or source.

3. **Answer in the user's fixed order**: ①直接结论 → ②法律依据（文号+条款原文要点）→ ③实务风险提示/操作落点 → ④offer a deliverable. Keep the 结论 crisp; the citations carry the credibility.

4. **Deliver**: generate .docx via the docx skill (`python3 scripts/docx_create.py spec.json out.docx`) and place on the Windows desktop `/mnt/c/Users/jiangmin/Desktop/`, then report the exact path. Offer .md / .xlsx alternatives. See references/tax-qa-deliverables.md for the desktop + docx conventions.

5. **Compliance honesty gate**: when the user probes a borderline arrangement (reclassification to squeeze under the 小型微利 5000万 asset threshold, 核定征收 to dodge tax, drafting liability-shifting contract clauses), answer the law truthfully and flag the red line explicitly — 虚构核定条件/虚假申报 = 偷税 (罚款0.5–5倍); 故意泄密 免责条款无效 (民法典506条). Never present an untested tax-avoidance manipulation as safe.

## Pitfalls

- **会计准则 vs 税法 is the #1 conflation.** Balance-sheet line classification/reclassification is an ACCOUNTING-standard matter (小企业会计准则, 企业会计准则第30号), not tax law; tax law governs 应税所得 (收入确认/扣除/资产计税基础). Do not tell a client "tax requires/forbids reclassification" — tax issues no such requirement.
- **Reclassification changes 资产总额 even though it is 调表不调账.** Moving a credit balance from 应收账款 to 预收账款 raises stated 资产总额 (asset shows 100 instead of net 70). This feeds the 小型微利 judgment (资产总额≤5000万), so a "just presentation" change has a real tax-threshold effect — but the classification must follow the standard and economic substance, NOT whatever keeps the client eligible. Advising manipulation there is advising 虚假申报.
- **坏账准备 is not deductible — only actually-realized losses are.** 计提的坏账准备 = 未经核定准备金 (企业所得税法第十条第(7)项 + 实施条例55条). The loss is 税前扣除 only when actually realized per 财税〔2009〕57号 + 25号公告, and the evidence chain matters more than the amount (现行 = 留存备查; if inspected you must produce contracts/cancellation/violation-decision/judgment originals).
- **合伙企业所得 attribution is by the year EARNED, not received.** Under 财税〔2008〕159号 先分后税 a corporate partner taxes its share of the partnership's income in the year the partnership earned it, even if cash arrives later. Do not apply the 股息红利 "利润分配决定日期" rule (实施条例17条) to partnership pass-through income.
- **Cite the 文号, not "按税法规定".** A 财税 professional's output is only as credible as its 文号; vague citations are a quality failure, not a shortcut.

## references

- references/corporate-income-tax.md — 投资收益确认时点、资产/坏账损失税前扣除、小型微利标准的文号与条款框架.
- references/individual-business-and-enforcement.md — 个体工商户 查账/核定征收、无票成本、经营所得 5–35%、偷税认定与稽查口径.
- references/tax-qa-deliverables.md — 桌面交付目录与 docx 生成约定.
