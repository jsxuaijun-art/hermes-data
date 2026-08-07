---
name: knowledge-base-architecture
description: Design and organize shared knowledge bases for teams.
platforms: [linux, macos, windows]
---

# Knowledge Base Architecture

Design a shared knowledge base (Obsidian vault, markdown directory) for a company or team, with multi-AI-tool sharing. Covers the structure, ownership model, and integration strategy.

## When to Use

- The user asks to set up or reorganize a knowledge base / Obsidian vault / 知识库
- The conversation involves structuring markdown notes for company use
- The user asks about sharing a knowledge base between Hermes, Codex CLI, or Claude Code
- The user asks what to put in vs keep out of a shared vault

## Core Principles

### 1. Know Your Owner

**FIRST QUESTION**: Who owns the knowledge base?

| Owner | Structure | Example |
|-------|-----------|---------|
| **Individual** | Personal organization, flat categories | "我的学习笔记" |
| **Company / Team** | Role-aware, shared knowledge + team member contributions | 江姐/徐总/黎经理/许经理 团队 |

When the user says "我的" (my), probe gently — do they mean "my personal" or "our company's"? Frame the default as company/team level unless they explicitly say personal. A company KB that starts as personal will need painful restructuring later.

### 2. Public Knowledge Zone + Tool Config Zone (分享与隔离)

AI tools (Hermes, Codex CLI, Claude Code) **share** the public knowledge zone but each needs **isolated** configuration space.

```
vault/
├── 01-知识库/       ← SHARED: knowledge assets, case studies, industry insights
├── 02-项目/         ← SHARED: project notes
└── 03-工具库/       ← ISOLATED per tool
    ├── Hermes/      ← Hermes config docs, AGENTS.md (精读版), command cheatsheet
    ├── Codex/       ← Codex CLI rules (empty until needed)
    └── Claude-Code/ ← Claude Code rules (empty until needed)
```

### 3. Copy, Don't Move

**QUESTION**: When integrating tool config / docs into the KB...

| Action | When |
|--------|------|
| **Copy** (复制) | Tool documentation, config notes (without secrets), skill lists, cheatsheets |
| **Don't move** (不移入) | Runtime files (config.yaml, .env, skills/ directories), source code, database files |
| **Don't add** (不放) | Dynamic/often-updated content best left in the tool's own directory |

The KB should hold **knowledge documents**, not runtime assets. Moving a config file out of its tool's home breaks the tool.

### 4. 收件箱 Workflow (Inbox → Process → Archive)

```
00-收件箱/
├── 待处理/    ← raw inbound: articles, video notes, screenshots, client materials
└── 已归档/    ← processed inbound that still has reference value
```

All external content enters here first, then gets classified into the appropriate 01-知识库/ subcategory.

## Recommended Vault Structure

```
vault/
├── 00-收件箱/
│   ├── 待处理/
│   └── 已归档/
│
├── 01-知识库/              ← permanent knowledge assets
│   ├── 财税知识/
│   │   ├── 公司注册
│   │   ├── 代理记账
│   │   ├── 税务合规
│   │   ├── 民办非企业
│   │   ├── 股权转让
│   │   └── 政策法规
│   ├── 客户案例/            ← anonymized case studies
│   ├── 话术与销售/
│   │   ├── S1-S5体系
│   │   ├── 价格谈判
│   │   └── 客户沟通模板
│   ├── GEO运营/
│   ├── 技术笔记/            ← toolchain, devops, sync config
│   └── 行业洞察/
│       ├── 财税
│       └── 企业管理
│
├── 02-项目/               ← active projects
│   ├── <year>-<project>
│   └── ...
│
├── 03-工具库/             ← tool-specific config docs
│   ├── Hermes/
│   ├── Codex/
│   └── Claude-Code/
│
├── 04-输出/               ← tool-generated output
│   ├── Hermes/
│   ├── Codex/
│   └── Claude-Code/
│
├── 05-存档/               ← archived by year
│   ├── 2024/
│   └── 2025/
│
└── .obsidian/             ← Obsidian auto-generated
```

Top-level directories use numeric prefixes (00, 01, 02...) for sorting. Keep to 6 or fewer top-level dirs.

## Hermes Integration

In Hermes, set the vault path in `~/.hermes/.env`:

```
OBSIDIAN_VAULT_PATH=/mnt/d/obsidian-vault   # Windows D: drive via WSL
```

Or for a native Linux vault:

```
OBSIDIAN_VAULT_PATH=/home/user/obsidian-vault
```

The vault path can then be resolved via `OBSIDIAN_VAULT_PATH` env var and used with `read_file`/`write_file`/`search_files`.

## Pitfalls

- **Don't assume personal ownership.** The user may be building for their whole team. Always ask who the KB serves.
- **Don't move runtime files into the KB.** Config files, API keys, skill directories, and tool binaries must stay in their original locations. Only copy knowledge documentation.
- **Don't hardcode WSL paths.** For Windows users, the vault lives on a Windows drive (/mnt/d/) but is accessed from WSL. Ensure paths are WSL-compatible.
- **Don't skip 收件箱.** Without a raw inbox, the KB has no ingestion path and external content (公众号 articles, videos) has nowhere to land before classification.
- **Chinese vault paths work fine** in WSL and Obsidian. No need to English-ify directory names — they're the user's natural language.

## Verification

- All top-level dirs exist and are visible from WSL (`ls /mnt/d/obsidian-vault/`)
- `OBSIDIAN_VAULT_PATH` is set in `~/.hermes/.env`
- Hermes can read/write a test note in the vault via `write_file`
