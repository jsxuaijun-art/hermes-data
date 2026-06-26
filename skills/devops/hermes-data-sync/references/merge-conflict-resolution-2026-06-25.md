# 分叉分支 + 内容冲突案例（2026-06-25）

## 场景

用户通过 Hermes CLI 说 "hermes update"。在 WSL 侧的 Hermes Agent 仓库执行同步时遇到：

```
28 commits ahead, 9 commits behind origin/main
```

→ `git push` 被拒（non-fast-forward，远程有新提交）
→ `git pull --rebase` 产生 4 个文件冲突
→ `git pull --no-rebase`（merge 模式）也产生冲突

## 根因

多端同步模式下（WSL 办公室电脑 + 阿里云服务器），两边各自有未推送提交，分支分叉。

## 为什么常见方案不行

| 方案 | 为什么失败 |
|------|-----------|
| `git push` | non-fast-forward 拒绝 — 远程有本地没有的提交 |
| `git fetch + reset --hard origin/main` | **丢弃本地未推送提交** — 数据丢失 |
| `git pull --rebase` | 产生冲突，auto-merge 可能选错版本 |
| `git pull --no-rebase`（merge） | 产生冲突，需要手动解决 |

`fetch + reset --hard` 只在「仅拉取，不关心本地提交」时安全。在「双方都有未推送提交」时致命。

## 解决流程

### 1. 确认是否分叉

```bash
git log --oneline origin/main..HEAD | wc -l   # 本地未推送提交数
git log --oneline HEAD..origin/main | wc -l   # 远程未拉取提交数
```

如果 **本地 > 0 且 远程 > 0** → 分叉 → 不能用 reset --hard。

### 2. 选择合并策略

用 merge（而非 rebase）保留双方历史：

```bash
git pull --no-rebase origin main
```

### 3. 解决冲突

```bash
git diff --name-only --diff-filter=U   # 列出冲突文件
```

Hermes 同步仓库的冲突文件有明确的保留优先级：

| 文件 | 冲突类型 | 默认策略 |
|------|---------|---------|
| `config.yaml` | 内容冲突 | **留本地**（本地有当前机器在用的 API 端点配置） |
| `memories/MEMORY.md` | 内容冲突 | **留本地**（最新的训练/偏好记录） |
| `memories/USER.md` | 内容冲突 | **留本地**（最新的偏好修正） |
| `skills/*/SKILL.md` | 内容冲突 | **需要逐文件审核**（两边都可能独立修改） |
| `skills/*/README.md` | add/add 同内容 | 留任意（仅权限位差异） |

```bash
git checkout --ours config.yaml
git checkout --ours memories/MEMORY.md
git checkout --ours memories/USER.md
git add .
git commit -m "merge: 同步远程提交，冲突保留本地最新版"
git push origin main
```

## 和现有坑的关系

| 本案例 | 现有 Pitfall | 差异 |
|-------|-------------|------|
| 双方都有未推送提交 | #4（正常分叉） | #4 假设 pull --rebase 就能跑通，本案例有实际内容冲突 |
| 冲突文件内容解决 | #5（共享文件 merge 冲突） | #5 只描述现象，本案例给出具体命令和文件级别策略 |
| 不能用 reset --hard | #14（脏文件） | #14 的修复方案是 fetch+reset — 在本场景下会丢数据 |
