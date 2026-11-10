#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把财税判卷的 markdown 转成中文排版的 Word(.docx)。
用法: python3 md2docx_cn.py <输入.md> <输出.docx>
适用: 简答/综合/速查表等分节内容。自动处理 #标题、═══分隔线、-列表，中文字体微软雅黑。
"""
import re
import sys
from docx import Document
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


def set_font(run, size=11, bold=False, color=None, name="微软雅黑"):
    run.font.name = name
    run._element.rPr.rFonts.set(qn('w:eastAsia'), name)
    run.font.size = Pt(size)
    run.font.bold = bold
    if color:
        run.font.color.rgb = RGBColor(*color)


def md2docx(src, out):
    doc = Document()
    normal = doc.styles['Normal']
    normal.font.name = "微软雅黑"
    normal.font.size = Pt(11)
    normal.element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')

    NAVY = (0x1F, 0x3B, 0x73)

    def add_heading(text, level):
        sizes = {1: 16, 2: 14, 3: 12.5, 4: 11.5}
        p = doc.add_paragraph()
        r = p.add_run(text)
        set_font(r, size=sizes.get(level, 12), bold=True, color=NAVY)
        p.paragraph_format.space_before = Pt(12 if level <= 2 else 6)
        p.paragraph_format.space_after = Pt(4)

    def add_body(text, bold=False):
        p = doc.add_paragraph()
        r = p.add_run(text)
        set_font(r, size=11, bold=bold)
        p.paragraph_format.space_after = Pt(3)

    def add_sep():
        p = doc.add_paragraph()
        pBdr = OxmlElement('w:pBdr')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single'); bottom.set(qn('w:sz'), '4')
        bottom.set(qn('w:space'), '1'); bottom.set(qn('w:color'), '1F3B73')
        pBdr.append(bottom)
        p._p.get_or_add_pPr().append(pBdr)
        p.paragraph_format.space_after = Pt(4)

    def add_bullet(text):
        p = doc.add_paragraph(style='List Bullet')
        r = p.add_run(text)
        set_font(r, size=11)
        p.paragraph_format.space_after = Pt(2)

    with open(src, encoding='utf-8') as f:
        lines = f.read().splitlines()

    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            continue
        if set(line.strip()) <= set('═══'):
            add_sep()
            continue
        m = re.match(r'^(#{1,6})\s*(.*)$', line)
        if m:
            add_heading(m.group(2).strip(), len(m.group(1)))
            continue
        if re.match(r'^\s*[-*]\s+', line):
            add_bullet(re.sub(r'^\s*[-*]\s+', '', line))
            continue
        add_body(line)

    doc.save(out)
    print("saved:", out)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit("用法: md2docx_cn.py <输入.md> <输出.docx>")
    md2docx(sys.argv[1], sys.argv[2])
