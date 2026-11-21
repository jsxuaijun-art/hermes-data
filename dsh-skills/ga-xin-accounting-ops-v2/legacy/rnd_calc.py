#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""研发费用加计扣除 / 高企指标 计算与校验工具（ga-xin-accounting-ops）

用法：
  python rnd_calc.py other_limit  <前五项合计> [其他费用实际发生额]
  python rnd_calc.py entrust      <委托境内费用> [委托境外费用] [境内符合条件研发费总额]
  python rnd_calc.py superded     <可加计研发费基数> [加计比例 默认100]  ← 100 或 1 都对
  python rnd_calc.py hte_ratio    <近三年研发费合计> <近三年销售收入合计> [最近一年销售收入]
                                   ← 分档依据为「最近一年销售收入」，第3参数强烈建议传，勿用三年合计分档
  python rnd_calc.py hte_income   <高新技术产品服务收入> <总收入>
  python rnd_calc.py hte_staff    <科技人员全年月平均数> <职工总数全年月平均数>
  python rnd_calc.py rate_choice  <应纳税所得额> [高企税率 默认15] [小微实际税率 默认5]  ← 15 或 0.15 都对
  python rnd_calc.py reconcile    <利润总额> <纳税调增> <纳税调减> <研发加计扣除额>

⚠️ 税率、比例仅为测算参数，不写死；当年以电子税务局申报系统带出口径为准。
   比例参数兼容两种写法：100 / 1 均表示 100%，15 / 0.15 均表示 15%（>1 自动按百分数处理）。
⚠️ 高企15%与小微企业优惠不得同时享受（择一），研发加计扣除可叠加。
"""
import sys


def money(x):
    return f"{x:,.2f}"


def rate(v):
    """比例/税率参数兼容百分数与小数：100→1.0，1→1.0，15→0.15，0.15→0.15，1.2→1.2(120%加计)。"""
    v = float(v)
    if v > 3:          # 明显是百分数写法（>300% 才会误判，实务不存在）
        return v / 100.0
    return v


def other_limit(args):
    base = float(args[0])
    actual = float(args[1]) if len(args) > 1 else None
    # 国家税务总局公告2021年第28号：全部研发项目统一计算，不再按项目分别计算
    limit = base * 0.10 / (1 - 0.10)
    allowed = min(actual, limit) if actual is not None else None
    print(f"前五项合计(人员人工+直接投入+折旧+摊销+设计费等) = {money(base)}")
    print(f"其他相关费用限额 = {money(base)} × 10% / (1-10%) = {money(limit)}")
    if actual is not None:
        print(f"实际发生额 = {money(actual)}")
        print(f"可加计的其他相关费用 = {money(allowed)}")
        print(f"超限额需调增 = {money(max(0.0, actual - limit))}")
        print(f"加计扣除归集基数(前五项+允许其他费用) = {money(base + allowed)}")
    print("依据：财税〔2015〕119号、总局公告2015年第97号(公式)、2021年第28号(统一计算)")


def entrust(args):
    domestic = float(args[0])
    overseas = float(args[1]) if len(args) > 1 else 0.0
    domestic_total = float(args[2]) if len(args) > 2 else domestic
    d_base = domestic * 0.80
    cap = domestic_total * (2.0 / 3.0)
    o_base = min(overseas * 0.80, cap)
    print(f"委托境内：{money(domestic)} × 80% = {money(d_base)}")
    print(f"委托境外：{money(overseas)} × 80% = {money(overseas * 0.80)}；"
          f"不得超过境内符合条件研发费用 {money(domestic_total)} × 2/3 = {money(cap)}")
    print(f"委托境外可计入加计基数 = {money(o_base)}")
    print(f"委托研发合计加计基数 = {money(d_base + o_base)}")
    print("提示：委托个人研发须取得发票；委托/合作研发合同须经科技行政主管部门登记；"
          "关联方委托须提供费用支出明细。依据：财税〔2015〕119号、财税〔2018〕64号")


def superded(args):
    base = float(args[0])
    rate_ = rate(args[1]) if len(args) > 1 else 1.0
    print(f"可加计基数 = {money(base)}；加计比例 = {rate_ * 100:.0f}%")
    print(f"加计扣除额 = {money(base * rate_)}")
    print(f"合计税前扣除(据实+加计) = {money(base * (1 + rate_))}")
    print("提示：集成电路/工业母机 120%(2023-2027)、基础研究 100% 等按比例参数传入；"
          "加计扣除可形成或扩大亏损，亏损结转高企10年/一般5年。")


def hte_ratio(args):
    rnd, sales = float(args[0]), float(args[1])
    # 国科发火〔2016〕195号：占比 = 近三年研发费合计 ÷ 近三年销售收入合计，
    # 但【分档依据】是「最近一年销售收入」，不是近三年合计！吴健书 p297（印刷 p276）。
    last = float(args[2]) if len(args) > 2 else None
    ratio = rnd / sales * 100 if sales else 0
    basis = last if last is not None else sales / 3.0
    if basis <= 50_000_000:
        need, band = 5.0, "最近一年销售收入 ≤ 5000万"
    elif basis <= 200_000_000:
        need, band = 4.0, "5000万 < 最近一年销售收入 ≤ 2亿"
    else:
        need, band = 3.0, "最近一年销售收入 > 2亿"
    ok = ratio >= need
    print(f"近三年研发费合计 = {money(rnd)}；近三年销售收入合计 = {money(sales)}")
    print(f"研发费用占比 = {ratio:.2f}%；分档依据：{basis:,.2f} → {band} → 要求 ≥ {need:.0f}%")
    if last is None:
        print("⚠️ 未提供第3参数，档位暂按「近三年销售收入 ÷ 3」估算，可能误判；"
              "请改传：hte_ratio <近三年研发费> <近三年销售收入> <最近一年销售收入>")
    print(f"判定：{'达标 ✅' if ok else '不达标 ❌'}（缺口 {money(max(0, need / 100 * sales - rnd))}）")
    print("另需满足：中国境内发生的研发费用占全部研发费用比例 ≥ 60%；实际经营期不满三年按实际经营时间计算。")
    print("口径提示：此处用【高企认定口径】，其中'其他费用'一般≤研究开发总费用20%、委托外部研发按80%计入、"
          "含在用建筑物折旧与装备调试费；与加计扣除口径(其他费用10%、房屋折旧不计入)不同，勿混用。"
          "依据：国科发火〔2016〕32号第十一条、195号工作指引，吴健书 p297/p305/p329/p332-333")


def hte_income(args):
    hi, total = float(args[0]), float(args[1])
    ratio = hi / total * 100 if total else 0
    print(f"高新技术产品(服务)收入 = {money(hi)}；总收入 = {money(total)}")
    print(f"占比 = {ratio:.2f}%（要求 ≥ 60%）→ {'达标 ✅' if ratio >= 60 else '不达标 ❌'}")
    print("口径提示：总收入 = 收入总额 − 不征税收入（企业所得税法口径），非会计营业收入。")


def hte_staff(args):
    sci, staff = float(args[0]), float(args[1])
    ratio = sci / staff * 100 if staff else 0
    print(f"科技人员全年月平均数 = {sci}；职工总数全年月平均数 = {staff}")
    print(f"占比 = {ratio:.2f}%（要求 ≥ 10%）→ {'达标 ✅' if ratio >= 10 else '不达标 ❌'}")
    print("口径提示（书 p297）：科技人员须累计实际工作 ≥183天，含直接从事研发与技术创新活动人员、"
          "专门从事上述活动的管理和直接技术服务人员；职工总数含在职、兼职、临时聘用，均按全年月平均数计算。")


def rate_choice(args):
    taxable = float(args[0])
    hte = rate(args[1]) if len(args) > 1 else 0.15
    small = rate(args[2]) if len(args) > 2 else 0.05
    a, b = taxable * hte, taxable * small
    print(f"应纳税所得额 = {money(taxable)}")
    print(f"高企 15% 方案（参数 {hte*100:.1f}%）税额 = {money(a)}")
    print(f"小微优惠方案（参数 {small*100:.1f}%）税额 = {money(b)}")
    print(f"测算更优：{'高企15%' if a <= b else '小微优惠'}，差额 {money(abs(a-b))}")
    print("⚠️ 二者不得同时享受，只能择一；研发加计扣除可与任一方案叠加。")
    print("⚠️ 小微资格还须满足从业人数、资产总额等条件；税率参数为占位值，以当年申报系统为准。")


def reconcile(args):
    profit, add, sub, super_ = map(float, args[:4])
    taxable = profit + add - sub - super_
    print(f"利润总额 = {money(profit)}")
    print(f"纳税调增 = {money(add)}；纳税调减 = {money(sub)}；研发加计扣除额 = {money(super_)}")
    print(f"A100000 应纳税所得额 = {money(taxable)}")
    print("钩稽链：辅助账汇总表 → A107012 → A107010 → A105000 → A100000；"
          "A107041 高企优惠与 A107012 的研发费口径须与专项审计一致。")


CMDS = {
    "other_limit": other_limit, "entrust": entrust, "superded": superded,
    "hte_ratio": hte_ratio, "hte_income": hte_income, "hte_staff": hte_staff,
    "rate_choice": rate_choice, "reconcile": reconcile,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in CMDS:
        print(__doc__)
        sys.exit(2)
    try:
        CMDS[sys.argv[1]](sys.argv[2:])
    except (IndexError, ValueError) as e:
        print(f"参数错误：{e}\n")
        print(__doc__)
        sys.exit(2)
