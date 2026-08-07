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
For **multi-format → Markdown** (Word/Excel/PPT/PDF), `markitdown` (Microsoft) is a first-choice lightweight option — see below.

## Step 1: Remote URL Available?

If the document has a URL, **always try `web_extract` first**:

```
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])
web_extract(urls=["https://example.com/report.pdf"])
```

This handles PDF-to-markdown conversion via Firecrawl with no local dependencies.

Only use local extraction when: the file is local, web_extract fails, or you need batch processing.

## Step 1.5: MarkItDown (Microsoft) — lightweight multi-format → Markdown

`markitdown` (Microsoft OSS, `pip install markitdown[all]`) converts **Word (.docx), Excel, PowerPoint, PDF, HTML, audio/video** into Markdown. It is small (no PyTorch, unlike marker-pdf), fast, and handles Chinese text well. Verified in this environment against real tax/legal docs (docx AND pdf), including tables → markdown tables.

**Install** (in the venv; `[all]` pulls PDF/Office/audio deps):
```bash
pip install "markitdown[all]" -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**Usage**:
```bash
markitdown input.docx > output.md   # any supported format
markitdown input.pdf  > output.md
```
Python:
```python
from markitdown import MarkItDown
md = MarkItDown()
text = md.convert("input.docx").text_content
```

**Pitfalls (observed)**
- `.pdf` file with a filename indicating PDF but a broken structure throws `FileConversionException: No /Root object! - Is this really a PDF?`. Check the true format with `head -c 20 file.pdf | xxd` — a real PDF starts with `%PDF`. Some print-save/exported PDFs are structurally invalid despite the extension; try a different source or pymupdf on those.
- Audio/video → text needs `ffmpeg` on PATH (pydub warns if missing). If only imageio-ffmpeg's binary is available, symlink it: `ln -sf <imageio-path>/ffmpeg ~/bin/ffmpeg`.
- Image OCR is NOT included by default in the base install; markitdown keeps images as references. For scanned-image text extraction use marker-pdf or an OCR model instead.
- MarkItDown goes "format → md" only. For the reverse (md → formatted .docx) use `pandoc` or the `word-documents` / `markdown-to-word-converter` skill.

**Decision** between local extractors:
| Tool | Best for | Size |
|------|----------|------|
| **markitdown** | multi-format (docx/xlsx/pptx/pdf→md), text + structure incl. Chinese | few MB |
| **pymupdf** | PDF only: split/merge/search/plain-text, instant, no models | ~25MB |
| **marker-pdf** | OCR of scanned PDFs, equations, complex layouts | ~5GB |

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

## PDF Generation with Chinese Text

When creating PDFs with reportlab and Chinese content, font selection is critical.

### Font Pitfall: DroidSansFallbackFull Lacks ASCII Number Glyphs

The default Chinese font on Ubuntu WSL (`/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf`) contains CJK ideographs but **does NOT contain ASCII digits (0-9), commas, periods, or parentheses**. PDFs generated with this font will have invisible numbers — `pdftotext` and `pymupdf` extract shows `\0` (null bytes) where numbers should be.

**Do NOT use** `DroidSansFallbackFull` for PDF generation with reportlab or fpdf2.

### Recommended Fonts

| Font | Install | Format | Notes |
|------|---------|--------|-------|
| **WenQuanYi Micro Hei** | `apt-get install fonts-wqy-microhei` | TrueType (.ttc) | Has CJK + ASCII digits. Extract subfont for reportlab. |
| Noto Sans CJK SC | `apt-get install fonts-noto-cjk` | CFF outlines (.ttc) | Not supported by reportlab (CFF/PostScript). Use fpdf2 instead. |

### WQY Micro Hei: Extract from .ttc for reportlab

reportlab's TTFont does not support .ttc (TrueType Collection) files. Extract the first subfont:

```bash
python3 -c "
from fontTools.ttLib import TTCollection
ttc = TTCollection('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc')
ttc.fonts[0].save('/usr/share/fonts/truetype/wqy/wqy-microhei-regular.ttf')
"
```

Then register and use:
```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont('WQY', '/usr/share/fonts/truetype/wqy/wqy-microhei-regular.ttf'))
```

This font renders both Chinese text and formatted numbers (e.g. `1,234,567.89` and `(305,000.00)`) correctly, verified with `pdftotext` and `pymupdf` text extraction.

### Alternative: fpdf2 with .ttc Directly

fpdf2 supports .ttc subfont selection natively but also hits the same glyph issue with DroidSansFallbackFull. Install WQY Micro Hei and register by family name:

```python
from fpdf import FPDF
pdf = FPDF()
pdf.add_font('WQY', '', '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc')
```

### Verify Font Has Required Glyphs

Before generating, check for missing glyphs:

```bash
python3 -c "
from fontTools.ttLib import TTCollection, TTFont
path = '/path/to/font.ttc'
try:
    f = TTCollection(path).fonts[0]
except:
    f = TTFont(path)
cmap = f.getBestCmap()
for ch in '0123456789,.()-':
    print(f'{repr(ch)}: {\"OK\" if ord(ch) in cmap else \"MISSING\"}' )
"

## Images → Text: RapidOCR (lightweight Chinese/onscreen OCR)

For **plain images** (comics, screenshots, long-platform images like 公众号 or 小红书 image-narratives) use **RapidOCR** (`rapidocr_onnxruntime`). It is far lighter than marker-pdf, handles Chinese well, and is the reliable path when the active model has NO vision capability (vision_analyze 400) — it beats both `web_extract` (no URL) and subagent vision (slow/timeouts).

```bash
# Install (WSL, no sudo — venv or system with --break-system-packages; pip via 清华源)
PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple python3 -m pip install --break-system-packages -q rapidocr_onnxruntime onnxruntime
```
```python
from rapidocr_onnxruntime import RapidOCR
ocr = RapidOCR()
res, _ = ocr('path.png')          # res = [box, text, conf] list
print([t for _, t, _ in res])
```

**Workflow for very long images** (e.g. a WeChat 漫画 long-image 928×16383):
1. Cut the long image into ~1600px strips with PIL (`Image.open(...)`, `crop`), OCR each strip, concatenate line order.
2. Record the **storyline/sequence** of each strip (strip index → key beats) so the narrative timeline survives the transcription and can be re-ordered later.
3. ⚠️ Chinese OCR produces a few recognition errors (e.g. 「产业园A座301」→「产业田A遮301」). Fix by semantic correction. **Never quote policy/legal text from OCR alone** — verify against the official source before publishing.

## Non-Standard Documents: Music Scores

**Standard OCR pipelines (Tesseract, pytesseract) cannot read Chinese numbered musical notation (jianpu/简谱).** See `references/music-score-ocr.md` for a complete breakdown of approaches tried and their results.

TL;DR: If `vision_analyze` is available (model supports image input), use it. Otherwise, OCR can recover only title/tempo/performance instruction text from the margins — the actual notation numbers (1–7) are unrecoverable via Tesseract. Fall back to human-assisted transcription: ask the user to read the numbers.

### After Transcription: Generate Audio

Once the user provides the jianpu numbers (even approximately), use `scripts/jianpu2midi.py` to:

- Generate MIDI audio (GM#22 Harmonica ≈ 口风琴)
- Print right-hand fingering annotations
- Print a structured practice guide (phased tempo, breath control tips, difficulty assessment)

```bash
# Example: user provides notes, you generate audio + guide
python scripts/jianpu2midi.py --guide --fingering --bpm 80 \
  "5 5 6 5 | 3 2 1 — | 5 5 6 5 | 3 2 1 — |"
```

See `references/jianpu-to-audio.md` for the full workflow, input format table, instrument numbering, and melodica fingering rules.

This applies to any document with mixed notation + text (sheet music, lead sheets, tablature) — not just Chinese jianpu.
