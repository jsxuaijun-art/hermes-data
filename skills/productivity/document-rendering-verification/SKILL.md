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

**Reopening the .docx with python-docx to verify text content** (catches text bugs a render won't show):
```python
from docx import Document
d = Document('out.docx')
print('paras:', len([p for p in d.paragraphs if p.text.strip()]), 'tables:', len(d.tables))
for p in d.paragraphs:
    if '待确认' in p.text:
        print('real newlines:', p.text.count('\n'))     # 应>0，说明填表说明正确分行
        print('literal \\n:', '\\\\n' in p.text)         # 应为 False —— 见下面陷阱
```
- **陷阱：字面 `\\n` vs 真实换行——别被 `repr()` 骗了。** 生成脚本里若写的是
  `'...待确认"\\\\n2. ...'`（源码里字面反斜杠+n 两个字符），docx 里存的就是字面
  `\n` 文本，打开时显示一行乱字而不分行。用 `p.text.count('\n') == 0` + `'\\\\n' in p.text`
  判定，比肉眼/shadow 的 `repr` 可靠（`repr` 把真实换行也显示成 `\n`，两难分清）。
- 修复：把源码里的 `'\\\\n'` 改成真实换行 `'\n'`（或 `add_paragraph` 多段），重新生成再复验一次。

**Docx packaged inside a delivery zip (徐总交付打包铁律: 桌面只留 zip)**:
If `out.docx` was zipped up (`fname.zip` → Desktop), the snippet above throws
`KeyError: word/document.xml` — the OUTER zip holds the .docx *file*, not its XML.
Go outer → docx bytes → `io.BytesIO` → inner zip. Two steps, not one:
```python
import zipfile, io
outer = zipfile.ZipFile("交付物.zip")
d = zipfile.ZipFile(io.BytesIO(outer.read(outer.namelist()[0])))  # 唯一条目=docx
xml = d.read("word/document.xml").decode()
print('tables:', xml.count('<w:tbl>'), 'paragraphs:', xml.count('<w:p>'))
```
Add a keyword spot-check to catch "该写的没写进去": `for kw in [...]: assert kw in xml`.


## Known environment quirk

Some providers/models (e.g. deepseek-v4-flash) do not accept image inputs, so the normal vision QA chain is unavailable for them. This is an environment trait, not a tool defect — the pdftotext fallback above is the reliable working path, not a refusal.

## Existing-umbrella note

This skill's content is a standalone class-level verification workflow. It complements (does not replace) the creation-side knowledge in the `word-documents` / `docx` skills — those cover HOW to build the file, this covers HOW to prove it rendered right.
