# Markdown to .docx Conversion Workflow

Parse a Markdown document line-by-line, detect structural elements (headings, tables, code blocks, lists, blockquotes), convert each to OOXML paragraph elements, then package into a .docx ZIP archive.

## When to Use

- User provides a large Markdown report (500-1000+ lines) and needs Word output
- python-docx is unavailable
- User requests both .md and .docx simultaneously
- Need Chinese government-style formatting (仿宋 body, 黑体 headings)

## Strategy Overview

Line-by-line parsing with state tracking (in_code_block, list counters). Each MD pattern maps to a specific Word formatting.

## Font Size Constants (half-points)

```python
SIZE_TITLE  = '32'   # 三号 16pt (center, bold)
SIZE_H1     = '28'   # 四号 14pt (黑体, bold)
SIZE_H2     = '24'   # 小四 12pt (黑体, bold)
SIZE_H3     = '21'   # 五号 10.5pt (楷体, bold)
SIZE_BODY   = '24'   # 小四 12pt (仿宋)
SIZE_SMALL  = '21'   # 五号 10.5pt (tables, code)
SIZE_TABLE  = '21'   # 五号 10.5pt
```

## Core Building Blocks

```python
import xml.sax.saxutils as saxutils
import zipfile

def esc(text):
    return saxutils.escape(str(text))

def simple_para(text, font_name='仿宋_GB2312', font_size='24', bold=False,
                alignment=None, spacing_before=0, spacing_after=0, line=480, firstLine=420):
    # Uses esc(), pPr_tag(), rPr_tag(), r_tag() from stdlib-ooxml.md pattern
    pass
```

## MD-to-Word Mapping

| MD Pattern | Word Output |
|-----------|-------------|
| `# Title` | center, 黑体 bold, SIZE_TITLE |
| `## Heading` | 黑体 bold, SIZE_H1 |
| `### Heading` | 楷体 bold, SIZE_H2 |
| `#### Heading` | 楷体 bold, SIZE_SMALL |
| `| col1 \| col2 \|` | inline text with `|` separator |
| `- item` / `* item` | `• item`, no firstLine indent |
| `1. item` | as-is, no firstLine indent |
| `` ``` `` block | toggle in_code_block, compact spacing |
| `> quote` | larger spacing |
| `---` | skip |
| Regular text | firstLine indent |

## Special Character Handling

```python
text = text.replace('**', '')  # remove MD bold markers
text = text.replace('✅', '✓').replace('⚠️', '▲')
text = text.replace('❌', '✗').replace('⛔', '✗')
text = text.replace('🏆', '').replace('📋', '')
```

## Verification

```python
with zipfile.ZipFile(output_path, 'r') as zf:
    doc = zf.read('word/document.xml').decode('utf-8')
para_count = doc.count('<w:p>')
import xml.etree.ElementTree as ET
try:
    ET.fromstring(doc)
    print("XML valid")
except ET.ParseError as e:
    print(f"XML error: {e}")
```

## Pitfalls

1. Table rows are inline pipe-separated text, not real Word `<w:tbl>`. Word users can convert if needed.
2. First Line indent on body text only — headings, list items, table rows, code blocks should NOT have firstLine indent.
3. Line spacing differs by content type: body 480 (24pt), code/tables 360 (compact).
4. Font size adjustments: if user says "all smaller by 2 sizes", recalculate: 三号(32)→四号(28)→小四(24)→五号(21)→小五(18).
