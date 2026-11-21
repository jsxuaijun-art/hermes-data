#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
gxrd_engine.py — 高企 + 研发费加计扣除「乙方服务」决策与计算引擎
=====================================================================
框架思想（区别于纯知识库 / 线性查表）：
  ① 决策优先(decision-first)　：从客户情境画像 → 输出适用结论，而不是人肉拼文档
  ② 证据驱动(evidence-driven) ：准入结论由「证据完备度」反推，而非先判定再找材料
  ③ 实例持久(instance)        ：client-profile + year 组成可跨会话续作的作业实例
  ④ 规则显式(rules)           ：20%/10%、40行公式、80%/2/3、分档依据全部可执行校验
  ⑤ 政策时效(policy expiry)   ：每条政策带 effective/expiry，可自动失效

用法：
  python gxrd_engine.py decide  --profile <client.json | inline-json>
  python gxrd_engine.py calc    --year 2026 --all <json>
  python gxrd_engine.py policy  [--asof 2026-12-31]
  python gxrd_engine.py selfcheck
  python gxrd_engine.py json-example

依赖：仅 Python 3 标准库。税率/比例/表样以电子税务局当年带出为准，本脚本为测算口径。
"""
import argparse, json, sys, datetime

# ============================================================
# 政策时效库（policy registry）
#   每条：id / 名称 / effective / expiry(None=长期) / authority / 摘要
#   effective/expiry 为 'YYYY-MM-DD'；不写死现行税率档位，只锁大框架+文号+生效窗
# ============================================================
POLICIES = [
    {"id":"P119","name":"财税〔2015〕119号 完善加计扣除","effective":"2016-01-01","expiry":None,
     "authority":"财政部 税务总局","summary":"适用范围、6类负面清单行业、7类不适用活动、核算要求、争议鉴定"},
    {"id":"P97","name":"总局公告2015年第97号 归集细化","effective":"2016-01-01","expiry":None,
     "authority":"国家税务总局","summary":"研发人员范围、多用途费用按合理方法分配、辅助账样式、留存备查；其他相关费用限额旧口径(逐项目)"},
    {"id":"P40","name":"总局公告2017年第40号 归集6类","effective":"2017-01-01","expiry":None,
     "authority":"国家税务总局","summary":"归集范围6类细目、资本化时点、失败研发费可加计"},
    {"id":"P64","name":"财税〔2018〕64号 委托境外","effective":"2018-01-01","expiry":None,
     "authority":"财政部 税务总局","summary":"取消委托境外研发不得加计限制；委托境外80%且≤境内2/3"},
    {"id":"P28","name":"总局公告2021年第28号 简化+统一限额","effective":"2021-01-01","expiry":None,
     "authority":"国家税务总局","summary":"可自行设计简化版辅助账；其他相关费用限额按全部项目统一计算(不再逐项目)；资本化项目形成资产年度统一纳入"},
    {"id":"P7","name":"财政部 税务总局公告2023年第7号 全行业100%","effective":"2023-01-01","expiry":None,
     "authority":"财政部 税务总局","summary":"2023.1.1起全行业统一100%：费用化×100%加计，无形资产按成本200%摊销"},
    {"id":"P44","name":"四部门公告2023年第44号 集成电路/工业母机120%","effective":"2023-01-01","expiry":"2027-12-31",
     "authority":"财政部等四部门","summary":"集成电路/工业母机120%加计、220%摊销；清单管理；资本化按摊销时点判断"},
    {"id":"P11","name":"总局 财政部公告2023年第11号 预缴三时点","effective":"2023-01-01","expiry":None,
     "authority":"国家税务总局 财政部","summary":"7月/10月/汇缴三时点享受；未选择可在后续时点统一享受"},
    {"id":"P32","name":"公告2022年第32号 企业出资基础研究","effective":"2022-01-01","expiry":None,
     "authority":"财政部 税务总局","summary":"出资非营利科研机构/高校/政府性自然科学基金用于基础研究，据实扣除并100%加计；接收方该收入免税"},
    {"id":"P98","name":"国税函〔2009〕98号 亏损结转","effective":"2009-01-01","expiry":None,
     "authority":"国家税务总局","summary":"加计形成/扩大亏损可结转(一般5年；高企10年-财税〔2018〕76号)"},
    {"id":"P23","name":"总局公告2018年第23号 备查制","effective":"2018-01-01","expiry":None,
     "authority":"国家税务总局","summary":"自行判别、申报享受、资料留存备查，无须事前备案"},
    {"id":"HTE32","name":"国科发火〔2016〕32号 高企认定办法","effective":"2016-01-01","expiry":None,
     "authority":"科技部 财政部 税务总局","summary":"认定条件、程序、监督管理、15%优惠"},
    {"id":"HTE195","name":"国科发火〔2016〕195号 工作指引","effective":"2016-01-01","expiry":None,
     "authority":"科技部 财政部 税务总局","summary":"研发费占比口径、科技人员界定、创新能力评价100分>70、申请材料"},
    {"id":"HTE76","name":"财税〔2018〕76号 高企亏损结转10年","effective":"2018-01-01","expiry":None,
     "authority":"财政部 税务总局","summary":"高企亏损结转10年(一般5年)"},
    {"id":"HTE63","name":"国科发政字〔2000〕63号 技术合同登记","effective":"2000-01-01","expiry":None,
     "authority":"科技部等","summary":"未登记技术合同不得享受有关税收优惠(委托/合作研发须登记)"},
    {"id":"HTE211","name":"国科发政〔2017〕211号 异议鉴定","effective":"2017-01-01","expiry":None,
     "authority":"科技部 财政部 税务总局","summary":"税务部门对研发项目有异议，转请科技部门鉴定"},
]

def policy_active(p, asof):
    a = datetime.date.fromisoformat(asof)
    if p["effective"] and a < datetime.date.fromisoformat(p["effective"]): return False
    if p["expiry"] and a > datetime.date.fromisoformat(p["expiry"]): return False
    return True

def cmd_policy(args):
    asof = args.asof or datetime.date.today().strftime("%Y-%m-%d")
    rows = [p for p in POLICIES if policy_active(p, asof)]
    print(f"现行有效政策（as of {asof}）共 {len(rows)} 条：")
    for p in rows:
        exp = f"到期 {p['expiry']}" if p["expiry"] else "长期"
        print(f"  [{p['id']}] {p['name']}  [{exp}]  → {p['summary']}")
    expired = [p["id"] for p in POLICIES if not policy_active(p, asof)]
    if expired:
        print(f"\n已失效/未生效（自动排除）：{', '.join(expired)}")
        print("  ⚠️ P44(120%) 若在 2028 年查询即自动失效——政策时效库按日期裁决，不靠 TODO。")

# ============================================================
# 固有常量（口径 — 用函数而非散落散文，便于脚本校验）
# ============================================================
def other_limit(base_five, actual):
    """其他相关费用限额：2021年度起按全部项目统一计算
       限额 = 前五项之和 ×10%/(1−10%)；可加计 = min(实际, 限额)
       实际若未给，只返回限额。"""
    lim = base_five * 0.10 / (1 - 0.10)
    allowed = min(actual, lim) if actual is not None else None
    return {"limit": lim, "allowed": allowed,
            "excess": (actual - lim) if (actual is not None and actual > lim) else 0.0}

def entrust_ext(domestic, overseas=0.0, domestic_total=None):
    """委托研发：境内×80%；境外×80%且≤境内符合条件研发费×2/3。"""
    domestic_total = domestic_total if domestic_total is not None else domestic
    d = domestic * 0.80
    cap = domestic_total * 2/3
    o = min(overseas * 0.80, cap)
    return {"domestic_80": d, "overseas_80": overseas*0.80, "o_cap": cap,
            "overseas_allowed": o, "total": d + o}

def hte_tier(last_year_sales):
    """高企研发费占比分档依据=最近一年销售收入。返回(要求%,档位文案)。"""
    if last_year_sales <= 50_000_000: return 5.0, "最近一年销售收入 ≤ 5000万"
    if last_year_sales <= 200_000_000: return 4.0, "5000万 < 最近一年销售收入 ≤ 2亿"
    return 3.0, "最近一年销售收入 > 2亿"

# ============================================================
# 决策模型：decide
#   输入 client-profile（dict）；输出 适用结论 + 路径 + 证据缺口 + 红线
# ============================================================
NEGATIVE_BRANCHES = ["住宿和餐饮","批发和零售","房地产","租赁和商务服务","娱乐业","烟草制造"]

def cmd_decide(args):
    raw = args.profile.strip()
    try:
        p = json.loads(raw) if raw.startswith("{") else json.load(open(raw, encoding="utf-8"))
    except Exception as e:
        print(f"读取 profile 失败：{e}"); return
    # 兼容两种形状：①顶层字典（快速 inline）②客户作业实例模板（字段在 profile 下，meta 带标志）
    if "profile" in p and isinstance(p["profile"], dict):
        p = {**p["meta"], **p["profile"]}

    out = {"profile": p, "conclusion": None, "path": None, "gates": [], "evidence_gaps": [], "redlines": []}

    # G1 主体
    if p.get("collection_method", "查账") != "查账":
        out["conclusion"] = "🔴 不做：核定征收不适用加计扣除（先规范建账、申请改查账）"
        out["gates"].append({"gate":"主体","pass":False,"reason":"非查账征收"})
    else:
        out["gates"].append({"gate":"主体","pass":True})

    # G2 行业（负面清单 + 兼营公式）
    industry = p.get("industry", "")
    is_neg = any(b in industry for b in NEGATIVE_BRANCHES)
    if is_neg:
        # 兼营判定：该业务收入 ÷ (收入总额−不征税收入−投资收益) > 50%
        rnd_revenue = p.get("neg_revenue", 0.0)
        total = p.get("total_revenue", 0.0)
        nt = p.get("nontax_income", 0.0); inv = p.get("investment_income", 0.0)
        denom = total - nt - inv
        ratio = (rnd_revenue / denom) if denom else 0.0
        if ratio > 0.50:
            out["conclusion"] = "🔴 不做：负面清单行业主营业务占比超50%，不得加计"
            out["gates"].append({"gate":"行业","pass":False,"reason":f"兼营占比{ratio:.0%}>50%"})
        else:
            out["gates"].append({"gate":"行业","pass":True,"note":f"兼营占比{ratio:.0%}≤50%，非负面清单主导"})
    else:
        out["gates"].append({"gate":"行业","pass":True})

    # G3 活动（7类不适用活动反列举）
    if p.get("negative_activity"):
        out["conclusion"] = "🔴 不做/重划：活动属7类不适用（常规升级/直接应用成果/售后支持/简单改变/市场调查/常规质检/人文社科）"
        out["gates"].append({"gate":"活动","pass":False})
    else:
        out["gates"].append({"gate":"活动","pass":True})

    # G4 证据链（evidence-driven：准入由证据完备度反推）
    ev = p.get("evidence", {})
    gaps = []
    if not ev.get("lixiang"): gaps.append("研发项目立项书/决议/可行性报告")
    if not ev.get("ledger"):   gaps.append("研发支出辅助账（立项时设账，不得事后补）")
    if not ev.get("attendance"): gaps.append("研发人员名单 + 工时记录（混岗须分摊）")
    if not ev.get("materials"): gaps.append("领料单/出库单 + 设备使用记录（与生产共用须分摊）")
    out["evidence_gaps"] = gaps

    # 结论
    pass_all = all(g.get("pass") for g in out["gates"])
    has_hte = p.get("has_hte_cert", False)
    if pass_all and not gaps:
        out["path"] = "A 高企客户" if has_hte else "B 非高企加计客户"
        out["conclusion"] = "✅ 可直接做"
    elif pass_all and gaps:
        out["path"] = "A 高企客户" if has_hte else "B 非高企加计客户"
        out["conclusion"] = "🟡 整改后做（存量规范：补立项/内控，从当期起设账，历史期不追补辅助账）"
    else:
        out["conclusion"] = out["conclusion"] or "🔴 不做（见 gates）"

    # 特殊主体
    if p.get("is_ic_machine"): out["redlines"].append("集成电路/工业母机 → 120%加计/220%摊销（P44，2023-2027，清单管理）")
    if p.get("is_tech_sme"):   out["redlines"].append("科技型中小企业 → 100%（需入库登记编号）")
    if p.get("has_hte_cert"):  out["redlines"].append("高企客户：15%与小微择一，加计可叠加；两套账（加计辅助账 ≠ 高企认定专用辅助账）")

    print("========== 准入决策路由 ==========")
    print(f"结论   ：{out['conclusion']}")
    print(f"路径   ：{out['path']}")
    for g in out["gates"]:
        print(f"  关卡  ：{g['gate']} → {'✅' if g.get('pass') else '❌'} {g.get('reason','')} {g.get('note','')}")
    if out["evidence_gaps"]:
        print("证据缺口（先补这些，验证证据完备度后倒推结论）：")
        for g in out["evidence_gaps"]: print(f"   - {g}")
    else:
        print("证据链：齐全（立项/辅助账/工时/领料均具备）")
    for r in out["redlines"]: print(f"   ⚠️ {r}")
    return out

# ============================================================
# 计算管道：calc（一次输入出全链）
#   输入 json:
#     { "year":2026, "ratio_type":"100", or "120",
#       "projects":[{"name":"A","base_five":1700000,"other_actual":300000}, ...],
#       "entrust":{"domestic":700000,"overseas":300000,"domestic_total":...},
#       "capital_assets":{"B":992063.49},  # 本年形成无形资产的资本化额(税前口径)
#       "amort_months":6  # 本年摊销月数(月/12)
#     }
# ============================================================
def cmd_calc(args):
    raw = args.json_text.strip()
    try:
        d = json.loads(raw) if raw.startswith("{") else json.load(open(raw, encoding="utf-8"))
    except Exception as e:
        print(f"读取输入失败：{e}"); print(__doc__); return

    year = d.get("year", datetime.date.today().year)
    rtype = str(d.get("ratio_type", "100")).replace("%","")
    rate = 1.20 if rtype in ("120","1.2") else 1.00
    projects = d.get("projects", [])

    # ① 各项目前五项合计 + 其他实际
    sum_base = sum(p.get("base_five", 0) for p in projects)
    sum_other_actual = sum(p.get("other_actual", 0) for p in projects)
    olim = other_limit(sum_base, sum_other_actual)
    # 分摊（按各项目实际发生数占比）；单值时全额给该项目的口径
    total_other_actual = sum(p.get("other_actual",0) for p in projects)
    allocated = {}
    if total_other_actual and olim["allowed"] is not None:
        for p in projects:
            share = olim["allowed"] * p.get("other_actual",0)/total_other_actual
            allocated[p.get("name", p.get("base_five"))] = share

    # ② 委托研发
    ent = d.get("entrust", {}) or {}
    ent_r = entrust_ext(ent.get("domestic",0), ent.get("overseas",0), ent.get("domestic_total"))

    # ③ 年度研发费用小计 & A107012 40行
    year_rnd = sum_base + (olim["allowed"] or 0) + ent_r["total"]
    row2 = sum_base + (olim["allowed"] or 0)          # 自主+合作+集中(不含委托)
    row36_80 = ent_r["domestic_80"]                    # 委托境内 80%
    row38 = ent_r["overseas_allowed"]                   # 允许加计的委托境外(经2/3)
    a107012_40 = row2 + row36_80 + row38               # = 2 + 36×80% + 38

    # ④ 资本化/费用化拆分 + 摊销
    #    例4-1 精髓：40行=年度研发费用小计(含当年新资本化 B=992,063.49)，
    #    但当年「允许加计的」只含费用化 + 本年形成无形资产的摊销额(正常100%)，
    #    资本化未摊销部分留以后年度。故允许扣除合计 ≠ 40行。
    cap_new_amount = d.get("cap_new", 0.0)   # 本年形成无形资产的资本化成本(加计口径)
    expensed = a107012_40 - cap_new_amount   # 费用化部分
    # 本年正常(100%)摊销：cap_new ÷ 摊销年限 × (本年已摊销月数/12)
    years = d.get("amort_years", 10)
    amort_norm = cap_new_amount / years * (d.get("amort_months", 12) / 12.0)
    # 允许扣除研发费用合计 = 费用化 + 本年摊销（200%/220% 通过加计比例 ×rate 体现）
    allowed_total = expensed + amort_norm

    # ⑤ 加计（= 允许扣除合计 × 加计比例；120%企业×1.2）
    super_total = allowed_total * rate

    print("========== 全链计算（A107012 口径） ==========")
    print(f"{year} 年度 · 加计比例 {rate*100:.0f}% · 项目数 {len(projects)}")
    print(f"① 前五项合计 {sum_base:,.2f}；其他相关费用实际发生 {sum_other_actual:,.2f}")
    print(f"   其他相关费用限额 = {sum_base:,.2f}×10%/(1-10%) = {olim['limit']:,.2f}")
    print(f"   可加计其他费用 = {olim['allowed']:,.2f}；超限额调增 = {olim['excess']:,.2f}")
    if allocated:
        print("   按各项目实发占比分摊：")
        for k,v in allocated.items(): print(f"     {k}: {v:,.2f}")
    print(f"② 委托研发：境内 {ent_r['domestic_80']:,.2f}(80%)；境外 {ent_r['overseas_80']:,.2f}(80%) 受限 {ent_r['o_cap']:,.2f}(2/3) → 计入 {ent_r['overseas_allowed']:,.2f}")
    print(f"③ 【A107012 40行】年度研发费用小计 = 2({row2:,.2f}) + 36×80%({row36_80:,.2f}) + 38({row38:,.2f}) = {a107012_40:,.2f}")
    print(f"④ 本年费用化 = {expensed:,.2f}；形成无形资产摊销额(正常) = {amort_norm:,.2f}")
    print(f"   允许扣除研发费用合计 = 费用化 + 摊销 = {allowed_total:,.2f}（资本化未摊销部分留以后年度）")
    print(f"⑤ 本年加计扣除总额 = {allowed_total:,.2f} × {rate*100:.0f}% = {super_total:,.2f}")
    print("依据：财税〔2015〕119号 / 2017年第40号 / 总局公告2021年第28号(统一限额) / 公告2023年第7号(P7) / 2023年第44号(P44 120%)")
    return {"year":year,"rate":rate,"row2":row2,"row36_80":row36_80,"row38":row38,
            "a107012_40":a107012_40,"super_total":super_total,"other_limit":olim,
            "entrust":ent_r}

# ============================================================
def cmd_json_example(args):
    print(json.dumps({
      "decide": {
        "collection_method":"查账","industry":"制造业-专用设备","has_hte_cert":True,
        "negative_activity":False,"evidence":{"lixiang":True,"ledger":True,"attendance":True,"materials":True},
        "is_ic_machine":False,"is_tech_sme":False
      },
      "calc": {
        "year":2026,"ratio_type":"100",
        "projects":[{"name":"A","base_five":1700000,"other_actual":300000},
                    {"name":"B","base_five":950000,"other_actual":50000}],
        "entrust":{"domestic":700000,"overseas":300000}
      }
    }, ensure_ascii=False, indent=2))

# ============================================================
# 回归自检：12条硬内核 + 例4-1 + 3个回归锚点
# ============================================================
def cmd_selfcheck(args):
    ok = True
    def chk(name, cond, detail=""):
        nonlocal ok
        print(f"  {'✅' if cond else '❌'} {name} {detail}")
        ok = ok and cond
    print("===== 回归自检（黄金测试集） =====")

    # 锚点1：例4-1 other_limit
    r = other_limit(2650000, 350000)
    chk("锚点1 其他费用限额=294,444.44", abs(r["limit"]-294444.44)<1, f"→ {r['limit']:,.2f}")
    chk("      超限额调增=55,555.56", abs(r["excess"]-55555.56)<1, f"→ {r['excess']:,.2f}")
    # 锚点2：40行 = 2 + 36×80% + 38（境外不重复乘80%）
    ent = entrust_ext(700000, 300000, 700000)
    row2 = 1700000+950000 + min(350000, other_limit(2650000,350000)["limit"])
    row40 = row2 + ent["domestic_80"] + ent["overseas_allowed"]
    exp_40 = 1700000+950000 + 294444.44 + 560000 + 240000
    chk("锚点2 A107012 40行=3,744,444.44", abs(row40-exp_40)<1.5, f"→ {row40:,.2f}")
    # 例4-1 加计总额锚点：费用化 2,752,380.95 + 半年摊销 49,603.17 = 2,801,984.12
    expensed = row40 - 992063.49
    amort_norm = 992063.49/10*(6/12)
    allowed = expensed + amort_norm
    chk("例4-1 允许扣除合计=2,801,984.12", abs(allowed-2801984.12)<1, f"→ {allowed:,.2f}")
    chk("      费用化=2,752,380.95 & 摊销=49,603.17",
        abs(expensed-2752380.95)<1 and abs(amort_norm-49603.17)<1,
        f"→ {expensed:,.2f} / {amort_norm:,.2f}")
    # 锚点3：分档按最近一年
    need,_ = hte_tier(30_000_000)
    chk("锚点3 最近一年3000万→要求5%", need==5.0, f"→ 要求{need:.0f}%（非按三年合计判4%）")
    need2,_ = hte_tier(80_000_000)
    chk("      最近一年8000万→要求4%", need2==4.0, f"→ 要求{need2:.0f}%")

    # 政策时效：2028年 P44 自动失效
    p44_active_2027 = any(p["id"]=="P44" and policy_active(p,"2027-12-31") for p in POLICIES)
    p44_active_2028 = any(p["id"]=="P44" and policy_active(p,"2028-01-01") for p in POLICIES)
    chk("政策时效：P44 2027年在册 / 2028年自动失效", p44_active_2027 and not p44_active_2028)

    print("\n结果：" + ("全部通过 ✅" if ok else "存在失败 ❌"))
    return 0 if ok else 1

CMDS = {"decide":cmd_decide,"calc":cmd_calc,"policy":cmd_policy,"selfcheck":cmd_selfcheck,"json-example":cmd_json_example}

def main():
    ap = argparse.ArgumentParser(description="gxrd_engine")
    ap.add_argument("cmd", choices=list(CMDS))
    ap.add_argument("--profile", default="")
    ap.add_argument("--json-text", default="")
    ap.add_argument("--asof", default="")
    a = ap.parse_args()
    if a.cmd == "calc" and not a.json_text:
        print("calc 需要 --json-text <json> 或 <文件路径>"); return 2
    if a.cmd == "decide" and not a.profile:
        print("decide 需要 --profile <inline-json> 或 <文件路径>"); return 2
    CMDS[a.cmd](a)
    return 0

if __name__ == "__main__":
    sys.exit(main())
