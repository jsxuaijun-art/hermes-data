# Hermes 15级自检 · 基线审计记录（2026-08-02 实测）

> 本文件是 `hermes-15-level-upgrade` 的会话基线快照。每次升级周结束后在此追加"已提升"标记，
> 基线随升级推进而更新。诊断必须用真实命令核查，禁止凭印象。

## 实测环境盘点（命令输出摘要）

### Cron 任务（L7 ✅）
- 9698e166ad5e | 销售谈判·双周全网搜索 | cron: 0 9 * * 1（每周一9点）
- 7ee18132d423 | 销售谈判·月度趋势简报 | cron: 0 9 1 * *（每月1号9点）
- 2017502ff5d6 | computer-use-reminder | once in 365d（一次性提醒）

### Delegation（L6 ⚠️ 已配未用）
```yaml
delegation:
  max_iterations: 50
  child_timeout_seconds: 600
  inherit_mcp_toolsets: true
```
- 能力已配置，但从未实际发起过多路并行调研 → 半达标

### Kanban（L10 ⚠️ 已配未用）
```yaml
kanban:
  dispatch_in_gateway: true
  dispatch_interval_seconds: 60
  failure_limit: 2
```
- kanban_decomposer 模型 = deepseek-v4-flash（走 llm.chudian.site 代理）
- 未用于真实业务流水线 → 半达标

### Gateway 状态（企微通道 ✅）
gateway_state.json 显示：
- wecom_callback: connected（企微回调）
- wecom: connected（企微 AI 机器人 WebSocket）
- api_server: connected（127.0.0.1:8642）
- 云端在跑，本地 WSL `wecom.enabled: false`（防独占连接冲突，见 wecom skill 10.0.4）

### 语音（L11 ⚠️ 已装未启用）
- faster-whisper 1.2.1 已安装
- 未配置 stt.enabled / 未启用语音模式 → 半达标

### MCP（L5 ❌ 硬缺口）
- config.yaml 中 `mcp_servers` 段为空（grep 无任何 server）
- node v24.16.0 + npx 可用（stdio MCP 前提就绪）
- 邮箱：env 无 EMAIL/GMAIL/IMAP/SMTP 任何 key，himalaya 未装

### 模型分层（L4 ⚠️）
- 主模型 deepseek-v4-flash，走中转 llm.chudian.site/v1
- auxiliary title_generation 已修复为 provider: custom + 同代理（不再401）
- 无便宜/贵模型分层路由 → 半达标

## 15级判定总表

| 级 | 判定 | 依据 |
|----|------|------|
| L1 | ✅ | 公众号/短视频/代账方案均在用工具产出 |
| L2 | ✅ | SOUL.md 已写满商业模式/高会素材/同步策略 |
| L3 | ✅ | 89个skill + 自动化流水线 |
| L4 | ⚠️ | 仅单模型 deepseek，未分层 |
| L5 | ❌ | mcp_servers 空 |
| L6 | ⚠️ | delegation 配好未用 |
| L7 | ✅ | 3个cron在跑 |
| L8 | ❌ | 无多智能体职责隔离 |
| L9 | ⚠️ | 有 memory 无研究笔记库 |
| L10 | ⚠️ | kanban 配好未用 |
| L11 | ⚠️ | faster-whisper 装好未启用 |
| L12 | ❌ | 无打包复刻包 |
| L13 | ❌ | 无本地零成本监控脚本 |
| L14 | ❌ | 无成本门控 |
| L15 | ⚠️ | 部分cron，未成完整系统 |

## 结论（交付给用户的措辞）
"你现在稳定处于【第7级】（异步定时任务）。基础1-3级全绿，杠杆4-7级完成一半，
尚未进入自主8-15级。你是会用工具的人，但还没到让系统替你干活的境界。"

## 交付物
- 桌面 Word：`/mnt/c/Users/Admin/Desktop/Hermes_15级升级日程表_20260802.docx`
- 结构：封面 → 诊断结论 → 逐级总览表 → 未达标清单 → 四周分日行动表 → 使用指南
