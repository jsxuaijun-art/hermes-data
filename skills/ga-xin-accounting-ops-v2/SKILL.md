---
name: ga-xin-accounting-ops-v2
title: 高企账务与研发加计扣除 v2（CARE 可计算内核·实验性）
description: 以「客户实例进 → 一次全链可复算结论出 → 评估集守住口径不退化」为核心的研发税务技能重构版（CARE：Case 实例 / Active Rules 显式规则 / Recalc 单入口引擎 / Evaluation 回归护栏）。适用于需要把研发费用归集、其他相关费用10%限额、委托研发80%与境外2/3、A107012逐行填报、高企认定三口径、政策生效期、风险阈值一次性算清并留痕的场景；也适用于跨会话续做同一客户、政策到期模拟（如2028年44号120%回落100%）、多条件交叉裁决、高企账务质量/合规诊断打分与整改、以及改动规则后验证口径未退化。触发词：全链复算、客户实例、规则表、口径裁决、政策时效、as_of、评估集、golden case、状态机、高企两套账、例4-1、政策核验、文号核验、法规时效、高企账务诊断、账务质量体检、合规程度、整改清单。与 v1 `ga-xin-accounting-ops`（文档查表式操作手册）并列，**本技能为实验性重构，默认不启用**；需要读政策原文、账套样例、模板与案例卡时仍查 v1 保留的 references/ 与 assets/。
---

# 高企账务与研发税务 v2 — CARE 可计算内核

## 0. 定位（先读，避免与 v1 混淆）

| | v1 `ga-xin-accounting-ops` | **v2 本技能** |
|---|---|---|
| 形态 | 文档查表：按场景翻哪个 md | 可计算内核：一个实例 → 一次全链 JSON |
| 口径 | 写在散文里，靠人守 | 写在 `rules/rules.json`，带生效期与优先级 |
| 计算 | 8 个孤立命令手工串联 | 单入口 `rnd_engine.py case`，一次输出全链 |
| 判据 | 无评估集 | 14 组 golden cases / 66 断言自动回归 |
| 状态 | 线性 S0–S7 | 8 态状态机 + 固定裁决顺序 |
| 部署 | 已软链、日常使用 | **实验性，并列，不覆盖 v1** |

**使用原则**：日常乙方作业仍用 v1；当任务涉及「复算/交叉裁决/跨会话续做/改规则验退化/政策到期模拟」时用 v2。v2 的 `references/` 与 `assets/` 是 v1 知识层的原样副本，仅作依据，不参与运行时计算。

---

## 1. 目录地图

```
ga-xin-accounting-ops-v2/
├─ SKILL.md                       入口（本文件）
├─ FRAMEWORK.md                   框架说明书：选型理由、10条局限矩阵、8维对比、独立复核发现
├─ schema/
│   ├─ client_case.schema.json    客户实例字段契约（人/智能体对照，非运行时强校验）
│   ├─ audit_case.schema.json     高企账务诊断实例契约（五维诊断输入）
│   └─ cases/example_4_1.json    源书例4-1 结构化实例（黄金案例）
│       cases/audit_example_good.json / audit_example_blocked.json   诊断示例
├─ rules/rules.json               21 条显式规则（12 条硬内核 + 沿革/流程/风险/申报）
│                                 每条带 id/op/scope/priority/effective_from|to/authority/source
├─ engine/rnd_engine.py           单入口引擎，Python 3 标准库、零第三方依赖
├─ workflow/state_machine.md      8 态状态机 + 7 层裁决顺序 + 年度日历
├─ tests/
│   ├─ golden_cases.json          14 组 / 66 断言
│   └─ run_tests.py               回归 runner，退出码即判据
├─ references/  assets/           v1 知识层原样保留（17 文件，依据层）
└─ legacy/rnd_calc.py             v1 计算器，仅供对照，不调用
```

---

## 2. 三条命令（先跑，别先看文档）

```bash
P="C:/Python314/python.exe"   # 或任意 Python 3

# ① 快检：引擎内置自检
"$P" engine/rnd_engine.py selftest

# ② 回归：必须全绿才允许改规则
"$P" tests/run_tests.py                      # 14 组 / 66 断言 / 退出码 0

# ③ 复算一个客户实例（--as-of 可做政策时效模拟）
"$P" engine/rnd_engine.py case schema/cases/example_4_1.json
"$P" engine/rnd_engine.py case schema/cases/example_4_1.json --as-of 2028-06-30 --compact
```

辅助命令：`rules --as-of <日期>` 列出该时点生效/失效规则；`kernel` 列出 12 条硬内核与规则编号；`case --out <path>` 把结果 JSON 落盘归档。`verify` 做政策时效核验。`audit` 做高企账务质量/合规诊断。

---

## 2.4 高企账务质量诊断（AUDIT——审查既有/拟认定企业）

**用途**：诊断一家高新技术企业（或拟认定企业）的**账务处理质量与合规程度**，输出五维打分、整改清单与承接结论。这不是"怎么干活"，是"体检"。

```bash
# 材料先让客户按 assets/高企账务质量诊断-材料清单.md 准备（8类：报表/科目余额表/两套研发专用账/项目档案/人员/投入/收入/知识产权/已申报）
python engine/rnd_engine.py audit schema/cases/audit_example_good.json         # 体检一家
python engine/rnd_engine.py audit schema/cases/audit_example_blocked.json      # 高风险/禁接案
python engine/rnd_engine.py audit <客户审计实例.json> --out 诊断结果.json        # 落盘归档
```

**五大维度（权重）**：
| 维度 | 权重 | 检查要点 |
|---|---|---|
| 账务处理合规 | 25 | 按月记账、账实相符、研发科目、两套账（2021辅助账+高企认定专用账）、中介专项审计 |
| 研发费用归集口径 | 30 | 六类明细、兼岗/共用分摊、非研发剔除、特殊收入冲减、财政补助处理、10%限额、资本化时点、委托登记 |
| 高企资格维持指标 | 25 | 研发占比≥5%/4%/3%（按最近一年收入）、高新收入≥60%、科技人员≥10%且≥183天、知识产权、八大领域 |
| 税务申报合规 | 15 | A107012 填报、40行勾稽、年报报送、税率/加计叠加一致 |
| 证据链完整 | 5 | 材料 9 项齐备（A–H 类） |

**结论分级**：≥85 合格（可正常承接）｜60–85 需整改（整改后承接）｜<60 或禁接情形 → 高风险（出风险提示函）。禁接情形：负面清单行业、核定征收。

诊断**不替代专项审计**；涉及稽查转 `tax-audit-response`；资格指标判定复用运营引擎 R014/R015/R016 同口径。

---

## 2.6 高企全生命周期主流程（事前·事中·事后）

本技能不止做研发费用计算，而是覆盖一家企业**从普通企业到高企、运营、年检/复审**的完整生命周期。总调度图见 `references/lifecycle.md`：

```
【事前】普通→够格             【事中】认定后账务+税务          【事后】年检/复审/退场
1 资格预诊断(audit)           5 日常账务(两套账按月归集)       8 年度发展情况报表
2 培育立项·建账·IP布局         6 加计申报+15%/小微择一         9 资格期复审(3年)
3 硬指标滚动静养(1-3年)        7 风险合规自查(audit体检)        10 更名/迁移/复核追缴应对
4 达标→认定申报               ↕ 全链复算(case)/政策时效(verify) 11 退场/转其他优惠
```

- **事前培育**（普通→够格认定，v2 新补）：`references/nurture_before.md`——资格预诊断→立项建账 IP 布局（第1年）→三项硬指标滚动静养（1–3年）→达标认定申报。心智：**近三年指标是滚动的，必须申报前一年就动手**，临时补只会在复审翻车。
- **事中运营**：原有 `workflow/state_machine.md`（INTAKE→…→DELIVER）+ 年度作业日历。
- **事后维持**：`references/hte_certification.md` §七（年报/复审/更名/迁移/复核追缴/取消资格三类情形）+ `service_workflow.md` 日历。
- **AUDIT 体检贯穿**：接新客户/培育期每年/运营期/复审前都先跑 `audit`，横向前置在任意阶段。

新资产：`references/nurture_before.md`（事前培育）、`references/lifecycle.md`（全周期主流程）、`assets/高企账务质量诊断-材料清单.md`（诊断材料）。

---

## 2.5 政策时效核验（每个财税 skill 的必备动作）

**原则**：`rules/rules.json` 引用的每个文号都不是"引了就完事"——**必须主动、不定时核验其现行性**，官方信源（税务总局政策法规库 fgk.chinatax.gov.cn、财政部、科技部）为终裁。用错废止/变更的文号比不引用更危险。

**一键核验**：
```bash
python engine/rnd_engine.py verify                 # 全量：抽出全部文号按「已到期/90天临期/现行」分类
python engine/rnd_engine.py verify --due-only      # 只看到期/临期
python engine/rnd_engine.py verify --checklist     # 只出文号核验清单
python engine/rnd_engine.py verify --as-of 2028-06-30   # 期末模拟
```
`verify` 每个文号都会给出**官方核验信源**（fgk / 财政部 / 科技部 / 电子税务局表样）。它本身**不联网**（引擎刻意零依赖），联网核验动作交给 `cn-regulation-verification`（fgk 官方库状态标签终裁）与定期巡查 `tax-regulation-monitor`。

**核验纪律（写进作业）**：
1. **引用前必核**：任何规则、文书、客户方案用到文号，先 `verify` 拉出待核清单，再交 `cn-regulation-verification` 逐号核 fgk 状态标签（全文有效 / 已修改 / 全文废止失效）。
2. **已修改 ≠ 废止**：如 2015年97号（研发加计）多条款已被 2017年40号/2021年28号废止，核心规则仍现行——**按现行条款引用，勿整体引用旧号**。fgk 状态标签为准，不信二手站。
3. **到期规则改 `effective_to`，不删除**（保留沿革，R021 依赖）。R012 的 44号 120% 2027-12-31 到期，`as_of>=2028` 自动回落 R011 的 100%（G04b 断言压住）。
4. **每年复核政策版本**（44号 120% 到期、申报表版本），核查结果可沉淀回 `rules.json` 的 `effective_to`/`authority`。
5. **涉及税率/比例/金额/文号，回查官方原文或原 PDF 页面图像**（OCR 有形近字风险），不采信二手站与 OCR 表格乱码。

**引擎输出**：`admission`（路径与准入）、`collection`（双口径并列）、`limits` / `entrusted` / `accounting`、`filing.a107012`（逐行）、`superdeduction`、`rate`、`indicators`、`risk_hits`、`cross_scope_warnings`、`evidence_gaps`、`warnings`、`active_rules` / `expired_rules_excluded`、`trace`（每条结论带 rule_id / op / inputs / output / source / authority）。

---

## 3. 工作流：按状态机逐态过闸，不按文档顺序翻

`INTAKE → EVIDENCE → SETUP → COLLECT → CALC → FILE → REVIEW → DELIVER`，任一闸门失败进 **HOLD**（记录 `blocked_by`、整改清单、当前状态，实例 JSON 存档，换会话可续）。详见 `workflow/state_machine.md`。

**固定裁决顺序**（v1 缺的核心，多条件交叉不得跳级）：
```
准入门禁 → 时点过滤(as_of) → 口径分流(禁止交叉污染) → 归集与限额
        → 优惠择一(15% vs 小微, 加计可叠加) → 风险处置 → 交付签收
```
同层冲突按规则 `priority` 降序，覆盖结果写 `trace`，不静默丢弃。

---

## 4. 五条绝对红线（操作前必查）

1. **高企资格不是加计扣除前提**：非高企 / 科技型中小企业 / 集成电路 / 工业母机均可做加计（R011）；负面清单六行业与兼营 50% 判定先过闸。
2. **两套口径各算各的**：加计扣除「其他相关费用」10%、按**全部项目统一计算**（2021年第28号）；高企认定「其他费用」20%。房屋折旧/租赁费、装备调试费与田间试验费、知识产权（非专利权）摊销 **仅高企口径**。
3. **高企客户是两套账**：加计扣除 2021 版辅助账 ≠ 高企认定专用辅助账（需按近三年分年、按 RD 项目、中介专项审计）。
4. **A107012 第 40 行 = 2 + 36×80% + 38**；38 行已是限额后数，**不得重复乘 80%**。45 行 = 费用化 + 本年摊销；51 行 = 45 × 加计比例。
5. **高企研发费占比分档依据是「最近一年销售收入」**，不是近三年合计：<5000万 ≥5%、5000万–2亿 ≥4%、>2亿 ≥3%；境内研发费占比 ≥60%、高新收入 ≥60%、科技人员 ≥10%（且累计实际工作 ≥183 天）。

补充红线：无辅助账不得加计；不得事后补造台账；15% 与小微优惠不得同时享受（择一），研发加计可叠加；未在某预缴时点享受不作废。

---

## 5. 改规则的纪律

**改一条规则 = 三件事一起做**，缺一不可：

1. 填 `authority`（政策文号）+ `source`（源书 PDF 页码）+ `effective_from`（必要时 `effective_to`）；
2. 在 `tests/golden_cases.json` 加/改一条断言，覆盖新规则与相邻规则；
3. 跑 `tests/run_tests.py` **全绿**（退出码 0），并跑 `selftest`。

到期规则**改 `effective_to`，不要删除**（保留沿革，2019 年案例 G13 依赖 R021）。每年复核政策版本（2023年第44号 120% 2027 到期、申报表版本）。

**裁决顺序（采信优先级）**：现行政策原文 > 源书 > OCR 文本 > 规则表 > 引擎输出。规则表是「已审核的政策快照」，**不是政策本身**；涉及税率、比例、金额、文号必须回查官方原文或原 PDF 页面图像。表格页 OCR 数字存在倒置乱码（源书 p201–203 / p205 已证实），不得直接采信。

---

## 6. 移植与解耦

- 内容层 `schema/ rules/ engine/ workflow/ tests/ references/ assets/` **平台无关，原样复制**；只有本 `SKILL.md` 是封装层要改。
- WorkBuddy / Claude 用 frontmatter 注册；Codex 放 `~/.codex/skills/<name>/`、Hermes 放 `~/.hermes/skills/<name>/`，约定式加载免注册。
- 运行时**只依赖 Python 3 标准库**，无数据库、无网络、无第三方包。

---

## 7. 明确未完成（不假装做完）

1. 源书 70 案例中仅例 4-1 结构化；`references/cases.md` 仍为叙述体。
2. `accounting_tax_diff.md` 汇缴与税会差异主线仍缺（待 #4 冯秀娟《一案解析》）。
3. 风险指标无权重评分与误报处理；交付模板未参数化；无真实客户实例。
4. 6 本源书仍有 5 本未蒸馏；无政策原文在线核验能力；schema 未做运行时强校验。
5. 引擎为命名算子 + 数据驱动，新增规则若需新算子仍要改 Python（刻意收敛，避免引入 DSL 依赖）。

> 内部作业参考，不构成税务意见；实际申报以电子税务局当年表样与主管税务机关口径为准。对外动作（提交申报、发送、出具报告）一律需用户明确确认。
