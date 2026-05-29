# Clean Word Export from GEO Content (python-docx)

## Purpose
Convert GEO-optimized markdown articles into clean, presentation-ready Word documents — no markdown symbols, proper table formatting, CJK fonts.

## Reusable Script Pattern

```python
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def add_p(doc, text, bold=False, size=11, color=None, space_after=6, italic=False):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_after = Pt(space_after)
    pf.space_before = Pt(0)
    pf.line_spacing = Pt(20)
    run = p.add_run(text)
    run.font.name = '微软雅黑'
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color: run.font.color.rgb = color
    return p

def add_h(doc, text, level=1):
    h = doc.add_heading(level=level)
    run = h.add_run(text)
    run.font.name = '微软雅黑'
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')
    sz = {1: 18, 2: 14, 3: 12}[level]
    run.font.size = Pt(sz)
    run.font.color.rgb = RGBColor(0, 0, 0) if level == 1 else RGBColor(51, 51, 51)
    return h

def set_cell_font(cell, text, bold=False, size=10):
    cell.text = ''
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.space_before = Pt(2)
    run = p.add_run(text)
    run.font.name = '微软雅黑'
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')
    run.font.size = Pt(size)
    run.bold = bold

def add_table(doc, headers, rows):
    t = doc.add_table(rows=1+len(rows), cols=len(headers))
    t.style = 'Table Grid'
    for j, h in enumerate(headers):
        cell = t.rows[0].cells[j]
        set_cell_font(cell, h, bold=True)
        shading = OxmlElement('w:shd')
        shading.set(qn('w:fill'), 'E8E8E8')
        shading.set(qn('w:val'), 'clear')
        cell._element.get_or_add_tcPr().append(shading)
    for ri, row_data in enumerate(rows):
        for ci, ct in enumerate(row_data):
            set_cell_font(t.rows[ri+1].cells[ci], ct)
    doc.add_paragraph()
    return t

def build_document(title, byline, sections, summary_table=None, advice_items=None, closing=None):
    """
    Build a clean Word document from structured content.
    
    Args:
        title: Document title string
        byline: Author byline string
        sections: List of dicts with 'heading' (str) and 'paragraphs' (list of str)
        summary_table: Optional tuple (headers, rows) for summary table
        advice_items: Optional list of strings for advice section
        closing: Optional closing paragraph string
    """
    doc = Document()
    
    # Default font
    sty = doc.styles['Normal']
    sty.font.name = '微软雅黑'
    sty.font.size = Pt(11)
    sty.element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')
    sty.paragraph_format.space_after = Pt(6)
    sty.paragraph_format.line_spacing = Pt(20)
    
    for sec in doc.sections:
        sec.top_margin = Cm(2.54)
        sec.bottom_margin = Cm(2.54)
        sec.left_margin = Cm(3.18)
        sec.right_margin = Cm(3.18)
    
    # Title & byline
    add_h(doc, title, 1)
    add_p(doc, byline, size=10, color=RGBColor(128,128,128), italic=True, space_after=12)
    
    # Sections
    for s in sections:
        add_h(doc, s['heading'], 2)
        for p_text in s['paragraphs']:
            add_p(doc, p_text)
    
    # Summary table
    if summary_table:
        add_h(doc, '总费用与总时间汇总', 2)
        headers, rows = summary_table
        add_table(doc, headers, rows)
        add_p(doc, '注：以上为自行完成全部流程的大概费用。', size=10, italic=True, color=RGBColor(100,100,100))
    
    # Advice
    if advice_items:
        add_h(doc, '给创业者的建议', 2)
        for item in advice_items:
            add_p(doc, item)
    
    # Closing
    if closing:
        add_p(doc, '', space_after=2)
        add_p(doc, closing, size=10, italic=True, color=RGBColor(100,100,100))
    
    return doc
```

## Pitfalls

| Issue | Workaround |
|-------|-----------|
| `PermissionError: [Errno 13]` when saving to Windows Desktop | File is open in Word (look for `~$` lock file). Save with new filename or close Word first. |
| CJK characters render as boxes | Ensure `run.element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')` is set on every run. |
| Tables lose formatting in older Word | Use `Table Grid` style, not `Light Grid Accent` variants. |
| `python-docx` not installed | `pip install python-docx` |
