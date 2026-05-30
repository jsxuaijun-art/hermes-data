# State Extraction from Previous Cron Sessions

When running as a cron task, use these techniques to determine what was said in previous attempts.

## Find Previous Cron Sessions

```bash
# List all cron session files sorted by time
ls -lt /home/administrator/.hermes/sessions/cron_*.json
```

## Extract the Last Assistant Message

```python
import json

with open('session_cron_<hash>_<timestamp>.json') as f:
    data = json.load(f)

msgs = [m for m in data['messages'] if m.get('role') == 'assistant']
if msgs:
    last = msgs[-1]
    content = last.get('content', '')
```

## Quick Terminal One-Liner

```bash
python3 -c "
import json
with open('/home/administrator/.hermes/sessions/session_cron_<hash>.json') as f:
    data = json.load(f)
    msgs=[m for m in data['messages'] if m.get('role')=='assistant']
    if msgs: print(msgs[-1].get('content','')[:2000])
"
```

## Determine Attempt Number

Count cron sessions with the same task hash that exist before the current session.

```bash
ls /home/administrator/.hermes/sessions/cron_<same_hash>_*.json | wc -l
```

The count of files = number of previous attempts. Current run adds 1.

## Verify User Didn't Act Between Reminders

Check non-cron sessions between the last cron reminder and now:

```bash
# Check if user interacted with the task topic in non-cron sessions
# Use session_search with relevant task keywords
session_search(query="task keyword")
```

Look for sessions with `source=cli` or `source=wecom` that mention the task topic.
