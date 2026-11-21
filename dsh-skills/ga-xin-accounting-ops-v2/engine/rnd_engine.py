#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ga-xin-accounting-ops-v2 / CARE 框架的 Recalc Engine（单入口全链引擎）

设计要点：
  1. 规则是数据（rules/rules.json），算子是代码（本文件 OPS 表）——新增规则若命中已有算子，
     只改 JSON 不改 Python；只有全新算子才需要写代码。刻意不引入表达式引擎/第三方依赖。
  2. 按 as_of 过滤生效期，按 priority 降序裁决，每个结论写入 trace（rule_id/authority/source）。
  3. 客户实例（schema/）是唯一真相源：所有金额从项目明细复算，不读预先写好的结论数字。
  4. 内部作业参考，不构成税务意见；税率/比例/文号须回查官方原文或原 PDF 页面图像。

用法：
  python rnd_engine.py case  <实例.json> [--as-of YYYY-MM-DD] [--out 结果.json] [--compact]
  python rnd_engine.py rules [--as-of YYYY-MM-DD]
  python rnd_engine.py verify [--as-of YYYY-MM-DD] [--due-only] [--checklist]
  python rnd_engine.py kernel
  python rnd_engine.py selftest

verify = 政策时效核验：自动抽取 rules.json 引用的全部文号，按「已到期/90天内临期/现行」分类，
         并给出每个文号的官方核验信源（税务总局 fgk 政策法规库 / 财政部 / 科技部）。
         联网核验动作由 cn-regulation-verification skill（fgk 官方库终裁）执行。
"""
import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
RULES_PATH = ROOT / "rules" / "rules.json"
ENGINE_VERSION = "2.0.0"

OPS = {}


def op(name):
    def deco(fn):
        OPS[name] = fn
        return fn
    return deco


def money(x):
    """金额保留两位（与申报表列至角分一致）"""
    return round(float(x) + 1e-9, 2)


def num(v):
    return float(v or 0)


def ratio6(x):
    """比例/占比保留 6 位，不能用金额的两位精度"""
    return round(float(x), 6)


def effective(rule, as_of):
    if rule.get("effective_from") and as_of < rule["effective_from"]:
        return False
    if rule.get("effective_to") and as_of > rule["effective_to"]:
        return False
    return True


# ---------------------------------------------------------------- 算子

@op("admission_gate")
def _admission_gate(case, rule, ctx):
    p = rule["params"]
    client = case.get("client", {})
    ev = case.get("evidence", {})
    gaps = ctx["_internal"].setdefault("evidence_gaps", [])
    blocked = ctx["_internal"].setdefault("blocked", [])

    if client.get("collection_method") != "查账征收":
        blocked.append("核定征收不适用研发费用加计扣除")
    if client.get("industry_negative_list"):
        blocked.append("负面清单行业（由 R002 计算 50% 兼营判定）")

    req_map = {
        "辅助账": ("auxiliary_ledger", "无研发支出辅助账 → 不得加计扣除"),
        "立项决议": ("project_resolution", "缺立项决议/内部有权部门决议"),
        "工时表": ("timesheet", "缺研发工时记录"),
        "领料记录": ("material_records", "缺领料单/材料记录"),
        "设备使用记录": ("equipment_log", "缺设备使用记录"),
        "科技行政主管部门登记": ("contract_registration", "委托/合作研发合同未经科技部门登记"),
    }
    for req in p.get("require", []):
        key, msg = req_map.get(req, (None, None))
        if key and not ev.get(key, False):
            if msg not in gaps:
                gaps.append(msg)

    need_contract = any(
        pr.get("form") in ("委托研发", "合作研发") for pr in case.get("projects", [])
    )
    if need_contract and "科技行政主管部门登记" in p.get("require", []):
        for pr in case.get("projects", []):
            if pr.get("form") in ("委托研发", "合作研发") and pr.get("contract_registered") is False:
                m = f"项目 {pr.get('id')} 委托/合作合同未登记"
                if m not in gaps:
                    gaps.append(m)

    ctx["admission"]["gates"].append(rule["id"])
    return {"gates": rule["id"], "gaps_found": len(gaps), "blocked": len(blocked)}


@op("negative_list_50")
def _negative_list_50(case, rule, ctx):
    p = rule["params"]
    c = case.get("client", {})
    rev = num(c.get("negative_list_revenue"))
    denom = num(c.get("revenue_total_for_negative"))
    ratio = ratio6(rev / denom) if denom else 0.0
    hit = ratio > p["threshold"]
    ctx["admission"]["negative_list"] = {
        "ratio": ratio, "threshold": p["threshold"], "hit": hit,
        "formula": p["formula"],
    }
    if hit and c.get("industry_negative_list"):
        ctx["_internal"]["blocked"].append("负面清单业务收入占比 >50%，不适用加计扣除")
    return {"ratio": ratio, "hit": hit}


@op("scope_divergence")
def _scope_divergence(case, rule, ctx):
    p = rule["params"]
    w = []
    for d in p.get("divergences", []):
        w.append({"type": "口径差异", "item": d["item"], "加计扣除": d["加计扣除"], "高企认定": d["高企认定"]})
    for l in p.get("ledgers", []):
        w.append({"type": "两套账", "requirement": l})
    if p.get("audit"):
        w.append({"type": "专项审计", "requirement": p["audit"]})

    # 实例中确实存在两口径相反的费用时，给出针对性告警
    for pr in case.get("projects", []):
        e = pr.get("expenses", {})
        for field, label in (("building_depreciation", "房屋折旧/租赁费"),
                             ("equipment_commissioning", "装备调试费"),
                             ("ip_amortization_other", "非专利权知识产权摊销")):
            if num(e.get(field)) > 0:
                w.append({"type": "实例命中", "project": pr.get("id"), "item": label,
                          "action": "该金额仅可计入高企认定口径，不得计入加计扣除口径"})
    ctx["cross_scope_warnings"].extend(w)
    if case.get("client", {}).get("hte_certificate") and p.get("ledgers"):
        ctx["evidence_gaps_ext"].append("高企客户须同时维护高企认定专用辅助账并完成中介专项审计（R006）")
    return {"warnings_added": len(w)}


@op("limit_other_10")
def _limit_other_10(case, rule, ctx):
    p = rule["params"]
    ratio = p["ratio"]
    fields = p.get("base_fields", ["personnel", "direct_input", "depreciation", "amortization", "design"])
    rows = []
    for pr in case.get("projects", []):
        e = pr.get("expenses", {})
        five = sum(num(e.get(k)) for k in fields)
        rows.append({"id": pr.get("id"), "five": five,
                     "other": num(e.get("other_related")), "project": pr})
    base5 = money(sum(r["five"] for r in rows))
    actual = money(sum(r["other"] for r in rows))

    unified = "统一" in p.get("basis", "") or "全部项目" in p.get("basis", "")
    if unified:
        cap = money(base5 * ratio / (1 - ratio))
        allowed = money(min(actual, cap))
        # 按各项目实际发生额占比分摊；最后一项用差额兜底，保证加总闭合
        acc = 0.0
        nonzero = [r for r in rows if r["other"] > 0]
        for i, r in enumerate(nonzero):
            if i == len(nonzero) - 1:
                r["allowed_other"] = money(allowed - acc)
            else:
                r["allowed_other"] = money(allowed * r["other"] / actual) if actual else 0.0
                acc = money(acc + r["allowed_other"])
        for r in rows:
            if r["other"] == 0:
                r["allowed_other"] = 0.0
        allocation = "全部项目统一计算，按项目实际发生额占比分摊"
    else:  # 2020 年及以前：R021 沿革规则，逐项目分别算、不可调剂
        cap = 0.0
        allowed = 0.0
        for r in rows:
            c = money(r["five"] * ratio / (1 - ratio))
            r["allowed_other"] = money(min(r["other"], c))
            cap = money(cap + c)
            allowed = money(allowed + r["allowed_other"])
        allocation = "按每一研发项目分别计算（97号，项目间不可调剂）"

    allowed_by_project = {r["id"]: r["allowed_other"] for r in rows}
    project_allowed = {r["id"]: money(r["five"] + r["allowed_other"]) for r in rows}
    ctx["_internal"]["base5"] = base5
    ctx["_internal"]["allowed_other"] = allowed
    ctx["_internal"]["allowed_by_project"] = allowed_by_project
    ctx["_internal"]["project_allowed"] = project_allowed
    ctx["_internal"]["actual_other"] = actual

    ctx["limits"]["other_related"] = {
        "rule": rule["id"], "basis": p.get("basis"), "base_five_items": base5,
        "actual_other_related": actual, "cap": cap, "allowed": allowed,
        "allocation_method": allocation, "by_project": allowed_by_project,
        "line34": allowed,
    }
    ctx["collection"]["加计扣除"] = {
        "五项费用合计": base5, "其他相关费用实际": actual,
        "经限额调整后其他相关费用(第34行)": allowed,
        "第2行_自主合作集中": money(base5 + allowed),
    }
    return {"base_five_items": base5, "cap": cap, "allowed": allowed,
            "by_project": allowed_by_project}


@op("limit_other_20")
def _limit_other_20(case, rule, ctx):
    p = rule["params"]
    # 高企口径以「总研发费用」为分母；此处只做上限提示，不参与加计扣除计算
    hte_total = None
    if case.get("client", {}).get("hte_certificate"):
        base5 = ctx["_internal"].get("base5")
        if base5 is not None:
            hte_total = money(base5 / (1 - p["ratio"]))
    ctx["collection"]["高企认定"] = {
        "其他费用上限": p["ratio"], "计算基准": p["basis"],
        "按20%反推的研发总费用参考值": hte_total,
        "口径提示": "与加计扣除 10% 是两套独立上限；含在用建筑物折旧、装备调试费、知识产权摊销",
    }
    return {"hte_other_cap_ratio": p["ratio"], "reference_total": hte_total}


@op("entrust_domestic_80")
def _entrust_domestic_80(case, rule, ctx):
    p = rule["params"]
    raw = money(sum(num(pr.get("entrusted_domestic")) for pr in case.get("projects", [])))
    allowed = money(raw * p["ratio"])
    ctx["entrusted"]["domestic_raw"] = raw
    ctx["entrusted"]["domestic_allowed"] = allowed
    ctx["entrusted"]["line36"] = raw
    return {"raw": raw, "ratio": p["ratio"], "allowed": allowed}


@op("entrust_overseas_2_3")
def _entrust_overseas_2_3(case, rule, ctx):
    p = rule["params"]
    raw = money(sum(num(pr.get("entrusted_overseas")) for pr in case.get("projects", [])))
    after80 = money(raw * p["ratio"])
    qualifying = money(sum(num(pr.get("domestic_qualifying_rnd_total")) for pr in case.get("projects", [])))
    cap = money(qualifying * p["cap_ratio"])
    allowed = money(min(after80, cap)) if qualifying else after80
    ctx["entrusted"].update({
        "overseas_raw": raw, "overseas_after_80": after80,
        "domestic_qualifying_total": qualifying, "overseas_cap_2_3": cap,
        "overseas_allowed": allowed, "line38": allowed,
        "note": "第38行已是限额后金额，第40行不得再乘80%",
    })
    return {"raw": raw, "after_80": after80, "cap_2_3": cap, "allowed": allowed}


@op("a107012_line40")
def _a107012_line40(case, rule, ctx):
    base5 = ctx["_internal"].get("base5", 0)
    allowed_other = ctx["_internal"].get("allowed_other", 0)
    line2 = money(base5 + allowed_other)
    line36 = ctx["entrusted"].get("line36", 0)
    line38 = ctx["entrusted"].get("line38", 0)
    d80 = ctx["entrusted"].get("domestic_allowed", 0)
    line40 = money(line2 + d80 + line38)

    # 独立路径交叉校验：项目允许额 + 委托境内可计入 + 委托境外可计入
    alt = money(sum(ctx["_internal"].get("project_allowed", {}).values()) + d80 + line38)
    consistent = abs(alt - line40) < 0.02
    ctx["filing"]["a107012"] = {
        "line2": line2, "line28_其他相关费用实际": ctx["_internal"].get("actual_other", 0),
        "line34": allowed_other, "line36": line36, "line38": line38,
        "line40_年度研发费用小计": line40,
        "formula": rule["params"]["formula"],
        "cross_check_from_projects": alt, "consistent": consistent,
    }
    if not consistent:
        ctx["warnings"].append(f"A107012 第40行两条路径不一致：{line40} vs {alt}")
    return {"line2": line2, "line40": line40, "cross_check": alt, "consistent": consistent}


@op("amortization_cap")
def _amortization_cap(case, rule, ctx):
    p = rule["params"]
    items = []
    total_capitalized = 0.0
    total_amort = 0.0
    for pr in case.get("projects", []):
        if pr.get("expense_type") != "资本化":
            continue
        cap = pr.get("capitalization", {})
        amount = ctx["_internal"].get("project_allowed", {}).get(pr.get("id"), 0)
        years = num(cap.get("amort_years")) or 1
        months = num(cap.get("amort_months_in_year")) or 12
        amort = money(amount / years / 12 * months)
        items.append({"project": pr.get("id"), "capitalized": money(amount),
                      "amort_years": years, "months": months, "amortization_current": amort})
        total_capitalized = money(total_capitalized + amount)
        total_amort = money(total_amort + amort)
    ctx["accounting"] = {
        "capitalized_total": total_capitalized,
        "amortization_current": total_amort,
        "formula": p["formula"], "projects": items,
    }
    return {"capitalized": total_capitalized, "amortization_current": total_amort}


@op("superded_rate")
def _superded_rate(case, rule, ctx):
    p = rule["params"]
    q = case.get("client", {}).get("qualification")
    if q not in p.get("applies_to", []):
        return {"skipped": f"资格 {q} 不适用本规则"}
    if ctx["rate"].get("value") is not None:
        return {"skipped": "已有更高优先级的加计比例规则命中"}
    ctx["rate"] = {
        "value": p["rate"], "amortization_rate": p.get("amortization_rate"),
        "rule_id": rule["id"], "authority": rule["authority"],
        "qualification": q, "list_managed": p.get("list_managed", False),
        "capitalization_judge_by": p.get("capitalization_judge_by"),
    }
    return {"rate": p["rate"], "rule_id": rule["id"]}


@op("a107012_line51")
def _a107012_line51(case, rule, ctx):
    pa = ctx["_internal"].get("project_allowed", {})
    expensed_projects = money(sum(
        pa.get(pr.get("id"), 0) for pr in case.get("projects", [])
        if pr.get("expense_type") == "费用化" and pr.get("form") != "委托研发"
    ))
    d80 = ctx["entrusted"].get("domestic_allowed", 0)
    overseas = ctx["entrusted"].get("overseas_allowed", 0)
    expensed_total = money(expensed_projects + d80 + overseas)
    amort = ctx["accounting"].get("amortization_current", 0)
    base = money(expensed_total + amort)
    rate = ctx["rate"].get("value") or 1.0  # 历史年度/资格未匹配时局部兜底，避免全链中断
    line51 = money(base * rate)
    ctx["filing"]["a107012"].update({
        "expensed_total": expensed_total,
        "capitalized_total": ctx["accounting"].get("capitalized_total", 0),
        "amortization_current": amort,
        "line45_本年允许加计扣除研发费用合计": base,
        "line50_加计比例": rate,
        "line51_本年加计扣除总额": line51,
    })
    ctx["superdeduction"] = {"base": base, "rate": rate, "amount": line51,
                             "rule": rule["id"]}
    return {"expensed_total": expensed_total, "base": base, "rate": rate, "line51": line51}


@op("hte_ratio_band")
def _hte_ratio_band(case, rule, ctx):
    p = rule["params"]
    f = case.get("finance", {})
    rnd, sales = f.get("rnd_3y"), f.get("sales_3y")
    last = f.get("sales_last_year")
    if not rnd or not sales:
        return {"skipped": "非高企实例或未提供近三年数据"}
    ratio = ratio6(rnd / sales)
    if last is None:
        ctx["warnings"].append("未提供【最近一年销售收入】，无法按 R014 正确分档；切勿用近三年销售收入合计代替")
        return {"skipped": "缺最近一年销售收入"}
    band = next((b for b in p["bands"] if b["max"] is None or last <= b["max"]), p["bands"][-1])
    domestic = f.get("domestic_rnd_ratio")
    ctx["indicators"]["rnd_ratio"] = {
        "value": ratio, "band_field": p["band_field"], "band_basis": last,
        "band": band["label"], "required": band["required"],
        "pass": ratio >= band["required"],
        "domestic_ratio": domestic, "domestic_min": p["domestic_ratio_min"],
        "domestic_pass": (domestic is None or domestic >= p["domestic_ratio_min"]),
        "note": "分档依据为最近一年销售收入，不是近三年销售收入合计",
    }
    return {"ratio": ratio, "band": band["label"], "pass": ratio >= band["required"]}


@op("hte_income_60")
def _hte_income_60(case, rule, ctx):
    f = case.get("finance", {})
    hi, ti = f.get("hte_income"), f.get("total_income")
    if not hi or not ti:
        return {"skipped": "未提供高新收入/总收入"}
    v = ratio6(hi / ti)
    ctx["indicators"]["hte_income"] = {"value": v, "required": rule["params"]["threshold"],
                                        "pass": v >= rule["params"]["threshold"]}
    return {"value": v, "pass": v >= rule["params"]["threshold"]}


@op("hte_staff_10")
def _hte_staff_10(case, rule, ctx):
    p = rule["params"]
    s = case.get("staff", {})
    total, sci = s.get("total_avg"), s.get("sci_tech_avg")
    if not total or sci is None:
        return {"skipped": "未提供职工/科技人员月平均数"}
    v = ratio6(sci / total)
    days = s.get("sci_tech_days_min")
    days_ok = days is None or days >= p["days_min"]
    ctx["indicators"]["hte_staff"] = {"value": v, "required": p["threshold"],
                                       "pass": v >= p["threshold"],
                                       "days_min": p["days_min"], "days": days, "days_pass": days_ok}
    return {"value": v, "pass": v >= p["threshold"], "days_pass": days_ok}


@op("rate_choice")
def _rate_choice(case, rule, ctx):
    p = rule["params"]
    ti = case.get("finance", {}).get("taxable_income")
    if not ti:
        return {"skipped": "未提供应纳税所得额"}
    hte = money(ti * p["hte_rate"])
    small = money(ti * p["small_rate_param"])
    choice = "小微优惠" if small < hte else "高企15%"
    ctx["indicators"]["rate_choice"] = {
        "taxable_income": ti, "hte_15_tax": hte, "small_tax": small,
        "choose": choice, "stackable": p["stackable"],
        "note": "二者择一不得同时享受；研发加计扣除可叠加。档位以当年申报系统带出为准",
    }
    return {"choose": choice, "hte_tax": hte, "small_tax": small}


@op("filing_prepay_3")
def _filing_prepay_3(case, rule, ctx):
    p = rule["params"]
    ctx["filing"]["prepay"] = {
        "windows": p["windows"], "no_waiver": p["no_waiver"],
        "used": case.get("filing", {}).get("prepay_window_used"),
        "note": "未选择不作废，可在后续时点或汇缴统一享受",
    }
    return {"windows": len(p["windows"])}


@op("risk_threshold")
def _risk_threshold(case, rule, ctx):
    p = rule["params"]
    hits, evaluated = [], []
    a = ctx["filing"].get("a107012", {})
    total = a.get("line40_年度研发费用小计", 0)
    personnel_plus_direct = money(
        sum(num(pr.get("expenses", {}).get("personnel")) + num(pr.get("expenses", {}).get("direct_input"))
            for pr in case.get("projects", []))
    )
    structure = ratio6(personnel_plus_direct / total) if total else 0
    values = {
        "K1": structure,
        "K2": None,  # 缺上年度数据，不臆造
        "K3": ctx["superdeduction"].get("amount", 0),
        "K4": case.get("filing", {}).get("a107012_line51") if case.get("client", {}).get("hte_certificate") else None,
    }
    for ind in p["indicators"]:
        v = values.get(ind["id"])
        evaluated.append({"id": ind["id"], "name": ind["name"],
                          "value": v, "threshold": ind["threshold"],
                          "status": "数据不足" if v is None else "已评估"})
        if v is None:
            continue
        t = ind["threshold"]
        hit = (v >= t) if ind["cmp"] == ">=" else (v < t)
        if hit:
            hits.append({"id": ind["id"], "name": ind["name"], "value": v,
                         "threshold": t, "action": ind["action"],
                         "need_evidence": ind["need_evidence"],
                         "note": "命中≠违法，但须提前备证"})
    ctx["risk_hits"] = hits
    ctx["risk_evaluated"] = evaluated
    return {"evaluated": len(evaluated), "hits": len(hits)}


# ---------------------------------------------------------------- 引擎

def run(case, as_of=None, rules_doc=None):
    rules_doc = rules_doc or json.loads(RULES_PATH.read_text(encoding="utf-8"))
    as_of = as_of or case.get("as_of") or date.today().isoformat()
    active, expired = [], []
    for r in rules_doc["rules"]:
        (active if effective(r, as_of) else expired).append(r)
    active.sort(key=lambda r: -r.get("priority", 0))

    ctx = {
        "_internal": {},
        "admission": {"gates": []},
        "collection": {},
        "limits": {},
        "entrusted": {},
        "accounting": {},
        "rate": {"value": None},
        "filing": {},
        "indicators": {},
        "superdeduction": {},
        "risk_hits": [],
        "risk_evaluated": [],
        "warnings": [],
        "cross_scope_warnings": [],
        "evidence_gaps_ext": [],
    }
    trace = []
    for r in active:
        fn = OPS.get(r["op"])
        if fn is None:
            trace.append({"rule_id": r["id"], "op": r["op"], "status": "NO_OPERATOR"})
            continue
        try:
            out = fn(case, r, ctx)
            trace.append({
                "rule_id": r["id"], "op": r["op"], "title": r["title"],
                "priority": r.get("priority"), "scope": r.get("scope"),
                "authority": r["authority"], "source": r["source"],
                "output": out,
            })
        except Exception as e:  # 单条规则失败不阻断全链，但必须留痕
            trace.append({"rule_id": r["id"], "op": r["op"], "status": "ERROR", "error": str(e)})
            ctx["warnings"].append(f"规则 {r['id']} 执行失败：{e}")

    internal = ctx.pop("_internal")
    gaps = list(dict.fromkeys(internal.get("evidence_gaps", []) + ctx["evidence_gaps_ext"]))
    blocked = list(dict.fromkeys(internal.get("blocked", [])))
    eligible = not blocked and not gaps
    ctx["admission"].update({
        "eligible": eligible,
        "path": "A 高企" if case.get("client", {}).get("hte_certificate") else "B 非高企加计扣除",
        "blocked_by": blocked,
        "note": "证据缺口或准入闸门命中时结论为不可做；整改后能做须逐项补齐证据",
    })
    ctx["evidence_gaps"] = gaps
    ctx.pop("evidence_gaps_ext", None)
    if ctx["rate"]["value"] is None:
        ctx["warnings"].append("无适用的加计比例规则（可能是历史年度或资格未匹配）；1.0 仅为占位值，不得作为申报依据，请按所属年度政策文件核对")
        ctx["rate"]["value"] = 1.0

    return {
        "engine_version": ENGINE_VERSION,
        "case_id": case.get("case_id"),
        "as_of": as_of,
        "active_rule_count": len(active),
        "active_rules": [r["id"] for r in active],
        "expired_rules_excluded": [r["id"] for r in expired],
        **ctx,
        "trace": trace,
    }


# ---------------------------------------------------------------- 政策时效核验

# 官方核验信源映射：税务类文件 → 税务总局政策法规库（fgk）；财政类 → 财政部官网；高企认定 → 科技部/税务总局
_VERIFY_SOURCES = {
    "财税": "财政部/税务总局 fgk.chinatax.gov.cn + 财政部官网",
    "国科发火": "科技部/税务总局 fgk.chinatax.gov.cn",
    "国税": "fgk.chinatax.gov.cn 税务总局政策法规库",
    "税总": "fgk.chinatax.gov.cn 税务总局政策法规库",
    "国家税务总局公告": "fgk.chinatax.gov.cn 税务总局政策法规库",
    "税务总局": "fgk.chinatax.gov.cn 税务总局政策法规库",
    "财政部": "财政部官网 + fgk.chinatax.gov.cn",
    "企业所得税法": "国家法律法规数据库 flk.npc.gov.cn",
    "企业会计准则": "财政部会计准则委员会 kjs.mof.gov.cn",
    "A1070": "电子税务局当年表样（非规范性文件，以系统为准）",
    "表样": "电子税务局当年表样（非规范性文件，以系统为准）",
}


def _pick_source(authority):
    for k, s in _VERIFY_SOURCES.items():
        if k in authority:
            return s
    return "官方发布机关官网（税务总局/财政部/科技部）查证"


def verify(doc, as_of, due_only=False, checklist=False):
    today = as_of
    rules = doc["rules"]
    print("=" * 72)
    print(f"政策时效核验  as_of = {today}｜规则表共 {len(rules)} 条")
    print("信源：官方发布机关官网（税务总局政策法规库 fgk.chinatax.gov.cn、财政部、科技部）")
    print("=" * 72)

    # 分类：已到期 / 临期(90天内) / 现行(无到期) / 现行(有到期)
    overdue, due_soon, current_open, current_fixed = [], [], [], []
    for r in rules:
        et = r.get("effective_to")
        if not et:
            status = "never"
        elif len(et) >= 8:  # ISO 日期字符串比较即可
            if et < today:
                status = "overdue"
            elif et <= _add_days(today, 90):
                status = "due_soon"
            else:
                status = "current_fixed"
        else:
            status = "never"
        bucket = {
            "overdue": overdue, "due_soon": due_soon,
            "current_fixed": current_fixed, "never": current_open,
        }[status]
        bucket.append(r)

    print(f"\n[1] 已到期（effective_to < {today}）：{len(overdue)} 条")
    for r in overdue:
        print(f"    {r['id']} ⚠️ 到期 {r['effective_to']}｜{r['title']}｜文号：{r['authority']}")

    print(f"\n[2] 90天内临期：{len(due_soon)} 条")
    for r in due_soon:
        print(f"    {r['id']} 🔜 到期 {r['effective_to']}｜{r['title']}")

    print(f"\n[3] 现行（设定了有效期，未到期）：{len(current_fixed)} 条")
    for r in current_fixed:
        print(f"    {r['id']} 现行至 {r['effective_to']}｜{r['authority']}")

    print(f"\n[4] 现行（未设到期日，仍须核验现行性）：{len(current_open)} 条")
    for r in current_open:
        print(f"    {r['id']}｜{r['authority']}")

    # 去重文号核验清单
    print("\n" + "=" * 72)
    print("[5] 全部引用文号核验清单（去重，逐号核现行性）")
    print("=" * 72)
    seen = []
    for r in sorted(rules, key=lambda x: x["id"]):
        for w in _split_wenhao(r["authority"]):
            if w in seen:
                continue
            seen.append(w)
            print(f"    {w}")
            print(f"        ↳ 核定信源：{_pick_source(_ref_authority(r))}｜源自规则：{r['id']}")
    if checklist:
        return
    if due_only:
        print("\n(仅列到期/临期——已打印 [1][2])")
    print("\n说明：政策原文 > 源书；涉及税率/比例/金额/文号须回查官方原文。到期规则保留沿革，勿删除。")


def _add_days(iso, days):
    from datetime import timedelta
    return (date.fromisoformat(iso) + timedelta(days=days)).isoformat()


def _split_wenhao(authority):
    """从 authority 字段中切出可核验的文号片段"""
    parts = []
    for seg in re.split(r"[；;，,、/]+", authority):
        seg = seg.strip()
        if not seg:
            continue
        # 去掉"书p…"页码与规则说明，只留疑似文号
        if re.search(r"\d{4}", seg):
            parts.append(seg)
    if not parts:
        parts = [authority.strip()]
    return parts


def _ref_authority(r):
    # authority 过长时截断做信源匹配用（match 键用子串即可）
    return r.get("authority", "")


# ---------------------------------------------------------------- 高企账务诊断 AUDIT

AUDIT_DIMENSIONS = [
    {"id": "accounting", "label": "账务处理合规", "weight": 25},
    {"id": "collection", "label": "研发费用归集口径", "weight": 30},
    {"id": "hte_indicators", "label": "高企资格维持指标", "weight": 25},
    {"id": "tax_filing", "label": "税务申报合规", "weight": 15},
    {"id": "evidence", "label": "证据链完整", "weight": 5},
]

# 每维度的检查项：key -> (字段, 通过值, 通过时文字说明, 失败时整改建议)
_AUDIT_CHECKS = {
    "accounting": [
        ("monthly_bookkeeping", True, "按月及时记账，无长期挂账/账外经营", "账外经营/长期挂账须先并账规范，再谈研发归集"),
        ("book_voucher_consistent", True, "账证/账实相符", "抽查凭证，纠正账实不符项目"),
        ("rnd_subject_set", True, "设研发支出科目并按项目核算", "补设「研发支出」科目，费用化/资本化分设"),
        ("auxiliary_ledger_2021", True, "建2021版研发支出辅助账", "无辅助账不得加计（R001），须从当期起建账，不得事后补造"),
        ("hte_special_ledger", True, "高企另建认定专用辅助账（两套账）", "补建表7-8专用账，近三年分年按RD项目"),
        ("hte_special_audited", True, "高企专用账经中介专项审计", "安排有资质中介出具专项审计/鉴证"),
    ],
    "collection": [
        ("six_categories_clean", True, "按六类明细归集", "查补六类明细，剔除混入非研发费用"),
        ("mixed_post_allocated", True, "兼岗/共用按工时等合理分摊", "建立工时与领料分配表"),
        ("non_rnd_excluded", True, "非研发费用未误计入", "剔除纯管理/后勤费用"),
        ("special_income_offset", True, "特殊收入冲减当年研发", "补做下脚料/形成产品销售冲减"),
        ("gov_subsidy_treated", True, "不征税收入部分未加计", "财政性资金作不征税收入处理的部分不得加计"),
        ("other_limit_check", True, "其他相关费用按全部项目10%限额", "校正限额口径；高企20%与加计10%不得混用"),
        ("capitalization_justified", True, "资本化/费用化划分有据", "补齐资本化时点判断依据"),
        ("entrusted_contract_registered", True, "委托/合作合同科技部门登记", "补登记；境外委托按80%与2/3"),
    ],
    "hte_indicators": [
        ("ip_owned", True, "拥有有效知识产权", "补缴年费/增补知识产权"),
        ("ip_type_valid", True, "II类知识产权未重复使用", "核查II类仅用一次的规则"),
        ("field_in_eight", True, "属八大领域", "核实技术领域归属"),
    ],
    "tax_filing": [
        ("a107012_filed", True, "汇缴已填A107012", "补A107012填报"),
        ("line40_reconciled", True, "第40行勾稽正确", "校正40=2+36×80%+38，勿重复乘80%"),
        ("annual_report_submitted", True, "年报按时报送", "补报高企年度发展情况报表（两年未报取消资格）"),
        ("rates_consistent", True, "税率/加计叠加与申报一致", "核对15%、加计叠加未错用"),
    ],
    "evidence": [],  # 证据链按字段齐不齐单独累计
}

_EVIDENCE_EXPECTED = [
    "financial_statements", "subject_balance", "auxiliary_ledger",
    "project_archive", "staff_roster", "input_evidence",
    "income_evidence", "ip_cert", "filed_returns",
]


def audit(ac, as_of=None):
    """高企账务诊断：对一家既有（或拟认定）高企的账务质量与合规程度打分、出整改清单与承接结论。
    返回 dict：dimension_scores / total_score / verdict / risk_hits / rectifications / evidence_gaps。
    """
    as_of = as_of or ac.get("as_of") or date.today().isoformat()
    res = {
        "case_id": ac.get("audit_id"), "annual": {"year": ac.get("year"), "as_of": as_of},
        "client": ac.get("client", {}).get("name"),
        "dimension_scores": {}, "total_score": 0,
        "verdict": None, "verdict_color": None,
        "risk_hits": [], "rectifications": [], "evidence_gaps": [],
        "blocked_admission": [],
    }

    # 衔接运营引擎：若材料能支撑，复用 client_case 的资格指标判定（R014/R015/R016）
    hte = ac.get("hte_indicators", {})
    indicators = {}
    if hte.get("rnd_3y") and hte.get("sales_3y") and hte.get("sales_last_year"):
        ratio = ratio6(hte["rnd_3y"] / hte["sales_3y"]) if hte["sales_3y"] else 0
        last = hte["sales_last_year"]
        band = (0.05 if last <= 5e7 else 0.04 if last <= 2e8 else 0.03)
        indicators["rnd_ratio"] = {"value": ratio, "needed": band, "pass": ratio >= band,
                                   "note": "分档依据为最近一年销售收入"}
    if hte.get("hte_income") and hte.get("total_income"):
        inc = ratio6(hte["hte_income"] / hte["total_income"])
        indicators["hte_income"] = {"value": inc, "needed": 0.6, "pass": inc >= 0.6}
    if hte.get("sci_tech_avg") and hte.get("total_avg"):
        st = ratio6(hte["sci_tech_avg"] / hte["total_avg"])
        indicators["sci_staff"] = {"value": st, "needed": 0.1, "pass": st >= 0.1}
    set_total = 0.0
    for dim in AUDIT_DIMENSIONS:
        did = dim["id"]
        data = ac.get(did, {})
        if did == "evidence":
            ok_n = sum(1 for k in _EVIDENCE_EXPECTED if data.get(k))
            total_n = len(_EVIDENCE_EXPECTED)
            score = round(100.0 * ok_n / total_n, 1)
            missing = [k for k in _EVIDENCE_EXPECTED if not data.get(k)]
            for m in missing:
                res["evidence_gaps"].append(m)
        else:
            checks = _AUDIT_CHECKS.get(did, [])
            passed = 0
            for key, want, ok_desc, fix in checks:
                v = data.get(key)
                if v == want:
                    passed += 1
                else:
                    res["rectifications"].append({"dim": dim["label"], "check": ok_desc,
                                                  "fix": fix, "field": key})
            score = round(100.0 * passed / len(checks), 1) if checks else 0.0
        res["dimension_scores"][did] = {"label": dim["label"], "weight": dim["weight"],
                                        "score": score,
                                        "weighted": round(score * dim["weight"] / 100.0, 1)}
        set_total += score * dim["weight"] / 100.0
    res["total_score"] = round(set_total, 1)

    # 承接结论/分级
    cl = ac.get("client", {})
    if cl.get("industry_negative_list"):
        res["blocked_admission"].append("负面清单行业，不承接研发加计申报")
    if cl.get("collection_method") == "核定征收":
        res["blocked_admission"].append("核定征收不适用加计扣除")

    if res["total_score"] >= 85 and not res["blocked_admission"]:
        res["verdict"] = "合格（可正常承接加计/维持服务）"
        res["verdict_color"] = "green"
    elif res["total_score"] >= 60 and not res["blocked_admission"]:
        res["verdict"] = "需整改（有真实研发但账套/证据有缺口，整改后承接）"
        res["verdict_color"] = "yellow"
    else:
        res["verdict"] = "高风险（存在禁接情形或账务/证据严重不足，出风险提示函）"
        res["verdict_color"] = "red"

    # 风险命中：硬指标不过关
    for k, inf in indicators.items():
        if not inf["pass"]:
            res["risk_hits"].append({"indicator": k, "value": inf.get("value"),
                                     "needed": inf.get("needed"), "note": inf.get("note")})
    if hte.get("sci_tech_days_min") is not None and hte["sci_tech_days_min"] < 183:
        res["risk_hits"].append({"indicator": "sci_tech_days", "value": hte["sci_tech_days_min"],
                                 "needed": 183, "note": "兼/临人员累计实际工作须≥183天"})
    return res


def _print_dim(label, weight, score):
    bar = "█" * int(score / 10) + "░" * (10 - int(score / 10))
    print(f"  {label:<14} 权重{weight:<3} {score:5.1f}/100  {bar}")


def _audit_cli(path, as_of):
    ac = json.loads(Path(path).read_text(encoding="utf-8"))
    r = audit(ac, as_of)
    print("=" * 72)
    print(f"高企账务诊断｜{r['client'] or ac.get('audit_id')}｜年度 {r['annual']['year']}（as_of={r['annual']['as_of']}）")
    print("=" * 72)
    for d in AUDIT_DIMENSIONS:
        s = r["dimension_scores"][d["id"]]
        _print_dim(s["label"], s["weight"], s["score"])
    print("-" * 72)
    print(f"  综合得分：{r['total_score']}/100　结论：【{r['verdict']}】")
    if r["blocked_admission"]:
        print("  ⛔ 禁接情形：")
        for b in r["blocked_admission"]:
            print(f"      - {b}")
    if r["risk_hits"]:
        print("\n  ⚠️ 资格指标风险命中：")
        for h in r["risk_hits"]:
            print(f"      - {h['indicator']}: {h.get('value')}（需 {h.get('needed')}）｜{h.get('note')}")
    if r["evidence_gaps"]:
        print("\n  📄 材料缺口（让客户补）：")
        print(f"      {', '.join(r['evidence_gaps'])}")
    if r["rectifications"]:
        print("\n  🔧 整改清单：")
        for rec in r["rectifications"]:
            print(f"      [{rec['dim']}] {rec['check']} → {rec['fix']}")
    print("\n说明：诊断不替代专项审计；结论供承接与整改参考；涉及稽查转 tax-audit-response。")


def cli():
    ap = argparse.ArgumentParser(description="研发税务 CARE 引擎（规则驱动全链复算）")
    sub = ap.add_subparsers(dest="cmd")

    c = sub.add_parser("case", help="复算一个客户实例")
    c.add_argument("path")
    c.add_argument("--as-of", help="覆盖实例的 as_of，用于政策时效模拟")
    c.add_argument("--out", help="把结果 JSON 写到指定路径")
    c.add_argument("--compact", action="store_true", help="输出中省略 trace")

    r = sub.add_parser("rules", help="列出某时点的生效/失效规则")
    r.add_argument("--as-of", default=date.today().isoformat())

    v = sub.add_parser("verify", help="政策时效核验：抽取规则表引用的全部文号，按状态分类并给出官方核验信源")
    v.add_argument("--as-of", default=date.today().isoformat(), help="核验时点（默认今天）")
    v.add_argument("--due-only", action="store_true", help="只列已到期/临期规则（默认全量）")
    v.add_argument("--checklist", action="store_true",
                   help="只输出文号核验清单（不重复整条规则）")

    sub.add_parser("kernel", help="列出 12 条硬内核及其规则编号")
    sub.add_parser("selftest", help="内置快速自检")

    a = sub.add_parser("audit", help="高企账务质量/合规诊断：打分、整改清单、承接结论")
    a.add_argument("path", help="audit_case 实例 JSON 路径")
    a.add_argument("--as-of", help="覆盖实例 as_of（政策时点）")
    a.add_argument("--out", help="把诊断结果 JSON 写到指定路径")

    args = ap.parse_args()
    doc = json.loads(RULES_PATH.read_text(encoding="utf-8"))

    if args.cmd == "verify":
        verify(doc, args.as_of, due_only=args.due_only, checklist=args.checklist)
        sys.exit(0)
    elif args.cmd == "audit":
        r = audit(json.loads(Path(args.path).read_text(encoding="utf-8")), args.as_of)
        if args.out:
            Path(args.out).write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"WROTE {args.out} | score={r['total_score']} | verdict={r['verdict']}")
        else:
            _audit_cli(args.path, args.as_of)
        sys.exit(0)
    elif args.cmd == "case":
        case = json.loads(Path(args.path).read_text(encoding="utf-8"))
        res = run(case, args.as_of, doc)
        if args.compact:
            res.pop("trace", None)
        text = json.dumps(res, ensure_ascii=False, indent=2)
        if args.out:
            Path(args.out).write_text(text, encoding="utf-8")
            print(f"WROTE {args.out} | active={res['active_rule_count']} | "
                  f"expired={len(res['expired_rules_excluded'])} | "
                  f"eligible={res['admission']['eligible']} | "
                  f"line51={res['filing'].get('a107012', {}).get('line51_本年加计扣除总额')}")
        else:
            print(text)
    elif args.cmd == "rules":
        act = [r for r in doc["rules"] if effective(r, args.as_of)]
        exp = [r for r in doc["rules"] if not effective(r, args.as_of)]
        print(f"as_of = {args.as_of}｜生效 {len(act)} 条｜失效 {len(exp)} 条")
        for r in sorted(act, key=lambda x: -x["priority"]):
            print(f"  {r['id']}  P{r['priority']:<4} {r['title']}")
        if exp:
            print("失效（保留沿革）：", ", ".join(r["id"] for r in exp))
    elif args.cmd == "kernel":
        ks = {}
        for r in doc["rules"]:
            k = r.get("kernel_id")
            if k:
                ks.setdefault(k, []).append(r["id"])
        for k in sorted(ks):
            print(f"  硬内核 #{k:<2} → {', '.join(ks[k])}")
    elif args.cmd == "selftest":
        case = json.loads((ROOT / "schema" / "cases" / "example_4_1.json").read_text(encoding="utf-8"))
        res = run(case, None, doc)
        a = res["filing"]["a107012"]
        checks = [
            ("限额 294,444.44", res["limits"]["other_related"]["cap"], 294444.44),
            ("A 分摊 252,380.95", res["limits"]["other_related"]["by_project"]["A"], 252380.95),
            ("B 分摊 42,063.49", res["limits"]["other_related"]["by_project"]["B"], 42063.49),
            ("第40行 3,744,444.44", a["line40_年度研发费用小计"], 3744444.44),
            ("本年摊销 49,603.17", res["accounting"]["amortization_current"], 49603.17),
            ("加计基数 2,801,984.12", a["line45_本年允许加计扣除研发费用合计"], 2801984.12),
            ("第51行 2,801,984.12", a["line51_本年加计扣除总额"], 2801984.12),
            ("两路径一致", a["consistent"], True),
        ]
        ok = True
        for name, got, want in checks:
            good = (got == want) if isinstance(want, bool) else (abs(got - want) < 0.01)
            ok &= good
            print(f"  {'PASS' if good else 'FAIL'}  {name}: {got}")
        print("SELFTEST =", "OK" if ok else "FAILED")
        sys.exit(0 if ok else 1)
    else:
        ap.print_help()


if __name__ == "__main__":
    cli()
