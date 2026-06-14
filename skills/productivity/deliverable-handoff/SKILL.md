---
name: deliverable-handoff
description: 交付文件/搜索结果/报告给用户时，如何告知路径和格式。用户为Windows用户，通过WSL使用Hermes。
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [delivery, File-Formatting, Communication, Output]
---

# Deliverable Handoff

Rules for presenting file-based deliverables to the user.

## File path format

**ALWAYS** give the Windows path with drive letter when the file is on the Windows filesystem (Desktop, Documents, Downloads, etc.):

```
✅ C:\Users\jsxuaijun\Desktop\上海闵行区中考近三年试题资源汇总.md
❌ /home/jsxuaijun/Desktop/...           # WSL路径，用户看不懂
❌ /mnt/c/Users/jsxuaijun/Desktop/...    # WSL挂载路径，用户不认
```

**Exception**: If the file is purely on the WSL Linux filesystem (e.g., `~/.hermes/` or `/tmp/`), give the WSL path and explain it's a WSL-internal file.

### Path mapping cheat sheet

| Windows | WSL mount | Notes |
|---------|-----------|-------|
| `C:\Users\jsxuaijun\Desktop\` | `/mnt/c/Users/jsxuaijun/Desktop/` | 用户桌面——首选交付位置 |
| `C:\Users\jsxuaijun\Documents\` | `/mnt/c/Users/jsxuaijun/Documents/` | 用户文档 |
| `C:\Users\jsxuaijun\Downloads\` | `/mnt/c/Users/jsxuaijun/Downloads/` | 用户下载 |
| (WSL only) | `/home/jsxuaijun/` | WSL Linux home——仅内部文件放这 |
| (WSL only) | `/home/jsxuaijun/bin/` | 快捷脚本位置 |

**Windows username**: `jsxuaijun` (not `Admin` — the old memory was from a different machine).

## When to announce

**Immediately** after writing the file. Do NOT wait until the end of a long response. The moment the file is created or modified, state:

> ✅ 已保存到：`C:\Users\jsxuaijun\Desktop\文件名.md`

Followed by a one-liner of what's in it (file size, content summary).

## What to include

1. **完整Windows路径** — always with drive letter
2. **文件大小** — e.g. "2,613 bytes"
3. **内容概要** — what's in the file, one line
4. **如果有多个文件** — 逐个列出路径

## Example

```
✅ 已保存到：C:\Users\jsxuaijun\Desktop\上海闵行区中考近三年试题资源汇总.md
（2,613 bytes，含数学/英语/语文/物理/化学五科近三年试题链接）
```

## Pitfalls

- **WSL路径 ≠ Windows路径** — 用户不用WSL的home目录做日常文件管理。所有交付物放Windows桌面（`/mnt/c/Users/jsxuaijun/Desktop/`），除非特别说明。
- **不要用 `/mnt/c/` 路径** — 用户不认识这个格式。直接翻译成 `C:\...`
- **不要只说"已保存"** — 必须带路径，这是纪律。
- **桌面文件可直接打开** — 用户的双击习惯，路径尽量指向他能直接双击打开的位置。
