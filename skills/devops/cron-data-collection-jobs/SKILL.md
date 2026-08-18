---
name: cron-data-collection-jobs
description: Design unattended Hermes cron jobs that need live web data.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [cron, scheduler, web-scraping, data-collection, automation]
    category: devops
    related_skills: [cron-tasks, python-web-scraping-setup]
---

# Cron Data-Collection Jobs

Hermes cron jobs that need live web data (调研、检索、爬取、监控类任务) run
**fully unattended**: no user is present to approve anything. This changes the
design rules completely. This skill covers designing and debugging such jobs.

## When to Use

- Creating or editing a cron job whose prompt needs to fetch web/search data.
- A cron job shows `Execution: running` in `hermes cron list` and never finishes.
- Designing the quarterly 新媒体检索调研 job or similar scheduled research.

## Core Constraint (unattended sessions)

In an unattended cron session the agent CANNOT rely on:

1. **`terminal` network commands** — they hit the safety approval gate; with no
   user to approve they fail `BLOCKED: User denied this command` (or time out
   to the same). This is verified for manual runs (`source=direct`); treat it
   as true for every unattended path.
2. **`web_search` tool** — it only works if a web-search provider is configured
   via `hermes tools`. On this machine it is NOT configured, so the tool fails
   every time with `No web search provider configured`.

When both fail, the agent loops inside the retrieval step forever: the job
stays `running`, never reaches its final reply, and **delivery (企微/邮件等)
never happens**. The failure is silent unless you read the logs.

## Diagnosis (job stuck in "running")

```bash
hermes cron runs <job_id>        # source=direct → manual trigger (blocks on approval)
grep "cron_<job_id>_" ~/.hermes/logs/errors.log | tail -20
```

Stall signatures in errors.log:
- `Tool terminal returned error: BLOCKED: User denied this command` (×N)
- `Tool web_search returned error: No web search provider configured` (×N)

A runnable probe: `scripts/diagnose-cron-stall.sh <job_id>`.

## Procedure — Designing a Data-Needing Cron Job

1. **Prefer the job's `--script` pre-collection hook (designed path).** Write a
   standalone script (requests+bs4, etc.); its stdout is injected into the
   agent prompt. `no_agent=True` turns the script into the entire job. Data
   collection runs OUTSIDE the agent's tool loop, so no approval gate, no
   web_search dependency.
2. **If the task only reminds/reviews (no live data), keep it offline.**
3. **Manual foreground run** is fine for one-off research (user present).
4. **`--accept-hooks` / `hooks_auto_accept: true`** — explicit opt-in that lets
   unattended sessions auto-approve commands. Security risk (any command runs
   unattended); only with user consent, never the default.

## Pitfalls

- **Even `hermes cron edit` can be approval-blocked unattended.** Changing the
  prompt from an agent session with no user present may time out into BLOCKED.
  The user must be at the terminal to approve edits.
- **`hermes cron run <id>` may not re-fire** if the scheduler already holds the
  job ("Job is already being fired by the scheduler") — check `hermes cron runs`
  for the real execution id before re-triggering.
- **Don't design the prompt around tools that need configuration you haven't
  verified** (web_search). Verify with `hermes tools` first, or use `--script`.
- Do not promise delivery until `hermes cron runs <id>` shows a completed
  execution AND the delivery target actually received the message.

## Verification

- [ ] `hermes cron runs <job_id>` shows a completed execution (not `running`)
- [ ] No `BLOCKED` / `No web search provider configured` lines in errors.log
- [ ] Delivery target (企微 dm 等) actually received the output
- [ ] `hermes cron list` shows a sane `Next run`

## Related

Bundled skill `cron-tasks` covers reminder escalation ladders and its
`references/cron-failure-diagnosis.md` (in that skill's own directory)
Pattern D documents the manual-run approval stall — its "prefer web_search"
advice only holds on machines with a configured search provider; this machine
is not one. Scraping methods live in `python-web-scraping-setup`.
