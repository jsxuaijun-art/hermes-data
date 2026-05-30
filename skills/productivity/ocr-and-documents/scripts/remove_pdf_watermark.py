#!/usr/bin/env python3
"""
remove_pdf_watermark.py — Remove text watermarks and header/footer logos from PDFs.

Usage:
    python remove_pdf_watermark.py input.pdf -w "公司名称" -o output.pdf
    python remove_pdf_watermark.py input.pdf -w "机密" -x 1040 -o cleaned.pdf
    python remove_pdf_watermark.py input.pdf -w "CONFIDENTIAL" --analyze-only

Requires: pip install pymupdf

Author: Hermes Agent — built for 财税/代账 PDF sanitization workflows
"""

import pymupdf
import argparse
import sys
import os


def analyze_pdf(doc: pymupdf.Document) -> dict:
    """Analyze PDF structure — find images, text patterns, and per-page stats."""
    info = {"pages": len(doc), "images": [], "text_samples": []}
    for i, page in enumerate(doc):
        page_info = {
            "page": i + 1,
            "images": [],
            "text_preview": page.get_text("text")[:500],
        }
        for img in page.get_images(full=True):
            xref = img[0]
            bbox = page.get_image_bbox(img)
            pix = pymupdf.Pixmap(doc, xref)
            page_info["images"].append({
                "xref": xref,
                "width": pix.width,
                "height": pix.height,
                "bbox": f"{bbox.x0:.0f},{bbox.y0:.0f},{bbox.x1:.0f},{bbox.y1:.0f}",
            })
        info["text_samples"].append(page_info)
    return info


def remove_text_watermark(page: pymupdf.Page, text: str, max_len: int = 10):
    """
    Remove text watermarks from a page.
    Only redacts matches where the surrounding text is shorter than max_len
    (avoids removing legitimate content that contains the watermark string).
    """
    instances = page.search_for(text)
    count = 0
    for inst in instances:
        nearby = page.get_text("text", clip=inst).strip()
        if len(nearby) <= max_len:
            page.add_redact_annot(inst, fill=None)
            count += 1
        else:
            print(f"  ⚠ SKIP (content text): \"{nearby[:50]}...\"")
    page.apply_redactions()
    return count


def remove_logo_images(page: pymupdf.Page, margin: float = 100, clean_xrefs: bool = False):
    """
    Remove logo images from header/footer area.
    - margin: Y threshold from top (Y < margin) or bottom (Y > height - margin)
    - clean_xrefs: if True, also delete the image xref (reduces file size but
      can cause issues with shared images across pages)
    """
    page_height = page.rect.height
    removed = 0
    for img in page.get_images(full=True):
        xref = img[0]
        bbox = page.get_image_bbox(img)
        if bbox.y0 < margin or bbox.y0 > page_height - margin:
            print(f"  Removing image xref={xref} at Y={bbox.y0:.0f}, size={bbox.width:.0f}x{bbox.height:.0f}")
            page.draw_rect(bbox, color=(1, 1, 1), fill=(1, 1, 1), width=0)
            if clean_xrefs:
                try:
                    page.delete_image(xref)
                except Exception as e:
                    print(f"  ⚠ delete_image failed for xref={xref}: {e}")
            removed += 1
    return removed


def main():
    parser = argparse.ArgumentParser(
        description="Remove text watermarks and header/footer logos from PDFs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s report.pdf -w "CONFIDENTIAL" -o clean.pdf
  %(prog)s report.pdf -w "安信伯君" -x 1040 -o clean.pdf
  %(prog)s report.pdf --analyze-only
        """,
    )
    parser.add_argument("input", help="Input PDF file")
    parser.add_argument("-w", "--watermark", help="Text watermark string to remove")
    parser.add_argument("--watermark-max-len", type=int, default=10,
                        help="Max text length to consider as watermark (default: 10)")
    parser.add_argument("-r", "--remove-logo", action="store_true",
                        help="Remove header/footer logo images")
    parser.add_argument("--margin", type=float, default=100,
                        help="Y margin for logo detection (default: 100)")
    parser.add_argument("-x", "--clean-xrefs", action="store_true",
                        help="Also delete image xrefs (cleaner but risk with shared images)")
    parser.add_argument("-o", "--output", help="Output PDF path (default: input_cleaned.pdf)")
    parser.add_argument("--analyze-only", action="store_true",
                        help="Only analyze PDF structure, don't modify")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: file not found: {args.input}")
        sys.exit(1)

    if not args.analyze_only and not args.watermark and not args.remove_logo:
        print("Error: nothing to do. Use --watermark, --remove-logo, or --analyze-only")
        sys.exit(1)

    doc = pymupdf.open(args.input)
    total_watermarks = 0
    total_logos = 0

    print(f"📄 {doc.page_count} pages — {args.input}")
    print()

    # Analyze phase
    info = analyze_pdf(doc)
    print("=== Structure Analysis ===")
    for p in info["text_samples"]:
        print(f"  Page {p['page']}: {len(p['images'])} images")
        if p["images"]:
            for img in p["images"]:
                print(f"    xref={img['xref']} {img['width']}x{img['height']}px at [{img['bbox']}]")
    print()

    if args.analyze_only:
        doc.close()
        print("✅ Analyze only — no changes made.")
        return

    # Sanitize
    print("=== Sanitizing ===")
    for i, page in enumerate(doc):
        page_num = i + 1
        print(f"Page {page_num}:")

        if args.watermark:
            n = remove_text_watermark(page, args.watermark, args.watermark_max_len)
            if n:
                print(f"  Removed {n} watermark(s): \"{args.watermark}\"")
            total_watermarks += n

        if args.remove_logo:
            n = remove_logo_images(page, args.margin, args.clean_xrefs)
            total_logos += n

        print()

    # Save
    output = args.output or args.input.rsplit(".", 1)[0] + "_cleaned.pdf"
    doc.save(output, garbage=4, deflate=True, clean=True)
    doc.close()

    original_size = os.path.getsize(args.input)
    new_size = os.path.getsize(output)

    print("=== Summary ===")
    print(f"  Watermarks removed: {total_watermarks}")
    print(f"  Logo images removed: {total_logos}")
    print(f"  Input:  {original_size / 1024:.0f} KB")
    print(f"  Output: {new_size / 1024:.0f} KB  ({output})")
    print(f"  Delta:  {new_size / original_size:.1f}x")
    print()


if __name__ == "__main__":
    main()
