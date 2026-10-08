---
name: health-record
description: 健康档案管理 - 管理检查报告、用药记录和健康笔记
---

# 健康档案 (Health Record)

**位置:** `/home/administrator/hermes-agent/obsidian-vault/健康档案/`

## 子文件夹

| 文件夹 | 用途 |
|--------|------|
| `检查报告/` | 体检报告、化验单、影像检查结果等 |
| `用药记录/` | 用药情况、剂量、时间记录 |
| `健康笔记/` | 健康心得、医生建议、养生知识 |

## 读取健康记录

```bash
VAULT="/home/administrator/hermes-agent/obsidian-vault"
cat "$VAULT/健康档案/检查报告/文件名.md"
```

## 列出所有健康记录

```bash
VAULT="/home/administrator/hermes-agent/obsidian-vault"
find "$VAULT/健康档案" -name "*.md" -type f
```

## 创建健康记录

```bash
VAULT="/home/administrator/hermes-agent/obsidian-vault"
cat > "$VAULT/健康档案/检查报告/2026年体检报告.md" << 'ENDNOTE'
---
tags: [健康, 体检]
date: 2026-07-24
---

# 2026年体检报告

...
ENDNOTE
```
