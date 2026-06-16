# Curator Internals Reference

## State File

Path: `~/.hermes/skills/.curator_state`

```json
{
  "last_report_path": "/home/dmin/.hermes/logs/curator/20260503-062255",
  "last_run_at": "2026-05-03T06:22:55.292218+00:00",
  "last_run_duration_seconds": 0.15196,
  "last_run_summary": "auto: no changes; llm: skipped (no candidates)",
  "paused": false,
  "run_count": 1
}
```

Key fields:
- `last_run_summary`: `auto: no changes` → all skills healthy, nothing to archive; `llm: skipped (no candidates)` → no skills triggered LLM review
- `paused`: set to `true` to temporarily disable curator without changing config
- `run_count`: total runs since installation

## Report File

Reports are empty text files (touch files) at `~/.hermes/logs/curator/<YYYYMMDD-HHmmss>/`. They act as run markers. Actual details are in the state JSON.

## Config Under `auxiliary`

The curator uses an auxiliary model for LLM-driven analysis:

```yaml
auxiliary:
  curator:
    provider: auto        # defaults to main provider fallback
    model: ''             # empty = auto-select
    timeout: 600          # 10 minute timeout for LLM analysis
```

## Common Patterns

### "auto: no changes" → healthy
All skills are actively used or recently enough that none hit the stale/archive thresholds.

### "llm: skipped (no candidates)"
No skills qualify for LLM-driven improvement analysis. Curator only engages the LLM when it detects skills that could benefit from restructuring, not on every run.

### First run behavior
After fresh install, curator reports are empty until the first full cycle completes.

## Discovery Process (how to inspect)

```bash
# 1. Check state
cat ~/.hermes/skills/.curator_state

# 2. List report markers
ls ~/.hermes/logs/curator/

# 3. Check config
grep -A 5 'curator:' ~/.hermes/config.yaml | head -10

# 4. Check auxiliary model config
grep -A 5 'curator:' ~/.hermes/config.yaml | tail -10

# 5. View pinned skills (skills protected from curator)
ls -la ~/.hermes/skills/ | grep -E '\.pinned|->'
# Pinned skills have a .pinned_state marker or are flagged via hermes skills config
```
