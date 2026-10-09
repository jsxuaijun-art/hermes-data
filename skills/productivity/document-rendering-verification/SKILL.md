---
name: document-rendering-verification
description: 生成/编辑文档后，交付前验证渲染排版是否正确。
trigger: user asks to generate a Word/PDF/PowerPoint file, or after building a document deliverable you need to verify it renders correctly before reporting done.
category: productivity
---

# Document Rendering Verification

Confirm a generated document deliverable actually looks right before telling the user it's done. Applies to .docx, .pdf, .pptx — anything that must render when opened.

## Why this matters

`doc.save(path)` succeeding only proves the bytes were written. It says nothing about broken tables, clipped columns, garbled Chinese, empty pages, or misplaced content. For user-facing deliverables (江姐's daily docx reports), verify every time — skipping it lets formatting defects reach the user.

## Primary path: render to images + visual QA

```bash
# 1) Convert to PDF with LibreOffice (close to Word's rendering)
soffice --headless --convert-to pdf "output.docx" --outdir /tmp

# 2) PDF → page images (r=100 is enough for layout QA)
pdftoppm -jpeg -r 100 "/tmp/output.pdf" /tmp/pg    # → /tmp/pg-01.jpg, pg-02.jpg, ...
```

Then inspect each page with `vision_analyze` (look for broken tables, clipping, spacing artifacts, leftover placeholders).
- Image count = page count. `pdftoppm` zero-pads to the width of the page count (`pg-01.jpg`…`pg-12.jpg`).
- Prereqs: `soffice` (libreoffice), `pdftoppm` (poppler-utils). Verify with `which soffice pdftoppm`.

## Fallback: no vision model → pdftotext layout check

**When**: the active model rejects image input. `vision_analyze` returns `400 {"... does not accept input types: image"}`. Do NOT keep retrying vision — it will fail identically every time. Drop to text.

```bash
soffice --headless --convert-to pdf "output.docx" --outdir /tmp
pdftotext -layout "/tmp/output.pdf" -      # -layout preserves table column alignment
```

**Reading the output**:
- Text order, header/body completeness, content bleeding to next page → all readable directly.
- Column alignment → `-layout`'s space padding reflects it; a cell wrapping to a second line (long text) is normal, not an error.
- Page count → run `pdftoppm -r100 ... /tmp/pg` and count generated jpg files (no vision needed, just a filename count).
- Emoji/special glyphs may appear as gaps in plain text — expected; only use vision if a visual element MUST be verified.

**Quick structural spot-check (no render at all)**:
```python
import zipfile
xml = zipfile.ZipFile('out.docx').read('word/document.xml').decode()
print('tables:', xml.count('<w:tbl>'), 'paragraphs:', xml.count('<w:p>'))
```
Good for counting tables/paras, not for layout.

## Fallback: no LibreOffice installed at all → structural QA

**When**: `soffice` is not installed AND you can't install it (headless box, no sudo). Both render-to-image and pdftotext are off the table. Do NOT stall — drop to structural QA of the package itself.

For **.pptx** decks:
```bash
# requires python-pptx (already present in the repo .venv as 'pptx')
venv/bin/python scripts/pptx_structural_qa.py /path/to/deck.pptx
```
Prints per-slide text with bounding boxes, flags likely overflow boxes via a chars-per-line heuristic, lists images (confirms the deck isn't text-only), and scans for leftover placeholder strings. **Trust it only for content presence/order and gross overflow** — large-font single values (a big stat number, a two-line title) routinely false-positive; and it cannot see cross-shape stacking, icon/line collisions, or contrast issues. If those matter and no renderer exists, tell the user you verified content only and they should eyeball the layout in the real app.

## Best path for .pptx on Windows (WSL host): PowerPoint COM as render oracle

**When**: the user is on Windows and the deck must render exactly as they will see it. This beats every fallback below — it is the real renderer, not an approximation. Verified working from WSL: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\...\script.ps1"` drives `New-Object -ComObject PowerPoint.Application`.

Run `scripts/pptx_com_metrics.ps1` (in this skill) to dump one TSV row per shape:
slide, name, Left/Top/Width/Height, Font.Size, `ParagraphFormat.LineRuleWithin`, LineSpacing, SpaceAfter, `TextRange.Lines().Count`, and per-line `BoundLeft`/`BoundWidth`.

**What is trustworthy from COM, and what is NOT** (this cost a full session to establish — do not re-derive):

| API | Verdict |
|---|---|
| `Lines().Count` | **Reliable.** The actual rendered wrapped-line count. This is the single most useful number. |
| per-line `BoundLeft` / `BoundWidth` | **Reliable.** Confirms wrapping and horizontal extent. |
| `BoundTop` / `BoundHeight` | **UNRELIABLE.** For multi-line text `BoundHeight` collapses to ~1pt and `BoundTop` is nonsense. Never build a verdict on them. |
| shape `Left/Top/Width/Height` | Reliable (your own geometry). |

Because Bound vertical data is junk, compute text extents arithmetically instead:

```
line_height = fontSize * 1.2 * lineSpacingMultiple
text_height = Σ(lines_in_para * line_height) + paraSpaceAfter * (paras - 1)
text_top    = box_top + (box_height - text_height) / 2     # only if valign is middle
text_rect   = [text_top, text_top + text_height] x [bound_left, bound_left + bound_width]
```

Then flag (a) `text_height > box_height` → overflow, and (b) pairwise rect intersection where both x- and y-ranges overlap.

`scripts/pptx_layout_audit.py` implements all of this directly from the COM TSV — overflow plus real text-rect intersections, with a final unit-bug signature scan (multi-line shapes on point-based spacing). Run it instead of hand-deriving coordinates; you only re-check by hand when it flags something.

**Two traps when reading the results:**
- **Overlapping boxes ≠ overlapping text.** A wide left box routinely overlaps a right-aligned label box whose text sits far to the right — check the *text rects*, not the boxes, or you will "fix" non-bugs and miss real ones.
- Only shapes whose paragraphs carry explicit line spacing can collapse (see next section). Single-line shapes and default-spacing shapes cannot produce this failure.

## Overlap root-cause checklist (multi-line text stacking on itself)

Before hunting coordinates, check the spacing attributes — the usual culprit is a **unit** bug in the generator, not bad x/y.

**pptxgenjs: `lineSpacing` is POINTS, not a multiple.**
- `lineSpacing: 1.05` → writes `spcPts val="105"` = **1.05 point** line spacing → every line of a multi-line paragraph renders on top of the previous one. This is what "文字重叠" looks like, and it appears on every page whose multi-line body used the property.
- `lineSpacingMultiple: 1.05` → writes `spcPct val="105000"` = 1.05× — this is the one you usually mean.
- Same family: `paraSpaceAfter` IS in points (correct as written); `lineSpacingMultiple` needs an honest re-check of downstream height budgets, because 1.3× multiplies the *font's* default line height (~1.2 em), so multi-line blocks get ~56% taller than a naive `fontSize * 1.3` estimate.

**The COM tell**: `ParagraphFormat.LineRuleWithin` is `-1` (msoTrue) for multiple-based spacing and `0` (msoFalse) for point-based. If only *some* shapes report `0`, those are exactly the shapes you set a line-spacing property on — and exactly the overlapping ones. This is a 10-second diagnosis; run it before any geometry work.

**Then, separately**, look for genuine layout collisions — a section heading placed only 0.08in above its first row (heading h=0.4 at y=1.42 vs row at y=1.5) is a real overlap independent of the spacing bug. Fix by moving the lower element down, not by shrinking the heading below its font size.

## Layer B: pixel ink-band check — independent second opinion

The arithmetic above is only as good as its `fontSize * 1.2 * multiple` model. Add a **render-driven** pass that needs no geometric model at all: export each slide to a PNG with the real renderer (PowerPoint COM `Presentation.Export`, or `soffice --convert-to pdf` + `pdftoppm`), then crop each text box's region and count the **ink row bands** (consecutive rows of non-background pixels). See `scripts/pptx_layout_audit.py --png-dir …`.

Reading the result:
- A clean multi-line box shows **bands ≈ Lines().Count from COM** — the two layers agree.
- `bands < lines` on a multi-line box = lines rendered on top of each other (the stacking bug). This catches collapse even where the arithmetic estimate was borderline.
- Ink taller than the box = overflow.
- Bands determined from `background = most-common color in the region` (works for dark text on light AND light text on dark).
- False positives to expect and ignore: single-line shapes inside bordered/pill shapes can read as 2 bands (the border edges) — only flag `bands < nlines` when `nlines >= 2`, and treat `bands > nlines` as noise, not a defect. Don't let these derail a clean report.

Run BOTH layers before declaring a deck fixed: A is exact on geometry, B is model-free on pixels; they catch different failure modes (a wrapped line that A thinks is fine because the estimate fit, an offset box B can't reason about).

Full worked detail, including the pptxgenjs XML mapping and the height arithmetic: `references/pptx-layout-overlap-diagnosis.md`.

## Known environment quirk

Some providers/models (e.g. deepseek-v4-flash) do not accept image inputs, so the normal vision QA chain is unavailable for them. This is an environment trait, not a tool defect — the pdftotext fallback above is the reliable working path, not a refusal.

## Delivery-path discipline (all formats)

Verify and ship the *same bytes*. When you rebuild a document, overwrite the
real delivery target in the same step — the repo copy, any scratch preview
copy, and the delivered file (e.g. the Windows Desktop path) must never drift.
Confirm the delivery path's size/mtime after copying. A corrected file sitting
in a scratch directory while the Desktop still holds the broken build reads to
the user as "the fix didn't work", and it is the most expensive possible
verification failure: correct work, reported as success, that the user cannot
see.

## Existing-umbrella note

This skill's content is a standalone class-level verification workflow. It complements (does not replace) the creation-side knowledge in the `word-documents` / `docx` skills — those cover HOW to build the file, this covers HOW to prove it rendered right.
