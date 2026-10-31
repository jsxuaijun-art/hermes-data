# Superpowers For OpenCode

This reference preserves the operational guidance from upstream
`docs/README.opencode.md`, adjusted for this `superpowers-*` adaptation.

## Installation

Add this package to the `plugin` array in global or project-level
`opencode.json`:

```json
{
  "plugin": ["/absolute/path/to/meta-skills/skills/superpowers"]
}
```

Restart OpenCode. The plugin installs or loads through OpenCode's plugin system
and registers all bundled skills.

Verify:

```text
use skill tool to list skills
use skill tool to load superpowers/superpowers-using-superpowers
```

Install separately per harness. Installing for Claude Code or Codex CLI does not
automatically install for OpenCode.

## Migrating From Old Symlinks

Remove old OpenCode Superpowers symlinks and cloned copies:

```bash
rm -f ~/.config/opencode/plugins/superpowers.js
rm -rf ~/.config/opencode/skills/superpowers
rm -rf ~/.config/opencode/superpowers
```

Also remove obsolete `skills.paths` entries for Superpowers from `opencode.json`.
The plugin now registers its own skills path.

## Personal And Project Skills

OpenCode can also load personal and project skills:

- personal: `~/.config/opencode/skills/`
- project: `.opencode/skills/`

Priority: project skills > personal skills > Superpowers skills.

## Updating

OpenCode installs git-backed packages through Bun. Some versions pin the
resolved dependency in a lockfile or cache, so restarting may not pick up the
newest commit. Clear OpenCode's package cache or reinstall if updates do not
appear.

When using a git source, pin a version with `#tag` or `#commit`.

## How It Works

The OpenCode plugin does two things:

1. Registers this package's `skills/` directory through a config hook.
2. Injects `superpowers-using-superpowers` bootstrap context into the first user
   message of a session, guarded against duplicate injection.

This adaptation uses `experimental.chat.messages.transform` and caches the
bootstrap content in module scope to avoid repeated disk reads.

## Tool Mapping

- `TodoWrite` -> `todowrite`
- `Task` with subagents -> OpenCode subagent or `@mention` workflow
- `Skill` tool -> OpenCode native `skill` tool
- `Read`, `Write`, `Edit`, `Bash` -> native file and shell tools

## Troubleshooting

### Plugin Not Loading

1. Check logs: `opencode run --print-logs "hello" 2>&1 | grep -i superpowers`
2. Verify the plugin line in `opencode.json`.
3. Confirm OpenCode is recent enough for plugin config hooks and chat transforms.

### Windows Install Issues

Some Windows builds have issues with git-backed specs, cache paths for
`git+https` URLs, or Bun not finding `git.exe`. If that happens, install with
system npm into OpenCode's config directory and point OpenCode at the local
package path.

### Skills Not Found

1. Use OpenCode's `skill` tool to list available skills.
2. Check that the plugin is loading.
3. Confirm every skill has a valid `SKILL.md`.
4. Remember this adaptation's skill names are prefixed, for example
   `superpowers-brainstorming`.

### Bootstrap Not Appearing

1. Restart OpenCode after config changes.
2. Confirm `.opencode/plugins/superpowers.js` can read
   `skills/superpowers-using-superpowers/SKILL.md`.
3. Check that the first user message has not already been transformed.
