# Terminal Grid Table Formatting (table-formatter absorbed)

This skill was absorbed from the standalone `table-formatter` skill (archived). It provides a Python function for creating clean grid tables in terminal output using Unicode box-drawing characters, with correct Chinese character width handling.

## When to use

- Displaying comparison tables, checklists, or structured data in CLI output
- Chinese-language tables where CJK characters need double-width alignment
- Any structured output that benefits from visible grid lines

## Core function

```python
def dw(s):
    """Calculate terminal display width: CJK=2, ASCII=1"""
    w = 0
    for c in s:
        if '\u4e00' <= c <= '\u9fff' or '\u3000' <= c <= '\u303f' or '\uff00' <= c <= '\uffef':
            w += 2
        else:
            w += 1
    return w

def pc(s, tw):
    """Pad cell to target display width"""
    c = f' {s} '
    while dw(c) < tw:
        c += ' '
    return c

def mt(h, r):
    """
    Generate full grid table with fine-line style.
    ┌──────┬──────────┬──────────────┐
    │ 维度 │ SEO      │ GEO          │
    ├──────┼──────────┼──────────────┤
    │ 目标 │ 上搜索首页│ 进AI第一句话 │
    └──────┴──────────┴──────────────┘

    h: header list
    r: list of data rows (each row is a list)
    """
    n = len(h)
    # Calculate column widths
    cw = []
    for i in range(n):
        m = dw(f' {h[i]} ')
        for row in r:
            x = dw(f' {row[i]} ')
            if x > m: m = x
        cw.append(m)

    top = '┌' + '┬'.join(['─' * w for w in cw]) + '┐'
    sep = '├' + '┼'.join(['─' * w for w in cw]) + '┤'
    bot = '└' + '┴'.join(['─' * w for w in cw]) + '┘'

    L = [top]
    L.append('│' + '│'.join([pc(h[i], cw[i]) for i in range(n)]) + '│')
    L.append(sep)

    for idx, row in enumerate(r):
        L.append('│' + '│'.join([pc(str(row[i]), cw[i]) for i in range(n)]) + '│')
        if idx < len(r) - 1:
            L.append(sep)

    L.append(bot)
    return '\n'.join(L)
```

## Style specification

- Full fine-line style: outer frame `┌─┬─┐`, inner dividers `├─┼─┤`, vertical bars `│`
- Every row has a horizontal separator (grid table)
- Left-right vertical bars aligned (CJK character width counted double)
- Cell content padded with 1 space before and after

## Character width rules

| Range | Width | Description |
|-------|-------|-------------|
| `\u4e00` - `\u9fff` | 2 | CJK Unified Ideographs |
| `\u3000` - `\u303f` | 2 | CJK Symbols and Punctuation |
| `\uff00` - `\uffef` | 2 | Fullwidth ASCII variants |
| Everything else | 1 | ASCII, digits, punctuation |

## Example output

```
┌──────────┬──────────────────────┬──────────────────────────────┐
│ 维度     │ SEO                  │ GEO                          │
├──────────┼──────────────────────┼──────────────────────────────┤
│ 目标     │ 上搜索结果首页        │ 进AI答案的第一句话           │
├──────────┼──────────────────────┼──────────────────────────────┤
│ 核心     │ 算法排名              │ 信任关联                     │
└──────────┴──────────────────────┴──────────────────────────────┘
```

## Table gallery

### 3-column comparison table
```
┌──────────┬──────────────────────┬──────────────────────────────┐
│ 维度     │ SEO                  │ GEO                          │
├──────────┼──────────────────────┼──────────────────────────────┤
│ 目标     │ 上搜索结果首页        │ 进AI答案的第一句话           │
├──────────┼──────────────────────┼──────────────────────────────┤
│ 核心     │ 算法排名              │ 信任关联                     │
└──────────┴──────────────────────┴──────────────────────────────┘
```

### 4-column data table
```
┌──────────────┬────────┬─────────┬────────┐
│ 指标         │ 2025年 │ 2026年e │ 变化   │
├──────────────┼────────┼─────────┼────────┤
│ 市场规模(亿) │ 6      │ 89      │ +1383% │
├──────────────┼────────┼─────────┼────────┤
│ AI渗透率     │ 17.7%  │ 36.5%   │ +106%  │
└──────────────┴────────┴─────────┴────────┘
```

### 2-column list table
```
┌───────────────────┬─────────────────────────────┐
│ 技能              │ 说明                        │
├───────────────────┼─────────────────────────────┤
│ geo-optimization  │ GEO方法论（已融合财税实战） │
├───────────────────┼─────────────────────────────┤
│ table-formatter   │ 终端表格格式化              │
└───────────────────┴─────────────────────────────┘
```

## Caution

- Best column count: 2-6. More than 6 may wrap on terminal.
- Use `│` (fine vertical bar) consistently — not `┃` (thick bar)
- Do NOT output markdown tables (`|---|`) for terminal display
- Always call `mt()` to generate the string, check alignment, then paste into reply
