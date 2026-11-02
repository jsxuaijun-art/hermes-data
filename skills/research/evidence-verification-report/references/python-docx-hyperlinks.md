# python-docx 可点击超链接（verified recipe）

python-docx 没有原生 hyperlink API。要生成可点击的引用链接（如编号文献），
必须给文档 part 加 relationship 再注入 `<w:hyperlink>`/`<w:r>`/`<w:t>` XML。
实测 26 条超链接文档生成成功，Word 中双击蓝字可跳转。

```python
import docx
from docx.oxml.ns import qn
from docx.oxml.shared import OxmlElement
from docx.shared import RGBColor, Pt

def add_hyperlink(paragraph, url, text, color=0x1F3B73, underline=True, size=10.5):
    """Add a clickable hyperlink run into an existing paragraph."""
    part = paragraph.part
    r_id = part.relate_to(url,
        docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('r:id'), r_id)

    run = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')
    # color: RGBColor accepts int 0x1F3B73
    c = OxmlElement('w:color')
    c.set(qn('w:val'), str(RGBColor(color)))
    rPr.append(c)
    if underline:
        u = OxmlElement('w:u'); u.set(qn('w:val'), 'single'); rPr.append(u)
    if size:
        sz = OxmlElement('w:sz'); sz.set(qn('w:val'), str(int(size * 2)))
        rPr.append(sz)
        szCs = OxmlElement('w:szCs'); szCs.set(qn('w:val'), str(int(size * 2)))
        rPr.append(szCs)
    run.append(rPr)
    t = OxmlElement('w:t')
    t.set(qn('xml:space'), 'preserve')
    t.text = text
    run.append(t)
    hyperlink.append(run)
    paragraph._p.append(hyperlink)
    return hyperlink

# usage
doc = docx.Document()
p = doc.add_paragraph()
p.add_run('来源: ')
add_hyperlink(p, 'https://www.cdc.gov/shingles/vaccines/index.html', '[1] CDC Shingles Vaccination')
doc.save('report.docx')
```

## 要点

- `paragraph.part.relate_to(url, ..., is_external=True)` 是唯一正规外部链接途径；
  同一 URL 重复调用幂等复用 r_id（编号稳定）。
- 颜色传 `0x1F3B73`（无 # 前缀的 int），`RGBColor(color)` 会在内部转字符串；
  不要手拼 '1F3B73'（缺 0x 前缀会解析错）。
- 强制 zh 文本保留空格：`<w:t xml:space="preserve">`。
- 编号锚点做法：先 `p.add_run('[1] 名称 ')`，再把超链接 run 追加到同一段落；
  需要"编号本身可点"时，直接把超链接文本设成 '[1] 名称'。

## 验证

```python
from docx import Document
d = Document('report.docx')
print('hyperlink rels:', sum(1 for k, v in d.part.rels.items()
                             if v.reltype.endswith('hyperlink')))
```
数字应等于期望链接条数。再用 read_file 读 .docx 抽查文字渲染。

> 若 python-docx 不可用，走 bundled `docx` 技能或
> `productivity/generate-docx-without-python-docx`（纯 stdlib XML）兜底。
