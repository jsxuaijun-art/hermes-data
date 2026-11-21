#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
parse_ledger.py — 科目余额表解析 + 资产负债表平衡检查 + 科目口径映射

输入：科目余额表 .xlsx（常见布局：表头 1-2 行，数据从第 3 行起；列含
      科目编码 / 科目名称 / 期初借方 / 期初贷方 / 本期借方 / 本期贷方 / 期末借方 / 期末贷方）
输出：解析结果 JSON（供 report_generator.py 消费）

用法：
  python parse_ledger.py --input 科目余额表_某某公司_2025年12月.xlsx --output result.json
  python parse_ledger.py --input x.xlsx --output result.json --print-rows   # 先打印行列结构

设计原则：
  - 列名自动探测，兼容"期末余额"单列或"期末借/贷"双列两种布局。
  - 跳过表头行与"科目标题"整行（余额为空的汇总行）。
  - 期末余额 = 期末借方 - 期末贷方（按科目方向取值）。
  - 平衡检查：全部科目 期末借方合计 - 期末贷方合计 应≈0（会计恒等式）。
  - 期初数 = 上期期末数 的跨期核对需用户提供上期文件，本脚本仅做表内期初借贷平衡提示。
"""

import argparse
import json
import re
import sys

try:
    from openpyxl import load_workbook
except ImportError:
    sys.exit("缺少 openpyxl：请先 `pip install openpyxl`")


# ---- 科目口径映射（按关键词归类，用于提取关键指标）----
# 每个科目按"期末余额方向"判断属于资产(借余)或负债/权益(贷余)。
KEYWORD_MAP = {
    "monetary": ["银行存款", "其他货币资金", "库存现金"],
    "receivable": ["应收账款", "应收票据"],
    "inventory": ["原材料", "库存商品", "半成品", "在产品", "生产成本",
                  "周转材料", "委托加工物资", "发出商品"],
    "fixed_asset": ["固定资产"],
    "accum_depr": ["累计折旧"],
    "intangible": ["无形资产"],
    "payable": ["应付账款", "应付票据"],
    "prereceive": ["预收账款", "预收款项"],
    "other_receive": ["其他应收款"],
    "other_pay": ["其他应付款"],
    "tax_payable": ["应交税费"],
    "short_borrow": ["短期借款"],
    "long_borrow": ["长期借款"],
    "paidin": ["实收资本", "股本"],
    "surplus": ["资本公积", "盈余公积", "未分配利润", "本年利润"],
}


def detect_columns(header_cells):
    """根据表头文本定位关键列索引。返回 dict: 逻辑名 -> 列号(0-based)。"""
    text = [str(c).strip() for c in header_cells]
    pos = {}
    # 科目名称
    for i, t in enumerate(text):
        if "科目名称" in t or "名称" in t:
            pos.setdefault("name", i)
        if "科目编码" in t or "编码" in t or "代码" in t:
            pos.setdefault("code", i)
    # 借/贷双列布局
    for i, t in enumerate(text):
        if re.search(r"期末", t) and ("借" in t):
            pos["end_debit"] = i
        if re.search(r"期末", t) and ("贷" in t):
            pos["end_credit"] = i
        if re.search(r"期初", t) and ("借" in t):
            pos["begin_debit"] = i
        if re.search(r"期初", t) and ("贷" in t):
            pos["begin_credit"] = i
    # 单列布局
    for i, t in enumerate(text):
        if "期末余额" == t or (re.search(r"期末", t) and "余额" in t and "借" not in t and "贷" not in t):
            pos.setdefault("end_balance", i)
        if re.search(r"期初", t) and "余额" in t and "借" not in t and "贷" not in t:
            pos.setdefault("begin_balance", i)
    return pos


def to_float(v):
    if v is None:
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    s = re.sub(r"[,\s]", "", str(v))
    if s in ("", "-", "—", "无"):
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0


def end_balance_of(rowvals, pos):
    """计算某科目期末余额（借-贷；若仅单列余额则直接取值）。"""
    if "end_debit" in pos and "end_credit" in pos:
        return to_float(rowvals[pos["end_debit"]]) - to_float(rowvals[pos["end_credit"]])
    if "end_balance" in pos:
        return to_float(rowvals[pos["end_balance"]])
    return 0.0


def begin_balance_of(rowvals, pos):
    if "begin_debit" in pos and "begin_credit" in pos:
        return to_float(rowvals[pos["begin_debit"]]) - to_float(rowvals[pos["begin_credit"]])
    if "begin_balance" in pos:
        return to_float(rowvals[pos["begin_balance"]])
    return 0.0


def classify(name):
    for key, kws in KEYWORD_MAP.items():
        for kw in kws:
            if kw in name:
                return key
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="科目余额表 xlsx 路径")
    ap.add_argument("--output", required=True, help="输出 JSON 路径")
    ap.add_argument("--print-rows", action="store_true", help="先打印前 20 行结构用于人工核对")
    ap.add_argument("--period-months", type=int, default=None,
                    help="本期覆盖月数（用于年化，如 12）；留空由 report_generator 提示")
    args = ap.parse_args()

    wb = load_workbook(args.input, data_only=True, read_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    wb.close()

    # 探测表头：取前两行中"科目名称/编码"出现的一行
    header_row_idx = 0
    for ridx in range(min(3, len(rows))):
        joined = " ".join(str(c) for c in rows[ridx] if c is not None)
        if "科目名称" in joined or "科目" in joined:
            header_row_idx = ridx
            break
    header = rows[header_row_idx]
    pos = detect_columns(header)

    if args.print_rows:
        print(f"[结构] 表头行={header_row_idx+1}，探测列={pos}")
        for i, r in enumerate(rows[:20]):
            print(i, [("" if c is None else c) for c in r][:10])

    if "name" not in pos:
        sys.exit("未定位到'科目名称'列，请用 --print-rows 检查表结构后调整。")

    accounts = []
    for r in rows[header_row_idx + 1:]:
        name = r[pos["name"]] if pos["name"] < len(r) else None
        if name is None:
            continue
        name = str(name).strip()
        if name == "":
            continue
        # 跳过"科目标题"整行：期末借贷均为空且名称像汇总
        eb = end_balance_of(r, pos)
        if eb == 0.0 and begin_balance_of(r, pos) == 0.0:
            # 可能是无余额科目或汇总行；保留有编码的，丢弃纯标题
            code = r[pos["code"]] if ("code" in pos and pos["code"] < len(r)) else None
            if code is None or str(code).strip() == "":
                continue
        code = r[pos["code"]] if ("code" in pos and pos["code"] < len(r)) else ""
        accounts.append({
            "code": str(code).strip(),
            "name": name,
            "begin_debit": to_float(r[pos["begin_debit"]]) if "begin_debit" in pos and pos["begin_debit"] < len(r) else None,
            "begin_credit": to_float(r[pos["begin_credit"]]) if "begin_credit" in pos and pos["begin_credit"] < len(r) else None,
            "end_debit": to_float(r[pos["end_debit"]]) if "end_debit" in pos and pos["end_debit"] < len(r) else None,
            "end_credit": to_float(r[pos["end_credit"]]) if "end_credit" in pos and pos["end_credit"] < len(r) else None,
            "end_balance": eb,
            "begin_balance": begin_balance_of(r, pos),
        })

    # 平衡检查：全部科目 期末借方合计 - 期末贷方合计 应≈0
    end_debit_total = sum(a["end_debit"] or 0.0 for a in accounts)
    end_credit_total = sum(a["end_credit"] or 0.0 for a in accounts)
    end_diff = round(end_debit_total - end_credit_total, 2)
    begin_debit_total = sum(a["begin_debit"] or 0.0 for a in accounts)
    begin_credit_total = sum(a["begin_credit"] or 0.0 for a in accounts)
    begin_diff = round(begin_debit_total - begin_credit_total, 2)

    # 关键指标口径映射（期末余额取数，带方向）
    key_metrics = {}
    for a in accounts:
        cat = classify(a["name"])
        if cat is None:
            continue
        # 资产类（借余为正）：monetary/receivable/inventory/fixed_asset/intangible/other_receive
        # 负债权益类（贷余为正，取负余额）：payable/prereceive/other_pay/tax_payable/short_borrow/long_borrow/paidin/surplus
        sign = 1.0 if cat in ("monetary", "receivable", "inventory", "fixed_asset",
                              "intangible", "other_receive") else -1.0
        val = a["end_balance"] * sign
        if cat == "accum_depr":
            continue  # 单独处理
        key_metrics.setdefault(cat, 0.0)
        key_metrics[cat] += val

    # 固定资产净值 = 固定资产 - 累计折旧
    fa = key_metrics.get("fixed_asset", 0.0)
    ad = sum(a["end_balance"] for a in accounts if classify(a["name"]) == "accum_depr")
    if fa or ad:
        key_metrics["fixed_asset_net"] = round(fa - ad, 2)

    # 聚合：资产总计 / 负债合计 / 所有者权益（按余额方向）
    asset_total = sum(a["end_balance"] for a in accounts if a["end_balance"] > 0)
    liab_equity_total = -sum(a["end_balance"] for a in accounts if a["end_balance"] < 0)
    key_metrics = {k: round(v, 2) for k, v in key_metrics.items()}

    flags = []
    if abs(end_diff) > 0.01:
        flags.append(f"资产负债表不平衡：期末借方合计 - 期末贷方合计 = {end_diff:,.2f}")
    if abs(begin_diff) > 0.01:
        flags.append(f"期初借贷不等：差额 {begin_diff:,.2f}（可能期初未结转）")
    if not key_metrics:
        flags.append("未提取到关键科目，请检查科目名称是否含标准关键词")

    result = {
        "source_file": args.input,
        "period_months": args.period_months,
        "columns_detected": pos,
        "row_count": len(accounts),
        "accounts": accounts,
        "key_metrics": key_metrics,
        "totals": {
            "end_debit_total": round(end_debit_total, 2),
            "end_credit_total": round(end_credit_total, 2),
            "begin_debit_total": round(begin_debit_total, 2),
            "begin_credit_total": round(begin_credit_total, 2),
            "asset_total": round(asset_total, 2),
            "liab_equity_total": round(liab_equity_total, 2),
        },
        "balance_check": {
            "end_diff": end_diff,
            "begin_diff": begin_diff,
            "ok": abs(end_diff) <= 0.01,
        },
        "flags": flags,
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"解析完成：{len(accounts)} 行，资产总计 {asset_total:,.2f}，"
          f"负债+权益 {liab_equity_total:,.2f}，平衡差 {end_diff:,.2f}")
    if flags:
        print("提示：")
        for fl in flags:
            print("  -", fl)


if __name__ == "__main__":
    main()
