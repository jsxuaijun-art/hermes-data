#!/usr/bin/env python3
"""Count horizontal ink bands inside a cropped region of a rendered slide PNG.

Purpose: Layer B (pixel) verification of a PowerPoint page, scoped to ONE text
box. Exists mainly to (a) confirm a multi-line box really renders N separate
lines, and (b) rule out the classic FALSE POSITIVE where a decorative shape
(rings / arcs / divider / watermark) crosses the text box's bounding rectangle
and its strokes fill the gaps between lines, collapsing the band count to 1.

A real stacking bug reports 1 band even on a tight crop that excludes all
decoration. A decoration artifact reports 2 (or nlines) once you crop away the
artwork -- so always pass a --box that covers the glyphs only.

Comparison truth: `bands` should equal COM's `TextRange.Lines().Count` for the
same shape (see scripts/pptx_com_metrics.ps1). bands < nlines => stacking.
bands > nlines => usually noise, not a defect.

Usage:
  python3 pptx_ink_bands.py slide-01.png --box 0.70,1.50,7.60,3.35 --light-ink
  python3 pptx_ink_bands.py slide-04.png --box 0.7,1.3,9.3,2.2          # dark text on light

--box is x0,y0,x1,y1 in INCHES from the slide's top-left, so it matches the
generator's own coordinates (pptxgenjs / python-pptx). Default slide is
10 x 5.625 in (LAYOUT_16x9); override with --slide-size.

Requires: Pillow.
"""
from __future__ import annotations

import argparse
import sys

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    sys.exit("Pillow required: pip install pillow")


def parse_floats(s: str, n: int, name: str) -> list[float]:
    parts = [p for p in s.replace(" ", "").split(",") if p]
    if len(parts) != n:
        raise argparse.ArgumentTypeError(f"{name} needs {n} comma-separated numbers, got {len(parts)}")
    return [float(p) for p in parts]


def main() -> int:
    ap = argparse.ArgumentParser(description="Count ink row-bands in a slide-PNG crop.")
    ap.add_argument("png", help="rendered slide image")
    ap.add_argument("--box", required=True,
                    help="crop rect x0,y0,x1,y1 in INCHES (glyphs only -- exclude decoration)")
    ap.add_argument("--slide-size", default="10,5.625",
                    help="slide size in inches, default 10,5.625 (LAYOUT_16x9)")
    ap.add_argument("--light-ink", action="store_true",
                    help="glyphs are LIGHT on a dark fill (default: dark glyphs on light)")
    ap.add_argument("--thresh", type=int, default=3,
                    help="min ink pixels per row to count as ink (default 3)")
    ap.add_argument("--min-band", type=int, default=3,
                    help="min rows tall to count as a band (default 3)")
    ap.add_argument("--invert", action="store_true",
                    help="alias for --light-ink, kept so ad-hoc scripts ported by hand still work")
    args = ap.parse_args()

    light = args.light_ink or args.invert
    box = parse_floats(args.box, 4, "--box")
    sw, sh = parse_floats(args.slide_size, 2, "--slide-size")

    im = Image.open(args.png).convert("RGB")
    W, H = im.size
    sx, sy = W / sw, H / sh  # px per inch

    px_box = (int(box[0] * sx), int(box[1] * sy), int(box[2] * sx), int(box[3] * sy))
    if px_box[2] <= px_box[0] or px_box[3] <= px_box[1]:
        return int(bool(sys.exit("crop is empty -- check --box / --slide-size order (x0,y0,x1,y1)")) or 1)

    reg = im.crop(px_box)
    w, h = reg.size
    px = reg.load()
    if px is None:
        return int(bool(sys.exit("could not load pixels")) or 1)

    rows: list[int] = []
    for y in range(h):
        c = 0
        for x in range(w):
            r, g, b = px[x, y]
            ink = (r > 170 and g > 170 and b > 170) if light else (r < 110 and g < 110 and b < 110)
            if ink:
                c += 1
        rows.append(c)

    bands: list[tuple[int, int]] = []
    inb = False
    start = 0
    for i, c in enumerate(rows):
        if c >= args.thresh and not inb:
            inb, start = True, i
        elif c < args.thresh and inb:
            inb = False
            if i - start >= args.min_band:
                bands.append((start, i))
    if inb and h - start >= args.min_band:
        bands.append((start, h))

    print(f"image {W}x{H}  scale {sx:.2f}px/in  crop {px_box}  ink={'light' if light else 'dark'}")
    print(f"bands: {len(bands)}")
    for s, e in bands:
        print(f"  y={s}..{e}  height={(e - s) / sy * 72:.1f}pt")
    if not bands:
        print("!! no ink found -- wrong --box, wrong ink polarity, or genuinely empty region")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
