# AI Agent 创建技能后的同步工作流

## 问题

当 Hermes Agent（AI）在对话中通过 `skill_manage` 创建/更新技能时，技能文件存放在 **WSL 的 `~/.hermes/skills/`** 下。但 Git 仓库在 **Windows 文件系统** 的 `/mnt/c/Users/Administrator/Desktop/HermesAgent/skills/`。

两者之间**没有自动同步**——即使用户随后跑 `Hermes同步-推送.bat`，也需要确认该 .bat 的步骤1是否真的从 WSL 拷贝了 skills 到 Windows。

## 当前推送脚本的覆盖情况

根据 `references/bat-scripts-inline-2026-05.md`，推送脚本步骤 [1/4] 包含：

```bash
cp -rf ~/.hermes/skills/* /mnt/c/Users/Administrator/Desktop/HermesAgent/skills/
```

✅ 理论上推送脚本已经覆盖了技能同步。但如果：
- 脚本版本旧（不含此行）
- 或 `~/.hermes/` 路径写错（用户名不对）
- 或用户只拉了没推

则技能不会到达 GitHub。

## 保险流程

```bash
# 1. 确认技能已创建
ls -la ~/.hermes/skills/<技能名>/

# 2. 复制到 Windows git 仓库
cp -rf ~/.hermes/skills/<技能名> \
  /mnt/c/Users/Administrator/Desktop/HermesAgent/skills/

# 2b. 或批量复制所有技能
cp -rf ~/.hermes/skills/* \
  /mnt/c/Users/Administrator/Desktop/HermesAgent/skills/

# 3. 推送
cd /mnt/c/Users/Administrator/Desktop/HermesAgent
git add -A
git commit -m "sync skills"
git push origin main
```

## 验证

```bash
git ls-tree -r origin/main --name-only | grep skills/<技能名>
```

## ⚠️ 常见陷阱

| 陷阱 | 症状 | 修复 |
|------|------|------|
| 驱动脚本不含 `cp skills` 步骤 | 推送成功提示但 GitHub 没技能 | 检查推送 .bat 的步骤1是否有 skills 的 cp |
| WSL 用户名写错 | `cp` 命令静默失败（路径不存在） | 确认 `whoami` 输出与脚本路径匹配 |
| 只拉了没推 | 技能只在本地 WSL | 跑推送脚本 |
| 技能是在家里电脑创建的 | 办公室拉取后没有该技能 | 先在家跑推送，再到办公室跑拉取 |
