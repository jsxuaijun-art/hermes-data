# Memory-Reminder — Codex AGENTS.md startup fragment

把以下整段加入（或合并到）你的 `~/.codex/AGENTS.md` **第 1 节**：

```markdown
## 1. Session Startup

**Codex 没有 SessionStart hook，每次会话开始时模型必须主动执行**：

1. 读 `~/.codex/memories/MEMORY.md`（若按项目分则改为 `<project>/memory/MEMORY.md`）
2. 读 `~/.codex/memories/reminders.md`（若存在）
3. 检查 8h cooldown stamp `~/.codex/memories/.last-reminded`：
   - 用 Bash 跑 `[ -f ~/.codex/memories/.last-reminded ] && echo $(($(date +%s) - $(cat ~/.codex/memories/.last-reminded)))`
   - 若小于 28800 秒（8 小时）→ 输出一句 `[startup] SKIP: tier check done X min ago, answering directly` → 直接答用户当前问题
   - 否则 → 进入完整 tier check 流程（步骤 4）
4. **完整 tier check 报告**（必须在答用户首条问题之前输出）：
   - 今日日期 + Now 时分
   - **boundary**：列出条目跨 7/30 天线需 move/archive 的（无则一句"无"）
   - **verified**：若今日为本月 1 号 → 列所有 [H] 条目让用户确认 still-in-use；否则一句"非月初，跳过"
   - **extraction**：若今日为 15 号或月末 → 触发模式提取（写 patterns.md）；否则一句"非提取日，跳过"
   - **reminders**：列今日到期 ⚠️ / 超期 🔴 / 3 天内 📅 / on-demand 常驻；on-demand 超 14 天 → 加 ❓ 问询
   - **建议动作**：若全部正常一句 "当前分级正确"
5. 写 stamp：`date +%s > ~/.codex/memories/.last-reminded`
6. 然后才回答用户当前问题
```

## 可选裁剪

如果你 codex 用得不像 CC 那么频繁多窗口（比如一天就开一次），可以**去掉 8h cooldown 那一段**——直接每次启动跑完整 tier check 即可。

## 配套数据

`~/.codex/memories/MEMORY.md` 应包含：
- User Info（你的角色、偏好）
- Preferences
- Memory Policy（分级规则，模板见 `../templates/MEMORY.md`）
- 主题索引
- Recent Memory（鲜明 / 精炼 / 长期三段）

`~/.codex/memories/reminders.md` 用模板（见 `../templates/reminders.md`）。

## 配套自然语言识别

让 codex 主 agent 在对话中识别这些表达并自动写 `reminders.md` / 标 done：

- "提醒我 X" / "remember X" → 加 reminder
- "X 月 Y 日 Z" → 加日期型 reminder
- "搞定/做完/完成 X" → 标 done
- "X 不做了 / 取消 / 算了" → 删除该条

这部分逻辑也来自 `templates/MEMORY.md` 顶部的 Memory Policy 段，codex 主 agent 读完会按规则执行。

## 验证

下次开 codex：
- 第一次开（没 stamp）→ 应见 `REQUIRED` + 完整报告
- 8 小时内再开 → 应见 `SKIP` + 直接答你
- 8 小时后再开 → 又是 `REQUIRED`
