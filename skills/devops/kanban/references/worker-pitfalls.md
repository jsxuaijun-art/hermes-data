# Worker Pitfalls & Examples — Full Reference

> Previously the standalone `kanban-worker` skill. Absorbed into the `kanban` umbrella.

The **lifecycle** (6 steps: orient, work, heartbeat, block/complete) is auto-injected into every worker's system prompt via `KANBAN_GUIDANCE`. This reference is the deeper detail: good handoff shapes, retry diagnostics, edge cases.

## Workspace handling

Your workspace kind tells you how to behave inside `$HERMES_KANBAN_WORKSPACE`:

| Kind | Description |
|---|---|
| `scratch` | Fresh tmp dir, yours alone. Read/write freely; GC'd when task is archived. |
| `dir:<path>` | Shared persistent directory. Other runs will read what you write. Path is guaranteed absolute. |
| `worktree` | Git worktree at the resolved path. If .git doesn't exist, run `git worktree add <path> <branch>` first. |

## Tenant isolation

If `$HERMES_TENANT` is set, the task belongs to a tenant namespace. Prefix memory entries with the tenant:

- Good: `business-a: Acme is our biggest customer`
- Bad (leaks): `Acme is our biggest customer`

## Good summary + metadata shapes

**Coding task:**
```python
kanban_complete(
    summary="shipped rate limiter -- token bucket, keys on user_id with IP fallback, 14 tests pass",
    metadata={
        "changed_files": ["rate_limiter.py", "tests/test_rate_limiter.py"],
        "tests_passed": 14,
        "decisions": ["user_id primary, IP fallback"],
    },
)
```

**Review-required coding task:**
```python
kanban_comment(
    body="review-required handoff:\n" + json.dumps({
        "changed_files": ["rate_limiter.py"],
        "tests_passed": 14,
        "diff_path": "/path/to/worktree",
    }, indent=2),
)
kanban_block(reason="review-required: rate limiter shipped, 14/14 tests pass -- needs eyes on user_id/IP fallback choice")
```

Use `kanban_complete` for terminal work (one-line fix, docs change, research task where the writeup IS the artifact). For code changes, use `kanban_block` with `review-required`.

**Research task:**
```python
kanban_complete(
    summary="3 libraries reviewed; vLLM wins on throughput, SGLang on latency, TRT-LLM on memory",
    metadata={"sources_read": 12, "recommendation": "vLLM", "benchmarks": {"vllm": 1.0, "sglang": 0.87}},
)
```

**Review task:**
```python
kanban_complete(
    summary="reviewed PR #123; 2 blocking issues (SQL injection, missing CSRF)",
    metadata={"pr_number": 123, "findings": [
        {"severity": "critical", "file": "api/search.py", "issue": "raw SQL concat"},
        {"severity": "high", "file": "api/settings.py", "issue": "missing CSRF middleware"},
    ], "approved": False},
)
```

Shape `metadata` so downstream parsers can use it without re-reading your prose.

## Claiming cards you actually created

If your run produced new kanban tasks (via `kanban_create`), pass the ids in `created_cards` on `kanban_complete`. The kernel verifies each id exists and was created by your profile; phantom ids block the completion.

```python
# GOOD
c1 = kanban_create(title="fix SQL injection", assignee="security-worker")
kanban_complete(summary="remediation cards created", created_cards=[c1["task_id"]])

# BAD -- claiming ids you didn't capture from kanban_create returns
kanban_complete(summary="Created cards t_abc123", created_cards=["t_abc123"])  # gate rejects
```

If `kanban_create` fails (exception, tool_error), the card was NOT created. Retry or omit the id.

## Block reasons that get answered fast

Bad: "stuck" (no context).
Good: one sentence naming the decision you need. Leave full context as a comment.

```python
kanban_comment(task_id=os.environ["HERMES_KANBAN_TASK"], body="Long context...")
kanban_block(reason="Rate limit key choice: IP (simple, NAT-unsafe) or user_id (requires auth)?")
```

The block message is what appears in the dashboard/gateway. The comment is deeper context.

## Heartbeats worth sending

Good: "epoch 12/50, loss 0.31", "scanned 1.2M/2.4M rows", "uploaded 47/120 videos".
Bad: "still working", sub-second intervals. Skip for tasks under ~2 minutes.

## Retry scenarios

If `kanban_show` returns `runs: [...]` with one or more closed runs, you're a retry:

- `outcome: "timed_out"` — previous attempt hit max_runtime_seconds. Chunk or shorten the work.
- `outcome: "crashed"` — OOM or segfault. Reduce memory footprint.
- `outcome: "spawn_failed"` + error — usually profile config issue. Ask human via `kanban_block`.
- `outcome: "reclaimed"` — operator archived the task; you probably shouldn't be running.
- `outcome: "blocked"` — previous attempt blocked; unblock comment should be in the thread.

## Do NOT

- Call `delegate_task` as a substitute for `kanban_create`. delegate_task is for short reasoning subtasks inside YOUR run; kanban_create is for cross-agent handoffs.
- Modify files outside `$HERMES_KANBAN_WORKSPACE` unless the task body says to.
- Create follow-up tasks assigned to yourself — assign to the right specialist.
- Complete a task you didn't actually finish — block it instead.

## Pitfalls

- **Task state can change between dispatch and startup.** Always `kanban_show` first.
- **Workspace may have stale artifacts** (especially `dir:` and `worktree`). Read the comment thread.
- **Don't rely on the CLI when tools are available.** `kanban_*` tools work across all backends; `hermes kanban` CLI may fail in containerized backends.
- **Don't invent `t_<hex>` ids.** The prose-scan catches unresolvable references (advisory warnings on the dashboard).

## CLI fallback (for scripting)

Every tool has a CLI equivalent:
- `kanban_show` -> `hermes kanban show <id> --json`
- `kanban_complete` -> `hermes kanban complete <id> --summary "..." --metadata '{...}'`
- `kanban_block` -> `hermes kanban block <id> "reason"`
- `kanban_create` -> `hermes kanban create "title" --assignee <profile> [--parent <id>]`

Use the tools inside agents; the CLI exists for human operators.
