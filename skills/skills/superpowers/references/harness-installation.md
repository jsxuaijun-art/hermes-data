# Superpowers Harness Installation

This file documents how to install or test this `meta-skills` adaptation across
the supported harnesses. Prefer local/project-level installs while testing.

More detailed operational references:

- `opencode.md` - OpenCode install, update, cache, Windows, and skill discovery behavior
- `polyglot-hooks.md` - Claude Code cross-platform hook wrapper details
- `testing.md` - static and integration test strategy

## Codex CLI

Codex plugin metadata is in `.codex-plugin/plugin.json`.

For local development, install or symlink this directory according to the Codex
CLI plugin workflow available in the current environment. The plugin's skill
root is `./skills/`, and the top-level helper skill is `superpowers`.

Validation:

```bash
python3 skills/superpowers/scripts/validate.py skills/superpowers
```

Smoke prompt:

```text
Use the superpowers skill and list the available superpowers-prefixed skills.
```

## Claude Code

Claude plugin metadata is in `.claude-plugin/plugin.json`.
For local Claude marketplace development, `.claude-plugin/marketplace.json`
exposes this package as `superpowers-dev`.

Optional hook support is provided in `hooks/hooks.json` and `hooks/session-start`.
The hook injects `superpowers-using-superpowers` at session start. Install it
only after confirming with the user because it changes session behavior.
The hook command goes through `hooks/run-hook.cmd` for Windows/macOS/Linux
compatibility. See `polyglot-hooks.md`.

Project-level install shape:

```text
.claude/
  hooks.json
  plugins/superpowers/
    SKILL.md
    skills/
    hooks/
    .claude-plugin/plugin.json
```

If installing the hook manually, ensure `CLAUDE_PLUGIN_ROOT` resolves to the
plugin directory and that `hooks/session-start` is executable.

Smoke prompt:

```text
Tell me about your superpowers.
```

## OpenCode

OpenCode plugin support is in `.opencode/plugins/superpowers.js`.
OpenCode-specific install instructions are also available at `.opencode/INSTALL.md`.

Local package install example:

```json
{
  "plugin": ["/absolute/path/to/meta-skills/skills/superpowers"]
}
```

The plugin registers `skills/` as a skill path and injects the
`superpowers-using-superpowers` bootstrap content once per session.
Some OpenCode and Bun versions cache git-backed plugin packages; if updates do
not appear after restart, clear the cache or reinstall. Windows builds can also
have `git+https` package resolution issues; see `opencode.md`.

Smoke prompt:

```text
use skill tool to list skills
use skill tool to load superpowers/superpowers-using-superpowers
```

## Notes For Agents

- Keep all bundled skill names prefixed with `superpowers-`.
- Keep upstream attribution in `SKILL.md`, plugin metadata, and license copy.
- Do not add broad global hooks unless the user explicitly asks for them.
- Preserve operational references when changing hooks, OpenCode plugin behavior,
  or test strategy.
