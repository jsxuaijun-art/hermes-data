---
name: word-documents
title: Word Documents
description: Create, format, and convert rich Word (.docx) documents — python-docx for rich formatting, pure-stdlib fallback for minimal environments, and markdown-to-docx conversion for large Chinese-government-style reports.
trigger: user asks to create a Word document, convert to .docx, save as Word format, or generate a formatted document for print/sharing.
category: productivity
---

# Word Documents with python-docx

Create richly formatted Word documents for Chinese users: complex tables with styled headers, alternating row colors, Chinese fonts (微软雅黑), headings hierarchy, and clean page layout.

## Core Setup

```python
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml
```

### Global Font (Chinese)

```python
doc = Document()
style = doc.styles['Normal']
font = style.font
font.name = '微软雅黑'
font.size = Pt(10.5)
style.element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')
```

This `rFonts.set(qn('w:eastAsia'), '字体名')` call is **required** for every text run that contains Chinese characters — without it, Word may fall back to a default font that garbles Chinese text.

### Page Margins

```python
for section in doc.sections:
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)
```

## Helper Functions

### Headings

```python
def add_heading_custom(text, level=1):
    h = doc.add_heading(level=level)
    r = h.add_run(text)
    r.font.name = '微软雅黑'
    r.element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')
    sizes = {1: 18, 2: 14, 3: 12, 4: 11}
    colors = {1: '1A3C6E', 2: '1A3C6E', 3: '2D5F8A', 4: '2D5F8A'}
    r.font.size = Pt(sizes.get(level, 11))
    c = colors.get(level, '1A3C6E')
    r.font.color.rgb = RGBColor(int(c[0:2],16), int(c[2:4],16), int(c[4:6],16))
```

### Paragraphs

```python
def add_para(text, bold=False, italic=False, size=10.5, color=None, align=None):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.name = '微软雅黑'
    r.font.size = Pt(size)
    r.element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')
    r.bold = bold
    r.italic = italic
    if color: r.font.color.rgb = color
    if align: p.alignment = align
```

### Cell Shading

```python
def shade_cell(cell, color):
    """Set background color of a table cell."""
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color}"/>')
    cell._tc.get_or_add_tcPr().append(shading)
```

### Tables with Header Row + Alternating Row Colors

```python
def add_table(headers, rows, col_widths=None):
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Header row
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]
        c.text = ''
        r = c.paragraphs[0].add_run(h)
        r.font.name = '微软雅黑'
        r.font.size = Pt(9.5)
        r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')
        c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        shade_cell(c, '1A3C6E')  # dark blue header

    # Data rows with alternating color
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            c = t.rows[ri+1].cells[ci]
            c.text = ''
            r = c.paragraphs[0].add_run(str(val))
            r.font.name = '微软雅黑'
            r.font.size = Pt(9)
            r.element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')
            if ri % 2 == 1:
                shade_cell(c, 'F0F4FA')  # light blue-gray

    # Column widths
    if col_widths:
        for row in t.rows:
            for i, w in enumerate(col_widths):
                row.cells[i].width = Cm(w)

    doc.add_paragraph()  # spacing after table
```

## File Paths on Windows via WSL

Windows paths in WSL: `/mnt/c/Users/<username>/Desktop/filename.docx`

To discover the Windows username: `ls /mnt/c/Users/` (ignore `All Users`, `Default`, `Public`, `desktop.ini`)

Save the document:
```python
doc.save('/mnt/c/Users/jiangmin/Desktop/文件名.docx')
```

## Pitfalls

1. **Chinese font encoding**: Every `Run` that contains Chinese text MUST call `.element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')`. Without this, Word on non-Chinese systems may substitute a font that garbles Chinese text. This applies even if you set `run.font.name`.

2. **`.doc` vs `.docx`**: Legacy `.doc` files may actually be RAR archives in disguise (e.g., from shijuan1.com). Run `file filename.doc` to check — if it says "RAR archive data", extract with `unrar x filename.doc` to get the real `.docx`.

3. **Table fonts**: python-docx's `table.style` (e.g., 'Table Grid') may override run-level font settings. Always set font explicitly on each cell's run after setting cell text.

4. **Save path validation**: Before saving, verify the target directory exists. WSL's `/mnt/c/` mounts can have case-sensitive paths.

5. **Avoid `w:shd` color string parsing errors**: Use `parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color}"/>')` — `nsdecls("w")` is critical for the XML namespace.

## Verification

```bash
# Check file type and size
file /mnt/c/Users/jiangmin/Desktop/输出文件.docx
ls -lh /mnt/c/Users/jiangmin/Desktop/输出文件.docx
```

## User Delivery Preferences (江姐专属)

**核心规则：Word (.docx) 是默认交付格式，不是备选。**

- ⚡ 所有文档类产出，**默认先出 .docx 版本**。.md 版本可以做辅助，但不是主交付物。
- 🚫 生成的文档**不发企业微信群给团队看**。文件直接放桌面 `D:\\360MoveData\\Users\\Admin\\Desktop\\`。
- ✅ 交付格式：.docx 格式化版本（含正规排版、字体、表格）为最终交付标准。
- 📋 如果同时需要 .md 版本，在 .docx 之后生成。
- 📊 **数据模板类产出（需填写计算的表格）→ 默认追加 .xlsx 版本**。用户明确说过"输出为Excel格式"，对于需勾稽校验的财务模板，Excel 天然对齐 + 自动计算，比 Word 表格更适合。参见下方 `Excel Workbook Alternative` 章节及 `references/excel-financial-workbook-patterns.md`。
  - 生成路径：先出 .xlsx（用 openpyxl），让用户确认可打开
  - 再补 .docx 版本（用 python-docx），供正式存档/打印使用

### Windows 路径速查

用户桌面路径（WSL映射）：
```
/mnt/d/360MoveData/Users/Admin/Desktop/
```

### 操作流程

1. 确认用户要生成的文档类型和内容
2. 优先用 `python-docx`（pip install python-docx 可安装）
3. 环境受限时降级到纯 stdlib 方案（见下方 Fallback 章节）
4. 生成后放桌面，报文件路径即可
5. 需要 Word 格式的发送版本直接用 .docx 输出

### 不宜场景

- 非正式沟通/群聊消息 → 直接用文字回复
- 用户明确要求 Markdown → 尊重要求但仍可附带 .docx

---

## Fallback: Stdlib-Only .docx (No python-docx)

When `python-docx` is unavailable (WSL, minimal containers, no pip), generate .docx files using pure Python stdlib with string-based OOXML construction:

```python
import zipfile, xml.parsers.expat, xml.sax.saxutils

def make_docx(path, html_body):
    """Create a .docx from an HTML string using pure stdlib."""
    from xml.sax.saxutils import escape
    document_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas"
            xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
            xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <w:body>
    <w:p><w:r><w:rPr><w:rFonts w:ascii="SimSun" w:eastAsia="SimSun"/><w:sz w:val="24"/></w:rPr><w:t xml:space="preserve">{escape(html_body)}</w:t></w:r></w:p>
  </w:body>
</w:document>'''
    # ... construct full OOXML with [Content_Types].xml, document.xml, rels
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('word/document.xml', document_xml)
        z.writestr('[Content_Types].xml', content_types_xml)
        # etc.
```

### When to use
- WSL/minimal environment where `pip install python-docx` fails
- No network access to install packages
- Simple documents with basic formatting (fonts, sizes, paragraphs)

See `references/generate-docx-without-python-docx.md` for the full implementation.

## Chinese Financial Template Patterns

For Chinese government-document-style financial/accounting templates (税务合规报告、纳税调整表、期初余额调整表、会计政策说明书 etc.), the document structure follows a reusable pattern:

```
Title → Applicability → Formula Flowchart → Main Table → Detail Schedules → Journal Entries → Operational Checklist
```

See `references/chinese-financial-template-patterns.md` for the full structural pattern, font/size/table conventions, and per-scenario adaptations.

### Excel Workbook Alternative

When the user needs a fillable data template with automatic calculations instead of a narrative Word document, offer .xlsx format. See `references/excel-financial-workbook-patterns.md` for:

- When to choose Excel vs Word
- Multi-sheet structure for financial adjustment workbooks
- Color code convention (yellow=input, green=formula, red=check)
- Formula injection patterns (SUM, IF+N, 倒轧, cross-sheet references)
- Merged cells handling pitfall
- Multi-category section layout pattern

Key signal: user requests reformatting of structured data and you're struggling with ASCII compliance → offer .xlsx as a native-grid alternative that avoids the alignment problem entirely.

### Pure Stdlib .xlsx (No openpyxl)

When openpyxl is unavailable (pip blocked by PEP 668, network timeout), generate .xlsx files using pure Python stdlib with string-based OOXML construction. The approach mirrors the pure stdlib .docx fallback — zipfile + XML string building.

- Header row with deep blue (`FF1A3C6E`) background + white bold text
- Shared string table for all cell values
- Works in any Python 3 environment with no external dependencies
- Cell type: shared string (`t="s"`) for text, direct value for numbers

See `references/generate-xlsx-without-openpyxl.md` for the full implementation with a reusable `make_xlsx()` function template.

**When to use this instead of Excel Workbook Alternative (openpyxl):**
- No pip access / PEP 668 restriction
- Need to generate a simple structured .xlsx quickly
- Data is static (no formulas, no merged cells, no conditional formatting)

## Fallback: Markdown to .docx Conversion

Convert large Markdown documents (500-1000+ lines) to .docx with proper Chinese government-document formatting:

- 仿宋 (FangSong) body text
- 黑体 (SimHei) main headings  
- 楷体 (KaiTi) sub-headings
- Automatic table conversion with shading
- Page number and header/footer support

```bash
python3 -c "
import re, zipfile, xml.sax.saxutils
# Parse markdown headings, paragraphs, tables
# Build OOXML zip structure
# Output: output.docx
"
```

### When to use
You have a large Markdown report and need both .md and .docx deliverables in a minimal environment without python-docx.

See `references/markdown-to-word-converter.md` for the full implementation.

---

## Advanced: Replace Markdown Pseudo-Tables with Real Word Grid Tables in Existing .docx

When an existing .docx file contains text-based pseudo-tables (Markdown `|---|` pipe tables, ASCII art grids like `┌┬┐│├┼┤`, or any text rendered as monospaced columns), replace them with proper Word grid tables using pure Python stdlib (no python-docx required).

### Why this is needed

- The user's `.docx` files were **originally generated from Markdown** and still contain embedded Markdown pipe tables as literal text
- Word does not render these as tables — they appear as ugly monospaced text blocks
- python-docx may not be available in the environment (PEP 668, no network, WSL)
- Solution: manipulate the `.docx` (which is a ZIP of XML files) directly via string operations

### Core Technique

```python
import zipfile, re, copy
from xml.sax.saxutils import escape

def replace_markdown_tables_in_docx(in_path, out_path):
    """
    Read a .docx file, find text-based pipe tables in paragraphs,
    and replace them with real Word grid tables.
    """
    with zipfile.ZipFile(in_path, 'r') as zin:
        doc_xml = zin.read('word/document.xml').decode('utf-8')

    # 1. Parse the document body
    body_match = re.search(r'<w:body>(.*?)</w:body>', doc_xml, re.DOTALL)
    body_content = body_match.group(1)

    # 2. Find paragraph blocks containing pipe-table-like content
    #    A pipe table paragraph looks like: <w:p>...<w:t>| Col1 | Col2 |</w:t>...</w:p>
    #    Tables span multiple consecutive <w:p> elements

    def parse_pipe_table(lines):
        """Parse pipe-table lines into headers + rows + column widths."""
        # lines: list of text strings (stripped)
        # Find separator line: |---|---|
        sep_idx = None
        for i, line in enumerate(lines):
            if re.match(r'^[\s\|:\-]+$', line) and '---' in line:
                sep_idx = i; break
        if sep_idx is None: return None

        header_text = lines[0]
        data_lines = lines[sep_idx+1:]

        def split_row(text):
            return [c.strip() for c in text.strip().strip('|').split('|')]

        headers = split_row(header_text)
        # Strip separator dashes and leading/trailing pipes, then split
        sep_parts = [c.strip() for c in lines[sep_idx].strip().strip('|').split('|')]
        col_widths = [max(len(h) + 2, 6) for h in headers]  # min width

        rows = [split_row(l) for l in data_lines if l.strip()]

        return headers, rows, col_widths

    # 3. Build a Word grid table XML snippet
    def make_table_xml(headers, rows, col_widths=None):
        """Generate <w:tbl> XML from parsed table data."""
        if col_widths is None:
            col_widths = [2000] * len(headers)

        # Table grid cols
        grid_cols = ''.join(
            f'<w:gridCol w:w="{w*200}" />' for w in col_widths
        )

        # Build rows
        def make_cell(text, is_header=False):
            # Bold for header
            bold_xml = '<w:b/>' if is_header else ''
            shading_xml = '<w:shd w:val="clear" w:color="auto" w:fill="1A3C6E"/>' if is_header else ''
            return f'''<w:tc>
              <w:tcPr><w:tcW w:w="2000" w:type="dxa"/>{shading_xml}</w:tcPr>
              <w:p><w:r><w:rPr><w:rFonts w:ascii="微软雅黑" w:eastAsia="微软雅黑"/><w:sz w:val="18"/>{bold_xml}</w:rPr><w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p>
            </w:tc>'''

        header_row = '<w:tr>' + ''.join(make_cell(h, True) for h in headers) + '</w:tr>'
        data_rows = ''
        for ri, row in enumerate(rows):
            fill = 'F0F4FA' if ri % 2 == 1 else 'FFFFFF'
            cells = ''
            for ci, val in enumerate(row):
                if ci < len(headers):
                    shade = f'<w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>'
                    cells += f'''<w:tc>
                <w:tcPr><w:tcW w:w="2000" w:type="dxa"/>{shade}</w:tcPr>
                <w:p><w:r><w:rPr><w:rFonts w:ascii="微软雅黑" w:eastAsia="微软雅黑"/><w:sz w:val="18"/></w:rPr><w:t xml:space="preserve">{escape(val)}</w:t></w:r></w:p>
              </w:tc>'''
            data_rows += '<w:tr>' + cells + '</w:tr>'

        return f'''<w:tbl>
      <w:tblPr>
        <w:tblStyle w:val="Table Grid"/>
        <w:tblW w:w="5000" w:type="dxa"/>
        <w:tblBorders>
          <w:top w:val="single" w:sz="4" w:space="0" w:color="auto"/>
          <w:bottom w:val="single" w:sz="4" w:space="0" w:color="auto"/>
          <w:insideH w:val="single" w:sz="4" w:space="0" w:color="auto"/>
          <w:insideV w:val="single" w:sz="4" w:space="0" w:color="auto"/>
        </w:tblBorders>
        <w:tblLook w:val="04A0"/>
      </w:tblPr>
      <w:tblGrid>{grid_cols}</w:tblGrid>
      {header_row}
      {data_rows}
    </w:tbl>'''

    # 4. The tricky part: WORD中段落是XML结构，pipe table文本可能跨多个XML节点。
    #   用段落分组法：找到连续的pipe table段落，整体替换成一个<table> XML块

    # Strategy: extract all <w:p> blocks, group consecutive pipe-table paragraphs
    para_pattern = re.compile(r'(<w:p\b[^>]*>.*?</w:p>)', re.DOTALL)
    paras = para_pattern.findall(body_content)

    # For each para, extract text content (strip XML tags)
    def extract_text(p_xml):
        texts = re.findall(r'<w:t[^>]*>([^<]*)</w:t>', p_xml)
        return ''.join(texts).strip()

    i = 0
    new_parts = []
    while i < len(paras):
        para_text = extract_text(paras[i])

        # Check if this paragraph starts a pipe table
        if para_text.startswith('|') and para_text.count('|') >= 2:
            # Collect consecutive pipe-table paragraphs
            table_lines = []
            j = i
            while j < len(paras):
                t = extract_text(paras[j])
                if t.startswith('|') and t.count('|') >= 2:
                    table_lines.append(t)
                    j += 1
                else:
                    break

            if len(table_lines) >= 2:  # at least header + separator
                result = parse_pipe_table(table_lines)
                if result:
                    headers, rows, widths = result
                    if headers and rows:
                        new_parts.append(make_table_xml(headers, rows, widths))
                        i = j
                        continue

        new_parts.append(paras[i])
        i += 1

    # 5. Reassemble body
    new_body = ''.join(new_parts)
    new_doc_xml = doc_xml.replace(body_content, new_body)

    # 6. Write output .docx
    with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as zout:
        with zipfile.ZipFile(in_path, 'r') as zin:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == 'word/document.xml':
                    data = new_doc_xml.encode('utf-8')
                zout.writestr(item, data)
```

### Known Issues & Debugging Guide

#### Problem A: Namespace prefix injection (ns0:)
**Symptom**: Word shows raw XML tags like `<w:tc><w:p>...</w:p></w:tc>` as literal text. Inspecting the XML reveals `ns0:` prefix on some tags.

**Root cause**: When you use `lxml.etree.fromstring()` then `tostring()`, lxml may invent namespace prefixes for tags that reference namespaces not declared in the immediate fragment. `ns0:` appears when lxml sees a reference like `w:tr` but the `xmlns:w=` declaration is absent from the parsed fragment.

**Fix**: Don't use lxml for docx manipulation. Use pure string operations (re + xml.sax.saxutils.escape) to build and splice XML. The docx XML namespace (`xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"`) must be declared on the `<w:tbl>` element itself, not assumed from ancestors.

```python
# ❌ BAD - lxml can inject ns0:
table_elem = etree.fromstring(table_xml)
body_elem.append(table_elem)  # tostring() may add ns0:

# ✅ GOOD - pure string splice
new_body = body_content.replace(old_paras_block, table_xml_block)
```

#### Problem B: Escaped angle brackets in output
**Symptom**: `<w:tc>` appears as `&lt;w:tc&gt;` in the document.

**Root cause**: Using `xml.sax.saxutils.escape()` on text that is already XML (table structure) — escaping the XML tags themselves.

**Fix**: Apply escape() only to cell *content* strings (user data), NOT to the table XML skeleton:
```python
# ✅ GOOD
cell_text = escape(user_data_string)  # ONLY user data
table_xml = f'<w:tc><w:p><w:r><w:t>{cell_text}</w:t></w:r></w:p></w:tc>'  # XML is raw
```

#### Problem C: Table not recognized by Word
**Symptom**: The table XML is present in the document.xml but Word renders it as raw text.

**Fix**: Ensure the `<w:tbl>` element includes these critical prerequisites:
1. **`<w:tblPr>`** with `<w:tblStyle w:val="Table Grid"/>` 
2. **`<w:tblGrid>`** with `<w:gridCol>` elements matching column count
3. Each `<w:tc>` must have `<w:tcPr><w:tcW>` with valid width
4. Every `<w:p>` must be a child of `<w:tc>`, not directly under `<w:tr>`

#### Problem D: AI-generated table XML from vision models
**Symptom**: When asking a vision model to "read this table and reproduce it as Word XML", the model hallucinates column headers, omits rows, or invents data.

**Fix**: The cell content must come from **reliable string extraction** (regex on the docx XML), not from LLM perception of the rendered paragraph text. Parse the pseudo-table text programmatically, then build the XML around the verified cell data.

### Pitfalls

1. **lxml namespace poisoning**: Never use lxml to build or splice docx XML fragments. The parent document has `xmlns:w=...` declared on the root, but lxml fragments parsed without that declaration get assigned synthetic prefixes (`ns0:`, `ns1:`, etc.) that break Word rendering.

2. **Consecutive pipe-table detection**: The regex extracts ALL `<w:p>` blocks, then groups consecutive pipe-table paragraphs. This works because Markdown-style pipe tables are always contiguous in the original Markdown.

3. **Column count mismatch**: If a row has fewer cells than the header, pad with empty strings. If more cells, truncate.

4. **Header alignment from separator row**: The separator line (`|---:|:---|---:|`) may indicate column alignment in Markdown. For a basic replacement, alignment is optional — just use the headers string.

5. **Nested tables**: Not supported. Pipe tables cannot be nested in Markdown, so the code assumes flat tables only.

### When to use this technique

- User has `.docx` files that were converted from Markdown and still contain pipe-table artifacts
- python-docx is unavailable (PEP 668, no pip, minimal container, WSL without venv)
- The document has 1-10 tables that need replacement (for 50+ tables, consider a batched approach)
- You need to preserve the original document's formatting (fonts, margins, headers) outside the table regions

### Verification

```bash
# Check table XML is well-formed
python3 -c "
import zipfile
with zipfile.ZipFile('output.docx') as z:
    xml = z.read('word/document.xml').decode()
    print('Tables found:', xml.count('<w:tbl>'))
    print('Paragraphs:', xml.count('<w:p>'))
"

# Quick visual check - extract first 500 chars of document body
python3 -c "
import zipfile, re
with zipfile.ZipFile('output.docx') as z:
    xml = z.read('word/document.xml').decode()
body = re.search(r'<w:body>(.*?)</w:body>', xml, re.DOTALL)
print(body.group(1)[:1000])
" | head -30

# Check file opens correctly
ls -lh output.docx
file output.docx  # should say 'Microsoft Word 2007+'
```
