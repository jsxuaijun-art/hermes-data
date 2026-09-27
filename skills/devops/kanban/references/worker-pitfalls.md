<<<<<<< LOCAL (this PC)
# Kanban Worker — Pitfalls and Examples
=======
# Worker Pitfalls & Examples — Full Reference

> Previously the standalone `kanban-worker` skill. Absorbed into the `kanban` umbrella.

The **lifecycle** (6 steps: orient, work, heartbeat, block/complete) is auto-injected into every worker's system prompt via `KANBAN_GUIDANCE`. This reference is the deeper detail: good handoff shapes, retry diagnostics, edge cases.

## Workspace handling
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
> The lifecycle (orient → work → heartbeat → block/complete) is auto-injected via KANBAN_GUIDANCE. This reference covers edge cases, handoff shapes, and retry diagnostics.
=======
Your workspace kind tells you how to behave inside `$HERMES_KANBAN_WORKSPACE`:
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
## Workspace Handling
=======
| Kind | Description |
|---|---|
| `scratch` | Fresh tmp dir, yours alone. Read/write freely; GC'd when task is archived. |
| `dir:<path>` | Shared persistent directory. Other runs will read what you write. Path is guaranteed absolute. |
| `worktree` | Git worktree at the resolved path. If .git doesn't exist, run `git worktree add <path> <branch>` first. |
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
| Kind | What it is | How to work |
|---|---|---|
| `scratch` | Fresh tmp dir, yours alone | Read/write freely; GC'd when task archived |
| `dir:<path>` | Shared persistent directory | Other runs read what you write. Path is absolute. |
| `worktree` | Git worktree at resolved path | If `.git` doesn't exist, run `git worktree add`. Commit here. |
=======
## Tenant isolation
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
## Tenant Isolation
=======
If `$HERMES_TENANT` is set, the task belongs to a tenant namespace. Prefix memory entries with the tenant:
>>>>>>> REPO (github)

If `$HERMES_TENANT` is set, prefix memory entries with the tenant:
- Good: `business-a: Acme is our biggest customer`
<<<<<<< LOCAL (this PC)
- Bad: `Acme is our biggest customer`
=======
- Bad (leaks): `Acme is our biggest customer`
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
## Good Handoff Shapes
=======
## Good summary + metadata shapes
>>>>>>> REPO (github)

**Coding task:**
```python
kanban_complete(
<<<<<<< LOCAL (this PC)
    summary="shipped rate limiter — token bucket, 14 tests pass",
    metadata={"changed_files": ["rate_limiter.py"], "tests_run": 14, "tests_passed": 14, "decisions": ["user_id primary, IP fallback"]},
=======
    summary="shipped rate limiter -- token bucket, keys on user_id with IP fallback, 14 tests pass",
    metadata={
        "changed_files": ["rate_limiter.py", "tests/test_rate_limiter.py"],
        "tests_passed": 14,
        "decisions": ["user_id primary, IP fallback"],
    },
>>>>>>> REPO (github)
)
```

<<<<<<< LOCAL (this PC)
**Coding task needing review (review-required):**
=======
**Review-required coding task:**
>>>>>>> REPO (github)
```python
<<<<<<< LOCAL (this PC)
kanban_comment(body="review-required handoff:\n" + json.dumps({"changed_files": [...], "tests_passed": 14}, indent=2))
kanban_block(reason="review-required: rate limiter shipped — needs eyes on user_id/IP fallback")
=======
kanban_comment(
    body="review-required handoff:\n" + json.dumps({
        "changed_files": ["rate_limiter.py"],
        "tests_passed": 14,
        "diff_path": "/path/to/worktree",
    }, indent=2),
)
kanban_block(reason="review-required: rate limiter shipped, 14/14 tests pass -- needs eyes on user_id/IP fallback choice")
>>>>>>> REPO (github)
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
<<<<<<< LOCAL (this PC)
kanban_complete(summary="3 libraries reviewed; vLLM wins", metadata={"sources_read": 12, "recommendation": "vLLM"})
=======
kanban_complete(
    summary="reviewed PR #123; 2 blocking issues (SQL injection, missing CSRF)",
    metadata={"pr_number": 123, "findings": [
        {"severity": "critical", "file": "api/search.py", "issue": "raw SQL concat"},
        {"severity": "high", "file": "api/settings.py", "issue": "missing CSRF middleware"},
    ], "approved": False},
)
>>>>>>> REPO (github)
```

Shape `metadata` so downstream parsers can use it without re-reading your prose.

<<<<<<< LOCAL (this PC)
## Claiming Cards You Created
=======
## Claiming cards you actually created
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
Pass `created_cards=[ids]` on `kanban_complete`. The kernel validates each id. Never invent ids from prose.
=======
If your run produced new kanban tasks (via `kanban_create`), pass the ids in `created_cards` on `kanban_complete`. The kernel verifies each id exists and was created by your profile; phantom ids block the completion.
>>>>>>> REPO (github)

```python
# GOOD
c1 = kanban_create(title="fix SQL injection", assignee="security-worker")
<<<<<<< LOCAL (this PC)
c2 = kanban_create(title="fix CSRF", assignee="web-worker")
kanban_complete(summary="Review done", metadata={}, created_cards=[c1["task_id"], c2["task_id"]])
=======
kanban_complete(summary="remediation cards created", created_cards=[c1["task_id"]])

# BAD -- claiming ids you didn't capture from kanban_create returns
kanban_complete(summary="Created cards t_abc123", created_cards=["t_abc123"])  # gate rejects
>>>>>>> REPO (github)
```

If `kanban_create` fails (exception, tool_error), the card was NOT created. Retry or omit the id.

<<<<<<< LOCAL (this PC)
## Block Reasons That Get Answered Fast
=======
## Block reasons that get answered fast
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
Bad: `"stuck"` — no context. Good: one sentence naming the specific decision needed.
=======
Bad: "stuck" (no context).
Good: one sentence naming the decision you need. Leave full context as a comment.
>>>>>>> REPO (github)

```python
<<<<<<< LOCAL (this PC)
kanban_comment(body="Full context: I have user IPs from Cloudflare but some users are behind NATs...")
=======
kanban_comment(task_id=os.environ["HERMES_KANBAN_TASK"], body="Long context...")
>>>>>>> REPO (github)
kanban_block(reason="Rate limit key choice: IP (simple, NAT-unsafe) or user_id (requires auth)?")
```

The block message is what appears in the dashboard/gateway. The comment is deeper context.

## Heartbeats worth sending

<<<<<<< LOCAL (this PC)
## Heartbeats Worth Sending
=======
Good: "epoch 12/50, loss 0.31", "scanned 1.2M/2.4M rows", "uploaded 47/120 videos".
Bad: "still working", sub-second intervals. Skip for tasks under ~2 minutes.
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
Good: `"epoch 12/50, loss 0.31"`, `"scanned 1.2M/2.4M rows"`.
Bad: `"still working"`. Skip for tasks under ~2 minutes.
=======
## Retry scenarios
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
## Retry Scenarios
=======
If `kanban_show` returns `runs: [...]` with one or more closed runs, you're a retry:
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
If `kanban_show` shows prior runs, that's a retry:
- `outcome: "timed_out"` — chunk the work or shorten it
- `outcome: "crashed"` — OOM or segfault. Reduce memory.
- `outcome: "spawn_failed"` — missing credential, bad PATH. Block instead of retrying blindly.
=======
- `outcome: "timed_out"` — previous attempt hit max_runtime_seconds. Chunk or shorten the work.
- `outcome: "crashed"` — OOM or segfault. Reduce memory footprint.
- `outcome: "spawn_failed"` + error — usually profile config issue. Ask human via `kanban_block`.
>>>>>>> REPO (github)
- `outcome: "reclaimed"` — operator archived the task; you probably shouldn't be running.
- `outcome: "blocked"` — previous attempt blocked; unblock comment should be in the thread.

## Do NOT

<<<<<<< LOCAL (this PC)
- Call `delegate_task` instead of `kanban_create`
- Call `clarify` — use `kanban_comment` + `kanban_block`
- Modify files outside `$HERMES_KANBAN_WORKSPACE`
- Create follow-up tasks assigned to yourself
- Complete a task you didn't actually finish — block it instead
=======
- Call `delegate_task` as a substitute for `kanban_create`. delegate_task is for short reasoning subtasks inside YOUR run; kanban_create is for cross-agent handoffs.
- Modify files outside `$HERMES_KANBAN_WORKSPACE` unless the task body says to.
- Create follow-up tasks assigned to yourself — assign to the right specialist.
- Complete a task you didn't actually finish — block it instead.
>>>>>>> REPO (github)

## Pitfalls

- **Task state can change between dispatch and startup.** Always `kanban_show` first.
- **Workspace may have stale artifacts** (especially `dir:` and `worktree`). Read the comment thread.
- **Don't rely on the CLI when tools are available.** `kanban_*` tools work across all backends; `hermes kanban` CLI may fail in containerized backends.
- **Don't invent `t_<hex>` ids.** The prose-scan catches unresolvable references (advisory warnings on the dashboard).

<<<<<<< LOCAL (this PC)
**Task state can change between dispatch and startup.** Always `kanban_show` first. If it's blocked or archived, stop.
=======
## CLI fallback (for scripting)
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
**Workspace may have stale artifacts.** Especially `dir:` workspaces. Read the comment thread.
=======
Every tool has a CLI equivalent:
- `kanban_show` -> `hermes kanban show <id> --json`
- `kanban_complete` -> `hermes kanban complete <id> --summary "..." --metadata '{...}'`
- `kanban_block` -> `hermes kanban block <id> "reason"`
- `kanban_create` -> `hermes kanban create "title" --assignee <profile> [--parent <id>]`
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
**Don't rely on CLI when tools are available.** `hermes kanban <verb>` may fail in containerized backends.
=======
Use the tools inside agents; the CLI exists for human operators.
>>>>>>> REPO (github)
