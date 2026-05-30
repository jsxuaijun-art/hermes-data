# PDF Watermark & Logo Removal — Pattern Catalog

## Common Watermark Patterns

| Type | Example | Detection | Removal Strategy |
|------|---------|-----------|------------------|
| Grid text overlay | "公司名称" repeated 15x/page at 45° | `page.search_for()` — same text, many instances | Redact each instance; filter <10 chars to avoid content |
| Shared header logo | Company logo ~1730x134px, xref shared across all pages | `page.get_images()` + check xref and Y bbox | White rect overlay; `delete_image` if no shared xref issue |
| Page-stamp watermark | Single centered "DRAFT" or "CONFIDENTIAL" | `page.search_for()` — 1 instance/page at center | Redact normally |
| Image-based watermark | Semi-transparent logo as full-page overlay | Low opacity image, check `get_images()` in non-header area | White rect overlay at image bbox |

## Advanced Patterns (Content Stream / XObject)

| Type | Example | Detection | Removal Strategy |
|------|---------|-----------|------------------|
| **XObject-form text** | Shared form `/KSPX1` with CID-encoded text | `page.get_contents()` → inspect XObject streams | Phase 5: XObject 3Tr injection or CID removal |
| **Large-font grid** | `/FT26 240 Tf` repeated at grid intervals | Parse content stream BT...ET blocks + Tm coordinates | Phase 4: Insert `3 Tr` before Tf in matching blocks |
| **CID-encoded CJK** | `<b0b2><d7a2><d0c5><befd>` Tj in XObject | Inspect XObject raw content for CID sequences | Phase 5: regex replace CID sequence with empty string |
| **Shared-font conflict** | Watermark + body both use `/FT26` | `page.get_text("dict")` → check font per text block | Phase 4: Position-based Tm matching (grid vs paragraph) |

## Short-Text Filter (Critical Safety)

When removing text watermarks, ALWAYS filter by text length:

```python
nearby = page.get_text("text", clip=inst).strip()
if len(nearby) < 10:  # watermark threshold
    page.add_redact_annot(inst)
```

**Why**: The watermark string may appear in legitimate content text. In a tax law PDF, "安信伯君" appeared in a sentence "安信伯君专家团队深耕财税咨询近二十年" (24 chars). Without the filter, this sentence's watermark match would be deleted, destroying document content.

## Shared Image Xref Problem

```python
# All pages may reference the same image xref
page.get_images(full=True)
# => [(8, 0, ...), ...]  # same xref=8 on every page
```

When images are shared by xref:
- Using `page.delete_image(xref)` on one page deletes for ALL pages
- Safer: use white rect overlay instead of delete_image
- If you must use delete_image, verify the image is NOT shared: different xrefs per page

## Logo Removal — Transparent Pixel Approach (No White Block)

For clean logo removal when the user requires NO white rectangles:

```python
# Replace shared logo with 1x1 transparent pixel
from pymupdf import Pixmap
white_pix = Pixmap(pymupdf.csGRAY, 1, 1, [255], False)
doc.xref_set_key(logo_xref, "Width", "1")
doc.xref_set_key(logo_xref, "Height", "1")
doc.update_stream(logo_xref, white_pix.tobytes())

# Clean up page content streams (remove Do references)
# See references/pdf-watermark-advanced.md Phase 6 for full code
```

## File Size Behavior

After redaction processing:
- Visual-only change → 1-3x file size increase (redaction annotations add data)
- Use `doc.save("output.pdf", garbage=4, deflate=True, clean=True)` to minimize
- If file size matters more than clean output, try `garbage=3` instead of 4
- Run through a PDF optimizer (e.g., Adobe Acrobat "Reduce File Size") for further reduction

**3Tr approach file size**: Inserting `3 Tr` adds ~4 bytes per text block — negligible
overhead. No redaction annotations means no file size inflation.

## Verification Checklist

1. Open output PDF — visually scan all pages
2. Count remaining occurrences of watermark text: `page.search_for(watermark)` 
3. Check that legitimate content wasn't removed (compare original vs cleaned)
4. Check header/footer area for logo remnants
5. Check file size is reasonable (expect 1.5-3x original for redact; near-original for 3Tr)

## Real Examples

### Example 1: Basic (Tax Law PDF from session 2026-05-11)

```
File: 增值税法18项核心变化.pdf (996 KB, 4 pages)
Watermark: "安信伯君" — 60 total (15 per page, grid pattern)
Logo: Company logo, xref=8 shared across pages, 1730x134px, header area

Result:
  - All 60 watermarks removed
  - Logo covered with white rect (no delete, to avoid shared xref issue)
  - Only 1 remaining "安信伯君" was legitimate content text (preserved)
  - Output: 2.9 MB (2.9x original — acceptable for redaction processing)
```

### Example 2: Advanced (Same PDF, transparency approach)

```
File: Same PDF, processed with 3Tr+XObject approach (session 2026-05-11 v11)
Watermark: In XObject forms (/KSPX1 /KSPX3 /KSPX5 /KSPX7 /KSPX9)  
           AND in page content streams at grid Tm positions
Logo: xref=8 shared, 1730x134px

Approach:
  - Page streams: Insert "3 Tr" before "/FT26" in watermark BT blocks
  - XObjects: Insert "3 Tr" before "/FT26" (watermark only, body untouched)
  - Logo: Replace image at xref level with 1x1 white pixel + clean Do refs

Result:
  - All watermarks invisible (3Tr)
  - Body text "安信伯君专家团队深耕" untouched (position-based filtering)
  - Logo gone (no white block)
  - Output: ~1 MB (near-original — no redaction overhead)
  - No visual artifacts, no white patches
```
