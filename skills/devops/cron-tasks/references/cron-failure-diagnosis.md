# Cron Failure Diagnosis

> When a user reports "cron didn't start" or a job shows `last_status: error`.

## Diagnostic Workflow

### Step 1 — Check Job Status

```
cronjob list
```

Key fields to inspect:
- `enabled` — is the job enabled? (false = disabled)
- `last_status` — `ok`, `error`, or `completed`
- `last_run_at` — when it last ran
- `state` — `scheduled`, `completed`, `paused`
- `next_run_at` — when it's expected to fire next
- `last_delivery_error` — delivery-level errors (gateway, not LLM)

### Step 2 — Check System Logs

The LLM call itself (not the delivery) failures show up in `errors.log`:

```bash
tail -50 /home/administrator/.hermes/logs/errors.log
```

Search for the error timestamp near `last_run_at`.

### Step 3 — Manual Re-run

Trigger a manual run to reproduce the failure in real time:

```
cronjob action=run job_id=<id>
```

If the re-run succeeds but the scheduled run failed, suspect environment drift
(config not loading the same way at boot vs. interactive session).

---

## Common Failure Patterns

### Pattern A — API Key 401 (Authentication Failure)

**Signature in errors.log:**
```
HTTP 401: Authentication Fails, Your api key: ****xxxx is invalid
```

**Root causes:**
- API key expired or rotated at the provider
- Key was valid when set but expired between setup and cron fire time
- .env file not updated after key rotation
- Cron runs in a different context that doesn't pick up the configured `base_url`

**Fix:**
1. Get a fresh API key from the provider
2. Update `/home/administrator/.hermes/.env` with the new key
3. Re-run the cron job to verify
4. Update `DEEPSEEK_API_KEY` in memory if needed

### Pattern B — Config Loading Discrepancy (Provider base_url resolver)

**Signature:**
Cron attempts `api.deepseek.com/v1` but config.yaml specifies a custom `base_url`
(e.g. `https://llm.chudian.site/v1`). Same API key, same config — cron uses a
different endpoint than the CLI. Manual `cronjob run` after the fact shows the
correct base_url, but the scheduled run used the default → **timing / code-path
dependent**, not a stale config.

**Root cause chain:**

The cron scheduler calls `resolve_runtime_provider(requested=job.get("provider"))`.
For API-key providers (deepseek, openai, etc.), this internally calls
`resolve_api_key_provider_credentials(provider_id)` in `hermes_cli/auth.py`.

That function resolves base_url via:
1. Check `base_url_env_var` from `PROVIDER_REGISTRY` (e.g. `DEEPSEEK_BASE_URL`)
2. If set in `.env` → use that env var value
3. If NOT set → fallback to `inference_base_url` (the provider's hardcoded default)

**Critical: `config.yaml`'s `model.base_url` is NOT read by this credential resolution.**
The CLI works because `AIAgent.__init__` receives `base_url` directly from
`resolve_runtime_provider()` (which reads config.yaml), bypassing
`resolve_api_key_provider_credentials` entirely. The cron scheduler path
constructs AIAgent the same way (line 1628: `base_url=runtime.get("base_url")`),
but the underlying HTTP client that actually makes the API call uses the
credential-resolution base_url, not the AIAgent constructor parameter.

**Key code references in `auth.py`:**
- `PROVIDER_REGISTRY["deepseek"].base_url_env_var` = `"DEEPSEEK_BASE_URL"` (∼line 347)
- `PROVIDER_REGISTRY["deepseek"].inference_base_url` = `"https://api.deepseek.com/v1"` (∼line 345)
- `PROVIDER_REGISTRY["deepseek"].api_key_env_vars` = `("DEEPSEEK_API_KEY",)` (∼line 346)

**Verification test (run in Hermes venv):**
```bash
cd /path/to/hermes-agent && source venv/bin/activate
python3 -c "
import os
from hermes_constants import get_hermes_home
from dotenv import load_dotenv
load_dotenv(get_hermes_home() / '.env', override=True)

from hermes_cli.runtime_provider import resolve_runtime_provider, _get_model_config
from hermes_cli.auth import PROVIDER_REGISTRY

mc = _get_model_config()
print('model_cfg base_url:', mc.get('base_url'))

p = PROVIDER_REGISTRY.get('deepseek')
print('default base_url:', p.inference_base_url)
print('base_url_env_var:', p.base_url_env_var)
print('ENV var value:', os.getenv(p.base_url_env_var, '(NOT SET)'))
print()
rt = resolve_runtime_provider(requested='deepseek')
print('resolved base_url:', rt.get('base_url'))
"
```
Note: `resolve_runtime_provider()` itself may return the CORRECT base_url
(because it reads `_get_model_config()`), but the credential-resolution path
that the HTTP client actually uses does NOT — this is the gap. The 401 is a
red herring: the key is valid, but it's being sent to the wrong server.

**Definitive fix:**
Add the `base_url_env_var` to `.env` so provider-level resolution picks it up:
```
DEEPSEEK_BASE_URL=https://llm.chudian.site/v1
```
This works because `resolve_api_key_provider_credentials` checks
`os.getenv(pconfig.base_url_env_var)` at the credential level. When set,
it takes priority over the hardcoded `inference_base_url`.

**Double insurance pattern (recommended):**
Set BOTH locations — this covers every code path:
```
┌───────────────────────────────────────┐
│  🔐 Double insurance                  │
├───────────────────────────────────────┤
│                                       │
│  Layer 1 — .env                       │
│  DEEPSEEK_BASE_URL=...                │
│  → covers: credential resolution      │
│    (the actual HTTP client path)      │
│                                       │
│  Layer 2 — config.yaml                │
│  model.base_url: ...                  │
│  → covers: AIAgent constructor path   │
│    (resolve_runtime_provider output)  │
│                                       │
│  Both layers needed for full coverage │
└───────────────────────────────────────┘
```
The `.env` layer is the **critical one for cron**. `config.yaml` alone is
**not sufficient** — confirmed by a real case where config.yaml had the
correct base_url but cron still failed with 401 until `.env` was set.

**Why the same API key works in CLI but not cron:**
- CLI: `AIAgent(base_url=config.base_url)` → API call uses custom base_url → relay works
- Cron: credential-resolution path → no `DEEPSEEK_BASE_URL` env var → falls back to `api.deepseek.com/v1` → key sent to wrong endpoint → 401

**Verification after fix:**
Re-run the failed cron job and check `last_status`:
```
cronjob action=run job_id=<id>
cronjob list     # confirm last_status=ok
```

**Alternative — pin model in cron job:**
```
cronjob update job_id=<id> model={provider: deepseek, model: deepseek-v4-flash}
```
This may help if the explicit model config changes the resolution path, but is
less reliable than setting the env var. The env var fix is the definitive solution.

### Pattern C — Subagent Authentication Failure

**Signature in errors.log:**
```
[subagent-0] Non-retryable client error: Error code: 401
```

**Root cause:**
Cron jobs that spawn subagents inherit authentication. If the parent agent's
key is invalid, subagents fail too — but the error trace is one level deep
in the delegation system.

### Pattern D — Manual `cronjob run` Stuck on pending_approval

**Signature in errors.log:**
```
agent.tool_executor: Tool terminal returned error: {"status": "pending_approval",
"approval_pending": true, "command": "curl -s --connect-timeout 10 --max-time 20 \"https://...\""}
```

**User-visible symptom:**
- `cronjob list` shows `last_status=ok` for the scheduled run
- Manual `cronjob run` creates a new session but no messages appear
- `session_search` shows `message_count=0` for the cron session
- The cron job appears to hang indefinitely

**Root cause:**
Scheduled cron runs set `HERMES_CRON_SESSION=1` which bypasses terminal
approval gates (`--yolo` mode). However, **manual `cronjob run` does NOT
set this env var**. If the cron job's prompt triggers terminal commands
that require approval (e.g. curl to external URLs, file writes outside
allowed paths), the agent blocks forever waiting for user approval that
never comes — there's no user monitoring a manual cron run.

**Fix:**
1. If the cron job needs manual re-run, the agent running the manual
   trigger should either:
   - Use `/approve` in the CLI to approve the pending command, OR
   - Kill the stuck manual session (`/stop` or process kill)
   - Rely on the **scheduled run** which bypasses approval
2. For cron jobs that frequently need manual debugging, redesign the
   prompt to use `web_search` tool instead of `curl` — web_search does
   not trigger approval gates.
3. Alternatively, add `--yolo` flag to the manual `cronjob run` if the
   tool supports it (check via `cronjob update` model/prompt options).

**Prevention:**
- Cron job prompts should prefer `web_search` over `curl` in terminal
- If curl is unavoidable, keep scheduled runs as the sole execution path;
  treat manual runs as diagnostics-only that may fail on approval
- When writing a cron prompt, assume it will **only** run in scheduled
  mode (no user to approve), and design it accordingly

---
## Session-Debugging Workflow for Empty Cron Sessions

When a cron job shows `last_status=ok` but `session_search` shows a cron
session with `message_count=0`:

1. Check `errors.log` around the session's creation timestamp
2. If you find `pending_approval` entries → Pattern D (above)
3. If you find `import error` / `cannot import name` → the codebase
   was updated while the gateway process was running; restart the
   gateway (`systemctl --user restart hermes-gateway` or kill+relaunch)
4. If nothing at all in the logs → the agent may have hit the iteration
   limit without producing output; try a manual run to reproduce

---

## Quick Checklist for User Reports

When a user says "cron didn't start" or "定时任务没有启动":

1. ✅ `cronjob list` — check `last_status` and `enabled`
2. ✅ If `last_status=error` → `tail errors.log` around `last_run_at` time
3. ✅ Check for `401` / `Authentication Fails` / `API key is invalid`
4. ✅ Check `.env` for the provider's API key
5. ✅ Check `config.yaml` for `base_url` override
6. ✅ Confirm `DEEPSEEK_API_KEY` (or equivalent) shows the correct key value
7. ✅ Confirm `DEEPSEEK_BASE_URL` (or equivalent `base_url_env_var`) is set in `.env` if using a custom relay — same key working in CLI but failing in cron is a base_url mismatch
8. ✅ **Double insurance**: ensure BOTH `.env` (the env var) AND `config.yaml` (model.base_url) have the custom base_url — `.env` covers credential resolution, config.yaml covers the AIAgent constructor path. config.yaml alone is NOT sufficient for cron.
9. ✅ Re-run after fix to confirm green status
