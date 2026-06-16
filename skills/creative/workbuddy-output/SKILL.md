---
name: workbuddy-output
description: WorkBuddy-style ASCII box and grid table generator — proper grid tables with ├──┤ horizontal lines and │ vertical dividers, plus bordered card boxes. CJK/emoji-aware wcwidth alignment.
category: creative
triggers:
  - table
  - grid
  - box
  - format output
  - ascii table
  - 表格
  - 输出格式
---

# workbuddy-output: ASCII 网格表 & 信息框生成器

江姐的终端输出格式标准工具。所有表格类内容必须使用此工具生成，禁止手写 Markdown 表格。

## 强制规则

⚠️ **所有输出到终端的表格内容，必须按以下流程生成：**

1. 加载本技能
2. 用 `exec()` 载入 `scripts/box_maker.py`
3. 调用 `make_grid_table()` 或 `make_box()`
4. 调用 `verify_box()` 验证所有行宽度一致

**禁止：** 手写文本表格、Markdown `|---|` 管道表格、无网格线的纯空格排列。

## 核心函数

### `make_grid_table(headers, rows)`

带 ├──┤ 横线分隔 + │ 竖线分隔的完整网格表。

- `headers`: 列表，表头文字
- `rows`: 列表的列表，每行数据
- 返回值: 带框线的 ASCII 字符串

输出结构：
```
┌─────────┬─────────┬─────────┐
│ 标题1   │ 标题2   │ 标题3   │
╞═════════╪═════════╪═════════╡
│ 数据1   │ 数据2   │ 数据3   │
├─────────┼─────────┼─────────┤
│ 数据4   │ 数据5   │ 数据6   │
└─────────┴─────────┴─────────┘
```

### `make_box(title, lines, width=72)`

带标题的单栏信息框。

- `title`: 可选标题（支持 emoji）
- `lines`: 行列表，`'---'` 为分隔线
- `width`: 内容宽度（默认 72）
- 返回值: 带框线的 ASCII 字符串

### `verify_box(box_string)`

验证所有行的 display_width 一致。返回 True/False。失败时打印偏差行。

## 脚本文件

- `scripts/box_maker.py` — 核心生成器（含 wcwidth、CJK/emoji 对齐逻辑）

## 典型用法

```python
import sys
sys.path.insert(0, '~/.hermes/skills/creative/workbuddy-output/scripts')
from box_maker import make_grid_table, make_box, display_width, verify_box

# 网格表
grid = make_grid_table(
    ['项目', '状态', '备注'],
    [
        ['文件A', '✅', '已完成'],
        ['文件B', '⏳', '处理中'],
    ]
)
print(grid)

# 验证对齐
glines = grid.split('\n')
gexp = display_width(glines[0])
assert all(display_width(l) == gexp for l in glines)

# 信息框
box = make_box('📋 标题', ['行1', '行2', '---', '行3'])
print(box)
verify_box(box)
```

## 坑 & 注意事项

1. **`skill_view('workbuddy-output')` 可能返回"not found"** — 因为缓存未刷新。直接读 `scripts/box_maker.py` 路径。
2. **emoji 后跟 U+FE0F（VS16）** — 会被渲染为 2 格宽，即使 wcwidth 说它是 1。`box_maker.py` 已处理此逻辑（2026.5.11 修复）。
3. **零宽字符** — U+200D (ZWJ)、U+FE0F、U+20E3、U+FEFF (BOM) 宽度为 0，不影响对齐。
4. **画框线和 CJK 混合时** — 每个 CJK 字符 / emoji 占 2 格，ASCII 字符占 1 格。`box_maker.py` 的 `display_width()` 会正确计算。

## 样式要求（江姐2026.5.24定）— 从用户纠错中沉淀

此规则源自用户反馈。最初我输出只有竖线的纯 `│` 表，用户说：**"输出表格比较好，但提出一点建议，表格还要有横线（细线）"**。此后所有表格必须带完整网格线。

- **所有表格必须有横细线（├──┤）**，不能只有竖线
- 表头用 `╞═══╪═══╡` 双线分隔，数据行之间用 `├───┼───┤` 单线分隔
- 必须用 `verify_box()` 验证对齐
- 生成后检查所有行的 `display_width` 一致
- 严禁手写 Markdown `|---|` 管道表格或纯空格对齐表
- 输出前渲染一次实际效果让用户确认（首次使用时）

## 实测用例（2026.5.24 本会话验证）

成功生成了4列7行的数据版本对比表，含 `←` `❌` `✅` 等符号：

```python
grid = make_grid_table(
    ['项目', '~/.hermes/', 'hermes-sync/', '说明'],
    [
        ['MEMORY.md',     'May 24 18:07', 'May 13 00:01', '← 本地更新，待推送'],
        ['阿里云SSH',     '—',            '—',            '❌ 连接失败'],
    ]
)
print(grid)
verify_box(grid)
```

## 参考文件

- `references/2026-05-24-horizontal-lines-demand.md` — 用户要求加横线的完整会话记录与教训

## 优化建议

若终端字符集受限无法渲染 `╞═╪╡`（某些旧终端），可用纯 `├─┼┤` 替代表头分割线。`box_maker.py` 的 `head_sep` 变量可调整。
