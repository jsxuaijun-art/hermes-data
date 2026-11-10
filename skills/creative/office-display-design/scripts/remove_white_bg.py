#!/usr/bin/env python3
"""Remove the near-white background from a logo/PNG, keeping only the colored graphic.

Use when a logo sitting on a white/light box must merge into a dark background
(welcome screen, PPT, business cards). 白底 LOGO → 透明底, 只留图形。

Usage:
  python3 remove_white_bg.py <in.png> [out.png] [--bg R G B] [--preview]

Defaults:
  out.png   = <in>_transparent.png
  --bg      composite preview onto this RGB background (default 10 26 47 = 深蓝 #0a1a2f)
  --preview also write <out>_on_bg.png preview and print retain/color stats

Method: per-pixel MIN-channel alpha (pass 1). min(r,g,b) >= 225 -> alpha 0
(fully transparent); <= 190 -> opaque; linear fade in between so antialiased
edges stay soft (no hard white/gray halo). PASS 2 (2026-11-05, real 盈信 logo):
the min-channel fade can leave a thin (~1-2px) LIGHT-GRAY line at the PNG's very
bottom edge — the antialiased edge of the original white box. On a dark
background it reads as "a white horizontal line under the logo". Kill it by also
zeroing low-saturation AND bright pixels (sat = max-min < 60 AND min-channel >
150): removes all gray/white residue while keeping high-saturation colored
strokes (red etc.) intact. Pure-PIL fallback runs when numpy is missing (slower
but identical result, both passes applied).

Acceptance: look at "保留不透明像素占比" (should be meaningfully >0) and the
平均RGB (a saturated color means the graphic survived). Verify the final on the
real background with a vision model (direct multi-modal POST, not vision_analyze
when the running session routes images to a text-only main model).

Verified 2026-11-05 on 盈信 logo (380x378 white box + red 纹样):
27.8% opaque pixels retained, avg RGB (195,23,31) pure red; composites cleanly
onto navy #0a1a2f. Output saved once as logo_transparent.png for reuse.
Pass 2 (v5, same day): user saw "a white horizontal line under the logo" — a
~1-2px light-gray line at the PNG's bottom edge (white-box antialiasing) that
pass 1's fade left. Pass 2 cleared 2168 gray/white px (26.3% opaque left), and
vision on the rendered design confirmed no line/edge residue.
"""
import os
import sys


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)
    src = args[0]
    out = args[1] if len(args) > 1 and not args[1].startswith('--') \
        else os.path.splitext(src)[0] + '_transparent.png'
    bg = None
    preview = False
    i = 1
    while i < len(args):
        a = args[i]
        if a == '--bg':
            bg = tuple(int(x) for x in args[i + 1:i + 4][:3])
            i += 4
        elif a == '--preview':
            preview = True
            i += 1
        else:
            i += 1

    try:
        from PIL import Image
    except ImportError:
        print("需要 Pillow: pip install Pillow")
        sys.exit(1)

    im = Image.open(src).convert('RGBA')
    try:
        import numpy as np
        a = np.array(im).astype(np.int16)
        minch = a[:, :, 0].copy()
        np.minimum(minch, a[:, :, 1], out=minch)
        np.minimum(minch, a[:, :, 2], out=minch)
        al = np.clip((225.0 - minch) / (225.0 - 190.0) * 255.0, 0, 255)
        a[:, :, 3] = np.clip(a[:, :, 3] * (al / 255.0), 0, 255).astype(np.uint8)
        # pass 2: kill light-gray/white antialiasing residue (e.g. bottom-edge
        # line of the original white box) — low saturation AND bright.
        mx = np.maximum(np.maximum(a[:, :, 0], a[:, :, 1]), a[:, :, 2])
        a[:, :, 3][(mx - minch < 60) & (minch > 150)] = 0
        out_im = Image.fromarray(a.astype(np.uint8), 'RGBA')
        opaque = float((a[:, :, 3] > 10).mean())
        avg = a[a[:, :, 3] > 10][:, :3].mean(axis=0)
    except ImportError:
        px = im.load()
        out_im = Image.new('RGBA', im.size)
        op = out_im.load()
        W, H = im.size
        tot = keep = 0
        rs = gs = bs = 0
        for y in range(H):
            for x in range(W):
                r, g, b, al = px[x, y]
                m = min(r, g, b)
                if m >= 225:
                    al = 0
                elif m > 190:
                    al = int(al * (225 - m) / (225 - 190))
                # pass 2: light-gray/white antialiasing residue -> transparent
                if max(r, g, b) - m < 60 and m > 150:
                    al = 0
                op[x, y] = (r, g, b, al)
                tot += 1
                if al > 10:
                    keep += 1
                    rs += r
                    gs += g
                    bs += b
        opaque = keep / tot if tot else 0
        avg = (rs / keep, gs / keep, bs / keep) if keep else (0, 0, 0)

    out_im.save(out)
    print(f"保存 {out} ({im.size[0]}x{im.size[1]})")
    print(f"保留不透明像素 {opaque * 100:.1f}%  平均RGB {tuple(int(v) for v in avg)}")
    if preview:
        bgr = bg or (10, 26, 47)
        canvas = Image.new('RGBA', (500, 500), bgr + (255,))
        thumb = out_im.copy()
        thumb.thumbnail((160, 160))
        canvas.paste(thumb, ((500 - thumb.width) // 2, (500 - thumb.height) // 2), thumb)
        pv = os.path.splitext(out)[0] + '_on_bg.png'
        canvas.save(pv)
        print(f"预览合成 {pv}")
    print("验收: 图形主体占比>0 且平均RGB带饱和色=保住了; 全浅/全透=误杀,"
          "下调阈值(190→更接近225)重跑。")


if __name__ == '__main__':
    main()
