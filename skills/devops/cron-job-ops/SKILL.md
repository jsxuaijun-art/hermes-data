---
name: cron-job-ops
description: Create, edit, retarget, verify Hermes cron jobs.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [cron, scheduler, delivery, operations]
    category: devops
    related_skills: [cron-data-collection-jobs, cron-tasks, competitor-news-monitor]
---

# Cron Job Ops

Operational layer for Hermes cron jobs on this machine: the CLI commands,
schedule grammar, delivery grammar, and verification for creating, editing,
retargeting, and debugging a scheduled job. Goes with `cron-data-collection-jobs`
(hows to design the job body for unattended live-data work) and `cron-tasks`
(reminder escalation); this skill owns the mechanics.

## When to Use

- Scheduling or rescheduling a recurring job for 徐总 ("每周/每月跑一次…").
- "帮我关注某人/某公司" — standing up an entity/competitor watch cron.
- A wecom-delivered cron isn't delivering and you need to tell setup from target.
- Verifying a job actually created correctly before telling the user.

## CLI quick reference

```bash
hermes cron list                     # all jobs: Name / Schedule / Next run / Deliver
hermes cron runs [job_id]            # executions for a job (manual run = source=direct)
hermes gateway status                # is the gateway up AND are platform creds present?
```

- **Create** — prompt is a POSITIONAL arg (there is NO `--prompt` on create):
  ```bash
  hermes cron create "0 9 1 * *" "<task prompt text>" \
      --name "名称" --skill <skill> --deliver <target>
  ```
- **Edit** — `hermes cron edit <job_id> --schedule ... --deliver ... --name ...`
  (schedule/deliver/name/skills are optional; this is how you retarget or
  re-time an existing job). Editing only changes the job record — it does NOT
  touch a skill's contract/state file; update those separately.
- **Remove** — `hermes cron remove <job_id>` (delete only after user confirms).

## Schedule grammar

5-field cron (分 时 日 月 周). Worked values:
- 每天 09:00 = `"0 9 * * *"`
- 每周一 09:00 = `"0 9 * * 1"`
- 每月 1 日 09:00 = `"0 9 1 * *"`
- Never 7-field; after create/edit, confirm via `hermes cron list` → `Next run`.

## Deliver grammar

- `origin` — result lands on disk; inspect via `hermes cron runs`.
- `local` — no delivery.
- `wecom:<chat_id>` — push to a wecom chat/group, e.g. `wecom:XuAiJun`,
  `wecom:yingxin_inner`.
- **Pitfall:** a `wecom:<chat_id>` target is only as good as the gateway.
  Until `hermes setup` actually connects wecom credentials, every run lands
  `blocked_config: ... has no gateway credentials configured (not connected)`
  and nothing is delivered — even though the target itself is valid. Fix =
  `hermes gateway status` + re-run setup, NOT re-targeting the job. Don't
  promise delivery until the gateway reports the platform connected.

## Entity / competitor watch ("帮我关注某人/某公司")

1. Design the watch contract (entities, aliases, categories, materiality,
   sources, cutoff) under `~/.hermes/competitor-watches/<slug>.json` — schema
   is owned by the `competitor-news-monitor` skill.
2. Create the job with `--skill competitor-news-monitor --deliver <target>`,
   prompt: "加载 competitor-news-monitor 技能，按 <contract path> 运行一次 tick…".
3. When the user later re-times or re-targets it, `hermes cron edit` the job
   AND update the contract's own `report_cadence`/`notes` fields so the tick
   and the job don't drift.
4. Log the watch's existence in memory (the user delegates "以后帮我关注…" and
   future sessions must not recreate it).

## Pitfalls

- `--prompt` on `create` → "unrecognized arguments"; the task text goes as the
  last positional arg.
- Re-timing a job via `cron edit` while the skill contract still claims the old
  cadence → tick and schedule drift. Sync both.
- Promising wecom delivery while `hermes gateway status` shows the platform
  unconfigured → the run lands `blocked_config` silently.
- Treating delivery failure as "wrong target" when it is really "gateway not
  connected" → pointless re-targeting noise.
- Source of truth for what's scheduled is `hermes cron list`, not memory or a
  hand-written reference — don't snapshot cron inventory into files.

## Verification

- [ ] `hermes cron list` shows the expected `Next run` and `Deliver` after any
      create/edit.
- [ ] If the job has a skill contract, its cadence/delivery fields match the job.
- [ ] wecom delivery only asserted when `hermes gateway status` shows the
      platform connected AND `hermes cron runs <id>` shows a completed delivery.

## Related

- `cron-data-collection-jobs` (devops, USER-OWNED — `hermes curator adopt` to
  edit): designing the job body when it needs live web data.
- `cron-tasks` (bundled): reminder escalation ladders.
- `competitor-news-monitor` (curated/external): watch-contract schema + tick
  procedure for entity monitoring.
