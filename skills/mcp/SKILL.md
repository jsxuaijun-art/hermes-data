---
name: mcp
category: devops
description: Model Context Protocol (MCP) client management — config servers in Hermes Agent for auto-discovered tools, or call tools ad-hoc from terminal via mcporter.
version: 1.0.0
metadata:
  hermes:
    tags: [mcp, model-context-protocol, servers, tools, integrations]
    related_skills: []
---

# MCP (Model Context Protocol)

## Overview

Two complementary approaches for working with MCP servers from Hermes:

| Approach | When to use | Reference |
|----------|-------------|-----------|
| **Native MCP client** | Permanent server config in `config.yaml` — tools auto-discovered at startup, appear alongside built-in tools | `references/native-mcp.md` |
| **mcporter** | Ad-hoc, one-off MCP tool calls from terminal; no config needed | `references/mcporter.md` |

## Choose Your Approach

- **For permanent setup** (tools you use every session): Configure servers in `~/.hermes/config.yaml` under `mcp_servers:`. Restart Hermes Agent to discover tools automatically.
- **For one-off calls** (exploring a new server, testing an endpoint): Use `npx mcporter` from the terminal — no config needed.
- **For both**: Set up permanent servers in config.yaml, and use mcporter for exploration and debugging.

## Quick Start — Native MCP

```yaml
# ~/.hermes/config.yaml
mcp_servers:
  time:
    command: "uvx"
    args: ["mcp-server-time"]
```

Then restart Hermes — the `time` server's tools appear as first-class tools.

## Quick Start — mcporter

```bash
npx mcporter list                          # List configured servers
npx mcporter call <server.tool> key=value   # Call a tool
npx mcporter list --http-url <url> --name s # Connect ad-hoc
```

## See Also

- `references/native-mcp.md` — full native client docs (install, config format, troubleshooting)
- `references/mcporter.md` — full mcporter CLI docs (auth, call syntax, type generation)
