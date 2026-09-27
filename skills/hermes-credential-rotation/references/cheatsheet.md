# Hermes Credential Rotation — Command Cheatsheet

All commands run **inside the WSL2 Ubuntu shell** (enter via `wsl` in PowerShell, or
open the "Ubuntu" app). Never run these in Windows PowerShell — `sed` and
`/home/dmin/...` paths are Linux-only.

Replace placeholders:
- `OLD_KEY` = the leaked/expired key (e.g. `sk-ag-4fe1e7d...`)
- `NEW_KEY` = the fresh key from the provider console (e.g. `sk-ag-a55f4...`)
- `REAL_SECRET` = the WeCom app Secret copied from the admin console (pure ASCII)

---

## 1. Locate what needs changing

```bash
# count distinct LLM keys in config.yaml (expect 1 after a clean rotation)
grep -in "api_key" /home/dmin/.hermes/config.yaml | grep -o 'sk-ag-[a-z0-9]*' | sort | uniq -c

# check whether the OLD key is still cached in auth.json (expect 0 after fix)
grep -c "OLD_KEY" /home/dmin/.hermes/auth.json

# show the WeCom secret line (value masked)
grep -n "WECOM_SECRET" /home/dmin/.hermes/.env | sed -E 's/(WECOM_SECRET[[:space:]]*=[[:space:]]*).*/\1***REDACTED***/'
```

## 2. Rotate the LLM key (config.yaml + auth.json cache)

```bash
sed -i 's|OLD_KEY|NEW_KEY|g' /home/dmin/.hermes/config.yaml
sed -i 's|OLD_KEY|NEW_KEY|g' /home/dmin/.hermes/auth.json
```

## 3. Rotate the WeCom secret (only if errcode 40001 appears)

Reset the app Secret in the WeCom admin console first, then:

```bash
sed -i -E 's|^(WECOM_SECRET=).*|\1REAL_SECRET|' /home/dmin/.hermes/.env
```

## 4. Restart the gateway

```bash
systemctl --user restart hermes-gateway.service
```

(Service is `hermes-gateway.service`, not `hermes.service`.)

## 5. Verify

```bash
# gateway health (expect HTTP 200)
curl -s -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1:8642/health

# direct key check — MUST bypass the WSL proxy (else HTTP 000)
curl -s --noproxy '*' -w "\nHTTP %{http_code}\n" https://llm.chudian.site/v1/chat/completions \
  -H "Authorization: Bearer NEW_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-v4-flash","messages":[{"role":"user","content":"hi"}],"max_tokens":10}'

# gateway logs — should show no 403/401/40001 after fix
journalctl --user -u hermes-gateway.service -n 50 --no-pager | grep -i "403\|401\|40001\|expired\|invalid"
```

## 6. Final real-world test

```bash
# Ctrl+C out of any running chat, then re-enter so the new key is loaded:
hermes chat
# send a message; a normal reply means the rotation succeeded.
```

---

## Undo (no git available)

To revert a bad edit, reverse the substitution:

```bash
sed -i 's|NEW_KEY|OLD_KEY|g' /home/dmin/.hermes/config.yaml
sed -i 's|NEW_KEY|OLD_KEY|g' /home/dmin/.hermes/auth.json
```

Or fall back to a backup file: `config.yaml.bak*`, `.curator_backups`, `backup-sqlite-*`.

## Security note

After any leak, rotate the key in the provider console and update BOTH `config.yaml`
and `auth.json`. Never paste live keys into shared chats.

---

## 7. Aliyun cloud instance (separate from local WSL2)

The cloud Hermes runs on a different host and must be rotated independently — changing
the local key does NOT sync to the cloud.

- Host: `47.103.27.171` (SSH reachable from the local machine via `root@`, key-based auth)
- Config dir: `/root/.hermes/` (NOT `/home/dmin/.hermes/`)
- Gateway is a **system-level** systemd service (root), so use `systemctl` WITHOUT `--user`

```bash
# locate from local machine (read-only)
ssh root@47.103.27.171 'grep -rhoE "sk-ag-[a-z0-9]+" /root/.hermes/config.yaml /root/.hermes/auth.json | sort | uniq -c'

# rotate on the cloud (same safe value-substitution pattern)
ssh root@47.103.27.171 'sed -i "s|OLD_KEY|NEW_KEY|g" /root/.hermes/config.yaml /root/.hermes/auth.json'

# restart (system scope — no --user)
ssh root@47.103.27.171 'systemctl restart hermes-gateway.service && sleep 3 && curl -s -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1:8642/health'

# verify no 403/401 (cloud has no --user either)
ssh root@47.103.27.171 'journalctl -u hermes-gateway.service -n 30 --no-pager | grep -iE "403|401|expired|invalid"'
```

Other cloud services on the same host (for reference, not part of key rotation):
`hermes-wsl-manager.service`, `wecom-bridge.service`, `hermes-diag.service`.

> Note: the cloud gateway self-heals via systemd — after `systemctl restart` a fresh
> PID picks up the new key, so no manual process kill is needed.
