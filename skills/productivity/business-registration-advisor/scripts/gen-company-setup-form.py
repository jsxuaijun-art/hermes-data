#!/usr/bin/env python3
"""
生成「有限公司设立必备信息采集表」Word文档

参考来源: D:/OneDrive/Desktop/工作/工商事务/必备信息（有限公司设立）.docx
输出到桌面，文件名: 有限公司设立必备信息采集表_YYYYMMDD.docx

用法:
    python3 gen-company-setup-form.py
    python3 gen-company-setup-form.py -o /custom/path/output.docx
"""

import os
import sys
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

# --- XML building blocks (pure stdlib, no python-docx) ---

NAMESPACES = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'pic': 'http://schemas.openxmlformats.org/drawingml/2006/picture',
    'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
    'wps': 'http://schemas.microsoft.com/office/word/2010/wordprocessingShape',
}

def _w(tag):
    return f'{{http://schemas.openxmlformats.org/wordprocessingml/2006/main}}{tag}'

def _r(tag):
    return f'{{http://schemas.openxmlformats.org/officeDocument/2006/relationships}}{tag}'

def make_element(tag, attrib=None, text=None):
    e = ET.Element(_w(tag), attrib or {})
    if text is not None:
        e.text = text
    return e

def make_paragraph(style=None, alignment=None):
    p = ET.Element(_w('p'))
    pPr = ET.SubElement(p, _w('pPr'))
    if style:
        ET.SubElement(pPr, _w('pStyle'), {_w('val'): style})
    if alignment:
        # alignment: left=left, center=center, right=right
        ET.SubElement(pPr, _w('jc'), {_w('val'): alignment})
    return p

def add_run_to_para(p, text, bold=False, font_size='21', font_name='微软雅黑', color=None):
    r = ET.SubElement(p, _w('r'))
    rPr = ET.SubElement(r, _w('rPr'))
    if bold:
        ET.SubElement(rPr, _w('b'))
    ET.SubElement(rPr, _w('sz'), {_w('val'): font_size})
    ET.SubElement(rPr, _w('rFonts'), {_w('eastAsia'): font_name, _w('ascii'): font_name})
    if color:
        ET.SubElement(rPr, _w('color'), {_w('val'): color})
    ET.SubElement(r, _w('t')).text = text
    return r

def make_table(headers, rows, col_widths=None):
    """Create a Word table from headers and rows."""
    tbl = ET.Element(_w('tbl'))

    # Table properties
    tblPr = ET.SubElement(tbl, _w('tblPr'))
    ET.SubElement(tblPr, _w('tblStyle'), {_w('val'): 'TableGrid'})
    ET.SubElement(tblPr, _w('tblW'), {_w('w'): '9000', _w('type'): 'dxa'})

    # Borders
    tblBorders = ET.SubElement(tblPr, _w('tblBorders'))
    for border_name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        ET.SubElement(tblBorders, _w(border_name), {
            _w('val'): 'single',
            _w('sz'): '4',
            _w('space'): '0',
            _w('color'): '000000',
        })

    # Grid columns
    num_cols = len(headers)
    tblGrid = ET.SubElement(tbl, _w('tblGrid'))
    for i in range(num_cols):
        w = col_widths[i] if col_widths and i < len(col_widths) else '2000'
        ET.SubElement(tblGrid, _w('gridCol'), {_w('w'): w})

    # Header row
    tr = ET.SubElement(tbl, _w('tr'))
    for h in headers:
        tc = ET.SubElement(tr, _w('tc'))
        tcPr = ET.SubElement(tc, _w('tcPr'))
        ET.SubElement(tcPr, _w('shd'), {_w('val'): 'clear', _w('color'): 'auto', _w('fill'): 'D9E2F3'})
        p = ET.SubElement(tc, _w('p'))
        add_run_to_para(p, h, bold=True, font_size='20', font_name='微软雅黑')

    # Data rows
    for row in rows:
        tr = ET.SubElement(tbl, _w('tr'))
        for i, cell_text in enumerate(row):
            tc = ET.SubElement(tr, _w('tc'))
            # merge cells if text is a placeholder for merged
            p = ET.SubElement(tc, _w('p'))
            add_run_to_para(p, str(cell_text), font_size='20', font_name='微软雅黑')

    return tbl

def create_docx(title, content_func, output_path):
    """Create a .docx file with given content."""
    # Document XML
    document_xml = ET.Element('w:document', {
        'xmlns:w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
        'xmlns:r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    })
    body = ET.SubElement(document_xml, _w('body'))

    # Title paragraph
    p_title = make_paragraph(alignment='center')
    add_run_to_para(p_title, title, bold=True, font_size='28')
    body.append(p_title)

    # Blank line
    body.append(make_paragraph())

    # Instruction text
    p_inst = make_paragraph()
    add_run_to_para(p_inst, '以下信息也可不填写在表中，逐项文字发过来，我们自行整理。', font_size='20', color='FF0000')
    body.append(p_inst)

    body.append(make_paragraph())

    # Call the content function to add more elements to body
    content_func(body)

    # Section properties (page size A4)
    sectPr = ET.SubElement(body, _w('sectPr'))
    pgSz = ET.SubElement(sectPr, _w('pgSz'), {_w('w'): '11906', _w('h'): '16838'})  # A4
    ET.SubElement(sectPr, _w('pgMar'), {
        _w('top'): '1440', _w('right'): '1440', _w('bottom'): '1440', _w('left'): '1440',
        _w('header'): '708', _w('footer'): '708',
    })

    # Build relations: styles
    styles_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="table" w:styleId="TableGrid">
    <w:name w:val="Table Grid"/>
    <w:pPr>
      <w:spacing w:after="0" w:line="240" w:lineRule="auto"/>
    </w:pPr>
    <w:tblPr>
      <w:tblBorders>
        <w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/>
        <w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>
        <w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>
        <w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>
        <w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/>
        <w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/>
      </w:tblBorders>
    </w:tblPr>
  </w:style>
</w:styles>'''

    rels_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>
</Relationships>'''

    theme_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Default Theme">
  <a:themeElements>
    <a:clrScheme name="Default">
      <a:dk1><a:srgbClr val="000000"/></a:dk1>
      <a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>
      <a:dk2><a:srgbClr val="44546A"/></a:dk2>
      <a:lt2><a:srgbClr val="E7E6E6"/></a:lt2>
      <a:accent1><a:srgbClr val="4472C4"/></a:accent1>
      <a:accent2><a:srgbClr val="ED7D31"/></a:accent2>
      <a:accent3><a:srgbClr val="A5A5A5"/></a:accent3>
      <a:accent4><a:srgbClr val="FFC000"/></a:accent4>
      <a:accent5><a:srgbClr val="5B9BD5"/></a:accent5>
      <a:accent6><a:srgbClr val="70AD47"/></a:accent6>
      <a:hlink><a:srgbClr val="0563C1"/></a:hlink>
      <a:folHlink><a:srgbClr val="954F72"/></a:folHlink>
    </a:clrScheme>
  </a:themeElements>
</a:theme>'''

    # Build package
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/word/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
</Types>''')
        z.writestr('_rels/.rels', '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>''')
        z.writestr('word/document.xml', ET.tostring(document_xml, encoding='unicode'))
        z.writestr('word/_rels/document.xml.rels', rels_xml)
        z.writestr('word/styles.xml', styles_xml)
        z.writestr('word/theme/theme1.xml', theme_xml)

    return output_path


def build_content(body):
    """Build the main content table and supplementary info."""
    col_widths = ['1000', '2200', '2200', '3600']

    headers = ['项目', '说明', '举例', '您的信息请填在本列']

    rows = [
        ['1\n公司名称', '江苏+名号+行业+有限公司', '苏州盈信电子科技有限公司', ''],
        ['2\n备选名号', '易重名，多想名号', '盈峰、腾盈、悦莱……', ''],
        ['3\n股东出资', '姓名（名称）+出资额XX万', '张X峰：出资50万；\n李X华：出资60万', ''],
        ['4\n任职情况', '不能在税务、市监的黑名单中。\n执行董事/董事（法定代表人）：\n监事：\n财务负责人：', '执行董事（法定代表人）：张X峰 138XXXX689\n监事：李华 138XXXX689', ''],
        ['5\n财务负责人', '由我们提供税务申报服务的可不提供。', '张X云 138XXXX689', ''],
        ['6\n经营范围', '只能搜索后选择，不能填写。\n使用微信小程序"经营范围规范表述查询系统"搜索。也可将表述发给我们。', '', ''],
        ['7\n住所材料', '产权证、租房合同照片。\n租房合同：甲方为全体产权人，乙方为全体股东。\n并附：产权人身份证号码（截图也行）、手机号', '', ''],
        ['8\n增值税纳税人\n分类', '1.小规模纳税人    2.一般纳税人\n\n(注：小规模纳税人不能收专票、税率为1%/3%/5%)\n(注：一般纳税人可以收专票抵扣、税率为6%/9%/13%)', '', ''],
        ['9\n电子邮箱', '用于接收税务事项通知', 'jsxuaijun@163.com', ''],
        ['10\n收件地址', '营业执照及发票邮寄地址', '', ''],
        ['11\n其他提示', '● 需下载APP并在支付宝中做人脸认证\n● 股东若为公司请准备营业执照副本\n● 以上信息也可逐项文字发过来，由我们整理', '', ''],
        ['12\n证件拍照', '第7项住所材料 + 第3、4、5项所有人员身份证需拍照发来，拍照要求见下页。', '', ''],
    ]

    # Main info table
    tbl = make_table(headers, rows, col_widths)
    body.append(tbl)

    body.append(make_paragraph())
    body.append(make_paragraph())

    # Photo requirements section
    p_photo_title = make_paragraph()
    add_run_to_para(p_photo_title, '━━━ 拍照要求 ━━━', bold=True, font_size='24', color='4472C4')
    body.append(p_photo_title)

    body.append(make_paragraph())

    photo_instructions = [
        ('一、拍照通用要求', [
            '角度垂直、光线良好、不要反光、镜头靠近、拍出全图',
            '请发送原图（不要压缩）',
        ]),
        ('二、股东证件', [
            '自然人：身份证正反面（表格第3、4、5项提及的所有人员）',
            '股东若为公司：营业执照副本拍照',
        ]),
        ('三、签字字迹', [
            '股东直接在白纸上用黑色签字笔签字，然后拍照（要求同上）',
        ]),
        ('四、住所材料', [
            '1. 租房合同：拍出四个角，页数齐全',
            '2. 产权证：拍出四角，左上角产权证号+登记部门章',
        ]),
    ]

    for section_title, items in photo_instructions:
        p_sec = make_paragraph()
        add_run_to_para(p_sec, section_title, bold=True, font_size='21')
        body.append(p_sec)
        for item in items:
            p_item = make_paragraph()
            add_run_to_para(p_item, f'    • {item}', font_size='20')
            body.append(p_item)
        body.append(make_paragraph())

    # Supplementary notes
    body.append(make_paragraph())
    p_note_title = make_paragraph()
    add_run_to_para(p_note_title, '━━━ 补充说明 ━━━', bold=True, font_size='24', color='4472C4')
    body.append(p_note_title)

    notes = [
        '1. 公司类型默认为有限责任公司（自然人控股），如需设其他类型请注明。',
        '2. 注册资本：新公司法（2024年7月1日施行）要求全体股东认缴出资自公司成立起5年内缴足。',
        '3. 存量公司（2024年7月1日前设立）有3年过渡期（至2027年6月30日）调整出资期限。',
        '4. 法定代表人可由执行董事或经理担任，建议由大股东担任。',
        '5. 监事不能由法定代表人、董事、经理兼任。',
        '6. 如注册地址为苏州工业园区，请确认是否在"一网通办"准入清单内。',
        '7. 如有前置审批行业（如教育培训、医疗、危化品等），需先取得许可证再注册公司。',
        '8. 经营范围规范表述查询：微信搜索小程序"经营范围规范表述查询系统"或访问 jyfwyun.com。',
    ]
    for note in notes:
        p_n = make_paragraph()
        add_run_to_para(p_n, note, font_size='20')
        body.append(p_n)


def main():
    # Determine output path
    now = datetime.now().strftime('%Y%m%d')
    default_name = f'有限公司设立必备信息采集表_{now}.docx'

    # Try WSL Windows desktop paths
    desktop_candidates = [
        Path('/mnt/c/Users/Administrator/Desktop'),
        Path('/mnt/c/Users/Admin/Desktop'),
        Path.home() / 'Desktop',
        Path.home(),
    ]

    output_dir = None
    for d in desktop_candidates:
        if d.exists():
            output_dir = d
            break

    if output_dir is None:
        # Fallback: use current directory
        output_dir = Path.cwd()

    output_path = output_dir / default_name

    # Allow overide via -o
    if len(sys.argv) > 2 and sys.argv[1] == '-o':
        output_path = Path(sys.argv[2])

    create_docx('有限公司设立必备信息采集表', build_content, str(output_path))
    print(f'✅ 采集表已生成: {output_path}')


if __name__ == '__main__':
    main()
