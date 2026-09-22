#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
report_generator.py — 生成 8 板块财务报表分析报告（Word + HTML 双交付）

输入：parse_ledger.py 的解析 JSON（可附带利润表手工数据：--revenue/--cost/--net-profit 等）
输出：{公司简称}财务分析报告_{年份对比}.docx  + 同名 .html

用法：
  python report_generator.py --data result.json --company 某某 --outdir ./out \
      --industry "商贸/批发零售" --period-label "2025 vs 2024" \
      --revenue 12000000 --cost 9600000 --net-profit 600000 --op-cash-flow 400000 \
      --prior-revenue 10000000 --prior-net-profit 500000
"""

import argparse
import json
import os
import sys
from datetime import datetime

# ---------------- 阈值库（与 references/threshold-library.md 同步）----------------
GENERIC = {
    "资产负债率": (40, 60, 30, 70),     # 绿灯(40-60) 黄灯边界(30/70)
    "流动比率": (2.0, None, 1.2, 1.0),
    "速动比率": (1.0, None, 0.5, 0.5),
    "现金比率": (0.20, None, 0.10, 0.10),
    "利润含金量": (1.0, None, 0.5, 0.5),
    "核心营业利润占比": (0.70, None, 0.50, 0.50),
    "存货周转率": (4.0, None, 2.0, 2.0),
}
INDUSTRY = {
    "先进制造/航空航天零部件": dict(gm=(0.40, 0.55), nm=(0.15, 0.25), dar=(0.40, 0.60), ar_days=(60, 120)),
    "软件/IT": dict(gm=(0.60, 0.80), nm=(0.10, 0.30), dar=(0.30, 0.50), ar_days=(60, 150)),
    "商贸/批发零售": dict(gm=(0.05, 0.20), nm=(0.02, 0.08), dar=(0.50, 0.70), ar_days=(30, 90)),
    "工程施工/设备": dict(gm=(0.10, 0.20), nm=(0.03, 0.08), dar=(0.60, 0.80), ar_days=(90, 240)),
    "餐饮": dict(gm=(0.50, 0.70), nm=(0.05, 0.15), dar=(0.30, 0.60), ar_days=(0, 5)),
    "纺织/服装": dict(gm=(0.15, 0.30), nm=(0.03, 0.10), dar=(0.50, 0.70), ar_days=(60, 120)),
    "房地产": dict(gm=(0.20, 0.40), nm=(0.05, 0.15), dar=(0.70, 0.85), ar_days=(None, None)),
}

LEVEL_COLOR = {"🔴": "CC0000", "🟡": "CC6600", "🟢": "008000", "❕": "CC6600", "🚨": "CC0000"}


def f2(v):
    return f"{v:,.2f}" if isinstance(v, (int, float)) else "—"


def ratio_level(name, val):
    """返回 ('🟢'/'🟡'/'🔴', 文本)。无阈值返回 ('', '—')。"""
    if val is None:
        return "", "数据不足"
    t = GENERIC.get(name)
    if not t:
        return "", f2(val)
    g_lo, g_hi, y_lo, y_hi = t
    if g_lo is not None and g_hi is not None:
        if g_lo <= val <= g_hi:
            return "🟢", f2(val)
    # 单侧阈值（越大越好）
    if name in ("流动比率", "速动比率", "现金比率", "利润含金量", "核心营业利润占比", "存货周转率"):
        if val >= (g_lo if g_lo is not None else g_hi):
            return "🟢", f2(val)
        if val >= y_lo:
            return "🟡", f2(val)
        return "🔴", f2(val)
    # 资产负债率（适中）
    if name == "资产负债率":
        if y_lo <= val <= y_hi:
            return "🟡", f"{val:.1%}"
        if g_lo <= val <= g_hi:
            return "🟢", f"{val:.1%}"
        return "🔴", f"{val:.1%}"
    return "", f2(val)


def compute_ratios(d, m):
    km = d.get("key_metrics", {})
    months = d.get("period_months") or 12
    tot = d.get("totals", {})
    rev = m.get("revenue")
    cost = m.get("cost")
    npf = m.get("net_profit")
    ocf = m.get("op_cash_flow")

    receivable = km.get("receivable")
    inventory = km.get("inventory")
    monetary = km.get("monetary")
    cur_assets = km.get("monetary", 0) + (receivable or 0) + (inventory or 0)
    cur_liab = km.get("payable", 0) + km.get("prereceive", 0) + km.get("other_pay", 0) + km.get("tax_payable", 0) + km.get("short_borrow", 0)
    total_assets = tot.get("asset_total")
    total_liab = total_assets - tot.get("liab_equity_total") if total_assets else None
    total_liab = tot.get("liab_equity_total")  # 负债+权益合计中负债部分无法拆分时用于率
    # 用 totals：asset_total 为资产总计；负债合计需从 key_metrics 估算
    liab_sum = (km.get("payable", 0) + km.get("prereceive", 0) + km.get("other_pay", 0)
               + km.get("tax_payable", 0) + km.get("short_borrow", 0) + km.get("long_borrow", 0))
    equity = km.get("paidin", 0) + km.get("surplus", 0)

    R = {}
    if rev and cost is not None:
        R["毛利率"] = (rev - cost) / rev if rev else None
    if rev and npf is not None:
        R["净利率"] = npf / rev if rev else None
    if cur_assets and cur_liab:
        R["流动比率"] = cur_assets / cur_liab if cur_liab else None
        R["速动比率"] = (cur_assets - (inventory or 0)) / cur_liab if cur_liab else None
        R["现金比率"] = (monetary or 0) / cur_liab if cur_liab else None
    if total_assets and liab_sum:
        R["资产负债率"] = liab_sum / total_assets if total_assets else None
    if rev and receivable is not None:
        avg = receivable  # 无期初时以期末近似
        R["应收周转率"] = rev / avg if avg else None
        R["应收周转天数"] = 365 / R["应收周转率"] if R["应收周转率"] else None
    if cost and inventory is not None:
        avg = inventory
        R["存货周转率"] = cost / avg if avg else None
        R["存货周转天数"] = 365 / R["存货周转率"] if R["存货周转率"] else None
    if ocf is not None and npf is not None and npf:
        R["利润含金量"] = ocf / npf
    return R


def run_rules(d, m, R):
    """返回命中规则列表 [dict]。"""
    km = d.get("key_metrics", {})
    tot = d.get("totals", {})
    hits = []
    bc = d.get("balance_check", {})

    def add(rid, level, title, detail, cause, advice):
        hits.append(dict(id=rid, level=level, title=title, detail=detail, cause=cause, advice=advice))

    # R1 资产负债表不平衡
    if not bc.get("ok", True):
        add("R1", "🔴", "资产负债表不平衡", f"期末借贷差 {f2(bc.get('end_diff'))}",
            "未分配利润未结转 / 外币折算 / 减值未提 / 期初错 / 口径不一", "要求会计核平后再出报告")
    # R2 期初借贷不等
    if abs(bc.get("begin_diff", 0) or 0) > 0.01:
        add("R2", "🔴", "期初数≠上期期末数", f"期初借贷差 {f2(bc.get('begin_diff'))}",
            "期初未结转或录入错误", "与上年末数核对")
    # R3 个人/关联方往来
    orr = km.get("other_receive", 0)
    cur_assets = km.get("monetary", 0) + km.get("receivable", 0) + km.get("inventory", 0)
    if orr and cur_assets and orr / cur_assets > 0.20:
        add("R3", "🟡", "关联方/个人资金往来", f"其他应收款占流动资产 {orr/cur_assets:.1%}",
            "关联方占用 / 抽逃资金嫌疑", "核实性质，涉个税视同分红")
    # R4/R5 应收集中度（需用户提供，数据不足则跳过）
    if m.get("ar_top1_ratio") is not None:
        r = m["ar_top1_ratio"]
        if r > 0.70:
            add("R4", "🔴", "应收集中度过高", f"前一大客户占应收 {r:.1%}", "单一客户依赖", "分散客户 / 保理")
        elif r >= 0.40:
            add("R5", "🟡", "应收集中度偏高", f"前一大客户占应收 {r:.1%}", "客户集中", "关注回款")
    # R6 存货增速>收入1.5倍（需 prior）
    if m.get("inv_growth") is not None and m.get("rev_growth") is not None:
        if m["inv_growth"] > m["rev_growth"] * 1.5:
            add("R6", "🟡", "存货增速远超收入", f"存货增 {m['inv_growth']:.1%} / 收入增 {m['rev_growth']:.1%}",
                "积压风险", "关注跌价计提")
    # R7/R8 所得税异常
    if m.get("net_profit", 0) and m.get("income_tax", 0) == 0:
        add("R7", "🚨", "净利润>0但所得税=0", f"净利 {f2(m['net_profit'])} / 所得税 0",
            "免税资质 / 递延 / 漏计", "要求会计解释")
    if m.get("effective_tax_rate") is not None and m["effective_tax_rate"] < 0.05:
        add("R8", "🚨", "实际税率<5%", f"实际税率 {m['effective_tax_rate']:.1%}",
            "享受优惠需真实合规", "确认优惠资质")
    # R9 应收增速连续2年>收入1.5倍
    if m.get("ar_growth_2y") is not None and m.get("rev_growth_avg") is not None:
        if m["ar_growth_2y"] > m["rev_growth_avg"] * 1.5:
            add("R9", "❕", "应收连续2年激进赊销", f"应收2年增 {m['ar_growth_2y']:.1%}",
                "坏账风险累积", "收紧信用政策")
    # R10 受限资金
    if m.get("restricted_cash_ratio") is not None and m["restricted_cash_ratio"] > 0.30:
        add("R10", "🟡", "受限资金占比高", f"{m['restricted_cash_ratio']:.1%}",
            "可动用资金低于账面", "核实冻结/质押")
    # R11 担保/净资产
    if m.get("guarantee_equity_ratio") is not None and m["guarantee_equity_ratio"] > 0.50:
        add("R11", "❕", "担保余额/净资产过高", f"{m['guarantee_equity_ratio']:.1%}",
            "互保圈 / 或有负债", "关注代偿风险")
    # R12 核心营业利润占比<50%
    if m.get("core_op_profit_ratio") is not None and m["core_op_profit_ratio"] < 0.50:
        add("R12", "🟡", "利润可持续性差", f"核心营业利润占比 {m['core_op_profit_ratio']:.1%}",
            "依赖一次性收益", "提升主业盈利")
    # R13 资金链三信号
    cr = R.get("现金比率")
    if cr is not None and cr < 0.10 and m.get("ar_days_worsen") and km.get("short_borrow", 0) > 0:
        add("R13", "🔴", "资金链三信号叠加", f"现金比率 {cr:.1%} + 应收恶化 + 短借上升",
            "流动性枯竭风险", "紧急融资安排")
    # R14 应收周转超账期60天
    if m.get("ar_days") is not None and m.get("credit_term") is not None:
        if m["ar_days"] > m["credit_term"] + 60:
            add("R14", "🔴", "应收周转超账期60天+", f"周转 {m['ar_days']:.0f} 天 / 账期 {m['credit_term']} 天",
                "回款停滞", "加强催收")
    # R15 存贷双高
    if km.get("monetary", 0) > 0 and km.get("short_borrow", 0) > 0 and m.get("cash_borrow_high"):
        add("R15", "🟡", "存贷双高", f"货币资金 {f2(km['monetary'])} / 短借 {f2(km['short_borrow'])}",
            "资金被占用 / 体外循环", "核查资金用途")
    # R16 其他应收>20%流动资产
    if orr and cur_assets and orr / cur_assets > 0.20:
        add("R16", "🟡", "其他应收款占比高", f"{orr/cur_assets:.1%}",
            "关联方占用嫌疑", "清理挂账")
    # R17 其他应付大
    if km.get("other_pay", 0) > 0 and m.get("other_pay_large"):
        add("R17", "🟡", "其他应付款余额大", f"{f2(km['other_pay'])}",
            "未入账收入 / 账外资金", "核实来源")
    # R18 销售费用率偏离行业
    if m.get("selling_ratio") is not None and m.get("industry_selling") is not None:
        if abs(m["selling_ratio"] - m["industry_selling"]) > 0.10:
            add("R18", "🔴", "销售费用率偏离行业", f"本企 {m['selling_ratio']:.1%} / 行业 {m['industry_selling']:.1%}",
                "过高疑回扣 / 过低疑隐瞒收入", "核查费用真实性")
    # R19 毛利率连续3期下滑
    if m.get("gm_decline_3q"):
        add("R19", "🟡", "毛利率连续3期下滑", "竞争/成本", "竞争力削弱或成本失控", "降本/提价")
    # R20 经营CF负利润正
    if m.get("op_cash_flow", 0) < 0 and m.get("net_profit", 0) > 0:
        add("R20", "🟡", "纸面富贵", f"经营CF {f2(m['op_cash_flow'])} / 净利 {f2(m['net_profit'])}",
            "赊销激进 / 存货积压 / 占款", "抓回款与去库存")
    # R21 存货增速远高于收入且巨大
    if m.get("inv_growth") is not None and m.get("rev_growth") is not None and km.get("inventory", 0) > 0:
        if m["inv_growth"] > m["rev_growth"] * 1.5 and km["inventory"] > (m.get("inv_big", 0)):
            add("R21", "🟡", "存货积压且余额巨大", f"存货 {f2(km['inventory'])}",
                "跌价风险", "计提减值")
    # R22 期限错配
    if m.get("maturity_mismatch"):
        add("R22", "🟡", "期限错配", "长借短用 / 短借滚存", "流动性风险", "匹配期限结构")
    return hits


# ---------------------------- 渲染 ----------------------------
def build_model(d, m, args):
    R = compute_ratios(d, m)
    hits = run_rules(d, m, R)
    # 核心指标对比（今年 / 去年 / 行业）
    core = []
    order = ["毛利率", "净利率", "流动比率", "速动比率", "资产负债率", "利润含金量", "核心营业利润占比"]
    for name in order:
        lvl, txt = ratio_level(name, R.get(name))
        prior = m.get("prior", {}).get(name)
        ind = ""
        ind_row = INDUSTRY.get(args.industry)
        if ind_row and name == "毛利率" and ind_row.get("gm"):
            lo, hi = ind_row["gm"]; ind = f"{lo:.0%}-{hi:.0%}"
        if ind_row and name == "净利率" and ind_row.get("nm"):
            lo, hi = ind_row["nm"]; ind = f"{lo:.0%}-{hi:.0%}"
        if ind_row and name == "资产负债率" and ind_row.get("dar"):
            lo, hi = ind_row["dar"]; ind = f"{lo:.0%}-{hi:.0%}"
        core.append((name, lvl, txt, (f"{prior:.1%}" if prior is not None else "—"), ind or "—"))
    return R, hits, core


def render_html(company, args, R, hits, core, d, m):
    rows = "".join(
        f"<tr><td>{n}</td><td style='color:#{LEVEL_COLOR.get(l,'000')};font-weight:500'>{l} {t}</td>"
        f"<td>{p}</td><td>{i}</td></tr>" for (n, l, t, p, i) in core)
    risk_rows = "".join(
        f"<tr><td>{h['level']}</td><td>{h['id']} {h['title']}</td><td>{h['detail']}</td>"
        f"<td>{h['cause']}</td><td>{h['advice']}</td></tr>" for h in hits) or "<tr><td colspan=5>未发现重大风险</td></tr>"
    km = d.get("key_metrics", {})
    summary = m.get("one_line") or ("整体财务结构" + ("基本平衡" if d.get('balance_check', {}).get('ok') else "存在不平衡，需核平") + "。")
    html = f"""<!doctype html><html lang=zh><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>{company}财务分析报告</title>
<style>
 body{{font-family:'Microsoft YaHei',sans-serif;max-width:900px;margin:24px auto;color:#222;line-height:1.6}}
 h1{{color:#1F497D}} h2{{color:#1F497D;border-bottom:2px solid #1F497D;padding-bottom:4px}}
 table{{border-collapse:collapse;width:100%;margin:10px 0;font-size:13px}}
 th,td{{border:1px solid #ccc;padding:6px 8px;text-align:left}}
 th{{background:#1F497D;color:#fff}}
 .muted{{color:#999;font-size:12px}}
 .card{{background:#f7f9fc;border-left:4px solid #1F497D;padding:10px 14px;margin:10px 0}}
</style></head><body>
<h1>{company} 财务分析报告</h1>
<p class=muted>数据来源：{d.get('source_file','')} ｜ 对标：{args.industry or '通用默认'}（{m.get('benchmark_type','—')}）｜ 生成：{datetime.now():%Y-%m-%d}</p>
<div class=card><b>执行概要：</b>{summary}</div>
<h2>一、核心指标对比</h2>
<table><tr><th>指标</th><th>本年</th><th>上年</th><th>行业基准</th></tr>{rows}</table>
<h2>七、风险警示</h2>
<table><tr><th>级别</th><th>风险</th><th>数据支撑</th><th>可能原因</th><th>建议</th></tr>{risk_rows}</table>
<h2>二~六、经营/偿债/运营/税务/高企</h2>
<p>关键科目：货币资金 {f2(km.get('monetary',0))} ｜ 应收 {f2(km.get('receivable',0))} ｜ 存货 {f2(km.get('inventory',0))} ｜
固定资产净值 {f2(km.get('fixed_asset_net',0))} ｜ 应付 {f2(km.get('payable',0))} ｜ 其他应收 {f2(km.get('other_receive',0))} ｜ 其他应付 {f2(km.get('other_pay',0))}</p>
<p>详见 Word 版完整 8 板块内容。</p>
<p class=muted>本报告为基于报表数据的初步诊断，异常均标"可能原因"，不构成审计/税务鉴证意见。</p>
</body></html>"""
    return html


def render_docx(company, args, R, hits, core, d, m, out_path):
    try:
        from docx import Document
        from docx.shared import Pt, RGBColor, Inches
        from docx.enum.text import WD_ALIGN_PARAGRAPH
    except ImportError:
        sys.exit("缺少 python-docx：请先 `pip install python-docx`")
    doc = Document()
    # 默认字体微软雅黑
    style = doc.styles["Normal"]
    style.font.name = "Microsoft YaHei"
    style.font.size = Pt(10.5)
    style.element.rPr.rFonts.set(__import__("docx.oxml.ns", fromlist=["qn"]).qn("w:eastAsia"), "Microsoft YaHei")

    def h1(t):
        p = doc.add_heading(t, level=1)
        for r in p.runs:
            r.font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)
        return p

    def para(t, color=None, bold=False, size=10.5):
        p = doc.add_paragraph()
        r = p.add_run(t)
        r.font.size = Pt(size)
        r.bold = bold
        if color:
            r.font.color.rgb = RGBColor.from_string(color)
        return p

    title = doc.add_heading(f"{company} 财务分析报告", level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub = doc.add_paragraph(f"数据来源：{d.get('source_file','')} ｜ 对标：{args.industry or '通用默认'} ｜ 生成：{datetime.now():%Y-%m-%d}")
    sub.runs[0].font.size = Pt(9); sub.runs[0].font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    h1("一、执行概要")
    para(m.get("one_line") or ("整体财务结构" + ("基本平衡。" if d.get('balance_check', {}).get('ok') else "存在不平衡，需核平。")), bold=True)
    tbl = doc.add_table(rows=1, cols=4); tbl.style = "Light Grid Accent 1"
    hdr = tbl.rows[0].cells
    for i, t in enumerate(["指标", "本年", "上年", "行业基准"]):
        hdr[i].text = t
    for (n, l, t, p, i) in core:
        c = tbl.add_row().cells
        c[0].text = n; c[1].text = f"{l} {t}"; c[2].text = p; c[3].text = i

    h1("二、经营业绩分析（利润表）")
    rev = m.get("revenue"); cost = m.get("cost"); npf = m.get("net_profit")
    para(f"营业收入：{f2(rev) if rev else '—'} ｜ 营业成本：{f2(cost) if cost else '—'} ｜ 净利润：{f2(npf) if npf else '—'}")
    gm = f"{R['毛利率']:.1%}" if R.get('毛利率') is not None else '—'
    nm = f"{R['净利率']:.1%}" if R.get('净利率') is not None else '—'
    para(f"毛利率：{gm} ｜ 净利率：{nm}")

    h1("三、资产结构与偿债能力（资产负债表）")
    km = d.get("key_metrics", {}); tot = d.get("totals", {})
    para(f"资产总计：{f2(tot.get('asset_total',0))} ｜ 负债+权益：{f2(tot.get('liab_equity_total',0))}")
    para(f"流动比率：{R.get('流动比率') and f2(R['流动比率']) or '—'} ｜ 速动比率：{R.get('速动比率') and f2(R['速动比率']) or '—'} ｜ 资产负债率：{R.get('资产负债率') and f'{R["资产负债率"]:.1%}' or '—'}")

    h1("四、运营效率分析")
    art = f2(R.get('应收周转率')) if R.get('应收周转率') is not None else '—'
    ard = f"{R['应收周转天数']:.0f}" if R.get('应收周转天数') is not None else '—'
    para(f"应收周转率：{art} ｜ 应收周转天数：{ard} 天")
    invt = f2(R.get('存货周转率')) if R.get('存货周转率') is not None else '—'
    invd = f"{R['存货周转天数']:.0f}" if R.get('存货周转天数') is not None else '—'
    para(f"存货周转率：{invt} ｜ 存货周转天数：{invd} 天")
    para(f"存货：{f2(km.get('inventory',0))} ｜ 应收账款：{f2(km.get('receivable',0))}")

    h1("五、税务合规性提示")
    for tip in [
        "增值税：进销项匹配、视同销售、出口退税单证一致性（如涉及）需核查。",
        "所得税：实际税率异常 / 净利>0而所得税=0 时确认优惠资质真实性。",
        "印花税：购销/借款/租赁合同常漏计，需补提。",
        "房产税：自用从价、出租从租分开计征。",
        "关联交易：个人/股东借款年度终了未还视同分红，代扣个税须到位。",
    ]:
        para("• " + tip)

    if m.get("is_high_tech") or args.industry in ("先进制造/航空航天零部件", "软件/IT"):
        h1("六、高新技术企业资质维护分析（如适用）")
        para("研发占比三档、高新收入≥60%、科技人员≥10% 按高企口径核查（数据充足时填列）。")

    h1("七、风险警示")
    if not hits:
        para("未发现重大风险。", color="008000")
    for h in hits:
        p = doc.add_paragraph()
        r = p.add_run(f"{h['level']} {h['id']} {h['title']} —— {h['detail']}")
        r.bold = True; r.font.color.rgb = RGBColor.from_string(LEVEL_COLOR.get(h['level'], "000000"))
        para(f"可能原因：{h['cause']} ｜ 建议：{h['advice']}", size=9)

    h1("八、管理建议")
    para("紧急（本周）：处理资金链/不平衡等🔴项。")
    para("短期（1-3月）：清理关联方往来、补提税费、去库存。")
    para("中长期（3-12月）：优化信用政策、提升主业盈利、匹配融资期限。")

    doc.add_paragraph("免责声明：本报告基于所提供报表数据的初步诊断，异常均标可能原因，不构成审计或税务鉴证意见。").runs[0].font.color.rgb = RGBColor(0x99, 0x99, 0x99)
    doc.save(out_path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="parse_ledger 的 JSON")
    ap.add_argument("--company", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--industry", default="")
    ap.add_argument("--period-label", default="")
    ap.add_argument("--benchmark-type", default="通用默认")
    ap.add_argument("--revenue", type=float, default=None)
    ap.add_argument("--cost", type=float, default=None)
    ap.add_argument("--net-profit", type=float, default=None)
    ap.add_argument("--op-cash-flow", type=float, default=None)
    ap.add_argument("--income-tax", type=float, default=None)
    ap.add_argument("--effective-tax-rate", type=float, default=None)
    ap.add_argument("--one-line", default="")
    ap.add_argument("--prior", default="")  # JSON 字符串：上年核心指标
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        d = json.load(f)
    m = dict(
        revenue=args.revenue, cost=args.cost, net_profit=args.net_profit,
        op_cash_flow=args.op_cash_flow, income_tax=args.income_tax,
        effective_tax_rate=args.effective_tax_rate, one_line=args.one_line,
        benchmark_type=args.benchmark_type,
    )
    if args.prior:
        try:
            m["prior"] = json.loads(args.prior)
        except Exception:
            pass

    R, hits, core = build_model(d, m, args)
    os.makedirs(args.outdir, exist_ok=True)
    label = args.period_label or datetime.now().strftime("%Y")
    base = f"{args.company}财务分析报告_{label}"
    docx_path = os.path.join(args.outdir, base + ".docx")
    html_path = os.path.join(args.outdir, base + ".html")
    render_docx(company=args.company, args=args, R=R, hits=hits, core=core, d=d, m=m, out_path=docx_path)
    html = render_html(company=args.company, args=args, R=R, hits=hits, core=core, d=d, m=m)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"已生成：\n  Word: {docx_path}\n  HTML: {html_path}\n命中风险 {len(hits)} 条")


if __name__ == "__main__":
    main()
