---
name: hermes-server-ops
category: devops
description: 云服务器上的 Hermes Agent 运维 — 升级、systemd 服务管理、安全拦截引导、混合目录诊断。
triggers:
  - 阿里云 / 云服务器 / ECS / 47.103.27.171 / 服务器上的 hermes
  - hermes update / 升级服务器 / 服务器升级
  - systemctl restart / gateway 重启被拦截 / BLOCKED
  - 混合目录 / fork 保护 / hermes update 不生效 / 跳过升级
  - hermes-gateway.service / hermes-wsl-manager.service / wecom-bridge.service
  - 财税情报推送 / unified_tax_loader / 服务器 cron
---

# Hermes 云服务器运维（阿里云 47.103.27.171）

## 概述

用户的 Hermes 跑在两端：**本机 WSL**（git 混合目录）和 **阿里云轻量服务器**（官方安装）。本 skill 管服务器端运维；WSL 本地环境细节见 `wsl-hermes-env` skill。

**核心结论（2026.8.10 实测）：数据同步 ≠ 代码升级。** hermes-data 仓库同步的是数据（skills/记忆/config），不包含 Hermes 代码。每台机器的代码要各自升级。

## 服务器拓扑（2026.8.10 实测）

```
公网 47.103.27.171 · root · Ubuntu 22.04 · 实例名 yingxinkuaiji
安装：官方脚本 → /usr/local/lib/hermes-agent（venv 在项目内）
launcher：/usr/local/bin/hermes（bash wrapper → venv/bin/hermes）
systemd 服务（3 个，全部 active）：
  hermes-gateway.service      # 消息网关（企微等）
  hermes-wsl-manager.service  # 云端 WSL 状态管理 API
  wecom-bridge.service        # 企微回调桥
Hermes cron：财税情报推送（30 8 * * 1，脚本 cron/unified_tax_loader.py，workdir /root）
crontab：0 3 1 * * /root/cleanup.sh（每月1号 GitHub 推送）+ acme.sh 证书续期
```

## SSH 登录（2026.8.10 更新：公钥已授权）

WSL 端公钥已加入服务器 authorized_keys，**免密直连**，优先用公钥：

```bash
ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@47.103.27.171 'command'
```

旧密码 `yx168168/*-`（sshpass）仍可作 fallback，但公钥更快更稳。登录前可用 `hostname` 确认连的是服务器而非本机。

## 服务器升级流程（官方安装 → hermes update 直接可行）

官方安装（/usr/local/lib/hermes-agent）没有 fork 保护问题，`hermes update` 直接可用：

```bash
# 1. 升级（可能几分钟，用长 timeout）
timeout 500 ssh root@47.103.27.171 'hermes update 2>&1 | tail -40; echo "EXIT: $?"'

# 2. 验证版本
hermes version   # 期望 "Up to date" + 目标版本号

# 3. 重启 gateway 让新代码生效（见下方安全拦截——可能需要用户手动执行）
systemctl restart hermes-gateway.service

# 4. 全面验证
systemctl is-active hermes-gateway.service hermes-wsl-manager.service wecom-bridge.service
journalctl -u hermes-gateway.service --since "2 min ago" --no-pager | grep -iE "error|traceback" 
hermes cron list   # 定时任务必须完好
```

**升级后的常见警告（无害，可忽略）：**
- `npm error engine Not compatible`（node v20 < 22.22，Web UI 构建跳过）→ 服务器不需要 dashboard，不影响核心
- `platform.slack failed to refresh: cannot import name ...` → 升级瞬间旧模块缓存，**重启服务后自动恢复**；函数本体在新代码里存在（用 grep 确认）
- `Syncing bundled skills ... +14 new, ~60 user-modified` → 正常

**升级不影响：** ~/.hermes/ 数据（SOUL/记忆/skills/config）、cron 配置、systemd 服务定义。今天已跑完的定时任务不受重启影响（重启前确认 next run 在未来）。

## ⚠️ 生产服务重启被安全系统 BLOCKED（2026.8.10 实测）

Hermes 安全系统会拦截生产服务器上的破坏性操作，包括：
- `systemctl restart hermes-gateway.service`（远程 SSH 里执行）
- `rsync` 覆盖源码目录

拦截特征：`BLOCKED: Command timed out without user response... Do NOT retry this command`。
**不要重试、不要换命令绕过、不要用 kill fallback 强上**（kill 是 gateway 401 调试场景的招，升级场景不该用）。

**正确姿势（实测有效）**：
1. 先 `clarify` 征求用户同意；用户未响应时**也不能擅自执行**（Silence is not consent）
2. 把命令给用户，让用户在**服务器 shell 里自己粘贴执行**（用户已登录时最快）：
   ```bash
   systemctl restart hermes-gateway.service && sleep 5 && systemctl is-active hermes-gateway.service && hermes version
   ```
3. 让用户把输出贴回来，再远程验证日志和 cron

⚠️ 用户在 Windows 终端跑 `ssh root@... "命令"` 可能因本机无公钥报 Permission denied——引导用户直接进服务器 shell 执行，不要绕 ssh。

## 混合目录 + fork 保护（为什么本机 hermes update 不升级）

本机 `~/hermes-agent` 是**混合目录**：git 仓库 = hermes-data 数据仓库（origin=jsxuaijun-art/hermes-data），上游源码文件在磁盘上但 untracked，git 跟踪的全是用户数据（skills/、memories/、obsidian-vault/、config.yaml、cron/ 数据、同步 bat）。

`hermes update` 的 fork 保护（update_cmd.py `_sync_with_upstream_if_needed()`）：origin 非官方仓库且本地有领先提交（如 37 个 sync 提交）→ 打印 "Your fork has N commit(s) not on upstream. Skipping upstream sync to preserve your changes." 并**跳过升级**。这是保护，不是报错。

**混合目录升级只能手动**：`git fetch upstream main` → `git archive upstream/main | tar -x`（或官方 tarball）→ rsync 覆盖 untracked 源码、排除所有 tracked 数据文件 → venv 装依赖 → 清 __pycache__。完整排除清单见 `wsl-hermes-env` 的 references/hermes-v0.20-upgrade.md。

诊断要点：`hermes version` 显示的 "upstream xxx" 是 origin/main（数据仓库）哈希，**不是**真正上游源码版本；判断混合目录看 `git remote -v`（origin 是 hermes-data 就是混合目录）和 `git ls-files | cut -d/ -f1 | sort | uniq -c`（tracked 全是用户数据目录）。

## 验证清单

- [ ] `hermes version` 显示目标版本 + "Up to date"
- [ ] 3 个 systemd 服务 is-active = active
- [ ] journalctl 无 error/traceback
- [ ] `hermes cron list` 任务完好（财税情报推送 next run 正常）
- [ ] 升级前今天的定时任务已完成、next run 在未来（重启无冲突）
