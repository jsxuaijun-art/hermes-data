---
name: kanban
category: devops
description: Kanban multi-agent workflow — orchestrator playbook for routing work through specialist workers, plus worker pitfalls and handoff examples. The core lifecycle (KANBAN_GUIDANCE) is auto-injected by the system.
version: 2.0.0
metadata:
  hermes:
    tags: [kanban, multi-agent, orchestration, worker, workflow, routing]
    related_skills: []
---

# Kanban Multi-Agent Workflow

## Overview

The Hermes Kanban system routes work through specialist workers on a persistent board. Two complementary skill sets are documented in `references/`:

| Role | Purpose | Reference |
|------|---------|-----------|
| **Orchestrator** | Decomposes tasks, routes to specialists, manages the board | `references/orchestrator.md` |
| **Worker** | Picks up tasks, does the work, hands off results | `references/worker.md` |

## Core Principles

- **Orchestrators route, they do not execute.** Decompose → assign → summarize — that's the whole job.
- **Workers get one task, do it well, hand off clearly.** Fresh context per task.
- **The board is persistent.** Tasks survive crashes and restarts. Audit trail lives in SQLite.
- **Human-in-the-loop always possible.** The user can interject at any step.

## When to Use the Board (vs. just doing the work)

Create Kanban tasks when any of these are true:
1. **Multiple specialists are needed** — research + analysis + writing is three profiles.
2. **The work should survive a crash or restart** — long-running, recurring, or important.
3. **The user might want to interject** — human-in-the-loop at any step.
4. **Multiple subtasks can run in parallel** — fan-out for speed.
5. **Review / iteration is expected** — a reviewer profile loops on drafter output.
6. **The audit trail matters** — board rows persist in SQLite forever.

If *none* of those apply, use `delegate_task` instead or answer directly.

## Standard Specialist Roster

| Profile | Does | Typical workspace |
|---------|------|-------------------|
| `researcher` | Reads sources, gathers facts, writes findings | `scratch` |
| `analyst` | Synthesizes, ranks, de-dupes | `scratch` |
| `writer` | Drafts prose in the user's voice | `scratch` or `dir:` |
| `reviewer` | Reads output, leaves findings, gates approval | `scratch` |
| `backend-eng` | Writes server-side code | `worktree` |
| `frontend-eng` | Writes client-side code | `worktree` |
| `ops` | Runs scripts, manages services, handles deployments | `dir:` |
| `pm` | Writes specs, acceptance criteria | `scratch` |

## See Also

- `references/orchestrator.md` — decomposition playbook, anti-temptation rules, task graph patterns
- `references/worker.md` — workspace handling, good summary shapes, retry diagnostics, edge cases
