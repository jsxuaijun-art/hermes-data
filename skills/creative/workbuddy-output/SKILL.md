---
name: workbuddy-output
description: >
  Generate terminal output in WorkBuddy style - emoji + bold titles, ASCII
  border cards with precise right-edge alignment using CJK-aware wcwidth.
  Covers box generation, grid tables, wcwidth pitfalls, and verification.
metadata:
  hermes:
    tags: [workbuddy, terminal, formatting, wcwidth, cjk, ascii-box, grid-table, creative-output]
    related_skills: [ascii-art]
---

# WorkBuddy Output Style

<<<<<<< HEAD
## 🚨 强制加载规则 + 循环刹车（2026.5.10-12 江姐定）

### 规则A：必须尝试表格
=======
## 🚨 最高等级约束 — 表格格式红线（2026.5.12 更新）

**这是本技能第一条规则。必须先读这条，再读下面任何内容。不遵守 = 用户放弃信任。**

### 核心规则

**绝对禁止在回复正文中出现任何 Markdown 表格格式。** 包括但不限于：

```
| 项目 | 价格 |
|:---|:---:|       ← 禁止
| 项目 | 价格 |     ← 禁止（即使没有分隔线）
```

只要内容涉及「对比、清单、步骤、方案、价格、配置、参数」等结构化数据 → **必须**强制走以下路径：

```
检测到结构化数据
    ↓
立即中断当前回复草稿（不允许发送）
    ↓
切换至 execute_code 模式
    ↓
exec(open(box_maker.py).read())
    ↓
make_grid_table() 或 make_box()
    ↓
verify_box() 全通过
    ↓
输出
```

### 心理机制（这不是「记不住」，是惯性）

**根因：** Markdown 表格是我的原生输出路径（打字直接出来，思考成本为零）。box_maker 是需要刻意切换到 execute_code + Python 的外部管道。快速回复时，大脑自动走默认路径。

**这不是记忆力问题，是动作惯性问题。** 唯一的解法是在「生成回复草稿 → 发送」之间设一个物理阻断：

```
在你即将输出任何包含 | 或 ┌ 或 ── 的字符之前 → 刹车 → 确认来源
如果这行字符是你手打的（不是 execute_code 输出）→ 删掉重来
```

### 用户已明确表达的标准（2026.5.12 用户原话）

> 「对啊，以后就要这样输出表格。」
> 「你也说过很多次要遵守规定的，但还是经常出错，是记不住还是其他原因？」

**这意味着：** 用户不再接受「我下次会注意」这类表态。唯一能重建信任的方式是：**再看到一次 Markdown 表格，整段重做，不辩解。**

### 强制预检流程

在每次输出**任何内容**之前（无论多短、多快的回复），必须执行以下预检：

```
预检步骤：
Step 0 ─ 扫描我的回复草稿中是否包含任何 `|---|` 或 `| :---` 或 `|:---` 字符串
Step 1 ─ 如果发现 → 立即整段删除回复草稿，不允许发送
Step 2 ─ 切换至 execute_code 模式
Step 3 ─ 加载 box_maker.py → exec() → make_grid_table()/make_box() → verify_box()
Step 4 ─ 只有 verify_box() 全通过后，才能输出
```

**关键记忆锚点：** 如果我在回复草稿中写了 `|` 符号且后面跟着 `-` 或 `:`，这 100% 是一个 Markdown 表格 — 刹车！

如果预检没做就输出了 → 用户说「违规」→ 整段重做，不辩解，不修补。

## ⚠️ 强制加载规则（江姐 2026.5.10 定，5.11 补充）
>>>>>>> 610b90e (sync 2026-05-12_23:56)

**本技能必须在每次输出含结构化数据/对比/列表时加载。** 步骤如下：

1. 先用 `skill_view('workbuddy-output', file_path='scripts/box_maker.py')` 读取脚本
2. 用 `exec(open(script_path).read())` 载入 `make_grid_table()` / `make_box()` 函数
3. 用该函数生成表格，**禁止手写、禁止 Markdown `|---|` 替代**
4. 生成后调用 `verify_box()` 验证所有行 dw 一致

### ⚠️ 2026.5.11 追加：Markdown 表格滑脱陷阱

**问题：** 在对话中，Hermes 多次在 inline 文本（非 execute_code 块）中手写 Markdown 表格：

```
| 项目 | 推荐 | 价格 |
|:---|:---|:---:|
```

这违反了强制规则，用户两次纠正：「表格你要按照早前的约定或记忆进行修改，横平竖直，成一条直线」。

**根因：** execute_code 调用 box_maker 需要「意识到需要格式化输出 → 主动加载技能 → 写代码」这个链条。而 Markdown 表格是 0 思考成本的自然习惯。在快速回复的场景下，容易滑向 Markdown 表格。

**强制触发条件：** 以下任何一个条件满足，**必须**用 make_grid_table() 而非 Markdown 写法：
- 内容包含「对比、清单、步骤、方案、价格」等结构化数据
- 你正在写 `|---|` 或 `| :--- |` 这样的字符串
- 用户之前就表格格式纠正过你

**纠正流程（已激活两次，不激活第三次）：**
1. 用户指出表格问题 → 立即承认，不辩解
2. 加载本技能 → exec(box_maker.py) → 重新生成
3. 调用 verify_box() 确认每行 dw 一致
4. 如果用户说「重新输出」→ 整段全部重做，不修修补补

这条规则已写入 memory 红线，跳过 = 不可靠。

### 规则B：一次不行立刻兜底（重要程度 ≥ 规则A）

**核心原则：用户要的是数据，不是格式修复。不要在ASCII表格对齐上纠缠。一次用户说不行就转，不需要三次。**

当用户指出表格显示不对/不对齐（即使 verify_box() 通过）：

1. **立即承认** — 不辩解，直接说"终端渲染问题，我直接出文件"
2. **主动提出替代方案** — **不等用户问**，直接说：
   > "我出个 .docx 放你桌面吧，终端显示不太稳。"
3. **跳过任何纠错循环** — 不允许出现 "让我重新生成一次" / "我调整一下" / "让我再试试"。一次不行就转，只有一次尝试机会
4. **兜底优先级**：
   - 🥇 .docx（用户默认交付格式，正规排版，见 word-documents 技能）
   - 🥈 .xlsx（数据模板类，天然网格对齐，见 word-documents 技能的 xlsx 生成参考）
   - ❌ 不要尝试 Markdown 表格（用户明确拒绝）
   - ❌ 不允许降级到无格式纯文本代替——表格就是表格，只换格式不丢结构
5. **兜底实施细节**：
   - 如果 python-docx 可安装 → pip install 后用 python-docx
   - 如果不可安装（PEP 668 限制或超时）→ 用纯 stdlib zipfile + OOXML 字符串构建
   - 同理对 .xlsx：openpyxl 不可用 → zipfile + OOXML 字符串构建
   - 文件放用户桌面：`/mnt/d/360MoveData/Users/Admin/Desktop/`
   - 报完文件路径即可，不浪费对话时间解释技术细节
6. **修复机制**（只在后台做，不在对话中耗时间）：
   - 如果确定是脚本bug→修复 box_maker.py 后 patch 本技能
   - 如果是用户终端兼容性→用 memory 记录终端特性

This skill governs how structured terminal output is formatted for the user. The user expects WorkBuddy style for all structured responses: emoji + bold titles, ASCII border cards, grid tables with both horizontal and vertical lines, and precise right-edge alignment.

## Style Conventions

Use these elements in structured output:

- **Emoji + bold title** for section headers: `✅ 标题`, `📋 内容`, `🎯 总结`
- **ASCII border cards** for grouping related info
- **Grid tables** for structured comparison/listing (must have both `├──┤` separators between rows AND `│` between columns)
- **Right-edge alignment** - all right `│` must be at the same column across ALL lines in a table
- **No hand-drawing** - always use scripts/box_maker.py via Python code execution

## Grid Tables (MANDATORY for structured data)

Do NOT use border cards as a substitute for tables. The user requires proper grid tables with:

- **At least 2 horizontal separator lines** (`├──┤`) between header/data/bottom
- **At least 2 vertical column dividers** (`│` between columns)
- **Right-edge alignment** - all right `│` must be at the same column
- **CJK/emoji-aware widths** via wcwidth

Use `make_grid_table(headers, rows)` from scripts/box_maker.py (see linked files).

### CRITICAL Cell Formula

```python
def cell(text, col_width):
    text_w = dw(text)
    pad = col_width - 1 - text_w     # -1 is CRITICAL: accounts for leading space
    return " " + text + " " * pad
```

Where `col_width = max(dw(column_contents)) + 2` (2 = 1 left padding + 1 right padding).

The `-1` is the most common bug. Without it, content rows are 1 column wider than border rows, breaking right-edge alignment.

### ⚠️ PITFALL: make_grid_table 不支持多行单元格

`make_grid_table()` 的每个单元格必须是**单行文本**。如果单元格内包含 `\n`（换行符），网格会在换行处断裂，`verify_box` 会报大量行宽不一致。

**正确做法：** 需要展示多行内容的条目，用 `make_box()` 分块输出，不要硬塞进 grid table。

```python
# ❌ 错误：make_grid_table 里塞 \n
t = make_grid_table(['时段', '内容'], [['工作时间', '第一行\n第二行']])  # 会断裂

# ✅ 正确：用 make_box 逐行输出
b = make_box('时段：工作时间', [
    '  第一行',
    '  第二行',
])
```

**正确分工：**
| 函数 | 适用场景 | 行数控制 |
|:---|:---|:---:|
| `make_grid_table()` | 纯 tabular 数据，每格一行 | 所有格无换行 |
| `make_box()` | 多行文本、方案说明、话术演示 | 每行一个 list item |

Do NOT re-implement `make_grid_table()` in `execute_code()` calls during conversation. The box_maker.py script already has the correct formula. Hand-written versions are prone to forgetting the `-1` leading-space offset.

**Correct approach:**
```python
exec(open('/home/dmin/.hermes/skills/creative/workbuddy-output/scripts/box_maker.py').read())
# Then call make_grid_table() directly
```

Or simply use `skill_view(name='workbuddy-output', file_path='scripts/box_maker.py')` to read it, then `exec()`.

The three most common inline bugs (all happened in production):
1. **Missing `-1`** in `pad = col_width - text_w` → content rows 1 col too wide
2. **Wrong wcwidth** with bare hex OR conditions (0x26CE or 0x26D4 is always True)
3. **Forgetting verification** — every table MUST run verify: all lines same dw

### ⚠️ PITFALL: Zero-width characters miscounted as wide (2026.5.11 bug, round 1)

U+FE0F (Variation Selector-16), U+200D (ZWJ), U+20E3 (Enclosing Keycap), and U+FEFF (BOM) are **zero-width** but were miscoded as width=2 in the wide range. This caused all emoji with VS16 (☁️, ❤️, etc.) and ZWJ sequences to be counted too wide, breaking right-edge alignment.

**Round 1 fix (2026.5.11):** Moved U+FE0F, U+200D, U+20E3 from wide range to zero-width range. Added U+FEFF. Extended range from U+FE00-U+FE0F (full VS range).

Despite this fix, tables with cloud emoji (☁️) still showed misaligned right border — see Round 2 below.

### ⚠️ PITFALL: Emoji presentation context — chars upgraded width 1→2 by U+FE0F (2026.5.11 bug, round 2)

**Problem:** After Round 1, `display_width("☁️")` returned `1 (U+2601) + 0 (U+FE0F) = 1`. Python said width=1, but **modern terminals render U+2601+U+FE0F as a full emoji taking 2 columns**. This caused the cell padding to be off by 1, shifting the right border left by one character.

The root cause: U+2601 (CLOUD) has **Ambiguous Width** in Unicode East Asian Width. Standalone `☁` renders as 1 column in text mode. But when followed by U+FE0F (emoji presentation selector), the terminal switches to emoji rendering and allocates 2 columns. Standard wcwidth can't know this because it evaluates codepoints independently without context.

**Same bug affects ANY emoji that:**
- Has a text-presentation codepoint with wcwidth=1 (often an Ambiguous Width char)
- Is followed by U+FE0F to request emoji presentation
- Examples: ☁ (U+2601), ☀ (U+2600), ☂ (U+2602), ☃ (U+2603), ❤ (U+2764), ⭐ (U+2B50)

**Round 2 fix (2026.5.11, this session):** `display_width()` now contextually detects emoji presentation:

```python
# Emoji presentation: a char followed by U+FE0F (VS16) renders as
# full-width emoji (2 cells) in modern terminals, even if wcwidth says 1.
if w == 1 and i + 1 < len(s) and ord(s[i+1]) == 0xFE0F:
    w = 2
    # Consume the FE0F and any following ZWJ sequences
    j = i + 2
    while j + 1 < len(s) and ord(s[j]) == 0x200D:
        j += 2  # ZWJ + next emoji base, ZWJ is zero-width
    total += w
    i = j
    continue
```

This handles:
- Simple emoji presentation: `☁️` → width 2 (not 1)
- ZWJ sequences: `👨‍👩‍👧‍👦` → correct compound width (not overcounted)

**Always verify with emoji-inclusive test cases after any wcwidth change:**
```python
tests = [
    ("\ufe0f", "VS-16", 0),         # zero-width
    ("☁️", "cloud emoji", 2),       # U+2601(1) upgraded by FE0F → 2
    ("☁", "cloud alone", 1),        # U+2601 alone (no FE0F) → 1
    ("✅", "checkmark", 2),         # U+2705 is explicitly in wide list
    ("❌", "cross", 2),             # U+274C is explicitly in wide list
    ("❤️", "heart emoji", 2),      # U+2764(1) upgraded by FE0F → 2
]
```

### Verification

After generating ANY box or table, verify all lines have equal display width:

```python
for i, line in enumerate(lines):
    assert dw(line) == expected, f"Line {i} width mismatch"
```

## Box Generation Method

Do NOT hand-type ASCII boxes - the visual width is unknowable without wcwidth calculation. Prefer scripts/box_maker.py.

**Lightweight alternative:** When box_maker.py isn't available, use the standalone `mt()` (make_table) function from `references/table-formatter-mt.md`. This is a simpler single-function version that handles basic grid tables — no imports needed, just copy-paste. See also `references/table-gallery.md` for quick visual table templates.

The script:
1. Defines a correct wcwidth() function
2. Provides `make_box(title, lines, width=72)` — single-column card
3. Provides `make_grid_table(headers, rows)` — multi-column grid table
4. Both return strings — embed directly in your response

After generating, verify every line has the same display width.

## CJK wcwidth Algorithm

Characters with display width 2 include:

- CJK Unified Ideographs (U+4E00-U+9FFF)
- CJK Radicals Supplement (U+2E80-U+2EFF)
- CJK Symbols and Punctuation (U+3000-U+303F)
- Fullwidth Forms (U+FF01-U+FF60, U+FFE0-U+FFE6)
- CJK Compatibility Ideographs (U+F900-U+FAFF)
- CJK Extension B-F (U+20000-U+2FFFF, U+30000-U+3FFFF)
- Hangul Jamo (U+1100-U+115F), Hangul Syllables (U+AC00-U+D7AF)
- Emoticons (U+1F600-U+1F64F), Misc Symbols (U+1F300-U+1F5FF)
- Transport Symbols (U+1F680-U+1F6FF)
- Enclosed Alphanumerics (U+1F100-U+1F9FF)
- Various emoji single codepoints (U+231A, U+23E9, U+25FD, U+2614, U+2705, U+274C, etc.)

Characters with display width 0:

- Control characters (U+0000-U+001F)
- DEL and C1 controls (U+007F-U+00A0)
- Combining diacritical marks (U+0300-U+036F, U+1AB0-U+1AFF, U+1DC0-U+1DFF, U+20D0-U+20FF)
- Zero Width Joiner (U+200D) — used in multi-emoji sequences (👨‍👩‍👧‍👦)
- Variation Selectors (U+FE00-U+FE0F) — VS-16 (U+FE0F) turns ☁ into ☁️ emoji, ZERO width
- Variation Selectors Supplement (U+FE20-U+FE2F)
- BOM / Zero Width No-Break Space (U+FEFF)

⚠️ **CRITICAL: display_width() NOW contextually upgrades characters followed by U+FE0F (2026.5.11 round 2 fix).** Standard wcwidth treats U+FE0F as zero-width but doesn't change the preceding character's width. However modern terminals render "emoji base + FE0F" as a 2-cell-wide emoji. display_width() detects this: if a char has wcwidth=1 and the next char is U+FE0F, it upgrades to width=2. It also skips any following ZWJ (U+200D) sequences. See the full pitfall section above.

Everything else has width 1 (ASCII, box-drawing like U+2500-U+257F, arrows like U+2192, etc.).

## CRITICAL PITFALL: Bare Hex Literals in Boolean Expressions

In Python boolean expressions like:

    0x26C4 <= cp <= 0x26C5 or 0x26CE or 0x26D4 or 0x26EA or ...

0x26CE and 0x26D4 are NOT comparisons - they are bare non-zero integers that evaluate to True unconditionally. This makes the ENTIRE OR-chain always True, causing EVERY character to report width=2.

**Fix:** Always write as `cp == 0x26CE or cp == 0x26D4`, or use a range `0x26CE <= cp <= 0x26D4` if codes are consecutive.

Always verify wcwidth before using:

    assert wcwidth(ord(' ')) == 1   # space = 1
    assert wcwidth(ord('a')) == 1   # ASCII = 1
    assert wcwidth(ord('中')) == 2  # CJK = 2
    assert wcwidth(0x2502) == 1     # box-drawing | = 1

## Output Order

When presenting multiple pieces of structured info:

1. Most critical card first (what the user asked for)
2. Supporting context second
3. Next steps / instructions last

Each card separated by one blank line.

## ⚠️ PITFALL: Know your audience — don't over-use box-drawing

Box-drawing characters (`┌┐└┘├┤│`) and `make_grid_table()` are designed for **CLI terminal display only**. They are **NOT** safe for:

| Destination | Problem | What to use instead |
|:---|:---|:---|
| 💬 企微/微信聊天 | 制表符显示为乱码/方框 | 纯文本分段 + 行内分隔线 `---` |
| 📄 文档文件 (.docx) | 不必要地复杂化格式 | Markdown 表格 → Word 原生表格 |
| 📱 手机端消息 | 对齐被字体/字号打乱 | 简短的纯文字列表 |

**Decision rule** before generating any box/table:

> 如果这份内容最终会出现在非终端环境（客户群、文档、手机端），用纯文字格式替代框框格式。

**2026.5.11 实战教训：** 在讨论企微外部群部署方案时，该用户连续调用了4次 `execute_code` 来生成 `┌┐└┘` 框框。用户直接指出：这些框框在 CLI 里看着漂亮，但内容讲的是企微客户群场景，框框既不能直接复制到企微用，又占用了大量对话空间。**正确答案是：单纯文字分段就能表达清楚的内容，不要画框。**

### ⚠️ PITFALL: Batch generation — don't scatter execute_code calls

When you need to present multiple boxes/tables in a single response, **generate ALL of them in ONE `execute_code` call**, not N separate calls. Each separate call:
- Clutters the conversation transcript with repetitive boilerplate (`import sys`, `insert path`, `verify_box`)
- Breaks the user's reading flow (they see your analysis, then a script, then output, then your next line, then another script...)
- Makes the conversation harder to follow in review

**Correct approach — single batch call:**
```python
# ONE execute_code call that outputs everything
grid = make_grid_table(...)
box1 = make_box('标题1', [...])
box2 = make_box('标题2', [...])
print(grid)
print()
print(box1)
print()
print(box2)
# verify at end
verify_box(grid)  # and each box
```

**Wrong approach (what happened in 2026.5.11):**
```python
# Call 1 — one table
# Call 2 — one box
# Call 3 — another box
# Call 4 — another box
# User: \"你先把你的上面的输出做好吧\" 😅
```

### ⚠️ PITFALL: "重新输出" = 整段重做，不要修修补补

**2026.5.11 实战教训：** 用户指出表格对齐问题后说「重新输出」—— 此时正确的做法是**整段全部清掉重来**，而不是在原有输出上修修补补。

**原因：**
- 用户看到的是一段破碎的对话（你的文字 → execute_code → 输出 → 你的文字 → 另一个 execute_code...）
- 修补式的修复让用户觉得你「记不住规矩，要一句一句教」
- 整段重做展示了「我懂了，一次性搞定」的态度

**正确流程（2026.5.11 验证可行）：**
1. 用户说「重新输出」→ 直接加载 `workbuddy-output` 技能
2. 在**一个** `execute_code` 调用里，把需要展示的全部内容（标题 + 多张表 + 多个框 + 收尾问句）生成完毕
3. 每个框/表分别调 `verify_box()` 确认对齐
4. 输出只有两段：execute_code 的 stdout + 你的收尾一句话
5. 不把"需要展示的内容"和"执行的代码"交替呈现给用户

When you need to present multiple boxes/tables in a single response, **generate ALL of them in ONE `execute_code` call**, not N separate calls. Each separate call:
- Clutters the conversation transcript with repetitive boilerplate (`import sys`, `insert path`, `verify_box`)
- Breaks the user's reading flow (they see your analysis, then a script, then output, then your next line, then another script...)
- Makes the conversation harder to follow in review

**Correct approach — single batch call:**
```python
# ONE execute_code call that outputs everything
grid = make_grid_table(...)
box1 = make_box('标题1', [...])
box2 = make_box('标题2', [...])
print(grid)
print()
print(box1)
print()
print(box2)
# verify at end
verify_box(grid)  # and each box
```

**Wrong approach (what happened in 2026.5.11):**
```python
# Call 1 — one table
# Call 2 — one box
# Call 3 — another box
# Call 4 — another box
# User: "你先把你的上面的输出做好吧" 😅
```
