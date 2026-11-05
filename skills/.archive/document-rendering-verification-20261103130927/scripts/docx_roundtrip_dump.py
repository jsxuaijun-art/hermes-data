#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""docx 结构回读闸门 —— 交付前最便宜的一道检查（无需渲染器）

用途
----
`doc.save()` 成功只证明字节写下去了。这个脚本把刚存盘的文件重新打开、按顺序
dump 出所有段落 + 所有表格，用来抓：
  * 缺章节 / 章节序号重复或跳号（生成器在 for 循环里写死序号的典型症状）
  * 表格丢失、行数不对、单元格串位
  * 段落顺序错乱（抬头/正文/脚注错位）

它**不**验证排版（页边距、溢出、重叠）——那是渲染 pass 的事（soffice / Word COM /
vision）。先用本脚本确认"结构对"，再花时间渲染才有意义。

用法
----
python3 docx_roundtrip_dump.py <file.docx> [--headings-only] [--json]

  --headings-only  只打印疑似标题行（短行 / 以序号开头 / 带「：」的标签行），
                   用于快速核对章节编号序列是否连续
  --json           以 JSON 输出（段落 + 表格二维数组），便于程序化 diff 两次生成结果

退出码
------
0 = 文件可打开且非空；2 = 打不开或零段落（此时不要交付，先修生成器）
"""

import argparse
import json
import re
import sys

try:
    from docx import Document
except ImportError:  # pragma: no cover
    sys.exit("缺少 python-docx：pip install python-docx")

# 中文数字章节序号，如「一、」「十二、」
CJK_SEC = re.compile(r"^\s*[一二三四五六七八九十]+[、.．]")
ARABIC_SEC = re.compile(r"^\s*\d+[、.．)]")


def looks_like_heading(t: str) -> bool:
    if not t:
        return False
    if CJK_SEC.match(t) or ARABIC_SEC.match(t):
        return True
    # 短行 + 结尾无句读 → 大概率是标题
    return len(t) <= 40 and not re.search(r"[。！？；，,]$", t)


def collect(path: str) -> dict:
    d = Document(path)
    paras = [p.text for p in d.paragraphs if p.text.strip()]
    tables = []
    for t in d.tables:
        rows = []
        for row in t.rows:
            rows.append([c.text.strip() for c in row.cells])
        tables.append(rows)
    return {"paragraphs": paras, "tables": tables}


def main() -> int:
    ap = argparse.ArgumentParser(description="docx 结构回读闸门")
    ap.add_argument("docx")
    ap.add_argument("--headings-only", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    try:
        got = collect(a.docx)
    except Exception as e:
        print("!! 打不开：%s" % e, file=sys.stderr)
        return 2

    paras, tables = got["paragraphs"], got["tables"]
    if not paras and not tables:
        print("!! 文档为空（零段落、零表格）——不要交付", file=sys.stderr)
        return 2

    if a.json:
        print(json.dumps(got, ensure_ascii=False, indent=2))
    elif a.headings_only:
        for t in paras:
            if looks_like_heading(t):
                print(t)
    else:
        for t in paras:
            print(t)
        print("\n--- tables: %d ---" % len(tables))
        for ti, rows in enumerate(tables, start=1):
            print("[table %d] %d rows x %d cols"
                  % (ti, len(rows), len(rows[0]) if rows else 0))
            for row in rows:
                print("  " + " | ".join(row))

    print("\n--- summary ---")
    print("paragraphs: %d   tables: %d   cells: %d"
          % (len(paras), len(tables), sum(len(r) for t in tables for r in t)))

    # 章节序号连续性自检（抓"循环里写死序号"）
    seq = [t for t in paras if CJK_SEC.match(t)]
    if seq:
        print("section-like lines: %d" % len(seq))
        seen = [CJK_SEC.match(t).group(0).strip("、.． ") for t in seq]
        dupes = sorted({s for s in seen if seen.count(s) > 1})
        if dupes:
            print("!! 序号重复：%s  ← 生成器可能把序号写死在循环里" % " ".join(dupes))
        else:
            print("序号无重复")
    return 0


if __name__ == "__main__":
    sys.exit(main())
