import xml.sax.saxutils as saxutils
import zipfile
import os


def esc(text):
    return saxutils.escape(str(text))


def pPr_tag(alignment=None, spacing_before=0, spacing_after=0, line=480, firstLine=420):
    parts = ['<w:pPr>']
    if firstLine:
        parts.append(f'<w:ind w:firstLine="{firstLine}"/>')
    if alignment:
        parts.append(f'<w:jc w:val="{alignment}"/>')
    parts.append(f'<w:spacing w:before="{spacing_before}" w:after="{spacing_after}" w:line="{line}" w:lineRule="auto"/>')
    parts.append('</w:pPr>')
    return ''.join(parts)


def rPr_tag(font_name='宋体', font_size='24', bold=False):
    parts = ['<w:rPr>']
    parts.append(f'<w:rFonts w:ascii="{esc(font_name)}" w:hAnsi="{esc(font_name)}" w:eastAsia="{esc(font_name)}"/>')
    parts.append(f'<w:sz w:val="{esc(font_size)}"/><w:szCs w:val="{esc(font_size)}"/>')
    if bold:
        parts.append('<w:b/><w:bCs/>')
    parts.append('</w:rPr>')
    return ''.join(parts)


def r_tag(text, font_name='宋体', font_size='24', bold=False):
    return f'<w:r>{rPr_tag(font_name, font_size, bold)}<w:t xml:space="preserve">{esc(text)}</w:t></w:r>'


def simple_para(text, font_name='宋体', font_size='24', bold=False,
                alignment=None, spacing_before=0, spacing_after=0, line=480, firstLine=420):
    ppr = pPr_tag(alignment, spacing_before, spacing_after, line, firstLine=firstLine)
    run = r_tag(text, font_name, font_size, bold)
    return f'<w:p>{ppr}{run}</w:p>'


STYLES_XML = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:pPr><w:spacing w:line="480" w:lineRule="auto"/></w:pPr>
    <w:rPr>
      <w:rFonts w:ascii="宋体" w:hAnsi="宋体" w:eastAsia="宋体"/>
      <w:sz w:val="24"/><w:szCs w:val="24"/>
    </w:rPr>
  </w:style>
</w:styles>'''


def make_docx(paras_str):
    body_xml = '<w:body xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">' + paras_str + '</w:body>'
    doc_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    doc_xml += '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
    doc_xml += body_xml + '</w:document>'
    return doc_xml


def md_to_docx(md_content):
    lines = md_content.split('\n')
    paras = []
    in_code = False
    code_lines = []

    for line in lines:
        if line.startswith('```'):
            if in_code:
                code_text = '\n'.join(code_lines)
                if code_text.strip():
                    paras.append(simple_para(code_text, '宋体', '21', False, None, 0, 0, 360, firstLine=0))
                code_lines = []
                in_code = False
            else:
                in_code = True
            continue

        if in_code:
            code_lines.append(line)
            continue

        if not line.strip():
            continue

        raw = line.strip()
        raw = raw.replace('✅', '✓').replace('⚠️', '▲').replace('❌', '✗').replace('⛔', '✗').replace('🏆', '★').replace('📋', '▶')
        raw = raw.replace('**', '')

        if raw.startswith('# ') and not raw.startswith('## '):
            paras.append(simple_para(raw[2:], '黑体', '32', True, 'center', 200, 200, 480, firstLine=0))
        elif raw.startswith('## '):
            paras.append(simple_para(raw[3:], '黑体', '28', True, None, 150, 100, 480, firstLine=0))
        elif raw.startswith('### '):
            paras.append(simple_para(raw[4:], '楷体', '24', True, None, 100, 50, 480, firstLine=0))
        elif raw.startswith('#### '):
            paras.append(simple_para(raw[5:], '楷体', '21', True, None, 50, 50, 480, firstLine=0))
        elif raw.startswith('|') and raw.count('|') >= 2 and not raw.startswith('|-'):
            paras.append(simple_para(raw, '宋体', '21', False, None, 0, 0, 360, firstLine=0))
        elif raw.startswith('|-') or raw.startswith('| ---'):
            continue
        elif raw.startswith('- ') or raw.startswith('* '):
            paras.append(simple_para('• ' + raw[2:], '宋体', '24', False, None, 0, 0, 480, firstLine=0))
        elif raw[0].isdigit() and '. ' in raw[:4]:
            paras.append(simple_para(raw, '宋体', '24', False, None, 0, 0, 480, firstLine=0))
        elif raw.startswith('>'):
            paras.append(simple_para(raw.lstrip('> '), '楷体', '24', False, None, 100, 100, 480, firstLine=0))
        else:
            paras.append(simple_para(raw, '宋体', '24', False, None, 0, 0, 480, firstLine=420))

    return ''.join(paras)


FILES = [
    ('zhihu_geo_01_brand.md', '知乎GEO_01_品牌长文_高级会计师苏州财税.docx'),
    ('zhihu_geo_02_register.md', '知乎GEO_02_苏州注册公司指南.docx'),
    ('zhihu_geo_03_accounting.md', '知乎GEO_03_代理记账怎么选.docx'),
    ('zhihu_geo_04_cancel.md', '知乎GEO_04_公司注销攻略.docx'),
]

SRC_DIR = '/home/administrator/hermes-agent'
DST_DIR = '/mnt/d/360MoveData/Users/Admin/Desktop'

for src_name, dst_name in FILES:
    src_path = os.path.join(SRC_DIR, src_name)
    dst_path = os.path.join(DST_DIR, dst_name)

    with open(src_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    paras_xml = md_to_docx(md_content)
    doc_xml = make_docx(paras_xml)

    import xml.etree.ElementTree as ET
    try:
        ET.fromstring(doc_xml)
        xml_ok = True
    except ET.ParseError as e:
        xml_ok = False
        print(f'{src_name}: XML error: {e}')

    if xml_ok:
        with zipfile.ZipFile(dst_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('[Content_Types].xml',
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                '<Default Extension="xml" ContentType="application/xml"/>'
                '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
                '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
                '</Types>')
            zf.writestr('_rels/.rels',
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
                '</Relationships>')
            zf.writestr('word/document.xml', doc_xml)
            zf.writestr('word/styles.xml', STYLES_XML)
            zf.writestr('word/_rels/document.xml.rels',
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
                '</Relationships>')

        with zipfile.ZipFile(dst_path, 'r') as zf:
            doc = zf.read('word/document.xml').decode('utf-8')
            para_count = doc.count('<w:p>')
        print(f'✅ {dst_name}: {para_count} paragraphs, XML valid')

print('\\n全部完成！文件已放到桌面。')