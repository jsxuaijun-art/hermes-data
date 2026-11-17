# -*- coding: utf-8 -*-
"""
tax-base 优惠时效核验钩子
扫描 rates.json 中标注"敏感，须核验最新"的优惠项，列出需用 cn-regulation-verification
逐条核验现行性 / 是否废止 / 最新文号的项目。执行频率建议：每月或使用优惠前。
用法：python3 verify_rates.py
"""
import json
import os


def main():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rates.json")
    with open(p, encoding="utf-8") as f:
        data = json.load(f)

    print("=" * 70)
    print("tax-base 优惠时效核验清单（须用 cn-regulation-verification 逐条核验）")
    print("=" * 70)
    print("提示：以下项时效敏感，计算涉优惠前务必核验最新有效性与文号，勿仅凭 rates.json。\n")

    n = 0
    def walk(obj, path):
        nonlocal n
        if isinstance(obj, dict):
            if obj.get("_note") and "敏感" in str(obj.get("_note", "")):
                n += 1
                print(f"[{n}] {path}")
                print(f"     优惠: {obj.get('内容') or obj.get('rate') or ''}")
                print(f"     文号: {obj.get('文号', '—')}  /  有效期: {obj.get('有效期', '—')}")
                print()
            for k, v in obj.items():
                walk(v, f"{path} > {k}")
        elif isinstance(obj, list):
            for i, it in enumerate(obj):
                walk(it, f"{path}[{i}]")

    walk(data, "rates")
    if n == 0:
        print("（未发现敏感优惠项）")
    print("=" * 70)
    print(f"共 {n} 项敏感优惠需核验。")


if __name__ == "__main__":
    main()
