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

## Remote User SSH Guidance (critical non-technical user pattern)

When guiding a user through SSH commands on a remote server, **recognize the terminal state** they're in — don't just repeat your command request:

### The `tail -f` trap (happened in this session)

**Symptom**: You ask the user to run `cat /some/file`. They keep pasting output with different timestamps every time. You think they're ignoring you and running the wrong command.

**Reality**: They ran `tail -f /some/file` (watching live logs) earlier, and **it's still running**. Every paste is the next batch of log lines being output. Your "run this other command" messages never reached a prompt — they were being typed into the same `tail -f` terminal that's busy emitting output.

**Fix sequence** (step by step, give them ONE action at a time):

```
Step 1: "先按 Ctrl+C 停掉当前输出"          ← Stop the live stream
Step 2: "输入 clear 然后回车"                ← Clear screen
Step 3: "复制这行，粘贴，回车: cat /path"    ← The actual command
```

**How to recognize `tail -f` vs static output:**
- ✅ Static file output: all lines arrive in one batch, no new content appears
- ❌ Live stream: new lines keep appearing with later timestamps each time the user pastes
- Telltale sign: `--` (less pager separator) or lines with known future timestamps

**Rule**: When a user pastes output more than twice that matches a known file pattern, **assume they're in a live log viewer and tell them to Ctrl+C first**. Do not ask again for the same command. Restate the exact escape sequence and THEN the command.

### The "Wrong command loop" (new: extension of tail -f trap)

**Symptom**: User keeps pasting output from `cat errors.log` (or similar) despite you asking for `cat config.yaml` (or any other file). Each paste shows different content. You tell them "don't run errors.log, run config.yaml" — they paste more errors.log output.

**What's actually happening (3 possible states):**
1. **Still in `tail -f`** — the live viewer is still running, they're pasting new log lines. Tell them to Ctrl+C first.
2. **Re-executing the wrong command manually** — they closed tail but `cat errors.log` has become muscle memory. They're running the wrong command over and over, pasting your instructions into the output stream without reading them.
3. **Reading from a piped pager** — `cat errors.log` output is long, they're scrolling through it and pasting chunks they see on screen.

**How to tell them apart:**
- State 1: Timestamps keep advancing, output is segmented (live feed)
- State 2: Timestamps are static, but different segments keep appearing (they're re-running the wrong command)
- State 3: All lines share the same `cat` output format, pasted in blocks

**Fix sequence (one action per message — do NOT combine steps):**

When you've asked 3+ times and they still paste wrong output, STOP repeating. Use this escalation ladder:

```
Attempt 1: "先按 Ctrl+C 停掉输出" (just this, wait for response)
Attempt 2: "再输入 clear 回车" (one line, wait)
Attempt 3: "最后输入: cat /root/.hermes/config.yaml" (one single command, wait)
```

**If they still paste wrong output after the cleared attempt above:**
→ SHUT IT DOWN and offer takeover immediately:

```
「关掉这个 SSH 窗口（点 X），重新开一个。
连上后只打一行：cat /root/.hermes/config.yaml
再搞不定就把服务器 IP 和密码发我，我直接 SSH 上去搞定。」
```

**Key insight: brevity is critical.** 3-step instructions in one message are too long. The user skims for the command, finds a similar-looking filename, runs it, pastes the output. Keep each instruction to **one action + one filename** with zero extra text.

### Filename similarity trap

**Problem**: Users confuse filenames that share characters or structure:
- `errors.log` ↔ `config.yaml` (both end differently but the `config` / `error` mental overlap causes mis-reads)
- `jobs.json` ↔ `errors.json`
- `config.yaml` ↔ `config.json`

**Mitigation**: When asking a struggling user to run a command, spell out the full path exactly once and bold it. Do not say the filename again without context: `cat /root/.hermes/config.yaml` not just `cat config.yaml`. If they run the wrong file, restart from `Ctrl+C` + `clear` before giving the CORRECT command.

## Cron Failure Diagnosis

When a user reports a cron job "not starting" or showing `last_status=error`:

### ⚡ Step 0: Confirm the job lives on THIS machine (critical for multi-environment setups)

**Context**: User may run Hermes Agent on multiple machines (WSL laptop, Aliyun cloud server, office PC). Cron jobs live on the machine where they were created. A job failure notification received in one session may belong to a **different machine**.

**Classic trap** (happened in this session): User received a cron failure report (`财税情报推送`, HTTP 502) in the WSL Hermes CLI. I searched `~/.hermes/cron/jobs.json` locally, found nothing, and incorrectly concluded "任务已消失 / auto-cleaned." The job was actually running on the **Aliyun cloud server** (`/root/.hermes/cron/jobs.json`). The user had to correct me.

**Diagnosis flow when a cron job is not found locally**:

```
Step                          Command                                   Meaning
────                          ───────                                   ───────
1. Check local jobs.json      cat ~/.hermes/cron/jobs.json               Not there → NOT on this machine
2. Check local output dir     ls ~/.hermes/cron/output/                  No matching dir → confirms absence
3. System crontab             crontab -l | grep <job_name>               Hermes jobs live in jobs.json,
                                                                         but check for hybrid setups
4. Global grep for job_id     grep -r "<job_id>" ~/.hermes/              Zero hits → job is on another machine
5. Remote env check           Recall memory for "aliyun", "cloud",       User may have mentioned other
                              "server", "another computer"               machines in past sessions
```

**Rule**: Once Step 1 shows the job isn't in local jobs.json, and Step 4 returns nothing — **ask immediately**. Do NOT exhaustively search every possible location before asking. The user will tell you the correct machine faster than you can enumerate all possibilities.

**Ask pattern** (concise, no apology):
```
"这个任务不在本机上，请问是在哪台服务器创建的？给我 SSH 信息我上去查。"
```

**If job was on a now-shut-down server**: the job is gone and needs recreating. Offer to create a new one on the current machine.

**Prevention**: When creating cron jobs, note the target machine in the job name or in memory (e.g. "财税情报推送 runs on Aliyun"). This prevents future cross-environment confusion.

### Standard Diagnosis Flow (job confirmed on this machine)

1. **First, locate the job**: Run `cat ~/.hermes/cron/jobs.json` — check if the named job still exists in the jobs array.
   - **Job not found in jobs.json** → The system may have auto-cleaned the failed task. Check `ls ~/.hermes/cron/output/` for residual log directories. The user may have received a one-off error notification from a job that already expired.
   - **Job found with `last_status=error`** → Continue to step 2.

2. Run `cronjob list` — check `last_status`, `enabled`, `last_run_at`
3. Check `errors.log` for the actual error near `last_run_at` timestamp
4. Identify the error type:

### Error Pattern A: HTTP 5xx (502/503 — upstream service unavailable)

- **Symptom**: `HTTP 502: 上游服务暂时不可用` or generic 5xx
- **Cause**: Provider API gateway overload, upstream model restart, or transient network blip
- **Action**: This is a **transient fault**. No config change needed. **Do NOT drag the user through a diagnostic workflow** (checking logs, checking config, running commands) — just tell them it's a transient error and the next scheduled run will likely succeed.
  - `cronjob run <job_id>` for manual retry
  - Or wait for next scheduled run (cron scheduler auto-retries on its next cycle)
  - If 5xx persists across 3+ consecutive runs → escalate to provider status page to check for outage
- **Persistence**: These jobs are often auto-cleaned from jobs.json after failure, leaving only the user's one-time error notification. In that case, offer to recreate the job from scratch **without involving the user in the diagnosis**. Say "上游暂时不可用，下个周期会自动重试，不用管" unless the user asks for details.

### Error Pattern B: API key 401
- Most common cause — key was valid when cron was created but expired by fire time
- Manual re-run (`cronjob run`) reproduces the failure
- Fix the key in `.env`, re-run to confirm

### Error Pattern C: Config loading discrepancy
- **Same key works in CLI but not in cron?** → Check `base_url_env_var`
  (even if config.yaml has the custom base_url, the credential path doesn't read it)

### Error Pattern D: Approval bypass
- **Manual `cronjob run` creates an empty session?** → Pattern D — approval bypass
  (scheduled runs auto-bypass, manual runs don't)
   Even if `resolve_runtime_provider()` returns the correct base_url, the
   actual API call may use a different endpoint. The fix is to set the
   provider's `base_url_env_var` in `.env` (e.g. `DEEPSEEK_BASE_URL`).
   See `references/cron-failure-diagnosis.md#pattern-b-config-loading-discrepancy-provider-base_url-resolver`
   for the full mechanism and test script.

### Quick Checklist

| Step | What to check | Tool |
|------|--------------|------|
| 0 | Is the job on THIS machine? | `~/.hermes/cron/jobs.json` grep → if not found, ask user |
| 1 | Job exists in jobs.json? | `~/.hermes/cron/jobs.json` |
| 2 | Job state + last_status | `cronjob list` |
| 3 | Error message text | `~/.hermes/cron/output/<job_id>/` or notification |
| 4 | 5xx → transient retry | `cronjob run` or wait |
| 5 | 401 → API key expired | `.env` key refresh |
| 6 | Empty session on manual run | Approval bypass check |
| 7 | Job vanished from local | Was it on another machine? Ask user |
| 8 | Job confirmed gone (remote machine dead) | Recreate from scratch on current machine |

See `references/cron-failure-diagnosis.md` for the full diagnostic workflow, common failure patterns (API key 401, config loading discrepancy, subagent auth failure), and a quick checklist.
