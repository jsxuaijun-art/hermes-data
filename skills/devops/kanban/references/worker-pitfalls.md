# Kanban Worker — Pitfalls and Examples

> The lifecycle (orient → work → heartbeat → block/complete) is auto-injected via KANBAN_GUIDANCE. This reference covers edge cases, handoff shapes, and retry diagnostics.

## Workspace Handling

| Kind | What it is | How to work |
|---|---|---|
| `scratch` | Fresh tmp dir, yours alone | Read/write freely; GC'd when task archived |
| `dir:<path>` | Shared persistent directory | Other runs read what you write. Path is absolute. |
| `worktree` | Git worktree at resolved path | If `.git` doesn't exist, run `git worktree add`. Commit here. |

## Tenant Isolation

If `$HERMES_TENANT` is set, prefix memory entries with the tenant:
- Good: `business-a: Acme is our biggest customer`
- Bad: `Acme is our biggest customer`

## Good Handoff Shapes

**Coding task:**
```python
kanban_complete(
    summary="shipped rate limiter — token bucket, 14 tests pass",
    metadata={"changed_files": ["rate_limiter.py"], "tests_run": 14, "tests_passed": 14, "decisions": ["user_id primary, IP fallback"]},
)
```

**Coding task needing review (review-required):**
```python
kanban_comment(body="review-required handoff:\n" + json.dumps({"changed_files": [...], "tests_passed": 14}, indent=2))
kanban_block(reason="review-required: rate limiter shipped — needs eyes on user_id/IP fallback")
```

**Research task:**
```python
kanban_complete(summary="3 libraries reviewed; vLLM wins", metadata={"sources_read": 12, "recommendation": "vLLM"})
```

## Claiming Cards You Created

Pass `created_cards=[ids]` on `kanban_complete`. The kernel validates each id. Never invent ids from prose.

```python
c1 = kanban_create(title="fix SQL injection", assignee="security-worker")
c2 = kanban_create(title="fix CSRF", assignee="web-worker")
kanban_complete(summary="Review done", metadata={}, created_cards=[c1["task_id"], c2["task_id"]])
```

## Block Reasons That Get Answered Fast

Bad: `"stuck"` — no context. Good: one sentence naming the specific decision needed.

```python
kanban_comment(body="Full context: I have user IPs from Cloudflare but some users are behind NATs...")
kanban_block(reason="Rate limit key choice: IP (simple, NAT-unsafe) or user_id (requires auth)?")
```

## Heartbeats Worth Sending

Good: `"epoch 12/50, loss 0.31"`, `"scanned 1.2M/2.4M rows"`.
Bad: `"still working"`. Skip for tasks under ~2 minutes.

## Retry Scenarios

If `kanban_show` shows prior runs, that's a retry:
- `outcome: "timed_out"` — chunk the work or shorten it
- `outcome: "crashed"` — OOM or segfault. Reduce memory.
- `outcome: "spawn_failed"` — missing credential, bad PATH. Block instead of retrying blindly.
- `outcome: "reclaimed"` — operator archived the task; you probably shouldn't be running.

## Do NOT

- Call `delegate_task` instead of `kanban_create`
- Call `clarify` — use `kanban_comment` + `kanban_block`
- Modify files outside `$HERMES_KANBAN_WORKSPACE`
- Create follow-up tasks assigned to yourself
- Complete a task you didn't actually finish — block it instead

## Pitfalls

**Task state can change between dispatch and startup.** Always `kanban_show` first. If it's blocked or archived, stop.

**Workspace may have stale artifacts.** Especially `dir:` workspaces. Read the comment thread.

**Don't rely on CLI when tools are available.** `hermes kanban <verb>` may fail in containerized backends.
