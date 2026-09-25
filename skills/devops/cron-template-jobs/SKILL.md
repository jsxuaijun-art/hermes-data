---
name: cron-template-jobs
description: Use Python scripts as cron job loaders for template-based, dynamic-datetime agent tasks. Covers the script+prompt split pattern, date injection, conditional logic, delivery configuration, remote deployment (SSH/.env/Gateway), and push endpoint architecture for Hermes cron.
tags: [cron, scheduling, templates, python, loader, automation, webhook]
---

# Cron Template Jobs

Use this skill when creating a Hermes cron job whose prompt needs dynamic content — dates, week numbers, conditional sections — that cannot be hardcoded in the `prompt` field.

## The Problem

Hermes cron jobs support a static `prompt` field. When you need:
- Dynamic dates (today, last Monday, next 30 days)
- Conditional output (load template A on Monday, B on Wednesday)
- File paths with date strings

You cannot template these directly in the cron prompt.

## The Pattern: Script + Prompt Split

### Structure

```
~/.hermes/cron/
├── my_job_loader.py           # Python script → stdout = rendered template
└── my_job_template.md         # Markdown template with {{PLACEHOLDERS}}
```

### Python Loader Script

The script:
1. Reads the `.md` template
2. Substitutes `{{PLACEHOLDERS}}` with computed values
3. Prints the rendered template to stdout
4. Add execution instructions at the end (where to save, what to do)

```python
#!/usr/bin/env python3
"""Example: daily report loader"""
import os, datetime

template_path = os.path.expanduser("~/.hermes/cron/daily_report.md")
with open(template_path) as f:
    template = f.read()

today = datetime.date.today()
template = template.replace("{{DATE}}", today.strftime("%Y-%m-%d"))

# Add execution instructions
template += f"""
## Execution Instructions
1. Search all sources listed above
2. Generate report and save to ~/reports/{today.strftime('%Y-%m-%d')}.md
"""

print(template)
```

### Template File (`.md`)

The template is a full prompt — system instructions, source list, output format. It's what the agent will see as its task instruction. Placeholders use `{{DOUBLE_BRACES}}`:

```
# Daily Report
Date: {{DATE}}

## Sources
1. Source A (url)
2. Source B (url)

## Tasks
- Monitor X
- Generate Y

## Output Format
...
```

### Cron Job Creation

```bash
hermes cron create "0 9 * * 1,3,5" \
  --name "My Job" \
  --prompt "Follow the template output by the script. Search all sources, generate report, save to path specified in instructions." \
  --script cron/my_loader.py \
  --workdir /home/user
```

Or via the tool:

```
cronjob(action='create',
  schedule='5 9 * * 1,3,5',
  name='My Job',
  prompt='...',
  script='cron/my_loader.py',
  workdir='/home/jsxuaijun')
```

Key points in the prompt:
- Tell the agent to follow the script's stdout (the rendered template)
- Remind it to delete any residual `{{ }}` placeholders
- Tell it where to save output files
- Specify tool constraints if needed

### Conditional Loader Pattern

Load different templates or sections based on day of week:

```python
today = datetime.date.today()
dow = today.weekday()  # 0=Mon

# Always include daily part
output = [load_daily_template()]

# Monday only: add weekly analysis
if dow == 0:
    output.append(load_weekly_template())

# Append push/delivery instruction for the agent
output.append(f"python3 /path/to/push_script.py ~/reports/{today.strftime('%Y-%m-%d')}.md markdown")

print("\n".join(output))
```

**Real-world example** (from `china-tax-policy-monitoring`):
- Single cron job fires Mon/Wed/Fri at 09:05
- Python loader script checks `today.weekday()`:
  - Mon (0): outputs daily + weekly template + push instructions
  - Wed (2): outputs daily template + push instructions
  - Fri (4): outputs daily template + push instructions
- The agent generates content and saves to date-stamped files

This avoids maintaining separate cron jobs for daily vs weekly runs.

### Direct `jobs.json` Write (When CLI/API Fails)

On some environments (e.g., older Hermes versions, or when `cronjob()` tool returns `KeyError: 2` due to incompatible cron library), both `hermes cron create` and the `cronjob(action='create')` tool may fail.

**Workaround**: Write the job directly to `~/.hermes/cron/jobs.json`:

```json
{
  "jobs": [
    {
      "id": "unique-job-id-here",
      "name": "Job Name",
      "schedule": "5 9 * * 1,3,5",
      "prompt": "Follow the template output by the loader script...",
      "script": "cron/unified_tax_loader.py",
      "workdir": "/root",
      "deliver": "local",
      "repeat": 0,
      "enabled_toolsets": ["web", "terminal", "file"],
      "profile": "default",
      "no_agent": false,
      "created_at": "2026-05-31T00:00:00+08:00",
      "updated_at": "2026-05-31T00:00:00+08:00"
    }
  ]
}
```

Then restart the Hermes gateway for the changes to take effect:
```bash
hermes gateway restart
# or
kill -HUP $(pgrep hermes)
```

**Pitfalls**:
- The jobs.json file uses a `{"jobs": [...]}` object wrapper — NOT a bare JSON array `[...]`. Writing a bare array will cause `hermes cron list` to crash.
- `id` must be unique across all jobs. Generate with `python3 -c "import uuid; print(uuid.uuid4().hex[:12])"`
- After manual edit, always verify with `hermes cron list` or `cat ~/.hermes/cron/jobs.json | python3 -m json.tool`
- The gateway must be restarted after editing jobs.json for changes to load (it caches jobs on startup)
- `deliver`: use `"local"` for file-only output; update to webhook URL (e.g. `"webhook://wecom?url=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx"`) once available

### Conditional Delivery Markers

Add markers in the output for post-processing:

```python
if dow == 0:  # Monday
    print("DELIVERY: push to wecom")
else:
    print("DELIVERY: archive only")
```

The agent can then add text markers like `⚠️ 本报告需发送至企业微信群` in the report itself.

### Multiple Outputs from One Job

When a single cron run needs to produce multiple files (e.g., daily + weekly on Mondays):

1. The script outputs multiple template sections
2. The agent prompt tells it to save each section to a different path
3. Each section ends with its own save instruction

## Post-Generation Delivery Pattern

After the agent generates output files (reports, analyses, digests), the loader script can instruct the agent to push via a webhook:

### Script Output Pattern

In the loader script, append **push instructions** at the end of the rendered template:

```python
instructions = []
instructions.append("")
instructions.append("=" * 60)
instructions.append("【推送指令】")
instructions.append("=" * 60)
instructions.append("")
instructions.append("报告生成完成后，执行以下推送步骤：")
instructions.append(f"python3 /opt/wecom-bot/push_report.py ~/reports/{today.strftime('%Y-%m-%d')}.md markdown")
instructions.append("确认推送结果中 errcode == 0")
output.extend(instructions)
print("\n".join(output))
```

The agent reads the stdout and uses it as instructions. It generates the report, saves it, then runs the push command.

### Architecture

```
Loader script (stdout = template + push instructions)
  &#x2514; Hermes AI runs the job
       &#x251C; Searches sources, generates report, saves file
       &#x2514; Runs: python3 push_report.py <report_file>
            &#x2514; POST to push endpoint
                 &#x2514; Delivery service forwards to group chat
```

## Push-Endpoint Architecture (When No Built-in Webhook Exists)

When the target group (e.g., WeCom/WeWork) doesn't provide a simple webhook URL, or you need more control, add an HTTP endpoint to an existing Flask service that acts as a relay:

### Endpoint Template

```python
@app.route('/push', methods=['POST'])
def handle_push():
    \"\"\"Receive cron output and forward to group chat.\"\"\"
    try:
        data = request.get_json(force=True)
        msgtype = data.get('msgtype', 'text')
        if msgtype == 'markdown':
            content = data.get('markdown', {}).get('content', '')
        else:
            content = data.get('text', {}).get('content', '')
        if not content:
            return jsonify({"errcode": 400, "errmsg": "empty"}), 400
        
        # Forward to group via webhook
        webhook_key = os.getenv('WECOM_WEBHOOK_KEY', '')
        if webhook_key:
            url = f'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={webhook_key}'
            resp = requests.post(url, json=payload, timeout=15)
            return jsonify(resp.json())
        return jsonify({"errcode": 0, "errmsg": "received, webhook not configured"})
    except Exception as e:
        return jsonify({"errcode": 500, "errmsg": str(e)}), 500
```

### Client Push Script (push_report.py)

Script placed alongside the Flask app, called by the agent after report generation:

```python
#!/usr/bin/env python3
import json, sys, urllib.request

def push_report(content, msgtype="markdown"):
    push_url = "https://your-domain.com/push"
    max_len = 4000 if msgtype == "markdown" else 2000
    if len(content) > max_len:
        content = content[:max_len] + "\n\n...（截断，完整版查看归档）"
    payload = json.dumps({"msgtype": msgtype, msgtype: {"content": content}}).encode()
    req = urllib.request.Request(push_url, data=payload,
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())

if __name__ == "__main__":
    content = open(sys.argv[1]).read()
    msgtype = sys.argv[2] if len(sys.argv) > 2 else "markdown"
    sys.exit(0 if push_report(content, msgtype).get("errcode") == 0 else 1)
```

### Deployment Checklist

- [ ] Add `/push` endpoint to existing Flask service
- [ ] Add `WECOM_WEBHOOK_KEY` (or equivalent) to the service's `.env`
- [ ] Restart the service (systemd: `systemctl restart <service>`)
- [ ] Test with: `python3 push_report.py <test_file> markdown`
- [ ] Verify group receives the message
- [ ] Update cron loader script to append push instruction at end of output

## Content Marketing Module (for cron jobs that generate marketing content)

When your cron job template includes a content marketing section (video topics, copywriting, client outreach), use this spec to ensure each topic forces real audience engagement:

### Mandatory Elements Per Topic

Each topic must answer: **"Why should the viewer stop scrolling?"**
- **Hook (first 3 seconds)**: risk/benefit/conflict/surprise/counter-intuition. Must make a business owner stop and pay attention.
- **Copy structure**: Hook → emotional resonance → expert info → emotional value → call to action
- **Ending**: Must include a clear interaction instruction ("Comment if you've had the same issue" / "Like if this helped" / "Reply with '1' for the checklist")
- **Comment strategy**: Each video gets 1-2 pinned comment prompts (e.g., "I put the tax checklist in the comments — grab it")

### Template Skeleton

In your loader template's content marketing section:

```markdown
### 【强制规范】每条选题必须包含：

1. **前3秒钩子**：风险/利益/冲突/悬念/反常识
2. **文案结构**：钩子→共情痛点→专业信息→情绪价值→引导互动
3. **结尾引导**：必须有明确互动指令
4. **评论区配套**：1-2条置顶引导评论

### 视频号选题（3条）
1. **标题**：（不超25字）
   **文案结构**：
   - 钩子：
   - 中段：
   - 结尾引导：
   **拍摄建议**：

### 小红书选题（2条）
1. **标题**：封面标题
   **文案要点**：（800字内，分条，有排版美感）
   **互动设计**：

### 客户咨询切入口（1条）
- **话题**：
- **切入话术**：（能直接发微信的自然话术）
- **目标客户**：
- **预计转化动作**：
```

## Pitfalls

- **Script path resolution**: Script paths are relative to `~/.hermes/` by default. Always set `workdir` to your project root for consistency.
- **Placeholder cleanup**: Always tell the agent to delete residual `{{ }}` placeholders — if a replacement key has a typo, the placeholder survives into the final document.
- **Script must only use stdlib**: Hermes cron runs scripts with the system Python. Don't rely on pip packages in loader scripts.
- **stdout is the only channel**: The agent sees the script's stdout as context. Don't write status messages to stdout that aren't part of the prompt — use stderr for debug logging.
- **Gateway required**: Cron jobs don't fire automatically without a running Gateway (`hermes gateway run` or `tmux new -s gateway 'hermes gateway run'`). On Aliyun with systemd: `systemctl start hermes-gateway`.
- **WSL caveat**: WSL systemd services don't survive WSL restarts. Use tmux for persistent Gateway.
- **`hermes cron create` CLI bugs**: On some Hermes versions (v0.15.1 tested), the CLI may fail with:
  - `KeyError: 2` — incompatible cron library version. Workaround: write directly to `jobs.json` (see Direct `jobs.json` Write section above).
  - Unrecognized prompt arguments — when prompt contains newlines or special characters, the argument parser may misinterpret them. Use the `cronjob()` tool instead of CLI when prompt is complex.
- **`cronjob()` tool also fails** on some versions. If both CLI and tool fail, the `jobs.json` direct write is the only reliable fallback.
- **`.env` updates via SSH**: Use Python heredoc, not sed. sed treats `.` as regex wildcard and expands `$` as shell variable — both corrupt API keys. Write a temporary Python script on the remote, execute it, then clean up:
  ```bash
  ssh user@host 'python3 << '\''PYEOF'\''
  val = "sk-your-key-here"
  lines = open("/path/to/.env").readlines()
  with open("/path/to/.env", "w") as f:
      for line in lines:
          if line.startswith("KEY="):
              f.write(f"KEY={val}\n")
          else:
              f.write(line)
  PYEOF'
  ```
- **`hermes cron run <id>` triggers async — does NOT block**: The command schedules the job on the next scheduler tick and returns immediately. To verify execution:
  1. Run `hermes cron run <job_id>`
  2. Wait 30-60 seconds for the tick to fire
  3. Check with `hermes cron list` — look for `Last run: ... ok` or an error
  4. Verify output files have new timestamps
  5. Check gateway logs: `journalctl -u hermes-gateway --since "2 minutes ago"`
- **Gateway restart resets pending triggers**: If you ran `hermes cron run <job_id>` before restarting the Gateway, the pending trigger is lost. The new process inherits the schedule from `jobs.json` but does NOT carry over pending triggered runs. Re-run `hermes cron run <job_id>` after restart.
- **Test the script first**: Run `python3 ~/.hermes/cron/my_loader.py` standalone before wiring it to a cron job. Verify all placeholders are substituted and the output reads like a complete prompt.

## Verification Checklist

- [ ] Script runs without errors standalone
- [ ] No residual `{{ }}` placeholders in output
- [ ] Cron job created: `hermes cron list`
- [ ] Gateway running: `hermes gateway status` or `ps aux | grep hermes`
- [ ] Next run time looks correct
- [ ] Output directory exists for file saving

## Deployment Infrastructure (For Remote Cron Jobs)

When deploying cron jobs to a remote server (e.g., Alibaba Cloud), use the following reference files in this skill package:

| Reference | When to Use |
|-----------|-------------|
| [`references/aliyun-cron-deployment.md`](references/aliyun-cron-deployment.md) | Full remote deployment: SSH key setup, step-by-step SCP/cron creation, gateway restart, verification, .env writing, git backup, zip extraction |
| [`references/wecom-bot-architecture.md`](references/wecom-bot-architecture.md) | Understanding WeCom push delivery: smart robot vs webhook robot, endpoints, env vars |
| [`references/anysearch-installation.md`](references/anysearch-installation.md) | Deploying a skill (AnySearch) across WSL, Windows Desktop, and Alibaba Cloud |

Key infrastructure patterns covered in these references:

- **SSH Key Setup** — SSH_ASKPASS trick when sshpass/paramiko unavailable
- **`.env` Writing** — Python heredoc or base64 encoding to avoid shell expansion (NEVER use `sed`)
- **Skill Installation** — Python stdlib zip extraction (no `unzip` needed), works on any OS
- **Gateway Management** — systemd vs tmux, local vs Aliyun separation
- **Git Merge Conflict Fix** — Removing `<<<<<<<` markers from Hermes agent code

See the individual reference files for full details.

## Reference Files

The following files under this skill package capture session-specific detail from the tax-intelligence cron deployment that informed SKILL.md content:
| File | What it covers |
|------|---------------|
| `references/2026-05-31-tax-intel-cron.md` | Full architecture: Aliyun deployment, WeCom push endpoint, push_report.py, cron job config, provider setup, key operational notes |
| `references/content-marketing-spec.md` | Content marketing spec: hook rules, copy structure, interaction design, platform differences, client outreach templates — extracted from user-provided video optimization advice |
| `references/aliyun-cron-deployment.md` | Step-by-step remote deployment to Alibaba Cloud: SCP, jobs.json creation, gateway restart, verification, SSH key setup, .env writing via base64/SSH, git backup |
| `references/anysearch-installation.md` | Multi-environment AnySearch setup: key installation on WSL/Windows Desktop/Aliyun, connectivity verification |
| `references/wecom-bot-architecture.md` | WeCom smart robot vs custom webhook robot comparison, endpoint reference, env vars, key pitfalls |
