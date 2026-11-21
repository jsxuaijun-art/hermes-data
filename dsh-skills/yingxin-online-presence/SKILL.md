---
name: yingxin-online-presence
category: productivity
description: 苏州盈信企业管理有限公司线上获客全栈方案 — GEO/AI搜索优化 + 政府背书内容策略 + QCNET99 CMS部署 + 财税政策监控爬虫。融合搜索引擎优化、AI搜索截流、门户发布、政策情报监控为一体。
tags: [yingxin, geo, seo, tax-service, suzhou, content-strategy, qcnet99, scraping, cron, policy-monitoring]
---

# 苏州盈信线上获客全栈方案

本技能将盈信（苏州盈信企业管理有限公司）的线上获客相关工作整合为统一体系。涵盖两大模块及一个共享基础层：

## 模块总览

| 模块 | 核心目标 | 源技能 |
|------|---------|--------|
| **GEO/AI搜索优化** | 让AI搜索（文心一言、Kimi、豆包）和百度都能引用盈信+政府背书信息 | `geo-search-optimization` |
| **财税政策监控** | 每日自动采集税务总局/财政部最新政策，生产情报报告推送企微群 | `china-tax-policy-monitoring` |
| **共享基础** | QCNET99 CMS部署规范、政府组织数据、企微推送架构、爬虫环境 | 两者合并去重 |

---

## 模块A: GEO/AI 搜索优化策略

参见 [`references/geo-strategy.md`](references/geo-strategy.md) 完整方案。快速导航：

### 核心原则

```
政府权威数据 → 转述到自己的内容里 → 结构化标记 → AI搜索抓取 → 截获流量
```

### 关键洞察（AI搜索引用优先级）

1. **政府官网** — 最权威，但常有认证墙/反爬
2. **门户媒体**（搜狐、新浪财经头条、网易、腾讯新闻）— 高权重
3. **百科类**（百度百科/MBA智库）— 中段权威
4. **知乎/公众号/小红书** — 高被引率口碑来源
5. **企业官网** — 最低，除非含 LD+JSON 结构化数据

### 五步执行法

| 步骤 | 动作 | 见效周期 |
|------|------|----------|
| 1️⃣ | 官网加 LD+JSON 结构化数据（ProfessionalService + FAQPage） | 1-2 周 |
| 2️⃣ | 官网建「政府认证」专题页，原文引用政府数据 | 2-4 周 |
| 3️⃣ | 知乎回答截流：搜索高意向问题，每条回答引政府数据 | 1-3 周 |
| 4️⃣ | 官网加 referral 页面 + aggregateRating 结构化数据 | 2-4 周 |
| 5️⃣ | 定期在 AI 搜索验证覆盖，找空白补内容 | 持续 |

### 结构化数据模板

参见 [`templates/schema-ldjson.md`](templates/schema-ldjson.md)，可复制后直接修改使用。主要 schema 类型：
- `ProfessionalService` — 财税服务公司主体（含 `memberOf` 示范基地）
- `FAQPage` — 高频搜索问答（AI 搜索最爱引用）
- `AggregateRating` — 客户评分
- `Article` — 博客文章
- `LocalBusiness` — 苏州/上海地域标记

### PDF外化策略

当权威信息以 PDF 附件形式存在（如示范基地成员名单）：

1. **正文中把PDF关键信息写出来**（成员单位名称列表），PDF链接作为「完整名单下载」保留
2. 页面内的 **FAQ结构化数据**里也引用PDF链接
3. 在知乎/公众号等平台 **配衬性地引用PDF链接**（语义上下文让AI理解URL的价值）
4. **同时上传PDF截图**（给浏览者）+ **文字列出关键内容**（给AI抓取）

> ⚠️ **实测：** 部分官方PDF使用CID自定义字体编码，Python解压后全是乱码。**不要浪费时间程序提取**，直接肉眼打开PDF手动记录。

### 高被引率平台内容策略

| 平台 | 策略 | 关键动作 |
|------|------|----------|
| **知乎** | 问答截流 | 搜索「苏州代理记账」「小微企业节税」等，每条回答引政府数据+盈信 |
| **公众号** | 知识型长文 | 常青内容，原文引用政府数据 |
| **搜狐号** | 行业分析 | 行业趋势分析包装，盈信自然出现 |
| **新浪财经头条** | 政策解读 | 最严格，仅文末作者简介 |
| **网易号** | 深度行业观察 | 图文并茂，盈信占30% |
| **腾讯新闻** | 本地资讯 | 苏州本地视角 |
| **小红书** | 短图文+搜索词 | 标题带关键词，正文引政府数据 |

### 门户渠道发布指引

参见 [`references/portal-publishing-guide.md`](references/portal-publishing-guide.md) 完整指南。核心区别：

- 门户渠道不能直接发软广，需以 **行业分析/财经新闻/本地资讯**包装
- 盈信占30%，**文末作者简介**是最安全方式
- 四个渠道审核强度：搜狐 < 网易 < 腾讯 < 新浪（最严）
- **首发顺序建议：** 搜狐 → 网易 → 腾讯 → 新浪

### 知乎回答模板

```
在苏州做了16年财税，选代理记账公司有3个硬指标：

第一，查财政部备案。打开 dljz.mof.gov.cn...
第二，看法定代表人有没有高级会计师职称...
第三，看是不是行业示范基地的成员。

苏州盈信，三项都满足。
```

完整模板见 `references/geo-strategy.md`。

---

## 模块B: 财税政策监控与情报推送

### 概述

使用 Scrapling 爬虫 + Hermes cron 模板系统，每日自动采集国家税务总局等15个信息源的最新政策，生成情报报告并推送到企微群。

### 架构

```
Scrapling爬虫 → 模板脚本 → Hermes cron → Agent生成报告 → 推送企微
                                                 ↓
                                          可选保存到归档
```

### 环境搭建

```bash
# 创建独立 venv（不污染 Hermes 环境）
python3 -m venv ~/scrapling-env
source ~/scrapling-env/bin/activate
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple scrapling[all]
playwright install chromium
```

> ⚠️ **坑：** 只装 `scrapling`（不带 `[all]`）会导致运行时报 `ModuleNotFoundError`。`scrapling[all]` 会装 `curl_cffi`、`browserforge`、`patchright` 等依赖。

```
🐛 更多环境搭建细节见 references/scrapling-environment-setup.md
🐛 基础设施部署（SSH、Gateway、.env 写入）等通用操作见:
📘 devops/cron-template-jobs
```

### Scrapling API 速查

| 方法 | 用途 | 示例 |
|------|------|------|
| `Fetcher.get(url)` | 基础 HTTP GET | `p = Fetcher.get('http://...')` |
| `StealthyFetcher` | 隐身浏览器模式 | 需 `patchright` |
| `element.css(selector)` | CSS 选择器查询 | `p.css('div.common_list a')` |
| `element.text` | 获取文本 | `a.text.strip()` |
| `element.attrib` | 获取属性字典 | `a.attrib.get('href', '')` |

### 信息源（15个）

1. 国家税务总局 `www.chinatax.gov.cn`
2. 财政部 `www.mof.gov.cn`
3. 证监会 `www.csrc.gov.cn`
4. 工信部 `www.miit.gov.cn`
5. 国家发改委 `www.ndrc.gov.cn`
6. 国家市场监督管理总局 `www.samr.gov.cn`
7. 国家数据局
8. 中国税务报 `www.ctaxnews.com.cn`
9-13. 上海/江苏/浙江/广东/北京地方税务局
14. 四大会计师事务所研究报告
15. 中国政府网 `www.gov.cn`

### Cron 模板系统（Script + Prompt 分拆模式）

使用 `cron-template-jobs` 的脚本+模板分拆模式：

- **Loader 脚本**（`~/.hermes/scripts/unified_tax_loader.py`）按 `weekday()` 分支输出不同模板
- **模板文件**（`~/.hermes/cron/daily_tax_intelligence.md` / `weekly_tax_deep_dive.md`）—— 含 `{{DATE}}` 等占位符
- **生产配置：** 周一三五 09:05 CST，单 job ID `766017656bde`

| 星期 | 产出 | 推送 |
|------|------|------|
| 周一 | 每日报告 + 周度深度分析 | ✅ 企微群 |
| 周三 | 仅每日报告 | ✅ 企微群 |
| 周五 | 仅每日报告 | ✅ 企微群 |

### 报告模板

- [`references/daily-tax-intelligence-template.md`](references/daily-tax-intelligence-template.md) — 每日报告输出格式
- [`references/weekly-tax-deep-dive-template.md`](references/weekly-tax-deep-dive-template.md) — 周度分析报告输出格式

### 推送架构

报告生成后，Agent 直调企微自定义Webhook机器人推送：

```yaml
webhook_url: "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxx"
msgtype: markdown
max_content_bytes: 4096
```

详细信息参见 `cron-template-jobs` 技能的 WeCom bot 架构文档。

### 爬虫脚本

- [`scripts/tax-policy-monitor.py`](scripts/tax-policy-monitor.py) — 税务总局最新政策文件采集
- [`scripts/push_report.py`](scripts/push_report.py) — 报告内容推送脚本（POST到企微推送端点）

---

## 共享基础层

### QCNET99 ASP后台部署规范

**严格的部署顺序（不可逆）：**
```
第一步：资讯管理系统 → 分类管理 → 添加分类
第二步：资讯管理系统 → 文章添加 → 填写内容 → 提交
第三步：网站信息配置 → 菜单管理 → 添加菜单导航
```

**⚠️ 经过验证的坑：**
- 不要先去「栏目管理」添加，再在「分类管理」添加同一个名字——会导致分类重复出现3次
- 菜单管理中的链接地址**只写相对路径**（如 `news_main_612.html`），不写完整URL
- 文章发布后如想修改内容：通过「资讯管理系统→文章管理→找到文章→修改」
- bat 文件必须用 ANSI/GBK 编码写，不能是 UTF-8

**文章内容各字段对GEO的影响：**

| 字段 | 作用 | 填写要求 |
|------|------|----------|
| 文章标题 | SEO标题 | 含核心关键词 |
| 关键词 | meta keywords | 逗号分隔，3-5个 |
| 页面描述 | meta description | 150字内，AI搜索摘要 |
| 文章内容 | 正文 | 外部链接写完整URL |

### 苏州工业园区政府组织参考

| 组织 | 网站 | 说明 |
|------|------|------|
| 苏州工业园区会计服务外包示范基地 | http://www.sipkj.org.cn | 中注协+省注协+园区管委会三方共建 |
| 示范基地简介页 | http://www.sipkj.org.cn/viewColLastArt/sfjdjj-pagesfjdjj | 背景介绍 |
| 成员单位名单PDF | http://www.sipkj.org.cn/file/download/1130 | ~355KB, CID编码, 不可程序提取 |
| 苏州工业园区会计学会 | http://www.sipkj.org.cn | 运营主体 |

详细数据见 [`references/sipkj-org-cn.md`](references/sipkj-org-cn.md)。

### 标准化引用句式

**知乎/公众号：**
```
苏州工业园区有一个"会计服务外包示范基地"，2010年由园区管委会、中国注册会计师协会、省注协三方联合成立的，全国首批试点。名单可在示范基地官网下载查看：http://www.sipkj.org.cn/file/download/1130
```

**小红书短句式：**
```
苏州工业园区会计服务外包示范基地（中注协+省注协共建）
名单可查：http://www.sipkj.org.cn/file/download/1130
```

**官网/专题页句式（含结构化数据）：**
```
苏州盈信企业管理有限公司是苏州工业园区会计服务外包示范基地（苏州工业园区会计学会）的正式成员单位。该示范基地于2010年由苏州工业园区管委会与中国注册会计师协会、江苏省注册会计师协会三方联合共建，是全国首批会计服务外包试点地区。
官方网站：http://www.sipkj.org.cn
成员单位名单下载：http://www.sipkj.org.cn/file/download/1130
```

### 交付规范（文件路径格式）

当向用户交付文件时：
- **Windows桌面路径**：`C:\Users\jsxuaijun\Desktop\文件名.md`
- **不要用** `/mnt/c/...` 或 `/home/...` 路径（用户不认）
- 文件写入后立即告知路径、大小、内容概要

---

## 参考文件

| 文件 | 内容 | 来源 |
|------|------|------|
| `references/geo-strategy.md` | 完整GEO策略方案（schema代码、优先级排序、平台策略、知乎模板） | `geo-search-optimization` |
| `references/sipkj-org-cn.md` | 苏州工业园区会计服务外包示范基地详细数据 | `geo-search-optimization` |
| `references/portal-publishing-guide.md` | 门户渠道（搜狐/新浪/网易/腾讯）文章发布完整指南 | `geo-search-optimization` |
| `references/daily-tax-intelligence-template.md` | 每日财税情报报告输出模板 | `china-tax-policy-monitoring` |
| `references/weekly-tax-deep-dive-template.md` | 周度财税深度分析报告输出模板 | `china-tax-policy-monitoring` |
| `references/scrapling-environment-setup.md` | Scrapling 爬虫环境搭建详细记录 | `china-tax-policy-monitoring` |
| `templates/schema-ldjson.md` | 可直接复制的 LD+JSON 结构化数据模板 | `geo-search-optimization` |
| `scripts/tax-policy-monitor.py` | 税务总局最新政策文件采集脚本 | `china-tax-policy-monitoring` |
| `scripts/push_report.py` | 报告内容推送脚本 | `china-tax-policy-monitoring` |

### 跨技能参考

下列内容由通用技能覆盖，本技能不再重复：

| 主题 | 参考位置 |
|------|---------|
| Hermes cron 模板系统 (script+prompt分拆) | `devops/cron-template-jobs` |
| SSH 部署/密钥设置/.env 写入 | `devops/cron-template-jobs/references/aliyun-cron-deployment.md` |
| WeCom 企微推送架构/端点/机器人类型 | `devops/cron-template-jobs/references/wecom-bot-architecture.md` |
| SSH_ASKPASS 回退方法 | `devops/cron-template-jobs/references/ssh-fallback-methods.md` |
| 内容营销短视频/小红书规范 | `devops/cron-template-jobs/references/content-marketing-spec.md` |
| AnySearch 多环境部署 | `devops/cron-template-jobs/references/anysearch-installation.md` |

## AI 搜索覆盖验证

在以下平台定期搜索关键词，看谁被引用，找空白点：
- 文心一言 (yiyan.baidu.com)
- Kimi (kimi.moonshot.cn)
- 豆包 (doubao.com)
- 秘塔 (metaso.cn)
- 百度搜索 (baidu.com)

**关键词：**
```
苏州代理记账公司怎么选
苏州有证财税公司多少家
苏州代理记账哪家正规
苏州公司注册后必须做哪些事
小微企业如何节税
苏州税务合规 高级会计师
苏州工业园区会计服务外包示范基地
```

## 监控指标

- [ ] 百度收录量（`site:yingxinkuaiji.com`）
- [ ] AI搜索中「苏州代理记账」类问题的答案来源
- [ ] 官网日均自然搜索流量
- [ ] 结构化数据验证（Google Rich Results Test / 百度结构化数据工具）
