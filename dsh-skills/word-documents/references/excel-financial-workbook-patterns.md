# Excel Financial Workbook Patterns (openpyxl)

For 财税服务 clients needing structured .xlsx templates: 期初余额调整表、工资表、折旧表、往来清理表等。

## When to Choose Excel over Word (.docx)

| 条件 | 推荐格式 |
|------|---------|
| 需用户自行填入数据 | ✅ **.xlsx** — 黄色单元格标记待填区域 |
| 需公式自动计算（SUM/IF/倒轧） | ✅ **.xlsx** — 公式嵌入单元格 |
| 需勾稽校验自动检查 | ✅ **.xlsx** — IF 公式显示"✓ 平衡"/"✗ 不平" |
| 用户反馈 ASCII 表格对齐有问题 | ✅ **.xlsx** — 天然网格对齐，跳过 ASCII 对齐问题 |
| 长篇报告、政策说明、叙述性文档 | ✅ .docx — 文字为主 |
| 用户明确要 Word | ✅ .docx |

## Installation (China Network)

```bash
# 清华镜像（推荐，速度快）
python3 -m pip install openpyxl -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
```

非中国网络直接用 `pip install openpyxl`。

## Core Patterns

### 1. Multi-Sheet Structure (Financial Adjustment Template)

```python
wb = openpyxl.Workbook()
ws0 = wb.active; ws0.title = '使用说明'
ws1 = wb.create_sheet('期初余额调整总表')
ws2 = wb.create_sheet('固定资产补提折旧')
ws3 = wb.create_sheet('配套凭证')
```

### 2. Style Definitions (Reusable)

```python
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

hdr_font = Font(name='微软雅黑', size=11, bold=True, color='FFFFFF')
title_font = Font(name='微软雅黑', size=14, bold=True)
sub_font = Font(name='微软雅黑', size=11, bold=True, color='1F4E79')
norm = Font(name='微软雅黑', size=10)
bold = Font(name='微软雅黑', size=10, bold=True)
small = Font(name='微软雅黑', size=9, color='666666')

hdr_fill = PatternFill('solid', fgColor='1F4E79')
light_fill = PatternFill('solid', fgColor='D6E4F0')
yellow_fill = PatternFill('solid', fgColor='FFF2CC')
green_fill = PatternFill('solid', fgColor='E2EFDA')
red_fill = PatternFill('solid', fgColor='FCE4EC')

thin = Border(*(Side('thin'),)*4)
center = Alignment(horizontal='center', vertical='center', wrap_text=True)
left = Alignment(horizontal='left', vertical='center', wrap_text=True)
right = Alignment(horizontal='right', vertical='center')

def sc(ws, r, c, v, font=norm, fill=None, align=left, border=thin, nf=None):
    cell = ws.cell(row=r, column=c, value=v)
    cell.font = font
    if fill: cell.fill = fill
    cell.alignment = align
    if border: cell.border = border
    if nf: cell.number_format = nf
    return cell
```

### 3. Color Code Convention (Standard for 财税 Templates)

| Color | Hex | Meaning | Usage |
|-------|-----|---------|-------|
| 🟡 Yellow | `FFF2CC` | 手动输入 | User fills data here |
| 🟢 Green | `E2EFDA` | 公式自动 | Calculated, do not edit |
| 🔵 Light Blue | `D6E4F0` | 分类/小计 | Section headers, subtotals |
| 🔵 Dark Blue | `1F4E79` | 表头(白字) | Column headers |
| 🔴 Light Red | `FCE4EC` | 校验行 | Check/validation |

### 4. Formula Injection Patterns

```python
# Basic SUM
ws.cell(row=total_row, column=5).value = f'=SUM(E{data_start}:E{data_end})'

# IF+N for blank-safe addition
sc(ws, row, 5, f'=IF(AND(C{row}="",D{row}=""),"",N(C{row})+N(D{row}))',
   bold, green_fill, right, nf='#,##0.00')

# Cross-row reference (固定资产净值 = 原值 + 累计折旧)
sc(ws, net_row, 5,
   f'=IF(OR(E{cost_row}="",E{depr_row}=""),"",N(E{cost_row})+N(E{depr_row}))',
   bold, green_fill, right, nf='#,##0.00')

# 倒轧 formula (未分配利润 = 资产-负债-其他权益)
eq_sum = '+'.join(f'N(E{r})' for r in equity_data_rows)
ws.cell(row=unprofit_row, column=5).value = \
    f'=IF(OR(E{asset_total}="",E{liab_total}=""),"",N(E{asset_total})-N(E{liab_total})-({eq_sum}))'

# Check formula — text result
ws.cell(row=check_row, column=5).value = \
    f'=IF(ABS(E{asset_total}-E{liab_total}-E{equity_total})<0.01,"✓ 平衡","✗ 不平")'
```

### 5. Merged Cells — Critical Pitfall

**Never write to a MergedCell.** Only the top-left (anchor) cell is writable:

**Approach A — Set value before merge:**
```python
ws['A1'] = 'Title Text'
ws.merge_cells('A1:F1')
```

**Approach B — Write to anchor after merge:**
```python
ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
sc(ws, r, 1, '标题', sub_font, light_fill, left)  # only (r, 1) is writable
```

### 6. Multi-Category Layout Pattern

For sections within one sheet (资产→负债→权益):

```python
data = [
    ('资产类', '货币资金', True, True, '以对账单为准'),
    ('资产类', '应收账款', True, True, '逐笔清理'),
    ('资产类', '▶ 资产合计', False, False, ''),
    ('负债类', '短期借款', True, True, ''),
]

current_cat = None
cat_start = {}
row = 4

for cat, name, inp_c, inp_d, note in data:
    if cat != current_cat:
        current_cat = cat
        cat_start[cat] = row
        # Merged header row
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
        sc(ws, row, 1, f'【{cat}】', sub_font, light_fill, left)
        row += 1
    # ... write data row, then subtotal = SUM(E{cat_start[cat]}:E{row-1})
    row += 1
```

## Verification

```python
wb.save(output_path)
import os
print(f"Size: {os.path.getsize(output_path)} bytes")
print(f"Sheets: {wb.sheetnames}")
```

## Common Pitfalls

1. **MergedCell write error**: Writing to any non-anchor cell in a merged range raises `AttributeError: 'MergedCell' object attribute 'value' is read-only`. Always write to the anchor only.
2. **Formulas use English punctuation**: Use `,` not `，` inside formulas. `SUM(A1,A2)` not `SUM(A1，A2)`.
3. **N() wrapper**: In IF statements, wrap cell refs in `N()`: `N(E{row})` returns 0 for empty cells, preventing `#VALUE!`.
4. **Sheet name quoting**: Chinese/numbered sheet names need single quotes in cross-sheet refs: `'固定资产补提折旧'!F3`.
5. **Number format**: `#,##0.00` for RMB amounts. No ¥ symbol unless explicitly requested.
