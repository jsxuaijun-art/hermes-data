# Review Output Template

Use this as the structure for PR review summary comments.

## For PR Summary Comment

```markdown
## Code Review Summary

**Verdict: [Approved ✅ | Changes Requested 🔴 | Reviewed 💬]** ([N] issues, [N] suggestions)

**PR:** #[number] — [title]
**Author:** @[username]
**Files changed:** [N] (+[additions] -[deletions])

### 🔴 Critical
<!-- Issues that MUST be fixed before merge -->
- **file.py:line** — [description]. Suggestion: [fix].

### ⚠️ Warnings
<!-- Issues that SHOULD be fixed -->
- **file.py:line** — [description].

### 💡 Suggestions
<!-- Non-blocking improvements -->
- **file.py:line** — [description].

### ✅ Looks Good
- [aspect that was done well]

---
*Reviewed by Hermes Agent*
```

## Severity Guide

| Level | Icon | Blocks merge? |
|-------|------|---------------|
| Critical | 🔴 | Yes |
| Warning | ⚠️ | Usually yes |
| Suggestion | 💡 | No |
| Looks Good | ✅ | N/A |

## Verdict Decision
- **Approved ✅** — Zero critical/warning items.
- **Changes Requested 🔴** — Any critical or warning item exists.
- **Reviewed 💬** — Observations only (draft PRs, informational).

## For Inline Comments

Prefix inline comments with severity icon:
```
🔴 **Critical:** User input passed directly to SQL query — use parameterized queries.
⚠️ **Warning:** This error is silently swallowed. At minimum, log it.
💡 **Suggestion:** This could be simplified with a dict comprehension.
```
