# CI Troubleshooting Quick Reference

Common CI failure patterns and how to diagnose them from the logs.

## Reading CI Logs

```bash
# With gh
gh run view <RUN_ID> --log-failed

# With curl — download and extract
curl -sL -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$GH_OWNER/$GH_REPO/actions/runs/<RUN_ID>/logs \
  -o /tmp/ci-logs.zip && unzip -o /tmp/ci-logs.zip -d /tmp/ci-logs
```

## Common Failure Patterns

### Test Failures
**Signature:** `FAILED tests/test_foo.py::test_bar - AssertionError`
**Fix:** Update assertion to match new expected behavior, fix logic, or add missing dependency.

### Lint / Formatting Failures
**Signature:** `src/auth.py:45:1: E302 expected 2 blank lines, got 1`
**Fix:** Run formatter: `black .`, `ruff check --fix .`, `isort .`

### Type Check Failures (mypy / pyright)
**Signature:** `src/api.py:23: error: Argument 1 to "process" has incompatible type "str"; expected "int"`
**Fix:** Add type cast, fix signature, or add `# type: ignore` as last resort.

### Build / Compilation Failures
**Signature:** `ModuleNotFoundError: No module named 'some_package'`
**Fix:** Add missing dependency to requirements.txt / package.json.

### Permission / Auth Failures
**Signature:** `Error: Resource not accessible by integration`
**Fix:** Add `permissions:` block to workflow YAML, verify secrets exist.

### Timeout Failures
**Signature:** `The operation was canceled.`
**Fix:** Add `timeout-minutes:` to step, fix infinite loop or slow network call.

### Docker / Container Failures
**Signature:** `COPY failed: file not found in build context`
**Fix:** Fix path in Dockerfile COPY/ADD, add missing files.

## Auto-Fix Decision Tree

```
CI Failed
├── Test failure → update test or fix logic
├── Lint failure → run formatter, fix style
├── Type error → fix types
├── Build failure → add dependency or update pins
├── Permission error → update workflow permissions (needs user)
└── Timeout → investigate performance (may need user input)
```

## Re-running After Fix

```bash
git add <fixed_files> && git commit -m "fix: resolve CI failure" && git push
gh pr checks --watch
```
