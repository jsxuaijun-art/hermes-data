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

### Verification

After generating ANY box or table, verify all lines have equal display width:

```python
for i, line in enumerate(lines):
    assert dw(line) == expected, f"Line {i} width mismatch"
```

## Box Generation Method

Do NOT hand-type ASCII boxes - the visual width is unknowable without wcwidth calculation. Use scripts/box_maker.py.

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
- Various emoji single codepoints (U+231A, U+23E9, U+25FD, U+2614, etc.)
- Variation Selectors (U+FE00-U+FE0F), ZWJ (U+200D), Enclosing Keycap (U+20E3)

Characters with display width 0:

- Control characters (U+0000-U+001F)
- DEL and C1 controls (U+007F-U+00A0)
- Combining diacritical marks (U+0300-U+036F, U+1AB0-U+1AFF, U+1DC0-U+1DFF, U+20D0-U+20FF, U+FE20-U+FE2F)

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
