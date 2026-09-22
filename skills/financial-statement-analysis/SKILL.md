---
name: financial-statement-analysis
description: 中小微企业财务报表深度分析：科目余额表/三大报表 → 上市+非上市双层行业基准对标 + 内置阈值判断 + 自动风险识别 + Word/HTML 双交付。当用户上传财务报表、科目余额表，或说"分析报表""这份报表健康吗""帮我看看这家公司报表""财务报表分析"时使用。
version: 1.0.0
author: 徐爱军（jsxuaijun-art）
agent_created: true
license: Proprietary
---

# 财务报表分析 Skill

为中小微企业提供财务报表深度诊断：识别财务风险、税务风险、资金链风险，产出可交付客户的
报告（Word 为主，HTML 供预览/分享）。分析以**科目余额表**细颗粒度数据为主，缺失时退回三大报表。

## 一、全局铁律（必须遵守）

1. **脱敏边界**：仅对用户**主动发送/上传**的文件脱敏（公司名拼音首字母、信用代码末 8 位 X、
   法人前两字 TT、身份证中间 8 位 X）；agent 主动联网检索（WebSearch）得到的公开数据**不脱敏**。
   交付客户真实版用本地路径，绝不入公开仓库。
2. **上市/非上市双层基准**：上市公司指标只是"优秀上限/参照"，中小微客户必须叠加非上市口径
   （行业统计、中小企业数据、同行代账样本）对标。每个对标指标在报告里**标注对标对象类型**。
3. **阈值内置为主、联网校准可选**：以 `references/threshold-library.md` 为默认真值；仅在用户要求
   或明显过时时用 WebSearch 校准，且与库不符时**先提案（指标/原值/新值/依据）再写回**，绝不静默改。
4. **异常标"可能原因"而非"肯定结论"**：对异常指标给可能性，不给断言。
5. **交付 Word 为主 + HTML 预览**：Word 必出并展示路径；HTML 一并生成用于预览/分享。
6. **路径不写死**：每次分析前探测桌面实际位置（默认 `~/Desktop/报表分析/`，回退 `~/Desktop/`），
   探测不到向用户确认。

## 二、工作流程

### 阶段 A — 初始触发协议（说了触发词但没给数据）
按优先级引导：①直接贴核心数字（推荐）②给文件路径由 agent 读取 ③口头描述几个关键数做初步判断。

### 阶段 B — 标准分析流程
1. 用户给资产负债表、利润表、现金流量表（或科目余额表）。
2. 加载 `references/threshold-library.md` 与 `references/zhang-xinmin-framework.md`。
3. 跑 `references/discovery-rules.md` 的风险扫描，异常标红/黄灯。
4. 输出 8 大板块报告，异常一律给"可能原因"。

### 阶段 C — 科目余额表自动读取（主力流程）
- **C0 路径探测**：优先 `~/Desktop/报表分析/`，其次 `~/Desktop/`；命名
  `科目余额表_{公司全称}_{年}年{月}月.xlsx`，优先 xlsx（兼容老 xls）。
- **C1 解析**：运行 `scripts/parse_ledger.py`，脚本会先打印行列结构再定位数据，自动跳过表头/
  科目标题整行，做科目口径映射与**资产负债表平衡检查**（差额 > 0.01 即红色警告）、
  **期初数=上期期末数**校验、年化指标 ×12/本期月数。输出解析结果 JSON。
- **C2 加载基准**：读取内置阈值库（双层）；如需联网校准，先向用户提案。
- **C3 风险扫描**：依据 `references/discovery-rules.md` 逐条判定，分级 🔴高/🟡中/🟢低。
- **C4 生成报告**：运行 `scripts/report_generator.py`，按固定 8 板块渲染 Word + HTML。

## 三、报告 8 大板块（顺序固定）

一、执行概要（必做）——一句话总体评价 + 核心指标对比表(今年 vs 去年 vs 行业,红绿灯) + 紧急关注 3-5 点
二、经营业绩分析-利润表（必做）——收入拆分/增长驱动力、毛利率趋势/行业对比、期间费用、净利率
三、资产结构与偿债能力-资产负债表（必做）——资产/负债结构表、流动/速动比率、资产负债率
四、运营效率分析（必做）——应收周转率(年化)、存货周转率(年化)、周转天数、存货结构
五、税务合规性提示（必做）——增值税进销项/出口退税、所得税、印花税、房产税、关联交易、个人借款视同分红
六、高新技术企业资质维护分析（如适用）——研发占比三档、高新收入≥60%、科技人员≥10%
七、风险警示（必做）——按🔴高/🟡中/🟢低分级，每条：标题→数据支撑→后果→建议
八、管理建议（必做）——紧急(本周)/短期(1-3月)/中长期(3-12月)

## 四、脚本与环境

依赖：受管 Python 3.13 + 独立 venv（`openpyxl`、`python-docx`）。首次使用先建 venv：

```bash
PY="C:/Users/Administrator/.workbuddy/binaries/python/versions/3.13.12/python.exe"
VENV="C:/Users/Administrator/.workbuddy/binaries/python/envs/fin-analysis"
"$PY" -m venv "$VENV"
"$VENV/Scripts/python.exe" -m pip install openpyxl python-docx
```

运行（用 venv 内的 python，路径写绝对）：

```bash
# 1) 解析科目余额表 → 输出解析 JSON
"$VENV/Scripts/python.exe" scripts/parse_ledger.py --input "<xlsx路径>" --output "<json路径>"
# 2) 生成报告（Word + HTML）
"$VENV/Scripts/python.exe" scripts/report_generator.py --data "<json路径>" --company "<公司简称>" --outdir "<输出目录>"
```

若用户仅贴文字数字（无文件），跳过 parse_ledger.py，由 agent 按同样口径手动填 JSON 再跑 report_generator.py。

## 五、参考文档（按需加载）

- `references/threshold-library.md` — 完整阈值库（通用默认 + 行业细分 + 资金链专项），判断真值。
- `references/discovery-rules.md` — 自动发现规则（重排去重后的 ~24 条，分类标注红黄灯）。
- `references/zhang-xinmin-framework.md` — 质量分析四维框架 + 现金流质量四象限。
- `references/tax-compliance.md` — 板块五"税务合规性提示"的内容指引。

## 六、交付规范

- 输出目录：探测到的桌面 `报表分析/` 文件夹，探测不到放桌面。
- Word 文件名：`{公司简称}财务分析报告_{年份对比}.docx`
- HTML 文件名：`{公司简称}财务分析报告_{年份对比}.html`
- Markdown：可一并生成留底（不主动展示）。
- 交付后验证：文件 >10KB、UTF-8 可打开、标题注明数据来源 + 对标对象类型；仅向用户展示 Word/HTML 路径。

## 七、Pitfalls（实现时必须处理）

1. 表头在第 1-2 行、数据常从第 3 行起；"科目标题"整行跳过。
2. 期初数必须与上期期末核对一致。
3. xlsx 直接读即可；不要在 NTFS 上建 egg-info。
4. 年化指标：本期为 X 个月数据时必须 ×12/X。
5. 应收/存货平均余额用期初期末均值。
6. 个人借款视同分红、关联方往来是税务红线。
7. 阈值判断优先行业口径，不套通用值。
8. 所有数字格式化 `f'{v:,.2f}'`。
9. 报告每处异常给"可能原因"，不下断言。
