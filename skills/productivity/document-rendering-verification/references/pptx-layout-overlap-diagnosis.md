# Diagnosing "文字重叠" in pptxgenjs decks

Worked detail behind the SKILL.md sections "Best path for .pptx on Windows" and
"Overlap root-cause checklist". Source case: a 10-page 盈信财税 company-
introduction deck built with pptxgenjs where the user reported "第1到第7页都有
文字是重叠的".

## Symptom

Multi-line text blocks render with their lines stacked on top of each other —
not "slightly tight", but genuinely superimposed, so only the last line reads
clearly. Pages with single-line text look fine, which makes it look like a
geometry/coordinate problem on specific pages. It is not.

## Root cause: pptxgenjs `lineSpacing` is POINTS, not a multiple

pptxgenjs exposes two different line-spacing properties, and the names do not
tell you the unit:

| Property | Written to XML | Unit | Meaning |
|---|---|---|---|
| `lineSpacing` | `<a:lnSpc><a:spcPts val="N*100"/>` | **points** | absolute line height in points |
| `lineSpacingMultiple` | `<a:lnSpc><a:spcPct val="N*100000"/>` | **multiple** | N× the font's default line height |

Confirmed against `node_modules/pptxgenjs/dist/pptxgen.cjs.js`:
`spcPts val = lineSpacing * 100` and `spcPct val = lineSpacingMultiple * 100000`.

Writing the idiomatic-looking `lineSpacing: 1.05` therefore emits
`spcPts val="105"` = **1.05 point** line spacing. A 40pt headline's two lines
land 1.05pt apart → total overlap. That is the entire reported bug.

Fix: replace `lineSpacing:` with `lineSpacingMultiple:` — a mechanical
find/replace across the whole build script, not a per-page coordinate hunt.

### The 10-second diagnosis via COM

`ParagraphFormat.LineRuleWithin` distinguishes the two encodings:

- `-1` (msoTrue) → multiple-based spacing
- `0` (msoFalse) → point-based spacing

If the metric dump shows that only *some* shapes report `0`, those are exactly
the shapes the build script gave a line-spacing property to — and exactly the
overlapping ones. Run this before spending any time on geometry; in the source
case it isolated the whole failure class to 9 shapes across slides 1–9 in one
pass, and the user's "pages 1–7" matched the multi-line ones precisely.

## Why the height budget must be recomputed after the fix

`lineSpacingMultiple: 1.3` multiplies the font's **default** line height, which
is roughly 1.2em — not the font size itself. So a line is about
`fontSize * 1.2 * 1.3 ≈ fontSize * 1.56`, i.e. ~56% taller than a naive
`fontSize * 1.3` budget. Card bodies laid out against the naive estimate will
overflow their boxes once spacing is correct. Re-derive each multi-line block
before rebuilding:

```
line_height = fontSize * 1.2 * lineSpacingMultiple
text_height = Σ(lines_in_para * line_height) + paraSpaceAfter * (paras - 1)
```

Cross-check the per-paragraph `lines_in_para` against the real
`Lines().Count` from the COM dump — that number is reliable, so the arithmetic
is grounded rather than guessed.

## Verification loop (run it, don't skip the second pass)

1. Diagnose (`LineRuleWithin`) → 2. fix the unit → 3. `node build.js` →
4. re-dump metrics with `scripts/pptx_com_metrics.ps1` → 5. recompute text
rects and check pairwise intersections → 6. only then report done.

Always run step 4–5 on the *rebuilt* file. A fix that "should" work is not
verified output; the user is looking at pixels.

## Two false-positive traps

- **Overlapping boxes ≠ overlapping text.** A wide left-hand text box
  (x 54–720, right-aligned label default) overlaps a brand/logo text box
  (x 611–702) on the same slide, yet the left text is only ~468pt wide and
  never reaches x=611. Comparing shape *boxes* flags these; comparing *text
  rects* (using the reliable `BoundLeft`/`BoundWidth` and the computed
  vertical extent) does not. Fixing box-level false positives wastes a pass.
- **A big empty-looking box is not a bug.** Centre-aligned single lines in a
  50pt-tall box leave a lot of slack; that reads as an overlap in a naive
  box scan but the glyphs are ~17pt tall and clear.

## Genuine collisions still happen — fix them separately

Unit bugs and real coordinate collisions are independent; fixing spacing does
not clear both. In the source case there was a second, real defect: a section
heading at `y=1.42, h=0.4` with its first data row at `y=1.5` — an 0.08in gap
between a 0.4in-tall heading box and the row below it. Fix by moving the lower
element down (here rows to `y=1.78`, heading to `y=1.34, h=0.32`), never by
shrinking a heading box below its own font size.

## Delivery-path discipline

After a rebuild, overwrite the *actual* delivery target in the same step, and
confirm identity (size + mtime) at that path. In the source case a corrected
deck was rebuilt in the repo and copied to a scratch preview directory while
`C:\Users\Administrator\Desktop\盈信财税_公司介绍.pptx` still held the broken
build — so the user opening the delivered file would have re-seen the bug and
reasonably concluded the fix failed. Repo copy + scratch copy + delivery copy
must not drift.

## Honest caveat on the source session

The unit fix and the heading/row fix were both applied and the deck rebuilt
successfully. The post-fix metric re-dump was prepared but not completed before
the iteration budget ran out, so the second verification pass was left
outstanding — the next session should re-run steps 4–5 above and confirm zero
intersections before reporting the deck clean.
