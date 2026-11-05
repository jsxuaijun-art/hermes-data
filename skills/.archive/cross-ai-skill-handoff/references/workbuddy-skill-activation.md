# WorkBuddy 技能激活机制实测（2026-09 修正：junction 全激活；「只报 1 个」是扫描误报）

> ⚠️ 本文件的旧版结论「junction 不激活、必须改物理复制」已被推翻并修正。
> 修正依据：本轮让 WorkBuddy 自己重新扫描自查，反馈为 58/58 全部激活、零断链、frontmatter 全合规。
> 之前的「只报出 1 个」是其异步技能索引**扫描未完成时的误报**。

## 症状（原始）

58 个技能全部以 junction 装进 `C:\Users\Admin\.workbuddy\skills\`，Codex/Claude Code 两端 OK，
但 WorkBuddy 初查只报出 1 个技能，用户问「其他的为什么没成功」。

## 排查过程（保留当时的判断链，供对照）

1. **文件系统层面 junction 完全合法**：`cmd /c dir C:\Users\Admin\.workbuddy\skills`
   显示 58 个 `<JUNCTION>` → `\??\D:\obsidian-vault\50-Skills\<技能>`，Windows 能解析，没坏。
2. **WorkBuddy 文件监听器确实看到了**：`~/.workbuddy/logs/<日期>/__workbuddy_cli_host__*.log` 里
   逐条出现 `[HotReload] Triggered by skills change: C:\...\skills\<技能>` + `[HotReload] Completed for skills`。
3. **WorkBuddy 自带技能当时全是物理目录**（agent-memory / browser-use / github / ZenStudio / gog…），
   这一点曾诱导出「加载器只认物理目录」的错误推断。

## 真实结论（修正后）

1. **junction 被 WorkBuddy 正常加载并激活**：自查报告 58 个链接全部在列、可直接调用、零断链，
   frontmatter 58/58 通过（name 与目录名一致）、无禁用标记。
2. **「只报 1 个」= 扫描未完成/异步索引滞后的误报**：不是架构失败，是时序问题。
   `[HotReload] ... Completed` 只证明 watcher 收到了变更，技能面板/注册表刷新有延迟。
3. **物理目录 → junction 的转换也被接受**：把唯一的本地物理技能
   （`hermes-credential-rotation`，原为物理目录）转成 junction 后 WorkBuddy 照常加载。
   WorkBuddy 自查时点了名要求它同步进 50-Skills 并改成链接式——与旧结论完全相反。

## 教训（现在有效）

- **工具报出偏低数量 → 先让它自查/刷新完再下结论**。WorkBuddy（及任何带异步技能索引的工具）
  初查结果可能是扫描快照，不是最终状态。旧结论差一点就触发「58 个 junction 全改物理副本」的
  破坏性操作——幸好行动前先让 WorkBuddy 自查。
- **验收以「工具自报清单」为准**：文件系统计数（`cmd dir | grep -c JUNCTION`）与
  `[HotReload]` 日志都只证明链接存在，不证明激活；让工具自己报数才是验收。
- 修正动作要保持最小化：先自查、再重启/刷新、最后才考虑换架构。

## 排查/操作命令（仍有效）

```bash
# 1) Windows 原生看 junction vs 物理目录
cmd.exe /c "dir C:\Users\Admin\.workbuddy\skills" | grep -iE "JUNCTION|<DIR>"   # 数 JUNCTION
# 2) 技能目录当前形态（WSL 侧）
ls -la /mnt/c/Users/Admin/.workbuddy/skills/        # l 开头=联接，d 开头=物理目录
# 3) 看 watcher 是否检测到（检测≠激活，仅作时序参考）
grep -aE "HotReload|skills change" ~/.workbuddy/logs/<日期>/__workbuddy_cli_host__*.log
# 4) 物理目录转 junction（实测流程）
rm -rf /mnt/c/Users/Admin/.workbuddy/skills/<技能>                  # WSL 删物理目录
powershell.exe -NoProfile -Command "New-Item -ItemType Junction -Path 'C:\Users\Admin\.workbuddy\skills\<技能>' -Target 'D:\obsidian-vault\50-Skills\<技能>' -Force"
[ -f /mnt/c/Users/Admin/.workbuddy/skills/<技能>/SKILL.md ] && echo OK # WSL 侧可解析
# 5) 让 WorkBuddy 自查：重启后问它/让它列技能清单（勿数文件系统条目当结果）
```