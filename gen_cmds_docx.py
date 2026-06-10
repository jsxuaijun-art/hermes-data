"""Generate Hermes Agent 命令手册 .docx (pure stdlib, no python-docx)"""
import xml.sax.saxutils as saxutils
import zipfile
import os

def esc(text):
    return saxutils.escape(str(text))

# ── data ──
categories = [
    ("会话管理", [
        ("/new", "/reset", "开新会话，可指定名称"),
        ("/clear", "—", "清屏+开新会话"),
        ("/title", "—", "给当前会话改名字"),
        ("/history", "—", "查看聊天记录"),
        ("/save", "—", "保存当前对话"),
        ("/retry", "—", "重试上一条消息"),
        ("/undo", "—", "撤回上一条交互"),
        ("/branch", "/fork", "分岔探索其他路径"),
        ("/compress", "—", "手动压缩上下文"),
        ("/rollback", "—", "回滚文件快照"),
        ("/snapshot", "/snap", "配置/状态快照"),
        ("/stop", "—", "杀掉所有后台进程"),
        ("/background", "/bg, /btw", "后台跑任务，不打断当前"),
        ("/agents", "/tasks", "查看后台进程状态"),
        ("/queue", "/q", "排队下一条指令"),
        ("/steer", "—", "在工具调用中插一句话"),
        ("/goal", "—", "设定跨轮持续目标"),
        ("/subgoal", "—", "给目标加额外条件"),
        ("/resume", "—", "恢复之前命名的会话"),
        ("/restart", "—", "重启网关（仅网关端可用）"),
        ("/status", "—", "查看当前会话信息"),
        ("/handoff", "—", "将会话移交到消息平台"),
        ("/sethome", "/set-home", "设置本聊天为 home 频道"),
    ]),
    ("配置", [
        ("/config", "—", "查看当前配置"),
        ("/model", "/provider", "切换模型，可指定 provider"),
        ("/codex-runtime", "—", "切换 Codex 运行模式"),
        ("/personality", "—", "设定预设人格"),
        ("/statusbar", "/sb", "开关状态栏（CLI）"),
        ("/verbose", "—", "切换工具调用显示详细度"),
        ("/footer", "—", "开关网关底部元数据"),
        ("/yolo", "—", "跳过危险命令确认"),
        ("/reasoning", "—", "管理推理强度和显示"),
        ("/fast", "—", "切快速模式（Normal/Fast）"),
        ("/skin", "—", "换皮肤/主题（CLI）"),
        ("/indicator", "—", "TUI 等待动画风格"),
        ("/voice", "—", "语音模式开关"),
        ("/busy", "—", "忙时 Enter 行为设置"),
    ]),
    ("工具 & 技能", [
        ("/tools", "—", "管理工具（list/disable/enable）"),
        ("/toolsets", "—", "列出可用工具集"),
        ("/skills", "—", "搜索/安装/查看技能"),
        ("/cron", "—", "管理定时任务"),
        ("/curator", "—", "后台技能维护"),
        ("/kanban", "—", "多 profile 协作看板"),
        ("/reload", "—", "重载 .env 环境变量"),
        ("/reload-mcp", "/reload_mcp", "重载 MCP 服务器"),
        ("/reload-skills", "/reload_skills", "重新扫描技能目录"),
        ("/browser", "—", "连接浏览器 CDP"),
        ("/plugins", "—", "查看插件状态"),
    ]),
    ("信息", [
        ("/help", "—", "显示帮助信息"),
        ("/commands", "—", "分页浏览命令（网关端）"),
        ("/usage", "—", "Token 用量和速率限制"),
        ("/insights", "—", "用量分析报告"),
        ("/whoami", "—", "查看权限等级"),
        ("/profile", "—", "查看 profile 名称和目录"),
        ("/platforms", "/gateway", "网关平台状态"),
        ("/copy", "—", "复制上条回复到剪贴板"),
        ("/paste", "—", "从剪贴板粘贴图片"),
        ("/image", "—", "上传本地图片"),
        ("/update", "—", "更新 Hermes Agent（网关端）"),
        ("/debug", "—", "上传调试报告"),
        ("/gquota", "—", "Gemini 配额查询（CLI）"),
    ]),
    ("退出", [
        ("/quit", "/exit", "退出 CLI"),
    ]),
]

# ── style definitions ──
styles_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:pPr><w:spacing w:before="0" w:after="60" w:line="360" w:lineRule="auto"/></w:pPr>
    <w:rPr><w:rFonts w:ascii="Microsoft YaHei" w:hAnsi="Microsoft YaHei" w:eastAsia="Microsoft YaHei"/><w:sz w:val="21"/><w:szCs w:val="21"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Title">
    <w:name w:val="Title"/>
    <w:pPr><w:spacing w:before="120" w:after="240" w:line="480" w:lineRule="auto"/><w:jc w:val="center"/></w:pPr>
    <w:rPr><w:rFonts w:ascii="Microsoft YaHei" w:hAnsi="Microsoft YaHei" w:eastAsia="Microsoft YaHei"/><w:b/><w:bCs/><w:sz w:val="44"/><w:szCs w:val="44"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading2">
    <w:name w:val="heading 2"/>
    <w:pPr><w:spacing w:before="240" w:after="120" w:line="400" w:lineRule="auto"/></w:pPr>
    <w:rPr><w:rFonts w:ascii="Microsoft YaHei" w:hAnsi="Microsoft YaHei" w:eastAsia="Microsoft YaHei"/><w:b/><w:bCs/><w:sz w:val="32"/><w:szCs w:val="32"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Subtitle">
    <w:name w:val="Subtitle"/>
    <w:pPr><w:spacing w:before="20" w:after="20" w:line="360" w:lineRule="auto"/></w:pPr>
    <w:rPr><w:rFonts w:ascii="Microsoft YaHei" w:hAnsi="Microsoft YaHei" w:eastAsia="Microsoft YaHei"/><w:i/><w:sz w:val="21"/><w:szCs w:val="21"/></w:rPr>
  </w:style>
</w:styles>"""

# ── helpers ──
def rPr_tag(font_name='Microsoft YaHei', font_size='21', bold=False, color=None):
    sz = str(font_size)
    parts = ['<w:rPr>']
    parts.append(f'<w:rFonts w:ascii=\"{esc(font_name)}\" w:hAnsi=\"{esc(font_name)}\" w:eastAsia=\"{esc(font_name)}\"/>')
    parts.append(f'<w:sz w:val=\"{esc(sz)}\"/><w:szCs w:val=\"{esc(sz)}\"/>')
    if bold:
        parts.append('<w:b/><w:bCs/>')
    if color:
        parts.append(f'<w:color w:val=\"{esc(color)}\"/>')
    parts.append('</w:rPr>')
    return ''.join(parts)

def r_tag(text, font_name='Microsoft YaHei', font_size='21', bold=False, color=None):
    return f'<w:r>{rPr_tag(font_name, font_size, bold, color)}<w:t xml:space=\"preserve\">{esc(text)}</w:t></w:r>'

def pPr_tag(alignment=None, spacing_before=20, spacing_after=20, line=360):
    parts = ['<w:pPr>']
    parts.append(f'<w:spacing w:before=\"{spacing_before}\" w:after=\"{spacing_after}\" w:line=\"{line}\" w:lineRule=\"auto\"/>')
    if alignment:
        parts.append(f'<w:jc w:val=\"{alignment}\"/>')
    parts.append('</w:pPr>')
    return ''.join(parts)

def simple_para(text, font_name='Microsoft YaHei', font_size='21', bold=False, alignment=None, color=None, spacing_before=20, spacing_after=20):
    return f'<w:p>{pPr_tag(alignment, spacing_before, spacing_after)}{r_tag(text, font_name, font_size, bold, color)}</w:p>'

def empty_para():
    return '<w:p><w:pPr><w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/></w:pPr></w:p>'

# ── table builder ──
def make_table(cmd_rows):
    """cmd_rows: list of (cmd, aliases, desc)"""
    col_widths = [2200, 2600, 5500]
    rows = []

    for i, (cmd, aliases, desc) in enumerate(cmd_rows):
        row_parts = ['<w:tr>']
        for ci, (text, cw) in enumerate(zip([cmd, aliases, desc], col_widths)):
            is_header = 0 == 0  # no header row
            cell = f"""<w:tc>
<w:tcPr><w:tcW w:w=\"{cw}\" w:type=\"dxa\"/><w:vAlign w:val=\"center\"/></w:tcPr>
<w:p><w:pPr><w:spacing w:before=\"10\" w:after=\"10\" w:line=\"300\" w:lineRule=\"auto\"/><w:jc w:val=\"left\"/></w:pPr>
<w:r>{rPr_tag('Microsoft YaHei', '20', bold=(ci==0))}<w:t xml:space=\"preserve\">{esc(text)}</w:t></w:r></w:p>
</w:tc>"""
            row_parts.append(cell)
        row_parts.append('</w:tr>')
        rows.append(''.join(row_parts))
    return '\n'.join(rows)

def table_xml(cmd_rows):
    lines = ['<w:tbl>']
    # table properties with full borders
    lines.append("""<w:tblPr>
<w:tblW w:w="10300" w:type="dxa"/>
<w:tblBorders>
<w:top w:val="single" w:sz="8" w:space="0" w:color="4472C4"/>
<w:left w:val="single" w:sz="4" w:space="0" w:color="D9E2F3"/>
<w:bottom w:val="single" w:sz="4" w:space="0" w:color="D9E2F3"/>
<w:right w:val="single" w:sz="4" w:space="0" w:color="D9E2F3"/>
<w:insideH w:val="single" w:sz="4" w:space="0" w:color="D9E2F3"/>
<w:insideV w:val="single" w:sz="4" w:space="0" w:color="D9E2F3"/>
</w:tblBorders>
<w:tblLook w:val="04A0"/>
</w:tblPr>""")
    # header row
    lines.append("""<w:tr>
<w:trPr><w:cnfStyle w:val="00100001" w:firstRow="1" w:lastRow="0" w:firstColumn="1" w:lastColumn="0" w:oddVBand="1"/></w:trPr>
<w:tc><w:tcPr><w:tcW w:w="2200" w:type="dxa"/><w:shd w:val="clear" w:color="auto" w:fill="4472C4"/><w:vAlign w:val="center"/></w:tcPr>
<w:p><w:pPr><w:spacing w:before="10" w:after="10" w:line="300" w:lineRule="auto"/><w:jc w:val="center"/></w:pPr>
<w:r><w:rPr><w:rFonts w:ascii="Microsoft YaHei" w:hAnsi="Microsoft YaHei" w:eastAsia="Microsoft YaHei"/><w:b/><w:bCs/><w:color w:val="FFFFFF"/><w:sz w:val="20"/><w:szCs w:val="20"/></w:rPr><w:t xml:space="preserve">命令</w:t></w:r></w:p></w:tc>
<w:tc><w:tcPr><w:tcW w:w="2600" w:type="dxa"/><w:shd w:val="clear" w:color="auto" w:fill="4472C4"/><w:vAlign w:val="center"/></w:tcPr>
<w:p><w:pPr><w:spacing w:before="10" w:after="10" w:line="300" w:lineRule="auto"/><w:jc w:val="center"/></w:pPr>
<w:r><w:rPr><w:rFonts w:ascii="Microsoft YaHei" w:hAnsi="Microsoft YaHei" w:eastAsia="Microsoft YaHei"/><w:b/><w:bCs/><w:color w:val="FFFFFF"/><w:sz w:val="20"/><w:szCs w:val="20"/></w:rPr><w:t xml:space="preserve">别名</w:t></w:r></w:p></w:tc>
<w:tc><w:tcPr><w:tcW w:w="5500" w:type="dxa"/><w:shd w:val="clear" w:color="auto" w:fill="4472C4"/><w:vAlign w:val="center"/></w:tcPr>
<w:p><w:pPr><w:spacing w:before="10" w:after="10" w:line="300" w:lineRule="auto"/><w:jc w:val="center"/></w:pPr>
<w:r><w:rPr><w:rFonts w:ascii="Microsoft YaHei" w:hAnsi="Microsoft YaHei" w:eastAsia="Microsoft YaHei"/><w:b/><w:bCs/><w:color w:val="FFFFFF"/><w:sz w:val="20"/><w:szCs w:val="20"/></w:rPr><w:t xml:space="preserve">作用</w:t></w:r></w:p></w:tc>
</w:tr>""")
    lines.append(make_table(cmd_rows))
    lines.append('</w:tbl>')
    return '\n'.join(lines)

# ── build document body ──
doc_parts = []

# Title
doc_parts.append(simple_para('Hermes Agent 常用命令手册', font_size='44', bold=True, alignment='center', spacing_before=240, spacing_after=120))

# Subtitle
doc_parts.append(simple_para('全命令速查 · 2026年5月', font_size='24', alignment='center', color='666666', spacing_before=0, spacing_after=360))

# Introduction
doc_parts.append(simple_para('斜杠命令一览', font_size='28', bold=True, spacing_before=120, spacing_after=120))
doc_parts.append(simple_para('本手册涵盖 Hermes Agent 所有内置斜杠命令，按功能分类整理。CLI = 仅交互式终端可用，网关 = 企微/电报等消息平台可用，无标注 = 两者皆可用。', spacing_before=0, spacing_after=240))

for cat_name, cmds in categories:
    doc_parts.append(simple_para(cat_name, font_size='28', bold=True, color='4472C4', spacing_before=360, spacing_after=120))
    doc_parts.append(table_xml(cmds))
    doc_parts.append(empty_para())

# ── build body ──
body = '\n'.join(doc_parts)

full_document = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<w:body>
<w:sectPr>
<w:pgSz w:w="11906" w:h="16838"/>
<w:pgMar w:top="1134" w:bottom="1134" w:left="1134" w:right="1134"/>
</w:sectPr>
{body}
</w:body>
</w:document>"""

# ── support files ──
content_types_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>"""

rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

doc_rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>"""

# ── write to Windows Desktop ──
output_path = "/mnt/c/Users/Administrator/Desktop/Hermes Agent 命令手册.docx"

with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.writestr('[Content_Types].xml', content_types_xml.encode('utf-8'))
    zf.writestr('_rels/.rels', rels_xml.encode('utf-8'))
    zf.writestr('word/document.xml', full_document.encode('utf-8'))
    zf.writestr('word/styles.xml', styles_xml.encode('utf-8'))
    zf.writestr('word/_rels/document.xml.rels', doc_rels_xml.encode('utf-8'))

# Verify
with zipfile.ZipFile(output_path, 'r') as zf:
    doc = zf.read('word/document.xml').decode('utf-8')
    paras = doc.count('<w:p>')
    tbls = doc.count('<w:tbl>')
    print(f"✅ 已生成，段落={paras}，表格={tbls}")
    print(f"📁 {output_path}")
