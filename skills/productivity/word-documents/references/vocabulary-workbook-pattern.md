# Vocabulary Workbook Generation Pattern

Generate rich .docx vocabulary workbooks for Chinese Gaokao English learners. Built on python-docx with root-grouping, Ebbinghaus schedule, and compact 6-column review layout.

## Full Workflow

```
word list → group by ROOT (词根) → assign writing frequency from real corpus
  → DAY 1 learning (single-column cards, 2-row format)
  → DAY 2-30 review (6-column compact, each on ONE page)
  → Full-bleed ocean cover + instructions + writing-word summary
```

## Three Key Design Decisions

### 1. Group by ROOT, Not by Prefix

**Wrong**: Group by prefix (`ab-`, `ac-`, `ad-`…). Words like `abandon`, `abnormal`, `aboard` share no common root meaning.

**Right**: Group by ROOT (`tract`=pull, `press`=press, `port`=carry…). Each group shares a concrete root meaning, and every word in the group uses that root:

```
▸ 【tract】= 拉/抽
  abstract  = abs-(离开) + tract(拉) → 从具体中抽离出来
  attract   = at-(朝向)   + tract(拉) → 把注意力拉过来
  attractive= at-(朝向)   + tract(拉) + -ive(…的) → 迷人的
  subtraction= sub-(向下) + tract(拉) + -ion(名) → 往下抽→减法
```

### 2. Writing Index from Real Corpus Data

Use the **FrequencyWords** corpus (https://github.com/hermitdave/FrequencyWords) — a 14K+ word frequency list based on OpenSubtitles and other corpora:

```python
# Download (one-time)
curl -sL "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2016/en/en_50k.txt" -o /tmp/freq.txt

# Look up a word
grep -i "^abstract " /tmp/freq.txt  # → abstract 1264

# Convert to 1-5 stars
def freq_to_stars(count):
    if count > 40000: return 5   # top: different(133K), report(61K), offer(46K), respect(45K)
    if count > 10000: return 4   # very high: support(36K), access(21K), success(20K)
    if count > 4000:  return 3   # high: transport(8K), expression(7K), permit(7K)
    if count > 1500:  return 2   # moderate: attract(4K), predict(3K), dismiss(3K)
    return 1                      # lower: abstract(1.3K), import(1.4K), differ(1.3K)
```

**Pitfall**: Uncommon words (`subtraction`, `abrupt`, `erupt`) may not appear in the 14K list. Assign baseline 1-2 stars by estimation.

### 3. 6-Column Compact Review Layout (Saves ~60% Paper vs Card Layout)

Replace card-per-word layout with a dense grid — **ultra-narrow number columns**:

```
┌────┬──────────────┬───────────────┬────┬──────────────┬───────────────┐
│序号│  英文        │ 中文（填空）  │序号│  英文        │ 中文（填空）  │
├────┼──────────────┼───────────────┼────┼──────────────┼───────────────┤
│  1 │ ★ abstract  │ (＿＿＿＿＿＿) │ 26 │ ★ express   │ (＿＿＿＿＿＿) │
│  2 │ ★ attract   │ (＿＿＿＿＿＿) │ 27 │ ★ impress   │ (＿＿＿＿＿＿) │
│ ... │             │               │ ...│             │               │
└────┴──────────────┴───────────────┴────┴──────────────┴───────────────┘
```

**Column widths: `[Cm(0.25), Cm(3.5), Cm(5.25), Cm(0.25), Cm(3.5), Cm(5.25)]`**

| Column | Width | Purpose |
|:--|:--:|:--|
| 序号 L/R | **0.25 cm** | Absolute minimum — just holds "50" at Pt(6) font |
| Content | 3.5 cm | Word or definition text |
| Fill-in blank | **5.25 cm** | Maximum space for handwriting |

**Key constraints (user-verified):**
- Column headers must say **"序号"** not "序"
- **No checkmarks** (✓□ ✗□) anywhere in review cells — they clutter the layout
- Table must be set to **full page width** via XML: `tblW.set(qn('w:w'), '11000')` for 0.8cm margins
- Number cell font: Pt(6), content: Pt(7), fill-in: Pt(6)

## Page Header (ALL pages: centered)

```python
# CENTER-ALIGNED for all day headers
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER  # ← critical
p.paragraph_format.space_before = Pt(2)
p.paragraph_format.space_after = Pt(1)
r = p.add_run(f'DAY {day_number}  {title}')
r.font.size = Pt(13); r.font.bold = True

# Info bar: 姓名 | 日期 | 正确数 (NO 准确率)
t = doc.add_table(rows=1, cols=3)
for i,(txt,w,clr) in enumerate([
    ('姓名: ___________', Cm(6.0), '2C3E50'),
    ('日期: ___________', Cm(5.0), '2C3E50'),
    ('正确: ___ / {total}', Cm(4.0), 'C0392B'),
]):
    c = t.cell(0,i); c.text = ''
    p = c.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.line_spacing = Pt(8)
    r = p.add_run(txt); r.font.size = Pt(8); r.font.bold = True
```

## Learning Card (2-Row Only — NO correct/error row)

```
┌─ ★ abstract [ˈæbstrækt] ──┬─ 抽象的（作品）(＿＿＿＿＿＿) ┐  ← LEFT-ALIGNED
│ 🔬 abstract = abs-离开+tract→抽离  │ 写作指数: ●●○○○  ⭐ 高频词 │
└─────────────────────────────────┴──────────────────────────────┘
```

- **Row 0 right cell**: LEFT-aligned (p.alignment = LEFT), not right-aligned — definition text flushes to left border, underlines extend right
- **No Row 2** (removed completely)
- "写作" → "写作指数" with real star data
- ⭐ badge only for high-frequency words

## Document Structure & Compactness

```
PAGE 1:  COVER (full-bleed ocean theme, margins=0)
PAGE 2:  INSTRUCTIONS + SCHEDULE
PAGES:   DAY 1 LEARNING (single-column cards, root-grouped)
         DAY 2 REVIEW  (6-column, ONE page)
         DAY 4 REVIEW  (6-column, ONE page)
         DAY 7 REVIEW  (6-column, separate page — exempted from single-page rule)
         DAY 15 REVIEW (6-column, ONE page, star words only)
         DAY 30 REVIEW (6-column, ONE page, mixed directions)
LAST:    Writing Word Summary
```

### Making 50-Word 6-Column Tables Fit on ONE Page

Critical compactness settings for 25 data rows + 1 header row:

```python
# Table header row
p.paragraph_format.space_before = Pt(0)
p.paragraph_format.space_after = Pt(0)
p.paragraph_format.line_spacing = Pt(8)
r.font.size = Pt(6)  # tiny

# Data cells — repeat for ALL cells in the 6-column table:
p.paragraph_format.space_before = Pt(0)
p.paragraph_format.space_after = Pt(0)
p.paragraph_format.line_spacing = Pt(8)
r.font.size = Pt(7)   # content
r.font.size = Pt(6)   # number and blank
```

Without these, 25 rows overflow to a second page.

## Cover Page (Full-Bleed) — Correct dxa Values

```python
# STEP 1: Zero margins for first section (cover)
for sec in doc.sections:
    sec.top_margin = Cm(0); sec.bottom_margin = Cm(0)
    sec.left_margin = Cm(0); sec.right_margin = Cm(0)

# STEP 2: Build cover with CORRECT table width
bg = doc.add_table(rows=1, cols=1)
tbl = bg._tbl
tblPr = tbl.tblPr
# Remove existing tblW if any
for child in list(tblPr):
    if child.tag == qn('w:tblW'):
        tblPr.remove(child)
tblW = OxmlElement('w:tblW')
tblW.set(qn('w:w'), '11906')  # ← CORRECT: A4=21cm=11906 dxa (NOT 17000!)
tblW.set(qn('w:type'), 'dxa')
tblPr.append(tblW)

# STEP 3: Section break for content pages
new_sec = doc.add_section()
new_sec.top_margin = Cm(0.8); new_sec.bottom_margin = Cm(0.8)
new_sec.left_margin = Cm(0.8); new_sec.right_margin = Cm(0.8)
```

**dxa calculation**: 1 cm = 567 dxa. A4 = 21 cm = 21 × 567 = 11907 ≈ 11906 dxa.
- Cover (0 margins): table width = 11906 dxa (full page)
- Content (0.8cm margins): table width = 11000 dxa (19.4 cm available)

## Ebbinghaus Schedule (6 Rounds)

| Day | Type | Direction | Format |
|:---:|:---|:---|:---|
| 1 | Learn | en→cn | Single-column cards with root breakdown |
| 2 | Review ① | en→cn | 6-column: English → Chinese |
| 4 | Review ② | cn→en | 6-column: Chinese → English |
| 7 | Review ③ | phonetic→en+cn | 6-column: → write word + definition |
| 15 | Review ④ | cn→en (★ only) | 6-column: high-frequency words only |
| **30** | Review ⑤ | mixed | 6-column: random en→cn / cn→en |

**Note**: Day 31 was user-corrected → Day 30. DAY 7 is the only review exempted from the "fit on one page" rule.

## Word Data Embedding (When Source File Unavailable)

The vocabulary `.txt` file may be deleted. Embed definitions directly:

```python
WORD_DEFS = {
    "abstract": ("ˈæbstrækt", "抽象的（作品）；摘要"),
    "attract": ("əˈtrækt", "吸引，引起"),
    # ... all 50 words
}

# Usage:
info = WORD_DEFS.get(wd, ('', ''))
phonetic = info[0]
definition = info[1]
```

## Pitfalls

1. **Cover dxa value**: Cover table width must be **11906** (A4 full width at 0 margins). Using 17000 (from early session attempt) creates a table wider than the page, and the excess gets clipped — the cover appears NOT full-bleed because Word clips table overflow.

2. **Section margins**: You MUST use `doc.add_section()` after the cover to create a new section with normal margins. Without it, content pages also have 0 margins.

3. **Number column width**: `Cm(0.25)` is the practical minimum for "序号" holding 2-digit numbers at Pt(6) font. At Pt(6.5) they need Cm(0.3). User explicitly said 0.25.

4. **Compactness**: 50 words × 25 rows in 6-column layout requires aggressive spacing reduction:
   - `space_before/after = Pt(0)`, `line_spacing = Pt(8)`
   - Number font Pt(6), content Pt(7), blank Pt(6)
   - Header font Pt(6), title Pt(13) instead of Pt(14)

5. **Chinese font in every run**: Every Run with Chinese text must set `.element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')`.

6. **DAY 7 exception**: The phonetic-to-both review has more content per cell and is exempted from the single-page rule.

7. **User naming preferences** (captured from corrections): "序号" (not "序"), "写作指数" (not "写作"), "DAY X" (all caps), "正确数" header (not "正确率").

8. **WSL path**: Never use `D:\...` in WSL Python. Use `/mnt/c/Users/Admin/Desktop/...`. Windows `D:\` path with backslashes creates a literal backslash filename in the current directory.

## Real-World Example: 50-Word Workbook

The final verified script is at `/tmp/build_vocab_v9.py` — a complete, working template covering 50 words across 12 root groups:
`tract / press / port / fer / cess/cede / spect / struct / rupt / mit/miss / dict / sist / pend/pens`

To regenerate: `python3 /tmp/build_vocab_v9.py`
Output: `/mnt/c/Users/Admin/Desktop/高考英语词汇默写本_50词实验版.docx`
