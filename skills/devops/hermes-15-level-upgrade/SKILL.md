---
name: hermes-15-level-upgrade
description: Hermes 智能体15级进化框架自检与升级路线。用户对照"深度拆解Hermes 15阶段进化"视频框架做自检/升级时使用——逐级核对真实配置诊断现状、生成四周升级日程表(Word放桌面)、按周落地MCP/邮箱/多智能体/知识库/看板/语音/成本门控。触发词：15级、进化框架、自检、升级日程、用了百分之几的能力。
version: 1.0.0
category: devops
metadata:
  hermes:
    tags: [hermes, 15级进化, 自检, 升级路线, MCP, 多智能体, 日程表]
---

# Hermes 15级进化框架 · 自检与升级路线

## 触发条件
- 用户提到"15级""进化框架""自检""升级日程""Hermes只用了不到百分之十"等
- 用户要求对照 Hermes 15阶段进化视频做自我评估
- 用户按周执行升级任务（第1周MCP/邮箱 → 第4周成本门控）

## 一、15级框架速查表（诊断口径）
| 级 | 阶段 | 核心能力 | 在真实环境哪里查 |
|----|------|----------|------------------|
| L1 | 基础 | 聊天→行动(调工具/写代码/跨系统) | 历史会话是否在用工具产出（公众号/短视频/方案） |
| L2 | 基础 | 记忆+SOUL身份文件 | ~/.hermes/SOUL.md 是否写满商业模式/客户画像 |
| L3 | 基础 | 斜杠命令/后台运行 | skills 数量与自动化流水线 |
| L4 | 杠杆 | 多模型分层/成本控制 | config.yaml model 段是否有多个 provider 分层 |
| L5 | 杠杆 | MCP外部工具接入 | config.yaml `mcp_servers` 段（**非空**才算达标） |
| L6 | 杠杆 | 子智能体并行调研 | delegation 配置 + 是否实际用过 delegate_task 多路 |
| L7 | 杠杆 | 异步定时任务 | ~/.hermes/cron/jobs.json 有任务在跑 |
| L8 | 自主 | 多文件架构/职责隔离 | 是否建了多个独立角色/智能体分工 |
| L9 | 自主 | LLM wiki知识库自我进化 | 是否建研究笔记库（仅 memory 不算） |
| L10 | 自主 | 看板编排流水线 | kanban 是否实际用于任务依赖编排 |
| L11 | 自主 | 语音模式 | stt 配置 + faster-whisper 是否启用 |
| L12 | 自主 | 打包分发/一键复刻 | 是否有可复刻包（profile export 等） |
| L13 | 自主 | 零成本监控/本地确定性任务 | 是否写本地脚本盯网页变化 |
| L14 | 自主 | 代币经济学/唤醒门控 | 是否做成本门控（无更新不调模型） |
| L15 | 自主 | 全天候自动化商业引擎 | 定时任务+监控+门控是否成完整系统 |

## 二、环境核查命令清单（先查再判，禁止凭空猜）
```bash
# cron 任务（L7）
python3 -c "import json;d=json.load(open('/home/dmin/.hermes/cron/jobs.json'));jobs=d.get('jobs',d) if isinstance(d,dict) else d;print([(j.get('id'),j.get('name')) for j in jobs] if isinstance(jobs,list) else jobs)"
# delegation / kanban 配置（L6/L10）
grep -A8 'delegation' ~/.hermes/config.yaml; grep -i -A5 'kanban' ~/.hermes/config.yaml
# gateway 状态（企微/API是否在线）
cat ~/.hermes/gateway_state.json
# 语音本地组件（L11）
pip show faster-whisper 2>/dev/null | grep -i version
# MCP servers（L5 硬指标——空=未达标）
grep -i -B2 -A10 'mcp_servers' ~/.hermes/config.yaml
# 邮箱接入痕迹（L5邮箱部分）
grep -iE 'EMAIL|GMAIL|IMAP|SMTP' ~/.hermes/.env 2>/dev/null; ls ~/.config/himalaya/ 2>/dev/null
# node/npx（MCP stdio 前提）
which node npx
```

## 三、用户基线（2026-08-02 实测诊断）
- 当前稳定等级：**L7（异步定时任务）**。基础1-3全绿，杠杆4-7完成一半，自主8-15基本空白。
- ✅ 达标：L1 L2 L3 L7（云端企微gateway在线、3个cron在跑、89个skill）
- ⚠️ 半达标：L4(单模型无分层) L9(有memory无笔记库) L10(kanban配好未用) L11(whisper装好未启用) L15(部分cron)
- ✅ 2026-08-02 升级后：**L6 已跑通**（3路并行调研：竞品定价/金税四期/抖音获客，4分32秒出三份报告）→ 执行手册见 references/l6-parallel-research.md
- ❌ 未达标：L5(mcp_servers空) L8 L12 L13 L14
- 详细审计记录 → references/baseline-audit-2026-08-02.md

## 四、四周升级路线（用户已确认执行）
| 周 | 主题 | 内容 |
|----|------|------|
| 第1周 | 打通工作台 | L5 MCP+邮箱接入、L4 模型分层（进行中 → references/week1-email-mcp.md） |
| 第2周 | 多智能体 | L8 职责分工、L6 并行调研（✅ L6 已跑通 → references/l6-parallel-research.md） |
| 第3周 | 护城河 | L9 知识库、L10 看板编排 |
| 第4周 | 成本引擎 | L11 语音、L13 零成本监控、L12 打包、L14 门控 |

## 五、交付规范（用户硬性偏好）
1. 交付物默认 **Word .docx 放桌面**：`/mnt/c/Users/Admin/Desktop/`（WSL路径），不额外出Markdown。
2. 表格类内容必须用 box_maker.py 网格（`/mnt/c/Users/Admin/hermes-sync/skills/creative/workbuddy-output/scripts/box_maker.py`），生成后 verify_box() 验证对齐，禁止Markdown表格、禁止手写。
3. 日程表结构：封面 → 诊断结论 → 逐级总览表 → 未达标清单 → 每周分日行动表(周一~周末) → 使用指南。
4. 沟通风格：分层决策——提方案让江姐拍板；逐步引导操作，复杂配置我方写，用户只粘贴/验证。

## 六、Pitfalls
0. **L4 模型分层先探中转站真实清单，别假设**：OpenAI 兼容中转站（如 llm.chudian.site）通常不开放 `GET /models`（返回空/需鉴权），但会以**单模型白名单**运行。实测方法——逐一 curl 候选模型名（deepseek-v4-flash / deepseek-v4 / deepseek-reasoner / gpt-4o / qwen-max 等），返回 `200` 即可用、`404 model_not_found` 即不存在。江姐的中转站实测**只开放 `deepseek-v4-flash` 一个模型**，其余全 404 → 经典"贵模型+便宜模型"分层无解。此时 L4 正确姿势：①**等有第二个模型再分层**，先备好"便宜/贵"两档配置骨架注释掉，开通后填名即启用；②用 **cron `--script --no-agent` 零成本门控**（Pitfall 0b）替代多模型成本优化——这是单模型中控成本的正道。
0b. **cron 零成本门控 = L4/L13/L14 核心落地装置**：`hermes cron create "<schedule>" --name X --script foo.py --no-agent --deliver local`。`--no-agent` 让 cron **完全跳过 LLM**，只跑脚本、stdout 直接当结果；stdout 为空=静默不打扰（经典 watchdog）。适合一切"本地确定性读/监控"任务（读邮箱、盯网页、查磁盘、ping 接口）——**零 token、纯脚本**，一次实现 L4(成本)+L13(确定性/零成本监控)+L14(无更新不调模型)。监控类任务务必用这个，勿用带 agent 的 cron（每次跑都烧 token）。**注意**：`--no-agent` 任务在本 CLI 无实时投递，`--deliver local` 只存档，跨会话看不到实时通知——要通知须 `--deliver telegram/discord` 等网关平台。
1. **Python 字符串内中文引号**：execute_code 写 docx 生成代码时，字符串内出现弯引号（中文双引号）会提前终止字符串 → SyntaxError。实测报错 `invalid character '、'` 是引号提前截断的连锁反应。解法：外层用单引号包裹、或内部引号转义、或先写脚本文件再执行。
2. **企微 ≠ MCP**：企业微信走 Hermes gateway 平台通道（wecom/wecom_callback），不是 MCP。云端已在跑 wecom_callback+wecom（gateway_state.json 可见）；本地WSL 必须 `wecom.enabled: false` 防 WebSocket 独占连接冲突（详见 wecom-external-service skill 10.0.4）。评估 L5 时企微不计数，邮箱/Notion/外部API才是MCP缺口。
3. **aux title_generation 401**：中转代理（llm.chudian.site）环境下 auxiliary 任务必须 `provider: custom` + 同代理 base_url，否则直连原生API报401（详见 wecom skill 10.0.1）。
4. **诊断先查后判**：评估任何一级前先跑第二节核查命令，不要凭印象。上次实测 L5 实际是"mcp_servers 空"，与用户以为的"企微通了=外部接入通了"不同，先查环境再下结论。

## 相关技能
- wecom-external-service：企微通道行为规范与部署拓扑
- mcp（references/native-mcp.md）：MCP server 配置格式
- word-documents：docx 生成规范
- hermes-agent（官方受保护，勿改）：CLI/配置参考
