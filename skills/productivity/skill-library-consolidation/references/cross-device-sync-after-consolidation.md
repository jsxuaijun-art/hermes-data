# 整合结果跨设备同步（GitHub）— 实测记录

2026-09 实操：把 5 个话术 skill 整合成 `communication/sales-communication`（含新增「通用话术模块」9 文件），删 4 个源 skill，推到 `jsxuaijun-art/hermes-data` 供其它电脑使用。以下为实测通过的命令与验证方法。

## 背景事实（本机 Home / WSL）

- 同步仓库：`git@github.com:jsxuaijun-art/hermes-data.git`（唯一 HERMES_REPO）
- 本机同步夹：`/mnt/c/Users/Admin/hermes-sync`（Home 机；Office 机是 `C:\Users\Administrator\Desktop\HermesAgent`）
- 推送脚本：`hermes_push.sh`（在 `skills/devops/hermes-data-sync/scripts/`），流程 = rsync WSL→同步夹 → pull --rebase → git add -A → sync_guard → commit → push

## 关键：skills 的 rsync 是去 --delete 的

`hermes_push.sh` 里 skills 的 rsync **不带 --delete**（防多机误删远端 skill）。后果：**被整合删除的源 skill 目录在同步夹里原样保留**，git add -A 不会把它们当删除。必须先在同步夹手动删：

```bash
cd /mnt/c/Users/Admin/hermes-sync
rm -rf "skills/compliant-accounting/price-negotiation" \
       "skills/enterprise-diagnostic" \
       "skills/marketing/client-group-welcome" \
       "skills/compliant-accounting/client-communication"
```

删完 git 仍跟踪它们 → 后续 add -A 会正确记录为删除。新建母skill 由 rsync 自动加入，无需手动拷。

## sync_guard 拦删除 → 故意删除用 BYPASS

sync_guard 的「缺失阻断」会检测到「git 有、本机缺被整合 skill」→ 中止推送（防的是"推送机技能不全把远端 skill 当删除"——但这次删除是**故意的整合**）。脚本明文支持：

```bash
cd ~ && export SYNC_GUARD_BYPASS=1 && bash ~/.hermes/skills/devops/hermes-data-sync/scripts/hermes_push.sh
```

## git 把内容相同的搬迁识别成 rename

把旧 SKILL.md 原文复制进母skill 后，git 在 commit 里显示 `rename old → 母skill/references/xx/xxx.md (100%)` 而非 delete+add。所以 `git show --stat` 看到的是 rename 属正常，不是没删。

## 验证删除是否真进 HEAD —— 退出码陷阱

**`git ls-files <路径>` 对不存在的路径也返回退出码 0**（空输出照样成功）。用它做 `&& echo 仍在 || echo 已移除` 会全部误判成"仍在"（本次实测踩中）。

正确验证（存在才退出 0）：

```bash
if git cat-file -e "HEAD:skills/xxx/SKILL.md" 2>/dev/null; then
  echo "HEAD中仍存在"; else echo "HEAD中已移除"; fi
```

或 `git ls-tree HEAD -- <路径>`（有输出 = 存在）。

## 验证远端真的推上去了

不只看 push 成功信息：

```bash
cd /mnt/c/Users/Admin/hermes-sync
git log --oneline -1          # 本地 HEAD
git ls-remote origin main     # 远端 sha，应与本地 HEAD 一致
git ls-files skills/communication/sales-communication/SKILL.md   # 母skill 已跟踪
```

## 其它电脑使用

目标机双击 `Hermes同步-拉取.bat`（git fetch+reset 同步夹 → rsync 进 `~/.hermes/`），然后 `skill_view name=sales-communication` 应 available。拉取会顺带删掉那 4 个旧 skill——正是整合想要的效果。拉取前确认目标机无未推送本地修改（fetch+reset 会丢弃）。
