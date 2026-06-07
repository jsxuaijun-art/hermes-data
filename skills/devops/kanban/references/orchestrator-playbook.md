# Kanban Orchestrator Playbook

> **Core worker lifecycle** (including the kanban_create fan-out pattern and "don't do the work yourself" rule) is auto-injected via KANBAN_GUIDANCE. This playbook is the deeper detail for routing work.

## Profiles are user-configured — not a fixed roster

There is **no default specialist roster**. Before fanning out, ground decomposition in profiles that actually exist:

```bash
hermes profile list
```

Or ask the user. Never invent profile names — the dispatcher silently drops unknown assignees.

## When to use the board (vs. just doing the work)

Create Kanban tasks when any of these are true:
1. **Multiple specialists** are needed
2. Work should survive a crash or restart
3. User might want to interject (human-in-the-loop)
4. Multiple subtasks can run in parallel
5. Review / iteration is expected
6. The audit trail matters

If none apply, use `delegate_task` instead.

## The Anti-Temptation Rules

- **Do not execute the work yourself.** Create a task for the right specialist.
- **For any concrete task, create a Kanban task and assign it.** Every single time.
- **Split multi-lane requests before creating cards.** One card per independent workstream.
- **Run independent lanes in parallel.** Link only true data dependencies.
- **Never create dependent work as independent ready cards.** Pass `parents=[]` in the create call.
- **If no specialist fits, ask the user.** Do not invent profile names.

## Decomposition Playbook

### Understand the Goal
Ask clarifying questions if ambiguous. Cheap to ask; expensive to spawn the wrong fleet.

### Sketch the Task Graph
Extract lanes from the request. Map each to a discovered profile. Decide independence vs. gating.

### Create Tasks and Link

```python
t1 = kanban_create(title="research: cost comparison", assignee="<profile-A>",
    body="Compare infrastructure costs over 3-year window.")["task_id"]
t2 = kanban_create(title="research: performance bench", assignee="<profile-A>",
    body="Compare query latency at 500GB / 10k QPS.")["task_id"]
t3 = kanban_create(title="synthesize recommendation", assignee="<profile-B>",
    body="Read T1+T2, produce 1-page recommendation.", parents=[t1, t2])["task_id"]
```

Create parent cards first, capture their IDs, then create children with `parents=[...]`.

### Complete Your Own Task

```python
kanban_complete(
    summary="decomposed 3 task graph",
    metadata={"task_graph": {"T1": {"assignee": "profile-A"}, "T2": {"assignee": "profile-A"}, "T3": {"assignee": "profile-B", "parents": ["T1", "T2"]}}}
)
```

### Report to User

Tell them what was created and which profiles are working. "The dispatcher will pick up T1 and T2 now."

## Common Patterns

- **Fan-out + fan-in**: N research cards, one synthesis card with all parents.
- **Pipeline with gates**: planner → implementer → reviewer.
- **Same-profile queue**: N cards, same assignee, no dependencies. Dispatcher serializes.
- **Human-in-the-loop**: Any task can `kanban_block()`. Operator unblocks via comment.

## Pitfalls

- **Inventing profile names** — dispatcher silently fails. Always discover first.
- **Bundling independent lanes** into one card. Two independent outcomes = two cards.
- **Over-linking due to wording** — "finally check X" may be parallel if X is static.
- **Forgetting dependency links** — parent links gate children from running too early.
- **Creating the whole graph if shape depends on findings** — let T3 be a "synthesize findings" task.
- **Reassignment vs. new task** — reviewer blocks with changes? Create a NEW task for the implementer.
- **Link argument order** — `kanban_link(parent_id=..., child_id=...)` — parent first.
