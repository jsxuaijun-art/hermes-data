---
name: powerpoint
description: "Create, read, edit .pptx decks, slides, notes, templates."
license: Proprietary. LICENSE.txt has complete terms
platforms: [linux, macos, windows]
---

# Powerpoint Skill

## When to use

Use this skill any time a .pptx file is involved in any way — as input, output, or both. This includes: creating slide decks, pitch decks, or presentations; reading, parsing, or extracting text from any .pptx file (even if the extracted content will be used elsewhere, like in an email or summary); editing, modifying, or updating existing presentations; combining or splitting slide files; working with templates, layouts, speaker notes, or comments. Trigger whenever the user mentions "deck," "slides," "presentation," or references a .pptx filename, regardless of what they plan to do with the content afterward. If a .pptx file needs to be opened, created, or touched, use this skill.

## Quick Reference

| Task | Guide |
|------|-------|
| Read/analyze content | `python -m markitdown presentation.pptx` |
| Edit or create from template | Read [editing.md](editing.md) |
| Create from scratch | Read [pptxgenjs.md](pptxgenjs.md) |

---

## Reading Content

```bash
# Text extraction
python -m markitdown presentation.pptx

# Visual overview
python scripts/thumbnail.py presentation.pptx

# Raw XML
python scripts/office/unpack.py presentation.pptx unpacked/
```

---

## Editing Workflow

**Read [editing.md](editing.md) for full details.**

1. Analyze template with `thumbnail.py`
2. Unpack → manipulate slides → edit content → clean → pack

---

## Creating from Scratch

**Read [pptxgenjs.md](pptxgenjs.md) for full details.**

Use when no template or reference presentation is available.

---

## Design Ideas

**Don't create boring slides.** Plain bullets on a white background won't impress anyone. Consider ideas from this list for each slide.

### Before Starting

- **Pick a bold, content-informed color palette**: The palette should feel designed for THIS topic. If swapping your colors into a completely different presentation would still "work," you haven't made specific enough choices.
- **Dominance over equality**: One color should dominate (60-70% visual weight), with 1-2 supporting tones and one sharp accent. Never give all colors equal weight.
- **Dark/light contrast**: Dark backgrounds for title + conclusion slides, light for content ("sandwich" structure). Or commit to dark throughout for a premium feel.
- **Commit to a visual motif**: Pick ONE distinctive element and repeat it — rounded image frames, icons in colored circles, thick single-side borders. Carry it across every slide.

### Color Palettes

Choose colors that match your topic — don't default to generic blue. Use these palettes as inspiration:

| Theme | Primary | Secondary | Accent |
|-------|---------|-----------|--------|
| **Midnight Executive** | `1E2761` (navy) | `CADCFC` (ice blue) | `FFFFFF` (white) |
| **Forest & Moss** | `2C5F2D` (forest) | `97BC62` (moss) | `F5F5F5` (cream) |
| **Coral Energy** | `F96167` (coral) | `F9E795` (gold) | `2F3C7E` (navy) |
| **Warm Terracotta** | `B85042` (terracotta) | `E7E8D1` (sand) | `A7BEAE` (sage) |
| **Ocean Gradient** | `065A82` (deep blue) | `1C7293` (teal) | `21295C` (midnight) |
| **Charcoal Minimal** | `36454F` (charcoal) | `F2F2F2` (off-white) | `212121` (black) |
| **Teal Trust** | `028090` (teal) | `00A896` (seafoam) | `02C39A` (mint) |
| **Berry & Cream** | `6D2E46` (berry) | `A26769` (dusty rose) | `ECE2D0` (cream) |
| **Sage Calm** | `84B59F` (sage) | `69A297` (eucalyptus) | `50808E` (slate) |
| **Cherry Bold** | `990011` (cherry) | `FCF6F5` (off-white) | `2F3C7E` (navy) |

### For Each Slide

**Every slide needs a visual element** — image, chart, icon, or shape. Text-only slides are forgettable.

**Layout options:**
- Two-column (text left, illustration on right)
- Icon + text rows (icon in colored circle, bold header, description below)
- 2x2 or 2x3 grid (image on one side, grid of content blocks on other)
- Half-bleed image (full left or right side) with content overlay

**Data display:**
- Large stat callouts (big numbers 60-72pt with small labels below)
- Comparison columns (before/after, pros/cons, side-by-side options)
- Timeline or process flow (numbered steps, arrows)

**Visual polish:**
- Icons in small colored circles next to section headers
- Italic accent text for key stats or taglines

### Typography

**Choose an interesting font pairing** — don't default to Arial. Pick a header font with personality and pair it with a clean body font.

| Header Font | Body Font |
|-------------|-----------|
| Georgia | Calibri |
| Arial Black | Arial |
| Calibri | Calibri Light |
| Cambria | Calibri |
| Trebuchet MS | Calibri |
| Impact | Arial |
| Palatino | Garamond |
| Consolas | Calibri |

| Element | Size |
|---------|------|
| Slide title | 36-44pt bold |
| Section header | 20-24pt bold |
| Body text | 14-16pt |
| Captions | 10-12pt muted |

### Spacing

- 0.5" minimum margins
- 0.3-0.5" between content blocks
- Leave breathing room—don't fill every inch

### Avoid (Common Mistakes)

- **Don't repeat the same layout** — vary columns, cards, and callouts across slides
- **Don't center body text** — left-align paragraphs and lists; center only titles
- **Don't skimp on size contrast** — titles need 36pt+ to stand out from 14-16pt body
- **Don't default to blue** — pick colors that reflect the specific topic
- **Don't mix spacing randomly** — choose 0.3" or 0.5" gaps and use consistently
- **Don't style one slide and leave the rest plain** — commit fully or keep it simple throughout
- **Don't create text-only slides** — add images, icons, charts, or visual elements; avoid plain title + bullets
- **Don't forget text box padding** — when aligning lines or shapes with text edges, set `margin: 0` on the text box or offset the shape to account for padding
- **Don't use low-contrast elements** — icons AND text need strong contrast against the background; avoid light text on light backgrounds or dark text on dark backgrounds
- **NEVER use accent lines under titles** — these are a hallmark of AI-generated slides; use whitespace or background color instead

---

## QA (Required)

**Assume there are problems. Your job is to find them.**

Your first render is almost never correct. Approach QA as a bug hunt, not a confirmation step. If you found zero issues on first inspection, you weren't looking hard enough.

### Content QA

```bash
python -m markitdown output.pptx
```

Check for missing content, typos, wrong order.

**When using templates, check for leftover placeholder text:**

```bash
python -m markitdown output.pptx | grep -iE "xxxx|lorem|ipsum|this.*(page|slide).*layout"
```

If grep returns results, fix them before declaring success.

### Visual QA

**⚠️ USE SUBAGENTS** — even for 2-3 slides. You've been staring at the code and will see what you expect, not what's there. Subagents have fresh eyes.

Convert slides to images (see [Converting to Images](#converting-to-images)), then use this prompt:

```
Visually inspect these slides. Assume there are issues — find them.

Look for:
- Overlapping elements (text through shapes, lines through words, stacked elements)
- Text overflow or cut off at edges/box boundaries
- Decorative lines positioned for single-line text but title wrapped to two lines
- Source citations or footers colliding with content above
- Elements too close (< 0.3" gaps) or cards/sections nearly touching
- Uneven gaps (large empty area in one place, cramped in another)
- Insufficient margin from slide edges (< 0.5")
- Columns or similar elements not aligned consistently
- Low-contrast text (e.g., light gray text on cream-colored background)
- Low-contrast icons (e.g., dark icons on dark backgrounds without a contrasting circle)
- Text boxes too narrow causing excessive wrapping
- Leftover placeholder content

For each slide, list issues or areas of concern, even if minor.

Read and analyze these images:
1. /path/to/slide-01.jpg (Expected: [brief description])
2. /path/to/slide-02.jpg (Expected: [brief description])

Report ALL issues found, including minor ones.
```

### Verification Loop

1. Generate slides → Convert to images → Inspect
2. **List issues found** (if none found, look again more critically)
3. Fix issues
4. **Re-verify affected slides** — one fix often creates another problem
5. Repeat until a full pass reveals no new issues

**Do not declare success until you've completed at least one fix-and-verify cycle.**

---

## Converting to Images

Convert presentations to individual slide images for visual inspection:

```bash
python scripts/office/soffice.py --headless --convert-to pdf output.pptx
pdftoppm -jpeg -r 150 output.pdf slide
```

This creates `slide-01.jpg`, `slide-02.jpg`, etc.

To re-render specific slides after fixes:

```bash
pdftoppm -jpeg -r 150 -f N -l N output.pdf slide-fixed
```

---

## Pitfalls — pptxgenjs 单位陷阱（直接导致「文字重叠/重影」）

**`lineSpacing` 的单位是「磅」，不是倍数。** 想设 1.3 倍行距必须写
`lineSpacingMultiple: 1.3`（写入 `<a:spcPct>`）；写成 `lineSpacing: 1.3`
会得到「行距 1.3 磅」——比字还矮，**同一段的多行文字叠印成一坨**，
肉眼就是文字重叠/重影。

- 症状指纹：多行正文/副标题糊在一起，单行文字却完全正常 → 先查这一条。
- 核实（解开 pptx 查 XML，10 秒定案）：
  `unzip -o out.pptx -d /tmp/x && grep -o 'spcPct val="[0-9]*"' /tmp/x/ppt/slides/slideN.xml`
  正确是 `spcPct val="130000"`（130%），错误是 `spcPts val="130"`。
  注意 `spcPts` 若出现在 `spcAft`/`spcBef` 里是正常的（那是 paraSpaceAfter/Before，单位本来就是磅）。
- 修复后必须复算高度：单行高 ≈ 字号 × 1.2 × 倍数；改对后多行正文会**明显变高**，
  可能撑破卡片 → 重新核对每个正文框的高度是否够。

## 装不了 LibreOffice 时的排版验证（Windows + WSL 无目视闭环）

Linux 侧没有 `soffice`、`sudo apt` 又要密码时，用 **Windows PowerPoint COM 当真值渲染器**
（渲染结果与用户所见一致）。三步闭环：

```bash
# 1) COM 导出每页 PNG
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\\path\\export.ps1"
# 2) COM 导出每个形状的框几何 + 文字边界 → tsv
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\\path\\dshapes.ps1"
# 3) 像素行带检测 + 文本框相交检测（python + Pillow）
python3 pixcheck.py && python3 final_check.py
```

**COM 字段可信度（实测，别踩）：**
- 可靠：`Shape.Left/Top/Width/Height`；`TextRange.Lines().Count`（真实渲染行数）；
  逐行 `Lines(i).BoundLeft/BoundWidth`（最宽行宽）；`TextFrame.VerticalAnchor`；
  `ParagraphFormat.LineRuleWithin`（true=倍数 / false=磅）。
- **不可靠**：`BoundHeight`、`BoundTop` 对多行文本严重失真（曾对 40pt 行返回 1pt）。
  判断增高一律用 `行数 × 字号 × 1.2 × 倍数`，不要用 BoundHeight。
- 多数文本框是垂直居中（`VerticalAnchor=3`），文字矩形 = `框top + (框高 - 文字高)/2`。
- PowerPoint 导出的 PNG 是中文名（`幻灯片1.PNG`），先重命名成 ASCII 再处理。

**两类不靠肉眼也能抓的缺陷：**
1. **文本框相交**：用框 rect 做矩形相交（面积>阈值报警）。注意「页面标题框 vs 右上角品牌标签框」
   常见**框相交但文字不碰**的假阳性 —— 必须再用「标题文字右缘 br」对「品牌标签文字左缘 bl」
   复核，真正相碰才修。
2. **文字塌缩/溢出**：把每页 PNG 逐框裁出，按「与背景色差异」统计每行墨迹像素并归并成「行带」。
   正常 N 行文字应得 N 条独立行带；行带数 < N = 多行叠印；墨迹纵向超出框 = 溢出。

## 会话模型读不了图时的兜底（便宜视觉模型自动降级）

若 `vision_analyze` 报 `does not accept input types: image`，说明 `auxiliary.vision`
指到了纯文本模型。指到一个**便宜的视觉模型**即可自动降级，无需更换主模型：

```bash
hermes config set auxiliary.vision.model Doubao-Seed-2.1-Pro
hermes config set auxiliary.vision.base_url https://aigw.telecomjs.com/v1
hermes config set auxiliary.vision.api_key '${TELECOM_DOUBAO_KEY}'
```

（`~/.hermes/config.yaml` 受保护，agent 不能用 patch/write 直接改，必须走 `hermes config set`。）
配置完用一张**已知内容**的图验证（例：图里写随机码 `QX7-7271-BLUE`，看模型能否读对），
探针脚本与渠道选择见 `hermes-free-model-channels` 技能。

## 对外材料的「事实纪律」——无据不得杜撰（2026-10 徐总纪律固化）

做公司介绍/方案/汇报类 PPT 时，凡**具体事实**——学历院校届别、评审通过人数/通过率、
行业占比、客户数量/转介绍比例、成立年份、资质分数——**没有真实来源就绝不能编**。
占位可以留（为了版面完整），但必须做到三条：

1. **醒目标记**：把未核实内容用高辨识色渲染（例：`#C00000` 深红），并加"待核实"角标；
   不要在交付件里让它长得像真数据。
2. **显式清单**：另附一份《待核实清单》(md/txt)，逐项写清"第几页·哪句话·要填什么·依据从哪来"。
3. **主动提醒**：在回复里明确点名"此处系占位/待核实，请按真实情况修改"。

实现套路（build.js 里加两个小工具函数，全篇复用）：
```js
const TODO = "C00000";                     // 待核实标记色
function todoTag(slide, x, y, w=1.15, h=0.28, text="待核实") {   // 红底白字角标
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.06, fill:{ color: TODO } });
  slide.addText(text, { x, y, w, h, align:"center", valign:"middle", fontSize: 9, bold: true, color:"FFFFFF", margin: 0 });
}
function imgSlot(slide, x, y, w, h, label) { // 图片占位：红色虚线框
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE,
    { x, y, w, h, rectRadius: 0.08, fill:{ color:"FFF5F5" }, line:{ color: TODO, width: 1.25, dashType:"dash" } });
  slide.addText(label, { x, y, w, h, align:"center", valign:"middle", fontSize: 10, color: TODO, margin: 0.12, lineSpacingMultiple: 1.2 });
}
```
数字类用 `color: TODO` 渲染，旁边挂 `todoTag`；标题页眉写一句
"⚠ 下列数字为占位示例：请替换为……真实数据，并附年份+文号/链接"。

**配图的诚实边界**：装饰性图形（同心圆环、色块、线条）随便用；**原生图表**用
`slide.addChart(pres.shapes... pres.charts.BAR, [{name, labels, values}], opts)` 生成真图表（可编辑）；
但**绝不能放暗示"这是本公司实景/本团队成员"的网图或 AI 图**。要放就放**占位框**（`imgSlot`），
让客户自己填真实照片/证书截图。

- 原生横向条形图要点：`barDir:"bar"`、`showValue:true`、`dataLabelPosition:"outEnd"`、
  `showLegend:false`、`valGridLine:{style:"none"}`、`catGridLine:{style:"none"}`；生成后
  pptx 内会多出 `ppt/charts/chart1.xml`（`unzip -l` 可验）。范围要另留一行小字标注数据来源/状态。

## 大字号多行「视觉粘连」——封面标题常见坑（2026-10 实证）

封面/章节页的主标题常写成单段 `"第一行\n第二行"` 且行距压得很紧（如
`lineSpacingMultiple: 1.05`）。**字号越大，1.05 越致命**：40pt 字下 1.05 只留 ≈2pt 行间空隙，
两行在像素层面**粘成一体**，肉眼就是"两行糊在一起"，像素行带检测会判出 `1 band`（应为 2）。

- 经验阈值：**≥28pt 的多行标题，行距给到 1.25~1.3**（`lineSpacingMultiple: 1.28`）。
- 复核方法不是靠肉眼：裁出**纯文字实际区间**（避开装饰图形），逐行统计墨迹像素、归并成行带，
  N 行文字应得 N 条独立行带。**本技能自带脚本 `scripts/line_bands.py`**：
  `python3 line_bands.py slide-01.png --box 0.70,1.50,7.60,3.35 --expect 2 --ink light`
- ⚠ **装饰图形的行带假阳性**：若新加的金环/色块等装饰**落在该文本框的矩形范围内**，
  装饰笔画会把两行之间的空隙填满 → 检测误判"多行叠印"。**排查：把裁切区缩到文字实际宽高
  （避开装饰所在 x/y 区间）再测**。别为假阳性去瞎改行距。

## Dependencies

- `pip install "markitdown[pptx]"` - text extraction
- `pip install Pillow` - thumbnail grids
- `npm install -g pptxgenjs` - creating from scratch
- LibreOffice (`soffice`) - PDF conversion (auto-configured for sandboxed environments via `scripts/office/soffice.py`)
- Poppler (`pdftoppm`) - PDF to images
