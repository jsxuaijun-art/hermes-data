---
name: cron-tasks
title: Cron Tasks — Autonomous Reminder Escalation
description: Autonomous cron-triggered task reminders — escalation ladder, state management, and graceful termination across N attempts. Governs how to handle recurring reminders when no user is present.
category: devops
triggers:
  - running as a cron job
  - scheduled task reminder
  - autonomous follow-up
  - no user present
  - escalation pattern
---

# Cron Tasks — Autonomous Reminder Escalation

## Core Principle

When running as a cron job with no user present, every message is a "last chance" until proven otherwise. Evolve the message — never repeat yourself.

## State Awareness

Before composing the output, determine:

1. **Attempt number**: Check `session_search` for previous cron sessions targeting the same task. Look for session IDs matching `cron_<hash>_*` in the sessions directory.
2. **What was said before**: Read the final assistant message from each previous cron session. Do NOT re-state the same information.
3. **User response status**: Has the user acted/interacted in non-cron sessions since the last reminder? If yes, adjust accordingly. If no, escalate.

## 3-Attempt Escalation Ladder

### Attempt 1 — Full Context + Friendly Nudge
- **Tone**: Warm, helpful, assumes good faith (user is busy, not ignoring)
- **Structure**: 
  - ✅ What's done (completed items)
  - ⏳ What's pending (blockers)
  - 🔜 What happens next (post-completion flow)
  - 📋 Explicit offer: "挑能答的答就行，跳过也行" (answer partials, skip, or I'll proceed with what I have)
- **Exit**: Soft landing — "如果先忙别的，直接忽略，回头说 X 就行"

### Attempt 2 — Time-Aware + Direct Push
- **Tone**: More direct, references elapsed time ("距离启动已经过去 N 天")
- **Structure**:
  - Compact summary (not full re-list)
  - Highlight the ONE most critical pending item
  - Post-completion flow (shortened)
  - End with a grounded observation ("一句话实话" section — industry insight, why this matters now)
- **Exit**: "准备好随时告诉我，直接开干，不用预热"

### Attempt 3 (Final) — Decisive + Options + Default
- **Tone**: Direct, respectful but final. Acknowledge this is attempt N.
- **Structure**:
  - State: "第 N 次提醒"
  - Time elapsed: "项目卡了 X 小时/天"
  - Two concrete options labeled **A** and **B**:
    - **A**: Proceed with reasonable assumptions (document what assumptions are being made)
    - **B**: Archive/pause the task (with clear "how to resume" instructions)
  - Guarantee: option A output is a draft that gets verified/refined, not a final deliverable
- **Default behavior**: "不回复的话默认归档，省得每天早上又弹一条"

## Default Fallback Rule

If this is attempt N of N (final attempt in the cron schedule):
- State the "no reply = archive" default explicitly
- Archive the task in memory/session notes
- Do NOT queue another reminder

## Prohibited Patterns

- ❌ Repeating the same message verbatim across attempts
- ❌ Sending the same tone/content for attempt 2 and attempt 3
- ❌ Leaving an open-ended "please let me know" at attempt 3 without a default action
- ❌ Apologizing for reminding (wastes characters, weakens tone)

## Reasonable Assumptions (for Option A)

When proceeding without complete data, use these defaults:
- **Tax collection method**: 查账征收 (strictest, most conservative — plan up, adjust down)
- **Revenue range**: 小规模纳税人 standard bracket for the industry
- **Missing fields**: Industry average or midpoint value
- **Document assumptions**: List each assumption explicitly in the output so the user knows what to verify

## Verification

After output, confirm:
- [ ] Attempt count is correct
- [ ] Tone matches the attempt number
- [ ] Not repeating any message from a previous attempt
- [ ] Default behavior is set if final attempt
- [ ] No open-ended "please respond" at attempt 3

## Cron Failure Diagnosis

When a user reports a cron job "not starting" or showing `last_status=error`:

1. Run `cronjob list` — check `last_status`, `enabled`, `last_run_at`
2. Check `errors.log` for the actual error near `last_run_at` timestamp
3. Most common cause: **API key 401** — key was valid when the cron was created but expired by fire time
4. Manual re-run (`cronjob run`) reproduces the failure
5. Fix the key in `.env`, re-run to confirm
- **Same key works in CLI but not in cron?** → Check `base_url_env_var`
  (even if config.yaml has the custom base_url, the credential path doesn't read it)
- **Manual `cronjob run` creates an empty session?** → Pattern D — approval bypass
  (scheduled runs auto-bypass, manual runs don't)
   Even if `resolve_runtime_provider()` returns the correct base_url, the
   actual API call may use a different endpoint. The fix is to set the
   provider's `base_url_env_var` in `.env` (e.g. `DEEPSEEK_BASE_URL`).
   See `references/cron-failure-diagnosis.md#pattern-b-config-loading-discrepancy-provider-base_url-resolver`
   for the full mechanism and test script.

See `references/cron-failure-diagnosis.md` for the full diagnostic workflow, common failure patterns (API key 401, config loading discrepancy, subagent auth failure), and a quick checklist.
