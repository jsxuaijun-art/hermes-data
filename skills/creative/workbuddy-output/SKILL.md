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

## 🚨 强制加载规则 + 循环刹车（2026.5.10-12 江姐定）

### 规则A：必须尝试表格 + 主动预加载（2026.5.13 经验修正）

**本技能必须在每次输出含结构化数据/对比/列表时加载。** 这是硬性要求。但光有规则不够——实战中暴露的常见失败模式是：先输出了Markdown表格，被用户指出后才补加载。必须做到 **在输出任何结构化内容前主动预加载**，而不是用户指出后纠正。

- 哪怕只有两行对比数据，也走 box_maker.py
- 不要有"数据少就先手写一个"的念头——手写Markdown表格被用户看到就是一次信任扣分
- 如果同时有文本+表格要输出，先加载技能生成表格，再组合成完整回复
- 建议在每次准备输出前先反问自己：这段内容能不能做成表格？能，就加载本技能

步骤如下：

1. 先用 `skill_view('workbuddy-output', file_path='scripts/box_maker.py')` 读取脚本
2. 用 `exec(open(script_path).read())` 载入 `make_grid_table()` 函数
3. 用该函数生成表格，禁止手写、禁止 Markdown `|---|` 替代
4. 生成后调用 `verify_box()` 验证所有行 dw 一致

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

### ⚠️ PITFALL: Never hand-write table code inline

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
