#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""买断 vs 按张付费全包 —— 三年总账对比 + 印量敏感性 + break-even 反算。

为什么要用脚本：本技能反复栽在"口径不统一"上 —— 一个版本用 1.5 分/页、
另一个版本用 2.5 分/页，结论就跟着漂。把口径固化在这里，每次都重跑。

关键口径（不要改）：
  * 耗材成本必须按 **覆盖率折算后的实际页产量** 算，不能照抄标称页产量。
    标称按 ISO/IEC 19752 的 5% 覆盖率；实际覆盖率越高，能打的页数越少。
      实际页产量 ≈ 标称页产量 × (5% / 实际覆盖率)
    例：实际覆盖率 15% → 实际页产量 ≈ 标称 × 1/3。
  * 纸张两种模式都自付，默认单独列出，不进"谁更省"的比较口径。
  * 全包单价要和「买断的单页综合成本」比，不是和购机价比。

用法：
  python compare_buyout_vs_perpage.py                    # 用内置默认（财税代理实测场景）
  python compare_buyout_vs_perpage.py --annual 100000 --perpage 0.03
  python compare_buyout_vs_perpage.py --help
"""
from __future__ import annotations

import argparse


def effective_yield(nominal_yield: int, actual_coverage_pct: float = 15.0,
                    iso_coverage_pct: float = 5.0) -> float:
    """把标称页产量折算为实际页产量（覆盖率折算）。

    标称页产量按 ISO/IEC 19752 的 5% 覆盖率测定；财税凭证 / 报表实际覆盖率
    常在 15%~30%，因此实际能打的页数只有标称的 1/3 ~ 1/2。
    """
    if actual_coverage_pct <= 0:
        raise ValueError("actual_coverage_pct 必须 > 0")
    return nominal_yield * (iso_coverage_pct / actual_coverage_pct)


def buyout(annual: int, years: int, purchase: float, toner_price: float,
           nominal_yield: int, cov: float, maint_per_year: float,
           drum_price: float = 0.0, drum_yield: int = 0) -> dict:
    """买断路线的三年总账与单页综合成本。"""
    pages = annual * years
    per_page_toner = toner_price / effective_yield(nominal_yield, cov)
    toner_total = per_page_toner * pages
    drum_total = 0.0
    if drum_price and drum_yield:
        drum_total = drum_price * (pages / drum_yield)
    maint_total = maint_per_year * years
    total = purchase + toner_total + drum_total + maint_total
    return {
        "pages": pages,
        "per_page_toner": per_page_toner,
        "toner_total": toner_total,
        "drum_total": drum_total,
        "maint_total": maint_total,
        "total": total,
        "per_page_all_in": total / pages if pages else 0.0,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="买断 vs 按张付费全包 三年总账对比")
    # 印量
    ap.add_argument("--annual", type=int, default=76800, help="年印量（张），默认 76800")
    ap.add_argument("--years", type=int, default=3, help="合同/生命周期年数，默认 3")
    ap.add_argument("--sensitivity", type=str, default="0.65,1.0,1.3",
                    help="敏感性倍数（逗号分隔），默认 0.65,1.0,1.3")
    # 全包
    ap.add_argument("--perpage", type=float, default=0.03,
                    help="全包单价（元/张），默认 0.03")
    ap.add_argument("--market-perpage", type=float, default=0.05,
                    help="市场常规全包行情（元/张），默认 0.05")
    # 买断
    ap.add_argument("--purchase", type=float, default=1650, help="购机价，默认 1650")
    ap.add_argument("--toner-price", type=float, default=120,
                    help="耗材单价（兼容件），默认 120")
    ap.add_argument("--nominal-yield", type=int, default=2600,
                    help="耗材标称页产量，默认 2600")
    ap.add_argument("--coverage", type=float, default=15.0,
                    help="实际覆盖率 %%（财税凭证常用 15~30），默认 15")
    ap.add_argument("--maint-per-year", type=float, default=170,
                    help="年维修摊销，默认 170")
    ap.add_argument("--drum-price", type=float, default=0.0, help="感光鼓单价（可选）")
    ap.add_argument("--drum-yield", type=int, default=0, help="感光鼓标称页产量（可选）")
    # 纸张
    ap.add_argument("--paper", type=float, default=0.025, help="纸张单价（元/张），默认 0.025")
    ap.add_argument("--duplex-discount", type=float, default=0.30,
                    help="双面打印纸张节省比例，默认 0.30")
    args = ap.parse_args()

    b = buyout(args.annual, args.years, args.purchase, args.toner_price,
               args.nominal_yield, args.coverage, args.maint_per_year,
               args.drum_price, args.drum_yield)

    pp_total = args.perpage * b["pages"]
    mkt_total = args.market_perpage * b["pages"]
    paper = args.paper * b["pages"]

    print("=" * 72)
    print(f"三年总账对比  年印量 {args.annual:,} 张 · 合计 {b['pages']:,} 张 · {args.years} 年")
    print("=" * 72)
    print(f"  折算后实际页产量       {effective_yield(args.nominal_yield, args.coverage):,.0f} 页"
          f"（标称 {args.nominal_yield:,} × 5%/{args.coverage:g}%）")
    print(f"  买断·单页耗材成本      {b['per_page_toner']:.4f} 元/页")
    print(f"  买断·单页综合成本      {b['per_page_all_in']:.4f} 元/页")
    print()
    print(f"  {'方案':<26}{'首期':>10}{'3年总支出':>13}{'单页综合':>11}")
    print(f"  {'-'*60}")
    print(f"  {'按张付费全包 ' + f'{args.perpage:g}元/张':<26}"
          f"{'¥0':>10}{'¥' + format(pp_total, ',.0f'):>13}"
          f"{pp_total / b['pages']:>10.4f}")
    print(f"  {'买断 + 自购耗材':<26}{'¥' + format(args.purchase, ',.0f'):>10}"
          f"{'¥' + format(b['total'], ',.0f'):>13}{b['per_page_all_in']:>10.4f}")
    print(f"  {'对照·市场租赁 ' + f'{args.market_perpage:g}元/张':<26}"
          f"{'¥0':>10}{'¥' + format(mkt_total, ',.0f'):>13}"
          f"{mkt_total / b['pages']:>10.4f}")
    print()
    print(f"  纸张（两模式均自付）：¥{paper:,.0f}；默认双面可降至 "
          f"¥{paper * (1 - args.duplex_discount):,.0f}")
    print()

    winner_full, winner_buy = "按张付费全包", "买断 + 自购耗材"
    gap = b["total"] - pp_total
    if gap > 0:
        print(f"  ▶ 结论：{winner_full} 更省，{args.years} 年省 ¥{gap:,.0f}"
              f"（且首期 0 投入、零维修风险、零加粉管理）")
    elif gap < 0:
        print(f"  ▶ 结论：{winner_buy} 更省，{args.years} 年省 ¥{-gap:,.0f}")
    else:
        print("  ▶ 结论：两者持平（此时优先全包：风险转移与管理成本归零）")
    print()

    # ---- 印量敏感性 ----
    print("=" * 72)
    print("印量敏感性（结论是否稳健）")
    print("=" * 72)
    print(f"  {'年印量':>10}{'印量包 3 年':>16}{'买断 3 年':>16}{'谁更省':>16}")
    print(f"  {'-'*58}")
    all_full_wins = True
    for mult in [float(x) for x in args.sensitivity.split(",") if x.strip()]:
        a = int(args.annual * mult)
        bb = buyout(a, args.years, args.purchase, args.toner_price,
                    args.nominal_yield, args.coverage, args.maint_per_year,
                    args.drum_price, args.drum_yield)
        t_full = args.perpage * bb["pages"]
        w = "印量包" if t_full <= bb["total"] else "买断"
        if t_full > bb["total"]:
            all_full_wins = False
        print(f"  {a:>10,}{'¥' + format(t_full, ',.0f'):>16}"
              f"{'¥' + format(bb['total'], ',.0f'):>16}{w:>16}")
    print()
    if all_full_wins:
        print("  ▶ 三档全包都更省 → 该结论不依赖印量估得准不准。"
              "把这句话明确讲给用户，消掉「印量估错会不会翻盘」的顾虑。")
    else:
        print("  ▶ ⚠ 结论对印量敏感，必须把印量区间如实告知用户，不要给单一结论。")
    print()

    # ---- break-even ----
    be = b["total"] / b["pages"]
    print("=" * 72)
    print("谈判用数：break-even 全包单价")
    print("=" * 72)
    print(f"  买断单页综合成本            {be:.4f} 元/页")
    print(f"  → 全包单价 ≤ {be:.4f} 元/张 时，全包更省")
    print(f"  → 报价 {args.perpage:g} 元/张 相对 buyout "
          f"{(be - args.perpage) / be * 100:+.1f}%")
    if args.perpage < args.market_perpage * 0.7:
        print()
        print("  ⚠ 该报价低于市场行情约 "
              f"{(1 - args.perpage / args.market_perpage) * 100:.0f}%，属让利价。"
              "追查：促销拉客 / 机器配得低 / 另有最低消费条件。"
              "谈判重点转为【三年锁价 + 月最低印量 + 备机条款】，不要继续压价。")
    print()
    print("  提醒：全包模式下「耗材结构」维度整体作废，不要再用粉盒容量 / 加粉 /")
    print("        单页耗材成本去评价方案 —— 要改谈机器规格与合同条款。")


if __name__ == "__main__":
    main()
