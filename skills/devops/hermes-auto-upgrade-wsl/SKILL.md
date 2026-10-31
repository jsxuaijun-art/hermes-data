---
name: hermes-auto-upgrade-wsl
description: "Use when user says 升级Hermes/方式2. Agent自动执行WSL下Hermes完整升级流程."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, upgrade, wsl, git, maintenance]
---

# Hermes 自动升级 (WSL, git 安装)

用户已从 tarball 转为 **git 安装**：源码 `/home/dmin/hermes-agent`，origin = 官方仓库
NousResearch/hermes-agent，main 分支。venv 在 `~/.venv-hermes`（Python 3.12）。

用户选择「方式2」：说「升级 Hermes / 方式2 / hermes update」时，**由 agent 自动执行**完整
升级流程，而不是让用户自己跑 `hermes update` 命令。

## 关键坑：为什么 agent 不能直接跑 `hermes update`

`hermes update` 在 agent 的 terminal 管道里运行时，stdin 不是终端（fd=0），它检测到非
交互环境会在需要确认时静默跳过 git pull，只输出版本横幅就退出。所以 **agent 必须手动执行
git 操作**完成升级，再手动重装依赖。

## 完整升级流程

### 1. 获取 Windows 代理 IP 并配置仓库级 git 代理

WSL2 每次重启 Windows IP 可能变。执行：

```bash
cd /home/dmin/hermes-agent
WIN_IP=$(ip route | grep default | awk '{print $3}')
git config http.proxy "http://$WIN_IP:7890"
git config https.proxy "http://$WIN_IP:7890"
echo "代理: $(git config http.proxy)"
```

⚠️ 代理必须配在**仓库级**（`.git/config`），这样 agent 手动调 git fetch 时自动带上。
Windows Clash 端口默认 7890。若 `127.0.0.1:7890` 连接被拒，说明那是 Windows 自己，
WSL 内必须用 Windows 主机 IP。

### 2. Fetch 官方最新 + 检查落后

```bash
cd /home/dmin/hermes-agent
git fetch origin main 2>&1 | tail -3
echo "落后commit数: $(git rev-list --count HEAD..origin/main)"
git log --oneline HEAD..origin/main
```

⚠️ **浅克隆陷阱**：若仓库是 shallow（`git rev-parse --is-shallow-repository` 返回
true），`rev-list --count` 会**低估**落后数（可能显示 1，但实际差异几百文件）。判断真实
差异用 `git diff --name-status HEAD origin/main | wc -l`。若本地 main 是基于 tarball 建
的孤儿提交，`git pull --ff-only` 必然失败（历史不连续），此时只能 `git reset --hard`。

### 3. 对齐 main 到 origin/main

工作树干净（无未提交改动）时：

```bash
git reset --hard origin/main
```

⚠️ **破坏性命令**，agent 安全机制会拦截，需用户明确授权。执行前确认：
- `git status --short | wc -l` 为 0（工作树干净）
- 本地无需要保留的自定义改动（纯官方代码）
- 旧源码有备份（如 hermes-agent.bak-v0.20.0）

reset 前向用户说明为什么 fast-forward 失败、为什么必须 reset、本地无可丢改动、有备份，
等用户同意再执行。

### 4. 重装依赖

```bash
cd /home/dmin/hermes-agent
unset http_proxy https_proxy  # pip 走清华镜像，不走代理
~/.venv-hermes/bin/pip install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple --no-input
```

cryptography 冲突警告（cryptography 50 vs msal/pyopenssl 要求 <49）是**假冲突**，可忽略
——验证 `python -c "import OpenSSL; OpenSSL.SSL.Context(OpenSSL.SSL.TLS_METHOD)"` 无报错
即正常。

### 5. 迁移配置 + 验证

```bash
hermes config migrate    # 自动迁移到新版本 config 版本号
hermes --version
# 核心模块导入健康检查
~/.venv-hermes/bin/python -c "import hermes_cli.main, run_agent, model_tools, toolsets; print('核心模块导入 OK')"
hermes doctor | grep -E '✓|Found .* issue'
```

### 6. 收尾

- 告知用户：**退出重开 Hermes** 让升级完全生效（editable 安装已指向新代码，重开会加载干净环境）
- 旧备份可保留数天，确认稳定后删：`rm -rf /home/dmin/hermes-agent.bak-v0.20.0`

## 版本策略

`git reset --hard origin/main` 追的是官方 **main 开发分支**（日常持续提交），不是稳定发布
tag。若用户想要只追正式发布版，需改策略：`git fetch --tags` 后 checkout 到最新 tag。

## 相关参考

- `hermes-agent` skill 的 `references/non-git-upgrade-wsl-network.md`（tarball→git 转换
  历史与完整网络笔记）
- 首次 tarball 升级下载大 tarball 时用 `background=true` 绕过 600s 前台超时
