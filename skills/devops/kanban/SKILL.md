---
name: kanban
description: "Multi-agent kanban workflow: orchestrator decomposition playbook and worker pitfalls/examples. Covers the full lifecycle: task decomposition, routing, execution, handoff, and recovery."
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [kanban, multi-agent, orchestration, worker, workflow]
    related_skills: []
---

# Kanban Multi-Agent Workflow

> This is the class-level umbrella for the Hermes Kanban system. It covers both the **orchestrator** perspective (decomposing goals into kanban cards for routing) and the **worker** perspective (executing tasks, summarizing, handing off). The core lifecycle (KANBAN_GUIDANCE) is auto-injected into every worker's system prompt; this skill provides the deeper detail.

## When to load this skill

- You're acting as an **orchestrator** and need to decompose a goal into kanban cards, route to specialist profiles, and manage dependencies.
- You're a **worker** spawned by the dispatcher and need guidance on summarizing, blocking, recovery, retry scenarios, and workspace handling.
- You want to understand the kanban system architecture (profiles, task graph, tenant isolation, dispatcher lifecycle).

---

## Section A — Orchestrator: Decomposition & Routing

> Full detail: `references/orchestrator-playbook.md`

The orchestrator's job is **"decompose, route, summarize -- don't execute."** Key responsibilities:

### Discover profiles before planning

Profiles are user-configured (no fixed roster exists). Before fanning out:

```bash
hermes profile list
```

Or ask the user what profiles exist. Assigning to an unknown profile name silently drops the card into `ready` forever.

### When to use the board (vs. delegate_task)

Create kanban tasks when:
1. **Multiple specialists** are needed
2. Work should **survive a crash** or restart
3. User might want to **interject** (human-in-the-loop)
4. Multiple subtasks can run **in parallel**
5. **Review / iteration** is expected
6. **Audit trail** matters

Otherwise, use `delegate_task` or answer directly.

### Core anti-temptation rules

- **Do not execute the work yourself.** Route it.
- **For any concrete task, create a kanban card and assign it.**
- **Split multi-lane requests** before creating cards (one card per lane).
- **Run independent lanes in parallel** (no parent links).
- **Link dependencies with `parents=[...]`** at creation time (not prose, not after).
- **If no specialist profile fits, ask the user.**

### Decomposition playbook

1. **Understand the goal** (ask clarifying questions).
2. **Sketch the task graph** (extract lanes, map to profiles, decide dependencies).
3. **Create tasks and link** (parents first, capture ids, pass to children).
4. **Complete your own task** with a structured summary.
5. **Report back** to the user.

### Recovering stuck workers

- **Reclaim** (abort worker, reset to ready)
- **Reassign** (switch to a different profile)
- **Change profile model** (edit config, reclaim)

See `references/orchestrator-playbook.md` for full detail on profile discovery, task graph examples with python code, dependency bootstrapping, and recovery commands.

---

## Section B — Worker: Execution & Handoff

> Full detail: `references/worker-pitfalls.md`

The worker's job is **"orient, work, heartbeat, block/complete."** Key responsibilities:

### Workspace handling

| Kind | Description |
|---|---|
| `scratch` | Fresh tmp dir, yours alone (GC'd when archived) |
| `dir:<path>` | Shared persistent directory (what you write persists) |
| `worktree` | Git worktree at resolved path (commit your work) |

### Tenant isolation

If `$HERMES_TENANT` is set, prefix memory entries with the tenant namespace.

### Good handoff shapes

- **Coding task**: `kanban_complete` with `changed_files`, `tests_run`, `tests_passed`, `decisions`
- **Review-required task**: `kanban_comment` with metadata, then `kanban_block(reason="review-required: ...")`
- **Research task**: `kanban_complete` with `sources_read`, `recommendation`, `benchmarks`
- **Review task**: `kanban_complete` with `pr_number`, `findings[]`, `approved`

### Block reasons that get answered

Bad: "stuck" (no context). Good: one specific decision needed.

### Heartbeats

Name progress (e.g., "epoch 12/50, loss 0.31"). Skip for tasks under ~2 minutes.

### Retry scenarios

Check `kanban_show` for prior runs (each has outcome, summary, error telling you what went wrong).

See `references/worker-pitfalls.md` for full detail on workspace edge cases, retry diagnostics, CLI fallbacks, claiming card rules, and all the "don't" rules.

---

## Architecture notes

- The **dispatcher** (kernel) claims ready tasks and spawns workers with `--skills kanban-worker`
- Profile names are user-configured; silent failure for unknown assignees
- Dependency engine: children stay in `todo` until all parents reach `done`, then auto-promote to `ready`
- Task state can change between dispatch and worker startup (always `kanban_show` first)
- Every `kanban_*` tool has a CLI equivalent: `hermes kanban <verb> <id> [args]`
