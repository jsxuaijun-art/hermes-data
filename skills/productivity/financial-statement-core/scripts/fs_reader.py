#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fs_reader.py — 统一财务报表读取引擎（共享底座 financial-statement-core v1）

设计目标
--------
把「读表取数」这一层从各业务 skill（注销 / 财报分析 / 格式转换 / 股权转让）抽出，
统一口径、一处修复处处生效。本脚本只负责「文件 → 标准化 JSON」，不做任何业务分析，
也不做脱敏（脱敏由各业务处理层负责）。

统一口径（全部来自公司注销 qingshui_risk_engine 实盘踩坑后的结论）
------------------------------------------------------------------
1. 科目余额表：借贷列从「子行」识别；期末取【最后一组】借方/贷方（覆盖式取尾），
   【第一组】为期初 —— 防止把期初误读成期末（QD 案例差一个数量级）。
2. 资产负债表：左右双栏 [A名称|B行次|C期末|D年初] [E名称|F行次|G期末|H年初]，
   只读 C/G（期末）；**不取「最后非零数字列」**（会误中年初 H）。
3. 现金流量表 sheet 一律跳过（行名会误匹雷区/风险关键词）。
4. 科目余额表顶层科目 = 科目编码为 4 位者。
5. totals 取资产负债表「资产总计 / 负债合计 / 所有者权益合计」权威值（供清税测算、净资产）。
6. 数据源优先级交给消费方：科目余额表明细 覆盖 报表汇总（清税测算用报表权威总额）。

用法
----
    python3 fs_reader.py --input <文件.xlsx|.xls> [--output out.json] \\
                         [--period end|begin|both] [--print-rows]

输出 JSON 结构
--------------
{
  "ok": true,
  "warnings": [ ... ],
  "source":   { "path","type","sheets_seen","sheets_skipped" },
  "subject_balance": {           # 若检测到科目余额表
     "period": "end",
     "layout": {"header_row","sub_row","data_start"},
     "subjects_top": { "应收账款": 496.0, ... },     # 顶层科目 借贷净值
     "detail": [ {"code","name","debit_end","credit_end","net","is_top"}, ... ],
     "begin": { "subjects_top": {...}, "detail": [...] }   # 仅 period in (begin,both)
  },
  "statement": {                 # 若检测到财务报表
     "balance_sheet":  { "end": {...}, "begin": {...} },
     "income_statement": { "annual": {...} }
  },
  "totals": { "assets","liabilities","equity" }
}
"""
import argparse
import json
import os
import sys
from collections import OrderedDict

try:
    import openpyxl
except ImportError:
    openpyxl = None

try:
    import xlrd
except ImportError:
    xlrd = None


# ---------------------------------------------------------------------------
# 小工具
# ---------------------------------------------------------------------------
def _clean(v):
    """把单元格值安全转成 float，空/非数字返回 0.0"""
    if v is None:
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).replace(",", "").replace("￥", "").replace("¥", "").strip()
    if not s or s in ("-", "--"):
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0


def _is_numeric(v):
    if isinstance(v, (int, float)):
        return True
    if v is None:
        return False
    s = str(v).replace(",", "").replace("￥", "").replace("¥", "").strip()
    if not s:
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False


def _fix_text(s):
    """修复老式 .xls 的内码乱码：财务软件导出的 xls 常以 GBK(CP936) 存中文，
    但内码记录指向 Latin-1，xlrd 按 Latin-1 解码 → 全变乱码（如
    'ÒøÐÐ´æ¿î'=银行存款）。策略：若字符串无中文且含疑似 Latin-1 扩展字符，
    尝试 latin-1 编码还原字节 → gbk 解码；修复结果含中文才采用。"""
    if not isinstance(s, str):
        return str(s) if s is not None else ""
    if not s:
        return s
    if any("\u4e00" <= ch <= "\u9fff" for ch in s):
        return s  # 已是中文，无需修复
    try:
        fixed = s.encode("latin-1").decode("gbk")
        if any("\u4e00" <= ch <= "\u9fff" for ch in fixed):
            return fixed
    except Exception:
        pass
    return s


def _xlrd_open(path):
    """打开 xlrd workbook。老 .xls 会在打开时向默认 logfile（绑定到 stdout 的文件对象）打
    'OLE2 inconsistency...' 警告，污染 fs_reader 的 JSON 输出。这里显式把 logfile 指向
    stderr，保证 stdout 纯净。"""
    return xlrd.open_workbook(path, logfile=sys.stderr)


# ---------------------------------------------------------------------------
# 科目余额表 (xlsx)
# ---------------------------------------------------------------------------
def _find_header_row(ws, max_col):
    """定位科目余额表表头行：优先找含「科目名称/科目编码」且其后出现「借方/贷方」子行的行。
    避免误中标题行（如第一行就是「科目余额表」四个字）。"""
    for r in range(1, min(ws.max_row, 12) + 1):
        rowtxt = "|".join(str(ws.cell(r, c).value or "") for c in range(1, max_col + 1))
        if ("科目名称" in rowtxt or "科目编码" in rowtxt or "科目编号" in rowtxt):
            # 检查下一行是否是 借方/贷方 子行
            nxt = "".join(str(ws.cell(r + 1, c).value or "") for c in range(1, max_col + 1))
            if "借方" in nxt or "贷方" in nxt:
                return r
            return r
    return 1


def _subject_columns(ws, header_row, max_col):
    """返回列定位 dict：
       name_col / code_col /
       begin_debit / begin_credit / end_debit / end_credit (可能为 None)
    规则：子行出现多组「借方/贷方」时，第一组=期初、最后一组=期末(覆盖式取尾)。"""
    cols = {"name": None, "code": None,
            "begin_debit": None, "begin_credit": None,
            "end_debit": None, "end_credit": None}
    data_start = header_row + 1
    # 子行（表头下一行）
    subvals = [str(ws.cell(data_start, c).value or "").strip() for c in range(1, max_col + 1)]
    if "借方" in "".join(subvals) or "贷方" in "".join(subvals):
        debit_cols, credit_cols = [], []
        for c in range(1, max_col + 1):
            sv = subvals[c - 1]
            if sv == "借方":
                debit_cols.append(c)
            elif sv == "贷方":
                credit_cols.append(c)
        if debit_cols:
            cols["begin_debit"] = debit_cols[0]
            cols["end_debit"] = debit_cols[-1]
        if credit_cols:
            cols["begin_credit"] = credit_cols[0]
            cols["end_credit"] = credit_cols[-1]
        data_start = header_row + 2
    else:
        # 无子行：直接在表头行找「期末余额/期末借方/期末贷方/借方余额/贷方余额」
        for c in range(1, max_col + 1):
            h = str(ws.cell(header_row, c).value or "").strip()
            if "科目名称" in h or h == "科目":
                cols["name"] = c
            elif "科目编码" in h or "科目编号" in h:
                cols["code"] = c
            elif "期初" in h and ("借方" in h or "贷方" in h):
                if "借方" in h and cols["begin_debit"] is None:
                    cols["begin_debit"] = c
                elif "贷方" in h and cols["begin_credit"] is None:
                    cols["begin_credit"] = c
            elif ("期末余额" in h and ("借方" in h or "贷方" in h)) or "期末借方" in h or "借方余额" in h:
                cols["end_debit"] = c if "借" in h else cols["end_debit"]
            elif ("期末余额" in h and ("借方" in h or "贷方" in h)) or "期末贷方" in h or "贷方余额" in h:
                cols["end_credit"] = c if "贷" in h else cols["end_credit"]
    # name 列必须有
    for c in range(1, max_col + 1):
        if cols["name"] is None:
            h = str(ws.cell(header_row, c).value or "").strip()
            if h in ("科目", "科目名称", "账户名称", "会计科目"):
                cols["name"] = c
    cols["data_start"] = data_start
    return cols


def _read_subject_balance_xlsx(path, period="end"):
    if openpyxl is None:
        raise RuntimeError("缺少 openpyxl")
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active
    max_col = ws.max_column
    header_row = _find_header_row(ws, max_col)
    cols = _subject_columns(ws, header_row, max_col)
    if cols["name"] is None:
        raise ValueError("未找到科目名称列")
    use_begin = period in ("begin", "both")

    def _is_top(code):
        return (len(str(code)) == 4) if str(code) else True

    detail = []
    for r in range(cols["data_start"], ws.max_row + 1):
        name = str(ws.cell(r, cols["name"]).value or "").strip()
        if not name or name.startswith("合计") or name.startswith("总计") or "合计" in name:
            continue
        code = str(ws.cell(r, cols["code"]).value or "").strip() if cols["code"] else ""
        debit_end = _clean(ws.cell(r, cols["end_debit"]).value) if cols["end_debit"] else 0.0
        credit_end = _clean(ws.cell(r, cols["end_credit"]).value) if cols["end_credit"] else 0.0
        debit_beg = _clean(ws.cell(r, cols["begin_debit"]).value) if (use_begin and cols["begin_debit"]) else 0.0
        credit_beg = _clean(ws.cell(r, cols["begin_credit"]).value) if (use_begin and cols["begin_credit"]) else 0.0
        net = debit_end - credit_end
        net_beg = debit_beg - credit_beg
        top = _is_top(code) if code else True
        detail.append({
            "code": code, "name": name,
            "debit_end": debit_end, "credit_end": credit_end, "net": net,
            "debit_begin": debit_beg, "credit_begin": credit_beg, "net_begin": net_beg,
            "is_top": top,
        })
    # 顶层科目：编码4位（或无可忽略的编码），后同名覆盖取净值
    subjects_top = OrderedDict()
    for d in detail:
        if d["is_top"]:
            subjects_top[d["name"]] = d["net"]
    layout = {"header_row": header_row,
              "sub_row": header_row + 1,
              "data_start": cols["data_start"]}
    return subjects_top, detail, layout


# ---------------------------------------------------------------------------
# 科目余额表 (xls)
# ---------------------------------------------------------------------------
def _read_subject_balance_xls(path, period="end"):
    if xlrd is None:
        raise RuntimeError("缺少 xlrd（读取 .xls 需要）")
    wb = _xlrd_open(path)
    ws = wb.sheet_by_index(0)
    nrows, ncols = ws.nrows, ws.ncols
    # 找含「科目名称/科目编码」的表头行
    header_row = None
    for r in range(min(nrows, 12)):
        rowtxt = "|".join(_fix_text(ws.cell_value(r, c)) for c in range(ncols))
        if "科目名称" in rowtxt or "科目编码" in rowtxt or "科目编号" in rowtxt:
            header_row = r
            break
    if header_row is None:
        header_row = 0
    cols = {"name": None, "code": None,
            "begin_debit": None, "begin_credit": None,
            "end_debit": None, "end_credit": None}
    data_start = header_row + 1
    subvals = [_fix_text(ws.cell_value(data_start, c)).strip() for c in range(ncols)]
    if "借方" in "".join(subvals) or "贷方" in "".join(subvals):
        db, cr = [], []
        for c in range(ncols):
            sv = subvals[c]
            if sv == "借方":
                db.append(c)
            elif sv == "贷方":
                cr.append(c)
        if db:
            cols["begin_debit"], cols["end_debit"] = db[0], db[-1]
        if cr:
            cols["begin_credit"], cols["end_credit"] = cr[0], cr[-1]
        data_start += 1
    if cols["name"] is None:
        # 单行表头：显式列名（如 期初余额(借方)/期末余额(贷方)），直接按表头文字识别
        for c in range(ncols):
            h = _fix_text(ws.cell_value(header_row, c)).strip()
            if "科目名称" in h or h == "科目":
                if cols["name"] is None:
                    cols["name"] = c
            elif "科目代码" in h or "科目编码" in h or "科目编号" in h:
                if cols["code"] is None:
                    cols["code"] = c
            elif "期末余额" in h or ("期末" in h and ("借" in h or "贷" in h)):
                if "借" in h:
                    cols["end_debit"] = c
                elif "贷" in h:
                    cols["end_credit"] = c
            elif "期初余额" in h or ("期初" in h and ("借" in h or "贷" in h)):
                if "借" in h and cols["begin_debit"] is None:
                    cols["begin_debit"] = c
                elif "贷" in h and cols["begin_credit"] is None:
                    cols["begin_credit"] = c
            elif "借方余额" in h or "借方" == h:
                cols["end_debit"] = c
            elif "贷方余额" in h or "贷方" == h:
                cols["end_credit"] = c
    if cols["name"] is None:
        raise ValueError("未找到科目名称列")
    use_begin = period in ("begin", "both")

    def _is_top(code):
        return (len(str(code)) == 4) if str(code) else True

    detail = []
    for r in range(data_start, nrows):
        name = _fix_text(ws.cell_value(r, cols["name"])).strip()
        if not name or "合计" in name or "总计" in name:
            continue
        code = str(ws.cell_value(r, cols["code"])).strip() if cols["code"] is not None else ""
        debit_end = _clean(ws.cell_value(r, cols["end_debit"])) if cols["end_debit"] is not None else 0.0
        credit_end = _clean(ws.cell_value(r, cols["end_credit"])) if cols["end_credit"] is not None else 0.0
        debit_beg = _clean(ws.cell_value(r, cols["begin_debit"])) if (use_begin and cols["begin_debit"] is not None) else 0.0
        credit_beg = _clean(ws.cell_value(r, cols["begin_credit"])) if (use_begin and cols["begin_credit"] is not None) else 0.0
        net = debit_end - credit_end
        net_beg = debit_beg - credit_beg
        top = _is_top(code) if code else True
        detail.append({
            "code": code, "name": name,
            "debit_end": debit_end, "credit_end": credit_end, "net": net,
            "debit_begin": debit_beg, "credit_begin": credit_beg, "net_begin": net_beg,
            "is_top": top,
        })
    subjects_top = OrderedDict((d["name"], d["net"]) for d in detail if d["is_top"])
    layout = {"header_row": header_row + 1, "sub_row": header_row + 2,
              "data_start": data_start + 1}
    return subjects_top, detail, layout


# ---------------------------------------------------------------------------
# 财务报表（资产负债表双栏 + 利润表）—— 多 sheet，跳过现金流量表
# ---------------------------------------------------------------------------
def _read_statements_xlsx(path, period="end"):
    if openpyxl is None:
        raise RuntimeError("缺少 openpyxl")
    wb = openpyxl.load_workbook(path, data_only=True)
    sheets_seen, sheets_skipped = [], []
    bs_end, bs_begin = {}, {}
    pl_annual = {}
    for ws in wb.worksheets:
        sheets_seen.append(ws.title)
        if "现金流量表" in ws.title:
            sheets_skipped.append(ws.title)
            continue
        is_bs = "资产负债表" in ws.title
        is_pl = "利润表" in ws.title
        if not is_bs and not is_pl:
            continue
        for r in range(1, ws.max_row + 1):
            if is_bs:
                # 左栏 [A名称|B行次|C期末|D年初] —— 名空时跳过左栏，但继续处理右栏
                name = str(ws.cell(r, 1).value or "").strip()
                if name and name not in ("资产", "流动资产：", "非流动资产："):
                    if ws.max_column >= 3 and _is_numeric(ws.cell(r, 3).value):
                        bs_end[name] = _clean(ws.cell(r, 3).value)
                    if ws.max_column >= 4 and _is_numeric(ws.cell(r, 4).value) and period in ("begin", "both"):
                        bs_begin[name] = _clean(ws.cell(r, 4).value)
                # 右栏 [E名称|F行次|G期末|H年初]
                if ws.max_column >= 7:
                    rname = str(ws.cell(r, 5).value or "").strip()
                    if rname and rname not in ("负债和所有者权益", "流动负债：", "非流动负债："):
                        if _is_numeric(ws.cell(r, 7).value):
                            bs_end[rname] = _clean(ws.cell(r, 7).value)
                        if ws.max_column >= 8 and _is_numeric(ws.cell(r, 8).value) and period in ("begin", "both"):
                            bs_begin[rname] = _clean(ws.cell(r, 8).value)
            elif is_pl:
                name = str(ws.cell(r, 1).value or "").strip()
                if name and ws.max_column >= 3 and _is_numeric(ws.cell(r, 3).value):
                    pl_annual[name] = _clean(ws.cell(r, 3).value)
    return {"balance_sheet": {"end": bs_end, "begin": bs_begin},
            "income_statement": {"annual": pl_annual},
            "sheets_seen": sheets_seen, "sheets_skipped": sheets_skipped}


def _read_statements_xls(path, period="end"):
    if xlrd is None:
        raise RuntimeError("缺少 xlrd")
    wb = _xlrd_open(path)
    sheets_seen, sheets_skipped = [], []
    bs_end, bs_begin = {}, {}
    pl_annual = {}
    for ws in wb.sheets():
        sname = _fix_text(ws.name)
        sheets_seen.append(sname)
        if "现金流量表" in sname:
            sheets_skipped.append(sname)
            continue
        is_bs = "资产负债表" in sname
        is_pl = "利润表" in sname
        if not is_bs and not is_pl:
            continue
        for r in range(ws.nrows):
            if is_bs:
                # 左栏 [A名称|B行次|C期末|D年初]
                name = _fix_text(ws.cell_value(r, 0)).strip()
                if name and name not in ("资产", "流动资产：", "非流动资产："):
                    if ws.ncols >= 3 and _is_numeric(ws.cell_value(r, 2)):
                        bs_end[name] = float(ws.cell_value(r, 2))
                    if ws.ncols >= 4 and _is_numeric(ws.cell_value(r, 3)) and period in ("begin", "both"):
                        bs_begin[name] = float(ws.cell_value(r, 3))
                # 右栏 [E名称|F行次|G期末|H年初]
                if ws.ncols >= 7:
                    rname = _fix_text(ws.cell_value(r, 4)).strip()
                    if rname and rname not in ("负债和所有者权益", "流动负债：", "非流动负债："):
                        if _is_numeric(ws.cell_value(r, 6)):
                            bs_end[rname] = float(ws.cell_value(r, 6))
                        if ws.ncols >= 8 and _is_numeric(ws.cell_value(r, 7)) and period in ("begin", "both"):
                            bs_begin[rname] = float(ws.cell_value(r, 7))
            elif is_pl:
                name = _fix_text(ws.cell_value(r, 0)).strip()
                if name and ws.ncols >= 3 and _is_numeric(ws.cell_value(r, 2)):
                    pl_annual[name] = float(ws.cell_value(r, 2))
    return {"balance_sheet": {"end": bs_end, "begin": bs_begin},
            "income_statement": {"annual": pl_annual},
            "sheets_seen": sheets_seen, "sheets_skipped": sheets_skipped}


def _extract_totals(bs_end):
    """从资产负债表期末项提取权威总额（资产总计/负债合计/所有者权益合计）。"""
    totals = {}
    seen = {}
    for k, v in bs_end.items():
        kk = k.replace(" ", "")
        if "资产总计" in kk or "资产合计" in kk:
            seen["assets"] = abs(v)
        elif "负债合计" in kk or "负债总计" in kk:
            seen["liabilities"] = abs(v)
        elif ("负债" not in kk) and (("所有者权益" in kk or "股东权益" in kk) and ("合计" in kk or "总计" in kk)):
            seen["equity"] = abs(v)
        elif "权益合计" in kk or "股东权益合计" in kk:
            seen.setdefault("equity", abs(v))
    for k in ("assets", "liabilities", "equity"):
        if k in seen:
            totals[k] = seen[k]
    return totals


def _looks_like_subject_balance_xlsx(path):
    """按表结构判断是否科目余额表：表头含 科目名称/科目编码/科目，且其后有 借方/贷方 子行。"""
    if openpyxl is None:
        return False
    try:
        wb = openpyxl.load_workbook(path, data_only=True)
        ws = wb.active
        max_col = ws.max_column
        for r in range(1, min(ws.max_row, 12) + 1):
            rowtxt = "|".join(str(ws.cell(r, c).value or "") for c in range(1, max_col + 1))
            if "科目名称" in rowtxt or "科目编码" in rowtxt or "科目编号" in rowtxt:
                nxt = "".join(str(ws.cell(r + 1, c).value or "") for c in range(1, max_col + 1))
                if "借方" in nxt or "贷方" in nxt:
                    return True
                return True
        return False
    except Exception:
        return False


def _looks_like_subject_balance_xls(path):
    if xlrd is None:
        return False
    try:
        wb = _xlrd_open(path)
        ws = wb.sheet_by_index(0)
        for r in range(min(ws.nrows, 12)):
            rowtxt = "|".join(_fix_text(ws.cell_value(r, c)) for c in range(ws.ncols))
            if "科目名称" in rowtxt or "科目编码" in rowtxt or "科目编号" in rowtxt:
                return True
        return False
    except Exception:
        return False


# ---------------------------------------------------------------------------
# 顶层入口：识别类型并组装标准化 JSON
# ---------------------------------------------------------------------------
def read_file(path, period="end"):
    if not os.path.isfile(path):
        raise FileNotFoundError(f"文件不存在: {path}")
    ext = os.path.splitext(path)[1].lower()
    base = os.path.basename(path).lower()
    warnings = []
    result = {"ok": True, "warnings": warnings,
              "source": {"path": path, "type": "unknown",
                         "sheets_seen": [], "sheets_skipped": []},
              "subject_balance": None, "statement": None, "totals": {}}

    # 类型识别：文件名含「科目余额表」，或表结构含「科目名称/编码 + 借贷子行」→ 科目余额表
    is_kemu = "科目余额表" in base
    if not is_kemu:
        try:
            is_kemu = (_looks_like_subject_balance_xlsx(path) if ext == ".xlsx"
                       else _looks_like_subject_balance_xls(path))
        except Exception:
            is_kemu = False

    if is_kemu:
        try:
            if ext == ".xls":
                subs_top, detail, layout = _read_subject_balance_xls(path, period)
            else:
                subs_top, detail, layout = _read_subject_balance_xlsx(path, period)
            warnings.append("期末余额取最后一组借贷列(覆盖式取尾)，防止误读为期初")
            result["source"]["type"] = "subject_balance"
            result["subject_balance"] = {
                "period": period, "layout": layout,
                "subjects_top": dict(subs_top), "detail": detail,
            }
            if period in ("begin", "both"):
                result["subject_balance"]["begin"] = {
                    "subjects_top": {d["name"]: d["net_begin"] for d in detail if d["is_top"]},
                    "detail": detail,
                }
            return result
        except Exception:
            result["warnings"].append(f"科目余额表解析失败，改按财务报表解析: {sys.exc_info()[1]}")

    # 财务报表（资产负债表/利润表）
    rd = _read_statements_xlsx(path, period) if ext == ".xlsx" else _read_statements_xls(path, period)
    result["source"]["sheets_seen"] = rd["sheets_seen"]
    result["source"]["sheets_skipped"] = rd["sheets_skipped"]
    if rd["sheets_skipped"]:
        warnings.append(f"已跳过现金流量表sheet: {rd['sheets_skipped']}（行名会误匹风险关键词）")
    if any(x in ("资产负债表",) for x in rd["sheets_seen"]):
        result["source"]["type"] = "balance_sheet"
    elif any("利润表" in x for x in rd["sheets_seen"]):
        result["source"]["type"] = "income_statement"
    result["statement"] = rd
    result["totals"] = _extract_totals(rd["balance_sheet"]["end"])
    if result["source"]["type"] == "balance_sheet":
        warnings.append("资产负债表仅取C/G期末列，未用'最后非零数字列'(会误中年初H)")
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _print_rows(path, max_rows=25):
    """打印行列结构，用于排查（不生成正式结果）。"""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".xls":
        wb = _xlrd_open(path)
        ws = wb.sheet_by_index(0)
        print(f"sheet='{ws.name}' rows={ws.nrows} cols={ws.ncols}")
        for r in range(min(ws.nrows, max_rows)):
            print(r, [str(ws.cell_value(r, c))[:18] for c in range(ws.ncols)])
        return
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active
    print(f"sheet='{ws.title}' rows={ws.max_row} cols={ws.max_column}")
    print("merged:", list(ws.merged_cells.ranges)[:30])
    for r in range(1, min(ws.max_row, max_rows) + 1):
        print(r, [str(ws.cell(r, c).value)[:18] if ws.cell(r, c).value is not None else "" for c in range(1, ws.max_column + 1)])


def main():
    ap = argparse.ArgumentParser(description="统一财务报表读取引擎 (financial-statement-core)")
    ap.add_argument("--input", required=True)
    ap.add_argument("--output")
    ap.add_argument("--period", default="end", choices=["end", "begin", "both"])
    ap.add_argument("--print-rows", action="store_true")
    args = ap.parse_args()
    if args.print_rows:
        _print_rows(args.input)
        return
    data = read_file(args.input, period=args.period)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        print(f"[ok] wrote {args.output}")
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
