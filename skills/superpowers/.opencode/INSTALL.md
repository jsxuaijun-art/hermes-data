# Installing This Superpowers Pack For OpenCode

This file adapts upstream `obra/superpowers/.opencode/INSTALL.md` for the
`meta-skills` version, where bundled skills are named `superpowers-*`.

## Prerequisites

- OpenCode installed.
- This directory available locally or through a git package source.

## Installation

For local development, add this package directory to the `plugin` array in your
global or project-level `opencode.json`:

```json
{
  "plugin": ["/absolute/path/to/meta-skills/skills/superpowers"]
}
```

Restart OpenCode. The plugin registers `skills/` through OpenCode's config hook.

Verify:

```text
use skill tool to list skills
use skill tool to load superpowers/superpowers-using-superpowers
```

OpenCode uses its own plugin install path. If you also use Claude Code or Codex
CLI, install or enable this pack separately for each harness.

## Migrating From Old Symlink-Based Installs

If an older Superpowers install used `git clone` and symlinks, remove the stale
OpenCode setup before installing this package:

```bash
rm -f ~/.config/opencode/plugins/superpowers.js
rm -rf ~/.config/opencode/skills/superpowers
rm -rf ~/.config/opencode/superpowers
```

Also remove any obsolete Superpowers `skills.paths` entry from `opencode.json`.
This package's OpenCode plugin registers the skills path itself.

## Updating

OpenCode and Bun may pin git-backed plugin specs in a lockfile or package cache.
If a restart does not pick up a new version, clear OpenCode's package cache or
reinstall the plugin.

If using a git source, pin a specific tag or commit in the plugin spec.

## Troubleshooting

### Plugin Not Loading

1. Check logs: `opencode run --print-logs "hello" 2>&1 | grep -i superpowers`
2. Verify the `plugin` entry in `opencode.json`.
3. Make sure OpenCode is recent enough to support plugin config hooks and chat message transforms.

### Windows Install Issues

Some Windows OpenCode builds have issues with git-backed plugin specs, cache
paths for `git+https` URLs, or Bun not finding `git.exe`. If git-backed install
fails, install with system npm into OpenCode's config directory and point
OpenCode at the installed local package.

### Skills Not Found

1. Use the `skill` tool to list discovered skills.
2. Check that the plugin is loading.
3. Confirm each skill has `SKILL.md` with valid YAML frontmatter.
4. Confirm this adaptation uses names like `superpowers-brainstorming`, not upstream unprefixed names.

### Tool Mapping

When skills reference Claude Code tools, map them to OpenCode equivalents:

- `TodoWrite` -> `todowrite`
- `Task` with subagents -> OpenCode subagent or `@mention` workflow
- `Skill` tool -> OpenCode native `skill` tool
- file operations -> native OpenCode tools
