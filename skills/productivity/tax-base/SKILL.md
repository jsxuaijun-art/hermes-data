---
name: tax-base
description: 财税测算窄底座：现行税率速查+定性清单+计算helper+优惠核验，各财税skill复用。
version: 1.0.0
author: 徐爱军（jsxuaijun-art）
agent_created: true
license: Proprietary
tags: [税务, 财税, 税率, 税负测算, 底座]
---

# tax-base 财税测算底座 Skill

## 这是什么（以及不是什么）
这是给各类财税 skill 共用的**窄底座**：提供「现行税率速查 + 定性检查清单 + 计算 helper + 优惠时效核验钩子」四样。**它不是"全能税务引擎"**——不做税法判断的取代，判断仍由各财税 skill / 人工按现行法条完成，本底座只负责"一处维护、处处引用"的共享层。

## When to Use
- 任何税负测算 / 税额计算 / 税率选取 / 印花税·附加·个税·企税计算。
- 做财税 skill（公司注册/注销、股权转让、税收筹划、涉税文书）需要取税率或算税时。
- 需要"严格按现行税法税率计算 + 精确条号引用"的涉税结论。

## Prerequisites
- 优惠类(小微/小规模减按/六税两费减半/高新/证券减半)时效敏感：**计算前先 `python3 <base>/scripts/verify_rates.py` 列出敏感项，再经 cn-regulation-verification 核验现行性**，以最新文件为准。
- `<base>` 按当前工具 skill 根解析（Hermes 示例：`~/.hermes/skills/productivity/tax-base/`）。

## How to Run
```bash
# 计算（纯函数 helper）
python3 <base>/scripts/calc.py --vat-split 113000,0.13     # 价税分离
python3 <base>/scripts/calc.py --eit 4889189 一般            # 企税(一般/高新/小微)
python3 <base>/scripts/calc.py --iit-comp 150000            # 个税综合(年)
python3 <base>/scripts/calc.py --iit-op 200000              # 个税经营(年)
python3 <base>/scripts/calc.py --surtax 9000                # 城建及附加
python3 <base>/scripts/calc.py --stamp 租赁合同 936000       # 印花税(按税目)

# 优惠时效核验（列出需核验项）
python3 <base>/scripts/verify_rates.py
```

## Quick Reference
- 税率/税目 → `scripts/rates.json`（带文号/施行日/有效期/核验标记）
- 计算函数 → `scripts/calc.py`（也可 `import` 复用：`eit_calc / iit_comprehensive / iit_operating / surtax / vat_split / stamp_duty`）
- 定性检查 → `references/qualitative-checklist.md`（★必读，防定性错）
- 公式 → `references/formulas.md`

## Procedure
任一税负测算，按顺序执行：
1. **定性**（先于计算）：过 `qualitative-checklist.md`——纳税人身份 → 是否应税销售 → 款项是收入还是资金往返 → 计税依据 → 税率优惠。**特别核对"应税所得 ≠ 实际净收款"**（退款/押金不减所得）。
2. **取税率**：读 `rates.json`；涉优惠先 `verify_rates.py` + cn-regulation-verification 核验现行性。
3. **计算**：用 `calc.py` 的纯函数，或按 `formulas.md`。
4. **引用条号**：涉税结论列精确条号+文号（如《企业所得税法》第4/5/6/8条、《印花税法》第2条）。
5. **不确定项红标**：当地口径/政策临界存疑 → 【待核实】+ 给"若…则…"两组结果，不硬填。

## Pitfalls
- **不要凭记忆报税率**；优惠类必须核验，rates.json 本身也标注了"敏感，须核验最新"。
- **定性错 > 计算错**：先确认款项是不是收入、有没有发生应税销售。
- 含税/不含税要分清，先价税分离再计税。
- 各税种附加（城建/教育/地方）依附增值税/消费税，无正税即无附加。

## Verification
- `python3 <base>/scripts/calc.py --eit 4889189 一般` → 应得 1222297.25
- `python3 <base>/scripts/calc.py --vat-split 113000,0.13` → 不含税 100000、税额 13000
- `python3 <base>/scripts/calc.py --stamp 租赁合同 936000` → 应得 936.0
- `python3 <base>/scripts/verify_rates.py` → 列出自检清单，无异常

## 配套（相关 skill）
- 涉法规现行性核验：`cn-regulation-verification`
- 税法条文精确引用：`tax-law` 主路由 + 各 `tax-*` 子 skill
- 税政问答：`tax-policy-qa` / `china-tax-policy-advisory`
- 财务读表：`financial-statement-core`
