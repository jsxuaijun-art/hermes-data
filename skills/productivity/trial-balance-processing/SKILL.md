---
name: trial-balance-processing
description: "Merge duplicate 科目名称 in a 科目余额表 Excel and net 借/贷."
version: 1.0.0
author: Hermes Agent
tags: [accounting, chinese, trial-balance, 科目余额表, excel, openpyxl]
---

# Trial Balance (科目余额表) Processing

Clean up and consolidate a Chinese 科目余额表 / account-balance Excel: merge rows that share the same 科目名称, cancel 借方 against 贷方, and place the net balance in whichever column is positive. This is a recurring task for 财税 clients.

## Trigger

When the user asks to:
- 合并相同的科目名称、借贷相互抵消、余额放在正数那栏
- Summarize a 科目余额表 / 余额表 by account name
- Reconcile 借/贷 balances or dedupe repeated customer/supplier names across sub-ledgers

## Procedure

1. **Locate the source file.** Desktop files live at `/mnt/c/Users/<user>/Desktop/`. Use `ls` on the Desktop, not a recursive `find` over the whole drive (full-tree scans time out). Copy the exact filename.

2. **Inspect the sheet layout first.** Run the xlsx skill's reader to see headers, merged cells, and where data starts:
   ```bash
   cd /root/.hermes/skills/productivity/xlsx/scripts && \
   python3 xlsx_read.py '<file>' --sheets
   python3 xlsx_read.py '<file>' --json --sheet Sheet1
   ```
   A 科目余额表 typically has title rows (1-2), a unit/currency row, a header block with merged cells, then data rows, then a `=SUM(...)`/合计 row at the end. Identify the exact data row range and skip the total row when grouping.

3. **Group by exact 科目名称 and net 借/贷.** Load with `data_only=True`, iterate the data rows, and aggregate into an OrderedDict keyed by the name (column 2). Sum 借方 (col 3) and 贷方 (col 4) for every row sharing that name. Net = 借 − 贷:
   - net > 0 → write net into 借方, leave 贷方 blank
   - net < 0 → write −net into 贷方, leave 借方 blank
   - net == 0 → both blank
   Keep the first occurrence's 科目编码 for the merged row. Treat empty/Non-numeric cells as 0.

4. **Rebuild the workbook in place (to a NEW file, never overwrite the source).** `load_workbook(path)` a second time WITHOUT `data_only` to keep styling, clear the old data rows, write the merged rows contiguously from the data start, then append a total row with `=SUM(C<start>:C<end>)` and `=SUM(D<start>:D<end>)`. Save as `<原名>_合并后.xlsx` on the Desktop.

5. **Verify the merge is arithmetic-sound before reporting done.** Netting is INVARIANT to the 借/贷 total difference, so recompute `sum(借) − sum(贷)` on the OUTPUT and on the SOURCE and confirm they are equal. A nonzero difference that matches the source is pre-existing data (usually a missing equity account like 实收资本), NOT a merge error — report it as such and offer to find the cause, don't silently ignore or invent a fix. Also confirm each previously-duplicated name now appears exactly once, and that rows are contiguous (trailing blanks after the 合计 row are fine).

## Pitfalls

- **Do NOT run multi-line Python via heredoc (`python3 - <<'EOF'`) in this WSL terminal — it hangs and times out.** Write the logic to a script file with `write_file`, then run `python3 myscript.py`. The xlsx CLI scripts and script-file invocations work reliably; heredoc does not. When a command times out mid-read, redo it as a script file rather than retrying the heredoc.
- **`load_workbook(data_only=True)` discards formulas on save** — load twice: `data_only=True` for reading values, plain `load_workbook` for editing/preserving styling. Never save a `data_only` workbook.
- **Don't `find` the whole Windows drive** to locate a Desktop file — it hits TCC/timeouts. `ls` the Desktop directly.
- **Account names recur across DIFFERENT parent accounts** (a customer as 应收 in one code range and 应付 in another). Grouping by exact name nets these into one line per counterparty; that is the literal request. If the user instead wants per-account-category subtotals, confirm scope first — state which names collapsed across code ranges.
- A nonzero 借/贷 difference or missing 实收资本-type equity account in the source is common; it is not introduced by grouping. Verify against the source before describing the output as balanced.

## Cross-references

- Statement *format conversion* between standards (小企业会计准则 ↔ 民间非营利组织) is handled by `chinese-accounting-format-conversion` — its `scripts/convert_minsheng_balance_sheet.py` shows openpyxl styling and number-format conventions (`#,##0.00`, negative-in-parentheses) that apply here too.
- General `.xlsx` I/O, styling, and recalculation: the `xlsx` skill.
