# install.ps1 - Prints setup instructions for Windows PowerShell users
# No automatic modification of settings.json

[CmdletBinding()]
param(
    [ValidateSet("claude", "cc", "codex", "hermes")]
    [string]$Target = "claude"
)

$SkillDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

switch ($Target.ToLower()) {
    { $_ -in @("claude", "cc") } {
        @"
===========================================
 Claude Memory & Reminder Skill - Installer (Claude Code)
===========================================

This script only prints manual steps. It will NOT modify your
~/.claude/settings.json automatically.

Skill location: $SkillDir

-------------------------------------------
Step 1. Deploy the hook script (run in Git Bash / WSL)
-------------------------------------------

  mkdir -p ~/.claude/hooks
  cp "$SkillDir/hooks/session-start.sh" ~/.claude/hooks/
  chmod +x ~/.claude/hooks/session-start.sh

Note: Claude Code on Windows uses bash syntax inside hooks.
      Run these commands in Git Bash or WSL, NOT PowerShell.

-------------------------------------------
Step 2. Register the hook in settings.json
-------------------------------------------

Open ``C:\Users\<you>\.claude\settings.json`` and add this block
under the top-level object (merge with existing keys):

  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          { "type": "command", "command": "bash ~/.claude/hooks/session-start.sh" }
        ]
      }
    ]
  }

-------------------------------------------
Step 3. Initialize a project's memory folder
-------------------------------------------

Find your project's memory folder at:
  ``C:\Users\<you>\.claude\projects\<PROJECT>\memory\``

Copy the template files:
  Copy-Item "$SkillDir\templates\MEMORY.md"    "C:\Users\<you>\.claude\projects\<PROJECT>\memory\"
  Copy-Item "$SkillDir\templates\reminders.md" "C:\Users\<you>\.claude\projects\<PROJECT>\memory\"

Then fill in User Info / Preferences in MEMORY.md.

-------------------------------------------
Step 4. (Optional) Customize parameters
-------------------------------------------

  Copy-Item "$SkillDir\config.example.json" "$SkillDir\config.json"
  # Edit config.json

-------------------------------------------
Step 5. Verify
-------------------------------------------

Start a new Claude Code session. Claude should print a tier-check report
before answering your first message.
"@
    }
    "codex" {
        @"
===========================================
 Memory & Reminder - Installer (Codex CLI)
===========================================

Codex has NO SessionStart hook, so this skill works as an AGENTS.md
"Session Startup" instruction that the main agent executes itself.

Skill location: $SkillDir

-------------------------------------------
Step 1. Add the startup fragment to AGENTS.md
-------------------------------------------

Open this file:

  $SkillDir\codex\agents-md-startup-fragment.md

Copy its '## 1. Session Startup' block into your ~/.codex/AGENTS.md
section 1. If your AGENTS.md does not have a section 1 yet, insert
the entire block.

-------------------------------------------
Step 2. Deploy memory templates (run in Git Bash / WSL or PowerShell)
-------------------------------------------

PowerShell:
  New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.codex\memories" | Out-Null
  Copy-Item "$SkillDir\templates\MEMORY.md"    "$env:USERPROFILE\.codex\memories\MEMORY.md"
  Copy-Item "$SkillDir\templates\reminders.md" "$env:USERPROFILE\.codex\memories\reminders.md"

Git Bash:
  mkdir -p ~/.codex/memories
  cp "$SkillDir/templates/MEMORY.md" ~/.codex/memories/MEMORY.md
  cp "$SkillDir/templates/reminders.md" ~/.codex/memories/reminders.md

Fill in MEMORY.md User Info / Preferences blocks.

-------------------------------------------
Step 3. Verify
-------------------------------------------

Start a new codex session. The main agent should:
  - First time (no stamp): print full tier-check REQUIRED report
  - Within 8h: print one-line SKIP and answer directly
  - After 8h: REQUIRED again

See $SkillDir\codex\README.md for full details and the difference
matrix vs Claude Code.
"@
    }
    "hermes" {
        @"
Hermes platform support is not yet implemented (TODO for v0.3.0).
Hermes lacks a public SessionStart hook mechanism. If you have details
on how to inject a startup instruction in your Hermes deployment,
please open an issue at:

  https://github.com/moyunliuyin/claude-memory-reminder/issues
"@
        exit 1
    }
}
