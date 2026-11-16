---
name: superpowers
description: Use when installing, testing, adapting, or invoking the Superpowers methodology in this skills collection. Provides the superpowers-prefixed skill library, harness setup guidance for OpenCode, Codex CLI, and Claude Code, and validation checks.
version: 5.1.0-meta.1
user-invocable: true
source: https://github.com/obra/superpowers
license: MIT
---

**Korean:** See `SKILL.ko.md` for the Korean version.

# Superpowers Skill Pack

This is a meta-skills adaptation of Jesse Vincent's Superpowers project.
All bundled workflow skills are prefixed with `superpowers-` so their origin is
clear inside mixed skill collections.

## What Is Included

Core workflow skills live under `skills/`:

- `superpowers-using-superpowers`
- `superpowers-brainstorming`
- `superpowers-using-git-worktrees`
- `superpowers-writing-plans`
- `superpowers-subagent-driven-development`
- `superpowers-executing-plans`
- `superpowers-test-driven-development`
- `superpowers-systematic-debugging`
- `superpowers-verification-before-completion`
- `superpowers-requesting-code-review`
- `superpowers-receiving-code-review`
- `superpowers-dispatching-parallel-agents`
- `superpowers-finishing-a-development-branch`
- `superpowers-writing-skills`

## Use In This Repository

When a user asks for Superpowers behavior, load the most specific prefixed
skill. Use `superpowers-using-superpowers` only as the bootstrap/orientation
skill.

Do not silently install hooks into a user's global agent configuration. If hooks
are useful, read `references/harness-installation.md`, explain the exact files
that would change, and get approval before writing outside the current
workspace.

## Harness Support

This pack includes metadata and setup guidance for:

- Codex CLI: `.codex-plugin/plugin.json`
- Claude Code: `.claude-plugin/plugin.json` plus optional session-start hook
- OpenCode: `.opencode/plugins/superpowers.js`

Read `references/harness-installation.md` when the task is installation,
hook setup, troubleshooting, or cross-harness packaging.

Operational details are split into focused references:

- `references/opencode.md` for OpenCode install, update, cache, Windows, and tool mapping behavior
- `references/polyglot-hooks.md` for Claude Code cross-platform hook behavior
- `references/testing.md` for static and integration test strategy

## Validation

Run the structural checks after editing this pack:

```bash
python3 skills/superpowers/scripts/validate.py skills/superpowers
```

The validator checks frontmatter names, required plugin files, hook references,
OpenCode bootstrap paths, operational references, and accidental unprefixed
bundled skill names.

## Upstream Attribution

Original project: <https://github.com/obra/superpowers>

Author: Jesse Vincent

License: MIT. A copy is stored in `references/UPSTREAM-LICENSE`.
