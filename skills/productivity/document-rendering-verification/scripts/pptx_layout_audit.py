#!/usr/bin/env python3
"""Audit a pptx_com_metrics.ps1 TSV dump for PPTX layout defects.

WHY: PPTX is a zip of XML; you cannot see overlap by reading it. This script
turns the PowerPoint COM metrics dump into concrete verdicts, so you never
hand-re-derive coordinate math. Two independent layers:

  Layer A (needs only the TSV): arithmetic text-extent check —
      - text_height overflow beyond the box, and
      - pairwise text-RECT intersections (NOT box intersections; two boxes
        overlapping is normal when one text frame is wide and left-aligned).
  Layer B (needs rendered PNGs + slide size): pixel ink-band check —
      crops each text box region from a real render and counts ink row bands.
      A clean deck shows bands >= Lines().Count. bands < lines = lines stacked
      on top of each other; ink taller than the box = overflow. Independent of
      the COM Bound* vertical API (which is junk for multi-line text).

USAGE:
  # after dumping metrics (Windows):
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File pptx_com_metrics.ps1 \
      -Deck deck.pptx -Out shapes.tsv
  # then audit (WSL):
  python pptx_layout_audit.py shapes.tsv
  # with rendered PNGs for the pixel layer (each named slide-01.png .. slide-NN.png):
  python pptx_layout_audit.py shapes.tsv --png-dir img --slide-w 720 --slide-h 405

TSV format understood (the pptx_com_metrics.ps1 header):
  slide name left top w h fontSize lineRule lineSpacing spaceAfter lines maxBoundW minBoundL text
  # lineRule: -1 = multiple-based spacing, 0 = point-based. If any multi-line
  # body shape has lineRule==0, that is the lineSpacing-writes-points bug.
"""
import sys, os, argparse, collections

def load(path):
    rows = []
    with open(path, encoding='utf-8-sig') as fh:
        header = None
        for line in fh:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            if header is None:
                header = line.split("\t")
                continue
            f = line.split("\t")
            rows.append(dict(zip(header, f)))
    return rows

def fnum(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

def text_rect(r, anchor="middle"):
    """Approximate text rect from reliable COM values only (skips junk BoundTop).
    line_height uses font's ~1.2em default; if spacing is multiple-based
    (lineRule==-1) multiply. Handles point-based spacing as font*1.2."""
    fs = fnum(r.get("fontSize")) or 12
    lines = int(fnum(r.get("lines")) or 1)
    lrw = fnum(r.get("lineRule"))
    lsp = fnum(r.get("lineSpacing"))
    line_h = fs * 1.2
    if lrw == -1 and lsp and lsp > 0:
        line_h *= lsp
    th = lines * line_h
    # paragraphs: spaceAfter*(paras-1) is ignored here (TSV has no para count);
    # multi-paragraph boxes get a slight underestimate — treat near-misses as suspicious.
    w = fnum(r.get("w")) or 0
    h = fnum(r.get("h")) or 0
    L = fnum(r.get("minBoundL"))
    BW = fnum(r.get("maxBoundW"))
    if L is None or BW is None:
        return None
    if anchor == "middle":
        top = (fnum(r.get("top")) or 0) + (h - th) / 2.0
    elif anchor == "bottom":
        top = (fnum(r.get("top")) or 0) + (h - th)
    else:
        top = fnum(r.get("top")) or 0
    return dict(L=L, R=L + BW, T=top, B=top + th, th=th, h=h, lines=lines)

def audit_geometry(rows):
    issues = 0
    by = collections.defaultdict(list)
    for r in rows:
        by[int(r["slide"])].append(r)
    print("== Layer A: geometry (overflow + real text-rect overlap) ==")
    for sl in sorted(by):
        rects = {}
        for r in by[sl]:
            tr = text_rect(r)
            if tr is None:
                continue
            tr["text"] = r["text"][:30]
            rects[r["name"]] = tr
            if tr["th"] > tr["h"] + 3:
                issues += 1
                print(f"  S{sl} {r['name']:>6} OVERFLOW text_h={tr['th']:.0f}pt > box_h={tr['h']:.0f}pt  {r['text'][:34]}")
        names = list(rects)
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = rects[names[i]], rects[names[j]]
                # two text rects genuinely crossing in BOTH axes = real collision
                if not (a["R"] > b["L"] and b["R"] > a["L"] and a["B"] > b["T"] and b["B"] > a["T"]):
                    continue
                issues += 1
                print(f"  S{sl} {names[i]} x {names[j]} TEXT RECTS CROSS")
                print(f"        A [{a['L']:.0f}-{a['R']:.0f}]x[{a['T']:.0f}-{a['B']:.0f}] {a.get('text','')}")
                print(f"        B [{b['L']:.0f}-{b['R']:.0f}]x[{b['T']:.0f}-{b['B']:.0f}] {b.get('text','')}")
    print(f"  geometry issues: {issues}")

def ink_bands(im, box, bg, thr=60, minrun=2):
    x0, y0, x1, y1 = box
    reg = im.crop((x0 + 2, y0 + 2, x1 - 2, y1 - 2))
    w, h = reg.size
    px = reg.load()
    rows = []
    for y in range(h):
        c = 0
        for x in range(w):
            r, g, b = px[x, y][:3]
            if abs(r - bg[0]) + abs(g - bg[1]) + abs(b - bg[2]) > thr:
                c += 1
        rows.append(c)
    out = []
    y = 0
    while y < h:
        if rows[y] >= 1:
            y0 = y
            while y < h and rows[y] >= 1:
                y += 1
            if y - y0 >= minrun:
                out.append((y0, y - 1))
        else:
            y += 1
    return out, rows

def audit_pixels(rows, png_dir, sw, sh, anchor="middle"):
    from PIL import Image
    issues = 0
    by = collections.defaultdict(list)
    for r in rows:
        by[int(r["slide"])].append(r)
    print(f"== Layer B: pixel ink-band check (png_dir={png_dir}, slide {sw}x{sh}pt) ==")
    for sl in sorted(by):
        p = os.path.join(png_dir, f"slide-{sl:02d}.png")
        if not os.path.exists(p):
            continue
        im = Image.open(p).convert("RGB")
        W, H = im.size
        sx, sy = W / sw, H / sh
        for r in by[sl]:
            tr = text_rect(r, anchor)
            if tr is None:
                continue
            l = fnum(r.get("left")); t = fnum(r.get("top")); w = fnum(r.get("w")); h = fnum(r.get("h"))
            if None in (l, t, w, h):
                continue
            x0 = max(0, int(l * sx)); y0 = max(0, int(t * sy))
            x1 = min(W, int((l + w) * sx)); y1 = min(H, int((t + h) * sy))
            if x1 - x0 < 8 or y1 - y0 < 4:
                continue
            reg = im.crop((x0 + 2, y0 + 2, x1 - 2, y1 - 2))
            bg = collections.Counter(reg.getdata()).most_common(1)[0][0]
            bands, _ = ink_bands(im, (x0, y0, x1, y1), bg)
            n = len(bands)
            nl = int(fnum(r.get("lines")) or 1)
            ink_h = ((bands[-1][1] - bands[0][0] + 1) / sy) if bands else 0
            note = ""
            if nl >= 2 and n < nl:
                note = f"!! BANDS({n}) < LINES({nl}) — lines stacked"
            if ink_h > h + 3:
                note += " !! OVERFLOW"
            if note:
                issues += 1
            print(f"  S{sl} {r['name']:>6} lines={nl:>2} bands={n:>2} ink={ink_h:>5.0f}pt box={h:>5.0f}pt {note:<34} {r['text'][:26]}")
    print(f"  pixel issues: {issues}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tsv")
    ap.add_argument("--png-dir", default=None)
    ap.add_argument("--slide-w", type=float, default=720)
    ap.add_argument("--slide-h", type=float, default=405)
    ap.add_argument("--anchor", default="middle", choices=["top", "middle", "bottom"],
                    help="vertical anchor of text frames (pptxgenjs + valign middle -> 'middle')")
    a = ap.parse_args()
    rows = load(a.tsv)
    audit_geometry(rows)
    if a.png_dir:
        audit_pixels(rows, a.png_dir, a.slide_w, a.slide_h, a.anchor)

    # Unit-bug signature scan: many boxes point-based but generator meant multiple
    pt = [r for r in rows if fnum(r.get("lineRule")) == 0 and (fnum(r.get("lines")) or 1) >= 2]
    if pt:
        print(f"== WARNING: {len(pt)} multi-line shapes have lineRule==0 (point-based spacing). "
              f"If the generator passed a multiple, that is the stacking bug — fix the property, not the coordinates. ==")

if __name__ == "__main__":
    main()
