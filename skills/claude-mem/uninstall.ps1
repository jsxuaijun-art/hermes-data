# uninstall.ps1 - Prints manual uninstall steps for Windows PowerShell users

@"
===========================================
 Claude Memory & Reminder Skill - Uninstall
===========================================

Run the following manually:

  # 1. Remove the hook script
  Remove-Item -Force "$env:USERPROFILE\.claude\hooks\session-start.sh"

  # 2. Remove the cooldown stamp file
  Remove-Item -Force "$env:USERPROFILE\.claude\memory\.last-reminded"

  # 3. Edit settings.json and remove the hook registration
  notepad "$env:USERPROFILE\.claude\settings.json"

  # 4. Optional: delete this skill directory
  Remove-Item -Recurse -Force "$env:USERPROFILE\.claude\skills\claude-memory-reminder"

Your MEMORY.md / reminders.md files stay untouched - they are your data.
"@
