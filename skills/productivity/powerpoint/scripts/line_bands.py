#!/usr/bin/env python3
"""行带检测：判断一段多行文字是否发生「视觉粘连 / 叠印」（PPT 排版 QA 用）。

原理：把图片裁到【纯文字实际区间】（务必避开装饰图形，否则假阳性），
逐行统计"墨迹像素"（与背景色有明显差异的像素），归并成连续的"行带"。
N 行文字应得到 N 条独立行带；行带数 < 行数 = 多行叠印/粘连。

用法：
  python3 line_bands.py slide-01.png --box 0.70,1.50,7.60,3.35 --expect 2 --ink light
  # box = x1,y1,x2,y2（英寸）；--ink light 表示浅色文字(深底)，dark 表示深色文字(浅底)
  # 幻灯片尺寸默认 10 x 5.625 in（LAYOUT_16x9），可用 --slide 13.33,7.5 覆盖

退出码：0 = 行带数符合预期；1 = 不符（疑似叠印/需人工确认）；2 = 用法错误。
"""
import argparse
import sys

from PIL import Image


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("png")
    ap.add_argument("--box", required=True,
                    help="裁切区 x1,y1,x2,y2，单位英寸（避开装饰图形！）")
    ap.add_argument("--expect", type=int, default=None, help="预期行数")
    ap.add_argument("--ink", choices=["light", "dark"], default="light",
                    help="light=浅色文字(深背景,默认)；dark=深色文字(浅背景)")
    ap.add_argument("--slide", default="10,5.625", help="幻灯片尺寸(英寸)")
    ap.add_argument("--min-px", type=int, default=3, help="墨迹像素数阈值")
    args = ap.parse_args()

    sw, sh = (float(v) for v in args.slide.split(","))
    x1, y1, x2, y2 = (float(v) for v in args.box.split(","))

    im = Image.open(args.png).convert("RGB")
    W, H = im.size
    sx, sy = W / sw, H / sh  # px per inch

    reg = im.crop((int(x1 * sx), int(y1 * sy), int(x2 * sx), int(y2 * sy)))
    w, h = reg.size
    px = reg.load()

    rows = []
    for y in range(h):
        c = 0
        for x in range(w):
            r, g, b = px[x, y]
            lum = (r + g + b) / 3
            if (args.ink == "light" and lum > 170) or (args.ink == "dark" and lum < 90):
                c += 1
        rows.append(c)

    bands, inb, start = [], False, 0
    for i, c in enumerate(rows):
        if c >= args.min_px and not inb:
            inb, start = True, i
        elif c < args.min_px and inb:
            inb = False
            if i - start >= 3:
                bands.append((start, i))
    if inb:
        bands.append((start, h))

    print("image: %dx%d  scale=%.1f px/in" % (W, H, sx))
    print("crop : x %.2f~%.2f in, y %.2f~%.2f in  (ink=%s)" % (x1, x2, y1, y2, args.ink))
    print("行带数 bands: %d" % len(bands))
    for s, e in bands:
        print("  band y=%d..%d  height=%.1fpt" % (s, e, (e - s) / sy * 72))

    if args.expect is None:
        print("提示：加 --expect N 可自动判定")
        return 0
    ok = len(bands) == args.expect
    print("期望 %d 行 -> %s" % (args.expect, "OK" if ok else "!!BANDS MISMATCH"))
    if not ok:
        print("可能原因:①行距过紧导致多行粘连(把 lineSpacingMultiple 提到 1.25~1.3)"
              " ②裁切区仍含装饰图形(缩小 box 避开) ③文字溢出/换行数变了")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
