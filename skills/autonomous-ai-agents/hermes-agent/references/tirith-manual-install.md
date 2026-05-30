# Tirith Manual Install

Tirith (`sheeki03/tirith`) is a command-level security scanner for terminal threats (homograph URLs, pipe-to-interpreter, injection). Hermes auto-installs it as a background thread on first use, but this can fail on slow/unreliable networks (GitHub release S3 CDN timeouts).

## Symptom

- Logs show: `tirith not found — downloading latest release for x86_64-unknown-linux-gnu...` followed by a timeout or `download_failed`
- Config has `tirith_enabled: true` but Hermes falls back to pattern matching
- Marker file `~/.hermes/.tirith-install-failed` exists with reason `download_failed`

## Manual Install

```bash
# 1. Find the right asset for your platform from latest release
#    https://github.com/sheeki03/tirith/releases/latest
#    Linux x86_64: tirith-x86_64-unknown-linux-gnu.tar.gz
#    macOS x86_64: tirith-x86_64-apple-darwin.tar.gz
#    macOS ARM:    tirith-aarch64-apple-darwin.tar.gz
#    Linux ARM:    tirith-aarch64-unknown-linux-gnu.tar.gz

# 2. Download (use a generous timeout — 5+ min for slow connections)
curl -sL --max-time 300 \
  "https://github.com/sheeki03/tirith/releases/download/v0.3.0/tirith-x86_64-unknown-linux-gnu.tar.gz" \
  -o /tmp/tirith.tar.gz

# 3. Extract and install
cd ~/.hermes/bin
tar xzf /tmp/tirith.tar.gz
chmod +x tirith
rm /tmp/tirith.tar.gz

# 4. Verify
~/.hermes/bin/tirith --help
~/.hermes/bin/tirith check "echo hello"

# 5. Clear the failure marker so Hermes stops treating it as broken
rm -f ~/.hermes/.tirith-install-failed

# 6. Set tirith_path to absolute path in config.yaml
hermes config set security.tirith_path /root/.hermes/bin/tirith
```

## Restart Required

Changes take effect on next Hermes restart (`/reset` in CLI, or `/restart` in gateway).

## Config Defaults

From `security` section of config.yaml:

```yaml
security:
  tirith_enabled: true
  tirith_path: tirith           # default: search PATH; best: absolute path after manual install
  tirith_timeout: 5             # seconds per scan
  tirith_fail_open: true        # allow commands if tirith itself fails
```
