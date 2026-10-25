# -*- coding: utf-8 -*-
"""中国中小学校官方表格类Word文档生成模板：少代会提案登记表。
换主题时只改 add_field(...) 各栏内容即可，30秒出一版新文档。
python-docx 需已安装： pip install python-docx
"""
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.oxml.ns import qn

# 输出路径 —— Windows 桌面
OUT = "/mnt/c/Users/jiangmin/Desktop/上海交通大学附属第二中学第二十次代表大会提案登记表.docx"

doc = Document()

# ===== A4 页面 =====
sec = doc.sections[0]
sec.page_width = Cm(21.0)
sec.page_height = Cm(29.7)
sec.left_margin = Cm(2.0)
sec.right_margin = Cm(2.0)
sec.top_margin = Cm(1.8)
sec.bottom_margin = Cm(1.8)

# ===== Normal 样式设中文字体 =====
style = doc.styles["Normal"]
style.font.name = "宋体"
style.font.size = Pt(12)
style.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")


def para(text="", size=12, bold=False, align=WD_ALIGN_PARAGRAPH.LEFT):
    """普通段落，中文必须同时设 font.name 与 eastAsia。"""
    p = doc.add_paragraph()
    p.alignment = align
    r = p.add_run(text)
    r.font.name = "宋体"
    r.font.size = Pt(size)
    r.bold = bold
    r.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    return p


def set_cell(cell, text, size=12, bold=False):
    """填表格单元格，支持 \\n 多行（逐 run add_break）。勿用 cell.text=（丢格式）。"""
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pf = p.paragraph_format
    pf.space_before = Pt(2)
    pf.space_after = Pt(2)
    for i, ln in enumerate(text.split("\n")):
        if i > 0:
            p.add_run().add_break()
        r = p.add_run(ln)
        r.font.name = "宋体"
        r.font.size = Pt(size)
        r.bold = bold
        r.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")


# ===== 标题（16pt 加粗居中）=====
para("少先队上海交通大学附属第二中学", size=16, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
para("第二十次代表大会", size=16, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
para("代表提案登记表", size=16, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
para("")

# ===== 代表信息表（两次两列）=====
info = doc.add_table(rows=0, cols=2)
info.style = "Table Grid"
r = info.add_row()
set_cell(r.cells[0], "中队：____________")
set_cell(r.cells[1], "代表姓名：____________")
r = info.add_row()
set_cell(r.cells[0], "性别：______  年龄：______")
set_cell(r.cells[1], "民族：____________")


def add_field(label, content, content_size=12, label_size=12):
    """两列表格字段：左=字段名(加粗3.2cm)，右=内容(13.8cm)。"""
    t = doc.add_table(rows=0, cols=2)
    t.style = "Table Grid"
    row = t.add_row()
    row.cells[0].width = Cm(3.2)
    row.cells[1].width = Cm(13.8)
    set_cell(row.cells[0], label, size=label_size, bold=True)
    set_cell(row.cells[1], content, size=content_size)


para("")
# ===== 提案七部分（改这里换主题）=====
add_field("提案题目", "关于……的提案", content_size=12)
add_field("提案主题/类别", "1.队员自身成长发展（□①学习生活 □②身心健康 □③权益维护）", content_size=12)
add_field("提案关键词", "关键词A；关键词B；关键词C", content_size=12)
add_field("提出缘由", "（为什么，结合观察与必要性）", content_size=12)
add_field("主要内容", "（是什么，语言严谨精确，不用“据说”）", content_size=12)
add_field("意见建议", "1.……\n2.……\n3.……\n4.……", content_size=12)
add_field("提案附议\n（4人，填姓名及身份）",
          "1.＿＿＿（同中队队员）　　2.＿＿＿（同中队队员）\n"
          "3.＿＿＿（同中队队员）　　4.＿＿＿（队员家长）",
          content_size=12)
para("")
para("共计　＿＿人")
para("")
p = para("（请于规定日期，A4纸正反双面打印1份，格式不变，上交中队辅导员。）", size=11)
p.alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.save(OUT)
print("SAVED:", OUT)