---
name: aliyun-hermes-server
description: 阿里云服务器(47.103.27.171) Hermes 运维：代码升级、服务重启、定时任务核查。
---

# 阿里云服务器 Hermes 运维

用户在阿里云轻量应用服务器（实例 yingxinkuaiji）上长期运行一个 Hermes 实例，承载企微桥接（wecom-bridge → hermes-gateway）和 Hermes 定时任务（财税情报推送）。本技能覆盖这台服务器上 Hermes 的代码升级、服务管理和问题排查。

## When to Use

- 用户提到「阿里云」「云端服务器」「服务器上的 Hermes」，要求升级/检查/重启/改任务
- `hermes version` 显示落后版本，需要判断各端是否一致
- 服务器上 gateway / 企微桥接服务异常需要排查

## Server Facts（持久拓扑）

| 项 | 值 |
|---|---|
| 公网 IP | 47.103.27.171（固定，公众号 API 白名单用它） |
| 实例 | yingxinkuaiji，Ubuntu 22.04，root 登录 |
| 主机名 | iZuf6hr71n2woh5l98hf1dZ |
| Hermes 安装 | 官方安装脚本 → /usr/local/lib/hermes-agent（自带 venv），launcher /usr/local/bin/hermes（bash wrapper → venv/bin/hermes） |
| systemd 服务 | hermes-gateway.service / hermes-wsl-manager.service / wecom-bridge.service |
| Hermes cron | 财税情报推送（每周一 8:30，脚本 unified_tax_loader.py，workdir /root） |
| 系统 crontab | 每月1日 3:00 cleanup.sh（GitHub 推送）；acme.sh 证书续期 |

## 核心心智：数据同步 ≠ 代码升级

hermes-data 仓库（见 hermes-data-sync skill）只同步**数据**（skills / SOUL.md / 记忆 / config.yaml），**不同步代码**。每台机器的 Hermes 代码必须各自执行 `hermes update`。所以「本机升级了」不代表「阿里云也升级了」——升级前先逐端 `hermes version` 对比。

## SSH 访问

- **WSL 端**：公钥已授权，`ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@47.103.27.171` 直接通（`-o BatchMode=yes` 可快速探测）。
- **用户 Windows 终端**：没有该公钥，ssh 会要密码；用户常在服务器 shell 里手动执行命令——此时直接给**裸命令**（不带 ssh 包装），让他粘贴 + 回车。

## 升级流程（v0.15.1 → v0.20.0 实测通过）

1. **升级前核查**：`systemctl is-active` 三个服务 + `hermes cron list` 看下次运行时间，避开定时任务窗口（当天任务已跑完再动手）。
2. **跑升级**（耗时 3-10 分钟，SSH timeout 给足 500s+）：
   ```bash
   hermes update 2>&1 | tail -40
   ```
   正常输出序列：pre-update snapshot → pull → 清理 pycache → Python 依赖 → lazy backends 刷新（个别失败可忽略，见 P3）→ 技能同步（+14 new, ~60 user-modified）→ configuration up to date。
3. **重启 gateway 生效**（磁盘新代码 ≠ 进程新代码，见 P4）：
   ```bash
   systemctl restart hermes-gateway.service && sleep 5 && systemctl is-active hermes-gateway.service && hermes version
   ```
4. **验证**：三个服务 active；`journalctl -u hermes-gateway.service --since "2 min ago"` 无 error/traceback；`hermes cron list` 任务完好、next run 正常。

## Pitfalls

- **P1 生产服务重启会被 Hermes 安全闸拦截**：通过 Hermes terminal 工具 SSH 执行 `systemctl restart` 生产服务，无用户明确同意会被 BLOCKED（"user has NOT consented"），重试同样被拦。**正确做法：把命令给用户在他自己的终端执行**，或先 clarify 拿到明确同意再操作。
- **P2 hermes update 的 npm 警告可忽略**：node v20 < 要求的 v22.22 → npm install 失败 → Web UI/TUI 构建跳过（"hermes web will not be available"）。服务器上核心功能（gateway/cron）不受影响，不用处理。
- **P3 platform.slack lazy backend 刷新失败**（`cannot import name 'apply_subprocess_home_env' from 'hermes_constants'`）：这是更新瞬间的旧模块缓存问题——该函数在新代码 hermes_constants.py 里存在。**重启 gateway 后自动恢复**，无需重装；若仍失败可再跑一次 `hermes update`。
- **P4 升级后必须重启服务才生效**：Python 进程已把旧代码加载进内存，磁盘更新不影响运行中进程。不重启 = 磁盘新/内存旧的混用状态，下次 cron 触发可能加载新文件产生混合行为，有风险。
- **P5 用户在服务器 shell 里粘贴命令后「光标不动」**：多半是没按回车；或命令含 `sleep 5` 造成几秒"卡住"假象。超过 10 秒无反应就 Ctrl+C，改为逐条手输。
- **P6 升级不动数据**：`~/.hermes/`（记忆/skills/config）完全不受 `hermes update` 影响，无需备份（update 自带 pre-update snapshot）。

## Verification

升级完成判定：`hermes version` 显示目标版本 + `Up to date`；`systemctl is-active hermes-gateway.service hermes-wsl-manager.service wecom-bridge.service` 全 active；journalctl 无 error；`hermes cron list` 任务完好。
