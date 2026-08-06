#!/usr/bin/env python3
"""
防火墙控股架构方案 → Word .docx 生成器

用途：将结构化方案数据输出为桌面可交付的 .docx 文档
依赖：纯 Python stdlib（zipfile + xml.etree.ElementTree），无需 python-docx

用法：
    python3 generate_firewall_docx.py > output.docx  (win: chcp 65001 先)
 或
    python3 generate_firewall_docx.py -o "路径/文件名.docx"

本脚本配合 holding-company-firewall 技能使用。
三技能联动流程：equity-architecture-guide(诊断) → holding-company-firewall(架构) → corporate-tax-planning(税务) → 本脚本(交付)
"""

import argparse
import io
import os
import zipfile
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

# ── Word XML 命名空间 ──
NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
    "wps": "http://schemas.microsoft.com/office/word/2010/wordprocessingShape",
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
    "wpc": "http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas",
    "wpg": "http://schemas.microsoft.com/office/word/2010/wordprocessingGroup",
    "wpi": "http://schemas.microsoft.com/office/word/2010/wordprocessingInk",
    "wne": "http://schemas.microsoft.com/office/word/2006/wordml",
    "wps-custom": "http://schemas.microsoft.com/office/word/2010/wordprocessingShape",
}
ET.register_namespace("", NS["w"])
for pfx, uri in NS.items():
    ET.register_namespace(pfx, uri)

# ── XML 构建辅助 ──
def tag(t):
    return f"{{http://schemas.openxmlformats.org/wordprocessingml/2006/main}}{t}"

def rtag(t):
    return f"{{http://schemas.openxmlformats.org/officeDocument/2006/relationships}}{t}"

def make_element(name, attrib=None):
    return ET.Element(tag(name), attrib or {})

def make_run(text="", bold=False, size=22, color=None, font_cn="宋体", font_en="Times New Roman"):
    """创建一个 Run（带文字的段落内元素）"""
    r = make_element("r")
    rPr = make_element("rPr")
    if bold:
        rPr.append(make_element("b"))
    sz = make_element("sz", {"w:val": str(size * 2)})
    rPr.append(sz)
    szCs = make_element("szCs", {"w:val": str(size * 2)})
    rPr.append(szCs)
    rFonts = make_element("rFonts", {"w:ascii": font_en, "w:hAnsi": font_en, "w:eastAsia": font_cn})
    rPr.append(rFonts)
    if color:
        rPr.append(make_element("color", {"w:val": color}))
    r.append(rPr)
    t = make_element("t")
    t.text = escape(text) if text else ""
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    r.append(t)
    return r

def make_paragraph(runs, style=None, spacing_before=0, spacing_after=120, justify="both"):
    """创建一个段落"""
    p = make_element("p")
    pPr = make_element("pPr")
    if style:
        pPr.append(make_element("pStyle", {"w:val": style}))
    sp = make_element("spacing", {"w:before": str(spacing_before), "w:after": str(spacing_after)})
    pPr.append(sp)
    jc = make_element("jc", {"w:val": justify})
    pPr.append(jc)
    p.append(pPr)
    for run in runs:
        p.append(run)
    return p

def make_table_simple(headers, rows, col_widths=None):
    """生成一个简单表格（无边框交叉线，Word原生风格）"""
    tbl = make_element("tbl")
    tblPr = make_element("tblPr")
    tblStyle = make_element("tblStyle", {"w:val": "TableGrid"})
    tblPr.append(tblStyle)
    tblW = make_element("tblW", {"w:type": "pct", "w:w": "5000"})
    tblPr.append(tblW)
    tbl.append(tblPr)

    # 可选列宽
    if col_widths:
        tblGrid = make_element("tblGrid")
        for w in col_widths:
            tblGrid.append(make_element("gridCol", {"w:w": str(w)}))
        tbl.append(tblGrid)

    all_rows = [headers] + rows
    for ri, row_data in enumerate(all_rows):
        tr = make_element("tr")
        is_header = ri == 0
        for ci, cell_text in enumerate(row_data):
            tc = make_element("tc")
            tcPr = make_element("tcPr")
            tcW = make_element("tcW", {"w:type": "auto", "w:w": "0"})
            tcPr.append(tcW)
            if col_widths and ci < len(col_widths):
                tcW.set("w:w", str(col_widths[ci]))
                tcW.set("w:type", "dxa")
            tc.append(tcPr)
            p = make_paragraph(
                [make_run(str(cell_text), bold=is_header, size=20)],
                spacing_before=40, spacing_after=40
            )
            tc.append(p)
            tr.append(tc)
        tbl.append(tr)
    return tbl

# ── 文档 OPC 骨架 ──

def _make_content_types():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>"""

def _make_rels():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

def _make_word_rels():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>"""

def _make_styles():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:styleId="Normal" w:default="1">
    <w:name w:val="Normal"/>
    <w:pPr><w:spacing w:line="360" w:lineRule="auto"/></w:pPr>
    <w:rPr><w:sz w:val="22"/><w:szCs w:val="22"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/>
    <w:basedOn w:val="Normal"/>
    <w:pPr><w:spacing w:before="240" w:after="120"/></w:pPr>
    <w:rPr><w:b/><w:sz w:val="36"/><w:szCs w:val="36"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading2">
    <w:name w:val="heading 2"/>
    <w:basedOn w:val="Normal"/>
    <w:pPr><w:spacing w:before="200" w:after="80"/></w:pPr>
    <w:rPr><w:b/><w:sz w:val="28"/><w:szCs w:val="28"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading3">
    <w:name w:val="heading 3"/>
    <w:basedOn w:val="Normal"/>
    <w:pPr><w:spacing w:before="160" w:after="60"/></w:pPr>
    <w:rPr><w:b/><w:sz w:val="24"/><w:szCs w:val="24"/></w:rPr>
  </w:style>
  <w:style w:type="table" w:styleId="TableGrid">
    <w:name w:val="Table Grid"/>
    <w:pPr><w:spacing w:before="0" w:after="0"/></w:pPr>
    <w:tblPr>
      <w:tblBorders>
        <w:top w:val="single" w:sz="4"/><w:bottom w:val="single" w:sz="4"/>
        <w:left w:val="single" w:sz="4"/><w:right w:val="single" w:sz="4"/>
        <w:insideH w:val="single" w:sz="4"/><w:insideV w:val="single" w:sz="4"/>
      </w:tblBorders>
    </w:tblPr>
  </w:style>
</w:styles>"""

def build_docx(body_elements: list) -> bytes:
    """将 body_elements 列表组装成 .docx 字节流"""
    body = make_element("body")
    for el in body_elements:
        body.append(el)

    document = ET.Element(tag("document"))
    document.append(body)

    xml_decl = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    doc_xml = xml_decl + ET.tostring(document, encoding="unicode")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", _make_content_types())
        zf.writestr("_rels/.rels", _make_rels())
        zf.writestr("word/_rels/document.xml.rels", _make_word_rels())
        zf.writestr("word/document.xml", doc_xml.encode("utf-8"))
        zf.writestr("word/styles.xml", _make_styles())
    return buf.getvalue()


# ══════════════════════════════════════════════════════════
#  使用示例（防火墙方案模板）
# ══════════════════════════════════════════════════════════

def build_firewall_case(case_data: dict = None) -> bytes:
    """
    生成防火墙控股架构方案文档

    case_data 结构（可选，不传则用模板默认值）：
    {
        "title": "文档标题",
        "couple": "A和B",
        "companies": [{"name": "...", "holder": "...", "pct": "..."}, ...],
        "third_party_pct": 12,
        "external_shareholders": "...",
        "tax_path": "...",
        "legal_basis": [...],
    }
    """
    d = case_data or {}
    title = d.get("title", "防火墙控股架构方案")
    couple = d.get("couple", "A（夫）和B（妻）")

    elements = []

    # ── 标题 ──
    elements.append(make_paragraph(
        [make_run(title, bold=True, size=28, color="2E4057")],
        spacing_before=200, spacing_after=400, justify="center"
    ))

    # ── 一、现状 ──
    elements.append(make_paragraph(
        [make_run("一、企业现状诊断", bold=True, size=24)],
        spacing_before=300, spacing_after=200
    ))

    companies = d.get("companies", [
        {"name": "苏州S桥国际旅行社有限公司", "holder": "A", "pct": "100%"},
        {"name": "苏州KB虾商务科技有限公司", "holder": "B", "pct": "100%"},
        {"name": "苏州ls达汽车服务有限公司", "holder": "B", "pct": "80%（C 10%, D 10%）"},
        {"name": "苏州EU环境技术有限公司", "holder": "B", "pct": "100%"},
    ])

    elements.append(make_paragraph(
        [make_run(f"自然人{couple}名下共有{len(companies)}家公司：")]
    ))
    for c in companies:
        elements.append(make_paragraph(
            [make_run(f"  · {c['name']} —— {c['holder']}持有 {c['pct']}")]
        ))

    elements.append(make_paragraph(
        [make_run("核心风险：夫妻100%持股 = 实质一人公司（最高院民终1364号），举证倒置 → 被穿透连带风险高。")]
    ))

    # ── 二、目标架构 ──
    elements.append(make_paragraph(
        [make_run("二、目标股权架构设计", bold=True, size=24)],
        spacing_before=300, spacing_after=200
    ))

    elements.append(make_paragraph([make_run("方案A（推荐）：引入第三方持股，打破＂实质一人公司＂认定")]))
    third_pct = d.get("third_party_pct", 12)
    elements.append(make_paragraph([make_run(
        f"A/{third_pct-4}% + B/{third_pct-4}% + 第三方 {third_pct}% —— A+B签一致行动人协议，合计控制"
    )]))

    elements.append(make_paragraph([make_run("方案B（备选）：夫妻100%持股控股公司（不推荐）")]))
    elements.append(make_paragraph([make_run("     穿透风险未解除，仅适用于实在找不到第三方的情形。")]))

    # ── 持股方案对比表 ──
    elements.append(make_paragraph([make_run("持股方案对比：", bold=True, size=22)], spacing_before=160))
    elements.append(make_table_simple(
        ["方案", "持股结构", "防火墙效果", "控制权"],
        [
            ["方案A（推荐）", f"A 44% + B 44% + 第三方 12%", "✅ 强——打破实质一人公司", "一致行动人协议（88%）"],
            ["方案B（备选）", "A 50% + B 50%", "⚠️ 中——穿透风险未解除", "A+B共同控制"],
        ],
        col_widths=[1200, 2400, 2200, 2200]
    ))

    # ── 三、税务路径 ──
    elements.append(make_paragraph(
        [make_run("三、股权转让税务路径", bold=True, size=24)],
        spacing_before=300, spacing_after=200
    ))

    elements.append(make_table_simple(
        ["路径", "个税", "条件"],
        [
            ["平价转让", "0（增值=0）", "注册资本原值转让，净资产未大幅增值"],
            ["非货币性资产投资", "20%但可5年分期", "财税〔2015〕41号"],
            ["溢价转让", "差额×20%", "净资产>注册资本"],
        ],
        col_widths=[2000, 2200, 3800]
    ))

    elements.append(make_paragraph([
        make_run("契税：", bold=True),
        make_run("股权转让不征（财税〔2021〕29号）"),
    ]))
    elements.append(make_paragraph([
        make_run("后续分红：", bold=True),
        make_run("子公司→控股公司免企业所得税（企业所得税法第26条）；控股公司→个人20%"),
    ]))

    # ── 四、执行路线 ──
    elements.append(make_paragraph(
        [make_run("四、执行路线图", bold=True, size=24)],
        spacing_before=300, spacing_after=200
    ))

    steps = d.get("steps", [
        "确定第三方人选 → 谈妥持股条件",
        "新设控股公司（注册资本100-500万，5年实缴）",
        "签署一致行动人协议（A+B联合控制）",
        "评估各公司净资产 → 确定转让价格",
        "通知外部股东 → 获取放弃优先购买权声明",
        "依次办理股权转让工商变更",
        "各子公司修改章程（股东变更为控股公司）",
        "建立财产独立管理制度（独立账户/账簿/决策记录）",
    ])
    for i, step in enumerate(steps, 1):
        elements.append(make_paragraph([make_run(f"  {i}. {step}")]))

    # ── 五、法律依据 ──
    elements.append(make_paragraph(
        [make_run("五、法律法规依据", bold=True, size=24)],
        spacing_before=300, spacing_after=200
    ))

    legal_items = d.get("legal_basis", [
        ("公司法（2023修订）第3条", "有限责任公司——防火墙法理根基"),
        ("公司法（2023修订）第23条", "防火墙例外——滥用独立地位则连带"),
        ("公司法（2023修订）第23条第3款", "一人公司举证倒置——夫妻公司的穿透风险"),
        ("公司法（2023修订）第84条", "股权对外转让→其他股东优先购买权"),
        ("公司法（2023修订）第66条", "持股比例线（67%/51%/34%）"),
        ("民法典第83条", "出资人不得滥用权利"),
        ("九民纪要（2019）§10-11", "人格混同与过度支配认定标准"),
        ("财税〔2015〕41号", "非货币性资产投资分期纳税"),
        ("财税〔2021〕29号", "股权转让不征契税"),
        ("企业所得税法第26条", "居民企业之间分红免税"),
    ])
    for law, desc in legal_items:
        elements.append(make_paragraph([
            make_run(f"  · {law}——", bold=True),
            make_run(desc),
        ]))

    # ── 尾注 ──
    elements.append(make_paragraph([], spacing_before=400))
    p_note = make_paragraph([
        make_run("⚡ 以上方案基于您提供的信息生成，实际执行前建议由专业会计师确认各公司净资产数字及税务预审意见。", color="666666", size=18),
    ], justify="left")
    elements.append(p_note)

    return build_docx(elements)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="防火墙控股架构方案 Word 生成器")
    parser.add_argument("-o", "--output", default=None, help="输出文件路径，默认输出到 stdout")
    args = parser.parse_args()

    docx_bytes = build_firewall_case()

    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)) or ".", exist_ok=True)
        with open(args.output, "wb") as f:
            f.write(docx_bytes)
        print(f"✅ 文档已保存到: {os.path.abspath(args.output)}")
        print(f"  文件大小: {len(docx_bytes):,} 字节")
    else:
        import sys
        sys.stdout.buffer.write(docx_bytes)
