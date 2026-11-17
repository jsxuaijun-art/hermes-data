# -*- coding: utf-8 -*-
"""
tax-base 计算 helper（纯函数，无副作用，供各财税 skill 调用）
用法：python3 calc.py --vat-split 113000,0.13  /  --eit 4889189  /  --iit-comp 150000 ...
也支持以模块方式 import 各函数。
数据源：同目录 rates.json（税费率速查，优惠类以最新文件核验为准）。
"""
import json
import os
import sys
import functools

_RATES_CACHE = {}


def rates():
    if not _RATES_CACHE:
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rates.json")
        with open(p, encoding="utf-8") as f:
            _RATES_CACHE.update(json.load(f))
    return _RATES_CACHE


# ---------- 价税分离 ----------
def vat_split(价税合计, rate=0.13):
    """价税合计 -> (不含税销售额, 销项税/增值税额)"""
    rate = float(rate)
    不含税 = 价税合计 / (1 + rate)
    return round(不含税, 2), round(价税合计 - 不含税, 2)


def vat_from(不含税, rate=0.13):
    return round(不含税 * float(rate), 2)


# ---------- 企业所得税 ----------
def eit_calc(应纳税所得额, 类型="一般"):
    """类型: 一般(25%) / 高新(15%) / 小微(实际5%, ≤300万)"""
    d = float(应纳税所得额)
    if 类型 == "高新":
        return round(d * 0.15, 2)
    if 类型 == "小微":
        if d <= 3000000:
            return round(d * 0.05, 2)  # 减按25%计入×20%
        raise ValueError("小微仅适用年应纳税所得额≤300万")
    return round(d * 0.25, 2)


# ---------- 个人所得税(综合所得, 按年, 7级) ----------
IIT_COM = [
    (36000, 0.03, 0), (144000, 0.10, 2520), (300000, 0.20, 16920),
    (420000, 0.25, 31920), (660000, 0.30, 52920), (960000, 0.35, 85920),
    (None, 0.45, 181920),
]


def iit_comprehensive(年应纳税所得额):
    """综合所得年度个税（超额累进）。年应纳税所得额=年收入-6万-专项扣除-专项附加-其他。"""
    y = float(年应纳税所得额)
    if y <= 0:
        return 0.0
    for up, r, qs in IIT_COM:
        if up is None or y <= up:
            return round(y * r - qs, 2)
    return round(y * IIT_COM[-1][1] - IIT_COM[-1][2], 2)


# ---------- 个人所得税(经营所得, 按年, 5级) ----------
IIT_OP = [
    (30000, 0.05, 0), (90000, 0.10, 1500), (300000, 0.20, 10500),
    (500000, 0.30, 40500), (None, 0.35, 65500),
]


def iit_operating(年应纳税所得额):
    y = float(年应纳税所得额)
    if y <= 0:
        return 0.0
    for up, r, qs in IIT_OP:
        if up is None or y <= up:
            return round(y * r - qs, 2)
    return round(y * IIT_OP[-1][1] - IIT_OP[-1][2], 2)


# ---------- 城建税及附加 ----------
def surtax(增值税额, 城建税率=0.07, 教育附加=0.03, 地方教育附加=0.02):
    v = float(增值税额)
    城建 = round(v * 城建税率, 2)
    教育 = round(v * 教育附加, 2)
    地方 = round(v * 地方教育附加, 2)
    return {"城建税": 城建, "教育费附加": 教育, "地方教育附加": 地方, "合计": round(城建 + 教育 + 地方, 2)}


# ---------- 印花税 ----------
def stamp_duty(税目, 计税金额):
    """税目: 租赁合同/建设工程合同/买卖合同/借款合同/保管合同/产权转移书据/营业账簿/证券交易"""
    tbl = {
        "租赁合同": 0.001, "保管合同": 0.001, "仓储合同": 0.001,
        "建设工程合同": 0.0003, "买卖合同": 0.0003, "承揽合同": 0.0003,
        "运输合同": 0.0003, "技术合同": 0.0003,
        "借款合同": 0.00005, "融资租赁合同": 0.00005,
        "产权转移书据": 0.0005, "营业账簿": 0.00025, "证券交易": 0.0005,
    }
    if 税目 not in tbl:
        raise ValueError(f"未知印花税税目: {税目}，可用={list(tbl)}")
    return round(float(计税金额) * tbl[税目], 2)


# ---------- CLI ----------
def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__); return
    if a[0] == "--vat-split":
        v, r = float(a[1].split(",")[0]), float(a[1].split(",")[1])
        print(json.dumps({"不含税": vat_split(v, r)[0], "税额": vat_split(v, r)[1]}, ensure_ascii=False))
    elif a[0] == "--eit":
        print(json.dumps({"企业所得税": eit_calc(a[1], a[2] if len(a) > 2 else "一般")}, ensure_ascii=False))
    elif a[0] == "--iit-comp":
        print(json.dumps({"个税综合": iit_comprehensive(a[1])}, ensure_ascii=False))
    elif a[0] == "--iit-op":
        print(json.dumps({"个税经营": iit_operating(a[1])}, ensure_ascii=False))
    elif a[0] == "--surtax":
        v = float(a[1]) if len(a) > 1 else 0
        print(json.dumps(surtax(v), ensure_ascii=False))
    elif a[0] == "--stamp":
        print(json.dumps({"印花税": stamp_duty(a[1], a[2])}, ensure_ascii=False))
    else:
        print("未知参数")


if __name__ == "__main__":
    main()
