# .docx verification on Windows: Word COM as render oracle

Session detail behind the "Best path for .docx on Windows" section in SKILL.md.
Task shape: build a client-facing Chinese business document (a pricing/报价表 .docx)
with python-docx from an authoritative source document, then prove it renders right.

## The transaction that cost a run

The generator produced a valid 210 KB .docx with 6 tables. Verification then stalled:

```text
$src = "C:\Users\Administrator\Desktop\盈信财税_合规账服务报价表.docx"
$doc = $word.Documents.Open($src, $false, $true)

-> COMException: 找不到指定文件... (C:\Users\...\盈信财税_合规账服务报价表.docx)
```

The file existed (python-docx had just written it and reported its size). Two red herrings:

1. The error text arrives **mojibake** in the WSL console (`�ܱ�Ǹ...`) because the whole
   console round-trip is ANSI. Chasing the garbled message wastes time — read it as
   "cannot find the file".
2. It looks like a WSL/Windows path-translation problem. It is not: the path was the
   correct `C:\...` form.

**Root cause**: the `.ps1` was authored with `write_file` on Linux → UTF-8 **without BOM**.
Windows PowerShell 5.1 assumes ANSI for a BOM-less script file, so the Chinese filename
literal in the script body was decoded byte-wise into garbage *before* Word ever saw it.
Word was handed a genuinely non-existent path.

**Fix that works** (no script-encoding reasoning required): `cp` the deliverable to an
ASCII name and convert that.

```bash
cp "/mnt/c/Users/Administrator/Desktop/盈信财税_合规账服务报价表.docx" \
   /mnt/c/Users/Administrator/yingxin_quote/quote.docx
powershell.exe -NoProfile -ExecutionPolicy Bypass -File \
  "C:\Users\Administrator\yingxin_quote\docx2pdf.ps1"
```

Then hand the user the Chinese-named file. Only the path passed to COM needs to be ASCII —
the Chinese text *inside* the document renders fine.

The durable form of the fix is `scripts/docx_com_metrics.ps1`: `param()`-driven, zero
non-ASCII literals, so the failure cannot recur.

## Table-width arithmetic (no render needed)

`PageSetup.PageWidth - LeftMargin - RightMargin` is the usable text column. Sum each
table's column widths and compare. In this build every table was designed to sum to
exactly 17.8cm on A4 (21 − 1.6 − 1.6) — that is the "will not be re-fit" target.
Anything meaningfully over means Word re-fits at open time and the widths in the
generator are decorative rather than load-bearing.

## python-docx shape trap

```python
t = doc.add_table(rows=1, cols=3)      # 3 columns
for r in rows:                         # r had 5 values
    cells = t.add_row().cells          # tuple of exactly 3
    for ci, val in enumerate(r):
        cells[ci]                    # -> IndexError: tuple index out of range
```

`add_row().cells` is fixed-length. Assert `len(row) == len(headers)` up front, or build
every table through one helper deriving `cols=len(headers)`. The failure mode is a hard
crash at generation time, so it is cheap — but it is easy to hit when a table's shape
changes from 3 columns (category / content / price) to 5 (category / content / three
tiers).

## Rendering prerequisites are not guaranteed — check, don't assume

`soffice` and `pdftoppm` (poppler-utils) are the SKILL.md default path, but on this box
`pdftoppm` was absent, so PDF→page-image needs whatever is actually installed (PyMuPDF
`fitz` in the venv is a good substitute). `which pdftoppm` before relying on it; Word COM
needs no external binary at all, which is why it is the best path here.

## Source-provenance discipline for client-facing generated documents

The document was a **quote going to a customer**, built from the client's own
authoritative product manual. Rules that made it defensible — worth applying to any
generated business document whose numbers a third party will act on:

- Every price came **verbatim** from the source manual + its fee annex. Nothing was
  inferred, averaged, or "reasonably estimated".
- Where the source was silent, the document **left it blank or said so** rather than
  inventing a policy (no invented quote-validity window; "正式报价以双方确认的服务方案为准").
- The deliverable states its own provenance in a closing line: *依据《合规账产品手册》编制；
  手册未载明事项，已在表中如实留白，未作估计。*
- Extracted brand assets were **inspected before use**. `word/media/image1.png` (380×378)
  turned out to be a red four-lobed cloud motif — a decorative pattern with no text, not a
  company logo. It was used as a small header accent only; the text-logo slot was left to
  the user. Do not assume `image1` is the logo.

Cross-references: `content-evidence-discipline` (no-fabrication for outgoing copy) and the
user's standing rule that client-facing materials carry no unverifiable specifics.
