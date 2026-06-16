---
name: apple
platforms: [macos]
description: macOS Apple ecosystem tools — Notes, Reminders, Find My (AirTags/devices), and iMessage. All require macOS with Homebrew and specific CLI tools.
version: 1.0.0
metadata:
  hermes:
    tags: [apple, macos, notes, reminders, findmy, imessage, messaging, tracking]
    related_skills: []
---

# Apple Ecosystem Tools (macOS)

## Overview

These tools use macOS-native CLIs (installed via Homebrew) to interact with Apple's ecosystem. All require a Mac with the relevant Apple apps signed in.

| Tool | App | CLI | Purpose | Reference |
|------|-----|-----|---------|-----------|
| **Notes** | Notes.app | `memo` | Create, search, edit Apple Notes | `references/apple-notes.md` |
| **Reminders** | Reminders.app | `remindctl` | Add, list, complete reminders | `references/apple-reminders.md` |
| **Find My** | FindMy.app | AppleScript | Track devices & AirTags | `references/findmy.md` |
| **iMessage** | Messages.app | `imsg` | Send & receive iMessages/SMS | `references/imessage.md` |

## Common Prerequisites

- **macOS** with the relevant Apple apps signed into iCloud
- **Homebrew** for installing CLI tools
- **System permissions** may need granting:
  - Full Disk Access for terminal (Messages)
  - Automation permission (Notes, FindMy)
  - Screen Recording permission (FindMy)

## Quick Reference

| Action | Notes | Reminders | FindMy | iMessage |
|--------|-------|-----------|--------|----------|
| List items | `memo notes` | `remindctl all` | Open app + screenshot | `imsg chats` |
| Create | `memo notes -a "Title"` | `remindctl add` | N/A | `imsg send` |
| Search | `memo notes -s "q"` | `remindctl list` | Vision on screenshot | `imsg history` |
| Configure | `brew install memo` | `brew install remindctl` | Screen Recording prefs | `brew install imsg` |

## See Also

- `references/apple-notes.md` — full Notes skill (folder management, export)
- `references/apple-reminders.md` — full Reminders skill (lists, dates, priorities)
- `references/findmy.md` — full Find My skill (screen capture, peekaboo)
- `references/imessage.md` — full iMessage skill (send, history, attachments)
