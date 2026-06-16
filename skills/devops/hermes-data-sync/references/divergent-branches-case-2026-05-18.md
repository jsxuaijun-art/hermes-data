# 分叉分支案例（2026-05-18）

## 场景

办公室电脑运行 `Hermes同步-拉取.bat`（桌面），报以下错误：

```
wsl: 检测到 localhost 代理配置，但未镜像到 WSL。NAT 模式下的 WSL 不支持 localhost 代理。
From github.com:jsxuaijun-art/hermes-data
 * branch            main       -> FETCH_HEAD
hint: You have divergent branches and need to specify how to reconcile them.
hint:
hint:   git config pull.rebase false  # merge
hint:   git config pull.rebase true   # rebase
hint:   git config pull.ff only       # fast-forward only
hint:
hint: You can replace "git config" with "git config --global" to set a default
hint: preference for all repositories. You can also pass --rebase, --no-rebase,
hint: or --ff-only on the command line to override the configured default per
hint: invocation.
fatal: Need to specify how to reconcile divergent branches.
[ERROR] Pull failed, check network
```

## 根因

用户在多个电脑上各自有未推送的 commit（比如家里电脑推送了新 skill，办公室电脑也有本地改动），导致本地分支与远程 `origin/main` 分叉。`git pull` 在没有配置 pull 策略时拒绝执行。

## 当时处境

- **办公室电脑**：桌面 `.bat` 文件仍在用 `git pull`（旧版），未更新为 `fetch + reset --hard`
- **`.bat` 文件位置**：`C:\Users\Administrator\Desktop\Hermes同步-拉取.bat`，不在 git 仓库中，无法通过同步更新
- **更新方式**：需要人肉在每台电脑上双击修改后的 .bat，或通过 U 盘拷贝新版

## 修复方案

### 短期：手动修复本次运行

```bash
# 从 WSL 内执行
cd /mnt/c/Users/Administrator/Desktop/HermesAgent
git config pull.rebase true
# 重试拉取
git pull origin main
# 或走 fetch + reset
git fetch origin main && git reset --hard origin/main
```

### 长期：批量替换桌面 .bat

用 `fetch + reset --hard` 替代 `git pull`。已完成参考文件更新：
- `references/bat-scripts-inline-2026-05.md` 中的拉取脚本已使用 `fetch + reset --hard`
- SKILL.md 中的 `sync-pull.sh` 也同步更新

### 预防：设置全局 pull.rebase

```bash
git config --global pull.rebase true
```

这样即使某个脚本仍用 `git pull`，也不会弹出交互提示（自动选 rebase 模式）。
