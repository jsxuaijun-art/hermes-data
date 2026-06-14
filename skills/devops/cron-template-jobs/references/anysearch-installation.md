# AnySearch Multi-Environment Deployment Reference

## API Key
- Key: `as_sk_cf46eaaeec4776778b29da489e8f9c1b`
- Registration: https://anysearch.com/console/api-keys
- Type: Free tier (anonymous access available, key provides higher rate limits)
- Anonymous vs key: Anonymous works but has "lower rate limits" (unpublished). Key does NOT affect free tier — it just identifies you and grants higher quota.
- **Bound to all 3 environments on:** 2026-05-31

## WSL Local
- **Config path:** `~/.hermes/skills/anysearch/.env`
- **Contents:** `ANYSEARCH_API_KEY=as_sk_cf46eaaeec4776778b29da489e8f9c1b`
- **File size:** 57 bytes

## Windows Hermes Desktop
- **Config path:** `/mnt/c/Users/jsxuaijun/AppData/Local/hermes/skills/anysearch/.env`
- **Note:** This is the `AppData/Local/hermes/` path, NOT `AppData/Roaming/` or user home `.hermes/`

## Alibaba Cloud (47.103.27.171)
- **Config path:** `/root/.hermes/skills/anysearch/.env`
- **Contents:** Same key
- **Write method used:** base64-encoded echo via SSH (to avoid shell expansion of `$`, backticks, etc.)
- **Alibaba Cloud CAN reach `api.anysearch.com`** — tested via direct API call, returns Status 200. No VPN or special network config needed.

## Verification
```bash
# Run a search test (any environment)
python3 ~/.hermes/skills/anysearch/scripts/anysearch_cli.py search "财税政策" --max_results 2 --zone cn

# SSH ping test from Alibaba Cloud
ssh root@47.103.27.171 'python3 -c \
  "import requests; r = requests.post(\"https://api.anysearch.com/mcp\", timeout=15); print(r.status_code)"'
```

## Notes
- Anonymous search works on all three environments
- The `--zone cn` flag produces Chinese-language results (relevant for tax/finance queries)
- AnySearch API endpoint is `https://api.anysearch.com/mcp` (AWS CloudFront, Tokyo edge)
- Key written via base64 encoding to prevent shell expansion truncation
