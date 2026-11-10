---
name: tax-exam-grading
description: 上传税务师/注税等财税考试PDF，自动判卷并出【答案+解析+速查表】Word。
version: 1.0.0
author: 徐爱军 (jsxuaijun-art)
license: Proprietary. LICENSE.txt has complete terms
agent_created: true
metadata:
  hermes:
    tags: [exam, tax, grading, ocr, docx, 税务师, 判卷]
    category: education
    related_skills: [pdfkit-py, docx, cn-regulation-verification, chinese-exam-preparation]
---

# 财税考试判卷（tax-exam-grading）

收到用户上传的税务师、注册会计师(税法)等财税考试卷（PDF/扫描件），逐题作答、给解析，并输出一份含「答案+解析+答案速查表」的 Word 交付物。判卷口径默认按「考试标准答案」，同时在涉及新旧法处标注差异。

## When to Use

- 用户上传财税考试卷（税务师《税法一/税法二/涉税服务实务》《财务与会计》、注会《税法》等），要求"做题/判卷/给答案+解析"。
- 触发词：税务师 / 注税 / 考前预测卷 / 模拟卷 / 传PDF做一遍 / 出答案解析 / 判卷。

## Prerequisites

- PDF 读取：`read_file`（有文字层直接抽）；扫描件无文字层时需 OCR——本机 tesseract(chi_sim+eng)+pymupdf+pdf2image，或用 `pdfkit-py` 技能（`extract_text --ocr_fallback`）。
- Word 生成：python-docx（中文需设 eastAsia 字体）。
- 法条核验：用 `cn-regulation-verification` / `tax-regulation-monitor` / `web_search` 核现行条文（政策库 fgk.chinatax.gov.cn）。

## How to Run

1. 定位并确认 PDF 存在；`read_file` 尝试抽文字。
2. 抽不到（扫描件）→ `pdfkit.py to_images`(或 pymupdf) 渲染 300dpi 分页图 → tesseract `chi_sim+eng --psm 6` 逐页 OCR。
3. 识别卷面结构（单选/多选/简答/综合），逐题作答并写解析。
4. 生成「答案+解析+速查表」Word（见 Procedure）。
5. 交付到用户桌面（默认 `C:\Users\Admin\Desktop`；若源文件在其他目录则放同目录，只报 Windows 路径）。

## Quick Reference

| 步骤 | 命令/做法 |
|---|---|
| 找文件 | `ls -la <路径>`（WSL 下 D:→/mnt/d/） |
| 抽文字 | `read_file <pdf>` |
| 扫描件OCR | pymupdf 渲染 + `tesseract pXX.png stdout -l chi_sim+eng --psm 6` |
| 出Word | `python3 scripts/md2docx_cn.py <md> <out.docx>` |
| 判卷口径 | 默认按考试标准答案；新旧法差异处标注 |

## Procedure

1. **读卷**：确认文件存在 → `read_file` 抽文字。扫描件走 OCR，逐页通读，识别题型与分值。
2. **判卷口径自检**：先明确"算分用(考试标准口径)"还是"实务用(最新法)"——默认考试标准口径；每题遇到新旧法冲突（如增值税法2026配套、公司法2023修订、职工教育经费比例、一般纳税人年销售额口径）时，在解析里标注。
3. **逐题作答**：
   - 单选/多选：给答案字母 + 解析，锚定法条"名称+条+款+项"，不用"根据相关法律规定"。
   - 简答/综合：分点作答，涉及计算列过程并保留题目要求的小数位；会计分录按题目单位（元/万元）给出。
   - 分录/账务处理题核对借贷平衡。
4. **标争议**：口径不确定的题，解析里明确"⚠ 建议以官方答案复核"，并尽量给双口径说明。
5. **速查表**：文末附单选题/多选题答案串，方便对答案。
6. **出 Word**：先把答案写成 `.md`，再用 `scripts/md2docx_cn.py` 转 `.docx`（自动设中文字体微软雅黑、标题深蓝、分隔线、列表）。
7. **交付**：落桌面，报 Windows 路径（`D:\...` 或 `C:\...`）；同步保留 `.md` 原稿或按交付习惯打包。

## Pitfalls

- **扫描件 OCR 噪点**：数字/选项字母可能误识别（如 1500000 vs 1200000、B/C）。作答时用财税逻辑校验关键数字；实在无法确认的在解析里标注。严禁在没有任何 OCR 结果时编造卷面内容。
- **官方答案在会员端**：很多考前预测卷（如"之了课堂"）标准答案藏在微信扫码/登录的会员解析里，网上检索不到。能核到法条层依据就给出确定性结论，并如实告知"最终以官方答案解析为准"，绝不冒充已拿到官方答案。
- **考试口径 vs 最新法**：考试按当年教材/注税协会口径，可能与最新法冲突。两套都说明，别混。
- **分清"算分用"与"实务用"**：用户要算分就按标准答案口径；要实务就按现行法。
- **ocr 命令限制**：`--psm 6` 适合正文；表格/排版乱时试 `--psm 3`；中文用 `chi_sim+eng`。

## Verification

- Word 能打开且中文正常（回读感看：标题、分隔线、答案速查表都在）。
- 每道题答案给出明确字母/数值，解析有法条依据或计算过程。
- 争议题已在解析中标注并给出核验依据。
- 交付物在 Windows 桌面/lib 报的是 Windows 路径。
