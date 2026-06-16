# Classic CLI (prompt_toolkit) — Internal Reference

> Where hardcoded prompt_toolkit settings live and how to make them config-driven.

## Application Creation

The prompt_toolkit `Application` is created **inside** `HermesCLI.run()` in `cli.py`, around **line 11088**:

```python
app = Application(
    layout=layout,
    key_bindings=kb,
    style=style,
    full_screen=False,
    mouse_support=self.mouse_support,   # ← was hardcoded False
    **({'cursor': _STEADY_CURSOR} if _STEADY_CURSOR is not None else {}),
)
```

This is a large method (~1600 lines from `def run(self):` at line 9530). The Application constructor call is its final piece — everything above builds the layout, key bindings, and style dict.

## Pattern: Externalizing a Hardcoded Setting

### Step 1 — Add default in `hermes_cli/config.py`

```python
DEFAULT_CONFIG = {
    "display": {
        "mouse_support": False,  # or True
        # ... other display keys
    },
}
```

### Step 2 — Read in `HermesCLI.__init__` (cli.py ~line 1905)

```python
self.mouse_support = CLI_CONFIG["display"].get("mouse_support", False)
```

Place it near sibling display settings (compact, bell_on_complete, show_reasoning, etc.).

### Step 3 — Use in Application constructor

Replace the hardcoded value with `self.mouse_support`.

### Step 4 — Restart

Config is read at startup. In CLI: exit and relaunch. In gateway: `/restart`.

## How `mouse_support` Works

prompt_toolkit's `mouse_support=True` enables:
- **Left-click** → positions cursor in the input area
- **Right-click** → pastes clipboard content (Windows Terminal default behavior)
- **Mouse wheel** → scrolls through output

When `mouse_support=False` (the old default), prompt_toolkit sends escape sequences to **disable** mouse tracking (DEC private mode 1000), and raw mouse events pass through to the terminal emulator instead. This prevents accidental cursor jumps but also blocks click-to-position.

Tradeoff with gateways: mouse support only matters for the interactive CLI. Gateway sessions (Telegram, Discord, etc.) don't use prompt_toolkit — they dispatch via `gateway/run.py` directly.

## Other Hardcoded prompt_toolkit Parameters

The `Application()` constructor supports many parameters not yet exposed via config:

| Parameter | Current status | Suggested config key |
|-----------|---------------|---------------------|
| `mouse_support` | ✅ Now `display.mouse_support` | — |
| `full_screen` | Hardcoded `False` | Usually correct |
| `cursor` | Built from `_STEADY_CURSOR` | Rarely needs changing |
| Key bindings | Built inline in `run()` | Config for custom shortcuts? |
| `style` | Built from `_build_tui_style_dict()` | Skin system |
| `min_redraw_interval` | Not set | Could go under `display` |

## Finding Other Hardcoded Values

```bash
# Search for prompt_toolkit imports
grep -r "from prompt_toolkit" cli.py

# Search for Application parameters that could be config-driven
grep -n "Application(" cli.py

# Find all hardcoded boolean config candidates
grep -n "=\s*False\|=\s*True" cli.py | grep -v "self\." | grep -v "CLI_CONFIG" | head -20
```

## Key Files

| File | Purpose |
|------|---------|
| `cli.py` (line ~9530) | `HermesCLI.run()` — builds Application |
| `cli.py` (line ~1905) | `HermesCLI.__init__()` — reads config |
| `hermes_cli/config.py` (line ~731) | `DEFAULT_CONFIG["display"]` section |
| `agent/display.py` | Spinner, activity feed, output formatting (not prompt_toolkit) |
