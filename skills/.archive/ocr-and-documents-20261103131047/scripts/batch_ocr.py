#!/usr/bin/env python3
"""
Batch OCR script for scanned PDFs using pdftoppm + tesseract CLI.
Best for: Large Chinese scanned PDFs (100-600 pages).
Fallback path when pip install pytesseract/marker-pdf times out.

Usage:
  python scripts/batch_ocr.py scanned_book.pdf [--output /tmp/ocr_out] [--lang chi_sim+eng] [--dpi 200]
"""
import argparse, os, subprocess, sys, time

def extract_text_pdfinfo(pdf_path):
    """Get page count from PDF."""
    result = subprocess.run(["pdfinfo", pdf_path], capture_output=True, text=True, timeout=30)
    for line in result.stdout.split('\n'):
        if 'Pages' in line:
            return int(line.split(':')[1].strip())
    return 0

def batch_ocr(pdf_path, output_dir, lang="chi_sim+eng", dpi=200, batch_size=10, max_pages=None):
    os.makedirs(output_dir, exist_ok=True)
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    
    total = extract_text_pdfinfo(pdf_path)
    if total == 0:
        print("❌ Could not determine page count")
        return
    
    if max_pages:
        total = min(total, max_pages)
    
    print(f"📄 {pdf_name}: {total} pages, DPI={dpi}, batch={batch_size}")
    print(f"📂 Output: {output_dir}/")
    
    all_output = []
    start_time = time.time()
    
    for batch_start in range(0, total, batch_size):
        batch_end = min(batch_start + batch_size, total)
        batch_num = batch_start // batch_size + 1
        total_batches = (total + batch_size - 1) // batch_size
        
        t0 = time.time()
        
        # Step 1: pdftoppm - convert batch to PNG
        prefix = os.path.join(output_dir, f"batch_{batch_start+1}_{batch_end}")
        subprocess.run(
            ["pdftoppm", "-png", "-r", str(dpi),
             "-f", str(batch_start + 1), "-l", str(batch_end),
             pdf_path, prefix],
            check=True, capture_output=True, timeout=180
        )
        
        # Step 2: OCR each page
        for pg in range(batch_start + 1, batch_end + 1):
            img_file = f"{prefix}-{pg:06d}.png"
            if not os.path.exists(img_file):
                continue
            
            ocr_out = os.path.join(output_dir, f"page_{pg:05d}")
            subprocess.run(
                ["tesseract", img_file, ocr_out, "-l", lang, "--psm", "6"],
                capture_output=True, timeout=60
            )
            
            # Read result and clean up
            txt_file = f"{ocr_out}.txt"
            if os.path.exists(txt_file):
                with open(txt_file) as f:
                    text = f.read()
                all_output.append(f"\n--- Page {pg} ---\n{text}")
                os.remove(txt_file)
            
            if os.path.exists(img_file):
                os.remove(img_file)
        
        elapsed = time.time() - t0
        chars = sum(len(t) for t in all_output[-batch_size:]) if batch_num > 1 else sum(len(t) for t in all_output)
        pct = batch_end / total * 100
        remaining = (elapsed / batch_size) * (total - batch_end) if batch_end < total else 0
        print(f"  [{batch_num}/{total_batches}] p{batch_start+1}-{batch_end} ({pct:.0f}%) | {elapsed:.0f}s | ~{remaining:.0f}s left")
    
    # Write consolidated output
    final_path = os.path.join(output_dir, f"{pdf_name}_ocr_output.txt")
    with open(final_path, "w") as f:
        f.write(f"Source: {pdf_path}\nPages: {total}\nOCR: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Language: {lang} | DPI: {dpi}\n{'='*60}\n")
        f.write("".join(all_output))
    
    total_time = time.time() - start_time
    total_chars = sum(len(t) for t in all_output)
    print(f"\n✅ Done: {final_path}")
    print(f"   {total} pages, {total_chars} chars, {total_time:.0f}s ({total_time/total:.1f}s/page)")

def main():
    parser = argparse.ArgumentParser(description="Batch OCR scanned PDFs using pdftoppm + tesseract")
    parser.add_argument("pdf", help="Path to scanned PDF")
    parser.add_argument("--output", "-o", default=None, help="Output directory")
    parser.add_argument("--lang", "-l", default="chi_sim+eng", help="Tesseract language (default: chi_sim+eng)")
    parser.add_argument("--dpi", "-r", type=int, default=200, help="Render DPI (default: 200)")
    parser.add_argument("--batch", "-b", type=int, default=10, help="Pages per batch (default: 10)")
    parser.add_argument("--max", "-m", type=int, default=None, help="Max pages to OCR")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.pdf):
        print(f"❌ File not found: {args.pdf}")
        sys.exit(1)
    
    output_dir = args.output or os.path.join(os.path.dirname(args.pdf), "ocr_output")
    
    batch_ocr(args.pdf, output_dir, args.lang, args.dpi, args.batch, args.max)

if __name__ == "__main__":
    main()
