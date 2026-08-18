# Generate .xlsx Without openpyxl

## When to Use
- WSL/minimal environment where pip is blocked by PEP 668 (`--break-system-packages`)
- Network timeout prevents downloading openpyxl/xlsxwriter
- Need a simple structured .xlsx with headers, data rows, column widths, and basic cell styling
- Python 3 stdlib (xml.sax.saxutils, zipfile) is available

## OOXML .xlsx Structure

A .xlsx file is a ZIP archive containing:

```
[Content_Types].xml
_rels/.rels
xl/
├── workbook.xml
├── _rels/workbook.xml.rels
├── styles.xml
├── sharedStrings.xml
└── worksheets/
    └── sheet1.xml
```

## Key Components

### 1. Shared Strings Table

All cell text values go into a shared strings table, referenced by index. This is required by the OOXML spec.

```python
all_strings = []
ss_map = {}

def get_ss(text):
    t = str(text)
    if t not in ss_map:
        ss_map[t] = len(all_strings)
        all_strings.append(t)
    return ss_map[t]
```

Each shared string entry:

```xml
<si><t xml:space="preserve">苏州代理记账</t></si>
```

### 2. Sheet Data

Cells can be:
- `<c r="A1" t="s"><v>0</v></c>` — shared string (index 0)
- `<c r="B2" t="inlineStr"><is><t>text</t></is></c>` — inline string (avoids shared string table)
- `<c r="C3"><v>123</v></c>` — number
- `<c r="D4" s="1"><v>0</v></c>` — shared string with custom style index

### 3. Styles

Example with header row styling (blue background, white bold text):

```xml
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="2">
    <font><sz val="11"/><name val="微软雅黑"/></font>
    <font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="微软雅黑"/></font>
  </fonts>
  <fills count="3">
    <fill><patternFill patternType="none"/></fill>
    <fill><patternFill patternType="gray125"/></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FF1A3C6E"/></patternFill></fill>
  </fills>
  <borders count="1">
    <border><left/><right/><top/><bottom/><diagonal/></border>
  </borders>
  <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
  <cellXfs count="2">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0"/>
    <xf numFmtId="0" fontId="1" fillId="2" borderId="0" applyFont="1" applyFill="1"/>
  </cellXfs>
</styleSheet>
```

Style index 0 = default, index 1 = header.

### 4. Column Widths

```xml
<cols>
  <col min="1" max="1" width="8" customWidth="1"/>
  <col min="2" max="2" width="22" customWidth="1"/>
</cols>
```

### 5. Workbook with Sheet Name

```xml
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
          xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>
    <sheet name="GEO执行进度" sheetId="1" r:id="rId1"/>
  </sheets>
</workbook>
```

## Complete Working Script Pattern

```python
import zipfile
import xml.sax.saxutils as saxutils
import os

def esc(text):
    return saxutils.escape(str(text))

def make_xlsx(output_path, sheet_name, headers, rows):
    """Generate a .xlsx with header styling and column widths."""

    all_strings = []
    ss_map = {}

    def get_ss(text):
        t = str(text)
        if t not in ss_map:
            ss_map[t] = len(all_strings)
            all_strings.append(t)
        return ss_map[t]

    # Column widths (customize per use case)
    widths = [8, 22, 8, 10, 10, 14, 14, 30]

    cols_xml = "<cols>"
    for i, w in enumerate(widths, 1):
        cols_xml += f'<col min="{i}" max="{i}" width="{w}" customWidth="1"/>'
    cols_xml += "</cols>"

    # Sheet data
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"  # supports up to 26 cols

    sheet_body = "<sheetData>"
    # Header row (style 1 = blue bg + white bold)
    sheet_body += '<row r="1">'
    for ci, h in enumerate(headers):
        sheet_body += f'<c r="{letters[ci]}1" t="s" s="1"><v>{get_ss(h)}</v></c>'
    sheet_body += "</row>"
    # Data rows
    for ri, row in enumerate(rows, 2):
        sheet_body += f'<row r="{ri}">'
        for ci, val in enumerate(row):
            sheet_body += f'<c r="{letters[ci]}{ri}" t="s"><v>{get_ss(val)}</v></c>'
        sheet_body += "</row>"
    sheet_body += "</sheetData>"

    sheet_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        + cols_xml + sheet_body + "</worksheet>"
    )

    # Shared strings table
    ss_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'
        f' count="{len(all_strings)}" uniqueCount="{len(all_strings)}">'
    )
    for s in all_strings:
        ss_xml += f"<si><t xml:space=\"preserve\">{esc(s)}</t></si>"
    ss_xml += "</sst>"

    # Styles (same as template above)
    styles_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<fonts count="2">'
        '<font><sz val="11"/><name val="微软雅黑"/></font>'
        '<font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="微软雅黑"/></font>'
        '</fonts>'
        '<fills count="3">'
        '<fill><patternFill patternType="none"/></fill>'
        '<fill><patternFill patternType="gray125"/></fill>'
        '<fill><patternFill patternType="solid"><fgColor rgb="FF1A3C6E"/></patternFill></fill>'
        '</fills>'
        '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
        '<cellXfs count="2">'
        '<xf numFmtId="0" fontId="0" fillId="0" borderId="0"/>'
        '<xf numFmtId="0" fontId="1" fillId="2" borderId="0" applyFont="1" applyFill="1"/>'
        '</cellXfs>'
        '</styleSheet>'
    )

    # Write ZIP
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
            '<Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/>'
            '</Types>'
        ).encode("utf-8"))
        zf.writestr("_rels/.rels", (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
            '</Relationships>'
        ).encode("utf-8"))
        zf.writestr("xl/workbook.xml", (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'
            ' xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            f'<sheets><sheet name="{esc(sheet_name)}" sheetId="1" r:id="rId1"/></sheets>'
            '</workbook>'
        ).encode("utf-8"))
        zf.writestr("xl/_rels/workbook.xml.rels", (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
            '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
            '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings" Target="sharedStrings.xml"/>'
            '</Relationships>'
        ).encode("utf-8"))
        zf.writestr("xl/worksheets/sheet1.xml", sheet_xml.encode("utf-8"))
        zf.writestr("xl/styles.xml", styles_xml.encode("utf-8"))
        zf.writestr("xl/sharedStrings.xml", ss_xml.encode("utf-8"))

    print(f"OK .xlsx saved: {output_path}")
```

## Usage Example

```python
xlsx_path = "/mnt/d/360MoveData/Users/Admin/Desktop/进度表.xlsx"
make_xlsx(
    xlsx_path,
    sheet_name="GEO执行进度",
    headers=["序号", "方向", "优先级", "状态", "执行人", "计划完成日期", "实际完成日期", "备注"],
    rows=[
        ["1", "AI可见度诊断", "P0", "待开始", "", "", "", ""],
        ["2", "信源补全",     "P0", "待开始", "", "", "", ""],
    ]
)
```

## Pitfalls

1. **Column letter limit**: The simple `letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"` pattern only supports up to 26 columns. For more, generate letters via:
   ```python
   def col_letter(n):
       s = ""
       while n > 0:
           n, r = divmod(n - 1, 26)
           s = chr(65 + r) + s
       return s
   ```

2. **Color format**: OOXML colors use ARGB hex (8 chars). Blue = `FF1A3C6E` (FF = fully opaque). Missing the `FF` prefix causes the color to render as black in some viewers.

3. **Cell type `t="s"`** requires the value to be an index into the shared strings table. Using `t="s"` with an integer > actual string count will cause Excel to report a corrupted file.

4. **Default font**: Always set `<name val="微软雅黑"/>` or another Chinese font. Without this, Excel may fall back to a font that garbles Chinese text.

5. **Merge cells not supported**: This pure-stdlib approach does not handle merged cells. For merged cells, use openpyxl.

6. **No formulas**: This approach only writes static text values. Formula support requires more OOXML parsing. For formulas, use openpyxl or xlsxwriter.

7. **Sheet data encoding**: All string content must go through `saxutils.escape()` to handle XML special characters (`&`, `<`, `>`, `"`).

8. **Content types:** Every XML file path must have an `<Override>` in `[Content_Types].xml`. Missing an override causes "Excel cannot open the file because the file format or file extension is not valid."
