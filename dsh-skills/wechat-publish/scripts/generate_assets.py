#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公众号素材自生成工具（2026.8.5 固化）
====================================
两大能力，解决"封面重复"和"数字横幅需自给"两个痛点：
1. generate_banner(数字)  — 生成与 shuma 01-06 同款的白底蓝色大数字横幅（长条1920x281）
2. generate_cover(标题, 副标题) — 生成原创财税主题封面（深蓝渐变，100%不重复）

用法：
    python3 generate_assets.py banner 07 /tmp/shumabanner_07.jpg
    python3 generate_assets.py cover /tmp/cover.jpg --title "公账上的钱 不申报" --sub "税局是怎么发现的？"

依赖：PIL (Pillow)
中文封面需微软雅黑字体(/mnt/c/Windows/Fonts/msyhbd.ttc)或文泉驿(wqy-zenhei)
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont

# ---------- 常量 ----------
BANNER_W, BANNER_H = 1920, 281
BANNER_BLUE = (30, 60, 240)          # 与原版 shuma 横幅同款主蓝
BANNER_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

COVER_W, COVER_H = 900, 1200
MSYHBD = "/mnt/c/Windows/Fonts/msyhbd.ttc"
SIMHEI = "/mnt/c/Windows/Fonts/simhei.ttf"
GOLD = (255, 193, 87)
WHITE_T = (255, 255, 255)
LIGHT = (200, 215, 235)
TOP_BG = (13, 32, 71)
BOT_BG = (26, 60, 110)


def _font(path, size):
    return ImageFont.truetype(path, size)


def generate_banner(number: str, output: str) -> str:
    """生成与 shuma 01-06 同款的白底蓝色数字横幅。number 如 '07' '10'"""
    img = Image.new("RGB", (BANNER_W, BANNER_H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    # 左侧大号蓝色数字（数字越多字号适当缩小）
    fs = int(235 * (2 / max(1, len(number))))
    fnt = _font(BANNER_FONT, fs)
    bbox = d.textbbox((0, 0), number, font=fnt)
    x0, y0 = 60, (BANNER_H - (bbox[3] - bbox[1])) // 2 - bbox[1]
    d.text((x0, y0), number, font=fnt, fill=BANNER_BLUE)
    # 底部蓝色色带（横跨约左 2/3）
    d.rectangle([0, BANNER_H - 6, int(BANNER_W * 0.69), BANNER_H], fill=BANNER_BLUE)
    img.save(output)
    return output


def generate_cover(output: str, title: str = "公账上的钱 不申报",
                   sub: str = "税局是怎么发现的？",
                   tag: str = "税务合规 · 风险警示",
                   company: str = "苏州盈信财税") -> str:
    """生成原创财税主题封面（深蓝渐变，100%原创不重复）"""
    img = Image.new("RGB", (COVER_W, COVER_H))
    for y in range(COVER_H):
        t = y / COVER_H
        col = (int(TOP_BG[0] + (BOT_BG[0] - TOP_BG[0]) * t),
               int(TOP_BG[1] + (BOT_BG[1] - TOP_BG[1]) * t),
               int(TOP_BG[2] + (BOT_BG[2] - TOP_BG[2]) * t))
        for x in range(COVER_W):
            img.putpixel((x, y), col)
    d = ImageDraw.Draw(img)
    cx = COVER_W // 2

    # 顶部标签 + 分割线
    d.text((cx, 90), tag, font=_font(SIMHEI, 42), fill=GOLD, anchor="mm")
    d.line([(150, 180), (COVER_W - 150, 180)], fill=GOLD, width=3)

    # 主标题（支持多行，按 \n 分）
    lines = title.split("\n") if "\n" in title else [title]
    fsize = 92 if max(len(x) for x in lines) <= 6 else 76
    main_f = _font(MSYHBD, fsize)
    start_y = 420 - (len(lines) - 1) * 62
    for i, ln in enumerate(lines):
        d.text((cx, start_y + i * 125), ln, font=main_f, fill=WHITE_T, anchor="mm")

    # 副标题
    d.text((cx, 700), sub, font=_font(MSYHBD, 56), fill=GOLD, anchor="mm")

    # 底部数据柱状图（代表银行流水/数据监控）
    bars = [(150, 390), (230, 530), (310, 460), (390, 600), (470, 500), (550, 640), (630, 430)]
    for i, (bx, bh) in enumerate(bars):
        col = (80, 130, 210) if i % 2 == 0 else GOLD
        d.rectangle([bx, COVER_H - 360, bx + 60, COVER_H - 360 + bh], fill=col)

    # 底部公司名
    d.text((cx, COVER_H - 70), company, font=_font(MSYHBD, 40), fill=LIGHT, anchor="mm")
    img.save(output)
    return output


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    kind, out = sys.argv[1], sys.argv[2]
    if kind == "banner":
        num = sys.argv[3] if len(sys.argv) > 3 else "07"
        generate_banner(num, out)
        print(f"横幅 {num} 已生成 → {out}")
    elif kind == "cover":
        title = sub = None
        if "--title" in sys.argv:
            title = sys.argv[sys.argv.index("--title") + 1]
        if "--sub" in sys.argv:
            sub = sys.argv[sys.argv.index("--sub") + 1]
        generate_cover(out, title or "公账上的钱 不申报", sub or "税局是怎么发现的？")
        print(f"封面已生成 → {out}")
