---
name: tianyancha
description: 天眼查企业数据查询入口，使用本地 tyc CLI 完成企业主体核验、商业尽调与风险评估。
version: 1.0.0
author: 天眼查
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [business, research, tianyancha, 天眼查, 企业查询, 尽调]
    related_skills: [research]
---

# 天眼一下

英文名：TYC It，唤起命令：`/tyc-it`

天眼查商业查询入口。优先使用本地 `tyc` 命令查询企业数据，先锚定主体，再按用户问题调用必要维度，最后给出结论、证据和未覆盖点。

**调用通道选择**：本机可执行 `tyc` 命令时，一律使用 CLI；仅当环境只接入远程 MCP、无法执行本地命令时，使用 MCP 模式。

## When to Use
- 企业主体核验、商业尽调、合作方/客户/供应商风险评估
- 股东实控与受益所有人、关联关系路径、集团信息
- 司法诉讼、执行失信、行政处罚、经营异常
- 招投标、资质许可、知识产权、董监高与人员背景
- 历史沿革、上市财务、行业/园区/榜单发现

## Prerequisites
- `npm install -g tyc-cli`，并使用 `tyc login --no-open --no-block` + `tyc login --resume` 完成 OAuth Device Flow 登录（不要主动索要 API Key）
- 使用 `tyc` 命令，不使用 `tyc-cli`
- 登录状态：本机 `~/.tyc/config.json` 存在且凭证有效时直接查询，否则重新走 Device Flow

## Quick Reference
```bash
tyc --version
tyc company companies "百度" --pageNum 1 --pageSize 5 --md      # 主体锚定搜索
tyc company registration-info "<企业名>"                        # 工商登记信息
tyc risk overview "<企业名>"                                     # 风险总览
tyc layers; tyc L1 list --md                                     # 工具分层
```

## Procedure
1. 从用户问题提取主体、意图、深度和决策场景。
2. 除非用户给出完整企业名或 18 位统一社会信用代码，否则先用 `tyc company companies "<query>" --pageNum 1 --pageSize 5 --md` 锚定主体。
3. 先调用一到两个总览命令（`registration-info`、`risk overview`）。
4. 只下钻回答问题必需的维度。
5. 重要判断尽量用两个以上维度交叉验证。
6. 输出时先给结论，再给证据、限制和下一步建议。
7. 空结果只表示当前命令未返回数据，不要写成"绝对没有风险"。

### 主体锚定
简称/品牌/曾用名/模糊名称，先用企业搜索，优先选择经营状态正常、名称匹配语境，且法定代表人、地区、行业或 USCC 与线索一致的候选。多候选让用户确认（企业名称/USCC/状态/法人/注册地表格）。

### 常用命令映射
- 主体画像：`registration-info`、`profile`、`scale`、`contact-info`
- 合作风险：`risk overview`、`business-exception`、`administrative-penalty`、`judgment-debtor-info`、`dishonest-info`
- 司法执行：`judicial-case`、`judicial-documents`、`case-filing-info`、`high-consumption-restriction`
- 行政合规：`serious-violation`、`environmental-penalty`、`tax-violation`、`tax-arrears-notice`
- 股东实控：`shareholder-info`、`actual-controller`、`beneficial-owners`、`equity-tree`、`equity-ratio`
- 关联关系：`relation-path`、`relation-graph`、`group-info`
- 经营真实性：`bidding-info`、`qualifications`、`administrative-license`、`recruitment-info`、`products-info`、`suppliers-and-customers`
- 知识产权：`ipr-score`、`patent-info`、`trademark-info`、`software-copyright-info`
- 人员：`key-personnel`、`person-profile --humanName`、`person-risk-overview`、`personnel-positions`、`personnel-related-companies`
- 历史沿革：`historical-overview`、`historical-registration`、`historical-shareholders`、`change-records`、`history-names`
- 上市财务：`financial-summary`、`financial-data`、`listing-info`、`income-statement`、`balance-sheet`、`cash-flow-statement`

### 意图捷径
- "查一下这家公司"：主体画像 + 风险总览 + 经营真实性 + 实控摘要
- "能不能合作/供应商准入"：登记状态 + 风险总览 + 行政处罚 + 执行失信 + 经营异常
- "背后是谁/实控人"：股东 + 实际控制人 + 受益所有人 + 股权树 + 集团信息
- "两家有关系吗"：先锚定双方，再查关联路径和关键中间节点
- "真实经营吗"：登记 + 规模 + 招投标 + 资质 + 许可 + 产品 + 招聘 + 客户供应商
- "商标/专利/技术实力"：ipr-score + 专利 + 商标 + 软著

## Pitfalls
- 不替用户做法律、投资、授信或采购最终决策；给数据驱动建议并列出需人工复核材料。
- 重大风险结论必须说明业务记录或数据维度，不向用户展示内部 `tyc` 命令。
- 优先用具体记录和近期记录，不只看总数；总览与明细冲突时直接说明。
- 集团/实控/关联判断以路径、持股、任职、集团信息为依据，不以名称相似为依据。
- 调用返回 `quota_exceeded` 是用户额度触顶，不是故障：按错误信息转述剩余额度、重置时间与升级方式，不要反复重试。
- 不编造中国企业数据；没有查到时说明"未返回记录"或"该维度未覆盖"。

## Verification
```bash
tyc company registration-info "北京金堤科技有限公司"
```
能返回法定代表人、成立日期、注册资本、经营状态等工商登记字段即接入成功（该调用消耗 1 次额度，不要重复验证）。
