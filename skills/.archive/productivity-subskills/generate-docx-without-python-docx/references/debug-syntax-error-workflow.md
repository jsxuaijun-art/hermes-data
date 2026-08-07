# Debug Syntax Errors in docx Generation Scripts

## Problem Pattern

When manually constructing large OOXML scripts with embedded Chinese text data, the following syntax errors are common:

1. **Tuple with `key=value`** (most common)
2. **Late import in function** (zipfile, xml.etree, etc.)
3. **Unicode escape vs raw string** confusion (`\u201c` vs actual characters)
4. **Missing quotes around f-string values**
5. **Duplicate imports** causing confusion

## Diagnostic Workflow

### Symptom: `ast.parse()` gives a misleading error

Example: `SyntaxError: 'return' outside function` at line X, but line X is fine.

**Root cause is usually NOT where the error points** — the parser got confused by a different syntax issue earlier in the file.

### Step 1: Binary-search isolation

```python
# test_range.py
with open('your_script.py', 'r') as f:
    lines = f.readlines()

# Check first half
try:
    compile(''.join(lines[:300]), '<test>', 'exec')
    print("Lines 1-300: OK")
except SyntaxError as e:
    print(f"Lines 1-300: {e}")

# Check second half
try:
    compile(''.join(lines[300:]), '<test>', 'exec')
    print("Lines 300-end: OK")
except SyntaxError as e:
    print(f"Lines 300-end: {e}")
```

Repeat narrowing until the offending section is ~20 lines.

### Step 2: Tokenize (catches things ast.parse might misreport)

```python
import tokenize, io, sys
with open('your_script.py', 'rb') as f:
    try:
        for tok in tokenize.tokenize(f.readline):
            pass
        print("Tokenization OK")
    except tokenize.TokenError as e:
        print(f"Token error: {e}")
        # Check line/col from the error
```

### Step 3: Check known patterns

**Pattern A: `("text", "font", size, bool, key=val)`**

```python
# Grep for lines that open a tuple and contain '='
grep -n '^\s*("' your_script.py | head -30
# Then check each for key=value in the tuple
```

**Pattern B: `import X` after `X.usage()`**

```python
# Extract all import statements and check ordering vs first usage
grep -n '^import\|^from' your_script.py
# Check if any zipfile.ZipFile, xml.etree.ElementTree etc. appear before their import
```

### Step 4: Isolate the data structure

If the script has inline data (like `script_sections`), extract it:

```python
# Create a minimal reproducer with just the suspect data
suspect_data = [
    ("title", [
        {"text": "ok", "font": "xxx", "bold": False, "before": 10},  # dict is fine
    ]),
    ("title2", [
        ("text", "xxx", "10", False, before=10),  # tuple with kw — INVALID
    ]),
]

# Actually it's better to just manually inspect the raw file around the data section
```

## Prevention

- **Always use dicts for structured data** that includes keyword-style properties
- **Keep imports at the top of the file or function** — never after first usage
- **Use raw strings `r"..."` or double-escape** for backslashes in f-strings
- **Run `python3 -c "import ast; ast.parse(open('f').read()); print('OK')"`** as the FIRST thing before running the script
- **Validate data structure independently** before integrating into the full script
