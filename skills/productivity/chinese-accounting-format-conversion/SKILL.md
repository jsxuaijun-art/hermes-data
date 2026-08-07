---
name: chinese-accounting-format-conversion
description: "Convert Chinese accounting statements between formats: 小企业会计准则 ↔ 民间非营利组织, 企业会计制度 ↔ 民非, etc. Covers data extraction from PDF/Excel, mapping rules, and PDF/Excel output generation."
version: 1.0.0
author: Hermes Agent
tags: [accounting, chinese, format-conversion, pdf, excel, non-profit, 民间非营利组织]
---

# Chinese Accounting Format Conversion

Convert balance sheets and other accounting statements between different Chinese accounting standards.

## Trigger

When the user asks to:
- Convert a balance sheet to 民间非营利组织 (non-profit) format
- Convert between 小企业会计准则 and 企业会计制度
- Generate formatted accounting documents in PDF or Excel
- "资产负债表改成民非格式"

## Common Conversion: 小企业会计准则 → 民间非营利组织

### Format Mapping

| 小企业会计准则 | 民间非营利组织 | Notes |
|---|---|---|
| 所有者权益(或股东权益) | 净资产 | 完全替代关系 |
| 实收资本(或股本) | → 并入非限定性净资产 | 民非没有"实收资本"概念 |
| 未分配利润 | → 并入非限定性净资产 | 负数直接体现 |
| 资本公积 | → 并入非限定性净资产 | |
| 盈余公积 | → 并入非限定性净资产 | |
| 应收账款 + 预付账款 + 其他应收款 | **应收款项** | 合并为一个科目 |
| 应付账款 + 其他应付款 | **应付款项** | 合并为一个科目 |
| 应付职工薪酬 | **应付工资** | 科目重命名 |
| 应交税费 | **应交税金** | 科目重命名 |
| 长期债券投资 | **长期债权投资** | 科目重命名 |

### 限定性净资产 vs 非限定性净资产

- **非限定性净资产** = 原所有者权益合计（无限制用途的净资产）
- **限定性净资产** = 有指定用途的净资产（如专项拨款、捐赠限定）
- 如果原始表中没有区分，全部归入非限定性净资产

### 具体转换公式

```
应收款项_期末 = 应收账款_期末 + 预付账款_期末 + 其他应收款_期末
应收款项_年初 = 应收账款_年初 + 预付账款_年初 + 其他应收款_年初

应付款项_期末 = 应付账款_期末 + 其他应付款_期末
应付款项_年初 = 应付账款_年初 + 其他应付款_年初

非限定性净资产_期末 = 所有者权益合计_期末
非限定性净资产_年初 = 所有者权益合计_年初

限定性净资产 = 0 (默认，除非有专项拨款数据)
```

### 数据校验规则

转换后必须满足：
```
资产总计 = 负债合计 + 净资产合计
```
与原始表的 `资产总计 = 负债合计 + 所有者权益合计` 恒等。

## Data Sources

### From .xls (Excel 97-2003)
Use `xlrd`:
```python
import xlrd
wb = xlrd.open_workbook(path)
sh = wb.sheet_by_index(0)
```

### From .xlsx (Excel 2007+)
Use `openpyxl`:
```python
from openpyxl import load_workbook
wb = load_workbook(path)
ws = wb.active
```

### From PDF
Use `pdftotext` (poppler-utils) or `pymupdf`:
```python
import pymupdf
doc = pymupdf.open(path)
text = doc[0].get_text()
```

**Important**: Chinese PDFs often use left-right dual-column layout. `pdftotext` interleaves both columns. Parse carefully — cross-check against Excel data if available. Excel data is more reliable than PDF extraction for Chinese dual-column layouts.

## Output Generation

### Excel (.xlsx) with openpyxl

```python
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill

# Styles
THIN = Side(style='thin')
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
FONT_TITLE = Font(name='微软雅黑', size=14, bold=True)
FONT_HEADER = Font(name='微软雅黑', size=9, bold=True, color='FFFFFF')
FONT_NORMAL = Font(name='微软雅黑', size=9)
FONT_SMALL = Font(name='微软雅黑', size=8)
FONT_BOLD = Font(name='微软雅黑', size=9, bold=True)
FILL_HEADER = PatternFill('solid', fgColor='336699')
FILL_SECTION = PatternFill('solid', fgColor='4472C4')
FILL_ALT = PatternFill('solid', fgColor='F2F2F2')
```

For a complete working script, see `scripts/convert_minsheng_balance_sheet.py` which reads .xls (xlrd), maps to 民非 format, and produces a styled .xlsx with proper table borders, header colors, number format `#,##0.00`, alternating row fills, and signature footer.

### PDF with reportlab

**Font selection is critical** — the default Chinese font on Ubuntu WSL (`DroidSansFallbackFull`) contains CJK characters but **does NOT contain ASCII digits (0-9), commas, periods, or parentheses**. PDFs generated with it will have invisible numbers.

**Required font: WenQuanYi Micro Hei**
```bash
apt-get install fonts-wqy-microhei
pip install fonttools reportlab
```
Extract the first subfont from .ttc (reportlab's TTFont does not support .ttc natively):
```bash
python3 -c "
from fontTools.ttLib import TTCollection
ttc = TTCollection('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc')
ttc.fonts[0].save('/usr/share/fonts/truetype/wqy/wqy-microhei-regular.ttf')
"
```

**Register and use in reportlab:**
```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont('WQY', '/usr/share/fonts/truetype/wqy/wqy-microhei-regular.ttf'))

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

# Define paragraph styles using the registered font
styles = getSampleStyleSheet()
styles.add(ParagraphStyle('CNTitle', fontName='WQY', fontSize=14, leading=20,
    alignment=TA_CENTER, spaceAfter=6))
styles.add(ParagraphStyle('CNNormal', fontName='WQY', fontSize=9, leading=13,
    alignment=TA_CENTER))
```

**Building a table-based PDF (balance sheet style):**
```python
doc = SimpleDocTemplate(output_path, pagesize=landscape(A4),
    topMargin=1.5*cm, bottomMargin=1.0*cm,
    leftMargin=1.5*cm, rightMargin=1.5*cm)
elements = []

# Title
elements.append(Paragraph('资产负债表', styles['CNTitle']))
elements.append(Paragraph('（适用民间非营利组织）', styles['CNNormal']))

# Table: data rows are lists of Paragraph objects
table_data = []
for row in source_rows:  # [label, seq, period_end, period_start]
    table_data.append([Paragraph(cell, styles['CNNormal']) for cell in row])

t = Table(table_data, colWidths=[7*cm, 2*cm, 5*cm, 5*cm])
t.setStyle(TableStyle([
    ('FONTNAME', (0, 0), (-1, -1), 'WQY'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
    ('ALIGN', (1, 0), (1, -1), 'CENTER'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#336699')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
]))
elements.append(t)
doc.build(elements)
```

**Avoid `keepWithNext` on PDF table rows** — reportlab's TableStyle does not support this attribute. Use `SPLIT_BY_ROW` or set row heights manually if you need page-break control.

### Number Format
Use `#,##0.00` for Excel cells. Display negative numbers in parentheses `(1,234.56)` for Chinese accounting conventions.

### Legacy .doc Processing Pipeline

When you need to read or merge content from old-format `.doc` files (common for Chinese accounting reports):

```bash
# Extract text from .doc (antiword handles Chinese best; catdoc is fallback)
antiword input.doc 2>/dev/null || catdoc input.doc

# Convert .doc → .docx for python-docx editing
libreoffice --headless --convert-to docx --outdir /tmp/ input.doc
# Output: /tmp/input.docx

# Read the converted .docx with python-docx
from docx import Document
doc = Document('/tmp/input.docx')
for p in doc.paragraphs:
    print(p.text)
```

**Merging content from one .doc into another's specific sections** (e.g., merging 清算事项说明 into 清算审计报告):
1. Extract text from source .doc via antiword to understand its structure
2. Convert target .doc → .docx via libreoffice
3. Read the .docx, locate section markers (e.g., '四、' headings), insert content
4. Save to a **new filename** to avoid PermissionError if original is open in Word

**Avoid `PermissionError`**: If the original `.doc` file is open in Word on Windows, `doc.save()` to a new filename (e.g., `-更新版.docx` suffix), not the same path.

## Pitfalls

1. **PDF dual-column layout**: `pdftotext` interleaves left and right columns. The text line `货币资金 1 908,827.23 短期借款 31` means 货币资金 is in the left column's 期末余额 and 短期借款 is in the right column. Don't read it as sequential data.

2. **Zero vs empty**: In Chinese balance sheets, a blank cell means "no data" while 0 means "zero balance". When converting, treat 0 values as blank/empty unless they're in a total/合计 row.

3. **Negative prepayments/ receivables**: 预付账款 and 应收账款 can appear as negative numbers (credit balances). Keep the sign — they represent 预收款项 and 应付款项 in disguise.

4. **Asset total may not equal sum of sub-items** in the original data because some items are omitted from detail rows. Always use the 合计/总计 row values from the original, not computed from sub-items.

5. **openpyxl Border keyword**: Use lowercase `left=`, `right=`, `top=`, `bottom=` (openpyxl v3+). Uppercase `LEFT=` causes TypeError.

6. **Font glyph check**: Before generating PDFs with Chinese text, verify the font has both CJK and ASCII digit glyphs:
   ```bash
   python3 -c "
   from fontTools.ttLib import TTCollection, TTFont
   path = '/path/to/font.ttf'
   f = TTFont(path)
   cmap = f.getBestCmap()
   for ch in '0123456789,.()-':
       ok = 'OK' if ord(ch) in cmap else 'MISSING'
       print(f'{repr(ch)}: {ok}')
   "
   ```
