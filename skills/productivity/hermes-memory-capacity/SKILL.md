---
name: hermes-memory-capacity
description: 调大记忆条/档案字符上限(memory_char_limit)。记忆写不进或问上限能否调时用。
category: productivity
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [memory, 容量, 扩容, config, 上限]
    related_skills: [memory-management]
trigger: 用户说"记忆满了""记忆上限能不能调大""加内存容量""memory 写不进去了""exceeds the limit"。
---

# Hermes Memory 容量扩容（调大上限）

## 当何时使用（When to Use）
当用户问"记忆空间还有多少""记忆上限能不能调大""memory 写不进去 / exceeds the limit"、或希望在不删记忆的前提下腾出更多记忆容量时。若用户只是要清理/精简现有记忆内容，则参考「memory-management」技能（bundled）。

## 用途
Hermes 的记忆条（memory）和用户档案（user profile）有字符上限，写满后新增会被拒。本技能说明如何**安全地把上限调大**——这是治满的正解，比"反复删记忆腾地方"更根本。**不用改源码，升级不会被覆盖**（配置层持久化）。

## 关键事实
- 默认上限：记忆条 `memory_char_limit` = 2,200；用户档案 `user_char_limit` = 1,375。
- 这两个值**不是引擎固化常量**，是 config.yaml 里 `memory:` 段的配置项。
- 主会话在**启动时**读取（`agent/agent_init.py` 读 `memory.memory_char_limit` / `memory.user_char_limit`）。
- 改完必须**重启 Hermes** 才生效。

## 如何调大
用官方配置命令（不要手改 config 文件）：
```text
hermes config set memory.memory_char_limit 5000
hermes config set memory.user_char_limit 2200
```
生效后，memory 工具顶部会显示新上限，例如 `[93% — 2,300/5,000 chars]`。

## Pitfalls
- **不要用 patch/write_file 直接改 `~/.hermes/config.yaml` 的 memory 段** —— 会被安全机制拒绝，报 "Agent cannot modify security-sensitive configuration. Edit ~/.hermes/config.yaml directly or use 'hermes config' instead." 必须走 `hermes config set`。
- **上限在启动时读取** —— 改了不重启不生效；让用户 Ctrl+Q / /quit 退出后重新 `hermes`。
- **「超限 N 字」被拒 ≠ 必须扩容，批量精简可解（2026-09-21 实战）** —— memory 工具报「超限 42 字」（新词条 2242 字 > 当前上限 2200）时，说明容量已满。若不便扩容（config 改动需重启才生效，cron/会话中途做不到），用**一次批量原子操作**：1 个 `replace` 精简旧词条（`old_text` 必须逐字精确匹配现有词条全文）+ 1 个 `add` 新词条，同批一次提交可成功。不要反复单独尝试 `add`——多次失败会触发工具保护。实战一次成功（占用 2168/2200）。
- **「注入上限」与 `memory_char_limit` 是两个开关** —— 用户曾"放开容量"后仍报超限，是因为 memory 工具头部实际显示的注入上限（如 `[x/2200 chars]`）未变；判断剩余空间一律以工具头部实际显示为准，别只看 config 值。
- 判断"能否扩容"时，先查 `hermes_cli/config.py` 的 DEFAULT_CONFIG 和 `agent/agent_init.py` / `tools/memory_tool.py` 是否 honor 配置覆盖（`load_on_disk_store()` 也 honor），不要想当然认为不能调。

## 参考
- 记忆内容本身的管理/精简/迁移方法见「memory-management」技能（bundled，勿改）。扩容治满，精简治本——两者结合最优。
