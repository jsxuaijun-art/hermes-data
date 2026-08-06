---
name: debugging
category: software-development
description: Runtime-specific debugging tools for Node.js, Python, and Hermes TUI — breakpoints, remote attach, Chrome DevTools Protocol, and pdb. For the systematic debugging methodology (root cause analysis), see the `systematic-debugging` skill instead.
version: 1.0.0
metadata:
  hermes:
    tags: [debugging, nodejs, python, tui, breakpoints, pdb, inspect, cdp]
    related_skills: [systematic-debugging]
---

# Runtime Debugging Tools

## Overview

Runtime-specific debugging tools organized by language/runtime. Each reference file gives you exact commands for breakpoints, stepping, scope inspection, and remote attach.

| Runtime | Tool | Use for | Reference |
|---------|------|---------|-----------|
| **Python** | `pdb` / `debugpy` | Local breakpoints, remote attach, post-mortem | `references/python-debugpy.md` |
| **Node.js** | `node inspect` / CDP | V8 inspector REPL, Chrome DevTools Protocol | `references/node-inspect-debugger.md` |
| **Hermes TUI** | Gateway + Ink | Debug slash commands across Python/TypeScript layers | `references/debugging-hermes-tui-commands.md` |

## Quick Decision Flow

```
What is the bug in?
├── Python code
│   ├── Quick check → breakpoint() + run
│   └── Remote/long-running → debugpy + attach
├── Node.js / TypeScript code
│   └── node inspect <script>  (or --inspect-brk for tsx)
└── Hermes TUI slash commands
    └── Check 3-layer stack: Python registry → gateway → Ink frontend
```

## Systematic Methodology

For **root cause analysis**, not runtime-specific tool commands, use the `systematic-debugging` skill. That skill covers the 4-phase process (understand → reproduce → isolate → verify) that applies across all runtimes. This umbrella skill covers the **tool commands** — the "how to set a breakpoint" part.

## See Also

- `references/python-debugpy.md` — pdb REPL, debugpy remote/DAP, post-mortem
- `references/node-inspect-debugger.md` — node inspect, CDP automation, CPU profiles
- `references/debugging-hermes-tui-commands.md` — Hermes TUI 3-layer architecture, sync issues
- `systematic-debugging` — the process methodology (separate skill, not a reference)
