# Reminders / 记事本

## Entry format / 条目格式
- `[due: YYYY-MM-DD][active] content`  — dated reminder
- `[due: YYYY-MM-DD][earliest:HH:MM][active] content`  — dated, only triggers after HH:MM on that day
- `[due: on-demand][active][created:YYYY-MM-DD] content`   — no date, persistent until `done`; `created` used for timeout
- `[due: daily-until-done][active] content` — shown every session until user says it's done

## States / 状态
- `active`  — pending
- `done`    — user acknowledged completion (archived on next session-start per tier rules)
- `expired` — date passed without response (prompt once, then archive per `[L]`)

## Trigger rules (called from MEMORY.md Startup Protocol step 4)
- Today-due → **⚠️ Today**
- Overdue → **🔴 Expired X days**
- Upcoming within 3 days → 📅 Soon
- `on-demand` → shown every session until `done`
  - **If `today - created > ondemand_timeout_days` (default 14)** → append **❓** "still on your list?"; user says "yes" → reset `created`; "no / drop it" → delete
- `daily-until-done` → shown every session

## Archive rules (tier-based)
- **done**: has reference value (config decision / incident conclusion) → write to Recent Memory as `[L]` or `[M]`; pure one-off (drug, dinner, car wash) → delete
- **expired, no response**: prompt once, still no response → delete per `[L]`
- **user cancelled** ("drop it", "不做了"): delete directly

## User intent recognition (auto-write)
- **Add**:
  - "remind me X" / "记得提醒我 X" → `[due: on-demand][active][created:TODAY]`
  - "X on YYYY-MM-DD" / "X 月 Y 日 Z" → `[due: YYYY-MM-DD][active]`
  - "X on DATE after HH:MM" / "X 月 Y 日 HH 点以后 Z" → `[due: YYYY-MM-DD][earliest:HH:MM][active]`
  - "daily until done X" / "每天提醒直到搞定 X" → `[due: daily-until-done][active]`
- **Complete**: "X done / finished / sorted / wrapped up / handled" / "搞定/做完/完成/处理完/弄好/解决/办好/结了 X" → mark `done`
- **Cancel**: "cancel X / drop X" / "X 不做了/取消/算了/跳过" → delete

---

## Active
<!-- e.g. [due: 2026-05-10][active] Annual health check-up -->

## Done (pending archive)
<!-- Processed on next session-start per tier rules -->

## Expired (pending user response)
<!-- Date passed; user hasn't confirmed completion or cancellation -->
