# Gateway Pairing & WeCom Troubleshooting

> Diagnosing "I don't recognize you yet" + pairing code errors, and "Gateway shutting down" interruptions.

## Symptom Map

| Error in WeCom | Message on user side | Root cause |
|---|---|---|
| "I don't recognize you yet! Here's your pairing code: XXXXXX" | User sees pairing prompt | Pairing data lost on gateway server — `/root/.hermes/pairing/` empty or missing |
| "⚠️ Gateway shutting down — Your current task will be interrupted." | Task interrupted mid-conversation | Gateway process restarted (--replace, systemd, or crash). Not necessarily an error — can happen during deployment or WebSocket reconnect |
| 401 during gateway LLM call | Silent failure or timeout | `auth.json` has `status: exhausted` with 401 for the LLM provider's API key — often a credential pool vs config mismatch |

## Diagnostic Checklist (Dual-Server Deployment)

When Gateway runs on a remote server (e.g. Aliyun ECS) and CLI is local (e.g. WSL), two sets of config exist:

### Step 1: Check gateway is running
```bash
# On gateway server
systemctl is-active hermes-gateway.service
# or
ps aux | grep 'hermes.*gateway'
```

### Step 2: Check pairing storage
```bash
# On gateway server
ls -la /root/.hermes/pairing/
hermes pairing list
# "No pairing data found" → pairing store is empty
```

Pairing data lives in `/root/.hermes/pairing/`. If this directory is empty but the user previously paired, the data was lost (e.g. filesystem reset, tmpfs, or manual cleanup).

### Step 3: Check credential pool vs config mismatch
A common pitfall: the `.env` points to a proxy/forwarder (`base_url: https://llm.chudian.site/v1`) but `auth.json` stores the raw DeepSeek key with `base_url: https://api.deepseek.com/v1`. The credential pool records status per base_url — if the key ever hit 401 at `api.deepseek.com`, the pool marks `status: exhausted` even though the key works fine via the forwarder.

```bash
# Check auth.json credential status
python3 -c "
import json
with open('/root/.hermes/auth.json') as f:
    d = json.load(f)
cp = d.get('credential_pool', {})
for k,v in cp.items():
    for cred in v:
        print(f'{k}: status={cred.get(\"last_status\")} base_url={cred.get(\"base_url\")}')
        if cred.get('last_error_message'):
            print(f'  error={cred[\"last_error_message\"][:100]}')
"

# Compare with config.yaml
grep -A5 "^model:" /root/.hermes/config.yaml | head -6
grep DEEPSEEK_API_KEY /root/.hermes/.env
```

**If the pool shows `status: exhausted` but the key is actually valid (works on a different base_url):**
```bash
# Reset the exhausted credential
hermes auth reset deepseek
```
Or, to prevent the pool from recording 401s from a different endpoint, ensure `credential_pool` records match the actual `model.base_url` in config.

### Step 4: Check gateway logs for context
```bash
# Look for pairing/recognition errors
grep -E '(pair|recognize|approve|auth|配对|不识别)' /root/.hermes/logs/gateway.log | tail -20

# Look for shutdown/crash events
grep -E '(shut|restart|reconnect|disconnected|--replace)' /root/.hermes/logs/gateway.log | tail -20

# Full gateway log (skip memory_monitor noise)
tail -100 /root/.hermes/logs/gateway.log | grep -v memory_monitor
```

### Step 5: Compare local vs remote config (if dual-server)
```bash
# Local (WSL)
echo "=== Local ==="
grep "base_url" ~/.hermes/config.yaml | head -1
python3 -c "import json; print(json.load(open('/home/dmin/.hermes/auth.json'))['credential_pool'])"

# Remote (via SSH)
ssh root@<server-ip> "echo '=== Remote ==='; grep 'base_url' /root/.hermes/config.yaml | head -1; python3 -c \"import json; print(json.load(open('/root/.hermes/auth.json'))['credential_pool'])\""
```

## Fixes

### Fix 1: Re-pair after pairing data loss
In WeCom, the bot sends a pairing code (e.g. `D8WFXSQX`). On the **gateway server**:
```bash
hermes pairing approve wecom D8WFXSQX
```
Returns `✅ Pairing approved for D8WFXSQX`. The user's WeCom DM should immediately resume.

### Fix 2: Gateway restart mid-conversation
If the user sees "Gateway shutting down — Your current task will be interrupted":
- This is usually a one-time event (deploy, reconnect, resource pressure)
- The task is interrupted; start a new conversation
- Check if restarts are frequent → look for crash loop in logs

### Fix 3: Credential pool status = exhausted but key works
```bash
hermes auth reset deepseek
```
Then verify:
```bash
hermes auth list deepseek
# Should show status=ok
```

### Fix 4: Prevent pairing data loss
Ensure `/root/.hermes/` lives on a persistent filesystem (not tmpfs). If using systemd:
```bash
# Check the service file for ExecStart to confirm HERMES_HOME path
systemctl cat hermes-gateway.service
```

## Prevention
- Monitor `auth.json` credential status as part of regular health checks
- Back up `/root/.hermes/pairing/` along with other config
- Use a dedicated LLM API key on the gateway server that isn't shared with other tools (avoids cross-contaminated exhaustion tracking)
