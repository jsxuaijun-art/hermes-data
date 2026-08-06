#!/usr/bin/env python3
"""生成南通咖萌/爽煌架构方案剩余待办综合文档"""

import xml.sax.saxutils as saxutils
import zipfile, os

OUTPUT = "/mnt/d/360MoveData/Users/Admin/Desktop/爽煌_待办完成文档.docx"

def esc(text):
    return saxutils.escape(str(text))

def rPr(font="微软雅黑", sz="24", bold=False, color=""):
    p = [f'<w:rPr><w:rFonts w:ascii="{esc(font)}" w:hAnsi="{esc(font)}" w:eastAsia="{esc(font)}"/>',
         f'<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/>']
    if bold:
        p.append("<w:b/><w:bCs/>")
    if color:
        p.append(f'<w:color w:val="{color}"/>')
    p.append("</w:rPr>")
    return "".join(p)

def r(text, font="微软雅黑", sz="24", bold=False, color=""):
    return f'<w:r>{rPr(font, sz, bold, color)}<w:t xml:space="preserve">{esc(text)}</w:t></w:r>'

def pPr(align="left", before=0, after=0, line=400, firstLine=0, outlineLvl=None):
    a = {"left": "start", "center": "center", "right": "end", "both": "both"}
    al = a.get(align, "start")
    p = [f'<w:pPr><w:spacing w:before="{before}" w:after="{after}" w:line="{line}" w:lineRule="auto"/>',
         f'<w:jc w:val="{al}"/>']
    if firstLine:
        p.append(f'<w:ind w:firstLine="{firstLine}"/>')
    if outlineLvl is not None:
        p.append(f'<w:outlineLvl w:val="{outlineLvl}"/>')
    p.append("</w:pPr>")
    return "".join(p)

def para(text, font="微软雅黑", sz="24", bold=False, color="", align="left", before=0, after=0, line=400, firstLine=0, outlineLvl=None):
    return f'<w:p>{pPr(align, before, after, line, firstLine, outlineLvl)}{r(text, font, sz, bold, color)}</w:p>'

def multi_run_para(runs, align="left", before=0, after=0, line=400, firstLine=0):
    """runs: list of (text, font, sz, bold, color)"""
    rp = pPr(align, before, after, line, firstLine)
    rs = "".join(r(t, f, s, b, c) for t, f, s, b, c in runs)
    return f'<w:p>{rp}{rs}</w:p>'

def table_xml(headers, rows, col_widths=None):
    """Generate table XML with borders"""
    ncols = len(headers)
    if col_widths is None:
        total = 9000
        col_widths = [total // ncols] * ncols
    
    # Table properties
    tbl_pr = f'''<w:tblPr>
      <w:tblW w:w="9000" w:type="dxa"/>
      <w:jc w:val="center"/>
      <w:tblBorders>
        <w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/>
        <w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>
        <w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>
        <w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>
        <w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/>
        <w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/>
      </w:tblBorders>
      <w:tblLook w:val="04A0"/>
    </w:tblPr>'''
    
    # Grid column widths
    grid_col = "".join(f'<w:gridCol w:w="{w}"/>' for w in col_widths)
    tbl_grid = f'<w:tblGrid>{grid_col}</w:tblGrid>'
    
    parts = [f'<w:tbl>{tbl_pr}{tbl_grid}']
    
    # Header row
    parts.append("<w:tr>")
    for i, h in enumerate(headers):
        p = pPr("center", 20, 20, 360, 0)
        cell = f'''<w:tc>
      <w:tcPr><w:tcW w:w="{col_widths[i]}" w:type="dxa"/><w:vAlign w:val="center"/></w:tcPr>
      {p}{r(h, "微软雅黑", "20", True)}
    </w:tc>'''
        parts.append(cell)
    parts.append("</w:tr>")
    
    # Data rows
    for row in rows:
        parts.append("<w:tr>")
        for i, cell_text in enumerate(row):
            p = pPr("left" if i > 0 else "center", 20, 20, 360, 0)
            cell = f'''<w:tc>
      <w:tcPr><w:tcW w:w="{col_widths[i]}" w:type="dxa"/><w:vAlign w:val="center"/></w:tcPr>
      {p}{r(cell_text, "微软雅黑", "20", False)}
    </w:tc>'''
            parts.append(cell)
        parts.append("</w:tr>")
    
    parts.append("</w:tbl>")
    return "\n".join(parts)

def build_document():
    # ========== SECTION ① ==========
    sec1_title = para("一、爽煌个体户注销前差额补税成本测算", "微软雅黑", "32", True, align="left", before=200, after=200, outlineLvl=0)
    
    sec1_sub1 = para("1.1 基本情况", "微软雅黑", "28", True, align="left", before=160, after=120, outlineLvl=1)
    
    basic_info_rows = [
        ["项目", "数值", "备注"],
        ["主体", "爽煌（苏州2家个体户）", "统一名号经营"],
        ["核定收入", "28,000元/月/店", "税务局核定征收"],
        ["合计核定", "56,000元/月（两店合计）", "低于增值税免税门槛"],
        ["实际收入", "5~6万/月/店", "取中值55,000元/月/店"],
        ["合计实际", "110,000元/月（两店合计）", "超过增值税免税门槛"],
        ["差额处理", "私户收款", "未申报、未入账"],
        ["经营时长假设", "36个月（约3年）", "用于滞纳金估算"],
        ["行业类型", "品牌代理/批发零售", "应税所得率5%~10%"],
    ]
    basic_table = table_xml(
        ["项目", "数值", "备注"],
        basic_info_rows[1:],
        col_widths=[2500, 3500, 3000]
    )
    
    sec1_sub2 = para("1.2 增值税补税测算", "微软雅黑", "28", True, align="left", before=160, after=120, outlineLvl=1)
    
    vat_intro = para(
        "政策依据：财政部 税务总局公告2023年第1号、第19号，小规模纳税人适用3%征收率减按1%征收增值税的政策延续至2027年12月31日；月销售额10万元以下免征增值税。",
        "微软雅黑", "20", False, before=40, after=40, line=360, firstLine=420
    )
    
    vat_rows1 = [
        ["方案", "判断逻辑", "结果"],
        ["按核定收入申报", "56,000元/月 < 100,000元", "免征增值税 ✓"],
        ["按实际收入（清算）", "110,000元/月 > 100,000元", "需全额缴增值税 ✗"],
    ]
    vat_table1 = table_xml(
        ["方案", "判断逻辑", "结果"],
        vat_rows1[1:],
        col_widths=[2500, 3500, 3000]
    )
    
    vat_calc = para(
        "如注销时税务局按实际收入清算，增值税补缴计算：",
        "微软雅黑", "20", False, before=40, after=40, line=360
    )
    
    vat_detail_rows = [
        ["项目", "计算过程", "金额"],
        ["月应缴增值税", "110,000 × 1%（减按1%）", "1,100元/月"],
        ["36个月合计", "1,100 × 36", "39,600元"],
        ["其中已申报部分", "核定收入56,000/月已享受免税", "0元"],
        ["需补缴增值税", "——", "39,600元"],
    ]
    vat_table2 = table_xml(
        ["项目", "计算过程", "金额"],
        vat_detail_rows[1:],
        col_widths=[3000, 3500, 2500]
    )
    
    sec1_sub3 = para("1.3 经营所得个人所得税补税测算", "微软雅黑", "28", True, align="left", before=160, after=120, outlineLvl=1)
    
    pit_intro = para(
        "政策依据：个体工商户经营所得适用5%~35%超额累进税率。苏州地区对核定征收个体户采用应税所得率或附征率方式。2023年至2027年底，年应纳税所得额不超过100万元部分减半征收。本测算按附征率1%（批发零售业常见标准）计算。",
        "微软雅黑", "20", False, before=40, after=40, line=360, firstLine=420
    )
    
    pit_rows = [
        ["项目", "核定收入口径", "实际收入口径", "差额"],
        ["月收入/店", "28,000元", "55,000元", "27,000元"],
        ["两店月合计", "56,000元", "110,000元", "54,000元"],
        ["月应缴个税（附征率1%×减半50%）", "280元", "550元", "270元"],
        ["36个月应缴合计", "10,080元", "19,800元", "9,720元"],
        ["已缴个税", "10,080元", "——", "——"],
        ["需补缴个税", "——", "——", "9,720元"],
    ]
    pit_table = table_xml(
        ["项目", "核定收入口径", "实际收入口径", "差额"],
        pit_rows[1:],
        col_widths=[2500, 2000, 2000, 2500]
    )
    
    sec1_sub4 = para("1.4 滞纳金测算", "微软雅黑", "28", True, align="left", before=160, after=120, outlineLvl=1)
    
    late_intro = para(
        "政策依据：《税收征收管理法》第三十二条，从滞纳税款之日起按日加收万分之五（0.05%）滞纳金，年化约18.25%，不予减免。滞纳金因税务机关责任导致的可免，但本案例为纳税人少申报，不可减免。",
        "微软雅黑", "20", False, before=40, after=40, line=360, firstLine=420
    )
    
    late_rows = [
        ["税种", "补税本金", "估算平均滞纳天数", "滞纳金", "计算说明"],
        ["增值税", "39,600元", "540天（约18个月）", "10,692元", "39,600×0.05%×540"],
        ["经营所得个税", "9,720元", "540天", "2,624元", "9,720×0.05%×540"],
        ["合计", "49,320元", "——", "13,316元", "——"],
    ]
    late_table = table_xml(
        ["税种", "补税本金", "估算平均滞纳天数", "滞纳金", "计算说明"],
        late_rows[1:],
        col_widths=[1800, 1800, 2200, 1500, 1700]
    )
    
    sec1_sub5 = para("1.5 罚款风险", "微软雅黑", "28", True, align="left", before=160, after=120, outlineLvl=1)
    
    penalty_text = para(
        "根据《税收征收管理法》第六十三条，纳税人少申报收入构成偷税的，税务机关可处不缴或少缴税款50%以上5倍以下罚款。",
        "微软雅黑", "20", False, before=40, after=40, line=360, firstLine=420
    )
    
    penalty_rows = [
        ["方案", "主动补税后注销", "直接注销（被动发现）"],
        ["补税总额", "49,320元（增值税+个税）", "49,320元"],
        ["滞纳金", "13,316元", "13,316元"],
        ["罚款", "可能免除（主动补缴）", "0.5~5倍税费≈24,660~246,600元"],
        ["税务信用影响", "低（主动纠正）", "高（可能进黑名单）"],
        ["合计成本（最低）", "62,636元", "87,296元（含0.5倍罚款）"],
        ["合计成本（最差）", "62,636元", "309,236元（含5倍罚款）"],
    ]
    penalty_table = table_xml(
        ["科目", "主动补税后注销", "直接注销（被动发现）"],
        penalty_rows[1:],
        col_widths=[3000, 3000, 3000]
    )
    
    sec1_conclusion_title = para("1.6 结论与建议", "微软雅黑", "28", True, align="left", before=160, after=120, outlineLvl=1)
    
    conclusion_rows = [
        ["决策点", "建议", "理由"],
        ["是否主动补税", "✅ 建议主动补税后再注销", "成本可控（约6.3万），避免罚款翻倍风险"],
        ["补税时点", "注销前1~2个月完成", "有缓冲期应对税务问询"],
        ["申报口径", "以"自查补申报"方式处理", "避免被定性为偷税"],
        ["是否聘请税务师", "✅ 建议聘请", "降低沟通成本，提高补税效率"],
    ]
    conclusion_table = table_xml(
        ["决策点", "建议", "理由"],
        conclusion_rows[1:],
        col_widths=[2500, 3500, 3000]
    )
    
    # ========== SECTION ② ==========
    sec2_title = para("\n二、POS私账+社保零参保的补救成本测算", "微软雅黑", "32", True, align="left", before=400, after=200, outlineLvl=0)
    
    sec2_sub1 = para("2.1 POS私账补救测算", "微软雅黑", "28", True, align="left", before=160, after=120, outlineLvl=1)
    
    pos_intro = para(
        "现状：爽煌两店实际收入中，核定部分（28,000/月/店）通过对公账户收款并正常申报，超出部分（约27,000/月/店）通过POS机走私户收款，未入账未申报。",
        "微软雅黑", "20", False, before=40, after=40, line=360, firstLine=420
    )
    
    # POS私账的核心问题是：
    # 1. 未申报收入的税款补缴（已在①中计算）
    # 2. 私户流水被银行或税务局发现的合规风险
    # 3. 私户收入在注销前需要处理
    # 其实POS私账的补救成本主要就是差额补税，已经在①中涵盖了
    # 但这里需要补充说明：私户资金如何合规处理
    
    pos_rows = [
        ["问题点", "风险等级", "补救措施", "预估成本"],
        ["私户收款未申报", "🔴 高", "主动补税（见第一部分）", "含在62,636元内"],
        ["私户流水异常", "🟡 中", "注销前清理私户流水、保留交易凭证", "时间成本"],
        ["公私账不分（混同）", "🟡 中", "注销前梳理资金流向，区分公私", "会计工时约2~3天"],
        ["个税遗漏（经营所得外）", "🟢 低", "私户收入视为经营所得统一处理", "已含在个税补缴中"],
        ["银行反洗钱风险", "🟢 低", "注销后私户可保留或销户", "0元"],
    ]
    pos_table = table_xml(
        ["问题点", "风险等级", "补救措施", "预估成本"],
        pos_rows[1:],
        col_widths=[2200, 1500, 3300, 2000]
    )
    
    pos_cost_text = para(
        "POS私账补救的核心成本已在第一部分补税中覆盖。额外成本主要为会计工时（梳理账务、调账）约2,000~3,000元。",
        "微软雅黑", "20", True, color="C00000", before=40, after=40, line=360, firstLine=420
    )
    
    sec2_sub2 = para("2.2 社保零参保补救测算", "微软雅黑", "28", True, align="left", before=160, after=120, outlineLvl=1)
    
    ss_intro = para(
        "政策依据：苏州市2025年7月~2026年6月社保最低缴费基数4,494元/月。单位+个人合计费率约35.2%（养老24%+医疗10%+失业1%+工伤0.2%），单位部分约24.7%，个人部分约10.5%。",
        "微软雅黑", "20", False, before=40, after=40, line=360, firstLine=420
    )
    
    ss_intro2 = para(
        "社保零参保的风险：①员工可随时要求补缴（无追溯时效限制）；②劳动监察可行政处罚；③工伤风险由企业全额承担。",
        "微软雅黑", "20", False, before=40, after=40, line=360, firstLine=420
    )
    
    # 假设爽煌员工人数：作为品牌代理，两店假设员工6~8人
    ss_rows = [
        ["项目", "测算逻辑", "金额"],
        ["假设员工人数", "两店合计6人", "——"],
        ["最低缴费基数", "苏州2025年度下限", "4,494元/月/人"],
        ["单位月缴费/人", "4,494×24.7%（养老16%+医疗7%+生育1%+失业0.5%+工伤0.2%）", "约1,110元"],
        ["个人月缴费/人", "4,494×10.5%（养老8%+医疗2%+失业0.5%）", "约472元"],
        ["单位月合计（6人）", "1,110×6", "6,660元/月"],
        ["历史补缴（假设需补12个月）", "6,660×12", "79,920元"],
        ["滞纳金（按日万分之五，平均180天）", "79,920×0.05%×180", "7,193元"],
        ["合计社保补救成本", "——", "约87,113元"],
    ]
    ss_table = table_xml(
        ["项目", "测算逻辑", "金额"],
        ss_rows[1:],
        col_widths=[3500, 3500, 2000]
    )
    
    ss_note = para(
        "注：社保补缴需结合员工实际就业时间计算。上述测算是假设需补缴过去12个月的社保。如果员工可协商以"新入职"方式重新参保（不补历史），则成本仅为每月6,660元的新增用工成本，无需历史补缴。",
        "微软雅黑", "20", False, color="C00000", before=40, after=40, line=360, firstLine=420
    )
    
    # Total section 2
    sec2_total_rows = [
        ["补救项目", "最低成本", "最高成本", "备注"],
        ["POS私账补税", "62,636元", "62,636元", "即为第一部分主动补税方案"],
        ["POS私账会计工时", "2,000元", "3,000元", "梳理账务调账"],
        ["社保历史补缴+滞纳金", "0元（重新参保）", "87,113元", "取决于是否补历史"],
        ["社保未来新增用工成本", "6,660元/月", "6,660元/月", "持续成本"],
        ["合计（一次+持续）", "71,296元 + 6,660元/月", "159,749元 + 6,660元/月", "——"],
    ]
    sec2_total_table = table_xml(
        ["补救项目", "最低成本", "最高成本", "备注"],
        sec2_total_rows[1:],
        col_widths=[2500, 2000, 2000, 2500]
    )
    
    # ========== SECTION ③ ==========
    sec3_title = para("\n三、与赵老板沟通话术", "微软雅黑", "32", True, align="left", before=400, after=200, outlineLvl=0)
    
    sec3_sub1 = para("3.1 沟通策略（不吓跑）", "微软雅黑", "28", True, align="left", before=160, after=120, outlineLvl=1)
    
    strategy = [
        para("核心原则：把"补税"包装成"合规升级"，把"成本"转化为"安全保障"。", "微软雅黑", "20", True, color="C00000", before=40, after=40, line=360, firstLine=420),
        para("① 先说好事（架构方案已经过验证）→ 再说要落地的事（补丁）", "微软雅黑", "20", False, before=20, after=20, line=360, firstLine=420),
        para("② 用"建议/可以选择"替代"必须/你应该"", "微软雅黑", "20", False, before=20, after=20, line=360, firstLine=420),
        para("③ 给出选择（方案A/方案B），让赵总有掌控感", "微软雅黑", "20", False, before=20, after=20, line=360, firstLine=420),
        para("④ 用数字说话，但换算成"九牛一毛"的比例", "微软雅黑", "20", False, before=20, after=20, line=360, firstLine=420),
        para("⑤ 最终归结到：这次弄干净，以后就省心了", "微软雅黑", "20", False, before=20, after=20, line=360, firstLine=420),
    ]
    strategy_text = "".join(strategy)
    
    sec3_sub2 = para("3.2 通话/见面话术脚本", "微软雅黑", "28", True, align="left", before=160, after=120, outlineLvl=1)
    
    script_sections = [
        ("开场｜回顾已有成果（30秒）", [
            ("赵总，上次我们聊的咖萌架构方案，我回去又反复推了几遍，大方向没问题——",
             "微软雅黑", "20", False, before=40, after=20, line=360),
            ("南通咖萌做母公司，苏州设子公司卡尔蒙，下面挂分公司。",
             "微软雅黑", "20", False, before=20, after=20, line=360),
            ("等分公司注册完你们苏州的店都变成同一个法人主体下的非独立核算分支，同城亏赚互抵，税负能降一截。",
             "微软雅黑", "20", False, before=20, after=20, line=360),
            ("这个方案我已经让律所和税务师都过了一遍，可以放心推进。",
             "微软雅黑", "20", True, before=20, after=40, line=360),
        ]),
        ("过渡｜提出需要落地的3件事（1分钟）", [
            ("现在要落地这个方案，有3件事需要先处理好，咱们把尾巴收干净了再搬进新房。",
             "微软雅黑", "20", False, before=40, after=20, line=360),
            ("前两件是这个月就要处理的——爽煌注销前的税务处理。",
             "微软雅黑", "20", False, before=20, after=20, line=360),
            ("第三件是整个新架构的运转流程设计，我建议先定好规则再跑。",
             "微软雅黑", "20", False, before=20, after=40, line=360),
        ]),
        ("话题1｜爽煌注销补税（3分钟）", [
            ("爽煌现在要注销，税务局那边会做清算。它现在是核定28,000的额度，",
             "微软雅黑", "20", False, before=40, after=20, line=360),
            ("但咱们实际业务量远超这个数。",
             "微软雅黑", "20", False, before=20, after=20, line=360),
            ("如果注销时被税务局翻出来，被动补税+罚款可能是十几万甚至三十万。",
             "微软雅黑", "20", False, before=20, after=20, line=360),
            ("但如果我们主动在注销前自查补报，成本大概在6万出头，",
             "微软雅黑", "20", True, before=20, after=20, line=360),
            ("而且主动的和被动的性质完全不同，前者是"自查纠正"，后者是"偷税"。",
             "微软雅黑", "20", False, before=20, after=20, line=360),
            ("所以我的建议是：先主动补缴，把底子弄干净了再注销。",
             "微软雅黑", "20", True, before=20, after=20, line=360),
            ("需要补多少我让团队算清楚了，等会儿发你看。",
             "微软雅黑", "20", False, before=20, after=40, line=360),
        ]),
        ("话题2｜社保问题（2分钟）", [
            ("员工社保这块目前是零参保，这件事风险其实比税务还大。",
             "微软雅黑", "20", False, before=40, after=20, line=360),
            ("员工哪天不高兴了去劳动监察投诉，企业要全额补缴，没有时效限制。",
             "微软雅黑", "20", False, before=20, after=20, line=360),
            ("而且万一出个工伤，没有社保的话企业全赔，那就不止几万了。",
             "微软雅黑", "20", False, before=20, after=20, line=360),
            ("我建议趁这次架构调整，把社保也一并规范起来。",
             "微软雅黑", "20", False, before=20, after=20, line=360),
            ("有两个选择：补历史社保（成本约8.7万）或者以新公司名义重新参保（每月6,660）。",
             "微软雅黑", "20", True, before=20, after=20, line=360),
            ("我建议用后者，成本可控，也不需要跟员工提补缴的事。",
             "微软雅黑", "20", False, before=20, after=40, line=360),
        ]),
        ("话题3｜新架构的结算机制（2分钟）", [
            ("架构落地的最后一步，是内部结算机制。",
             "微软雅黑", "20", False, before=40, after=20, line=360),
            ("苏州卡尔蒙是南通咖萌的全资子公司，但不是分公司。",
             "微软雅黑", "20", False, before=20, after=20, line=360),
            ("所以母子公司之间的货物流和资金流要有合同和发票，不能"转个账就完事"。",
             "微软雅黑", "20", False, before=20, after=20, line=360),
            ("我这边准备了一份结算流程图，明确每个环节谁开票、谁付款、谁记账。",
             "微软雅黑", "20", False, before=20, after=20, line=360),
            ("另外劳务派遣合同和房租合同需要平移给苏州卡尔蒙签，不然成本和收入对不上。",
             "微软雅黑", "20", False, before=20, after=20, line=360),
            ("这些我做了一页流程单，到时候让你办公室的人对接就行。",
             "微软雅黑", "20", False, before=20, after=40, line=360),
        ]),
        ("收尾｜给赵总一个明确的时间线（30秒）", [
            ("赵总，我这边已经把每个环节的预估成本和时间线整理好了。",
             "微软雅黑", "20", False, before=40, after=20, line=360),
            ("下周先把补税做了，同时把劳务合同平移的手续启动。",
             "微软雅黑", "20", False, before=20, after=20, line=360),
            ("等爽煌注销完成、卡尔蒙注册下来，咱们的新架构就能正式跑了。",
             "微软雅黑", "20", False, before=20, after=20, line=360),
            ("这次一次弄干净，以后就是合规经营，睡觉都踏实。",
             "微软雅黑", "20", True, before=20, after=40, line=360),
        ]),
    ]
    
    script_parts = []
    for title, runs in script_sections:
        script_parts.append(para(title, "微软雅黑", "24", True, before=120, after=80, line=400))
        for run in runs:
            script_parts.append(para(*run))
    script_text = "".join(script_parts)
    
    sec3_sub3 = para("3.3 常见问题应对（Q&A）", "微软雅黑", "28", True, align="left", before=160, after=120, outlineLvl=1)
    
    qa_rows = [
        ["赵总可能的反应", "正确回应"],
        [""6万太多了吧？"", "赵总，这笔钱交的是税不是服务费。如果等注销时税务局查出来，最少也要交八九万，还有可能罚款。6万已经是成本最低的方案了。"],
        [""以前也没出事啊"", "以前是以前，爽煌要注销是税务局必须过的一关。主动补和被动补，性质完全不同——前者叫自查纠正，后者叫偷税。我们替您做的是把后路堵住。"],
        [""社保先不交行不行？"", "可以，但风险咱们要心里有数：①员工随时可以去劳动监察要求补缴；②万一出工伤，没有社保，企业全赔。每月6,660元对您来说就是九牛一毛。"],
        [""那我这新公司弄下来总共要花多少？"", "两笔开支：①爽煌注销补税约6.3万（一次性）；②社保每月6,660元（持续）。架构本身不需要额外费用。合计下来一年也就14万出头，比被动挨罚便宜太多。"],
        [""这个事情急不急？"", "我建议下周开始操作。爽煌的注销走流程大概还要一段时间，补税需要提前做。拖久了滞纳金一直在涨，每天多几十块，没必要。"],
        [""合同平移怎么做？"", "劳务派遣和房租合同，跟甲方说一句"主体变更为苏州卡尔蒙"，在原合同上签个变更协议就行，不需要重新签。模板我让法务准备好了。"],
        [""搞这么复杂有必要吗？"", "赵总，您现在南通咖萌30多家店，以后还要继续做大。现在花6万把底子打干净，以后融资、扩店都没有后顾之忧。小钱办大事。"],
    ]
    qa_table = table_xml(
        ["赵总可能的反应", "正确回应"],
        qa_rows,
        col_widths=[2500, 6500]
    )
    
    sec3_sub4 = para("3.4 赵总需要做的动作清单", "微软雅黑", "28", True, align="left", before=160, after=120, outlineLvl=1)
    
    action_rows = [
        ["序号", "动作", "负责方", "时间"],
        ["①", "确认主动补税方案（签字确认）", "赵总", "今明2天"],
        ["②", "提供爽煌私户银行流水（近36个月）", "赵总/财务", "本周内"],
        ["③", "确认员工社保方案（重新参保）", "赵总", "本周内"],
        ["④", "联系劳务派遣公司签变更协议", "赵总/办公室", "下周"],
        ["⑤", "联系房东签房租合同变更协议", "赵总/办公室", "下周"],
        ["⑥", "注册苏州卡尔蒙公司", "江姐团队", "同步推进"],
        ["⑦", "补税申报（自查补报）", "江姐团队", "下周"],
        ["⑧", "爽煌注销（税务清算）", "江姐团队", "补税完成后"],
    ]
    action_table = table_xml(
        ["序号", "动作", "负责方", "时间"],
        action_rows[1:],
        col_widths=[600, 3800, 2300, 2300]
    )
    
    # ========== Assemble document ==========
    body_parts = [
        para("爽煌/南通咖萌架构方案 — 待办完成文件", "微软雅黑", "44", True, align="center", before=600, after=100),
        para("内部使用·机密", "微软雅黑", "20", False, align="center", before=0, after=0),
        para("编制：盈信财税 · 江敏", "微软雅黑", "24", False, align="center", before=200, after=200),
        para("日期：2026年5月15日", "微软雅黑", "24", False, align="center", before=0, after=400),
        # Section 1
        sec1_title, sec1_sub1, basic_table,
        para("", "微软雅黑", "20", before=40, after=40),
        sec1_sub2, vat_intro, vat_table1, para("", "微软雅黑", "20", before=20, after=20), vat_calc, vat_table2,
        para("", "微软雅黑", "20", before=40, after=40),
        sec1_sub3, pit_intro, pit_table,
        para("", "微软雅黑", "20", before=40, after=40),
        sec1_sub4, late_intro, late_table,
        para("", "微软雅黑", "20", before=40, after=40),
        sec1_sub5, penalty_text, penalty_table,
        para("", "微软雅黑", "20", before=40, after=40),
        sec1_conclusion_title, conclusion_table,
        # Section 2
        sec2_title, sec2_sub1, pos_intro, pos_table, pos_cost_text,
        para("", "微软雅黑", "20", before=40, after=40),
        sec2_sub2, ss_intro, ss_intro2, ss_table, ss_note,
        para("", "微软雅黑", "20", before=40, after=40),
        sec2_total_table,
        # Section 3
        sec3_title, sec3_sub1, strategy_text,
        para("", "微软雅黑", "20", before=40, after=40),
        sec3_sub2, script_text,
        para("", "微软雅黑", "20", before=40, after=40),
        sec3_sub3, qa_table,
        para("", "微软雅黑", "20", before=40, after=40),
        sec3_sub4, action_table,
    ]
    
    body = "\n".join(body_parts)
    
    # Build complete XML document
    full_doc = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <w:body>
    <w:sectPr>
      <w:pgSz w:w="11906" w:h="16838"/>  <!-- A4 -->
      <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720"/>
    </w:sectPr>
    {body}
  </w:body>
</w:document>'''
    
    # Styles
    styles_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:rPr>
      <w:rFonts w:ascii="微软雅黑" w:hAnsi="微软雅黑" w:eastAsia="微软雅黑"/>
      <w:sz w:val="24"/>
      <w:szCs w:val="24"/>
    </w:rPr>
  </w:style>
</w:styles>'''
    
    # Content types
    content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>'''
    
    # Relationships
    rels_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''
    
    doc_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>'''
    
    # Write ZIP
    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types.encode("utf-8"))
        zf.writestr("_rels/.rels", rels_xml.encode("utf-8"))
        zf.writestr("word/document.xml", full_doc.encode("utf-8"))
        zf.writestr("word/styles.xml", styles_xml.encode("utf-8"))
        zf.writestr("word/_rels/document.xml.rels", doc_rels.encode("utf-8"))
    
    # Verify
    import xml.etree.ElementTree as ET
    import zipfile
    with zipfile.ZipFile(OUTPUT, "r") as zf:
        doc = zf.read("word/document.xml").decode("utf-8")
    paras = doc.count("<w:p>")
    tbls = doc.count("<w:tbl>")
    try:
        ET.fromstring(doc)
        valid = "✓"
    except ET.ParseError as e:
        valid = f"✗ {e}"
    
    print(f"文件生成成功: {OUTPUT}")
    print(f"段落: {paras}, 表格: {tbls}, XML验证: {valid}")
    print(f"文件大小: {os.path.getsize(OUTPUT):,} 字节")

if __name__ == "__main__":
    build_document()
