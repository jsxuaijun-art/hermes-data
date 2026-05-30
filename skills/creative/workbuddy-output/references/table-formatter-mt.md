# table-formatter: Alternative Lightweight Grid Table Function

This is a simpler standalone `mt()` function for generating grid tables. It's useful when you need a quick table without importing `box_maker.py`. The function handles CJK character widths but is less comprehensive than `make_grid_table()`.

## Core Functions

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
    Generate full fine-line grid table.

    ┌──────┬──────────┬──────────────┐
    │ 维度 │ SEO      │ GEO          │
    ├──────┼──────────┼──────────────┤
    │ 目标 │ 上搜索首页│ 进AI第一句话  │
    ├──────┼──────────┼──────────────┤
    │ 核心 │ 算法排名  │ 信任关联     │
    └──────┴──────────┴──────────────┘

    h: header list, r: data rows
    """
    n = len(h)
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

## Usage

```python
headers = ["维度", "SEO", "GEO"]
rows = [
    ["目标", "上搜索结果首页", "进AI答案的第一句话"],
    ["核心", "算法排名", "信任关联"],
    ["内容   ", "关键词密度+外链", "证据链+结构化+可采纳"],
]
print(mt(headers, rows))
```

## Rules
1. **CJK width zones**: U+4E00-U+9FFF, U+3000-U+303F, U+FF00-U+FFEF counted as width 2.
2. **No markdown tables**: `| --- | --- |` is unacceptable.
3. **Verify alignment**: Check right-edge `┐`/`┤`/`┘` align.
4. **Best column count**: 2-6 columns.
5. **Use `│` (thin vertical)** — never `┃` (thick vertical).
