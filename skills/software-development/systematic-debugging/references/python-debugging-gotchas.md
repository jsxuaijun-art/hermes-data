# Python Debugging Gotchas

Real-world Python bugs that produce **misleading** error messages, making root cause identification harder than it should be.

---

## 1. Tuple with Keyword Arguments → `SyntaxError: 'return' outside function`

### The Bug

```python
# INVALID — tuples can only contain expressions, not keyword assignments
my_data = [
    ("header text", "微软雅黑", "20", False, before=40, after=20, line=360),
]
```

### The Misleading Error

Python reports a **different** syntax error, often at or near the **end** of the enclosing function/block:

```
SyntaxError: 'return' outside function
```

Or, depending on context:

```
SyntaxError: invalid syntax
```

The reported line number rarely points to the actual tuple. It may point to:
- A `return` statement many lines after the bad tuple
- The closing `]` of a list
- The end of a function definition

### Root Cause

- **Tuple literals** do not accept `key=value` syntax. `("a", "b", x=1)` is invalid Python.
- **Function calls** do accept `key=value` syntax. `func("a", "b", x=1)` is valid.
- **Dict literals** use `{"key": value}`, not `key=value`.
- Python's parser encounters the `key=value` in the tuple, fails, and the error propagates to a confusing location.

### Diagnosis

When you see `SyntaxError: 'return' outside function` and the reported line looks fine:

1. **Search backward** for any tuple that might contain `key=value` syntax
2. Look for patterns like `(expr, expr, key=value)` — these are **always invalid** in tuples
3. Use tokenizer to check: `python3 -c "import tokenize, sys; tokenize.tokenize(open(sys.argv[1], 'rb').readline)"` — tokenizer won't crash, so won't find the issue directly. Use `ast.parse()` which will report the SyntaxError.

### Fix

Convert the tuple to a **dict**:

```python
# VALID
my_data = [
    {"text": "header text", "font": "微软雅黑", "sz": "20", "bold": False, "before": 40, "after": 20, "line": 360},
]
```

If consuming via unpacking, change `*run` to `**run`:

```python
# Before (tuple unpacking)
for run in runs:
    para(*run)

# After (dict unpacking)
for run in runs:
    para(**run)
```

### Bulk Fix Workflow (30+ tuples)

When a generated file has **many** tuples that all need conversion, don't regex-transform broken syntax — that's unreliable. Instead:

**Step 1 — Extract data into a clean Python structure.**

Open the file, read the bad data section, and manually transcribe the values into proper dicts. This is faster than debugging regex failures.

**Step 2 — Generate the replacement section programmatically.**

Write a small Python script that emits the dict-literals with proper formatting:

```python
tab = "    "
for title, runs in sections:
    lines.append(f'{tab * 2}("{title}", [\n')
    for run in runs:
        kv = [f'"{k}": "{v}"' if isinstance(v, str) else f'"{k}": {v}' for k, v in run.items()]
        inner = ",\n" + tab * 4
        lines.append(f'{tab * 3}{{\n{tab * 4}{inner.join(kv)}\n{tab * 4}}},\n')
    lines.append(f'{tab * 2}]),\n')
```

**Common formatting mistake:** Don't put a comma right after `{` — `{,\n` is invalid Python. The dict entries should start immediately after `{`.

**Step 3 — Replace the section + patch the consumer.**

```python
# Read file, find section boundaries, splice new content
content = open("file.py").read()
new_content = content[:start] + generated_section + content[end:]
open("file.py", "w").write(new_content)
```

**Step 4 — Compile-test loop.**

```bash
python3 -c "import ast; ast.parse(open('file.py').read()); print('OK')"
python3 file.py
```

**Why this works:** You're replacing broken Python with guaranteed-valid Python dicts, not trying to transform syntax that Python can't even parse. The generation script itself is simple and easy to verify.

---

## 2. `import` After First Use → `UnboundLocalError`

### The Bug

```python
def build_document():
    # ... lots of code ...
    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as zf:  # Uses zipfile here
        ...
    import zipfile  # Imported here — TOO LATE
```

### The Error

```
UnboundLocalError: cannot access local variable 'zipfile' where it is not associated with a value
```

### Why It Happens

Python determines variable scope at **compile time**. When Python sees `import zipfile` anywhere in the function body, it treats `zipfile` as a **local variable** for the entire function. But at line execution time, the import hasn't executed yet when it's first referenced.

This happens most commonly when:
- Code was written incrementally (imports added later for verification)
- Refactoring moved imports inside a function without reordering
- Verification imports were added after the main logic

### Fix

**Move all imports to the top of the function** (or module level):

```python
def build_document():
    import zipfile
    import xml.etree.ElementTree as ET
    # ... rest of code, all zipfile/ET references below here ...
    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as zf:
        ...
    with zipfile.ZipFile(OUTPUT, "r") as zf:
        ...
```

### Prevention

- Put `import` statements at the **top** of the function, not at the bottom or in the middle
- When adding a verification block at the end of a function, check if it needs imports that don't exist yet at the top
- Search for "import" in the last 1/3 of a function if you see `UnboundLocalError` with a module name

---

## 3. Conflicting `ast.parse` Results — Sandbox Divergence

### Phenomenon

```
terminal("python3 -c 'import ast; ast.parse(open(\"file.py\").read()); print(\"OK\")'")  → ERROR
# But an identical script saved to /tmp/check.py and run via terminal → OK
```

### Cause

This can happen when:
1. The inline command has shell escaping issues (nested quotes, unescaped characters)
2. The file has been modified between the two invocations
3. The file contains very long lines that get truncated by the terminal tool

### Diagnosis

Always verify with a **separate script file** when inline parsing gives different results:
- Write a small script that reads and checks the file
- Run it via `python3 /tmp/check.py` (not inline `-c`)

---

## 4. Pyright/Pylance Reports Fine But `ast.parse` Fails

### Phenomenon

IDE shows no errors but `python3 -c "import ast; ast.parse(...)"` fails.

### Cause

Python syntax checkers in IDEs often run in a **less strict** mode, or handle encoding/decoding differently:
- The file may contain null bytes invisible to the editor
- The file may have mixed line endings causing parsing confusion
- The file may have been partially written (truncated on disk)

### Fix

1. Check file size: `wc -c file.py`
2. Check for null bytes: `python3 -c "print('null' if '\\x00' in open('file.py','rb').read() else 'clean')"`
3. Check file encoding: `file file.py`
4. Re-run `ast.parse()` with explicit encoding: `ast.parse(open('file.py', 'r', encoding='utf-8').read())`
