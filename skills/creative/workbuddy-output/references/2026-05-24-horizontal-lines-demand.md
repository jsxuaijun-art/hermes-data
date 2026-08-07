# 用户要求加横线的完整记录（2026.5.24）

## 背景

会话任务是检查 GitHub 同步状态。我输出了一个纯 `│` 竖线表格（无横线分隔），展示了 `~/.hermes/` 和 `hermes-sync/` 的数据版本对比。

用户反馈：**"输出表格比较好，但提出一点建议，表格还要有横线（细线）。"**

## 教训

- 初始输出用了我「手写」的管道表 `│` 风格，只有竖线，没有横线 `├──┤`
- 用户不是否定表格本身，而是要求**增加横线**变成完整网格
- 纠正后我用了 `make_grid_table()` 生成完整网格表，用户确认满意

## 解决方案

调用 `workbuddy-output` skill 的 `scripts/box_maker.py`：

```python
import sys
# 方式A：从 skill_view 加载脚本
script_content = skill_view('workbuddy-output', file_path='scripts/box_maker.py')
exec(script_content)

# 方式B：直接 import
sys.path.insert(0, '/home/dmin/.hermes/skills/creative/workbuddy-output/scripts')
from box_maker import make_grid_table, make_box, display_width, verify_box
```

关键点：
- 用 `make_grid_table()` 生成带 `├──┤` 和 `│` 的完整网格表
- 用 `verify_box()` 验证对齐
- 不允许手写文本表格或 Markdown `|---|`

## 最终效果（用户认可）

```
┌─────────────┬──────────────┬─────────────────┬────────────────────┐
│ 项目        │ ~/.hermes/   │ hermes-sync/    │ 说明               │
╞═════════════╪══════════════╪═════════════════╪════════════════════╡
│ MEMORY.md   │ May 24 18:07 │ May 13 00:01    │ ← 本地更新，待推送 │
├─────────────┼──────────────┼─────────────────┼────────────────────┤
│ ...         │ ...          │ ...             │ ...                │
└─────────────┴──────────────┴─────────────────┴────────────────────┘
```

## 后续强化

- 将此规则写入 SOUL.md 的 `【2026.5.10 强制输出规则 — ASCII 表格格式】` 部分
- 更新 SKILL.md 的样式要求章节，直接引用用户原话
- 任何时候输出表格，默认走 `make_grid_table()`，不思考「要不要横线」
