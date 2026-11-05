#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pptx_structural_qa.py — content/geometry QA for .pptx WITHOUT a renderer.

When LibreOffice (soffice) / poppler is unavailable (e.g. no sudo to install,
headless box), you cannot render slides to images for visual QA. This script is
the validated fallback: it extracts every text shape with its bounding box and
flags the two classes of defects a renderer would catch:

  1. Missing / misordered / leftover content  -> prints slide-by-slide text
  2. Likely text overflow / box collisions     -> rough chars-per-line heuristic
     + leftover placeholder scan (xxxx / lorem / ipsum / TODO / discover / ...)

Usage:
    venv/bin/python pptx_structural_qa.py /path/to/deck.pptx

Requires: pip install python-pptx  (checked in the repo .venv as 'pptx')

Limits (read these before trusting the output):
  - The overflow flag is heuristic (assumes ~0.035in per pt of font size).
    Large-font single values (a big "1000+", a two-line title, a stat number)
    routinely false-positive — verify those by eye, not by the flag.
  - It cannot see stacking/overlap across SHAPES (two boxes on top of each
    other), icon/line collisions, or color/contrast issues. If any of those
    matter, you still need a real render.
"""
import re
import sys

from pptx import Presentation
from pptx.util import Emu


def main(path: str) -> None:
    prs = Presentation(path)
    print("SLIDE SIZE:", round(Emu(prs.slide_width).inches, 2), "x",
          round(Emu(prs.slide_height).inches, 2), "inches")
    print("NUM SLIDES:", len(prs.slides))
    print("=" * 60)

    for i, slide in enumerate(prs.slides, 1):
        print(f"\n----- SLIDE {i} -----")
        for sh in slide.shapes:
            if sh.has_text_frame:
                txt = sh.text_frame.text.strip()
                if not txt:
                    continue
                w = Emu(sh.width).inches if sh.width else 0
                h = Emu(sh.height).inches if sh.height else 0
                x = Emu(sh.left).inches if sh.left else 0
                y = Emu(sh.top).inches if sh.top else 0
                dim = f"[x={x:.2f} y={y:.2f} w={w:.2f} h={h:.2f}]"

                # Font size: use first run with an explicit size (default 12)
                pt = 12.0
                for para in sh.text_frame.paragraphs:
                    for run in para.runs:
                        if run.font.size:
                            pt = run.font.size.pt
                            break
                    if pt != 12.0:
                        break

                # Rough wrap estimate: available width in cm -> chars per line
                avail_cm = max(w * 2.54 - 0.4, 0.1)
                cpl = max(int(avail_cm / (pt * 0.035)), 2)
                est_lines = 0
                for para in sh.text_frame.paragraphs:
                    seg = "".join(r.text for r in para.runs)
                    est_lines += max(1, -(-len(seg) // cpl))
                need = est_lines * pt * 1.25 / 72
                flag = "  <-- LIKELY OVERFLOW (verify by eye)" \
                    if (h > 0 and need > h + 0.08) else ""
                print(f"  {dim:40s} {flag} :: {txt[:80]}")
            # note pictures (so you can confirm the deck isn't text-only)
            elif sh.shape_type == 13:  # PICTURE
                try:
                    print(f"  [IMG w={Emu(sh.width).inches:.2f} "
                          f"h={Emu(sh.height).inches:.2f}]")
                except Exception:
                    pass

    print("\n" + "=" * 60)
    alltext = "\n".join(
        sh.text_frame.text
        for s in prs.slides for sh in s.shapes if sh.has_text_frame
    )
    for bad in ["xxxx", "lorem", "ipsum", "TODO", "placeholder",
                "present", "discover"]:
        if bad.lower() in alltext.lower():
            print("LEFTOVER PLACEHOLDER HIT:", bad)
    print("leftover placeholder scan done")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1])
