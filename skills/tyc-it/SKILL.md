---
name: 天眼一下
description: 天眼查商业查询入口（英文名 TYC It / tyc-it）。优先使用本地 `tyc` 命令查询天眼查企业数据，仅接入了远程 MCP 的环境走 MCP 调用契约。适用于企业主体核验、商业尽调、合作方/客户/供应商风险评估、股东实控与受益所有人、关联关系路径、司法诉讼、执行失信、行政处罚、经营真实性、招投标、资质许可、知识产权、董监高与人员背景、历史沿革、行业/园区/榜单发现、上市财务等商业及企业信用场景。
---

# 天眼一下

英文名：TYC It
建议唤起命令：`/tyc-it`

先锚定主体，再按用户问题调用必要维度，最后给出结论、证据和未覆盖点。

**调用通道选择**：本机可执行 `tyc` 命令时，一律使用 CLI（第一至七节）；仅当当前环境只接入了天眼AI远程 MCP、无法执行本地命令时，使用「MCP 模式调用契约」（第八节）。两者消耗同一份调用额度。

## 一、安装与鉴权（CLI）

安装：

```bash
npm install -g tyc-cli
```

使用 OAuth Device Flow 异步登录。**不要主动索要 API Key。**（例外：用户 Prompt 中已自带 API Key 时，直接 `tyc init --authorization "<KEY>"` 完成鉴权即可，不必让用户改走浏览器授权；Key 不得出现在最终回复、项目文件或日志中。）

如果本机已登录且凭证有效，不要重复走授权流程，直接开始查询。需要登录时，先启动非阻塞 Device Flow 登录：

```bash
tyc login --no-open --no-block
```

命令会返回授权 URL 和 6 位 auth 码。**授权 URL 以命令实际返回的为准，不要使用记忆中的地址。** 面向用户时必须把授权 URL 发成 Markdown 链接，并再用 code block 发一次原始 URL；auth 码也单独用 code block：

````markdown
请打开授权页：[打开天眼查授权页](<命令返回的授权URL>)

如果点击无法自动打开，请复制下面的链接到浏览器打开：

```text
<命令返回的授权URL>
```

授权码：
```text
123456
```
````

然后停下来等待用户回复"已授权"或"完成"，不要继续轮询刷屏。

用户确认已授权后，再继续完成登录：

```bash
tyc login --resume
```

- `--resume` 返回 `authorization_pending`：简短提醒用户继续完成浏览器授权，稍后重试。
- 返回过期：重新执行 `tyc login --no-open --no-block`，给出新的授权链接与 auth 码 code block。

首次查询前确认 CLI 可用：

```bash
tyc --version
tyc company companies "百度" --pageNum 1 --pageSize 3 --md
```

如果查询提示未登录、凭证缺失或凭证过期，重新执行上述异步登录流程。

## 二、命令规则

- 使用 `tyc` 命令，不使用 `tyc-cli` 命令。
- 不确定参数时，先运行 `tyc <category> --help` 或 `tyc <category> <method> --help`。
- 分析时优先使用默认 JSON 输出；需要给用户展示候选表或简短结果时使用 `--md`。
- 列表查询默认加 `--pageNum 1 --pageSize 10`，除非用户要求更多。
- 大结果使用 `--head`、`--threshold` 或 `--output-file` 控制输出，不把长原始数据直接塞进最终答复。
- 空结果只表示当前命令未返回数据；不要写成"绝对没有风险"。
- 调用返回额度超限（如 `quota_exceeded`）时：这不是故障，按错误信息向用户转述剩余额度、重置时间与升级方式（错误体自带说明与链接），不要反复重试。

## 三、查询流程

1. 从用户问题提取主体、意图、深度和决策场景。
2. 除非用户给出完整企业名或 18 位统一社会信用代码，否则先锚定主体。
3. 先调用一到两个总览命令。
4. 只下钻回答问题必需的维度。
5. 重要判断尽量用两个以上维度交叉验证。
6. 输出时先给结论，再给证据、限制和下一步建议。

## 四、主体锚定

简称、品牌、曾用名、模糊名称或不确定主体，先用企业搜索：

```bash
tyc company companies "<query>" --pageNum 1 --pageSize 5 --md
```

优先选择经营状态正常、名称匹配语境，并且法定代表人、地区、行业或 USCC 与用户线索一致的候选。

只有一个明确候选时，可继续使用官方名称或 USCC 查询。多个候选都可能匹配时，先让用户确认：

```markdown
你说的「<query>」匹配到多家企业，请确认是哪一家：

| # | 企业名称 | USCC | 状态 | 法定代表人 | 注册地 |
|---|---|---|---|---|---|
| 1 | ... | ... | ... | ... | ... |
| 2 | ... | ... | ... | ... | ... |

回复编号继续，或回复"都不是"重新输入。
```

多主体关系问题必须分别锚定每个主体，再判断关系。

## 五、常用命令

| 意图 | 命令 |
|---|---|
| 主体画像 | `tyc company registration-info "<company>"`; `tyc company profile "<company>"`; `tyc company scale "<company>"`; `tyc company contact-info "<company>" --pageNum 1 --pageSize 10` |
| 合作风险 | `tyc risk overview "<company>"`; `tyc risk business-exception "<company>" --pageNum 1 --pageSize 10`; `tyc risk administrative-penalty "<company>" --pageNum 1 --pageSize 10`; `tyc risk judgment-debtor-info "<company>" --pageNum 1 --pageSize 10`; `tyc risk dishonest-info "<company>" --pageNum 1 --pageSize 10` |
| 司法与执行 | `tyc risk judicial-case "<company>" --pageNum 1 --pageSize 10`; `tyc risk judicial-documents "<company>" --pageNum 1 --pageSize 10`; `tyc risk case-filing-info "<company>" --pageNum 1 --pageSize 10`; `tyc risk high-consumption-restriction "<company>" --pageNum 1 --pageSize 10` |
| 行政与合规 | `tyc risk administrative-penalty "<company>" --pageNum 1 --pageSize 10`; `tyc risk serious-violation "<company>" --pageNum 1 --pageSize 10`; `tyc risk environmental-penalty "<company>" --pageNum 1 --pageSize 10`; `tyc risk tax-violation "<company>" --pageNum 1 --pageSize 10`; `tyc risk tax-arrears-notice "<company>" --pageNum 1 --pageSize 10` |
| 股东与实控 | `tyc company shareholder-info "<company>" --pageNum 1 --pageSize 10`; `tyc company actual-controller "<company>"`; `tyc company beneficial-owners "<company>" --pageNum 1 --pageSize 10`; `tyc company equity-tree "<company>"`; `tyc company equity-ratio "<company>"` |
| 关联关系 | `tyc company relation-path "<companyA>" --searchKey2 "<companyB>"`; `tyc company relation-graph "<company>"`; `tyc company group-info "<company>"` |
| 经营真实性 | `tyc operation bidding-info "<company>" --pageNum 1 --pageSize 10`; `tyc operation qualifications "<company>" --pageNum 1 --pageSize 10`; `tyc operation administrative-license "<company>" --pageNum 1 --pageSize 10`; `tyc operation recruitment-info "<company>" --pageNum 1 --pageSize 10`; `tyc operation products-info "<company>" --pageNum 1 --pageSize 10`; `tyc operation suppliers-and-customers "<company>" --pageNum 1 --pageSize 10` |
| 知识产权与品牌 | `tyc intellectual_property ipr-score "<company>"`; `tyc intellectual_property patent-info "<company>" --pageNum 1 --pageSize 10`; `tyc intellectual_property trademark-info "<company>" --pageNum 1 --pageSize 10`; `tyc intellectual_property software-copyright-info "<company>" --pageNum 1 --pageSize 10` |
| 董监高和人员 | `tyc company key-personnel "<company>" --pageNum 1 --pageSize 10`; `tyc executive person-profile "<company>" --humanName "<name>"`; `tyc executive person-risk-overview "<company>" --humanName "<name>"`; `tyc executive personnel-positions "<company>" --humanName "<name>"`; `tyc executive personnel-related-companies "<company>" --humanName "<name>"` |
| 历史沿革 | `tyc history historical-overview "<company>"`; `tyc history historical-registration "<company>"`; `tyc history historical-shareholders "<company>" --pageNum 1 --pageSize 10`; `tyc history historical-investments "<company>" --pageNum 1 --pageSize 10`; `tyc company change-records "<company>" --pageNum 1 --pageSize 10`; `tyc company history-names "<company>"` |
| 企业发现 | `tyc company companies-by-industry-region "<keyword>" --industry "<code>" --region "<code>" --pageNum 1 --pageSize 10`; `tyc company companies-by-tag "<tag>" --pageNum 1 --pageSize 10`; `tyc company companies-by-ranking "<company>" --pageNum 1 --pageSize 10`; `tyc company park-companies "<park>" --pageNum 1 --pageSize 10` |
| 关键词搜索 | `tyc operation bids "<keyword>" --pageNum 1 --pageSize 10`; `tyc intellectual_property patents "<keyword>" --pageNum 1 --pageSize 10`; `tyc intellectual_property trademarks "<keyword>" --pageNum 1 --pageSize 10` |
| 上市与财务 | `tyc company financial-summary "<company>"`; `tyc company financial-data "<company>"`; `tyc company listing-info "<company>"`; `tyc company income-statement "<company>"`; `tyc company balance-sheet "<company>"`; `tyc company cash-flow-statement "<company>"`; `tyc company stock-shareholders "<company>" --pageNum 1 --pageSize 10` |

## 六、意图捷径

- 用户只说"查一下这家公司"时，默认查主体画像、风险总览、经营真实性和实控摘要。
- 用户问"能不能合作/供应商准入/客户风险"时，优先查登记状态、风险总览、行政处罚、执行失信、经营异常、经营信号和资质。
- 用户问"背后是谁/实际控制人/受益人"时，优先查股东、实际控制人、受益所有人、股权树和集团信息。
- 用户问"两家公司有没有关系"时，先锚定双方，再查关联路径和关键中间节点。
- 用户问"真实经营吗"时，结合登记信息、规模、招投标、资质、许可、产品、招聘、客户供应商和必要的舆情信息。
- 用户问"商标/专利/技术实力"时，结合创新力评分、专利、商标和软著明细。
- 用户问"高管/法人背景"时，先查主要人员，再带 `--humanName` 查询人员画像和人员风险。

## 七、判断规则与输出格式

判断规则：

- 区分"查到风险记录""已查询但未返回记录""未查询该维度"。
- 不替用户做法律、投资、授信或采购最终决策；给数据驱动建议，并列出需要人工复核的材料。
- 重大风险结论必须说明依据的业务记录或数据维度，不向用户展示内部 `tyc` 命令。
- 优先使用具体记录和近期记录，不只看总数。总览和明细冲突时，直接说明冲突。
- 集团、实控和关联关系判断以路径、持股、任职、集团信息为依据，不以名称相似为依据。

输出默认使用简体中文，结论先行：

```markdown
# 商查摘要：<company>

## 结论
<1-3 句话直接回答用户问题>

## 关键信号
| 维度 | 发现 | 判断 |
|---|---|---|
| 主体 | ... | 通过/关注/异常 |
| 风险 | ... | 低/中/高 |
| 经营 | ... | 强/一般/弱 |
| 股权/关系 | ... | 清晰/需复核 |

## 依据与限制
- <关键业务记录或数据维度>
- <需要人工复核的点>

## 下一步动作
- <下一步动作>
```

深度报告时在此基础上扩展为：结论先行 → 主体与经营基础 → 风险与合规 → 股权与关联 → 经营真实性 → 待复核事项。

## 八、MCP 模式调用契约（仅远程 MCP 环境）

当前环境只接入了天眼AI远程 MCP、无法执行本地 `tyc` 命令时，遵循以下契约（查询流程、主体锚定原则、判断规则与输出格式与 CLI 模式一致）：

- MCP Server 的 `tools/list` 默认只公开小工具面；162 个业务语义聚合工具仍在服务端注册，深层维度通过能力目录和代理工具进入。
- 实体锚定优先调用公开工具 `search_companies`，参数使用 `query`。从候选表同时保留 `name` 作为后续 `company_name`、`id` 作为 `company_id`、`creditCode` 作为最终主体标识。
- 基础信息优先直接调用公开画像工具：`get_company_basic_profile`、`get_group_info`、`get_company_group_profile`、`get_company_people`、`get_person_profile`、`get_person_risk_profile`。
- 除公开画像和通用搜索工具外，调用公司维度明细前先调用 `get_company_capabilities(company_id, company_name)`，只使用返回表格中真实存在的 `tool_name`。
- 调用内部工具时使用 `call_tool`；`tool_name` 必须逐字复制能力表中的真实名称，不要翻译、改写或猜测。顶层主体参数优先传 `company_name`，只有没有精确名称时才用 `company_id`。
- 列表型工具显式传 `page`、`page_size`（默认 1 / 10）。详情型工具先从上游列表拿 `id`、`regNo` 或其他编号，再单独调用详情工具。
- 仅当同一企业下多个事实补齐互不依赖时使用 `call_tools_batch`，每批最多 3 个。关系路径、主体搜索、详情下钻、人员画像、能力发现、会决定下一步的问题不要放入 batch。
- 行业/地区/标签/榜单/关键词发现使用对应 `search_*` 入口（`search_companies_by_industry_region`、`search_companies_by_tag`、`search_companies_by_ranking`、`search_trademarks`、`search_patents`、`search_bids` 等）。
- 错误处理：能力表没有目标工具时不要猜测工具名，换用公开画像、相关搜索入口或向用户说明该维度当前未开放；`call_tool` 返回未知工具错误时，重新调用 `get_company_capabilities` 复制真实 `tool_name` 后重试一次；额度超限同 CLI 模式，转述错误信息中的说明与升级方式。
