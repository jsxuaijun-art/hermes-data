# Orchestrator Decomposition Playbook — Full Reference

> Previously the standalone `kanban-orchestrator` skill. Absorbed into the `kanban` umbrella.

The core worker lifecycle (including the `kanban_create` fan-out pattern and the "don't do the work yourself" rule) is auto-injected into every kanban process via the `KANBAN_GUIDANCE` system-prompt block. This reference is the deeper playbook when you're an orchestrator profile whose whole job is routing.

## Profiles are user-configured (not a fixed roster)

Hermes setups vary widely. Some users run a single profile that does everything; some run a small fleet; some run a curated specialist team. There is **no default specialist roster** — the orchestrator skill does not know what profiles exist on this machine.

Before fanning out, you must ground the decomposition in the profiles that actually exist. The dispatcher silently fails to spawn unknown assignee names — it doesn't autocorrect, doesn't suggest, doesn't fall back. A card assigned to a non-existent profile just sits in `ready` forever.

**Step 0: discover available profiles before planning.**

- `hermes profile list` — prints the table of profiles configured on this machine
- `kanban_list(assignee="<some-name>")` — sanity-check a single name (returns empty list for unknown, not an error)
- **Just ask the user** — "What profiles do you have set up?" is a fine first turn

Cache the result in working memory for the rest of the conversation.

## The anti-temptation rules

Your job description says "route, don't execute." The rules that enforce that:

- **Do not execute the work yourself.** If you find yourself "just fixing this quickly" — stop and create a task for the right specialist.
- **For any concrete task, create a Kanban task and assign it.** Every single time.
- **Split multi-lane requests before creating cards.** A user prompt can contain several independent workstreams. Extract those lanes first, then create one card per lane.
- **Run independent lanes in parallel.** If two cards do not need each other's output, leave them unlinked.
- **Never create dependent work as independent ready cards.** If a card depends on another, pass `parents=[...]` in the original `kanban_create` call.
- **If no specialist fits the available profiles, ask the user.** Do not invent profile names.
- **Decompose, route, and summarize — that's the whole job.**

## Decomposition playbook

### Step 1 — Understand the goal

Ask clarifying questions if the goal is ambiguous.

### Step 2 — Sketch the task graph

Before creating anything, draft the graph:

1. Extract the lanes from the request.
2. Map each lane to one of the profiles you discovered in Step 0. If a lane doesn't fit any existing profile, ask.
3. Decide whether each lane is independent or gated by another lane.
4. Create independent lanes as parallel cards with no parent links.
5. Create synthesis/review/integration cards with parent links to the lanes they depend on.

Examples of prompts that should fan out:

- "Build an app" — one card to a design profile, one or two to engineering profiles, plus integration/review.
- "Fix blockers and check model variants" — one implementation card for blockers + one discovery card for variant check. Review depends on both.
- "Research docs and implement" — a docs-research card in parallel with a codebase-discovery card; implementation waits only if it truly needs findings.

Show the graph to the user before creating cards. Let them correct it.

### Step 3 — Create tasks and link

Use the profile names from Step 0. Example with placeholders:

```python
t1 = kanban_create(
    title="research: Postgres cost vs current",
    assignee="<profile-A>",
    body="Compare estimated infrastructure costs, migration costs, and ongoing ops costs.",
    tenant=os.environ.get("HERMES_TENANT"),
)["task_id"]

t2 = kanban_create(
    title="research: Postgres performance vs current",
    assignee="<profile-A>",
    body="Compare query latency, throughput, scaling at our data volume.",
)["task_id"]

t3 = kanban_create(
    title="synthesize migration recommendation",
    assignee="<profile-B>",
    body="Read findings from T1 and T2. Produce a recommendation.",
    parents=[t1, t2],
)["task_id"]
```

`parents=[...]` gates promotion — children stay in `todo` until every parent reaches `done`, then auto-promote to `ready`.

Create parent cards first, capture their returned ids, and include those ids in the child card's `parents` list during the child `kanban_create` call. Avoid creating all cards in parallel and linking afterward.

### Step 4 — Complete your own task

```python
kanban_complete(
    summary="decomposed into T1-T4: 2 research lanes in parallel, 1 synthesis on outputs, 1 prose draft on recommendation",
    metadata={
        "task_graph": {
            "T1": {"assignee": "<profile-A>", "parents": []},
            "T2": {"assignee": "<profile-A>", "parents": []},
            "T3": {"assignee": "<profile-B>", "parents": ["T1", "T2"]},
        },
    },
)
```

### Step 5 — Report back

Tell the user what you created, naming the actual profiles used.

## Common patterns

**Fan-out + fan-in:** N research cards (no parents), one synthesis card (parents = all of them).

**Parallel implementation + validation:** One implementer card + one explorer card + optional reviewer card depending on both.

**Pipeline with gates:** `planner -> implementer -> reviewer`. Each stage's `parents=[previous_task]`.

**Same-profile queue:** N tasks, same assignee, no dependencies. Dispatcher serializes.

**Human-in-the-loop:** Any task can `kanban_block()` to wait for input. Dispatcher respawns after `/unblock`.

## Pitfalls

- **Inventing profile names that don't exist** — silent failure. Always use Step 0 discovery.
- **Bundling independent lanes into one card** — "fix blockers and check model variants" is two cards.
- **Over-linking because of wording** — "Finally check X" may still be parallel if X doesn't depend on implementation.
- **Forgetting dependency links** — if the graph says `research -> implement`, use parent links.
- **Reassignment vs. new task** — if review blocks with "needs changes," create a NEW task, don't re-run the same one.
- **Argument order for links** — `kanban_link(parent_id=..., child_id=...)`. Parent first.
- **Don't pre-create the whole graph** if shape depends on intermediate findings.
- **Tenant inheritance** — pass `tenant=os.environ.get("HERMES_TENANT")` on every `kanban_create`.

## Recovering stuck workers

When a worker keeps crashing, hallucinating, or getting blocked by its own mistakes:

1. **Reclaim** (or `hermes kanban reclaim <task_id>`) — abort worker, reset to `ready`.
2. **Reassign** (or `hermes kanban reassign <task_id> <new-profile> --reclaim`) — switch to a different profile.
3. **Change profile model** — dashboard prints a copy-paste hint for `hermes -p <profile> model`; edit config, then Reclaim.

Hallucination warnings appear on tasks where a worker claims phantom card ids (gate blocks completion) or references unresolvable `t_<hex>` ids in prose (advisory scan).
