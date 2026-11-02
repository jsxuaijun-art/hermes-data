---
name: evidence-verification-report
description: 核查证据型报告：权威信源+编号链接，中文交付 .docx/.txt 不用 md。
version: 1.0.0
author: Hermes Agent + 徐总
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Verification, Reports, Citations, Health, Docx, Chinese]
    category: research
---

# Evidence-Verification Report（核查证据型报告交付）

用户提出的"某个说法有没有依据/值不值得做"类请求（医学、健康、疫苗、
政策、谣言核实等）产出的交付物：**逐条编号引用 + 可点击超链接 + 中文
为主**。本文是这类"核查型文档"的统一做法，区别于内容创作。

## When to Use

- 用户要"查一下某说法真假/有没有文献/值不值得（打疫苗、投资、方案）"。
- 用户明确要求"核实""核查""有没有依据/文献/链接"。
- 需要把多来源证据整理成可核验的正式文档交给用户或医生/第三人。
- 尤其适用于用户本人可能被误导的健康/疫苗/政治类说法核查。

## 铁律（用户偏好）

1. **交付格式不用 markdown**。用户明确说"以后也不需要md格式"。
   交付用纯文本 `.txt` 或 Word `.docx`。
2. **每条引用都给编号 + 可点击链接**，双击能跳转（PubMed/官网/权威机构）。
3. **中文为主**，可保留英文标题/术语对照。
4. **分域拆文档**：医学类问题归医学报告，政治/阴谋论类（如"生物战、
   灭种、基因战"）单独成文，不混在一个文件里。
5. **回答用户真正的问题**：核实完"有无依据"后，给出明确行动建议
   （该不该做、对谁、几岁、风险权衡），不要只罗列文献。

## 信源层级（国外优先，用户会要求少用国内源）

1. 权威机构原文：CDC / FDA / EMA / WHO（含 GACVS 声明）。
2. 同行评审期刊：Lancet、NEJM、JAMA 及 PMC 上大型队列研究/荟萃分析。
   注意**撤稿论文即学术不端证据**（如 Lancet 1998 Wakefield 被撤）。
3. 事实核查机构（针对谣言/阴谋论）：FactCheck.org、Snopes、AP、AFP、
   Lead Stories、PolitiFact。判定词汇：FALSE / MISSING CONTEXT / 无法证实。
4. 每个子主张单独查（如"疫苗铝汞""比尔盖茨减人口""NSSM-200"各自一查），
   逐一给判定，不要合并成一团。

## Procedure

1. 先用英文关键词搜索国外权威源（规避国内二手信息，用户会要求）。
2. 逐条登记来源：编号 + 原文标题 + URL。
3. 分域组织：医学证据一章、非医学（谣言/政治）另一章或另一文件。
4. 每条引用补一句"这条支持/反驳什么"。冲突来源并列呈现，说明采信哪个。
5. 用引用清单（sources.py / python-docx 超链接）生成可点击参考文献段。
6. 结尾给"结论 + 行动建议"：明确该不该做、对谁、注意事项。
7. 验证：重开 .docx 抽查超链接数与文字齐全；数 rels 中 hyperlink 数。

## python-docx 可点击超链接

python-docx 无原生 hyperlink API，须建 relationship 再注 XML。直接复用：

```
python scripts/hyperlink_docx.py in.docx out.docx   # 或复制脚本内 add_hyperlink()
```

核心思路：`paragraph.part.relate_to(url, RELATIONSHIP_TYPE.HYPERLINK,
is_external=True)` 拿 r_id → 构造 `<w:hyperlink r:id=...><w:r><w:rPr><w:color/>
<w:u/></w:rPr><w:t>文本</w:t></w:r></w:hyperlink>` 追加到 `paragraph._p`。
同一 URL 重调用会幂等复用 r_id。颜色用 `0x1F3B73`（int，无 # 前缀）。
详见 `references/python-docx-hyperlinks.md` 与 `scripts/hyperlink_docx.py`。
本 skill 自带已核实的疫苗核查锚点事实（Shingrix 有效率/副作用、HPV 年龄
窗口、撤稿文献、盖茨/NSSM-200 判定），见 `references/vaccine-claim-anchors.md`。

## Pitfalls

- 不要只搜国内来源或只给来源名不给可跳转链接（抓图/引证须给真链接）。
- 医学与政治阴谋论混写 = 用户不要的结构；先问或直接拆分。
- "副作用存在"≠"不值得打"：要同时给有效性、副作用概率、成本效益，
  让用户能自己权衡。
- 引用的数字（有效率、发生率、剂量）必须与来源文字逐字一致，拿不准就
  标"待核实"并点名要用户核对，绝不硬造。
- 生成 .docx 后必须验证（Word 打不开=失败）；验证脚本见 bundled `docx`
  技能的 validation 步骤。
