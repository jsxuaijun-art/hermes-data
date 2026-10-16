#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""交付前自检：扫反法旧条文号 + 占位符/脱敏值 + 未填当事人字段。

用途（对应 references 第十二节）：
  改稿生成新起诉状/预案后、交给用户之前跑一遍，机器抓出两类最贵的失误
  ——① 沿用 2019 旧反法编号；② 原稿的脱敏占位（TT）/AI 假名（赵帅甲）/下划线被原样拷进新稿。
  机器只查"文本形态"，查不出内容对不对：跑完仍须 read_file 回读成品逐字段核对。

用法：
    python3 check_doc_citations.py "民事起诉状_修订稿v3.docx" "预案_v3.docx"
    python3 check_doc_citations.py --dir .            # 扫目录下所有 docx/md/txt

退出码：0 干净；1 发现硬问题（旧反法编号 / 当事人字段仍是占位符）。
无第三方依赖：.docx 用 stdlib zipfile 直接读 word/document.xml。
"""
import argparse
import html
import os
import re
import sys
import zipfile

# 2019 旧编号 -> 2025 新编号（行为发生在 2025-10-15 后须用新编号）
OLD_ARTICLES = {
    "第八条": "虚假宣传：旧8 → 新9",
    "第十一条": "商业诋毁：旧11 → 新12",
    "第十七条": "赔偿+合理开支：旧17 → 新22",
}
NEW_ARTICLE_TOKENS = ["第九条", "第十二条", "第二十二条", "第二十八条"]
FA_CTX = re.compile(r"反不正当竞争|反法|不正当竞争法")
# 第7/10条在旧新法中编号不同（混淆6→7、商业秘密9→10），一并提示人工核对
HINT_ARTICLES = ["第六条", "第九条", "第十条", "第二十三条"]

PLACEHOLDERS = [
    (re.compile(r"法定代表人[：:]\s*TT\b"), "当事人字段仍是脱敏占位 TT"),
    (re.compile(r"赵帅甲"), "疑似 AI 生成的人名占位符（勿直接提交）"),
    (re.compile(r"【待填】|\[待填\]|待补充|待核实后填写"), "显式待填标记（确认是否已补齐）"),
    (re.compile(r"法定代表人[：:]\s*[_＿]{3,}"), "法定代表人未填 → 会致无法送达/不予立案"),
    (re.compile(r"统一社会信用代码[：:]\s*[_＿]{3,}"), "统一社会信用代码未填"),
    (re.compile(r"XXX{2,}|ＴＢＤ|TBD"), "通用占位串"),
]
REQUIRED_FIELDS = ["原告", "被告", "法定代表人", "统一社会信用代码", "诉讼请求"]


def read_text(path):
    """读 .docx（stdlib，无第三方依赖）或纯文本，返回带换行的文本。"""
    if path.lower().endswith(".docx"):
        with zipfile.ZipFile(path) as z:
            names = [n for n in z.namelist() if n == "word/document.xml"]
            if not names:
                return ""
            xml = z.read("word/document.xml").decode("utf-8", "ignore")
        xml = re.sub(r"</w:(p|tr)>", "\n", xml)          # 段落/表格行 -> 换行
        xml = re.sub(r"</w:tc>", " | ", xml)             # 单元格分隔
        return html.unescape(re.sub(r"<[^>]+>", "", xml))
    with open(path, encoding="utf-8", errors="ignore") as f:
        return f.read()


def check(path):
    text = read_text(path)
    if not text.strip():
        return False, ["无法读取文本内容（空文件或不支持的格式）"], 0, 0

    lines = text.splitlines()
    problems, notes = [], []
    doc_mentions_fa = bool(FA_CTX.search(text))   # 全文是否在谈反法

    # 1) 旧条文号
    for i, line in enumerate(lines, 1):
        for old, why in OLD_ARTICLES.items():
            if old in line:
                if doc_mentions_fa:
                    problems.append(f"L{i} 旧反法编号「{old}」（{why}）: {line.strip()[:70]}")
                else:
                    notes.append(f"L{i} 出现「{old}」，本文未见反法语境，人工确认: {line.strip()[:50]}")

    # 2) 占位符 / 脱敏值
    for i, line in enumerate(lines, 1):
        for pat, why in PLACEHOLDERS:
            if pat.search(line):
                problems.append(f"L{i} {why}: {line.strip()[:70]}")

    # 3) 必备字段是否齐
    for field in REQUIRED_FIELDS:
        if field not in text:
            problems.append(f"缺少必备字段：{field}")

    # 4) 反法条号清单（人工核对用）
    cited = sorted({a for a in NEW_ARTICLE_TOKENS + HINT_ARTICLES if a in text})
    if cited:
        notes.append("本文引用的反法相关条号：" + "、".join(cited) +
                     "（请确认全部为 2025 新编号、且未与民法典/民诉法条号混淆）")
    warn_count = text.count("⚠")
    if warn_count:
        notes.append(f"文内共有 {warn_count} 处 ⚠ 待核实标记——交付时必须逐条点名让用户替换/确认")
    return bool(problems), problems, notes, warn_count


def expand_targets(args):
    targets = list(args.files or [])
    if args.dir:
        for name in sorted(os.listdir(args.dir)):
            if name.lower().endswith((".docx", ".md", ".txt")):
                targets.append(os.path.join(args.dir, name))
    return targets


def main():
    ap = argparse.ArgumentParser(description="文书交付前自检：反法条号 / 占位符 / 必备字段")
    ap.add_argument("files", nargs="*", help="待检查的 .docx / .md / .txt")
    ap.add_argument("--dir", help="改为扫描该目录下全部 docx/md/txt")
    args = ap.parse_args()

    targets = expand_targets(args)
    if not targets:
        ap.print_help()
        return 0

    exit_code = 0
    for path in targets:
        if not os.path.exists(path):
            print(f"[跳过] 文件不存在：{path}")
            continue
        has_problem, problems, notes, warn_count = check(path)
        flag = "❌ 有问题" if has_problem else "✅ 通过"
        print(f"\n=== {flag} | {os.path.basename(path)} ===")
        for p in problems:
            print("  [问题] " + p)
        for n in notes:
            print("  [提示] " + n)
        if has_problem:
            exit_code = 1

    if exit_code:
        print("\n硬问题需先修正（旧编号 → 9/12/22/28；占位符 → 填真实值或用 __________ + ⚠ 注明核实渠道）。")
        print("注意：本脚本只查文本形态；仍须 read_file 回读成品，逐字段核对抬头/具状人/落款/金额/证据清单条数。")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
