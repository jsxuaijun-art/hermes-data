---
name: ocr-and-documents
description: Extract text from PDFs and scanned documents. Use web_extract for remote URLs, pymupdf for local text-based PDFs, marker-pdf for OCR/scanned docs. For DOCX use python-docx, for PPTX see the powerpoint skill.
version: 2.3.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [PDF, Documents, Research, Arxiv, Text-Extraction, OCR]
    related_skills: [powerpoint]
---

# PDF & Document Extraction

For DOCX: use `python-docx` (parses actual document structure, far better than OCR). See the **DOCX Table Extraction** section below for examples.
For PPTX: see the `powerpoint` skill (uses `python-pptx` with full slide/notes support).
This skill covers **PDFs, scanned documents, and DOCX data extraction**.

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

---

## PDF Sanitization (Watermark & Logo Removal)

Remove text watermarks and header/footer logo images from PDFs using pymupdf. No extra dependencies beyond pymupdf itself.

### Step 1: Analyze PDF Structure

```python
import pymupdf
doc = pymupdf.open("document.pdf")

for i, page in enumerate(doc):
    # Find text watermarks (grid-like repeating text)
    text_blocks = page.get_text("text")
    print(f"\n--- Page {i+1} ---")
    print(text_blocks[:2000])  # preview first 2000 chars

    # Find image objects
    for img in page.get_images():
        xref = img[0]
        bbox = page.get_image_bbox(img)
        pix = pymupdf.Pixmap(doc, xref)
        print(f"  Image xref={xref}, size={pix.width}x{pix.height}, bbox={bbox}")
```

### Step 2: Remove Text Watermarks

Use `search_for()` + redact annotations. **Critical: only apply to short text matches (<10 chars)** to avoid removing legitimate content that happens to contain the same string.

```python
import pymupdf
doc = pymupdf.open("document.pdf")

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

doc.save("cleaned.pdf")
```

**Pitfall — content vs watermark**: If the watermark text appears in a legitimate sentence (e.g., "安信伯君专家团队深耕财税咨询..."), `search_for()` will find it. Always verify with the <10 char filter, and use `page.get_text("text", clip=inst)` to inspect context.

### Step 3: Remove Logo Images (Header/Footer)

Two approaches:

| Approach | Pros | Cons |
|----------|------|------|
| **White block overlay** | Simple, preserves PDF integrity | Logo image data still in file |
| **delete_image + overlay** | Clean removal | May cause image reference issues on shared xrefs |

**Recommended: white block overlay** (safer for shared images):

```python
for page in doc:
    for img in page.get_images():
        xref = img[0]
        bbox = page.get_image_bbox(img)
        # Only target header/footer area (e.g., Y < 100 or Y > page_height - 100)
        page_height = page.rect.height
        if bbox.y0 < 100 or bbox.y0 > page_height - 100:
            # Draw white rectangle over the logo
            page.draw_rect(bbox, color=(1,1,1), fill=(1,1,1), width=0)
```

**Clean removal** (use when you want file size reduction, but verify shared xrefs):

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

**Pitfall — shared images**: If all pages share the same logo via xref (common in PDFs), `delete_image` on one page removes it from all pages. Verify with: `page.get_images(full=True)` lists all images with their page-specific bbox.

### Step 4: Save with Optimization

```python
doc.save("output.pdf", garbage=4, deflate=True, clean=True)
```

- `garbage=4` — maximum garbage collection of unused objects
- `deflate=True` — compress streams
- `clean=True` — remove redundant structures

File size may still increase vs original (redaction adds annotations). Expected: 1.5-3x original. If that's a problem, test `garbage=3` or run the file through a PDF optimizer.

### Advanced Watermark Removal (Complex PDFs)

When the basic `search_for()` + redact approach fails — watermarks live in shared XObject
forms, body text shares the same font as the watermark, or the user requires true
transparency (no white blocks) — use the content-stream approach.

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

```bash
pip install python-docx
```

### Basic: Read All Tables

```python
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
```

### Common Patterns

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

### Advanced: Extract as Dict (by Header Name)

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

### Handle Large Files (Pagination)

For tables with 50+ rows, print a preview first, then let the user decide:

```python
table = doc.tables[0]
n = min(5, len(table.rows))
for r in range(n):
    print(' | '.join(c.text.strip()[:40] for c in table.rows[r].cells))
print(f"... ({len(table.rows)} rows total)")
```

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
```

### Typical Use Cases

- **Read a skill inventory** from a docx table → extract mapping as dict/memory entry
- **Read financial data** from client-provided docx → import to analysis script
- **Read license/permit registry** → extract for comparison/dedup
- **Read org chart or process flow** represented in a Word table
- **Batch extract** tables from multiple .docx files in a folder
