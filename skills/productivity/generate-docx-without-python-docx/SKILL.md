---
name: generate-docx-without-python-docx
description: Generate Word .docx files using pure Python stdlib (no external packages) when python-docx is unavailable. Uses string-based OOXML construction with xml.sax.saxutils for escaping.
---

# Generate .docx Without python-docx

## When to Use
- WSL/container/minimal environment where pip is unavailable or network is blocked
- python-docx cannot be installed (no pip, no ensurepip, apt timeout)
- Need to generate a .docx file with specific formatting (fonts, sizes, tables)
- Python 3 stdlib (xml.etree.ElementTree, xml.sax.saxutils, zipfile) is available

## The Approach

OOXML (.docx) is a ZIP archive containing XML files. We construct the XML as strings (not ElementTree) to avoid namespace prefix issues (`ns0:` vs `w:`), then wrap in a ZIP.

### Key Components

```python
import xml.sax.saxutils as saxutils
import zipfile

def esc(text):
    return saxutils.escape(str(text))
```

### Document Structure

The archive needs 5 files:

1. `[Content_Types].xml` — content type declarations
2. `_rels/.rels` — root relationships (points to word/document.xml)
3. `word/document.xml` — main document body
4. `word/styles.xml` — style definitions
5. `word/_rels/document.xml.rels` — word-level relationships (points to styles.xml)

### Namespace

Always use `w:` prefix with explicit namespace declaration:

```xml
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
```

### Building Paragraphs

```python
def rPr_tag(font_name='仿宋_GB2312', font_size='16', bold=False):
    parts = ['<w:rPr>']
    parts.append(f'<w:rFonts w:ascii="{esc(font_name)}" w:hAnsi="{esc(font_name)}" w:eastAsia="{esc(font_name)}"/>')
    parts.append(f'<w:sz w:val="{esc(font_size)}"/><w:szCs w:val="{esc(font_size)}"/>')
    if bold:
        parts.append('<w:b/>')
    parts.append('</w:rPr>')
    return ''.join(parts)

def r_tag(text, font_name='仿宋_GB2312', font_size='16', bold=False):
    return f'<w:r>{rPr_tag(font_name, font_size, bold)}<w:t xml:space="preserve">{esc(text)}</w:t></w:r>'

def simple_para(text, font_name='仿宋_GB2312', font_size='16', bold=False, alignment=None, spacing_before=40, spacing_after=40, line=560):
    ppr = pPr_tag(alignment, spacing_before, spacing_after, line)
    run = r_tag(text, font_name, font_size, bold)
    return f'<w:p>{ppr}{run}</w:p>'
```

### Font Size Convention (CORRECT — Verified Working)
- `w:sz` and `w:szCs` values are in **half-points**
- 1 point = 2 half-points → `font_size = pt * 2`
- 二号 (22pt) = `font_size='44'`
- 三号 (16pt) = `font_size='32'`
- 小二号 (18pt) = `font_size='36'`
- 四号 (14pt) = `font_size='28'`
- 小四 (12pt) = `font_size='24'`
- 五号 (10.5pt) = `font_size='21'`

**CRITICAL**: If you use `font_size='16'` for 三号 (16pt), the rendered font will be 8pt (half the intended size). Always double the point value.

### Line Spacing Convention
- `w:spacing w:line` value is in **twips** (1/20 of a point, or 1/1440 of an inch)
- 28磅 fixed line spacing = 28 × 20 = 560 twips
- **Formula**: `line_twips = desired_line_spacing_in_points * 20`

### Page Margins (twips)
- 37mm ≈ 2098 twips (top)
- 35mm ≈ 1984 twips (bottom)  
- 28mm ≈ 1587 twips (left)
- 26mm ≈ 1474 twips (right)
- Conversion: 1mm ≈ 56.69 twips (or use 56.7)

### Tables

```python
def table_xml(rows_data, header_row=False):
    parts = ['<w:tbl>']
    # Table properties with borders
    parts.append('<w:tblPr>...</w:tblPr>')
    for row_idx, row in enumerate(rows_data):
        parts.append('<w:tr>')
        for cell_text in row:
            is_header = header_row and row_idx == 0
            parts.append(f'''<w:tc>
        <w:tcPr><w:tcW w:w="{col_width}" w:type="dxa"/><w:vAlign w:val="center"/></w:tcPr>
        <w:p><w:pPr><w:spacing w:before="20" w:after="20" w:line="360" w:lineRule="auto"/></w:pPr>
        <w:r>{rPr_tag('仿宋_GB2312', '14', bold=is_header)}<w:t xml:space="preserve">{esc(cell_text)}</w:t></w:r></w:p>
      </w:tc>''')
        parts.append('</w:tr>')
    parts.append('</w:tbl>')
    return '\n'.join(parts)
```

### ZIP Packaging

```python
with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.writestr('[Content_Types].xml', content_types_xml.encode('utf-8'))
    zf.writestr('_rels/.rels', rels_xml.encode('utf-8'))
    zf.writestr('word/document.xml', full_document.encode('utf-8'))
    zf.writestr('word/styles.xml', styles_xml.encode('utf-8'))
    zf.writestr('word/_rels/document.xml.rels', doc_rels_xml.encode('utf-8'))
```

## Pitfalls (from experience)

1. **`ET.tostring()` and `standalone`**: Python 3.10's `ET.tostring()` does NOT accept `standalone=True` or `standalone=False` parameter. Omit it entirely.

2. **Namespace prefix issues**: Using `ET.Element(f'{{{NS}}}element')` produces `ns0:element` prefix in serialized XML. Word CAN read this, but `w:element` is more reliable. **Solution**: Build XML as strings, not ElementTree. String-based construction also avoids the `standalone` issue entirely.

3. **Chinese characters in f-string bytes check**: Python f-strings cannot contain `b'...'` with non-ASCII characters like Chinese. Instead of `f"... {b'市场采购' in data}..."`, use: `"市场采购" in data.decode('utf-8')` or assign to a variable first.

4. **Word requires proper content_types.xml**: Missing content type overrides cause Word to display "The file is corrupt" error. Always include `Override` entries for `/word/document.xml` and `/word/styles.xml`.

5. **Font fallback**: If Chinese fonts like 仿宋_GB2312 aren't installed on the target Windows machine, Word falls back to SimSun (宋体). This is acceptable but worth noting.

6. **`xml:space="preserve"`**: Always set this on `<w:t>` elements when the text has spaces or leading/trailing whitespace that should be preserved.

7. **pPr inside tables**: Table cell paragraphs also need `w:pPr` for spacing — don't skip it.

## Verification

After generating, verify with:
```python
with zipfile.ZipFile(path, 'r') as zf:
    doc = zf.read('word/document.xml').decode('utf-8')
# Check structural elements
paras = doc.count('<w:p>')
tbls = doc.count('<w:tbl>')
print(f"Paras: {paras}, Tables: {tbls}")

# Verify XML well-formedness
import xml.etree.ElementTree as ET
try:
    ET.fromstring(doc)
    print("XML valid")
except ET.ParseError as e:
    print(f"XML error: {e}")
```
