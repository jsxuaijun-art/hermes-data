---
name: hermes-credential-rotation
description: "Rotate or replace credentials (LLM API keys, WeCom secrets) for the self-hosted Hermes Agent framework running on WSL2 (Ubuntu). Use when the user reports a stolen, expired, or invalid API key, an HTTP 401 or 403 from the LLM provider (chudian or deepseek), errcode 40001 from WeCom callbacks, or simply asks to change the Hermes API key, model, or secret. Covers the three credential locations (config.yaml, auth.json, .env), the only safe sed pattern, the correct systemd service name, and the gotchas that otherwise cause silent failures."
agent_created: true
---

# Hermes Credential Rotation (WSL2)

## Overview

The self-hosted Hermes Agent stores credentials in **three separate files** under
`/home/dmin/.hermes/`. A single logical key can live in more than one place, so
"changing the key" often means editing two files, not one. This skill encodes the
proven rotation procedure and the traps that caused repeated failures in practice.

## When to use

- User says the Hermes API key was stolen / leaked / expired and needs replacing.
- Gateway logs show `HTTP 403: API Key 已被禁用或已过期` or `HTTP 401: Incorrect API key`.
- WeCom callback logs `errcode 40001 invalid credential`.
- User asks to change the Hermes model or provider key.

## Three credential locations

| File | Field | What it holds |
|------|-------|---------------|
| `config.yaml` | `api_key:` (≈18 occurrences) | The chudian LLM key used for all LLM sub-tasks. All 18 share ONE key. |
| `auth.json` | `"access_token"` | **Disk cache of the LLM key.** If this still holds the OLD key, calls fail with 401 even after config.yaml is fixed. Must be updated too. |
| `.env` | `WECOM_SECRET` | WeCom application secret for `wecom_callback`. Reset it in the WeCom admin console, not just locally. |

Note: `config.yaml`'s `wecom:` section is only `enabled: false` — the real WeCom
secret lives in `.env`. There is **no git repo** here, so a bad edit can only be
undone via reverse-sed or the backup files (`config.yaml.bak*`).

## The ONE safe sed pattern

Always replace by **value**, never by field name:

```bash
sed -i 's|OLD_VALUE|NEW_VALUE|g' /home/dmin/.hermes/FILE
```

- Use `|` as delimiter (keys never contain `|`).
- `OLD_VALUE` / `NEW_VALUE` are the **actual key strings**, so only that value is
  touched — other providers/keys are never affected.

**Anti-pattern — never use this:**
```bash
sed -i -E 's|^( *)api_key:.*|\1api_key: "NEW"|' config.yaml   # WRONG: rewrites EVERY api_key line to the same value
```

For `.env` (a `KEY=VALUE` line) use the capture-prefix form:
```bash
sed -i -E 's|^(WECOM_SECRET=).*|\1REAL_SECRET|' /home/dmin/.hermes/.env
```

## Procedure

1. **Replace the LLM key in both files** (config.yaml + auth.json cache):
   ```bash
   sed -i 's|OLD_KEY|NEW_KEY|g' /home/dmin/.hermes/config.yaml
   sed -i 's|OLD_KEY|NEW_KEY|g' /home/dmin/.hermes/auth.json
   ```
2. **Replace the WeCom secret** (only if 40001 present): reset the app Secret in the
   WeCom admin console first, then:
   ```bash
   sed -i -E 's|^(WECOM_SECRET=).*|\1REAL_SECRET|' /home/dmin/.hermes/.env
   ```
3. **Restart the gateway** (service name is `hermes-gateway.service`, NOT `hermes.service`):
   ```bash
   systemctl --user restart hermes-gateway.service
   ```
4. **Verify** (see references/cheatsheet.md for the full command list).

## Critical gotchas

- **Exit and re-open `hermes chat`.** The interactive chat process (e.g. PID started
  before the fix) caches the bad key. Restarting only the gateway is not enough —
  Ctrl+C out of chat and run `hermes chat` again before re-testing.
- **`curl` to external APIs returns `HTTP 000` inside WSL.** The WSL shell has a proxy
  (`http://172.23.96.1:7890`) that blocks direct curl. Bypass it for key checks:
  `curl --noproxy '*' ...`. A `000` is the proxy, NOT an invalid key.
- **WeCom secret must be reset in the admin console.** Editing `.env` alone is not
  enough; the source of truth is the console. Do not paste placeholder text like
  `新SECRET` — the gateway strips non-ASCII and keeps failing (`non-ASCII '新'`).
- **Architecture note:** `hermes --help` reports "企微消息端固定由阿里云端处理" — WeCom
  delivery may run in the cloud, so a local `wecom_callback` 40001 might be a redundant
  config warning rather than a hard outage. Confirm with the user whether WeCom messages
  actually break before prioritizing the fix.

## Multi-instance propagation & leak response

Hermes runs on more than one host (this local WSL2 AND an Aliyun ECS). Each host has
its own credential files — editing one does NOT propagate. After rotating a key, repeat
the edit on EVERY instance, or the leak stays open on the others.

Known instances (verify before acting):
- Local WSL2: `/home/dmin/.hermes/` (user `dmin`, `systemctl --user`)
- Aliyun ECS `47.103.27.171`: `/root/.hermes/` (user `root`). SSH from the Windows host
  works with the existing `~/.ssh/id_ed25519` (passwordless). Confirm the service restart
  command there (`systemctl --user` vs root `systemctl`, or docker/screen) via
  `ps aux | grep hermes` BEFORE restarting.

If a key was LEAKED (not just expired): do not merely move it locally.
1. Revoke the leaked key(s) in the provider console (chudian) so they stop working
   everywhere, including instances that cannot be reached immediately.
2. Generate ONE fresh key (K3).
3. Deploy K3 to ALL instances (config.yaml + auth.json on each), then restart each.
A key pasted into a chat or shared channel is also leaked — revoke it too, do not reuse it.

## Resources

- `references/cheatsheet.md` — copy-paste command list (verify, rotate, restart, debug)
  with key values shown as placeholders.
