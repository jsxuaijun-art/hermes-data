---
name: equity-architecture-guide
description: >-
  股权架构全案知识库。整合《一本书讲透股权》完整精华，覆盖公司注册实务、
  控制权六大工具、七条比例线、股东类型进出、股权激励五大方案、全流程四步设计。
  与 holding-company-firewall（防火墙架构）、corporate-tax-planning（税务筹划）
  形成三向闭环：诊断→方案→执行。
trigger: >-
  用户提及以下任一场景：
  - 股权架构怎么设计？公司怎么注册？
  - 想做股权激励，怎么分股、分给谁、分多少？
  - 如何给员工期权？超额利润激励怎么做？
  - 注册资本写多少合适？认缴好还是实缴好？
  - 多个公司之间怎么设计股权关系？
  - 控股公司和子公司之间股权怎么分配？
  - 股东进来怎么给、走了怎么退？
  - 如何选激励工具？实股/期权/分红权怎么选？
  - 城市合伙人怎么设计股权？
metadata:
  hermes:
    tags:
      - equity
      - company-registration
      - equity-incentive
      - shareholder-management
      - control-tools
      - corporate-structure
      - tax-planning
    related_skills:
      - tax-planning/holding-company-firewall
      - tax-planning/corporate-tax-planning
      - enterprise-diagnostic
      - compliant-accounting
      - coze-tax-agent-prompt
---

# 股权架构全案知识库

## 一、技能定位

### 核心价值

本技能是一套**股权架构全案方法论**，把《一本书讲透股权》从架构设计到股权激励的完整知识转化为可落地执行的诊断→方案→交付流程。

### 三向闭环关系

| 技能 | 定位 | 使用时机的判断 |
|------|------|---------------|
| 本技能（equity-architecture-guide） | 框架层+知识库 | 启动任何股权话题 → 先打开 |
| holding-company-firewall | 防火墙架构 | 明确要设控股公司/防火墙时 |
| corporate-tax-planning | 税务筹划+架构重组 | 需要算税、做架构重组税务路径时 |

**推荐工作流：**

```
诊断发现股权问题 → equity-architecture-guide（框架定位+选工具）
    ├─ 需要防火墙 → holding-company-firewall（具体架构方案）
    └─ 需要节税   → corporate-tax-planning（税务路径+合规体检）
```

---

## 二、知识总览

本技能将所有股权知识按 **诊断→设计→交付** 三段式组织：

### 诊断层

| 模块 | 内容 | 参考文件 |
|------|------|---------|
| 股权健康度诊断 | 企业家股权问题快速定位清单 | 见本技能 §三 |
| 五大信号+追问 | 快速切入客户的股权需求 | 见本技能 §三 |

### 设计层（核心知识库）

| 模块 | 来源（Book1章） | 当前存放位置 |
|------|-----------------|-------------|
| ① 控制权六大工具 | 第四章 | → 已入 holding-company-firewall references/equity-book1-knowledge.md §一 |
| ② 股东类型进入与退出 | 第四章§7 | → 已入 holding-company-firewall references/equity-book1-knowledge.md §二 |
| ③ 七条比例生命线 | 第八章 | → 已入 holding-company-firewall references/equity-book1-knowledge.md §三 |
| ④ 股权转让 vs 增资扩股 | 第五章 | → 已入 holding-company-firewall references/equity-book1-knowledge.md §四 |
| ⑤ **股权激励五大工具** | 第十一章 | → **本技能新增** references/equity-incentive-tools.md |
| ⑥ **股权激励全流程** | 第十二章 | → **本技能新增** references/equity-incentive-process.md |
| ⑦ **公司注册实务** | 第六~七章 | → **本技能新增** references/company-registration-practice.md |

### 交付层

| 模块 | 关联技能 |
|------|---------|
| 防火墙架构方案 | holding-company-firewall |
| 税务筹划+合规体检 | corporate-tax-planning |
| 首次洽谈诊断 | enterprise-diagnostic |

---

## 三、诊断框架：股权健康度快速定位

### 五大信号

客户说以下任意一句话，立即启动股权排查：

| 信号 | 对应模块 | 追问切入点 |
|------|---------|-----------|
| "我们夫妻俩开了好几家公司，各管各的" | 控制权+防火墙 | 多家主体→控股架构→防火墙 |
| "我想给核心员工分点股份" | 股权激励 | 分什么（实股/分红/期权）→分给谁→分多少 |
| "有个朋友想入股，不知道怎么给" | 股东类型 | 资金/资源/管理/技术→进入条件→退出机制 |
| "注册公司时我随便写了个注册资本" | 公司注册实务 | 注册资本→认缴实缴→责任边界 |
| "我现在这家公司是我一个人100%的" | 一人公司穿透风险 | 举证倒置→第三方持股→防火墙 |

### 追问流程

```
Q1: 你名下有几家公司？股东都有谁？
    ├─ 多家 → Q2
    └─ 一家 → Q3

Q2: 这些公司之间是什么关系？有没有统一管理的想法？
    └─ 有 → 推控股公司/防火墙（→ holding-company-firewall）

Q3: 目前公司股东结构？
    ├─ 夫妻100% → 提示穿透风险+第三方代持方案
    ├─ 一人100%  → 提示举证倒置+引入新股东
    └─ 有外部股东 → 问股东关系+退出意向

Q4: 有没有想过做股权激励？
    ├─ 有 → 问：给谁？给什么类型？给多少？（→ equity-incentive ref）
    └─ 没有 → 问核心团队稳定性+留人策略

Q5: 财税是自家人管还是外聘？
    └─ 自家人 → 风险信号，推合规体检（→ corporate-tax-planning）
```

---

## 四、核心方法论：四层架构设计

### 4.1 架构层级

每个企业面对的股权问题可拆为四个层次：

```
第三层：公司注册实务
  └─ 主体类型、注册资本、法定代表人、印章管理
  └─ 这是做股权架构的"地基"，必须先想清楚

第二层：股东结构设计
  └─ 股东类型（资金/资源/管理/技术）→ 进入退出机制
  └─ 比例设计（67%/51%/34%...） → 控制权设计
  └─ 控制工具选型（双层架构/AB股/一致行动人...）

第一层：股权激励
  └─ 五大工具选型（超额利润/分红权/期权/实股/城市合伙人）
  └─ 四步设计（定人/定钱/定量/定源）

顶层：防火墙架构
  └─ 控股公司+防火墙（→ holding-company-firewall）
  └─ 家族公司设计（→ equity-book1-knowledge.md §家族公司）
```

### 4.2 设计流程

```
第一步：收集 → 见 §三 诊断框架，5个信号+追问
第二步：定位 → 客户在四层架构的哪个层
第三步：选工具 → 对应层级的 tool/knowledge
第四步：出方案 → 单层方案 or 多层组合方案
第五步：税务算账 → → corporate-tax-planning
第六步：执行路线 → → holding-company-firewall 的执行地图
```

---

## 五、模块入口：快速导航

### 模块A：公司注册实务（新）
详见 → `references/company-registration-practice.md`

覆盖：企业类型选择、企业名称、注册资本、法定代表人、印章管理

### 模块B：控制权设计（→ holding-company-firewall）
详见 → `holding-company-firewall` → `references/equity-book1-knowledge.md`

覆盖：控制权六大工具、股东类型进出、七条比例线、股权转让vs增资

### 模块C：股权激励（新）
详见 → `references/equity-incentive-tools.md`（五大工具详解）
详见 → `references/equity-incentive-process.md`（全流程四步设计）

覆盖：超额利润激励、分红权激励、期权激励、实股激励、城市合伙人 + 定人/定钱/定量/定源 + 退出机制

### 模块D：防火墙架构（→ holding-company-firewall）
详见 → `holding-company-firewall` 完整方法论

覆盖：防火墙法理逻辑、第三方持股、外部股东处理、税务路径、执行路线图

### 模块E：税务筹划（→ corporate-tax-planning）
详见 → `corporate-tax-planning`

覆盖：架构重组税务路径、股权转让个税、分红免税路径、合规体检

---

## 六、关联Skills索引

| 技能 | 关系 | 调用时机 |
|------|------|---------|
| holding-company-firewall | 防火墙架构子模块 | 客户要设控股公司/防火墙 → 此技能做具体方案 |
| corporate-tax-planning | 税务子模块 | 算股权转让税、设计重组税务路径 |
| enterprise-diagnostic | 前端入口 | 首次洽谈 → 股权健康度快速定位 |
| compliant-accounting | 后端保障 | 防火墙搭建后，日常核算合规 |
| coze-tax-agent-prompt | 全案自动化 | 用扣子智能体批量交付方案 |

---

## 七、交付物标准

### 方案结构（向客户交付）

```
一、股权架构现状分析（诊断结果）
二、核心诉求确认
三、架构设计方案
  方案A（推荐）：含具体模块建议
  方案B（备选）：保守方案
四、关键设计要点说明
  1. 股东结构设计
  2. 股权激励方案（如适用）
  3. 防火墙设计（如适用）
五、税务成本测算（→ corporate-tax-planning）
六、执行路线图
七、风险提示
八、法律依据索引
```

### 输出格式

- 默认 → 桌面 .docx
- 辅助 → 终端 ASCII 表格（结合 box_maker.py）

### 双版本PPT交付法（防白嫖策略）

**所有向客户展示的方案，必须出两个版本：**

| 版本 | 目标 | 讲什么 | 不讲什么 |
|------|------|--------|---------|
| **版① 实施方案** | 推动项目落地 | 完整架构图、法律依据、执行路线图 | 操作细节给全（客户已付费） |
| **版② 引流成交版** | 促成合作签约 | 做了的好处、不做的风险、判例故事 | **具体怎么操作** |

**核心逻辑：** 如果客户知道全部操作细节，他就会自己办或找便宜代办。版②只讲WHY（为什么这么做+为什么必须你们来做），不讲HOW（具体步骤、价格算法、文件模板）。详见 `corporate-tax-planning` §五「双版本PPT交付法」完整版。

---

## 引用来源

- 宋俊生、王亚龙《一本书讲透股权：从架构设计到股权激励》机械工业出版社 ISBN 978-7-111-79582-7
- 公司法（2023修订）
- 民法典
- 最高院（2019）民终1364号
