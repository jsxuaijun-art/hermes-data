# Installing the Browser Use CLI on Hermes (China-network, non-interactive)

Session that produced this: manager asked about the `"Browser Use CLI not found"` startup
note, chose to install the CLI (not just silence it).

## Why the note appears

`browser.backend: ""` (the default in `~/.hermes/config.yaml`) means **"Browser Use mode
whenever the CLI is runnable."** Hermes checks for the `browser-use` binary at startup; if
absent it falls back to the built-in `browser_*` CDP tools and prints the notice. It is a
notice, not an error. Alternatives:
- Install the CLI (this doc).
- Set `browser.backend: off` in config.yaml to silence it and stay on built-in browser tools.

## Install command (works in a non-interactive/scripted terminal)

The `hermes tools` curses UI cannot be driven from a script. `hermes_cli/tools_config.py:1666`
shows `hermes tools` → Browser → `post_setup: browser_use_cli` → calls
`tools.browser_use_cli.install_cli()`. Call that function directly instead. It:
1. Uses `hermes_cli.managed_uv.ensure_uv()` to bootstrap Hermes' own `uv` into
   `$HERMES_HOME/bin` if needed (no manual uv install required).
2. Runs `uv tool install browser-use` with `UV_TOOL_BIN_DIR=$HERMES_HOME/bin`.
3. Links the binary to `$HERMES_HOME/bin/browser-use`.

```bash
# MUST export mirror vars in the SAME shell, or uv stalls on slow China networks
export UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
export PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
cd ~/.hermes/hermes-agent
/usr/bin/python3 -c "
import sys; sys.path.insert(0, '.')
from tools.browser_use_cli import install_cli, _find_cli
print('BEFORE:', _find_cli())
ok, msg = install_cli(timeout_s=1500)   # 600s default can be too short for slow mirror bootstrap
print('RESULT:', ok, msg)
print('AFTER:', _find_cli())
"
```

**Timing:** first-run bootstrap + PyPI install can exceed the 180s foreground timeout. Run the
Python as a **background** terminal task (`background=true, notify_on_complete=true`) and wait,
or set the inner `timeout_s` generously (1500 used here). Add `--debug` if it stalls.

**Result observed:** `RESULT ok: True`, binary at `~/.hermes/bin/browser-use`, version 0.1.8.

## Resolution order (managed-first)

`_find_cli()` probes, in order: `$HERMES_HOME/bin` → PATH → `~/.local/bin` → `uvx browser-use`
(dispensed). Managed-copy-first means a user-level side install on PATH does NOT satisfy the
install check — only the `$HERMES_HOME/bin` copy short-circuits `install_cli()`.

## Verification

```bash
~/.hermes/bin/browser-use --version     # e.g. 0.1.8
```
The binary is a symlink into `~/.local/share/uv/tools/browser-use/bin/browser-use`.

## Pitfalls

- **Tool/backend changes apply on a NEW session only** — user must exit and relaunch `hermes`.
  The current session keeps using the old browser backend; the startup notice disappears after
  the restart.
- **Cloud vs local:** Browser Use *cloud* sessions need `browser-use auth login` or
  `BROWSER_USE_API_KEY`; *local* browser automation works with zero extra config.
- The provider subprocess env strips `PYTHONPATH`/`PYTHONHOME` (ABI-mismatch guard — see
  `_base_subprocess_env()`). The CLI runs under its own uv-tool Python, not Hermes' venv.
