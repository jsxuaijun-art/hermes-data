# 苏州政策监控 Cron — 运维与验证（2026.9.20 实测 / 9.21 更新）

本模块的政策监控任务的部署细节与验证方法。动这个任务前先读这篇 + SKILL.md。

## 任务标识

- cron 名：`苏州城市破播政策监控`，job id `72d7d5389d6d`
- 计划：`0 9 * * 2,5`（周二/周五 09:00，徐总决策1）
- 模式：`--script sz_policy_monitor.py --no-agent`（脚本 stdout = 整条任务，无新增则空 stdout 静默不推送）
- deliver：`wecom:wrBqtFBgAAFbj6ydc54nuVdDcLmMxgIg`（**徐江机器人·内部群**，2026.9.20 徐总拍板从单聊 `wecom:XuAiJun` 改到群；此前另一个任务曾在某群报 93001 `not allow send msg in room`，属另一任务/渠道，与本任务无关）
- 脚本：`~/.hermes/scripts/sz_policy_monitor.py`（与 skill `scripts/sz_policy_monitor.py` 同源）
- 素材库：`~/.hermes/city-breakout/sz_policy_lib.json`

## ⚠️ 硬前提：gateway 必须在线（2026.9.21 实测）

cron 调度器（ticker）由 gateway 托管（systemd `hermes-gateway.service`）。
**gateway 不在线/崩溃循环 → 周二/五永远不会自动触发**，不管 job 配得多对。

检查三步：
```bash
systemctl --user status hermes-gateway.service   # active? Main PID 是否每 ~20s 变?
hermes gateway status                            # 目标平台 connected?
journalctl --user -u hermes-gateway --no-pager -n 40 | grep -iE "import|error|traceback"
```

⚠️ **"active"≠健康**：2026.9.21 实测 gateway 在疯狂崩溃重启（restart counter
4234），根因是混合目录版本失配——`gateway/run.py` import
`scheduler_for_profile_mode` 而 `cron/scheduler_provider.py` 无此函数 →
启动即崩 ImportError，cron 完全停摆。修复见 `hermes-git-upgrade-repair`
skill「gateway 崩溃循环」一节（补函数 + 重启验证）。该修复已完成，
重启 gateway 后应看到 restart counter 不再涨、wecom connected。

## 验证顺序（防"以为通了其实没通"）

1. **先独立跑脚本**：`python3 ~/.hermes/scripts/sz_policy_monitor.py`；exit 0 且输出 NEW 列表 = 脚本健康。
2. **确认 gateway 在线**（见上节）——不在线则一切定时触发免谈。
3. 真报错看 `grep "<job_id>" ~/.hermes/logs/errors.log` —— 脚本失败的真 traceback 在这里，不是 cron runs 输出里。
4. 手动验证可走 `hermes cron run <id>`（**2026.9.21 起已可用**，见下节）；但手动 run 是独立进程（source=direct），**succeeded ≠ 已投递**——投递依赖常驻 gateway，最终闭环 = gateway connected → 触发 → gateway.log 有 send 记录 → **群里真实收到**。
5. 定时验证：周二/五真实 tick 后，`hermes cron runs <id>` 应有一条 completed 执行，并到**群里确认收到**（不能只看 cron 输出）。

## 已修 bug：`hermes cron run <id>` 曾报 "Ran now: failed."

2026-09-20 实测，手动/immediate run 路径在此仓库坏掉：

```
claim_job_for_fire() got an unexpected keyword argument 'return_job'
```

根因：`cron/jobs.py::claim_job_for_fire(job_id, *, claim_ttl_seconds=300)` 返回 bool，但
`tools/cronjob_tools.py` L834 / L1176 以 `return_job=True` 调用并期望返回 job 字典 ——
版本失配。

**✅ 已修复（2026.9.21）**：给 `jobs.py` 的 `claim_job_for_fire` 加 `return_job=False`
可选参数（True 时成功返回 job dict，向后兼容旧 bool 语义）；
`tests/cron/test_claim_job_for_fire.py` 3/3 通过；`hermes cron run <id>` 从
failed → "Ran now: succeeded"。修法模板：先在旧文件里补缺失符号/参数，不要改
调用方（调用方已是新版语义）。

## 群 chat_id 定位法

群 deliver 目标 = `wecom:<群chat_id>`；单聊才用用户名（如 `wecom:XuAiJun`）。群 chat_id 从
`state.db` 的 sessions / gateway_routing 查（无 sqlite3 CLI 时用 python3 查），群 session key
形如 `agent:main:wecom:group:<chat_id>:<user_id>`。示例：`wrBqtFBgAAFbj6ydc54nuVdDcLmMxgIg` = 徐江机器人
内部群（成员 XuAiJun + GaoJiHuiJiShianna）。deliver 前缀 `wecom:` 在 gateway 侧 split 为
platform + target；群/单聊的区分由 adapter 的 chat_id 处理，不在 `_parse_target_ref` 特殊化。