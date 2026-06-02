---
name: ocr-and-documents
description: "Extract text from PDFs/scans (pymupdf, marker-pdf)."
version: 2.4.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [PDF, Documents, Research, Arxiv, Text-Extraction, OCR]
    related_skills: [powerpoint]
---

# PDF & Document Extraction

For DOCX: use `python-docx` (parses actual document structure, far better than OCR).
For PPTX: see the `powerpoint` skill (uses `python-pptx` with full slide/notes support).
This skill covers **PDFs and scanned documents**.

## Step 1: Remote URL Available?

If the document has a URL, **always try `web_extract` first**:

```
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])
web_extract(urls=["https://example.com/report.pdf"])
```

This handles PDF-to-markdown conversion via Firecrawl with no local dependencies.

Only use local extraction when: the file is local, web_extract fails, or you need batch processing.

## Step 2: Choose Local Extractor

| Feature | pymupdf (~25MB) | marker-pdf (~3-5GB) |
|---------|-----------------|---------------------|
| **Text-based PDF** | ✅ | ✅ |
| **Scanned PDF (OCR)** | ❌ | ✅ (90+ languages) |
| **Tables** | ✅ (basic) | ✅ (high accuracy) |
| **Equations / LaTeX** | ❌ | ✅ |
| **Code blocks** | ❌ | ✅ |
| **Forms** | ❌ | ✅ |
| **Headers/footers removal** | ❌ | ✅ |
| **Reading order detection** | ❌ | ✅ |
| **Images extraction** | ✅ (embedded) | ✅ (with context) |
| **Images → text (OCR)** | ❌ | ✅ |
| **EPUB** | ✅ | ✅ |
| **Markdown output** | ✅ (via pymupdf4llm) | ✅ (native, higher quality) |
| **Install size** | ~25MB | ~3-5GB (PyTorch + models) |
| **Speed** | Instant | ~1-14s/page (CPU), ~0.2s/page (GPU) |

**Decision**: Use pymupdf unless you need OCR, equations, forms, or complex layout analysis.

If the user needs marker capabilities but the system lacks ~5GB free disk:
> "This document needs OCR/advanced extraction (marker-pdf), which requires ~5GB for PyTorch and models. Your system has [X]GB free. Options: free up space, provide a URL so I can use web_extract, or I can try pymupdf which works for text-based PDFs but not scanned documents or equations."

---

## pymupdf (lightweight)

```bash
pip install pymupdf pymupdf4llm
```

**Via helper script**:
```bash
python scripts/extract_pymupdf.py document.pdf              # Plain text
python scripts/extract_pymupdf.py document.pdf --markdown    # Markdown
python scripts/extract_pymupdf.py document.pdf --tables      # Tables
python scripts/extract_pymupdf.py document.pdf --images out/ # Extract images
python scripts/extract_pymupdf.py document.pdf --metadata    # Title, author, pages
python scripts/extract_pymupdf.py document.pdf --pages 0-4   # Specific pages
```

**Inline**:
```bash
python3 -c "
import pymupdf
doc = pymupdf.open('document.pdf')
for page in doc:
    print(page.get_text())
"
```

---

## marker-pdf (high-quality OCR)

```bash
# Check disk space first
python scripts/extract_marker.py --check

pip install marker-pdf
```

**Via helper script**:
```bash
python scripts/extract_marker.py document.pdf                # Markdown
python scripts/extract_marker.py document.pdf --json         # JSON with metadata
python scripts/extract_marker.py document.pdf --output_dir out/  # Save images
python scripts/extract_marker.py scanned.pdf                 # Scanned PDF (OCR)
python scripts/extract_marker.py document.pdf --use_llm      # LLM-boosted accuracy
```

**CLI** (installed with marker-pdf):
```bash
marker_single document.pdf --output_dir ./output
marker /path/to/folder --workers 4    # Batch
```

---

## Chinese Scanned PDF (Tesseract + chi_sim)

**When to use this path**: The document is scanned Chinese text, and marker-pdf's ~3-5GB is overkill or the system has insufficient disk space. Tesseract (~100MB with chi_sim) is the lightweight alternative.

### Install

```bash
sudo apt-get update && sudo apt-get install -y tesseract-ocr tesseract-ocr-chi-sim
pip install pytesseract pymupdf
# Verify
tesseract --list-langs | grep chi_sim
```

### Extract All Pages (Inline Python)

```python
import pytesseract
from PIL import Image
import pymupdf
import io

doc = pymupdf.open("scanned_doc.pdf")
for i in range(len(doc)):
    pix = doc[i].get_pixmap(dpi=300)  # 300 DPI for accuracy
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    text = pytesseract.image_to_string(img, lang="chi_sim")
    print(f"--- Page {i+1} ---\n{text}\n")
```

**⚠️ Speed**: At 300 DPI, each page takes ~3-10s. At 200 DPI ~1-3s. For a 380-page scanned PDF, 300 DPI → ~20-60 min total.

### Extract Specific Pages Only (TOC-first pattern)

```python
import pymupdf
from PIL import Image
import io

doc = pymupdf.open("doc.pdf")
print(f"Total pages: {len(doc)}")
# OCR just TOC area (usually covers first 5-8 pages)
for i in range(1, min(8, len(doc))):
    pix = doc[i].get_pixmap(dpi=200)
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    text = pytesseract.image_to_string(img, lang="chi_sim")
    print(f"Page {i+1}: {text}")
```

### ⚡ Tesseract 4 Limitation: No Direct PDF Input

**Tesseract 4.x (apt-installed) does NOT support reading PDF files directly.** You'll get:
```
Error in pixReadStream: Pdf reading is not supported
```

**Workaround**: Convert PDF pages to images first, then OCR the images.

Two conversion paths:

| Path | Best for | Install | Speed |
|------|----------|---------|-------|
| **PyMuPDF → PIL Image → pytesseract** | Small PDFs (<50 pages), inline Python | `pip install pymupdf pytesseract` | ~3-10s/page |
| **pdftoppm → tesseract CLI** | Large batches (50-600+ pages), pip timeout | `sudo apt install poppler-utils` | ~1-3s/page |

### Batch Pipeline (pdftoppm + tesseract CLI)

Use when: pip install times out, PDF is large (100+ pages), or you need memory-efficient processing.

```bash
# 1. Install tools
sudo apt-get install -y poppler-utils tesseract-ocr tesseract-ocr-chi-sim
```

```python
import subprocess, os, glob

# Full batch script pattern:
pdf_path = "scanned_book.pdf"
out_dir = "/tmp/ocr_output"
os.makedirs(out_dir, exist_ok=True)

# Get page count
info = subprocess.run(["pdfinfo", pdf_path], capture_output=True, text=True)
pages = int([l for l in info.stdout.split('\n') if 'Pages' in l][0].split(':')[1])

batch_size = 10
for start in range(0, pages, batch_size):
    end = min(start + batch_size, pages)
    prefix = f"{out_dir}/pages_{start+1}_{end}"
    
    # Step A: Convert → images
    subprocess.run(["pdftoppm", "-png", "-r", "300", "-f", str(start+1), "-l", str(end),
                    pdf_path, prefix], timeout=120)
    
    # Step B: OCR each image
    # ⚠️ DO NOT guess filename format with {page_num:06d} or {page_num:03d}!
    # pdftoppm's padding varies by total page count (1-digit, 2-digit, or 3-digit).
    # Use glob to find actual output files instead.
    img_files = sorted(glob.glob(f"{prefix}-*.png"))
    for img in img_files:
        # Extract page number from filename like "prefix-005.png"
        basename = os.path.basename(img)
        page_str = basename.split("-")[-1].replace(".png", "")
        pg = int(page_str.lstrip("0") or "0")
        subprocess.run(["tesseract", img, f"{out_dir}/page_{pg}", "-l", "chi_sim+eng", "--psm", "6"],
                       timeout=60)
        os.remove(img)  # cleanup
```

**Why two-step matters**: pdftoppm is 2-3x faster than PyMuPDF image rendering for large batches, and the CLI path works when `pip install` times out (a common issue in restricted environments).

**⚠️ CRITICAL BUG FIX (2026-05-24)**: The original code used `{pg:06d}.png` (6-digit zero-padded), but `pdftoppm` outputs filenames with **variable-digit padding** — matching the number of digits needed to represent the highest page number. For a 589-page PDF, it uses 3-digit padding (`-005.png`). For a 10-page PDF, it uses 2-digit padding (`-05.png`). Using a fixed format string will **always miss the files** and produce zero output. Always use `glob.glob()` to discover actual filenames.

### ⭐ Efficiency Strategy: TOC-First → Web Search

The most practical pattern for Chinese scanned textbooks (proven on a 380-page scanned Chinese PDF):

```
OCR just TOC (2-8 pages, ~30s)
  → Get chapter structure + author info
  → web_search for full book content/summary
  → Extract core methodology into reference doc
```

**Why this works**: Academic textbooks have stable structures across editions. Once you OCR the TOC (2-6 pages, ~30 seconds), you get the full chapter list and framework. A web search then yields the book's core content, chapter summaries, and key frameworks — without OCR'ing 380 pages at 20+ minutes.

**Proven workflow from this session**:
- Scanned PDF: 张新民、钱爱民《财务报表分析》第2版, ~380 pages, no text layer
- Step 1: OCR pages 1-6 (cover + TOC) → got 10 chapter titles + author info
- Step 2: `web_search("张新民 钱爱民 《财务报表分析》 第2版 目录 核心内容")` → chapter summaries + framework
- Step 3: `web_search("张新民 财务报表分析 核心方法论 资产质量 资本结构 利润质量 现金流质量")` → four-dimensional analysis framework
- Step 4: Created `references/张新民财务报表分析_核心框架摘要.md` with structured methodology
- Time saved: ~6-8 hours (full OCR) → ~15 minutes

### Tesseract vs. marker-pdf for Chinese

Tesseract + chi_sim:
- Install: ~100MB, 30s (apt)
- Chinese accuracy: Good (70-85%)
- Speed: 3-10s/page (CPU)
- Tables/layout: Poor (raw text block)
- Best for: Chinese scanned text-only docs, TOC extraction

marker-pdf:
- Install: 3-5GB, 5-15 min (pip + model download)
- Chinese accuracy: Excellent (90-95%+)
- Speed: 1-14s/page (CPU)
- Tables/layout: Excellent (table-aware)
- Best for: Mixed layout, tables, equations

**Decision**: Use tesseract for chapter structure + text content only. Use marker-pdf for complex layouts, tables, or production-quality extraction.

---

## Arxiv Papers

```
# Abstract only (fast)
web_extract(urls=["https://arxiv.org/abs/2402.03300"])

# Full paper
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])

# Search
web_search(query="arxiv GRPO reinforcement learning 2026")
```

## Split, Merge & Search

pymupdf handles these natively — use `execute_code` or inline Python:

```python
# Split: extract pages 1-5 to a new PDF
import pymupdf
doc = pymupdf.open("report.pdf")
new = pymupdf.open()
for i in range(5):
    new.insert_pdf(doc, from_page=i, to_page=i)
new.save("pages_1-5.pdf")
```

```python
# Merge multiple PDFs
import pymupdf
result = pymupdf.open()
for path in ["a.pdf", "b.pdf", "c.pdf"]:
    result.insert_pdf(pymupdf.open(path))
result.save("merged.pdf")
```

```python
# Search for text across all pages
import pymupdf
doc = pymupdf.open("report.pdf")
for i, page in enumerate(doc):
    results = page.search_for("revenue")
    if results:
        print(f"Page {i+1}: {len(results)} match(es)")
        print(page.get_text("text"))
```

No extra dependencies needed — pymupdf covers split, merge, search, and text extraction in one package.

---

## Notes

- `web_extract` is always first choice for URLs
- pymupdf is the safe default — instant, no models, works everywhere
- marker-pdf is for OCR, scanned docs, equations, complex layouts — install only when needed
- Both helper scripts accept `--help` for full usage
- marker-pdf downloads ~2.5GB of models to `~/.cache/huggingface/` on first use
- For Word docs: `pip install python-docx` (better than OCR — parses actual structure)
- For PowerPoint: see the `powerpoint` skill (uses python-pptx)
