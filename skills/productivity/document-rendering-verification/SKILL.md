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

**When**: `vision_analyze` returns `400 {"... does not accept input types: image"}` **and** you cannot re-point `auxiliary.vision` (or must finish this run immediately). Treat that error as a config state to fix — not as a permanent trait of the model. See "Fixing 'no vision model'" below. Without re-pointing the slot, retrying vision fails identically every time; use text until then.

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
- **Large display type needs a bigger multiple — the "wrong property" bug has a small-type twin.** A 40pt hero/cover title with `lineSpacingMultiple: 1.05` writes the *correct* percentage yet still looks stacked: 1.05 × 40pt leaves ~2pt of daylight, so the two lines read as one blob and the ink-band check reports `bands=1`. Rule of thumb: type ≥28pt → use ≥1.25; body ≤14pt → 1.05–1.15 is fine. Don't conclude "the fix didn't work" when the unit bug is already gone — the remaining cause is a too-tight multiple for the size. Sweep the whole family, not the one page you noticed: `grep -n 'lineSpacingMultiple:\s*1\.\(0\|1[0-4]\)' build.js` and bump every hit that is ≥28pt or can wrap.

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
- **Decoration inside the box's bbox collapses the bands.** If a shape you drew (rings, arcs, dividers, watermark, big icon) crosses the text box's rectangle, its strokes fill the empty rows *between* the lines → `bands` reports 1 and you get a false "text overlapping itself" verdict on a box that renders perfectly. Confirm before fixing: re-crop to just the glyph area and re-count. A genuine stacking bug still reports 1 band on the tight crop; a decoration artifact reports 2. Keep the crop as a script, don't loosen the detector. One-page spot check:

  ```bash
  venv/bin/python scripts/pptx_ink_bands.py slide-01.png --box 0.70,1.50,7.60,3.35 --light-ink
  #                                                        x0,y0,x1,y1 in INCHES, LAYOUT_16x9
  ```

  (`--light-ink` = light glyphs on a dark fill; omit for dark text on light. `--box` is exactly how you exclude the right-hand art: crop to x≤7.60 and the rings at x≥8.15 stop polluting the count.)

Run BOTH layers before declaring a deck fixed: A is exact on geometry, B is model-free on pixels; they catch different failure modes (a wrapped line that A thinks is fine because the estimate fit, an offset box B can't reason about).

Full worked detail, including the pptxgenjs XML mapping and the height arithmetic: `references/pptx-layout-overlap-diagnosis.md`.

## Best path for .docx on Windows (WSL host): Word COM as render oracle

Same rationale as the .pptx COM section — the real renderer beats a `soffice`
approximation, and a Windows user opens the .docx in Word. Verified from WSL via
`powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\...\docx_com_metrics.ps1" "<src.docx>" "<out.pdf>"`:

```powershell
$word = New-Object -ComObject Word.Application
$word.Visible = $false; $word.DisplayAlerts = 0
$doc = $word.Documents.Open($Src, $false, $true)      # (path, ConfirmConversions, ReadOnly)
Write-Output ("PAGES {0}" -f $doc.ComputeStatistics(2))   # 2 = wdStatisticPages
foreach ($t in $doc.Tables) { $t.Rows.Count; $t.Columns.Count; sum of $t.Columns.Width }
$doc.ExportAsFixedFormat($Pdf, 17)                    # 17 = wdExportFormatPDF
```

Run `scripts/docx_com_metrics.ps1` — it prints page count, per-table row/column counts, and each
table's summed column width versus the usable text-column width, then exports the PDF.

What each number proves:
- `ComputeStatistics(2)` → page count; cross-check it against the page images you render.
- **Table width vs text width is the docx analogue of the pptx geometry check and needs no render.**
  Compare the sum of your column widths with `PageSetup.PageWidth - LeftMargin - RightMargin`.
  Equal is the design target; **over** means Word silently re-fits and your carefully chosen widths
  are fiction. A row of `Cms` summing to exactly the text width (e.g. 21 − 1.6 − 1.6 = 17.8cm) is
  the number to aim for.
- Then export the PDF → page images → run the Layer B visual pass above.

**Rasterizing the PDF when poppler is absent.** The primary path's `pdftoppm` needs poppler-utils,
which is frequently not installed on a WSL box and not worth a system-level install. PyMuPDF does
the same job from pure Python and is a one-line pip:

```bash
venv/bin/pip install -q pymupdf -i https://pypi.tuna.tsinghua.edu.cn/simple
venv/bin/python scripts/pdf_to_png.py /path/quote.pdf /tmp/pg 110   # → pg-01.png, pg-02.png, …
```

Use `import pymupdf as fitz` with a fallback to `import fitz` — the old module name still resolves
but prints a deprecation warning. At `dpi=110` an A4 page comes out ~910×1287px, which is enough for
a vision model to read table cells and spot clipping. The script prints one line per page plus a
final `pages: N` — **cross-check that N against the COM `ComputeStatistics(2)` page count**; a
mismatch means the export silently truncated and the visual pass covered only part of the document.

**When `vision_analyze` returns no description for some pages** (an empty verdict, not an error),
don't skip that page and don't retry blindly — call the *configured* vision channel directly. Read
`auxiliary.vision` from `config.yaml`, expanding `'${VAR}'` against `os.environ` plus
`~/.hermes/.env`, then POST an OpenAI-shaped `chat/completions` request with the page as a base64
`data:image/png;base64,…` content part and print the reply verbatim. Never print or log the key.
The answer usually opens with the model name (`MODEL: Doubao-Seed-2.1-Pro`) — that is your proof the
request reached a real model rather than an empty cache.

Keep the prompt a fixed three-point checklist plus a content read-back, so the verdict is checkable
against your generator's constants instead of a vague "looks fine":

```
1) 有没有文字溢出页面边缘、被裁切、或相互重叠？
2) 表格有没有串行、错位、列宽异常？
3) 逐行罗列你看到的主要标题和表格内容。
```

Point 3 is the high-value one: read the rows back and diff them against the price/content constants
in your build script. That catches a wrong number in the document itself, which no amount of
overflow/clipping checking will ever surface.

**PITFALL — PowerShell 5.1 decodes a BOM-less `.ps1` as ANSI.** A script authored from Linux/WSL
(any `write_file`) is UTF-8 *without* BOM; `powershell.exe` then reads every non-ASCII byte as ANSI,
so a Chinese literal path turns to mojibake and `Documents.Open` fails with
"找不到指定文件 / cannot find the file" **for a file that plainly exists**. The COM error text itself
comes back mojibake in the WSL console too, so do not chase the message — suspect the script's own
encoding first. Two fixes, both cheap:
1. Keep the `.ps1` **all-ASCII** — no Chinese literals, comments, or paths; take paths through
   `param([string]$Src, [string]$Pdf)` and pass them as arguments.
2. Or write the `.ps1` with a UTF-8 BOM (`\ufeff`) so PS 5.1 decodes it as UTF-8.

Belt-and-braces for a Chinese-named deliverable: `cp` it to an ASCII name in a scratch dir, convert
*that*, and hand the user the Chinese-named result. The rendered content keeps its Chinese text —
only the filename fed to COM needs to be ASCII.

**PITFALL — python-docx cell tuples are fixed-length.** `table.add_row().cells` returns a tuple of
exactly the table's column count, so `for ci, val in enumerate(row)` over a longer row raises
`IndexError: tuple index out of range`. Assert the shape (`assert len(row) == len(headers)`) before
filling, or route every table through one helper that derives `cols=len(headers)`.

**Pulling brand/template assets out of a source .docx**: do it in Python, not by shelling out —
`zipfile.ZipFile(p).read('word/media/image1.png')`. And before reusing an extracted image as a logo,
actually *look* at it: a decorative motif (an abstract pattern) is not the company mark. Check the
image for the company name/text before assuming `image1` is the logo, or you ship a decoration as
brand identity.

Full worked detail — the mojibake transcript, the ASCII-copy recipe, the table-width arithmetic, and
the source-provenance discipline for client-facing generated documents:
`references/docx-word-com-verification.md`.

## Fixing "no vision model" (2026-10 — this is a *config state*, not a permanent trait)

The vision QA chain is the best verification path here, so if it is unavailable, **fix it
before falling back** — do not accept a text-only chain as the standing situation.

`auxiliary.vision` is an independent proxy slot in `config.yaml` and does **not** follow
`model.default`. Point it at any vision-capable model and `vision_analyze` works again —
the main model stays exactly as it is:

```bash
cp ~/.hermes/config.yaml ~/.hermes/config.yaml.bak.$(date +%Y%m%d_%H%M%S)
hermes config set auxiliary.vision.model    Doubao-Seed-2.1-Pro
hermes config set auxiliary.vision.base_url https://aigw.telecomjs.com/v1
hermes config set auxiliary.vision.api_key  '${TELECOM_DOUBAO_KEY}'
```

- `~/.hermes/config.yaml` is **protected**: `patch` / `write_file` are refused with
  `Refusing to write to Hermes config file`. `hermes config set` is the only path
  (it prints `✓ Set auxiliary.vision.model = ...`).
- Choose the **cheapest** vision-capable channel among the user's existing keys, and do it
  automatically rather than asking. Honest degradation, never a block.
- **Verify with a known-answer image.** "It did not error" proves nothing: generate a picture
  containing a random code, ask the model to read it back, accept only an exact match. A model
  that returns plausible-sounding content it never actually saw passes every weaker test.
  Probe script + the live-tested channel matrix live in the `hermes-free-model-channels` skill
  (`scripts/vprobe.py`).
- Before trusting any verdict afterwards, confirm the image genuinely reached your context —
  a "successful" `vision_analyze` call whose image never attached produces confident nonsense.

Once re-pointed, the **primary path above reopens** and is the strongest check available:
render → `vision_analyze` each page, and cross-check its verdict against the Layer A/B
measurements rather than taking either alone.

## Delivery-path discipline (all formats)

Verify and ship the *same bytes*. When you rebuild a document, overwrite the
real delivery target in the same step — the repo copy, any scratch preview
copy, and the delivered file (e.g. the Windows Desktop path) must never drift.
Confirm the delivery path's size/mtime after copying. A corrected file sitting
in a scratch directory while the Desktop still holds the broken build reads to
the user as "the fix didn't work", and it is the most expensive possible
verification failure: correct work, reported as success, that the user cannot
see.

The same rule governs anything *pushed or mirrored* rather than copied — a tool's success
message is not evidence, and neither is a local status line:

- **A push:** `## main...origin/main` from local `git status` can be a stale ref. Read the
  authoritative side back — `git ls-remote origin main` must return a SHA byte-identical to
  local `git rev-parse HEAD`. Compare the two strings; don't eyeball "the push looked fine".
- **A sync/mirror tool:** "wrote N files" says nothing about whether an *existing* target was
  updated — non-destructive syncs skip same-name targets silently. Prove it with a hash
  comparison of the mirror copies (`md5` of each `SKILL.md`/artifact across source and every
  destination); a green summary from the tool is not proof.

Generalize: **read the effect back from the place the user will actually look**, and compare
a value that can only match if the change truly landed.

## Existing-umbrella note

This skill's content is a standalone class-level verification workflow. It complements (does not replace) the creation-side knowledge in the `word-documents` / `docx` skills — those cover HOW to build the file, this covers HOW to prove it rendered right.
