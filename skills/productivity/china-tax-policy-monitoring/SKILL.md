---
name: china-tax-policy-monitoring
category: productivity
description: 采集中国税务/财政政府网站政策数据（税务总局、财政部等）。涵盖 Scrapling 环境搭建、爬虫脚本编写、多机共享、Hermes cron 定时监控。面向财税行业用户。
---

# 中国税务政策监控

采集国家税务总局、财政部等政府网站的最新政策文件，实现自动监控和推送。

## 适用场景

- 每日自动抓取税务总局最新文件列表
- 监控特定类型政策更新（增值税、所得税、出口退税等）
- 多机器共享爬虫脚本（通过 hermes-data GitHub 同步）

## 环境搭建

### 安装 Scrapling（独立 venv，不污染 Hermes 环境）

```bash
# 创建独立虚拟环境
python3 -m venv ~/scrapling-env

# 安装全部依赖（不要只装 scrapling 本体，要用 [all]）
source ~/scrapling-env/bin/activate
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple scrapling[all]

# 安装 Chrome 浏览器引擎
playwright install chromium
```

> ⚠️ **坑：** 只装 `scrapling`（不带 `[all]`）会导致运行时不断报 `ModuleNotFoundError`。依赖链包括 `curl_cffi`、`browserforge`、`patchright` 等。`scrapling[all]` 一次性解决。

### 验证环境

```python
from scrapling.fetchers import Fetcher, StealthyFetcher
print(Fetcher.get('https://www.chinatax.gov.cn').css('title')[0].text)
```

## 爬虫编写指南

### Scrapling API 要点

| 方法 | 用途 | 示例 |
|------|------|------|
| `Fetcher.get(url)` | 基础 HTTP GET | `p = Fetcher.get('http://...')` |
| `StealthyFetcher` | 隐身浏览器模式（绕过反爬） | 需 `patchright` |
| `element.css(selector)` | CSS 选择器查询 | `p.css('div.common_list a')` |
| `element.text` | 获取文本 | `a.text.strip()` |
| `element.attrib` | 获取属性字典 | `a.attrib.get('href', '')` |
| `element.tag` | 获取标签名 | `p.tag  # 'div'` |

### 税务总局页面结构

- 最新文件列表页：`http://www.chinatax.gov.cn/chinatax/n810341/n810755/index.html`
- 政策列表在 `<div class="common_list">` 下的 `<a>` 标签
- 链接是相对路径，需要补全 `https://www.chinatax.gov.cn` 前缀
- 页面内容可能缓存较旧（演示用没问题，生产监控可能需要找其他入口）

### 示例脚本结构

```python
from scrapling.fetchers import Fetcher

BASE_URL = "https://www.chinatax.gov.cn"
p = Fetcher.get(BASE_URL + "/chinatax/n810341/n810755/index.html")
list_area = p.css("div.common_list")[0]

for a in list_area.css("a"):
    title = a.text.strip()
    href = a.attrib.get("href", "")
    if title and len(title) > 4:
        print(f"{title} → {BASE_URL}{href}")
```

## 多机器共享

### 目录结构（放在 hermes-data 仓库中）

```
hermes-data/scrapling/
├── setup.sh              ← 新电脑一键安装脚本
├── activate.sh           ← 快速激活环境
├── README.md             ← 使用说明
└── scripts/              ← 爬虫脚本（所有机器共享）
    ├── test-scrapling.py          ← 环境验证
    └── tax-policy-monitor.py      ← 税务政策监控
```

### 分工

| 项目 | 同步方式 | 说明 |
|------|---------|------|
| 爬虫脚本 | ✅ GitHub (hermes-data) | 写一次，所有机器 git pull |
| Hermes cron 任务 | ✅ GitHub (hermes-data) | 在 config.yaml 中配置 |
| Python 包 | ❌ 每台机器单独 pip 装 | 二进制包，平台依赖 |
| Chromium 浏览器 | ❌ 每台机器单独 `playwright install` | ~170MB |

### .gitignore 注意

hermes-data 使用白名单机制（先 `*` 排除所有，再 `!` 放行），新增目录需要加：
```
!scrapling/
!scrapling/**
```

## 远程服务器部署（阿里云）

> **部署基础设施参考**：SSH 密钥设置、`.env` 写入（避开 shell 展开）、Gateway 管理等通用基础设施详见 [`cron-template-jobs`](devops/cron-template-jobs) 技能的 [阿里云部署指南](devops/cron-template-jobs/references/aliyun-cron-deployment.md) 和 [SSH 回退方法](devops/cron-template-jobs/references/aliyun-cron-deployment.md)。

通过本机 Hermes 将爬虫环境部署到阿里云服务器的概要流程：

1. **SSH 连接** — 推荐用 SSH key（见上方参考），首次可用 SSH_ASKPASS 或 paramiko
2. **同步仓库** — 确保 hermes-data 已 clone/pull 到服务器
3. **创建环境** — 远程执行 `python3 -m venv ~/scrapling-env`
4. **安装依赖** — 远程 pip install scrapling（阿里云用清华镜像加速）
5. **部署脚本** — scp 或 SFTP 写入远程目录
6. **验证运行** — 远程执行脚本，检查输出

### 阿里云特有坑

- `scrapling[all]` 下载极慢（400+包），优先装 `scrapling` + `curl_cffi` 精简版
- Playwright Chromium 下载 ~170MB 从国外 CDN，容易超时
- 基础 Fetcher 不需要 Playwright，服务器场景优先用 HTTP 模式
- 用 `stdout.channel.recv_exit_status()` 获取远程命令退出码

## 跨 Hermes 实例安装 Skill

当需要在多个 Hermes 实例（WSL、Windows Desktop、阿里云）上安装同一 Skill 时：

> **跨环境 Skill 安装指南**详见 [`cron-template-jobs`](devops/cron-template-jobs) 技能的 [阿里云部署指南](devops/cron-template-jobs/references/aliyun-cron-deployment.md)（含 zip 解压、Windows Desktop 路径、阿里云 SSH 安装）。

### 注意事项

- **`.env` 文件**：每个实例独立创建 `cp .env.example .env`（匿名可用），要提额需分别配置 API Key
- **`runtime.conf`**：Python 优先，如果在不同 OS 上运行，可保留自动检测
- **许可证**：部分 Skill 不包含许可声明，遵守上游仓库的许可条款
- **跨平台测试**：安装后执行 `python3 scripts/XXX_cli.py search "test" --max_results 1` 验证

## Hermes cron 集成 — 财税战略情报中心

### 整体架构

采用**统一调度架构**，一个 cron job 覆盖所有推送日：

```
Cron Job（周一三五09:05） — Unified Job (ID: 766017656bde)
├── 加载器: unified_tax_loader.py (按 weekday() 分支)
│   ├── 每日模板 → 搜索信息源 → 生成日报 → 保存到 daily/
│   ├── (周一) 周度模板 → 生成周报 → 保存到 weekly/
│   └── 推送指令 → agent 执行 push_report.py → 企微群
├── 日产出: 任务1(核心监控) + 任务7(内容营销素材)
└── 周一额外: 任务3(深度分析) + 任务8(趋势预测)
```

### 提示词模板 + 脚本加载模式

> **通用模式**：所有 template+loader cron job 的设计模式（条件分支、多模板、推送指令）详见 [`cron-template-jobs`](devops/cron-template-jobs) 技能。

#### 推荐模式：统一脚本（单Job，按星期分支）

**这是当前生产环境的架构** — 一个 cron job 覆盖所有推送日（周一、三、五），通过 Python 脚本按 weekday() 分支：

```python
#!/usr/bin/env python3
"""统一加载脚本 — 按星期几输出不同模板"""
import os, datetime

today = datetime.date.today()
dow = today.weekday()  # 0=周一, 2=周三, 4=周五
weekday_cn = ["星期一","星期二","星期三","星期四","星期五","星期六","星期日"]
dow_cn = weekday_cn[dow]

# 1. 每日监控部分（每天都有）
daily_template = load_daily_template()
daily_template = daily_template.replace("{{DATE}}", today.strftime("%Y-%m-%d")
output = [daily_template]

# 2. 周一额外输出周度分析
if dow == 0:
    weekly_template = load_weekly_template()
    output.append(weekly_template)

# 3. 附加推送指令
output.append(f"python3 /path/to/push_report.py ~/reports/{today.strftime('%Y-%m-%d')}.md markdown")

print("\n".join(output))
```

**优点**：
- 一个 cron job，无需维护两套调度
- 脚本自动处理工作日判断（脚本内部判断）
- 推送指令统一在脚本末尾输出

#### 备选模式：双任务分离（每日 + 每周）

每个 cron job 由两部分组成：
1. **提示词模板**（`.md` 文件）— 存于 `~/.hermes/cron/`，包含完整的分析框架和输出格式
2. **加载脚本**（`.py` 文件）— 读取模板、注入动态日期变量、输出给 agent 执行

#### 模板文件
- `~/.hermes/cron/daily_tax_intelligence.md` — 每日任务提示词（任务1+7）
- `~/.hermes/cron/weekly_tax_deep_dive.md` — 每周任务提示词（任务3+8）

#### 加载脚本

**`daily_tax_loader.py`** 核心逻辑：
```python
import os, datetime
prompt_path = os.path.expanduser("~/.hermes/cron/daily_tax_intelligence.md")
with open(prompt_path, "r") as f:
    template = f.read()

today = datetime.date.today()
weekday_cn = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]

template = template.replace("{{DATE_YYYY-MM-DD}}", today.strftime("%Y-%m-%d"))
template = template.replace("{{DOW_CN}}", weekday_cn[today.weekday()])

# 补充执行指令
template += f"""

## 执行说明
1. 先检查 ~/tax_intel/daily/ 目录下最后一份日报，避免重复
2. 搜索所有指定信息源（至少5个网站，每个至少2条信息）
3. 按模板格式生成完整的每日财税情报报告
4. 将报告保存到 ~/tax_intel/daily/{today.strftime('%Y-%m-%d')}.md
"""

print(template)
```

**`weekly_tax_loader.py`** 额外计算上周日期范围、周数、未来30/60/90天。

#### 信息源优先级
模板中列出15个来源，agent 执行时优先覆盖。包括：
- 国家税务总局 `www.chinatax.gov.cn`
- 财政部 `www.mof.gov.cn`
- 证监会、工信部、发改委、市监局
- 中国税务报 `www.ctaxnews.com.cn`
- 上海/江苏/浙江/广东/北京地方税务局
- 四大会计师事务所研究报告
- 中国政府网 `www.gov.cn`

### Cron Job 配置概要

> **Cron job 基础设施**：模板+加载器模式、`jobs.json` 写入、Gateway 管理、推送端点部署详见 [`cron-template-jobs`](devops/cron-template-jobs) 技能（同目录下的 [阿里云部署指南](devops/cron-template-jobs/references/aliyun-cron-deployment.md) 和 [2026-05-31 部署实录](devops/cron-template-jobs/references/2026-05-31-tax-intel-cron.md)）。

**当前生产环境配置**：
- 调度：周一三五 09:05 CST
- Job ID: `766017656bde`
- 加载脚本：`~/.hermes/cron/unified_tax_loader.py`（按 weekday() 分支）
- 模板文件：`~/.hermes/cron/daily_tax_intelligence.md` / `weekly_tax_deep_dive.md`
- 推送脚本：`/opt/wecom-bot/push_report.py`
- 推送端点：`https://callback.yingxinkuaiji.com/push`
- WeCom Webhook Key 已配置（推送已打通）

### 推送逻辑

| 星期 | 每日报告 | 每周报告 |
|------|---------|---------|
| 周一 | ⚠️ 需发送至企微群 | ⚠️ 需发送 |
| 周二 | 📁 已存档，无需推送 | — |
| 周三 | ⚠️ 需发送 | — |
| 周四 | 📁 已存档 | — |
| 周五 | ⚠️ 需发送 | — |
| 周六/日 | 📁 已存档 | — |

### 输出目录结构

```
~/tax_intel/
├── daily/          ← 每日报告
├── weekly/         ← 周度报告
└── monthly/        ← 预留（任务4：月度战略报告）
```

### 扩展建议

| 优先级 | 任务 | 频率 | 说明 |
|--------|------|------|------|
| ⭐ | 任务4：月度战略报告 | 每月1日 | 再加一个 cron job |
| ⭐ | 任务2：机会雷达 | 每日 | 合并到每日任务 |
| ⭐ | 任务6：知识库建设 | 每月 | 汇总当月报告 |

## 已知问题

- 税务总局 `最新文件` 页面可能存在缓存延迟，数据不是实时最新
- 部分政府网站有反爬机制，可能需要 `StealthyFetcher` 或调整请求头
- HTTPS 证书问题：税务总局支持 HTTPS，但部分子站可能只支持 HTTP

## 参考

- [每日报告模板](references/daily-tax-intelligence-template.md) — 财税情报中心每日报告输出格式和推送逻辑
- [周度报告模板](references/weekly-tax-deep-dive-template.md) — 财税情报中心周度分析报告输出格式
- [Scrapling 环境搭建](references/environment-setup.md) — Scrapling 环境搭建详细记录
- [wecom-bot 部署笔记](references/wecom-bot-architecture.md) — 阿里云 wecom-bot 服务架构、端点列表、API Key 管理、机器人类型辨析
- [推送脚本](scripts/push_report.py) — 报告内容推送脚本，从cron/agent调用POST到/push端点
- [爬虫脚本](scripts/tax-policy-monitor.py) — 税务总局最新政策文件采集脚本

> **通用基础设施参考**：SSH 密钥设置、zip 解压安装、`.env` 写入、Gateway 管理、cron job 创建等详见 [`cron-template-jobs`](devops/cron-template-jobs) 技能。
