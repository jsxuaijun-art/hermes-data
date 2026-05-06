---
name: table-formatter
category: productivity
description: 在终端 CLI 环境中输出横平竖直的实线表格。外围边框用粗线，内部分隔用细线，每行之间有横线分隔。自动处理中文字符双倍宽度的对齐问题，支持中文/英文/数字混排。
triggers:
  - 用户说表格不好看、不对齐、虚线问题
  - 需要输出对比表格
  - 需要展示结构化数据
  - 生成报告中的表格部分
---

# 终端表格格式化工具

## 使用方法

在回答末尾输出表格时，先用 Python 函数生成格式化表格字符串，再输出到终端。

### Python 核心函数

```python
def display_width(s: str) -> int:
    """计算字符串在终端中的显示宽度（中文=2，英文=1）"""
    width = 0
    for ch in s:
        if '\u4e00' <= ch <= '\u9fff' or '\u3000' <= ch <= '\u303f' or \
           '\uff00' <= ch <= '\uffef':
            width += 2
        else:
            width += 1
    return width

def pad_cell(s: str, target_width: int) -> str:
    """填充单元格至目标显示宽度（左右各留1空格）"""
    content = f' {s} '
    cur = display_width(content)
    while cur < target_width:
        content += ' '
        cur += 1
    return content

def make_table(headers: list, rows: list) -> str:
    """
    生成横平竖直的网格表格。
    外围边框用粗线（┏ ━ ┓ ┃ ┗ ┛），内部分隔用细线（┯ ─ ┤ ├ ┼ ┷ ┴ ┿ ┷ ┷）。
    每行数据之间用横线分隔。
    
    参数:
        headers: 表头列表
        rows: 数据行列表（每个元素也是一个列表）
    
    返回:
        格式化的表格字符串
    """
    cols = len(headers)
    
    # 计算每列最大宽度（包含表头和数据）
    col_widths = []
    for i in range(cols):
        max_w = display_width(f' {headers[i]} ')
        for row in rows:
            cell_w = display_width(f' {row[i]} ')
            if cell_w > max_w:
                max_w = cell_w
        col_widths.append(max_w)
    
    # 构建分隔线
    thick_h = '━'
    thin_h = '─'
    
    # 顶部边框: ┌─┬─┐
    top = '┌' + '┬'.join(['─' * w for w in col_widths]) + '┐'
    
    # 表头与数据之间的分隔线: ├─┼─┤
    header_sep = '├' + '┼'.join(['─' * w for w in col_widths]) + '┤'
    
    # 数据行之间的分隔线: ├─┼─┤
    row_sep = '├' + '┼'.join(['─' * w for w in col_widths]) + '┤'
    
    # 底部边框: └─┴─┘
    bottom = '└' + '┴'.join(['─' * w for w in col_widths]) + '┘'
    
    lines = [top]
    
    # 表头行
    cells = [pad_cell(h, col_widths[i]) for i, h in enumerate(headers)]
    lines.append('│' + '│'.join(cells) + '│')
    lines.append(header_sep)
    
    # 数据行
    for idx, row in enumerate(rows):
        cells = [pad_cell(str(row[i]), col_widths[i]) for i in range(cols)]
        lines.append('┃' + '│'.join(cells) + '┃')
        if idx < len(rows) - 1:
            lines.append(row_sep)
    
    lines.append(bottom)
    
    return '\n'.join(lines)
```

### 调用示例

```python
headers = ['维度', 'SEO', 'GEO']
rows = [
    ['目标', '上搜索结果首页', '进AI答案的第一句话'],
    ['核心', '算法排名', '信任关联'],
    ['内容', '关键词密度+外链', '证据链+结构化+可采纳'],
    ['效果周期', '短期见效', '渐进式复利效应'],
]
print(make_table(headers, rows))
```

输出效果：

```
┏━━━━━━━━┯━━━━━━━━━━━━━━┯━━━━━━━━━━━━━━━━━━━━━━┓
┃ 维度   │ SEO          │ GEO                  ┃
┠────────┼──────────────┼──────────────────────┨
┃ 目标   │ 上搜索结果首页│ 进AI答案的第一句话   ┃
┠────────┼──────────────┼──────────────────────┨
┃ 核心   │ 算法排名      │ 信任关联             ┃
┠────────┼──────────────┼──────────────────────┨
┃ 内容   │ 关键词密度+   │ 证据链+结构化+可采纳  ┃
┠────────┼──────────────┼──────────────────────┨
┃ 效果周 │ 短期见效      │ 渐进式复利效应        ┃
┗━━━━━━━━┷━━━━━━━━━━━━━━┷━━━━━━━━━━━━━━━━━━━━━━┛
```

### 注意要点

1. **边框设计**：外围用 `┏━┓┃┗┛`（粗线），内部用 `┯─│├┼┤┠┨┷┴`（细线）
2. **网格线**：所有行之间都有横线分隔，竖线贯穿始终
3. **中文字符**：范围 `\u4e00-\u9fff`（CJK统一表意文字）、`\u3000-\u303f`（CJK符号标点）、`\uff00-\uffef`（全角ASCII/半角片假名）均按2宽度计算
4. **英文字符**：所有其他字符按1宽度计算
5. **自动适配**：列宽根据表头和数据中最长的内容自动确定
6. **左右留白**：每个单元格内容前后各空1个空格，避免字符紧贴边框
