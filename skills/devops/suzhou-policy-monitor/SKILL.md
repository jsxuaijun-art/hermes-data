---
name: suzhou-policy-monitor
description: 苏州政策自动监控网页 — cron定时抓取+企微群推送+两处代码修复。部署城市破播素材库、换机重配、加监控方向时用。
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [cron, policy, suzhou, wecom, scraper]
    category: devops
---

# 苏州政策监控（城市破播素材自动采集）

## When to Use

- 用户说"苏州政策监控""城市破播素材""政策一出第一时间知道"，或让加监控方向
- 换电脑/重配 Hermes 后要恢复苏州政策推送
- gateway 崩溃重启(restart counter 狂涨)、cron 不调度、企微推送不通时排查

## 定位

徐总「城市破播」短视频类型的素材引擎：自动抓取苏州/江苏/国家可落苏的政策，去重入库，周二/周五定时把**新鲜**政策推送到企业微信内部群「徐江机器人」。文案创作见 `short-video-copywriting` 类型的城市破播章节。

## 已部署资产（当前机器）

- **脚本**：`~/.hermes/scripts/sz_policy_monitor.py`（cron 必须放 `~/.hermes/scripts/`）
- **素材库**：`~/.hermes/city-breakout/sz_policy_lib.json`（唯一源 + 条目，去重键=文号或URL尾）
- **cron 任务**：`hermes cron list` 里 `苏州城市破播政策监控`（72d7d5389d6d），周二/周五 9:00，no-agent，deliver=`wecom:wrBqtFBgAAFbj6ydc54nuVdDcLmMxgIg`
- **gateway**：systemd `hermes-gateway.service`（跑 cron 调度 + wecom 连接，必须活着才能推送）

## 核心原理

- 苏州政务网栏目列表页是 **JS 渲染**，requests 抓不到结构化列表 → 监控**不硬爬政务网**，改用 anysearch 搜关键词 + 文号/URL 去重
- 链路：`cron(周二五9点) → sz_policy_monitor.py → anysearch batch_search 8路关键词 → 域名白名单 + 外省/垃圾黑名单过滤 → 去重入库 JSON → 只输出"新鲜"(≤45天)新增 → gateway 推企微群`
- **新鲜度过滤**：旧文档(URL/文号已见)只入库存、不推送，避免把几个月前的政策当"新发现"噪音推(2026-09 徐总反馈低空条例也被当新)

## 加一个监控方向（最常用操作）

1. 编辑 `~/.hermes/scripts/sz_policy_monitor.py` 的 `QUERIES` 列表，加一行关键词（例如 `"苏州 XX产业 政策"`）
2. 若新领域有政府专用域名，把域名加进 `WHITELIST_HOSTS`
3. 可选：调小 `FRESH_DAYS`（默认45）让更新政策更快触发
4. 保存后手动跑一次验证：`python3 ~/.hermes/scripts/sz_policy_monitor.py`（应输出或静默，不报错）
5. 重启 gateway 让 cron 生效：`hermes gateway restart`

## 换机重配（一步复用）

```bash
# 1. 装 Hermes + 配好企微 gateway（wecom 能连、有内部群会话）
# 2. 拷脚本和存量素材库
mkdir -p ~/.hermes/scripts ~/.hermes/city-breakout
cp <源机>/.hermes/scripts/sz_policy_monitor.py ~/.hermes/scripts/
cp <源机>/.hermes/city-breakout/sz_policy_lib.json ~/.hermes/city-breakout/   # 可选，保留去重基线
# 3. 建 cron（周二五9点推企微群）
hermes cron create "0 9 * * 2,5" "" --name "苏州城市破播政策监控" \
  --script "sz_policy_monitor.py" --no-agent --deliver "wecom:<群chat_id>"
# 4. 确认 gateway 活着
hermes gateway status   # ✗ Gateway is not running — cron jobs will NOT fire 则必须先启
```

### 拿到企微内部群 chat_id 的方法（新机器必做）

群会话标识在 `~/.hermes/state.db`：
```python
import sqlite3
c=sqlite3.connect('/home/administrator/.hermes/state.db')
for r in c.execute("SELECT session_key FROM gateway_routing WHERE session_key LIKE '%wecom:group%'"):
    print(r[0])  # agent:main:wecom:group:<chat_id>:<user_id>
```
deliver 用群 chat_id（第三个冒号段）：`wecom:<chat_id>`。验证推送：改 deliver 后 `hermes cron run <id>` 手动触发，看群里是否收到。

## 两处已修复的核心 bug（换机升级后可能复发，检查这两点）

> task 触发路径与 gateway 启动路径各有一个代码失配会静默失败——升级前先 `grep` 断这两处，否则推送"看起来部署了但永远不推"。

### Bug A — `claim_job_for_fire` 缺 `return_job` 参数
- **症状**：`hermes cron run <id>` 报 `claim_job_for_fire() got an unexpected keyword argument 'return_job'`，手动触发 failed
- **根因**：`cron/jobs.py` 的 `claim_job_for_fire` 签名旧（只收 bool 语义），但 `tools/cronjob_tools.py`（834、1176 行）按新语义调 `return_job=True` 并期望返回 job dict
- **修复**：给 `cron/jobs.py` 的 `claim_job_for_fire` 加 `return_job: bool = False` 参数——默认保持 bool，`True` 时成功返回 job 记录 dict。所有现有调用/测试不受影响
- **检查**：`grep -n "return_job" /home/administrator/hermes-agent/cron/jobs.py` 应有参数声明

### Bug B — `scheduler_for_profile_mode` 缺失致 gateway 崩溃重启
- **症状**：`journalctl --user -u hermes-gateway` 显示 `ImportError: cannot import name 'scheduler_for_profile_mode' from 'cron.scheduler_provider'`，systemd restart counter 数千次，**cron 调度器根本不在跑、企微推送无法发生**（gateway 一启动即崩）
- **根因**：`gateway/run.py:31602` 从 `cron.scheduler_provider` 导入 `scheduler_for_profile_mode`，但该函数从未存在（版本失配：run.py 较新，scheduler_provider.py 较旧）
- **修复**：在 `cron/scheduler_provider.py` 补一个纯 identity 包装函数（返回传入的 scheduler；multiplex 实际由 `InProcessCronScheduler.start()` 的 `profile_homes` 参数处理，见 #69377）
- **检查**：`grep -n "scheduler_for_profile_mode" /home/administrator/hermes-agent/cron/scheduler_provider.py` 应有函数定义 + 调用处

## 排查清单（推送链路不通时）

```bash
# 1. gateway 必须活着（否则 cron 不调度、wecom 不推送）
hermes gateway status        # ✗ Gateway is not running → 先启/重启
systemctl --user status hermes-gateway  # 看是否崩溃重启(restart counter 狂涨)
journalctl --user -u hermes-gateway -n 30 | grep -iE "import|error|exited"  # 找 Bug B
# 2. 手动触发验证脚本本身
python3 ~/.hermes/scripts/sz_policy_monitor.py   # 应正常或静默，不报错
# 3. 手动触发 cron 看投递
hermes cron run <id>; sleep 20; hermes cron runs <id>  # completed 且群收到才叫通
# 4. 查投递错误
grep -iE "wecom.*(error|fail)|93001" ~/.hermes/logs/errors.log
```

## 已知坑

- cron `--script` 的脚本**必须在 `~/.hermes/scripts/`**，路径不符建任务失败
- `--no-agent` 模式：脚本 stdout 原样投递，**空 stdout = 静默不推**（watchdog 语义）
- 企微内部群可推、外部客户群官方不支持机器人推送
- 93001 错误 = 某个群/机器人不允许发消息；不代表所有企微都挂（`wecom:XuAiJun` 单聊通常通）
- anysearch 对"营商/补贴"等词会召回到赌场/旅游广告垃圾 → 域名白名单 + 标题黑名单双层拦
- gateway 反复重连 wecom = 多个进程/LSP 抢连接，或 gateway 崩了在重启 → 看 journalctl 找根因

## 验证

- [ ] `hermes gateway status` 显示 gateway running，无崩溃重启
- [ ] `python3 ~/.hermes/scripts/sz_policy_monitor.py` 不报错（有新增则输出，无则静默）
- [ ] `hermes cron list` 里任务 Next run 正常（周二五）
- [ ] 群里实际收到过推送（端到端才算通）
- [ ] 旧文（>45天）不会当"新发现"推（新鲜度过滤生效）