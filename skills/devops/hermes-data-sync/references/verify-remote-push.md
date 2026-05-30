# 排查"我已推送但远程没有"的步骤

## 场景

用户从家里电脑推送了文件（如 `tax-planning-fin-analysis-industry`），但办公室电脑拉取后找不到。

## 排查命令

```bash
# 1. 比较本地 HEAD vs 远程 HEAD
git fetch origin main --quiet
echo "本地: $(git rev-parse --short HEAD)"
echo "远程: $(git rev-parse --short origin/main)"
echo "本地落后: $(git rev-list --count HEAD..origin/main)"
echo "本地超前: $(git rev-list --count origin/main..HEAD)"

# 2. 远程有你要的文件吗？
git ls-tree -r origin/main --name-only | grep -i "关键词"

# 3. 远程没有任何新 commit → 家里没推成功
```

## 常见原因

| 原因 | 确认方式 | 解决 |
|------|---------|------|
| 推送时网络超时（从中国连 GitHub 不稳定） | 家里电脑 git push 报错信息有 `schannel` / `GnuTLS` / `timeout` | 重推 |
| 推到了错误仓库（`hermes-agent` vs `hermes-data`） | 检查家里电脑 `.git/config` remote URL | 修正远程地址后重推 |
| 只 commit 没 push | 家里电脑 `git status` 显示 ahead | 补跑 `git push` |
| 文件生成后没 git add | 家里电脑 `git status` 显示 untracked 文件 | `git add` → `commit` → `push` |
| 推了但拉取脚本报分叉错误 | 办公室电脑 `git pull` 分叉拒绝 | 已修复为 `fetch + reset --hard` |

## 预防措施

在推送脚本中增加提交确认：

```bash
# 推完后确认
sleep 2
echo ">> 验证推送..."
git fetch origin main --quiet
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)
if [ "$LOCAL" = "$REMOTE" ]; then
  echo ">> ✓ 远程已确认更新"
else
  echo ">> ⚠ 远程与本地不一致，可能没推成功"
fi
```
