---
name: ocr-and-documents
<<<<<<< LOCAL (this PC)
description: Extract text from PDFs and scanned documents. Use web_extract for remote URLs, pymupdf for local text-based PDFs, marker-pdf for OCR/scanned docs. For DOCX use python-docx, for PPTX see the powerpoint skill.
version: 2.3.0
=======
description: "Extract text from PDFs/scans (pymupdf, marker-pdf)."
version: 2.4.0
>>>>>>> REPO (github)
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [PDF, Documents, Research, Arxiv, Text-Extraction, OCR]
    related_skills: [powerpoint]
---

# PDF & Document Extraction

<<<<<<< LOCAL (this PC)
For DOCX: use `python-docx` (parses actual document structure, far better than OCR). See the **DOCX Table Extraction** section below for examples.
=======
For DOCX: use `python-docx` (parses actual document structure, far better than OCR).
>>>>>>> REPO (github)
For PPTX: see the `powerpoint` skill (uses `python-pptx` with full slide/notes support).
<<<<<<< LOCAL (this PC)
This skill covers **PDFs, scanned documents, and DOCX data extraction**.
=======
This skill covers **PDFs and scanned documents**.
For **multi-format → Markdown** (Word/Excel/PPT/PDF), `markitdown` (Microsoft) is a first-choice lightweight option — see below.
>>>>>>> REPO (github)

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

<<<<<<< LOCAL (this PC)
---
=======
## Notes
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
## PDF Sanitization (Watermark & Logo Removal)
=======
- `web_extract` is always first choice for URLs
- pymupdf is the safe default — instant, no models, works everywhere
- marker-pdf is for OCR, scanned docs, equations, complex layouts — install only when needed
- Both helper scripts accept `--help` for full usage
- marker-pdf downloads ~2.5GB of models to `~/.cache/huggingface/` on first use
- For Word docs: `pip install python-docx` (better than OCR — parses actual structure)
- For PowerPoint: see the `powerpoint` skill (uses python-pptx)
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
Remove text watermarks and header/footer logo images from PDFs using pymupdf. No extra dependencies beyond pymupdf itself.
=======
## PDF Generation with Chinese Text
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
### Step 1: Analyze PDF Structure
=======
When creating PDFs with reportlab and Chinese content, font selection is critical.
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
```python
import pymupdf
doc = pymupdf.open("document.pdf")
=======
### Font Pitfall: DroidSansFallbackFull Lacks ASCII Number Glyphs
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
for i, page in enumerate(doc):
    # Find text watermarks (grid-like repeating text)
    text_blocks = page.get_text("text")
    print(f"\n--- Page {i+1} ---")
    print(text_blocks[:2000])  # preview first 2000 chars
=======
The default Chinese font on Ubuntu WSL (`/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf`) contains CJK ideographs but **does NOT contain ASCII digits (0-9), commas, periods, or parentheses**. PDFs generated with this font will have invisible numbers — `pdftotext` and `pymupdf` extract shows `\0` (null bytes) where numbers should be.
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
    # Find image objects
    for img in page.get_images():
        xref = img[0]
        bbox = page.get_image_bbox(img)
        pix = pymupdf.Pixmap(doc, xref)
        print(f"  Image xref={xref}, size={pix.width}x{pix.height}, bbox={bbox}")
```
=======
**Do NOT use** `DroidSansFallbackFull` for PDF generation with reportlab or fpdf2.
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
### Step 2: Remove Text Watermarks
=======
### Recommended Fonts
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
Use `search_for()` + redact annotations. **Critical: only apply to short text matches (<10 chars)** to avoid removing legitimate content that happens to contain the same string.
=======
| Font | Install | Format | Notes |
|------|---------|--------|-------|
| **WenQuanYi Micro Hei** | `apt-get install fonts-wqy-microhei` | TrueType (.ttc) | Has CJK + ASCII digits. Extract subfont for reportlab. |
| Noto Sans CJK SC | `apt-get install fonts-noto-cjk` | CFF outlines (.ttc) | Not supported by reportlab (CFF/PostScript). Use fpdf2 instead. |
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
```python
import pymupdf
doc = pymupdf.open("document.pdf")
=======
### WQY Micro Hei: Extract from .ttc for reportlab
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
watermark_text = "安信伯君"  # replace with actual watermark string
for page in doc:
    instances = page.search_for(watermark_text)
    for inst in instances:
        # Only redact short matches — watermarks are typically short words
        # Full sentence matches are usually content text
        nearby_text = page.get_text("text", clip=inst).strip()
        if len(nearby_text) < 10:
            page.add_redact_annot(inst, fill=None)  # fill=None = transparent
    page.apply_redactions()
=======
reportlab's TTFont does not support .ttc (TrueType Collection) files. Extract the first subfont:
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
doc.save("cleaned.pdf")
=======
```bash
python3 -c "
from fontTools.ttLib import TTCollection
ttc = TTCollection('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc')
ttc.fonts[0].save('/usr/share/fonts/truetype/wqy/wqy-microhei-regular.ttf')
"
>>>>>>> REPO (github)
```

<<<<<<< LOCAL (this PC)
**Pitfall — content vs watermark**: If the watermark text appears in a legitimate sentence (e.g., "安信伯君专家团队深耕财税咨询..."), `search_for()` will find it. Always verify with the <10 char filter, and use `page.get_text("text", clip=inst)` to inspect context.

### Step 3: Remove Logo Images (Header/Footer)

Two approaches:

| Approach | Pros | Cons |
|----------|------|------|
| **White block overlay** | Simple, preserves PDF integrity | Logo image data still in file |
| **delete_image + overlay** | Clean removal | May cause image reference issues on shared xrefs |

**Recommended: white block overlay** (safer for shared images):

=======
Then register and use:
>>>>>>> REPO (github)
```python
<<<<<<< LOCAL (this PC)
for page in doc:
    for img in page.get_images():
        xref = img[0]
        bbox = page.get_image_bbox(img)
        # Only target header/footer area (e.g., Y < 100 or Y > page_height - 100)
        page_height = page.rect.height
        if bbox.y0 < 100 or bbox.y0 > page_height - 100:
            # Draw white rectangle over the logo
            page.draw_rect(bbox, color=(1,1,1), fill=(1,1,1), width=0)
=======
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont('WQY', '/usr/share/fonts/truetype/wqy/wqy-microhei-regular.ttf'))
>>>>>>> REPO (github)
```

<<<<<<< LOCAL (this PC)
**Clean removal** (use when you want file size reduction, but verify shared xrefs):
=======
This font renders both Chinese text and formatted numbers (e.g. `1,234,567.89` and `(305,000.00)`) correctly, verified with `pdftotext` and `pymupdf` text extraction.
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
```python
for page in doc:
    for img in page.get_images():
        xref = img[0]
        bbox = page.get_image_bbox(img)
        page_height = page.rect.height
        if bbox.y0 < 100 or bbox.y0 > page_height - 100:
            page.draw_rect(bbox, color=(1,1,1), fill=(1,1,1), width=0)
            page.delete_image(xref)
```
=======
### Alternative: fpdf2 with .ttc Directly
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
**Pitfall — shared images**: If all pages share the same logo via xref (common in PDFs), `delete_image` on one page removes it from all pages. Verify with: `page.get_images(full=True)` lists all images with their page-specific bbox.

### Step 4: Save with Optimization
=======
fpdf2 supports .ttc subfont selection natively but also hits the same glyph issue with DroidSansFallbackFull. Install WQY Micro Hei and register by family name:
>>>>>>> REPO (github)

```python
<<<<<<< LOCAL (this PC)
doc.save("output.pdf", garbage=4, deflate=True, clean=True)
=======
from fpdf import FPDF
pdf = FPDF()
pdf.add_font('WQY', '', '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc')
>>>>>>> REPO (github)
```

<<<<<<< LOCAL (this PC)
- `garbage=4` — maximum garbage collection of unused objects
- `deflate=True` — compress streams
- `clean=True` — remove redundant structures
=======
### Verify Font Has Required Glyphs
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
File size may still increase vs original (redaction adds annotations). Expected: 1.5-3x original. If that's a problem, test `garbage=3` or run the file through a PDF optimizer.
=======
Before generating, check for missing glyphs:
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
### Advanced Watermark Removal (Complex PDFs)
=======
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
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
When the basic `search_for()` + redact approach fails — watermarks live in shared XObject
forms, body text shares the same font as the watermark, or the user requires true
transparency (no white blocks) — use the content-stream approach.
=======
## Images → Text: RapidOCR (lightweight Chinese/onscreen OCR)
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
**Key differences from basic approach:**

| Aspect | Basic (redact) | Advanced (3Tr / XObject) |
|--------|----------------|--------------------------|
| Detection | `page.search_for("text")` | Content stream `Tm` position + font name |
| Removal | Redact annotation (opaque overlay) | `3 Tr` rendering mode (invisible text) |
| Watermark source | Page text objects | XObject forms (shared across pages) |
| Body text protection | `<10 char filter` | Position-based matching (grid vs sentence) |
| Visual artifact | Possible white patches | No visual change (transparent) |
| File size | 1.5-3x larger | Minimal increase |

**Decision tree:**

```
search_for() finds watermark text but needs transparency?
  └─ check content streams for XObject references
      ├─ XObject found → Use XObject manipulation (Phase 5)
      └─ No XObject   → Position-based Tm matching (Phase 4)

search_for() finds nothing but watermark is visible?
  └─ Watermark is in shared XObject → inspect /Type/XObject streams
      └─ Use XObject 3Tr approach

Body text contains same string as watermark?
  └─ Must use position-based matching, NOT search_for() + filter
```

**Reference document**: See `references/pdf-watermark-advanced.md` for the complete
6-phase workflow covering:
- Phase 1–2: Deep structure analysis + XObject inspection
- Phase 3: Attack strategy selection
- Phase 4: Position-based content stream matching (Tm coordinates)
- Phase 5: XObject content stream manipulation (3Tr injection, CID replacement)
- Phase 6: Clean LOGO removal (transparent pixel, no white block)
- Full decision tree, pitfall summary, and code examples

### Reference Script

See `scripts/remove_pdf_watermark.py` for a basic reusable script (search_for + redact).
For complex PDFs (XObject/3Tr approach), see `references/pdf-watermark-advanced.md`.

---

## Notes

- `web_extract` is always first choice for URLs
- pymupdf is the safe default — instant, no models, works everywhere
- marker-pdf is for OCR, scanned docs, equations, complex layouts — install only when needed
- Both helper scripts accept `--help` for full usage
- marker-pdf downloads ~2.5GB of models to `~/.cache/huggingface/` on first use
- For Word docs: `pip install python-docx` (better than OCR — parses actual structure)
- For PowerPoint: see the `powerpoint` skill (uses python-pptx)

---

## DOCX Table Extraction (python-docx)

When a user provides an existing .docx file with tables and asks you to extract/read/analyze the data, use python-docx to programmatically read the tables:

### Install
=======
For **plain images** (comics, screenshots, long-platform images like 公众号 or 小红书 image-narratives) use **RapidOCR** (`rapidocr_onnxruntime`). It is far lighter than marker-pdf, handles Chinese well, and is the reliable path when the active model has NO vision capability (vision_analyze 400) — it beats both `web_extract` (no URL) and subagent vision (slow/timeouts).
>>>>>>> REPO (github)

```bash
<<<<<<< LOCAL (this PC)
pip install python-docx
=======
# Install (WSL, no sudo — venv or system with --break-system-packages; pip via 清华源)
PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple python3 -m pip install --break-system-packages -q rapidocr_onnxruntime onnxruntime
>>>>>>> REPO (github)
```

### Basic: Read All Tables

```python
<<<<<<< LOCAL (this PC)
from docx import Document

doc = Document("/path/to/file.docx")
tables = doc.tables

for t_idx, table in enumerate(tables):
    print(f"\n=== Table {t_idx + 1} ({len(table.rows)} rows × {len(table.columns)} cols) ===")

    # Print header row
    if table.rows:
        header = [cell.text.strip() for cell in table.rows[0].cells]
        print(f"Headers: {header}")

    # Print data rows
    for r_idx, row in enumerate(table.rows):
        cells = [cell.text.strip() for cell in row.cells]
        print(f"  Row {r_idx}: {' | '.join(cells)}")
=======
from rapidocr_onnxruntime import RapidOCR
ocr = RapidOCR()
res, _ = ocr('path.png')          # res = [box, text, conf] list
print([t for _, t, _ in res])
>>>>>>> REPO (github)
```

<<<<<<< LOCAL (this PC)
### Common Patterns
=======
**Workflow for very long images** (e.g. a WeChat 漫画 long-image 928×16383):
1. Cut the long image into ~1600px strips with PIL (`Image.open(...)`, `crop`), OCR each strip, concatenate line order.
2. Record the **storyline/sequence** of each strip (strip index → key beats) so the narrative timeline survives the transcription and can be re-ordered later.
3. ⚠️ Chinese OCR produces a few recognition errors (e.g. 「产业园A座301」→「产业田A遮301」). Fix by semantic correction. **Never quote policy/legal text from OCR alone** — verify against the official source before publishing.
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
| Pattern | Code |
|---------|------|
| **Count tables** | `len(doc.tables)` |
| **Get row count** | `len(table.rows)` |
| **Get column count** | `len(table.columns)` |
| **Read specific cell** | `table.rows[1].cells[2].text.strip()` |
| **Read headers** | `[c.text.strip() for c in table.rows[0].cells]` |
| **Find table by header** | Iterate tables, inspect row 0 for a known column name |
| **Map header→column index** | `{h: i for i, h in enumerate(headers)}` then access by name |
| **Detect merged cells** | Check if `cell._tc.get_or_add_tcPr()` has `<w:gridSpan>` |
| **Find all text outside tables** | `[p.text for p in doc.paragraphs]` |
=======
## Non-Standard Documents: Music Scores
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
### Advanced: Extract as Dict (by Header Name)
=======
**Standard OCR pipelines (Tesseract, pytesseract) cannot read Chinese numbered musical notation (jianpu/简谱).** See `references/music-score-ocr.md` for a complete breakdown of approaches tried and their results.
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
```python
def tables_to_dicts(path):
    """Convert all docx tables to list of dicts (header→value)."""
    doc = Document(path)
    result = []
    for table in doc.tables:
        headers = [c.text.strip() for c in table.rows[0].cells]
        data = []
        for row in table.rows[1:]:
            vals = [c.text.strip() for c in row.cells]
            data.append(dict(zip(headers, vals)))
        result.append({"headers": headers, "rows": data})
    return result
```
=======
TL;DR: If `vision_analyze` is available (model supports image input), use it. Otherwise, OCR can recover only title/tempo/performance instruction text from the margins — the actual notation numbers (1–7) are unrecoverable via Tesseract. Fall back to human-assisted transcription: ask the user to read the numbers.
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
### Handle Large Files (Pagination)
=======
### After Transcription: Generate Audio
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
For tables with 50+ rows, print a preview first, then let the user decide:
=======
Once the user provides the jianpu numbers (even approximately), use `scripts/jianpu2midi.py` to:
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
```python
table = doc.tables[0]
n = min(5, len(table.rows))
for r in range(n):
    print(' | '.join(c.text.strip()[:40] for c in table.rows[r].cells))
print(f"... ({len(table.rows)} rows total)")
```
=======
- Generate MIDI audio (GM#22 Harmonica ≈ 口风琴)
- Print right-hand fingering annotations
- Print a structured practice guide (phased tempo, breath control tips, difficulty assessment)
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
### Pitfalls

1. **Empty cells**: `.text.strip()` may return `""`. Filter or replace with `"(empty)"`.
2. **Merged cells**: python-docx represents merged cells as the same object across rows. `cell.text` still works but the merged area spans multiple columns. Check `cell._tc.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}gridSpan')` if you need to detect spans.
3. **Nested tables**: `table.tables` (not `.tables` — nested access via `doc.tables` iterates top-level only). For nested, walk `table._tbl` manually.
4. **Large docs**: Tables with 500+ cells can take seconds. Consider extracting only the table(s) you need.
5. **Header detection**: python-docx doesn't natively mark "header row". Your code assumes row 0 is the header — verify by checking if cells contain column-like labels vs data values.
6. **File paths from WSL**: Convert Windows paths — see the **Path Conversion** section below.

### Path Conversion (WSL ⇄ Windows)

```python
# Windows path in WSL:
win_path = r"D:\360MoveData\Users\Admin\Desktop\file.docx"
wsl_path = win_path.replace("D:", "/mnt/d").replace("\\", "/")
# Result: /mnt/d/360MoveData/Users/Admin/Desktop/file.docx
=======
```bash
# Example: user provides notes, you generate audio + guide
python scripts/jianpu2midi.py --guide --fingering --bpm 80 \
  "5 5 6 5 | 3 2 1 — | 5 5 6 5 | 3 2 1 — |"
>>>>>>> REPO (github)
```

<<<<<<< LOCAL (this PC)
### Typical Use Cases
=======
See `references/jianpu-to-audio.md` for the full workflow, input format table, instrument numbering, and melodica fingering rules.
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
- **Read a skill inventory** from a docx table → extract mapping as dict/memory entry
- **Read financial data** from client-provided docx → import to analysis script
- **Read license/permit registry** → extract for comparison/dedup
- **Read org chart or process flow** represented in a Word table
- **Batch extract** tables from multiple .docx files in a folder
=======
This applies to any document with mixed notation + text (sheet music, lead sheets, tablature) — not just Chinese jianpu.
>>>>>>> REPO (github)
