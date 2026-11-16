# Cross-Platform Polyglot Hooks For Claude Code

This reference preserves upstream operational guidance for Claude Code hooks on
Windows, macOS, and Linux.

## Problem

Claude Code hook commands run through the system default shell:

- Windows: `cmd.exe`
- macOS/Linux: `bash` or `sh`

That creates portability problems:

1. Windows `cmd.exe` cannot execute `.sh` files directly.
2. Windows and Unix paths use different separators.
3. `$VAR` environment syntax does not work in CMD.
4. Git Bash may be installed but not available in CMD's `PATH`.

## Solution: `.cmd` Wrapper

Use a wrapper that can be entered from Windows CMD and from Unix shells. This
adaptation keeps `hooks/run-hook.cmd` as the cross-platform entry point and
`hooks/session-start` as the bash implementation.

The hook config points at the wrapper:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd\" session-start",
            "async": false
          }
        ]
      }
    ]
  }
}
```

Quote the path because plugin roots can contain spaces.

## Requirements

Windows:

- Git for Windows or another bash provider must be installed.
- `run-hook.cmd` searches common Git Bash locations and then `bash` on `PATH`.
- If no bash is found, the hook prints an error; the plugin can still exist, but
  session-start context injection will not work.

macOS/Linux:

- Standard shell environment.
- Hook wrapper and script should be executable.

## Writing Portable Hook Logic

Prefer:

- pure bash builtins where practical
- `$(command)` instead of backticks
- quoted variable expansions
- `printf` for JSON output
- explicit JSON escaping

Avoid relying on external tools that may not exist in the hook environment. If
external tools are unavoidable, remember that Windows hook execution may happen
through Git Bash rather than the user's normal interactive shell.

## JSON Output Shape

For Claude Code `SessionStart`, emit:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "<context>"
  }
}
```

This adaptation emits that shape when `CLAUDE_PLUGIN_ROOT` is set. Unknown
platforms fall back to top-level `additionalContext`.

## Troubleshooting

### Bash Is Not Recognized

Install Git for Windows or put bash on PATH. The wrapper also checks standard
Git Bash installation locations.

### Script Opens In A Text Editor

The hook config likely points directly at a shell script. Point it at
`hooks/run-hook.cmd`.

### Paths Look Wrong

Convert Windows paths before passing them to bash, or let the wrapper resolve
the script directory.

### Works In Terminal But Not As Hook

Simulate the hook environment:

```powershell
$env:CLAUDE_PLUGIN_ROOT = "C:\path\to\plugin"
cmd /c "C:\path\to\plugin\hooks\run-hook.cmd session-start"
```

On Unix:

```bash
CLAUDE_PLUGIN_ROOT=/path/to/plugin hooks/run-hook.cmd session-start
```
