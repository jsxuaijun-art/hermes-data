#!/usr/bin/env python3
"""Rasterize every page of a PDF to PNG using PyMuPDF — no poppler needed.

Companion to docx_com_metrics.ps1 / pptx_com_metrics.ps1: those export a PDF with
the real Office renderer, this turns that PDF into page images for the visual pass.

Usage:
    python pdf_to_png.py <in.pdf> <out_dir> [dpi]

Output: <out_dir>/<stem>-01.png, -02.png, ... plus one line per page and a final
`pages: N` line. Cross-check N against the COM page count (ComputeStatistics(2))
— a mismatch means the PDF export truncated.

Prereq (WSL, no sudo needed):
    pip install -q pymupdf -i https://pypi.tuna.tsinghua.edu.cn/simple

At dpi=110 an A4 page is ~910x1287px: enough for a vision model to read table
cells and spot clipping.
"""
import pathlib
import sys


def rasterize(src: str, out_dir: str, dpi: int = 110) -> int:
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    try:
        import pymupdf as fitz  # >= 1.24
    except ImportError:
        import fitz  # older releases; prints a deprecation warning

    doc = fitz.open(src)
    stem = pathlib.Path(src).stem
    for i, page in enumerate(doc, 1):
        pix = page.get_pixmap(dpi=dpi)
        path = out / f"{stem}-{i:02d}.png"
        pix.save(path)
        print(path, f"{pix.width} x {pix.height}")
    print(f"pages: {doc.page_count}")
    return 0


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 110
    return rasterize(sys.argv[1], sys.argv[2], dpi)


if __name__ == "__main__":
    sys.exit(main())
