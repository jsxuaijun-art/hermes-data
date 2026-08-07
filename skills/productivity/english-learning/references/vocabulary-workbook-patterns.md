# Vocabulary Workbook Generation Patterns (Ebbinghaus + Word Roots)

Created: 2026-07-02 from session with 江姐 (Gaokao English vocabulary planner)
Updated: 2026-07-03 v3 — review direction alternation, non-alphabetical ordering, root-based grouping
Updated: 2026-07-03 v7 — 6-column layout, header no accuracy rate, right-aligned blanks
Updated: 2026-07-03 v9 — 50-word sets, left/right 25+25, no ✓□✗□, slim "序号" cols, real frequency data

## Source Data Format

The `高考英语词汇表3817词.txt` on desktop follows this format:

```
word [phonetic]  part_of_speech. definition
abandon [əˈbændən]  v.抛弃，舍弃，放弃
ability [əˈbɪlɪtɪ]  n. 能力；才能
```

Parsing in Python:
```python
m = re.match(r'([a-zA-Z\-\(\)]+)\s', line)
word = m.group(1).lower().rstrip(',)')
ph = re.search(r'\[([^\]]+)\]', line)  # phonetic
rest = line[m.end():].strip()
if phon: rest = rest.replace(f'[{phon}]','',1).strip()
```

## Ebbinghaus Review Schedule (per unit)

| New Day | Review Days After |
|---------|------------------|
| Day N   | Day N+1, N+2, N+4, N+7, N+15, N+30 |

**间隔：** `[1, 2, 4, 7, 15, 30]` 天。Day 30 替代 Day 31（用户明确要求，2026-07-03 v9）。

## Trial-First Workflow (省token验证法)

```mermaid
flowchart LR
    A[取15词小样] --> B[配词根拆解+联想+数据]
    B --> C[生成Word文档]
    C --> D{用户验收}
    D -->|满意| E[全量生成3875词]
    D -->|不满意| A
```

## Review Direction Alternation (v9 final)

| Round | Direction | Layout | Notes |
|:--:|:--:|:--:|:--|
| Day 1 学习 | 英→中 | 2行卡片 | 无正确/错误行，左对齐释义+填空 |
| Day 2 复习① | 英→中 | 六栏 | 左1-25/右26-50 |
| Day 4 复习② | 中→英 | 六栏 | 方向切换！写英文 |
| Day 7 复习③ | 音标→英+中 | 六栏 | 反向测试 |
| Day 15 复习④ | 中→英·重点 | 六栏 | 仅⭐高频词 |
| Day 30 复习⑤ | 混合 | 六栏 | 英→中/中→英各半 |

## Non-Alphabetical Ordering

Each section uses independent random seeds:
```python
seeds = {'learn': 42, 'en2cn': 42, 'cn2en': 77, 'phonetic': 123, 'star': 555, 'mixed': 999}
```

## Root-Based Grouping (CORRECT — NOT prefix)

**Formula:** `Word = prefix + ROOT + suffix`

⚠️ Do NOT group by prefix (ab-/ac-/ad- etc. are just first letters, not shared roots).

### Verified Root Groups (12 groups, 50 words — 2026-07-03 v9)

| Root | Meaning | Words | Sample Breakdown |
|:--|:--|:--|:--|
| tract | 拉 | abstract, attract, attractive, subtraction | abstract = abs-(离开)+tract(拉) |
| press | 压 | express, expression, impress, impression | express = ex-(向外)+press(压) |
| port | 运/带 | import, portable, report, support, transport | transport = trans-(跨越)+port(运) |
| fer | 带/拿 | differ, different, offer, prefer, refer | prefer = pre-(先)+fer(拿) |
| cess/cede | 走/去 | access, necessary, process, success | access = ac-(靠近)+cess(走) |
| spect | 看 | aspect, inspect, respect, suspect | respect = re-(反复)+spect(看) |
| struct | 建造 | construct, construction, instruct, instruction | instruct = in-(向内)+struct(建造) |
| rupt | 断/破 | abrupt, corrupt, erupt, interrupt | interrupt = inter-(中间)+rupt(断) |
| mit/miss | 送/发 | admit, commit, permit, submit, dismiss | admit = ad-(朝向)+mit(送) |
| dict | 说 | contradict, dictionary, predict | predict = pre-(提前)+dict(说) |
| sist | 站立 | assist, consist, insist, resist | insist = in-(在上)+sist(站) |
| pend/pens | 悬挂/花费 | depend, independent, expense, expensive | depend = de-(向下)+pend(挂) |

## Learning Card (Day 1 — 2 rows only, LEFT-aligned definition)

```python
# Code pattern — 2-row table
t = doc.add_table(rows=2, cols=2)
# Row 0: [word + phonetic, bg=F0F4F8] | [definition + blank, LEFT-aligned]
# Row 1: [root breakdown, blue #2C3E50] | [writing_index + star]
```

| Row | Left | Right |
|:--:|:--|:--|
| 0 | ★ abstract [ˈæbstrækt] (12pt bold, bg=F0F4F8) | 抽象的（作品）`(＿＿＿＿＿＿)` **左对齐紧贴左竖线** |
| 1 | 🔬 abstract = abs-(离开) + tract(拉) → 从具体中抽离 (7.5pt, #2C3E50) | 写作指数: ●●●○○ (7pt, #888) + ⭐ 高频词 (#C0392B) |

Key: Row 0 Col 2 is **left-aligned** (not right-aligned — user corrected this in v9). Definition text + fill-in blank on same line.

## Six-Column Review Layout (v9 final — 省纸)

**Reference PDF:** `D:\360MoveData\Users\Admin\Desktop\上海中考英语单词_第2-3页.pdf`

### Table Dimensions\n```\n6 columns: [Cm(0.15), Cm(3.5), Cm(5.35), Cm(0.15), Cm(3.5), Cm(5.35)]\n       序号↑(极窄) 原文↑    填空↑(最宽)   序号↑   原文↑   填空↑\n```\n\n**50 words per set:** Left col 1-25, Right col 26-50. 25 rows per page.\n**Row height:** 600 dxa (≈1.06cm) — fills A4 page vertically, no white space at bottom.

### Column Content by Mode (v9 — NO ✓□✗□, headers say "序号" not "序")

| Mode | Col 0 (序号) | Col 1 (原文) | Col 2 (填空) |
|:--|:--|:--|:--|
| en2cn | 1-25 (7pt, #999) | ★ abstract (8pt, bold) | `(＿＿)` (7pt, #CCC) |
| cn2en | same | 抽象的（作品）(7pt, #444) | `(＿＿)` same |
| phonetic | same | 🔊[əˈbændən] (7pt, #2C3E50) | 英[＿＿]中[＿＿] |
| mixed | same | 英文/中文交替 (8pt) | 反向填空 |

### Header (3 columns, NO 准确率)
```python
# Cols: 姓名 | 日期 | 正确: ___/N
# Color header: bg=EBF5FB, borders=2C3E50
```

## Real Frequency Data Source

**Source:** English FrequencyWords corpus (https://github.com/hermitdave/FrequencyWords, based on OpenSubtitles 2016, 50K word list)
**Usage:** Downloaded `en_50k.txt`, extracted frequency counts for each word, converted to 1-5 star bands.

### Frequency Bands
| Stars | Frequency Range | Examples |
|:--:|:--|:--|
| 5 | > 40,000 | different, report, offer, respect |
| 4 | 10,000 - 40,000 | support, express, access, process, expensive |
| 3 | 4,000 - 10,000 | construction, transport, expression, permit, insist |
| 2 | 1,500 - 4,000 | attract, corrupt, predict, dismiss, dictionary |
| 1 | < 1,500 | abstract, import, differ, construct, subtraction |

### How to fetch (script)
```bash
curl -sL --max-time 15 "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2016/en/en_50k.txt" -o freq.txt
for word in abstract attract report; do
  grep -i "^$word " freq.txt | head -1
done
```

## Cover Page Design (v9 — Full-Bleed)

Blue ocean theme (#0A2463 background) with emoji decoration. **Full-page table cell — must use section break technique.**

### Technique: Section Break for Different Margins

```python
# STEP 1: Zero margins for cover
for sec in doc.sections:
    sec.top_margin = Cm(0); sec.bottom_margin = Cm(0)
    sec.left_margin = Cm(0); sec.right_margin = Cm(0)

# STEP 2: Build cover table — ⚠️ width = 11906 dxa (NOT 17000)
# 11906 = A4 full width at 0 margins (21cm × 567 dxa/cm)
bg = doc.add_table(rows=1, cols=1)
tbl = bg._tbl; tblPr = tbl.tblPr
if tblPr is None:
    tblPr = OxmlElement('w:tblPr')
    tbl.insert(0, tblPr)
# Remove any existing tblW first
for child in list(tblPr):
    if child.tag == qn('w:tblW'):
        tblPr.remove(child)
tblW = OxmlElement('w:tblW')
tblW.set(qn('w:w'), '11906')  # ⚡ CORRECT: A4 = 21cm = 11906 dxa
tblW.set(qn('w:type'), 'dxa')
tblPr.append(tblW)

# STEP 3: Add section break, restore content margins
new_sec = doc.add_section()
new_sec.top_margin = Cm(0.8); new_sec.bottom_margin = Cm(0.8)
new_sec.left_margin = Cm(0.8); new_sec.right_margin = Cm(0.8)
```

### Cover Visual Layout

```
✨    ⭐    ✨    ✨    ⭐    ✨
     高考英语词汇默写本
   词根词缀 · 艾宾浩斯记忆法
🌊🌊  ⛵  ⛵⛵  🌊🌊🌊  ⛵  🌊🌊
    学海无涯，扬帆起航
每一个词根，都是你驶向未来的帆
苏州盈信企业管理有限公司
公司注册 · 专注财税二十五年
18912633863
```

## Full Document Structure (50词实验版 v9)

```
① 封面        — 蓝色海洋帆船 #0A2463
② 使用说明     — 说明 + 日程表
③ 📖 DAY 1 学习页 — 2行卡片，按词根分组
④ DAY 2 英→中     — 六栏复习
⑤ DAY 4 中→英     — 六栏复习
⑥ DAY 7 音标→     — 六栏复习
⑦ DAY 15 ★ 中→英  — 六栏复习（仅⭐词）
⑧ DAY 30 混合终测 — 六栏复习
⑨ ✍ 高频写作词速查
⑩ 封底
```

## WSL Path Trap (重要)

```python
# ❌ WRONG — saves to /home/dmin/D:\\... as literal filename
doc.save(r'D:\360MoveData\Users\Admin\Desktop\file.docx')

# ✅ CORRECT — save to Windows desktop via /mnt/
doc.save(r'/mnt/c/Users/Admin/Desktop/高考英语词汇默写本_50词实验版.docx')
```

**Desktop paths:**
- Windows: `C:\Users\Admin\Desktop\`
- WSL: `/mnt/c/Users/Admin/Desktop/`
- Never use D: drive path (user doesn't recognize it)

## python-docx Table Patterns

### Cell Border Helper
```python
def set_bdr(c, **kw):
    tc=c._tc; p=tc.get_or_add_tcPr(); b=OxmlElement('w:tcBorders')
    for edge,val in kw.items():
        e=OxmlElement(f'w:{edge}')
        e.set(qn('w:val'),val.get('val','single'))
        e.set(qn('w:sz'),val.get('sz','4'))
        e.set(qn('w:color'),val.get('color','000000'))
        e.set(qn('w:space'),'0'); b.append(e)
    p.append(b)
```

### 6-Column Table Creation\n```python\n# Full page width table — 6 columns\nt = doc.add_table(rows=rows_needed + 1, cols=6)\nt.alignment = WD_TABLE_ALIGNMENT.CENTER\n# Set table to fill page width (A4 with 0.8cm margins = ~19.4cm = 11000 dxa)\ntbl = t._tbl; tblPr = tbl.tblPr\nif tblPr is None: tblPr = OxmlElement('w:tblPr'); tbl.insert(0, tblPr)\ntblW = OxmlElement('w:tblW'); tblW.set(qn('w:w'),'11000'); tblW.set(qn('w:type'),'dxa')\ntblPr.append(tblW)\ncol_widths = [Cm(0.15), Cm(3.5), Cm(5.35), Cm(0.15), Cm(3.5), Cm(5.35)]\nfor ci in range(6):\n    c = t.cell(0, ci); c.text = ''\n    p = c.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER\n    r = p.add_run('序号/中文释义/英文（填空）/序号/中文释义/英文（填空）'.split('/')[ci])\n    r.font.size = Pt(6); r.font.bold = True; r.font.color.rgb = RGBColor(0x33,0x33,0x33)\n    set_shd(c, 'EAEAEA')\n    c.width = col_widths[ci]\n\n# Row height to fill page (50 words = 25 rows)\nrow_h = '600'  # dxa, ~1.06cm\nfor ri in range(25):\n    trPr = t.rows[ri+1]._tr.get_or_add_trPr()\n    trH = OxmlElement('w:trHeight'); trH.set(qn('w:val'), row_h); trH.set(qn('w:hRule'), 'atLeast')\n    trPr.append(trH)\n```

## Color Palette Reference

| Element | Hex | Usage |
|---------|-----|-------|
| Dark navy | #1A1A2E | Main titles |
| Blue-gray | #2C3E50 | Subtitles, table headers |
| Light blue-gray | #F0F4F8 | Word card left bg |
| Root blue | #557A95 | Root breakdown text |
| Star red | #C0392B | ★标记, error counts |
| Ocean blue | #0A2463 | Cover background |
| Gold | #FFD766 | Cover subtitle |
| Light sky | #BBDDFF | Cover slogan |
| Table border | #DDDDDD | Grid lines |
| Alternate row | #F8F9FA | Stripe |
| Review orange | #E67E22 | Day 4 accent |
| Green teal | #1ABC9C | Day 7/30 accent |
| Header bg | #EAEAEA | Column header |
