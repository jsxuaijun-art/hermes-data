---
name: windows-user-file-transfer
description: "Handles Windows users who cannot upload local files (C:/D: drives) to the remote Hermes agent. The agent runs on a remote Linux server and cannot access the user's local Windows filesystem."
tags:
  - windows
  - file-transfer
  - local-files
  - cli
---

# Windows User File Transfer

## Trigger

User mentions a local path like `C:\xxx`, `D:\xxx`, or asks to "upload a file" or "read a folder."

## Core Constraint

`read_file`, `write_file`, and terminal all execute on the **remote Linux server** — they cannot access the user's local Windows filesystem. Direct attempts with `read_file("D:/path")` or `terminal("dir D:")` will fail.

## Alternative Methods (priority order)

### 1. User pastes content directly
Best for text files (TXT, code, CSV snippets, Word text).

Script: "I can't access your local files directly -- Hermes runs on a remote server. Just paste the file content into the chat."

### 2. File sharing service / URL
If the user can upload to a web URL (cloud storage, internal system, webpage), use `web_extract` or `browser_navigate` to fetch it.

### 3. Local agent/tool (e.g. WorkBuddy)
- User may have a local agent/script on their Windows machine that can read files
- Ask if they have WorkBuddy or similar

### 4. Excel/PDF and other binary files
- User pastes key content (table data, key numbers)
- Or describes what data is needed -- generate remotely
- OCR and document extraction also work on remote files only

### 5. Manual copy command (if terminal IS local/WSL)
```
cp /mnt/d/path/to/file ./target
```

## Verification

When user says file is available:
1. Try `read_file(path)` to confirm
2. If success, proceed with analysis
3. If fail, return to alternatives above

## Pitfalls

- Do NOT keep trying local paths repeatedly (wastes tokens)
- State the constraint once clearly, then offer the simplest next step
