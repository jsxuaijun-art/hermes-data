# Advanced PDF Watermark Removal — XObject / 3Tr / Content Stream

## When to Use This (Not the Basic Approach)

The basic `search_for()` + redact approach in `scripts/remove_pdf_watermark.py` works for
simple PDFs where the watermark appears as normal text objects. Use the ADVANCED approach
when ANY of these is true:

| Signal | How to Check |
|--------|-------------|
| `search_for()` finds 0 instances but watermark is visible | Watermark is embedded in a shared XObject form |
| Watermark uses unusual font encoding (CID/CJK) | Inspect content stream with `page.get_contents()` |
| Cannot distinguish watermark from body text by font name alone | Both use same font (e.g., `/FT26`) |
| Redaction leaves visual artifacts or breaks layout | Redaction changes object positioning |
| Body text contains the same string as the watermark | E.g. "安信伯君" in both watermark and "安信伯君专家团队深耕" |
| User explicitly requires NO white blocks or fill | Redact annotations may show white patches |

---

## Workflow (6 Phases)

### Phase 1: Deep Structure Analysis

```python
import pymupdf
doc = pymupdf.open("input.pdf")

for i, page in enumerate(doc):
    print(f"\n=== Page {i+1} ===")
    # 1a. Get text via pymupdf's text extraction
    text = page.get_text("text")
    print("TEXT:", text[:2000])
    
    # 1b. Get raw content stream(s)
    xrefs = page.get_contents()
    for xr in xrefs:
        stream = doc.xref_stream(xr)
        if stream:
            raw = stream.decode() if isinstance(stream, bytes) else stream
            print(f"\nCONTENT STREAM xref={xr} ({len(raw)} bytes):")
            print(raw[:3000])
    
    # 1c. Check for XObject references in content stream
    #    (look for "/XObject" or "Do" operators referencing external forms)
    
    # 1d. List images
    for img in page.get_images(full=True):
        xref = img[0]
        bbox = page.get_image_bbox(img)
        pix = pymupdf.Pixmap(doc, xref)
        print(f"  IMAGE xref={xref}, {pix.width}x{pix.height}, bbox={bbox}")
```

### Phase 2: Analyze XObjects (Shared Form Watermarks)

If the content stream references `/XObject << /KSPX1 ... >>` or similar form names,
those forms may carry the watermark. Inspect the XObject streams:

```python
# Find XObjects via page resources
page_xref = page.parent.page_xref(page.number)
resources = doc.xref_object(page_xref)  # or page.get_xml_metadata()
print(resources)

# Or search all XObjects in the document
for xref in range(1, doc.xref_length()):
    obj = doc.xref_object(xref)
    if "/Subtype" in obj and "/Form" in obj:
        stream = doc.xref_stream(xref)
        if stream and len(stream) < 50000:  # reasonable size
            raw = stream.decode() if isinstance(stream, bytes) else stream
            print(f"\nXObject xref={xref}:")
            print(raw[:2000])
```

**Key patterns in XObject watermarks:**
- Text appears as CID codes: `<b0b2><d7a2><d0c5><befd>` (e.g., "安信伯君" encoded)
- Uses `Tf` with a specific font name and large size (240+ points)
- Appears in a BT...ET block with `Tm` (text matrix) positioning
- The same XObject xref is referenced/Do'd on multiple pages

### Phase 3: Plan the Attack Strategy

Based on analysis results, choose strategy:

| Finding | Strategy |
|---------|----------|
| Watermark as page-level text, unique font or distinctive position | Basic `search_for()` + redact |
| Watermark in page content stream, same font as body | **Position-based Tm matching** (see Phase 4) |
| Watermark in XObject form(s) | **XObject content manipulation** (see Phase 5) |
| Both page stream AND XObject | **Combined approach** |
| Watermark and body share font but different size | Match by font size in content stream |

### Phase 4: Position-Based Content Stream Matching

When watermark and body text share the same font, match by position. Watermarks typically
appear in a grid pattern with identical Tm (text matrix) coordinates per instance.

```python
import re

def find_watermark_blocks(content: str, font_name: str, page_width: float, page_height: float):
    """Find text blocks in content stream that are likely watermarks."""
    blocks = []
    
    # Match BT...ET blocks
    bt_et_pattern = re.compile(r'BT(.*?)ET', re.DOTALL)
    
    for match in bt_et_pattern.finditer(content):
        block = match.group(1)
        # Get Tm coordinates
        tm_match = re.search(r'(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+Tm', block)
        if tm_match:
            x = float(tm_match.group(5))
            y = float(tm_match.group(6))
            
            # Check if this uses the watermark font
            if font_name in block:
                # Watermark text is typically:
                # - Centered or tiled across the page
                # - At consistent x/y intervals forming a grid
                # - Not near page edges (not header/footer)
                blocks.append({
                    "x": x, "y": y,
                    "start": match.start(),
                    "end": match.end(),
                    "block": block
                })
    
    return blocks


# In the actual implementation, after finding watermark blocks,
# insert "3 Tr" (invisible rendering mode) before the Tf command:
#
# Original: BT /FT26 240.00 Tf ... Tm (安信伯君) Tj ET
# Modified: BT 3 Tr /FT26 240.00 Tf ... Tm (安信伯君) Tj ET
```

**Pitfall — stream encoding**: Content streams may be ASCIIHexDecode or FlateDecode
encoded. pymupdf's `doc.xref_stream(xref)` returns the decoded content, but after
modification you need to re-encode it properly. Simplest approach:

```python
# Get the raw decoded stream, modify it as text
stream = doc.xref_stream(xref)
content = stream.decode() if isinstance(stream, bytes) else stream

# Make modifications to content string...

# Write back: pymupdf handles re-compression automatically
doc.update_stream(xref, content.encode())
```

### Phase 5: XObject Content Manipulation

When watermarks live in XObject forms shared across pages:

```python
def clean_xobject_watermark(doc: pymupdf.Document, xref: int, font_name: str):
    """
    Remove watermark text from an XObject content stream.
    Strategy: replace the watermark CID sequence with a no-op, or entirely remove
    the BT...ET block containing it.
    """
    stream = doc.xref_stream(xref)
    raw = stream.decode() if isinstance(stream, bytes) else stream
    
    # Option A: Delete entire BT...ET blocks containing the watermark font
    import re
    bt_block_pattern = re.compile(
        r'BT\s*.*?' + re.escape(f'/{font_name}') + r'.*?ET',
        re.DOTALL
    )
    modified = bt_block_pattern.sub('', raw)
    
    # Option B (preferred): Insert "3 Tr" before Tf to make text invisible
    # This preserves PDF structure and avoids syntax errors
    modified = raw.replace(
        f'/{font_name}',
        f'3 Tr /{font_name}'
    )
    # Fix any double-double issues: "3 Tr 3 Tr /FT26" → "3 Tr /FT26"
    modified = re.sub(r'(3 Tr\s+){2,}', '3 Tr ', modified)
    
    doc.update_stream(xref, modified.encode())
```

**CID text replacement** (alternative cleaner approach):

```python
def remove_cid_text_from_xobject(raw: str, cid_bytes: str = '<b0b2><d7a2><d0c5><befd>'):
    """
    Remove specific CID-encoded text from XObject content.
    CID bytes encode "安信伯君" or similar CJK text in custom encodings.
    """
    # Pattern: (CID sequence) Tj
    pattern = re.escape(cid_bytes) + r'\s*Tj'
    return re.sub(pattern, '', raw)
```

### Phase 6: LOGO Removal (Clean, No White Block)

When you need true logo removal without white rectangles:

```python
def remove_logo_clean(doc: pymupdf.Document, logo_xref: int):
    """
    Remove a logo image by replacing it with a transparent 1x1 pixel.
    This avoids the white-block issue while preserving PDF integrity.
    """
    # Create a 1x1 transparent PNG
    # (generate_id is needed for the replace_image API)
    # pymupdf >= 1.23.0: use page.replace_image()
    
    from pymupdf import Pixmap
    
    # Get the current image to know its type
    orig_pix = Pixmap(doc, logo_xref)
    
    # Create a 1x1 transparent replacement
    replacement = Pixmap(pymupdf.csGRAY, (0,))  # 1x1 black pixel
    # Or: replacement = Pixmap(pymupdf.csGRAY, 1, 1, [0], False)
    
    # On each page: replace the image
    for page in doc:
        for img in page.get_images():
            xref = img[0]
            if xref == logo_xref:
                bbox = page.get_image_bbox(img)
                # Replace image data at the xref level
                # This affects all pages sharing this xref
                pass  # see full implementation below
```

**Full implementation** (tested on real PDF with shared xref=8 logo):

```python
import pymupdf

def replace_logo_with_transparent(doc, logo_xref):
    """Replace logo at given xref with 1x1 transparent pixel across all pages."""
    # Step 1: Create a minimal transparent pixmap
    # White 1x1 pixel works as a transparent-looking replacement
    white_pix = pymupdf.Pixmap(pymupdf.csGRAY, 1, 1, [255], False)
    
    # Step 2: Replace at the xref level (updates all pages referencing it)
    # pymupdf's replace_image replaces the image data for ALL references
    try:
        # This API varies by pymupdf version
        doc.xref_set_key(logo_xref, "Width", "1")
        doc.xref_set_key(logo_xref, "Height", "1")
        doc.update_stream(logo_xref, white_pix.tobytes())
    except Exception as e:
        print(f"  ⚠ xref replacement failed: {e}")
        # Fallback: page-level replace_image
        for page in doc:
            for img in page.get_images():
                if img[0] == logo_xref:
                    try:
                        page.replace_image(logo_xref, pymupdf.Pixmap(pymupdf.csGRAY, 1, 1, [255], False))
                    except:
                        pass
    
    # Step 3: Clean up content streams to remove Do references
    # pymupdf doesn't auto-remove the Do operator, so we need to clear
    # the page content and re-add with the image removed
    clean_page_contents(doc)


def clean_page_contents(doc):
    """Remove Do references to the logo from all page content streams."""
    for page in doc:
        content_list = page.get_contents()
        if not content_list:
            continue
        
        for xref in content_list:
            stream = doc.xref_stream(xref)
            if not stream:
                continue
            
            raw = stream.decode() if isinstance(stream, bytes) else stream
            
            # Remove Do commands (image invocations)
            # Pattern: /Im0 Do  or  /XObject-name Do
            # These are the content-stream commands that place the image
            modified = re.sub(
                r'/[A-Za-z0-9_-]+\s+Do\s*',
                '', raw
            )
            
            if modified != raw:
                doc.update_stream(xref, modified.encode())
```

**Pitfall**: The `replace_image` / `xref_set_key` approach may leave ghost rectangles
if the viewer renders empty image areas. The white 1x1 pixel approach works well in
practice — it replaces the visible logo with a nearly invisible dot.

---

## Complete Reference Implementation

For the full end-to-end script that handles:
- Page content stream analysis + Tm position matching
- XObject watermark detection and 3Tr injection
- LOGO image replacement with transparent pixel
- Combined page+XObject approach

See this session's final script pattern:

```python
# CORE APPROACH (from session 2026-05-11, 增值税法18项核心变化.pdf)
#
# For each page:
#   1. Read content streams → find BT...ET blocks
#   2. Match watermark blocks by Tm position + font name
#   3. Insert "3 Tr " before "/FT26" to make text invisible
#
# For each XObject:
#   1. Read XObject content stream
#   2. Replace watermark CID sequences or inject 3Tr
#   3. Write modified stream back
#
# For LOGO:
#   1. Replace image xref with 1x1 white pixel
#   2. Clean page content streams (remove Do commands)
#
# Save with: doc.save("output.pdf", garbage=4, deflate=True, clean=True)
```

---

## Decision Tree

```
Is the watermark visible but search_for() finds nothing?
  ├─ YES → Check for XObject forms → inspect /Type/XObject
  │        └─ Watermark in XObject → Phase 5 + Phase 2
  └─ NO  → Can search_for() find it?
            ├─ YES → Is the watermark string also in body text?
            │        ├─ YES → Use <10 char filter or position-based (Phase 4)
            │        └─ NO  → Basic approach (search_for + redact) is sufficient
            └─ NO  → Try position-based content stream matching (Phase 4)

Is user requesting "transparency" / "no white blocks" / "invisible"?
  └─ YES → MUST use 3Tr approach, NOT redact annotations
```

---

## Pitfall Summary

1. **Shared XObjects**: Modifying an XObject stream affects ALL pages that `Do` it.
2. **Font name collision**: Watermark and body may share the same font. Never delete by
   font alone — use position or size as additional filter.
3. **3 Tr positioning**: Insert `3 Tr` BEFORE `Tf` in the BT block, not after.
   Correct: `BT 3 Tr /FT26 240 Tf ... Tj ET`
   Wrong: `BT /FT26 240 Tf 3 Tr ... Tj ET`
4. **Stream encoding**: `doc.xref_stream(xref)` returns decoded data (bytes). Always
   `.decode()` before manipulation, `.encode()` after.
5. **`doc.clean_contents()`**: Destructive! Resolves all XObject references and
   flattens content into page-level — use only as last resort, and verify output.
6. **Syntax errors**: Inserting `3 Tr` in the wrong position causes "MuPDF error:
   syntax error in array". Always verify the BT...ET block syntax before saving.
7. **File size increase**: `3 Tr` approach adds minimal overhead vs redaction's
   1.5-3x. If file size matters, the 3Tr approach is better.
8. **LOGO image xref**: If all pages share the same xref, `page.delete_image()`
   on one page removes it from ALL pages. Use xref-level replacement instead.
