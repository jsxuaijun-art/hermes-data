---
name: word-documents
title: Word Documents
description: Create, format, and convert rich Word (.docx) documents using python-docx — tables, styling, Chinese fonts, shading, headers, and page layout.
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

## Alternative Approaches

Depending on your environment and dependencies, there are two alternative approaches to .docx generation:

### Fallback: Pure Stdlib OOXML (without python-docx)

When `python-docx` is unavailable (WSL, containers, blocked pip), construct .docx files using only Python stdlib (`xml.sax.saxutils`, `zipfile`). The key insight: .docx is a ZIP of XML files. Build the XML as strings (avoid ElementTree namespace issues) and wrap in a ZIP.

```python
import xml.sax.saxutils as saxutils, zipfile
def esc(text): return saxutils.escape(str(text))
```

**Key differences from python-docx:**
- Font sizes in half-points (`w:sz val="24"` = 12pt)
- Line spacing in twips (1/20 point)
- Chinese font names specified via `w:rFonts` with `w:eastAsia` attribute
- Table cells need manual `<w:tcPr>` with widths

See `references/stdlib-ooxml.md` for complete implementation patterns including:
- Document structure (5 required files in the ZIP)
- Paragraph/run builders with font, size, bold, alignment
- Simple table construction with borders and cell shading
- Chinese government-document formatting conventions (仿宋 body, 黑体 headings)
- Verified working font size table (半角pt×2)
- Confirmed working line spacing (28pt fixed = 560 twips)

### Workflow: Markdown to .docx Conversion

Parse a Markdown document, detect structure (headings, tables, code blocks, lists, blockquotes), and render each element as OOXML. Useful when users provide reports in Markdown but need .docx output.

**Strategy:**
- Line-by-line parsing with state tracking (in_code_block, list counters)
- Headings map to Chinese government heading styles (黑体/楷体 at appropriate sizes)
- Tables rendered as inline pipe-separated text (simpler than `<w:tbl>` XML)
- Code blocks rendered monospace with compact line spacing
- Emoji and special characters sanitized (✅ → ✓, etc.)

See `references/markdown-to-docx.md` for the complete converter pattern.

### Approach Comparison

| Feature | python-docx (primary) | Stdlib OOXML (fallback) | MD→docx (workflow) |
|---------|----------------------|------------------------|-------------------|
| Deps | python-docx | Python stdlib only | Python stdlib only |
| Formatting | Rich (shading, styles) | Manual XML | Manual XML |
| MD input | No | No | Yes (parses MD) |
| Chinese fonts | `rFonts.set(qn('w:eastAsia'), ...)` | `w:eastAsia` in XML | Same as stdlib |
| Tables | Real `<w:tbl>` | Real `<w:tbl>` | Pipe-separated inline |

Choose the approach based on your dependency availability and input format.

## Pitfalls

1. **Chinese font encoding**: Every `Run` that contains Chinese text MUST call `.element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')`. Without this, Word on non-Chinese systems may substitute a font that garbles Chinese text. This applies even if you set `run.font.name`.

2. **`.doc` vs `.docx`**: Legacy `.doc` files may actually be RAR archives in disguise (e.g., from shijuan1.com). Run `file filename.doc` to check — if it says "RAR archive data", extract with `unrar x filename.doc` to get the real `.docx`.

3. **Table fonts**: python-docx's `table.style` (e.g., 'Table Grid') may override run-level font settings. Always set font explicitly on each cell's run after setting cell text.

4. **Save path validation**: Before saving, verify the target directory exists. WSL's `/mnt/c/` mounts can have case-sensitive paths.

5. **Avoid `w:shd` color string parsing errors**: Use `parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color}"/>')` — `nsdecls("w")` is critical for the XML namespace.

6. **PermissionError when overwriting .docx open in Windows Word**: If the target .docx file is currently open in Word on Windows, `doc.save()` raises `PermissionError: [Errno 13] Permission denied`. The file is locked by the Windows file-sharing system. Solutions: (a) save to a **new filename** (e.g., `-完整版.docx` suffix) to avoid the collision, or (b) ask the user to close the file in Word first. Check if this is the issue before debugging other causes — the file permissions (`rwxrwxrwx`) will look fine in `ls -la`.

## Terminal Grid Table Formatting

See `references/terminal-tables.md` for the `mt()` (make_table) function that generates Unicode grid tables for CLI output. This was absorbed from the standalone `table-formatter` skill.

When displaying structured data in terminal output (not Word documents), use:
```python
# Paste the mt(), dw(), pc() functions from references/terminal-tables.md
print(mt(headers, data_rows))
```

The function handles:
- Full fine-line grid style with Unicode box-drawing characters
- Correct CJK character double-width alignment
- 2-6 column tables for best terminal display

## Verification

```bash
# Check file type and size
file /mnt/c/Users/jiangmin/Desktop/输出文件.docx
ls -lh /mnt/c/Users/jiangmin/Desktop/输出文件.docx
```
