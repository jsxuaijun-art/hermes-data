# 群消息延迟排查指南

> 用途：当用户反馈"群里@了机器人没回复"时，追溯消息流向，定位瓶颈。
>
> 发现于：2026.5.10 全员群@未及时响应事件

---

## 排查步骤

### Step 1：确认网关是否收到消息

```bash
cat ~/.hermes/logs/gateway.log | grep "inbound message" | grep "group:"
```

关键信号：`inbound message: platform=wecom user=XuAiJun chat=<group_id> msg='...'`

如果搜不到 → 消息没到达网关 → 问题在企微平台侧（机器人没被拉入群 / 关键词没触发 / 企微推送故障）

### Step 2：确认网关是否发出响应

```bash
cat ~/.hermes/logs/gateway.log | grep "response ready" | grep "group:"
```

关键信号：`response ready: platform=wecom chat=<group_id> time=123.9s api_calls=11 response=1249 chars`

- `time=` → 处理耗时（秒）。> 60s 即为"用户感知不可接受"
- `api_calls=` → API调用次数。次数多通常意味着长上下文或多轮工具调用
- 如果搜不到 → agent 可能卡死或崩溃，查 `errors.log`

### Step 3：还原时间线

```bash
cat ~/.hermes/logs/gateway.log | grep -E "(23:3[0-9]:|group:|dm:XuAiJun)" | tail -20
```

按时间戳排序，还原用户操作的完整链条：

```
23:31:06  DM响应（😄）
23:33:01  群消息到达 → 开始处理
23:33:37  用户DM质问"为什么不回复"
23:35:05  response ready（耗时124秒）
```

### Step 4：判断瓶颈类别

| 模式 | 特征 | 根因 |
|:--:|:--|:--|
| 消息到→无响应 | gateway收到但无response ready | agent崩溃/超时/死循环 |
| 消息到→响应慢 | time > 60s | 串行排队 + 长上下文 |
| 消息未到 | gateway日志无inbound | 企微平台过滤/推送故障 |
| 响应发出→用户没看到 | response ready有，用户说没收到 | 企微推送失败/群配置问题 |

### Step 5：串行排队确认

检查时间线上 DM 和群消息的交替模式：

```bash
cat ~/.hermes/logs/gateway.log | grep -E "(inbound message|response ready)" | awk '{print $1, $2, $9, $NF}'
```

如果连续出现 `dm:XuAiJun` 的 inbound-response 序列，中间插入了 `group:` 的 inbound 但没有立即的 response → 确认串行排队发生。

---

## 常见修复

| 问题 | 修复 |
|:--|:--|
| 串行排队延迟 > 60s | 对群@先发短响应"收到，正在处理"占位，再长篇推理 |
| 消息未到 | 检查企微后台AI机器人配置 → 是否拉入群 → 是否开启关键词 |
| agent处理卡死 | 重启gateway: `pkill -f "hermes.*gateway"` 再重跑 |
| WebSocket断开 | 自动重连机制存在，检查日志是否有 "Reconnected" |

---

## 用户预期速查

| 用户 | 通道 | 可接受等待 | 超时行为 |
|:--:|:--|:--:|:--|
| 江姐 | 群@ | < 30秒 | 切DM质问 |
| 江姐 | DM | 即时（< 5秒） | 连续发送追问 |
| 盈信同事 | 群@ | < 60秒 | 可能重复@ |
| 外部客户 | 群@ | 按时间感知策略 | 联系人类同事 |
