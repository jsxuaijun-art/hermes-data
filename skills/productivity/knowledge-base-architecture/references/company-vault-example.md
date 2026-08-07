# Company Vault Example: 盈信财税团队

> Concrete vault structure from 2026-07-21 setup session.

## Context

Company: 盈信企业管理（苏州）, serving 苏州/上海 SME clients.
Team: 徐总 (MBA), 江姐 (高级会计师), 黎经理 (CTA), 许经理 (CPA).
Knowledge type: Tax/accounting compliance, GEO content marketing, sales playbooks, tech toolchain.

## Vault Location

Windows D: drive → `/mnt/d/obsidian-vault/` from WSL.

## Structure Created

```
D:\obsidian-vault\
├── 00-收件箱\
│   ├── 待处理\         ← 公众号文章、视频笔记、截图等原始素材
│   └── 已归档\
├── 01-知识库\
│   ├── 财税知识\
│   │   ├── 公司注册\
│   │   ├── 代理记账\
│   │   ├── 税务合规\
│   │   ├── 民办非企业\
│   │   ├── 股权转让\
│   │   └── 政策法规\
│   ├── 客户案例\
│   ├── 话术与销售\
│   │   ├── S1-S5体系\
│   │   ├── 价格谈判\
│   │   └── 客户沟通模板\
│   ├── GEO运营\
│   ├── 技术笔记\
│   └── 行业洞察\
│       ├── 财税\
│       └── 企业管理\
├── 02-项目\
│   ├── 2026-GEO项目\
│   ├── 客户项目\
│   └── 内部项目\
├── 03-工具库\
│   ├── Hermes\
│   │   ├── 配置技巧.md
│   │   ├── AGENTS（精读版）.md
│   │   ├── 常用命令备忘录.md
│   │   ├── WSL环境配置.md
│   │   ├── 自定义skills列表.md
│   │   ├── skill参考\
│   │   └── templates\
│   ├── Codex\           ← 预留
│   └── Claude-Code\     ← 预留
├── 04-输出\
│   ├── Hermes\
│   ├── Codex\           ← 预留
│   └── Claude-Code\     ← 预留
├── 05-存档\
│   ├── 2024\
│   └── 2025\
├── 公众号\
│   ├── 已发布\
│   └── 待发布\
└── 素材库\
    └── 短视频灵感\
```

Notes:
- Pre-existing dirs (`公众号/`, `素材库/`) were preserved, not replaced.
- All Chinese names work fine in both WSL and Obsidian.

## What Was Copied Into the Vault (Hermes section)

| Source | KB Location | Type |
|--------|-------------|------|
| `~/hermes-agent/AGENTS.md` (53KB) | `03-工具库/Hermes/AGENTS（精读版）.md` | **精读版** — only user-facing parts |
| `~/.hermes/config.yaml` (with secrets) | None | **Not copied** — secrets stay out |
| `~/.hermes/config.yaml` structure | `03-工具库/Hermes/配置技巧.md` | Key settings documented without API keys |
| CLI commands | `03-工具库/Hermes/常用命令备忘录.md` | Complete reference |
| WSL environment notes | `03-工具库/Hermes/WSL环境配置.md` | Paths, encoding pitfalls, proxy setup |
| Custom skills index | `03-工具库/Hermes/自定义skills列表.md` | 30+ skill catalog with descriptions |
| Team overview (who runs Hermes) | `01-知识库/技术笔记/Hermes配置记录.md` | Non-technical intro for other team members |

## Key Decision: Copy vs Move

Decision was **copy only** — reasoning:

- `~/.hermes/config.yaml`, `~/.hermes/.env`, `~/.hermes/skills/` are **runtime files** Hermes needs in place
- Moving them breaks Hermes
- The KB holds **knowledge documentation** about how Hermes is configured, not the config files themselves
- Same principle applies to Codex/Claude Code later

## Teammate Who Needs to Know

The user explicitly corrected: "不仅仅是我的知识资产，还包括江姐及整个公司的". 
This means the KB is company-owned, not personal. All naming, categorization, and language should reflect that.
