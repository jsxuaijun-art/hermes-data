# Categorized Multi-Section Document Pattern (分类目录式文档)

用于生成 **按分类组织的目录式 .docx 文档** — 数据分门别类排列，每类带独立表头和分隔标识，适合技能清单、产品目录、制度汇编、政策汇编等场景。

## 适用场景

- 技能清单/工具目录（按功能分类：AI代理、短视频、GEO、运维……）
- 产品手册（按产品线分类）
- 规章制度汇编（按部门或制度类型分类）
- 政策法规汇编（按税种或行业分类）

## 核心模式

文档结构：
  文档标题 + 前言
  ├─ 一、分类A  ┌────┬────┬────┐
  │            │序号│名称│说明│
  │            ├────┼────┼────┤
  │            │ 1  │项目1│描述│
  │            └────┴────┴────┘
  ├─ 二、分类B  ┌────┬────┬────┐
  │            │ ...│ ...│ ...│
  │            └────┴────┴────┘
  └─ ...

## 推荐实现 (python-docx)

### 步骤一：数据准备

```python
CATEGORIES = [
    {
        "id": "一",
        "name": "AI代理 & 自动化",
        "items": [
            {"no": 1, "name": "autonomous-ai-agents", "desc": "多智能体编排框架"},
            {"no": 2, "name": "hermes-agent", "desc": "Hermes Agent 本体"},
        ],
    },
    {
        "id": "二",
        "name": "短视频 & 内容创作",
        "items": [
            {"no": 9, "name": "short-video-copywriting", "desc": "短视频文案创作完整工作流"},
        ],
    },
]
```

### 步骤二：生成文档

```python
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml

doc = Document()

# 设置全局字体
style = doc.styles['Normal']
font = style.font
font.name = '微软雅黑'
font.size = Pt(10.5)
style.element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')

# 文档标题
title = doc.add_heading(level=0)
run = title.add_run("Hermes Agent 技能清单")
run.font.name = '微软雅黑'
run.font.size = Pt(22)
run.font.color.rgb = RGBColor(0x1A, 0x3C, 0x6E)
run.element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')

table_headers = ["序号", "英文名", "说明"]

for cat in CATEGORIES:
    # 分类标题（加粗大号段落，不带表格边框）
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    r = p.add_run(f"{cat['id']}、{cat['name']}")
    r.bold = True
    r.font.name = '微软雅黑'
    r.font.size = Pt(14)
    r.font.color.rgb = RGBColor(0x1A, 0x3C, 0x6E)
    r.element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')

    # 表格
    rows_data = [[str(item['no']), item['name'], item['desc']] for item in cat['items']]
    table = doc.add_table(rows=1 + len(rows_data), cols=len(table_headers))
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # 表头
    for ci, header in enumerate(table_headers):
        cell = table.rows[0].cells[ci]
        cell.text = ''
        r = cell.paragraphs[0].add_run(header)
        r.bold = True
        r.font.name = '微软雅黑'
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="1A3C6E"/>')
        cell._tc.get_or_add_tcPr().append(shading)

    # 数据行
    for ri, row_data in enumerate(rows_data):
        for ci, val in enumerate(row_data):
            cell = table.rows[ri + 1].cells[ci]
            cell.text = ''
            r = cell.paragraphs[0].add_run(str(val))
            r.font.name = '微软雅黑'
            r.font.size = Pt(9)
            r.element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')
            if ri % 2 == 1:
                shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F0F4FA"/>')
                cell._tc.get_or_add_tcPr().append(shading)

    doc.add_paragraph()

doc.save(output_path)
```

## 内容验证技巧

生成后**不打开 Word** 即可验证分类和内容位置：

```python
import zipfile, re

def verify_docx_content(path, checks):
    """
    checks: [(expected_text, must_be_after_text_or_None), ...]
    """
    with zipfile.ZipFile(path) as z:
        xml = z.read('word/document.xml').decode('utf-8')
    texts = re.findall(r'<w:t[^>]*>([^<]*)</w:t>', xml)
    full_text = ' '.join(texts)

    results = {}
    for i, (needle, after) in enumerate(checks):
        pos = full_text.find(needle)
        if pos == -1:
            results[f"check_{i}"] = f"❌ 未找到 '{needle}'"
        elif after:
            after_pos = full_text.find(after)
            if after_pos == -1:
                results[f"check_{i}"] = f"❓ 找到了 '{needle}'，但参考文本 '{after}' 未找到"
            elif pos <= after_pos:
                results[f"check_{i}"] = f"❌ '{needle}' 在 '{after}' 之前（期望在后）"
            else:
                results[f"check_{i}"] = f"✅ '{needle}' 在 '{after}' 之后 ✓"
        else:
            results[f"check_{i}"] = f"✅ '{needle}' 已找到 ✓"
    return results

print(verify_docx_content('output.docx', [
    ("GEO 搜索优化", "短视频"),
    ("网站 & 技术运维", "GEO 搜索优化"),
]))
```

## 常见问题

1. **字符溢出**：如果文档超过500项，确保 python-docx 不因内存不足崩溃。分批生成或分段保存。
2. **分类顺序校验**：始终用上述验证函数检查分类顺序，特别是在调整后。
3. **中文标题对齐**：分类标题后的空格用全角空格（\u3000）保持视觉对齐。
4. **序号跨分类连续性**：如果要求全局统一编号，需在所有分类数据合并后重新编号。
