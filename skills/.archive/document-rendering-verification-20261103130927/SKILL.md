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

## Known environment quirk

Some providers/models (e.g. deepseek-v4-flash) do not accept image inputs, so the normal vision QA chain is unavailable for them. This is an environment trait, not a tool defect — the pdftotext fallback above is the reliable working path, not a refusal.

## Existing-umbrella note

This skill's content is a standalone class-level verification workflow. It complements (does not replace) the creation-side knowledge in the `word-documents` / `docx` skills — those cover HOW to build the file, this covers HOW to prove it rendered right.
