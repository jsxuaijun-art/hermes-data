---
name: company-law
description: >
  《中华人民共和国公司法（2023年修订）》主路由。当用户咨询公司设立/登记/出资/治理/股权转让/
  合并分立增减资/解散清算注销/董监高义务/法律责任等任何公司法问题时，先经本 skill 路由到对应专题子 skill
  （company-law-establishment / company-law-governance / company-law-restructure / company-law-liability），
  再引用 references/全文.md（266 条完整全文）。盈信公司注册/注销业务高频引用。避免凭记忆改写条号。
version: 1.0.0
agent_created: true
---

# 中华人民共和国公司法（2023年修订）· 主路由 Skill

## 任务目标
把公司法问题路由到正确专题子 skill，并给出完整全文入口（references/全文.md，266 条）。

## 结构总览（15 章 → 4 个专题子 skill）
- `company-law-establishment`：第1–6章 总则/公司登记/有限公司设立与组织/有限公司股权转让/股份公司设立与组织/股份发行转让
- `company-law-governance`：第7–10章 国家出资公司/董监高资格义务/公司债券/公司财务会计
- `company-law-restructure`：第11–12章 公司合并分立增资减资/公司解散和清算（盈信注销风险高频）
- `company-law-liability`：第13–15章 外国公司分支/法律责任/附则

## 路由决策树
- 设公司、登记、章程、出资、股权/股份转让 → `company-law-establishment`
- 董监高、国家出资、债券、财务 → `company-law-governance`
- 合并/分立/减资/增资、解散/清算/注销 → `company-law-restructure`
- 外国公司分支、违法处罚、附则 → `company-law-liability`
- 跨章或不确定 → 直接查 `references/全文.md`（266 条）

## 注意事项
- 2023-12-29修订，2024-07-01施行，取代2018年修正版。
- 注销涉未结清税务债务，须同时满足《税收征收管理法》补税/滞纳金规定，跨法衔接见 `tax-admin`、`tax-law`。
- 司法解释（如公司法司法解释二第11/20条清算责任）属外部口径，引用时结合。
- 条号以 `references/全文.md` 为准。

## 全文
完整 266 条见 `references/全文.md`。
