#!/usr/bin/env python3
"""
WorkBuddy-style ASCII box and grid table generator with CJK-aware wcwidth.

Usage:
    from box_maker import make_box, make_grid_table, display_width, verify_box

    # Single-column card
    box = make_box('📋 Title', ['line 1', 'line 2'])
    print(box)
    verify_box(box)

    # Multi-column grid table (requires both ├──┤ and │)
    t = make_grid_table(
        ['文件', '状态', '内容'],
        [
            ['SOUL.md', '✅', '中文版（3290B）'],
        ]
    )
    print(t)
"""

def wcwidth(cp: int) -> int:
    """Return terminal display width of a Unicode codepoint."""
    # CJK and wide ranges
    if (0x1100 <= cp <= 0x115F or 0x2E80 <= cp <= 0x9FFF or
        0xA000 <= cp <= 0xA4CF or 0xAC00 <= cp <= 0xD7AF or
        0xF900 <= cp <= 0xFAFF or 0xFE30 <= cp <= 0xFE6F or
        0xFF01 <= cp <= 0xFF60 or 0xFFE0 <= cp <= 0xFFE6 or
        0x1B000 <= cp <= 0x1B0FF or 0x1B100 <= cp <= 0x1B12F or
        0x1F000 <= cp <= 0x1F9FF or 0x20000 <= cp <= 0x2FFFF or
        0x30000 <= cp <= 0x3FFFF or 0x1F600 <= cp <= 0x1F64F or
        0x1F300 <= cp <= 0x1F5FF or 0x1F680 <= cp <= 0x1F6FF or
        0x1FA00 <= cp <= 0x1FA6F or 0x1FA70 <= cp <= 0x1FAFF or
        0x231A <= cp <= 0x231B or 0x23E9 <= cp <= 0x23F3 or
        0x23F8 <= cp <= 0x23FA or 0x25FD <= cp <= 0x25FE or
        0x2614 <= cp <= 0x2615 or 0x2648 <= cp <= 0x2653 or
        0x26AA <= cp <= 0x26AB or 0x26BD <= cp <= 0x26BE or
        0x26C4 <= cp <= 0x26C5 or cp == 0x26CE or cp == 0x26D4 or
        cp == 0x26EA or 0x26F2 <= cp <= 0x26F3 or cp == 0x26F5 or
        cp == 0x26FA or cp == 0x26FD or cp == 0x2702 or cp == 0x2705 or
        0x2708 <= cp <= 0x270D or cp == 0x270F or cp == 0x2712 or
        cp == 0x2714 or cp == 0x2716 or cp == 0x271D or cp == 0x2721 or
        cp == 0x2728 or 0x2733 <= cp <= 0x2734 or cp == 0x2744 or
        cp == 0x2747 or cp == 0x274C or cp == 0x274E or
        0x2753 <= cp <= 0x2755 or cp == 0x2757 or
        0x2763 <= cp <= 0x2764 or 0x2795 <= cp <= 0x2797 or
        cp == 0x27A1 or cp == 0x27B0 or cp == 0x27BF or
        0x2934 <= cp <= 0x2935 or 0x2B05 <= cp <= 0x2B07 or
        cp == 0x2B1B or cp == 0x2B1C or cp == 0x2B50 or cp == 0x2B55 or
        cp == 0x3030 or cp == 0x303D or cp == 0x3297 or cp == 0x3299 or
        cp == 0xFE0F or cp == 0x200D or cp == 0x20E3):
        return 2
    # Zero-width characters
    if cp < 32 or (0x7F <= cp <= 0xA0):
        return 0
    if 0x0300 <= cp <= 0x036F or 0x1AB0 <= cp <= 0x1AFF or \
       0x1DC0 <= cp <= 0x1DFF or 0x20D0 <= cp <= 0x20FF or \
       0xFE20 <= cp <= 0xFE2F:
        return 0
    return 1


def display_width(s: str) -> int:
    """Total terminal display width of a string."""
    return sum(wcwidth(ord(ch)) for ch in s)


def make_box(title: str = None, lines: list = None, width: int = 72) -> str:
    """
    Create a perfectly-aligned ASCII box.

    Args:
        title: Optional title string (with emoji, CJK, etc.)
        lines: List of strings, one per row. Use '' for empty row, '---' for separator.
        width: Content area width in terminal columns (default 72).

    Returns:
        Box as a string with Unix line endings.
    """
    if lines is None:
        lines = []

    rows = []
    # Top
    rows.append('\u250c' + '\u2500' * width + '\u2510')

    # Title + separator
    if title:
        t = '  ' + title
        sp = max(0, width - display_width(t))
        rows.append('\u2502' + t + ' ' * sp + '\u2502')
        rows.append('\u251c' + '\u2500' * width + '\u2524')

    # Content lines
    for ln in lines:
        if ln == '---':
            rows.append('\u251c' + '\u2500' * width + '\u2524')
        elif ln == '':
            rows.append('\u2502' + ' ' * width + '\u2502')
        else:
            sp = max(0, width - display_width(ln))
            rows.append('\u2502' + ln + ' ' * sp + '\u2502')

    # Bottom
    rows.append('\u2514' + '\u2500' * width + '\u2518')

    return '\n'.join(rows)


def verify_box(box_string: str) -> bool:
    """Verify all lines in the box have equal display width. Returns True if OK."""
    lines = box_string.split('\n')
    if not lines:
        return True
    expected = display_width(lines[0])
    ok = True
    for i, line in enumerate(lines):
        w = display_width(line)
        if w != expected:
            print(f'Line {i}: dw={w} (expected {expected}) | {line!r}')
            ok = False
    if ok:
        print(f'All {len(lines)} lines OK (dw={expected})')
    return ok


def make_grid_table(headers: list, rows: list) -> str:
    """
    Create a properly-aligned multi-column grid table with ├──┤ separators
    and │ column dividers. Uses wcwidth for CJK/emoji alignment.

    Args:
        headers: List of header strings.
        rows: List of lists, each inner list is one row of cells.

    Returns:
        Grid table as a string with Unix line endings.
    """
    ncols = len(headers)

    # Calculate column widths: max display width of content + 2 for padding
    cw = []
    for ci in range(ncols):
        max_w = display_width(headers[ci])
        for row in rows:
            w = display_width(row[ci])
            if w > max_w:
                max_w = w
        cw.append(max_w + 2)  # +2 = 1 left pad + 1 right pad

    # Build border lines
    sep = "├" + "┼".join("─" * w for w in cw) + "┤"
    top = "┌" + "┬".join("─" * w for w in cw) + "┐"
    bot = "└" + "┴".join("─" * w for w in cw) + "┘"

    # Header-data separator (double line for visual distinction)
    head_sep = "╞" + "╪".join("═" * w for w in cw) + "╡"

    def cell(text, col_width):
        """Cell content that exactly fills col_width display columns."""
        text_w = display_width(text)
        pad = col_width - 1 - text_w  # -1 for the mandatory leading space
        return " " + text + " " * pad

    def fmt_row(cells):
        return "│" + "│".join(cell(cells[i], cw[i]) for i in range(ncols)) + "│"

    lines = [top, fmt_row(headers), head_sep]
    for ri, row in enumerate(rows):
        lines.append(fmt_row(row))
        if ri < len(rows) - 1:
            lines.append(sep)
    lines.append(bot)
    return "\n".join(lines)


def self_test():
    """Verify wcwidth correctness with known cases."""
    tests = [
        (' ', 1),
        ('a', 1),
        ('中', 2),
        ('\u2502', 1),  # box-drawing |
        ('\u2500', 1),  # box-drawing -
        ('\u2192', 1),  # arrow →
        ('\uFF08', 2),  # fullwidth （
        ('\uFF0C', 2),  # fullwidth ，
        ('📋', 2),      # emoji clipboard
        ('✅', 2),      # emoji checkmark
    ]
    for char, expected in tests:
        actual = wcwidth(ord(char))
        status = 'OK' if actual == expected else 'FAIL'
        print(f'  [{status}] U+{ord(char):04X} {char!r}: expected {expected}, got {actual}')


if __name__ == '__main__':
    import sys
    if '--test' in sys.argv:
        print('wcwidth self-test:')
        self_test()
        print()

    # Demo box
    sample = [
        '  1. 范话题类',
        '     short-video-general  →  纯追爆款，跟财税无关的话题',
        '',
        '  2. 行业自然流',
        '     short-video-industry-flow  →  讲故事中自然带出财税业务',
    ]
    box = make_box('📋 四大技能总表', sample)
    print(box)
    print()
    verify_box(box)

    # Demo grid table
    print()
    print('Grid table demo:')
    grid = make_grid_table(
        ['文件', '状态', '内容'],
        [
            ['SOUL.md',     '✅', '中文财税版（3290B）'],
            ['SOUL_Pro.md', '✅', '中文财税版（3290B）'],
            ['SOUL_Edu.md', '✅', '中文教育版（3293B）'],
        ]
    )
    print(grid)
    print()
    print(f'Grid lines check: ', end='')
    glines = grid.split('\\n')
    gexp = display_width(glines[0])
    gok = all(display_width(l) == gexp for l in glines)
    print('OK' if gok else 'FAIL')
