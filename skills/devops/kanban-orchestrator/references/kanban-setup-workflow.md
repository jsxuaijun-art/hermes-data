# Kanban Setup Worked Example

Complete workflow from zero to running multi-agent. Based on a real session with a Chinese-language
财税服务 (tax/accounting) user who had only the default profile.

## Scenario

User wants multi-agent: one profile researches tax policy, another writes marketing copy.

## Step-by-step

### 1. Create profiles

```bash
hermes profile create researcher --clone --description "财税政策研究、资料搜集、行业调研"
hermes profile create writer --clone     --description "短视频文案、获客内容、营销素材创作"
```

This clones config, .env, SOUL.md, and skills from the active profile (default).
Creates aliases so `researcher chat` works at the terminal.

### 2. Write role-defining SOUL.md

Path: `~/.hermes/profiles/researcher/SOUL.md`

Content pattern:
- Define role title (e.g. "财税研究专家")
- List core responsibilities (policy research, data analysis, report writing)
- Set working style (rigorous, source-attributed, structured output)

Path: `~/.hermes/profiles/writer/SOUL.md`

Content pattern:
- Define role title (e.g. "营销内容创作专家")
- List core responsibilities (short video scripts, copywriting, SEO)
- Set working style (strong hooks, benefit-driven, conversion-focused)

### 3. Set models per profile

```bash
hermes config set --profile researcher model.default deepseek-chat
hermes config set --profile writer model.default deepseek-chat
```

### 4. Verify

```bash
hermes profile list
# Expected output:
#   default       deepseek-v4-flash
#   researcher    deepseek-chat
#   writer        deepseek-chat
```

### 5. Create Kanban tasks

```bash
# Task 1: research (use --json for programmatic access to task id)
hermes kanban create "研究：2025年小微企业增值税优惠政策最新变化" \
  --assignee researcher \
  --body "查找2025年以来小微企业增值税减免政策的变化，包括月销售额免税额度、征收率调整等。输出500字以内政策摘要，标注来源。" \
  --json

# Task 2: write (independent — no dependency on task 1)
hermes kanban create "写短视频脚本：小微企业增值税优惠" \
  --assignee writer \
  --body "基于政策写一条60秒短视频口播脚本。格式：开头钩子+中间干货+结尾引导。" \
  --json

# Task 3: dependent task — waits for Task 1 to complete first
T1=$(hermes kanban create "研究政策" --assignee researcher --body "..." --json 2>&1 | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
hermes kanban create "基于研究写总结" --assignee writer --body "..." --parent $T1
```

### 6. Dispatch

```bash
hermes kanban dispatch
```

Expected output shows spawned workers with workspace paths:
```bash
Spawned: 2
  - t_a2ad956c  ->  researcher  @ /home/.../workspaces/t_a2ad956c
  - t_08e06ab1  ->  writer      @ /home/.../workspaces/t_08e06ab1
```

### 7. Monitor

```bash
# Quick status check
hermes kanban list

# Detailed output (after completion) — shows comments + events + summary
hermes kanban show t_a2ad956c

# Full worker log transcript — captures stdout unlike `show`
hermes kanban log t_08e06ab1

# Add context mid-run
hermes kanban comment t_a2ad956c "补充信息：关注某某公告的最新变化"

# Follow task events in real-time
hermes kanban tail t_a2ad956c
```

### 8. Recover stuck workers

If a worker crashes or hangs:

```bash
# Release the stuck worker's claim
hermes kanban reclaim t_a2ad956c

# Reassign to a different profile (or the same one after fixing the issue)
hermes kanban reassign t_a2ad956c researcher --reclaim
```

### 9. Results

Tasks complete in ~30-60 seconds each. Worker output is available via:
- `kanban show` — comments + events + final summary
- Workspace files (scratch workspaces are ephemeral — use `--workspace dir:/path` to persist)
- `kanban log` — full transcript of the worker's stdout

## Key learnings

| Item | Detail |
|------|--------|
| Task body flag | `--body`, NOT `--description` |
| Profile desc flag | `--description` on `hermes profile create` sets decomposer role hints |
| Workspace type | Default `scratch` is ephemeral. Use `--workspace dir:` to persist |
| Dispatch | Must call `hermes kanban dispatch` explicitly (or run gateway daemon) |
| Failed spawns | Unknown assignees → task stays in `ready` silently, no error |
| Worker log | `hermes kanban log <id>` captures full stdout unlike `show` which only has structured fields |
| JSON output | `--json` on `hermes kanban create` returns structured task data, useful for scripting |
| Parent link | `--parent <task_id>` creates dependency; child auto-promotes from `todo` to `ready` when all parents complete |
| Comment on task | `hermes kanban comment <task_id> "message"` for adding context mid-run |
| Task lock | If a worker crashes, `hermes kanban reclaim <id>` then `hermes kanban reassign <id> <profile> --reclaim` |
| Profile model | Set per-profile model with `hermes config set --profile <name> model.default <model>` |
