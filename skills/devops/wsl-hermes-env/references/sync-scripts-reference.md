# 同步脚本参考（2026.6.4 重写）

## 文件位置

所有文件在 Windows 桌面：`C:\Users\Admin\Desktop\`

| 文件 | 用途 |
|------|------|
| `Hermes_Sync_Push.bat` | 双击推送（下班前） |
| `Hermes_Sync_Pull.bat` | 双击拉取（上班时） |
| `Hermes_Sync_Check.bat` | 环境检查诊断 |
| `sync-push.sh` | 被 .bat 调用的推送脚本 |
| `sync-pull.sh` | 被 .bat 调用的拉取脚本 |

## .bat 编码陷阱（重要）

**不要用中文命名的 .bat 文件！** 即使加了 `chcp 65001`，Windows cmd.exe 仍会以 GBK 解析中文字符，导致 `wsl` 命令被切成乱码碎片，静默失败。全部用英文命名。

## 仓库

- 路径：`/mnt/c/Users/Admin/hermes-sync/`
- 远程：`git@github.com:jsxuaijun-art/hermes-data.git`（SSH）
- 分支：`main`
- SSH 已验证连通：`ssh -T git@github.com` 秒过

## 推送逻辑（sync-push.sh）

1. 从 `~/.hermes/` 复制 SOUL/memories/skills 到仓库目录
2. `git add -A` + `git commit`
3. `git pull --rebase origin main`（防冲突，冲突自动用本地版本）
4. `git push origin main`
5. 所有 git 网络操作用 `timeout` 保护（10s/15s/20s）

## 拉取逻辑（sync-pull.sh）

1. `timeout 10 git fetch origin`
2. 对比 `HEAD` vs `origin/main`，有更新才 pull
3. `timeout 15 git pull --rebase`
4. 从仓库复制回 `~/.hermes/`

## 冲突处理

推送时 pull --rebase 冲突 → 遍历 `git diff --name-only --diff-filter=U` → 每个文件 `git checkout --ours` → `git rebase --continue`。始终保留本地版本。
