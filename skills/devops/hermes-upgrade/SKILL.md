---
name: hermes-upgrade
description: Hermes Agent 代码升级：git/官方/混合仓库三种安装方式，含 China 网络 GitHub 镜像下载。
triggers:
  - hermes 升级 / hermes update / 版本落后 / commits behind
  - 升级到最新 / 同步版本 / v0.x 升级
  - 阿里云 hermes 升级 / 服务器升级
  - 混合仓库 / 数据仓库+源码 / untracked 源码
  - github 下载慢 / git fetch 卡死 / 镜像加速 / gh-proxy
---

# Hermes Agent 升级

## 概述

Hermes Agent 有三种安装方式，升级路径完全不同。**第一步永远是诊断安装方式**，
然后选对应路径。诊断错误（如在混合仓库上跑 hermes update）会导致升级被静默跳过。

## When to Use

- 用户要求升级 Hermes（本机、阿里云、Windows 任一端）
- `hermes version` 显示 "N commits behind"
- 多端版本不一致需要对齐
- GitHub 下载慢/卡死需要镜像加速

## Prerequisites

- `hermes version` 可运行
- 目标机器 SSH 可达（阿里云公钥已配，直接 `ssh root@47.103.27.171`）
- China 网络环境：准备 gh-proxy.com 镜像

## 步骤 0：诊断安装方式（决定升级路径）

```bash
hermes version          # 看 Install method + Install directory
git remote -v           # 混合仓库识别：origin=hermes-data + upstream=NousResearch
git ls-files | cut -d/ -f1 | sort | uniq -c | sort -rn | head
# tracked 顶层是 skills/memories/obsidian-vault 等数据目录 → 混合仓库
```

| 安装方式 | 特征 | 升级路径 |
|----------|------|----------|
| git 官方源码 | `.git` 是上游仓库 | `hermes update` 直接可用 |
| 官方安装脚本 | `/usr/local/lib/hermes-agent`，bash wrapper | `hermes update` 直接可用 |
| **混合仓库**（本机 WSL） | git 里是 hermes-data 数据，源码 untracked | **手动 zip 升级**（见下） |
| pip 安装 | site-packages 里 | `pip install --upgrade hermes-agent` |

## 步骤 1：官方安装 / 纯 git 安装升级

```bash
ssh root@47.103.27.171 'hermes update 2>&1 | tail -40'   # 阿里云
# 或本机：hermes update
```

升级输出解读（v0.15.1→v0.20.0 实测）：
- `npm error engine ... node >=22.22.0` → node 版本低，Web UI 构建跳过，**不影响核心**
- `lazy backend failed to refresh: cannot import name ...` → 代码替换瞬时失败，**重启后自愈**
- `Syncing bundled skills: +N new, ~M user-modified` → 正常
- `Configuration is up to date` → 配置无需迁移

**升级后必须重启服务才生效**（阿里云）：
```bash
systemctl restart hermes-gateway.service && sleep 5 && systemctl is-active hermes-gateway.service
# 三服务：hermes-gateway / hermes-wsl-manager / wecom-bridge；cron 任务不受影响
```

⚠️ **生产服务重启会被安全系统 BLOCKED**：`systemctl restart` 需要用户明确确认。
clarify 超时后系统说 "use your best judgement" 也不能继续——再试仍 BLOCKED。
正确做法：给用户一条命令让他自己在服务器终端跑，或等用户明确回复「继续」。

## 步骤 2：混合仓库手动升级（本机 WSL 关键路径）

`hermes update` 有 **fork 保护**：origin 是 fork（hermes-data）且有本地领先提交时
静默跳过升级。手动升级流程：

1. **下载官方 zip**（China 网络别用 git fetch，见步骤 3）
2. **解压** → `/tmp/hermes-upstream/hermes-agent-main/`
3. **rsync 覆盖源码**，排除全部 tracked 数据文件（不带 --delete）：
   ```bash
   rsync -a /tmp/hermes-upstream/hermes-agent-main/ . \
     --exclude='.git' --exclude='venv' --exclude='.env' \
     --exclude='.gitignore' --exclude='.gitattributes' \
     --exclude='skills/' --exclude='memories/' --exclude='obsidian-vault/' \
     --exclude='config.yaml' --exclude='cron/' --exclude='outputs/' \
     --exclude='scrapling/' --exclude='claw-memory/' \
     --exclude='sync-push-wsl.sh' --exclude='sync-pull-wsl.sh'
   ```
   原则：排除 `git ls-files` 里的用户数据；上游 zip 只有上游文件，只需排除
   与上游同名的数据目录（skills/、cron/、scripts/）和顶层用户文件
4. **更新依赖**：`venv/bin/pip install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple`
   （实测仅少量依赖变化，如 nemo-relay 0.6→0.7）
5. **清理**：删 `__pycache__`（排除 venv/.git）
6. **验证**（⚠️ 别信 hermes version 的 SHA，见陷阱）

## 步骤 3：China 网络下获取最新源码（GitHub 镜像）

**git 传输层在 China 网络静默失败**：`git fetch`/`git ls-remote` exit 0 但无输出、
无引用；但 SSH 裸连和 curl HTTPS 都通。解法 = curl 下载 zip 走加速镜像。

```bash
# 测速（Range 探针）选最快镜像
for url in \
  "https://gh-proxy.com/https://github.com/NousResearch/hermes-agent/archive/refs/heads/main.zip" \
  "https://ghfast.top/https://github.com/NousResearch/hermes-agent/archive/refs/heads/main.zip" \
  ; do
  timeout 25 curl -sS -o /dev/null -w "HTTP:%{http_code} speed:%{speed_download}B/s\n" -r 0-1000000 "$url"
done
# 2026.8.10 实测：gh-proxy.com 11.5MB/s ✅；ghproxy.net 失败(curl 92)；ghfast.top 失败；
# codeload 直连超时；github.com 直连 47KB/s 不可用

curl -sSL --http1.1 --retry 3 -o /tmp/hermes-main.zip \
  "https://gh-proxy.com/https://github.com/NousResearch/hermes-agent/archive/refs/heads/main.zip"
# 66MB 约 1 分钟；unzip 后验证：8680 文件 + pyproject version + run_agent.py 存在
```

## Pitfalls

1. **混合仓库上 hermes version 的 SHA 是假象**：upstream/local/"N commits behind"
   取自 git 数据仓库元数据（数据提交），不是磁盘源码。判定新旧只能 diff：
   ```bash
   diff -rq /tmp/hermes-upstream/hermes-agent-main/ . --exclude=.git --exclude=venv \
     --exclude=skills --exclude=memories --exclude=obsidian-vault --exclude=cron \
     --exclude=scripts --exclude=outputs --exclude=config.yaml --exclude=scrapling \
     --exclude=claw-memory --exclude=.gitignore --exclude=.gitattributes \
     --exclude=hermes_agent.egg-info --exclude=__pycache__ 2>/dev/null | grep -c '^Files .* differ'
   # 0 = 磁盘源码与上游完全一致
   ```
2. **不要在混合仓库跑 hermes update**——它静默跳过（fork 保护），浪费时间且误以为升级了
3. **git clone --filter=blob:none 会 checkout 失败**：clone "succeeded" 但 blob 懒加载
   超时，工作区空。别用，直接走 zip 下载
4. **升级源码后依赖必须重装**（`pip install -e .`），否则新代码 import 新依赖报错
5. **rsync 不带 --delete**：只覆盖不删除，防止误删用户数据
6. 阿里云官方安装的 `hermes version` 显示准确（upstream=真实上游 SHA）；混合仓库
   永远显示旧值——两端对比时别被误导

## Verification

- 官方安装：`hermes version` 显示 "Up to date"
- 混合仓库：diff 计数 0 + `venv/bin/python -c "import run_agent, hermes_constants; print('OK')"`
- 阿里云：三服务 active + 无错误日志 + cron 列表完好

详细实战见 `references/hermes-mixed-repo-upgrade.md`。
