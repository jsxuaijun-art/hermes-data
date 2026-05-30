---
name: markdown-to-word-converter
description: Convert large Markdown documents to Word .docx files using pure Python stdlib, with proper Chinese government-document formatting (fonts, sizes, headings, tables).
---

# Markdown to Word (.docx) Converter

## When to Use
- You have a large Markdown report/document (500-1000+ lines) and need Word output
- python-docx is unavailable (WSL/minimal environment)
- User requests both .md and .docx files simultaneously
- Need Chinese government-style formatting (仿宋 body, 黑体 headings, 楷体 sub-headings)
- User may ask to adjust font sizes (e.g., "all fonts 2 sizes smaller")

## Strategy Overview

Parse the Markdown line-by-line to detect structural elements (headings, tables, code blocks, lists, blockquotes), convert each to OOXML paragraph elements, then package into a .docx ZIP archive.

## Implementation Pattern

### 1. Font Size Constants (all in half-points)

```python
# Reference: w:sz uses half-points (pt * 2 = half-points value)
SIZE_TITLE  = '32'   # 三号 16pt (center, bold)
SIZE_H1     = '28'   # 四号 14pt (黑体, bold)
SIZE_H2     = '24'   # 小四 12pt (黑体, bold)
SIZE_H3     = '21'   # 五号 10.5pt (楷体, bold)
SIZE_BODY   = '24'   # 小四 12pt (仿宋)
SIZE_SMALL  = '21'   # 五号 10.5pt (for tables, code)
SIZE_TABLE  = '21'   # 五号 10.5pt
```

### 2. Core Building Blocks

```python
import xml.sax.saxutils as saxutils
import zipfile

def esc(text):
    return saxutils.escape(str(text))

def pPr_tag(alignment=None, spacing_before=0, spacing_after=0, line=480, firstLine=420):
    parts = ['<w:pPr>']
    if firstLine:
        parts.append(f'<w:ind w:firstLine=\"{firstLine}\"/>')
    if alignment:
        parts.append(f'<w:jc w:val=\"{alignment}\"/>')
    parts.append(f'<w:spacing w:before=\"{spacing_before}\" w:after=\"{spacing_after}\" w:line=\"{line}\" w:lineRule=\"auto\"/>')
    parts.append('</w:pPr>')
    return ''.join(parts)

def rPr_tag(font_name='仿宋_GB2312', font_size='24', bold=False):
    parts = ['<w:rPr>']
    parts.append(f'<w:rFonts w:ascii=\"{esc(font_name)}\" w:hAnsi=\"{esc(font_name)}\" w:eastAsia=\"{esc(font_name)}\"/>')
    parts.append(f'<w:sz w:val=\"{esc(font_size)}\"/><w:szCs w:val=\"{esc(font_size)}\"/>')
    if bold:
        parts.append('<w:b/><w:bCs/>')
    parts.append('</w:rPr>')
    return ''.join(parts)

def r_tag(text, font_name='仿宋_GB2312', font_size='24', bold=False):
    return f'<w:r>{rPr_tag(font_name, font_size, bold)}<w:t xml:space=\"preserve\">{esc(text)}</w:t></w:r>'

def simple_para(text, font_name='仿宋_GB2312', font_size='24', bold=False,
                alignment=None, spacing_before=0, spacing_after=0, line=480, firstLine=420):
    ppr = pPr_tag(alignment, spacing_before, spacing_after, line, firstLine=firstLine)
    run = r_tag(text, font_name, font_size, bold)
    return f'<w:p>{ppr}{run}</w:p>'
```

### 3. Markdown Parsing Logic (line-by-line)

Skip header/meta lines. For each remaining line:

| MD Pattern | Word Output |
|-----------|-------------|
| `# Title` | center, 黑体 bold, SIZE_TITLE |
| `## Heading` | 黑体 bold, SIZE_H1 |
| `### Heading` | 楷体 bold, SIZE_H2 |
| `#### Heading` | 楷体 bold, SIZE_SMALL |
| `\| col1 \| col2 \|` | inline text with `\|` separator, SIZE_TABLE |
| `- item` / `* item` | `• item`, no firstLine indent |
| `1. item` | as-is, no firstLine indent |
| `` ``` `` block | toggle in_code_block, SIZE_SMALL, line=360 |
| `> quote` | SIZE_BODY, larger spacing |
| `---` / separator | skip |
| Regular text | SIZE_BODY, firstLine indent |

### 4. Special Character Handling

```python
text = text.replace('**', '')  # remove MD bold markers
text = text.replace('✅', '✓').replace('⚠️', '▲')
text = text.replace('❌', '✗').replace('⛔', '✗')
text = text.replace('🏆', '').replace('📋', '')
text = text.replace('├─', '  ├─').replace('└─', '  └─')
```

### 5. ZIP Packaging (5 files)

Always include:
- `[Content_Types].xml`
- `_rels/.rels`
- `word/document.xml` (main body)
- `word/styles.xml` (style definitions)
- `word/_rels/document.xml.rels` (word-level relationships)

### 6. Styles XML Template

```xml
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:pPr><w:spacing w:line="480" w:lineRule="auto"/></w:pPr>
    <w:rPr>
      <w:rFonts w:ascii="仿宋_GB2312" w:hAnsi="仿宋_GB2312" w:eastAsia="仿宋_GB2312"/>
      <w:sz w:val="24"/><w:szCs w:val="24"/>
    </w:rPr>
  </w:style>
  <!-- Title, heading1, heading2, heading3 styles -->
</w:styles>
```

### 7. Verification

```python
with zipfile.ZipFile(output_path, 'r') as zf:
    doc = zf.read('word/document.xml').decode('utf-8')
para_count = doc.count('<w:p>')
# Check XML well-formedness
import xml.etree.ElementTree as ET
try:
    ET.fromstring(doc)
    print("XML valid")
except ET.ParseError as e:
    print(f"XML error: {e}")
```

## Pitfalls

1. **paras.count('<w:p>') won't work on list** — it's a list of strings containing `<w:p>`, not a single string. Use `doc.count('<w:p>')` on the final assembled XML instead.

2. **Table rows are not actual Word tables** — for simplicity, render table rows as inline pipe-separated text lines. Word users can convert to real tables if needed. Real `<w:tbl>` XML is complex and rarely justifies the effort for document-style tables.

3. **First Line indent on body text only** — headings, list items, table rows, and code blocks should NOT have firstLine indent. Pass `firstLine=0` for those.

4. **Line spacing differs by content type** — body text: 480 (24pt). Code blocks/tables: 360 for compactness.

5. **Empty lines in code blocks** — output a minimal paragraph to maintain vertical spacing within code sections.

6. **User wants both .md and .docx at once** — deliver both files in the same response, saved to the same desktop directory. This avoids a follow-up request.

7. **Font size adjustments** — if user says "all smaller by 2 sizes", recalculate all font size constants using the half-point table: 三号(32)→四号(28)→小四(24)→五号(21)→小五(18).
