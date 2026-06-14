---
name: deliverable-handoff
description: 交付文件/搜索结果/报告给用户时，如何告知路径和格式。用户为Windows用户，通过WSL使用Hermes。
version: 1.0.1
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [delivery, File-Formatting, Communication, Output, CMS, non-technical]
---

# Deliverable Handoff

Rules for presenting file-based deliverables and operational instructions to the user.

## File path format

**ALWAYS** give the Windows path with drive letter when the file is on the Windows filesystem (Desktop, Documents, Downloads, etc.):

```
✅ C:\Users\jsxuaijun\Desktop\文件名.md
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
✅ 已保存到：C:\Users\jsxuaijun\Desktop\文件名.md
（2,613 bytes，含内容概要）
```

## CMS / 建站系统操作指引（非技术用户模式）

当用户需要操作 CMS 后台（如 QCNET99 ASP 建站系统）或任何网页后台管理界面，且用户自称"小白/不懂技术"时：

### 核心原则

1. **不要解释原理，只告诉按哪个按钮**
2. **每一步都说清楚点哪里、填什么**
3. **用表格列出每个输入框该填的内容**
4. **每完成一步，告诉用户如何验证（刷新页面看效果、打开网址看内容）**
5. **如果用户对操作有疑问，用截图文字描述代替技术术语**

### 操作指引模板格式

```
### 第X步：[功能名称]

点左边菜单 → [菜单路径]

在页面上找到：
- [控件A]：填 [值A]
- [控件B]：填 [值B]

点 [提交/添加] 按钮。

✅ 验证：刷新首页，看到 [预期效果]
```

### 具体 CMS 操作顺序（已验证，不可颠倒）

**QCNET99 文章发布三步法（正确的顺序）：**

```
第一步：资讯管理系统 → 分类管理 → 添加分类
第二步：资讯管理系统 → 文章添加 → 填写内容 → 提交
第三步：网站信息配置 → 菜单管理 → 添加菜单导航
```

**关键陷阱（已验证）：**
- 不要先去「栏目管理」添加——栏目管理和分类管理是两套系统，先去栏目管理会导致重复出现3个同名分类
- 菜单链接地址**只写相对路径**（如 `news_main_612.html`），不写完整URL
- 已有文章可在「资讯管理系统 → 文章管理 → 修改」中编辑

### 文章内容各字段对GEO的影响

| 字段 | 作用 | 填写要求 |
|------|------|----------|
| 文章标题 | SEO标题，搜索引擎展示 | 含核心关键词 |
| 关键词 | meta keywords | 逗号分隔，3-5个 |
| 页面描述 | meta description，AI搜索会作为摘要 | 150字内 |
| 文章内容 | 正文 | 外部链接写完整URL |

## Pitfalls

- **WSL路径 ≠ Windows路径** — 用户不用WSL的home目录做日常文件管理。所有交付物放Windows桌面（`/mnt/c/Users/jsxuaijun/Desktop/`），除非特别说明。
- **不要用 `/mnt/c/` 路径** — 用户不认识这个格式。直接翻译成 `C:\...`
- **不要只说"已保存"** — 必须带路径，这是纪律。
- **桌面文件可直接双击打开** — 路径尽量指向他能直接双击打开的位置。
- **非技术用户输入bat文件时** — bat文件必须用 ANSI/GBK 编码写（默认Windows cmd），不能用 UTF-8。如果写入后发现乱码或语法错误，用 Python 以 `encoding='gbk'` 或 `newline='\r\n'` 重新写入。
