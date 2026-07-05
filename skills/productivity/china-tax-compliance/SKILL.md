---
name: china-tax-compliance
title: Chinese Tax Compliance Analysis
description: Chinese tax analysis for business structure comparison — individual businesses (个体工商户) vs companies (有限责任公司), tax evasion penalties, High-Tech Enterprise (高新技术企业) supplier risk, and relevant law citations. Covers 经营所得个人所得税, 企业所得税, 增值税, and虚列成本/虚开发票 penalties.
trigger: user asks about Chinese tax calculations, individual business vs company comparison, tax evasion penalties (虚列成本/偷税/逃税), business structure tax implications, High-Tech Enterprise supplier invoice risks, or requests tax law citations (税收征收管理法, 刑法第201/205条).
category: productivity
---

# Chinese Tax Compliance Analysis

## Scope

This umbrella skill covers Chinese (PRC) tax analysis for 财税服务 practitioners. Core topics:

1. **Individual business (个体工商户) vs company (有限责任公司)** — tax burden comparison under 查账征收
2. **经营所得个人所得税** — 5-level progressive rate (5%-35%) computation
3. **虚列成本/偷税 penalties** — Tax Collection Law §63/64, Criminal Law §201 (逃税罪)
4. **虚开增值税专用发票** — Criminal Law §205, 受票方(高新企业) cascade risks
5. **High-Tech Enterprise (高新技术企业)** — qualification cancellation, 10-year retroactive clawback
6. **Business entity liability** — 无限连带责任 (个体户) vs 有限责任 (公司)

## Key Tax Rate Tables

### 经营所得个人所得税 (5-level progressive)

| 级数 | 全年应纳税所得额 | 税率 | 速算扣除数 |
|------|-----------------|------|-----------|
| 1 | ≤30,000 | 5% | 0 |
| 2 | 30,000~90,000 | 10% | 1,500 |
| 3 | 90,000~300,000 | 20% | 10,500 |
| 4 | 300,000~500,000 | 30% | 40,500 |
| 5 | >500,000 | 35% | 65,500 |

Formula: `应纳税额 = 应纳税所得额 × 税率 - 速算扣除数`

### 查账征收 计算公式

**个体工商户：**
```
应纳税所得额 = 收入 - 有票成本 - 业主减除费用(60,000/年)
```
无合法凭证的暂估成本 — 不得税前扣除。

**公司（一般纳税人）：**
```
企业所得税应纳税额 = 利润总额 × 适用税率
小型微利企业优惠：应纳税所得额≤300万 → 减按25%计入×20%税率(实际税负5%)
```

## Key Legal Provisions

### 虚列成本/偷税

| 法律 | 条款 | 处罚 |
|------|------|------|
| 《税收征收管理法》 | §63 (偷税) | 追缴税款+滞纳金+50%~5倍罚款 |
| 《税收征收管理法》 | §64 (编造虚假计税依据) | 5万元以下罚款 |
| 《刑法》 | §201 (逃税罪) | 数额较大(10万+10%)→3年以下; 数额巨大(50万+30%)→3~7年 |

### 虚开增值税专用发票

| 虚开税额 | 刑期 | 依据 |
|---------|------|------|
| ≥10万 | 3年以下 | 《刑法》§205 |
| ≥50万(数额较大) | 3~10年 | 《刑法》§205 |
| ≥250万(数额巨大) | 10年~无期徒刑 | 《刑法》§205 |

### 受票方(高新企业)风险链条

个体户偷税被查 → 金税四期穿透发票 → 高新企业取得的专票被认定"虚开" →

1. **增值税**: 进项税额全额转出，补税+罚款
2. **企业所得税**: 成本不得扣除，调增应纳税所得额
3. **高新资格取消**: 追缴10年已享受的15%税率差+研发加计扣除
4. **刑事**: 虚开专票罪，追责法定代表人/财务负责人/采购负责人
5. **联合惩戒**: D级纳税人、限飞限高、限制出境、上市融资封堵

### 法律责任对比

| 主体 | 责任形式 | 依据 |
|------|---------|------|
| 个体工商户 | 无限连带责任(个人/家庭全部财产) | 《民法典》§56 |
| 有限责任公司 | 有限责任(认缴出资额为限) | 《公司法》§3 |
| 例外(刺破面纱) | 股东连带(财产混同/抽逃出资) | 《公司法》§20 |

## Current Status: 滞纳金 vs 税款迟纳金

- **现行有效**: 滞纳金 (0.05%/天), 《税收征收管理法》§32
- **修订草案(2025-2026)**: 拟改为 "税款迟纳金", 已提请全国人大一审, 尚未通过

## 高新技术企业风险（从偷税个体户取得专票）

Severity ranking:
1. 🌟 虚开增值税专用发票罪 → 无期徒刑 (§205)
2. 🌟 高新资格取消 → 追缴10年全部税收优惠 (可达1,200万+)
3. 🌟 34部门联合惩戒 → 企业实际"死亡"
4. 🌟 财务负责人/法定代表人个人刑事责任

## Pitfalls

1. **暂估成本不能乱用**: 查账征收个体户, 无票暂估成本若无合法凭证不得税前扣除。虚列构成偷税。
2. **小规模纳税人和一般纳税人增值税计算不同**: 小规模用征收率(目前1%), 一般纳税人用13%税率+进项抵扣。
3. **高新企业15%优惠不保护虚开方**: 被认定虚开专票后, 补缴企业所得税按25%计算, 不适用高新优惠税率。
4. **"善意取得"也不免责**: 即使不知情, 取得虚开发票的进项税额仍不得抵扣, 需补税(国税发〔2000〕187号)。
5. **追征时效**: 偷税/抗税/骗税无限期追征(《税收征收管理法》§52)。
6. **"三流一致"是红线**: 资金流、发票流、货物流必须一致; 个体户通过个人账户收款即破坏三流一致。

## References

See `references/tax-calculation-examples.md` for detailed walkthroughs:
- 个体户A (小规模, 收入160万, 有票成本8万, 暂估152万)
- 个体户B (一般纳税人, 收入180万, 进项票60万, 虚列60万)
- 公司合并方案 (收入340万, 原材料60%, 人工30%)
- 高新技术企业风险全推演

## Verification

After any tax calculation, cross-check with:
1. Progressive rate table (verify tax bracket)
2. 速算扣除数 correct
3. 业主减除费用 (60,000/年) included for 个体户
4. Small/micro enterprise qualification (应纳税所得额 ≤300万)
