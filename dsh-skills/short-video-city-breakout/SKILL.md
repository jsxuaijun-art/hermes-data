---
name: short-video-city-breakout
title: Short Video City Breakout (城市破播·苏州)
description: 城市破播·苏州引流短视频 — 讲苏州政策/营商/注册效率，反哺注册记账业务。
version: 1.0.0
tags: [短视频, 城市破播, 苏州, 政策引流, 财税获客, 抖音, 视频号, 营商环境, 政策监控]
---

# Short Video City Breakout (城市破播·苏州)

## 定位

同层级于 `short-video-copywriting` 下四类（纯广告/趣味破播/范话题/行业自然流）的**第五大视频类型**（2026.9 徐总提出）。核心逻辑：把「苏州」当主角，用真实政策/效率/作风做钩子，让在苏或计划来苏的中外创业者先信服苏州、再记住徐总的业务（公司注册/代理记账/财务外包/合规账）。表面讲苏州政策，实则以城市便利性为信任背书、自然导流自身财税业务。

## When to Use

- 用户提到「城市破播」「苏州政策」「苏州营商环境」「政策引流」选题
- 需要以苏州为主题、或以省级/国家级落实到苏州的政策为主题的短视频文案
- 政策监控脚本刷新素材库后，据此批量出选题

## Prerequisites

- `anysearch` CLI（`~/.hermes/skills/anysearch/scripts/anysearch_cli.py`）——苏州政策监控的唯一可靠搜索后端
- WSL Python venv：`/home/administrator/hermes-agent/venv/bin/python3`
- ⚠️ 苏州政务网 suzhou.gov.cn 栏目列表页是 JS 动态渲染，**不可硬爬**；正文本页可抓、搜索引擎索引可用（详见 Pitfalls）

## How to Run — 政策监控（"政策一出第一时间知道"）

徐总 2026.9 明确不满意被动搜索，要求类似「低空经济实施方案」的新政策**第一时间自动抓取**，不等被问。已验证链路：

1. 运行：`python3 <skill_dir>/scripts/sz_policy_monitor.py`
2. 脚本行为：8 路关键词 `anysearch batch_search` → **域名白名单 + 垃圾词/外省名黑名单过滤**（anysearch 对「营商环境」等泛词会语义召回赌场/旅游/ERP 垃圾，必须过滤）→ 解析标题/URL/日期 → 按文号（〔20XX〕N）或 URL 去重 → 入库 JSON → **只输出本轮新增（空输出 = 静默）**
3. 素材库：`<HERMES_HOME>/city-breakout/sz_policy_lib.json`（HERMES_HOME 默认 `~/.hermes`）
4. 实测：9.5 秒抓 29 个唯一政策源（含文号/日期/官方 URL），去重稳定
5. ✅ **已部署（2026.9.20 徐总拍板，决策1：周二+周五）**：cron `苏州城市破播政策监控`（id `72d7d5389d6d`），`0 9 * * 2,5`，`--script sz_policy_monitor.py --no-agent --deliver wecom:wrBqtFBgAAFbj6ydc54nuVdDcLmMxgIg`（徐江机器人·内部群，2026.9.20 徐总拍板：从单聊 XuAiJun 改为群推送）；脚本空 stdout = 静默不推送，有新政策才送达。⚠️ 群送达**尚未端到端确认**——手动 `hermes cron run` 已验证可用（2026.9.21 修好 `claim_job_for_fire` 参数失配），但最终闭环要等周二/五真实 tick + 群里收到。查执行：`hermes cron runs <job_id>`；运维细节见 `references/cron-policy-monitor-ops.md`（含 gateway 在线硬前提、崩溃循环诊断、验证顺序）

## Quick Reference — 子模块 A-F（徐总 2026.9 定稿）

| 模块 | 内容 | 引流 |
|---|---|---|
| A 政策热榜 | 产业政策（低空经济实施方案等）+ 省/国家级落实到苏州的政策 | 政策看不懂→会计帮你捋 |
| B 开办效率榜 | AI智能查名/名称核准成功率80%+、企业开办一件事、一日办结 | 公司注册生意 |
| C 营商环境作风 | 9.0版90项举措、一窗受理、整治吃拿卡要 | 敢承诺正规合规 |
| D 外资通道 | 外商投资利润再投资、外资一站式、外籍在苏设公司 | 中外创业者入口（徐总点名保留）|
| E 人才落户 | 领军人才100-500万资助+购房补贴、落户 | 想来苏落地的人才 |
| F 补贴专题 | 社保补贴、汽车购新补贴等"钱袋子"类 | 领补贴要合规账→财务外包 |
| G 在苏州做生意 | 本地生活/开店/经营场景（徐总 2026.9.20 追加） | 苏州本地创业者 |

素材口径：**苏州市级 + 江苏省一级 + 国家一级**，凡落实到苏州市一级执行、与苏州创业者相关的政策都是合格素材；有新政策出台（类似「低空经济实施方案」）由监控 cron 自动抓取，不等被问。

## Procedure — 文案骨架（40秒，沿用黄金三秒铁律）

```
0-5s   砸真实苏州政策/数字（热点/政策第一句，禁止"我做了二十年"慢热开头）
5-18s  拆政策：对"想在苏州开公司的人"意味着什么、落地路径
18-28s 映射观众：你是不是该注册苏州/外来创业者/公司要不要迁苏
28-30s 自然CTA：你来苏我带你办 / 评论区问政策 / 私信帮你算
```

注：**文案逻辑对照同级模块照抄其套路**（徐总 2026.9.20 明确：钩子怎么用、什么更吸引收藏/转发，参考短四类同级模块，不另造体系）；示例选题默认挑**最新发布**的政策（如 2026-09 社保补贴延长 25%、2027-03 申领截止这类"截止日期+门槛"最抓收藏转发），**低空经济类已过时，不作选题基础**。

## Quick Reference — 红线

- 每条必须含**至少一个可查证**的苏州/江苏/国家政策真事实：文号〔20XX〕N / 数据 / 举措，禁止编造（公众号铁律同源）
- 政策解读需用 anysearch 核实最新口径，不沿用旧记忆/旧参考（热点会更新，见 short-video-copywriting 韩红退股案教训）
- 落到自己业务时不夸大效果、不越"误导"红线：承认流程有节点，强调"按规矩走+交给专业的人=高效透明"
- 交付沿用 short-video-copywriting 规范：速览表（方向∣标题∣时长∣核心钩子）→ 标题三件套 → 话题标签 → 完整文案 → 拍摄速查表 → `.docx` + `.txt` 放桌面 `/mnt/c/Users/Admin/Desktop/`

## Pitfalls

- **苏州政务网列表页不可硬爬**：`szyw_list.shtml`/`zfwj_list.shtml`/`zfgb_list.shtml` 等 requests 直抓返回统一首页壳（~150KB，无列表内容）或 403；政策发现只能走 anysearch/搜索引擎索引
- anysearch 是本监控的可靠后端；Bing.cn/Sogou 有 JS 渲染与反爬局限（详见 `python-web-scraping-setup`）
- 监控脚本**首次运行全量入库**（全部标 NEW 属正常）；后续运行只报真正新增
- 本 skill 与 `short-video-copywriting`（四类母 skill）共享黄金三秒/六项指标/交付规范，写城市破播时如需四类语法细节可交叉加载

## Verification

- [ ] `scripts/sz_policy_monitor.py` 无报错，素材库 JSON 增长、NEW 列表合理
- [ ] 文案动笔前，素材库或 anysearch 中有对应政策的文号/URL 可查证
- [ ] 交付 .docx 到桌面，含标题三件套 + 话题标签 + 速览表

真实素材底稿索引见 `references/2026-09-suzhou-policy-material-bank.md`。监控 cron 的运维/验证顺序/已知坑见 `references/cron-policy-monitor-ops.md`。