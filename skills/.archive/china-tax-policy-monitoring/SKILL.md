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
- 政策列表在 `<div class=\"common_list\">` 下的 `<a>` 标签
- 链接是相对路径，需要补全 `https://www.chinatax.gov.cn` 前缀
- 页面内容可能缓存较旧（演示用没问题，生产监控可能需要找其他入口）

### 示例脚本结构

```python
from scrapling.fetchers import Fetcher

BASE_URL = \"https://www.chinatax.gov.cn\"
p = Fetcher.get(BASE_URL + \"/chinatax/n810341/n810755/index.html\")
list_area = p.css(\"div.common_list\")[0]

for a in list_area.css(\"a\"):
    title = a.text.strip()
    href = a.attrib.get(\"href\", \"\")
    if title and len(title) > 4:
        print(f\"{title} → {BASE_URL}{href}\")
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
- **跨平台测试**：安装后执行 `python3 scripts/XXX_cli.py search \"test\" --max_results 1` 验证

## Hermes cron 集成 — 财税战略情报中心

### 整体架构

采用**统一调度架构**，一个 cron job 覆盖所有推送日：

```
Cron Job（周一三五09:05） — Unified Job (ID: 766017656bde)
├── 加载器: unified_tax_loader.py (按 weekday() 分支)
│   ├── 每日模板 → Agent 搜索信息源 → 生成报告
│   └── (周一) 周度模板 → Agent 生成周度分析
└── 输出: Agent 直调企微 webhook 推送群聊（不保存本地文件）
```

### 提示词模板 + 脚本加载模式（当前生产环境）

#### 单一 Job 按星期分支（推荐模式）

**当前生产架构** — 一个 cron job 覆盖所有推送日（周一、三、五），通过 Python 脚本按 weekday() 分支：

```python
#!/usr/bin/env python3
\"\"\"统一加载脚本 — 按星期几输出不同模板\"\"\"
import os, datetime

today = datetime.date.today()
dow = today.weekday()  # 0=周一, 2=周三, 4=周五
weekday_cn = [\"星期一\",\"星期二\",\"星期三\",\"星期四\",\"星期五\",\"星期六\",\"星期日\"]
dow_cn = weekday_cn[dow]

# 1. 每日监控部分（每天都有）
daily_template = load_daily_template()
daily_template = daily_template.replace(\"{{DATE}}\", today.strftime(\"%Y-%m-%d\")
output = [daily_template]

# 2. 周一额外输出周度分析
if dow == 0:
    weekly_template = load_weekly_template()
    output.append(weekly_template)

print(\"\\n\".join(output))
```

**优点**：一个 cron job，无需维护两套调度；脚本自动处理工作日判断。

#### 模板文件

- `~/.hermes/cron/daily_tax_intelligence.md` — 每日任务提示词
- `~/.hermes/cron/weekly_tax_deep_dive.md` — 每周任务提示词

#### 信息源优先级

模板中列出15个来源，agent 执行时优先覆盖。包括：

- 国家税务总局 `www.chinatax.gov.cn`
- 财政部 `www.mof.gov.cn`
- 证监会、工信部、发改委、市监局
- 中国税务报 `www.ctaxnews.com.cn`
- 上海/江苏/浙江/广东/北京地方税务局
- 四大会计师事务所研究报告
- 中国政府网 `www.gov.cn`

### Cron Job 配置详情

**当前生产环境配置：**

| 项目 | 值 |
|------|------|
| 调度 | 周一、三、五 09:05 CST |
| Job ID | `766017656bde` |
| 加载脚本 | `unified_tax_loader.py`（位于 `~/.hermes/scripts/`）|
| 模板文件 | `~/.hermes/cron/daily_tax_intelligence.md` / `weekly_tax_deep_dive.md` |
| 推送方式 | Agent 直调企微 webhook |
| 文件存储 | ✅ 不保存到本地 |
| Workdir | `/root` |

### 企微 webhook 推送配置

```yaml
webhook_url: "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=41872151-7e41-410f-b006-a0db3f6f4e30"
msgtype: markdown
max_content_bytes: 4096  # 超出截断
```

Agent 在 cron 任务中通过 `curl` 或 `requests` 发送 POST 请求：
```json
{
  "msgtype": "markdown",
  "markdown": {"content": "报告内容（markdown格式）"}
}
```

可用 markdown 语法：标题、加粗、链接、列表、分割线、引用。**禁止在内容中包含电话号码、二维码等营销信息**。

### 脚本路径问题修复记录（2026-06-14）

**问题：** cron 任务的 `Script` 字段值为 `unified_tax_loader.py`，系统从 `~/.hermes/scripts/` 下解析。但脚本实际存放在 `~/.hermes/cron/` 下，导致每次执行报 `Script not found: /root/.hermes/scripts/cron/unified_tax_loader.py`。

**修复措施：**
1. 将脚本从 `~/.hermes/cron/unified_tax_loader.py` 复制到 `~/.hermes/scripts/unified_tax_loader.py`
2. 通过 `hermes cron edit` 设置 `--script unified_tax_loader.py`（不带路径前缀）和 `--workdir /root`
3. 脚本内容改为**只输出模板**（不含文件保存逻辑），Agent 读模板后生成报告并直接推送企微

**经验教训：** cron 任务的 Script 路径相对于 `~/.hermes/scripts/`，不是 `~/.hermes/cron/`。脚本名称不带目录前缀。创建 cron job 时脚本必须存在在 `~/.hermes/scripts/` 下，否则即便复制过去也需要 `hermes cron edit --script` 重新指定。

### 推送规则

| 星期 | 推送 | 说明 |
|------|------|------|
| 周一 | ✅ 推送到企微群 | 含日报告 + 周度深度分析 |
| 周三 | ✅ 推送到企微群 | 只推送每日报告 |
| 周五 | ✅ 推送到企微群 | 只推送每日报告 |
| 其他日 | ❌ 不推送 | cron 未调度 |

### Agent 提示词中嵌入推送规则

cron job 的 `--prompt` 中必须包含以下推送指令（否则 Agent 不会执行推送）：

```
【⚠️ 关键推送规则——必须执行】
报告生成后，不要保存到本地文件。直接调用企微webhook推送到企业微信群：

企微webhook地址：
https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=41872151-7e41-410f-b006-a0db3f6f4e30

格式要求：
- msgtype = markdown
- content 中可用的 markdown 语法：标题、加粗、链接、列表、分割线、引用
- content 总长度不能超过4096字节，超出需截断
- 调用后用 curl 或 python 发送POST请求

推送成功后，输出 推送成功 并结束。推送失败则输出错误信息。

重要规则：所有信息标注来源URL。内容中不要包含电话号码、二维码等营销信息。
```

## 扩展建议

| 优先级 | 任务 | 频率 | 说明 |
|--------|------|------|------|
| ⭐ | 任务4：月度战略报告 | 每月1日 | 再加一个 cron job |
| ⭐ | 任务2：机会雷达 | 每日 | 合并到每日任务 |
| ⭐ | 任务6：知识库建设 | 每月 | 汇总当月报告 |

## 已知问题

- 税务总局 `最新文件` 页面可能存在缓存延迟，数据不是实时最新
- 部分政府网站有反爬机制，可能需要 `StealthyFetcher` 或调整请求头
- HTTPS 证书问题：税务总局支持 HTTPS，但部分子站可能只支持 HTTP
- Agent 推送企微 webhook 可能因报告过长（超过 4096 字节）触发截断，导致格式异常

## 参考

- [每日报告模板](references/daily-tax-intelligence-template.md) — 财税情报中心每日报告输出格式
- [周度报告模板](references/weekly-tax-deep-dive-template.md) — 财税情报中心周度分析报告输出格式
- [Scrapling 环境搭建](references/environment-setup.md) — Scrapling 环境搭建详细记录
- [wecom-bot 部署笔记](references/wecom-bot-architecture.md) — 阿里云 wecom-bot 服务架构、端点列表、API Key 管理、机器人类型辨析
- [推送脚本](scripts/push_report.py) — 报告内容推送脚本
- [爬虫脚本](scripts/tax-policy-monitor.py) — 税务总局最新政策文件采集脚本
