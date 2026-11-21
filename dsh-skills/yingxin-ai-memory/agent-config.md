---
title: AI 工具配置
type: ai-memory
last-updated: 2026-08-09
---

# AI 工具配置

> 3 个 AI 工具的接入方式、模型选择、API 引用位置。**不**放凭证本身。

## 工具清单

| 工具 | 平台 | 默认模型 | 接入方式 |
|---|---|---|---|
| **Claw (WorkBuddy)** | Windows + WSL | MiniMax-M3 | 直接读 WSL 文件 |
| **Hermes Agent** | WSL2 (systemd) | DeepSeek V4 Flash | 直接读 WSL 文件 |
| **Claude Code** | WSL2 | Claude Sonnet | 直接读 WSL 文件 / MCP |
| **Codex CLI** | WSL2 | DeepSeek V4 Flash (via ccswitch-deepseek 代理 localhost:11435) | 直接读 WSL 文件（/mnt/d/obsidian-vault） |

## 凭证存放位置（不放 vault 内）

- DeepSeek API key: ~/.hermes/config.yaml (Hermes), ~/.codex-bridge/.env (Codex)
- OpenAI/Anthropic API keys: 各工具自带的 ~/.config/<tool>/
- GitHub PAT: ~/.config/gh/hosts.yml 或 git credential manager

## 共享 vault 路径

- WSL: /mnt/d/obsidian-vault
- Windows: \\wsl$\Ubuntu\home\dmin\obsidian-vault
- 远程 Git: https://github.com/jsxuaijun-art/obsidian-vault

## 模型切换约定

- 简单查资料 → 用 DeepSeek (便宜)
- 复杂推理 / 长上下文 → 用 Claude Sonnet
- 编程任务 → Claude Code / Codex
- 中国政策、合规、客户沟通 → 任何模型都行，注意审核
