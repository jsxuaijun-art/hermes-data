# Testing Superpowers Skills

This reference preserves upstream testing guidance and adapts it for this
`superpowers-*` skill pack.

## Overview

Workflow skills involving subagents, hooks, bootstrap injection, or long-lived
servers need integration tests, not just static file checks. Upstream tests run
real Claude Code or OpenCode sessions and inspect transcripts or logs.

This adaptation includes a lightweight static validator:

```bash
python3 skills/superpowers/scripts/validate.py skills/superpowers
```

Run it after every edit. It checks prefixed skill names, plugin metadata,
OpenCode bootstrap paths, Claude hook references, marketplace metadata, and
required operational references.

## Claude Code Integration Test Model

Upstream integration tests run Claude Code in headless mode from the Superpowers
plugin directory and verify behavior through `.jsonl` transcripts.

Requirements:

- Claude Code CLI installed as `claude`.
- Run from the Superpowers plugin directory, not an arbitrary temp directory.
- Local development marketplace or plugin enabled.
- Use permission flags and `--add-dir` for temp test projects.

Typical shape:

```bash
cd /path/to/superpowers
timeout 1800 claude -p "$PROMPT" \
  --allowed-tools=all \
  --add-dir "$TEST_PROJECT" \
  --permission-mode bypassPermissions
```

Transcript checks should parse Claude session `.jsonl` files rather than only
grepping user-facing output.

## What To Verify

For subagent-driven workflows:

1. The intended skill was invoked.
2. Subagents were dispatched.
3. Task tracking was used.
4. Implementers received full task context.
5. Spec compliance review ran before code quality review.
6. Reviewers independently inspected code instead of trusting implementer summaries.
7. Tests or targeted verification passed.

For hook/bootstrap behavior:

1. Session-start hook emits valid JSON.
2. Bootstrap content contains `superpowers-using-superpowers`.
3. OpenCode transform injects bootstrap only once.
4. Plugin registers the skills directory.

For this adaptation:

1. All upstream skill directories exist with `superpowers-` prefix.
2. All `SKILL.md` frontmatter names match directory names.
3. `.ko.md` translations exist for the top-level pack and each bundled skill.
4. Unsupported upstream harness references are either intentionally omitted or
   clearly marked as out of scope.

## Token Analysis

Upstream includes a Claude transcript token analyzer. The key operational lesson
is to measure coordinator and subagent token usage separately:

- main session has full context and higher cache reads
- each subagent should receive bounded task-local context
- similar task complexity should produce similar subagent costs

High cache reads are expected and usually good. Unexpectedly high subagent input
often means prompts include too much global context.

## Troubleshooting

### Skills Not Loading

1. Confirm the command runs from the plugin directory.
2. Confirm the harness has the plugin enabled.
3. Confirm skill files exist under `skills/`.
4. For this adaptation, use prefixed names like `superpowers-writing-plans`.

### Permission Errors

1. Grant access to temp test directories.
2. Use the harness permission bypass mode only for controlled test runs.
3. Check filesystem permissions.

### Test Timeouts

1. Increase timeout for real subagent workflows.
2. Inspect transcripts for loops.
3. Reduce task complexity if testing only skill triggering or sequencing.

### Session File Not Found

1. Check the harness transcript directory.
2. Search for recent `.jsonl` files.
3. Confirm the test actually started the harness.

## Writing New Integration Tests

Use temp projects and clean them up with traps. Test behavior through transcripts
or structured logs. Keep test prompts focused on one skill guarantee at a time.
