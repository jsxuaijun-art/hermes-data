#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""藏头诗机械核验器 —— LLM 产出的藏头诗/对联，交付前必跑。

为什么必须跑：模型自报的「藏头连读」和「每句字数」经常错。
实测（2026-10）豆包把实际藏头为「盈信敦慎」的诗标成「盈信敦行」
（第 4 句首字是「慎」不是「行」）。读着顺 ≠ 格式对，必须程序化核验。
韵脚不自动判定（近韵通押要人读），脚本只把每句末字打出来供你肉眼过韵。

支持的常见诗体：四言 / 五言 / 六言 / 七言（每句 4/5/6/7 字）。
2026-10 修：原版硬编码 `lens[0] not in (5, 7)`，四言稿（用户明确要过的格式）
会被自家门禁误杀报 exit 1 → 改为默认接受 4/5/6/7，需严格锁定时用 --line-len N。

用法：
  # 1) 每句一个参数
  python3 verify_acrostic.py 盈程伴企兴 信立专业精 守规存诚敬 正途稳步行 --expect 盈信守正

  # 2) 从文件读（一行一句；空行与 # / // 开头行忽略）
  python3 verify_acrostic.py --file poem.txt --expect 盈信守正

  # 3) 从 stdin 读
  cat poem.txt | python3 verify_acrostic.py --expect 盈信守正

  # 4) 整份草稿批量核验：每首之间用空行隔开，--expect 逗号分隔逐首给藏头
  python3 verify_acrostic.py --file draft.txt --split-blank --expect 盈信守正,盈信行稳

  # 5) 四言稿（每句 4 字）—— 默认就接受，无需额外参数
  python3 verify_acrostic.py 盈耕苏沪 信立诚彰 守规尽责 正伴业昌 --expect 盈信守正

  # 6) 锁定某一诗体（例：必须四言，五言稿即判不合格）
  python3 verify_acrostic.py --file poem.txt --expect 盈信守正 --line-len 4

退出码：0 = 全部通过；1 = 藏头不符 / 字数不齐或非诗体字数（可当交付门禁）。
"""
import argparse
import re
import sys

# 去标点后统计字数（中文标点、空格、全角符号都不算字）
PUNCT = re.compile(r"[^\u3400-\u9fff\u3040-\u30ffA-Za-z0-9]")

# 常见诗体：四言/五言/六言/七言。核验的是「整首齐整 + 落在常见字数」。
COMMON_LENS = (4, 5, 6, 7)
LEN_NAME = {4: "四言", 5: "五言", 6: "六言", 7: "七言"}


def clean(line: str) -> str:
    return PUNCT.sub("", line.strip())


def verify(lines, expect=None, label="诗", line_len=None) -> bool:
    lines = [c for c in (clean(x) for x in lines) if c]
    if not lines:
        print(f"[{label}] 空，跳过")
        return True
    lens = [len(l) for l in lines]
    head = "".join(l[0] for l in lines)
    ok = True
    print(f"[{label}] 句数={len(lines)} 每句字数={lens} 藏头连读=「{head}」")
    print("        每句末字(自查韵脚): " + " ".join(l[-1] for l in lines))
    allowed = (line_len,) if line_len else COMMON_LENS
    if len(set(lens)) != 1 or lens[0] not in allowed:
        allow_txt = f"{line_len} 字" if line_len else "/".join(
            LEN_NAME[n] for n in COMMON_LENS)
        print(f"        !! 字数不齐或非{allow_txt}: {lens}")
        ok = False
    else:
        print(f"        OK 每句 {lens[0]} 字（{LEN_NAME.get(lens[0], '?')}），齐整")
    if expect:
        exp = clean(expect)
        if head != exp:
            print(f"        !! 藏头不符: 实际「{head}」 / 标注「{exp}」——模型自报标签错了，必须改")
            ok = False
        else:
            print(f"        OK 藏头与标注一致「{exp}」")
    return ok


def main() -> None:
    ap = argparse.ArgumentParser(description="藏头诗机械核验（藏头首字拼接 + 每句字数）")
    ap.add_argument("lines", nargs="*", help="诗句，每句一个参数")
    ap.add_argument("--file", help="从文件读，一行一句")
    ap.add_argument("--expect", help="期望的藏头连读，如 盈信守正（多首用逗号分隔）")
    ap.add_argument("--split-blank", action="store_true",
                    help="按空行把文件切成多首逐首核验")
    ap.add_argument("--line-len", type=int, default=None, metavar="N",
                    help="锁定每句字数（4=四言 / 5=五言 / 7=七言）。不给则接受 4/5/6/7 且要求整首齐整")
    args = ap.parse_args()

    raw = list(args.lines)
    if args.file:
        with open(args.file, encoding="utf-8") as f:
            text = f.read()
        if args.split_blank:
            stanzas = [[ln for ln in blk.splitlines() if ln.strip()]
                       for blk in re.split(r"\n\s*\n", text)]
            expects = [e.strip() for e in args.expect.split(",")] if args.expect else []
            all_ok = True
            i = 0
            for st in stanzas:
                if not st:
                    continue
                exp = expects[i] if i < len(expects) else None
                i += 1
                if not verify(st, exp, label=f"第{i}首", line_len=args.line_len):
                    all_ok = False
            sys.exit(0 if all_ok else 1)
        raw = [ln for ln in text.splitlines()
               if ln.strip() and not ln.strip().startswith(("#", "//"))]
    elif not raw and not sys.stdin.isatty():
        raw = [ln for ln in sys.stdin.read().splitlines()
               if ln.strip() and not ln.strip().startswith(("#", "//"))]

    sys.exit(0 if verify(raw, args.expect, line_len=args.line_len) else 1)


if __name__ == "__main__":
    main()
