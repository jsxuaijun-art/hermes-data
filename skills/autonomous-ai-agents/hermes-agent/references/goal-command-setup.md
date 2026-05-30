# `/goal` 命令 — 配置与故障排查

## 前置条件

`/goal` 需要一个 **Judge 辅助模型** 来判定目标是否完成。需在 `config.yaml` 中配置：

```yaml
auxiliary:
  goal_judge:
    provider: auto          # 自动沿用主 provider（或指定如 deepseek/openrouter）
    model: ''               # 空 = provider 默认模型；可指定便宜模型省成本
    base_url: ''
    api_key: ''
    timeout: 30
    extra_body: {}
```

**不加这段 → `/goal` 报错**："no auxiliary client configured" 或静默跳过。

## 典型报错及原因

| 报错内容 | 根因 | 解决 |
|:--|:--|:--|
| `no auxiliary client configured` | config.yaml 缺 `auxiliary.goal_judge` | 加上面那段配置 |
| `auxiliary client unavailable` | import 或 provider 初始化失败 | 检查 provider 是否正确 |
| Judge 连续返回空 → 自动暂停 | Judge 模型太弱，无法输出 JSON 格式结果 | 换靠谱的模型（deepseek 可） |
| `judge error: APITimeoutError` | 网络或超时 | 增大 `timeout`（默认30s） |
| `Error: [Errno 36] File name too long` | 长文本 `/goal <长中文...>` 被 `_detect_file_drop()` 当成路径传给 `os.stat()`，触发 Linux ENAMETOOLONG | 在 `cli.py` 的 `_detect_file_drop()` 中加早期退出：如果输入以 `/` 开头且 `_looks_like_slash_command()` 返回 True，直接 return None（跳过 `_resolve_attachment_path`）。已修复于 v0.13.0+ 补丁。 |

## 调用链路（排查用）

```
/goal set
  → GoalManager.set()                   # 存目标到 SessionDB
  → AIAgent.run_conversation()          # 正常回复
  → GoalManager.evaluate_after_turn()   # 调用 Judge
    → get_text_auxiliary_client("goal_judge")
      → _resolve_task_provider_model("goal_judge")
        → config["auxiliary"]["goal_judge"]   # 没有 → 返回 "auto"
      → resolve_provider_client("auto", ...)  # auto 检测可用 provider
    → judge_goal(goal, response)        # 发 Judge 请求
      → 解析 JSON 结果 {done, reason}
  → 未完成 → 自动续跑（最多 max_turns 次）
  → 完成 → 通知用户
```

## 辅助命令

| 命令 | 作用 |
|:--|:--|
| `/goal <text>` | 设定跨轮次目标 |
| `/goal pause` | 暂停（新消息打断时会自动暂停） |
| `/goal resume` | 继续被暂停的目标 |
| `/goal status` | 查看目标状态和轮次 |
| `/goal clear` | 清除当前目标 |
| `/subgoal <text>` | 追加附加条件（Judge 同时评估） |
| `/subgoal remove N` | 移除第 N 条附加条件 |
| `/subgoal clear` | 清空所有附加条件 |

## 配置参数

```yaml
goals:
  max_turns: 20        # 单次 /goal 最大自动续跑轮数（默认20，防死循环）
```

可在 config.yaml 的 `goals:` 段调整。

## 设计要点

- Judge 是 fail-open：失败了默认判 `continue`，不卡死
- 用户中途发消息 → 打断自动续跑（但会暂时 pause 目标）
- Judge 模型每次调用只消耗几十 token，成本可忽略
- State 持久化在 SessionDB 的 `state_meta` 表（key = `goal:<session_id>`）
- `/resume` 恢复会话时自动检查是否有未完成的目标
