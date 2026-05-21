#!/usr/bin/env python3
"""
企业利润计算器 - 苏州盈信企业管理有限公司
适用于小微企业利润核算，支持增值税计算
"""

import json
from datetime import datetime

def calculate_profit():
    """企业利润计算主程序"""
    print("=" * 50)
    print("  企业利润计算器")
    print("  苏州盈信企业管理有限公司")
    print("=" * 50)

    # ========== 收入 ==========
    print("\n【收入信息】")
    revenue = float(input("请输入本期营业收入（元）: "))
    other_income = float(input("请输入其他业务收入（元，无则输0）: "))
    total_revenue = revenue + other_income

    # ========== 成本 ==========
    print("\n【成本信息】")
    cost = float(input("请输入营业成本（元）: "))

    # ========== 费用 ==========
    print("\n【费用信息】")
    salary = float(input("请输入员工工资（元，无则输0）: "))
    rent = float(input("请输入房租/物业费（元，无则输0）: "))
    utilities = float(input("请输入水电网费（元，无则输0）: "))
    office = float(input("请输入办公费用（元，无则输0）: "))
    travel = float(input("请输入差旅费（元，无则输0）: "))
    other_expense = float(input("请输入其他费用（元，无则输0）: "))
    total_expenses = salary + rent + utilities + office + travel + other_expense
    total_cost = cost + total_expenses

    # ========== 税金 ==========
    print("\n【增值税信息】")
    print("-" * 40)
    print("小规模纳税人适用（2026年政策）：")
    print("  月销售额 ≤ 10万（季度30万）：免征增值税")
    print("  月销售额 > 10万：适用1%征收率")
    print("  （本政策有效期至2027年12月31日）")
    print("-" * 40)

    is_small_scale = input("是否为小规模纳税人？(y/n，默认y): ").strip().lower() or "y"

    if is_small_scale == "y":
        if total_revenue <= 100000:
            vat_rate = 0
            vat_desc = "免税（月销售额≤10万）"
        else:
            vat_rate = 0.01
            vat_desc = "1% 征收率（有效期至2027.12.31）"
    else:
        vat_rate = float(input("请输入增值税税率（如一般纳税人13%输13）: ")) / 100
        vat_desc = f"{vat_rate*100:.0f}% 税率"

    vat = total_revenue * vat_rate
    city_tax = vat * 0.05
    edu_tax = vat * 0.03
    local_edu_tax = vat * 0.02
    surcharge = city_tax + edu_tax + local_edu_tax

    # ========== 企业所得税 ==========
    print("\n【企业所得税信息】")
    print("-" * 40)
    print("小型微利企业（2026年政策）：")
    print("  年应纳税所得额 ≤ 300万：实际税率 5%")
    print("  年应纳税所得额 > 300万：适用 25%")
    print("  （5%优惠税率有效期至2027年12月31日）")
    print("-" * 40)

    taxable_income = total_revenue - (total_cost + vat + surcharge)

    if taxable_income <= 0:
        corporate_tax = 0
        tax_desc = "亏损，无需缴纳"
    elif taxable_income <= 3000000:
        corporate_tax = taxable_income * 0.05
        tax_desc = "小型微利企业优惠税率 5%（有效期至2027.12.31）"
    else:
        corporate_tax = taxable_income * 0.25
        tax_desc = "一般税率 25%"

    net_profit = taxable_income - corporate_tax

    # ========== 输出结果 ==========
    print("\n\n" + "=" * 50)
    print("              利润计算报告")
    print(f"  生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)

    print(f"\n{'项目':<25} {'金额（元）':>15}")
    print("-" * 42)
    print(f"{'一、营业收入':<25} {total_revenue:>15,.2f}")
    print(f"{'二、减：营业成本':<25} {cost:>15,.2f}")
    print(f"{'三、减：期间费用':<25} {total_expenses:>15,.2f}")
    print(f"   {'- 工资':<23} {salary:>15,.2f}")
    print(f"   {'- 房租':<23} {rent:>15,.2f}")
    print(f"   {'- 水电网':<23} {utilities:>15,.2f}")
    print(f"   {'- 办公费':<23} {office:>15,.2f}")
    print(f"   {'- 差旅费':<23} {travel:>15,.2f}")
    print(f"   {'- 其他费用':<23} {other_expense:>15,.2f}")
    print(f"{'四、增值税':<25} {vat:>15,.2f}")
    print(f"   {'（' + vat_desc + '）':<23} {'':>15}")
    print(f"{'五、附加税':<25} {surcharge:>15,.2f}")
    print(f"   {'- 城建税(5%)':<23} {city_tax:>15,.2f}")
    print(f"   {'- 教育费附加(3%)':<23} {edu_tax:>15,.2f}")
    print(f"   {'- 地方教育费附加(2%)':<23} {local_edu_tax:>15,.2f}")
    print("-" * 42)
    print(f"{'六、利润总额':<25} {taxable_income:>15,.2f}")
    print(f"{'七、企业所得税':<25} {corporate_tax:>15,.2f}")
    print(f"   {'（' + tax_desc + '）':<23} {'':>15}")
    print("=" * 42)
    print(f"{'★ 净利润':<25} {net_profit:>15,.2f}")
    print("=" * 42)

    print(f"\n{'【财务指标分析】':^42}")
    rev = total_revenue if total_revenue else 1
    print(f"{'毛利率':<25} {(total_revenue - cost) / rev * 100:>14.1f}%")
    print(f"{'净利率':<25} {net_profit / rev * 100:>14.1f}%")
    print(f"{'费用收入比':<25} {total_expenses / rev * 100:>14.1f}%")
    tot_tax = vat + surcharge + corporate_tax
    print(f"{'综合税负率':<25} {tot_tax / rev * 100:>14.1f}%")

    result = {
        "生成时间": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "营业收入": total_revenue,
        "营业成本": cost,
        "期间费用": total_expenses,
        "增值税": vat,
        "附加税": surcharge,
        "利润总额": taxable_income,
        "企业所得税": corporate_tax,
        "净利润": net_profit,
        "毛利率%": round((total_revenue - cost) / rev * 100, 2),
        "净利率%": round(net_profit / rev * 100, 2),
        "综合税负率%": round(tot_tax / rev * 100, 2),
    }

    with open("profit_report.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n结果已保存至 profit_report.json")
    return result


if __name__ == "__main__":
    try:
        calculate_profit()
    except KeyboardInterrupt:
        print("\n计算已取消。")
    except Exception as e:
        print(f"\n出错: {e}")
