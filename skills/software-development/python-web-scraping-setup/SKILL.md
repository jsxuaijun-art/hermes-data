---
name: python-web-scraping-setup
description: Cross-platform web scraping environment setup — DrissionPage, scrapling, curl_cffi, Playwright, curl-impersonate. Covers WSL (Hermes venv) + Aliyun (system Python) dual-env deployment, shared scripts via GitHub, and environment verification.
---

# Python 爬虫环境设置

## 工具选择原则 ★（2026-08-18 徐总定稿：谁能出结果用谁）

**原则：哪个爬虫能达到效果就用哪个，不区分国内国外，先出结果优先。**
遇到抓取任务：先判断 Firecrawl 能不能搞定、本地工具稳不稳，哪个更快到结果就用哪个，不硬分地域。
（提示性参考，不是硬性分栏——海外+文档+结构化→Firecrawl 顺手；政务+公众号+封闭平台+数据私有+免费无限→本地顺手）

**⚠️ 用国外资源前，提醒徐总开启代理（Clash）**
- Firecrawl 云 API（api.firecrawl.dev / mcp.firecrawl.dev）WSL 实测**直连可达**，一般不用代理
- 但访问 firecrawl.dev 官网/Dashboard、GitHub、npm registry、海外网站正文等**国外资源**时，
  先提醒「请开启代理(Clash 全局)」再继续——WSL 里 git/curl/浏览器走代理有坑，需手动开

| 场景 | 首选 | 备注 |
|------|------|------|
| 海外站 / JS渲染重 / 反爬强的境外页 | **Firecrawl**（MCP） | mcp_firecrawl_scrape 等 |
| 网页/PDF/DOCX/XLSX → Markdown 或结构化JSON | **Firecrawl parse/scrape** | 一键转干净文本给LLM |
| 要全文搜索结果 / 全站crawl / 定时监控 | **Firecrawl search/crawl/monitor** | 一条API搞定 |
| 国内政务/政策公文 | **本地 requests+bs4** | 搜狗/360 直抓，见 chinese-government-site-retrieval |
| 微信公众号正文 | **本地半强流程** | 搜狗微信，见 chinese-wechat-content-retrieval |
| 小红书/抖音/视频号（封闭平台） | 两者都难 | 按该平台的既有note/方案 |
| 数据要私有 / 免费无限量 / 重度批量 | **本地** Playwright/scrapling/curl_cffi | 不耗 credits |

> 以上为**参考倾向**，真正原则（徐总 2026-08-18 定稿）：**谁能达到效果就用谁，不区分国内外，先出结果优先**。用国外资源前提醒徐总开代理。

## Firecrawl（云 API · MCP 直连，2026-08-18 接入）

- **性质**：云抓取管道 API，号称覆盖 96% 网页，托管反爬/JS渲染/代理轮换，输出 LLM-ready Markdown/JSON
- **本机已配**：`~/.hermes/.env` 的 `FIRECRAWL_API_KEY`（0600 权限，不同步）+ `config.yaml` 的 `mcp_servers.firecrawl`（HTTP 端点 `https://mcp.firecrawl.dev/v2/mcp` + Bearer 头）
- **⚠️ mcp 库锁定 1.28.1**（pyproject 项目的 `mcp==1.28.1`，勿升 2.x——`streamable_http_client` 的 yield 值数不同会导致 Hermes MCP 崩）
- **免费档 1000 credits/月**：scrape/crawl/map/parse=1/page，search=2/10条，interact=2/浏览器分钟；失败请求不收费；重度再上 Hobby($16/月 5000页)
- **MCP 工具（26 个，重启 Hermes 后生效）**：`firecrawl_scrape/search/crawl/map/parse/interact/agent` + `monitor_*` + `research_*`（论文/代码检索）
- **触发词**：用户说「用 Firecrawl / 云抓 / 抓海外页 / 转文档 / 结构化抽取 / 搜全文」→ 走 MCP 工具
- **局限**：海外代理池为主，国内政务/封闭平台（公众号/小红书/抖音/视频号）不保证能过，别指望用它替代本地政务流程

## 安装策略（A方案 — 当前）

所有工具统一安装到 **Hermes 主 Python 环境**，不建独立 venv：

| 环境 | Python 路径 | 说明 |
|------|------------|------|
| **WSL 本地** | `~/.venv-hermes/` | Hermes 虚拟环境 |
| **阿里云** | `/usr/local/lib/hermes-agent/venv/` | Hermes 专用 venv（非系统 Python） |

> ⚠️ **关键路径坑**：阿里云 Hermes 的 venv 路径是 `/usr/local/lib/hermes-agent/venv/`，**不是** `$HOME/.venv-hermes` 也不是系统 Python。setup.sh 的自动检测必须覆盖这个路径，否则会装到系统 Python 而 Hermes 实际跑的还是旧的。

### 一键安装

```bash
git pull                                          # 确保最新脚本
bash scrapling/setup.sh                           # 自动检测环境 → 安装全部工具
python scrapling/scripts/test-scrapling.py         # 验证 4 个工具全部就绪
```

`setup.sh` 自动完成：
1. 检测 Hermes venv（优先级：`/usr/local/lib/hermes-agent/venv/` > `~/.venv-hermes/` > 系统 Python）
2. 安装 DrissionPage + scrapling + curl_cffi + Playwright
3. 安装 Playwright Chromium 浏览器
4. 安装 curl-impersonate 系统二进制
5. 验证所有工具就绪

### 包含工具

| 工具 | 层级 | 用途 | 安装方式 |
|------|------|------|----------|
| **Requests + BeautifulSoup** | ✅ 核心 | 基础 HTTP + HTML 解析 | 预装 |
| **Scrapy** | ✅ 核心 | 大规模爬虫框架 | `pip install` |
| **Playwright** | ✅ 核心 | 浏览器自动化（多浏览器） | pip + 二进制 |
| **DrissionPage** | 🔧 拓展 | 多线程/多标签浏览器自动化 | pip 直装 |
| **scrapling** | 🔧 拓展 | 自适应智能爬虫（GitHub ~23K Stars） | pip 直装 |
| **curl_cffi** | 🔧 拓展 | TLS 指纹模拟（Python 版） | pip 直装 |
| **curl-impersonate** | 🔧 拓展 | 系统级 curl 指纹模拟二进制 | 系统安装 |

## 共享脚本架构

爬虫脚本统一放在 `hermes-data/scrapling/scripts/` 目录，通过 GitHub 同步到所有机器：

```
hermes-data/
├── scrapling/             ← Git 同步
│   ├── setup.sh           ← 新电脑一键安装
│   ├── activate.sh        ← 快速激活 Hermes 环境
│   ├── README.md          ← 完整文档
│   └── scripts/
│       ├── test-scrapling.py      ← 环境验证（4 工具 + 深度导入）
│       ├── tax-policy-monitor.py   ← 税务政策监控
│       └── ...                     ← 后续添加
```

### 多机同步规则

| 项目 | 同步方式 | 说明 |
|------|---------|------|
| 爬虫脚本 (scripts/) | ✅ GitHub | 写一次，所有机器 `git pull` |
| 安装脚本 (setup.sh) | ✅ GitHub | 一次配置，多机复用 |
| Python 包 | ❌ 每台手动装 | 平台依赖，不能 git 同步 |
| Chromium 浏览器 | ❌ setup.sh 自动装 | ~170MB |
| curl-impersonate 二进制 | ❌ setup.sh 自动装 | TLS 指纹模拟 |

## WSL Playwright 依赖坑

WSL 最小化安装缺音频/图形库，Playwright 启动报错：

```
error while loading shared libraries: libasound.so.2: cannot open shared object file
```

**修复**（一行搞定）：
```bash
sudo apt-get install -y libasound2 libgtk-3-0 libgbm1 libx11-xcb1 libnss3 libxcomposite1 libxcursor1 libxdamage1 libxi6 libxrandr2 libxss1 libxtst6
```

## curl-impersonate 安装说明

GitHub release 从中国下载不稳定。setup.sh 先尝试 Python requests 下载（走代理），失败则提示手动安装：

```bash
# 手动下载
wget https://github.com/lwthiker/curl-impersonate/releases/download/v0.6.1/curl-impersonate-v0.6.1.x86_64-linux-gnu.tar.gz
tar -xzf curl-impersonate-v0.6.1.x86_64-linux-gnu.tar.gz
sudo cp curl_chrome* curl_ff* curl_edge* /usr/local/bin/
```

> **注意**：curl-impersonate 是**可选系统工具**。如果装不上，Python 端的 `curl_cffi` 提供了相同能力（TLS 指纹模拟），不影响爬虫开发。

## 环境验证

```bash
# 完整验证
python scrapling/scripts/test-scrapling.py

# 快速验证（单行）
python3 -c "import DrissionPage, scrapling, curl_cffi, playwright; print('All OK')"
```

验证脚本检查内容：
- ✅ 4 个 Python 包版本号（**使用直接 import 取 `__version__`，不要用 `importlib.metadata.version()`** — 有 corrupt dist-info 时会异常退出）
- ✅ DrissionPage.ChromiumPage 可导入
- ✅ scrapling.Fetcher/StealthyFetcher 可导入
- ✅ curl_cffi 实际请求（impersonate=chrome110）
- ✅ playwright.sync_api 可导入

> ⚠️ **importlib.metadata 陷阱**：某个包的 `.dist-info` 目录损坏（如 `~etuptools`）会导致 `importlib.metadata.version()` 抛异常，但 `import` 实际正常。验证脚本必须用 `pkg.__version__` 方式抓版本，不能用 `importlib.metadata.version(pkg)`。

## 用户偏好：快速失败策略

当爬虫任务启动时，**按工具阶梯快速尝试，不要逐个工具深度调试**。如果前三阶都失败（curl_cffi → curl-impersonate → Playwright），直接报告结果并切换方案B（人工采集）。用户明确偏好"先试，不行就方案B"，不需要花大量时间绕反爬。

**爬虫工具清单**（可用工具，按优先级排列）：
1. scrapling（自适应智能爬虫）— 注意需 `pip install patchright` 一起装
2. Playwright（浏览器自动化）— 注意反检测注入脚本
3. DrissionPage（多标签浏览器自动化）— 注意需要Chrome二进制
4. curl_cffi（Python TLS模拟）— 纯HTTP，过不了JS签名
5. curl-impersonate（系统二进制）— 绕过TLS但可能触发CAPTCHA
6. agent-reach（备用）

**用户流程偏好**：
- 不要深入调试单一工具超过3次尝试
- 工具失败后立即切换，记录结果即可
- 全部失败后给完整表格报告，建议人工方案
- 用户会批准方案B（手动采集20-30条），数据质量第一

## 反爬绕过策略（多工具轮替阶梯）

当目标网站有强反爬（抖音、小红书等）时，按此阶梯依次尝试，每级失败后降级到下一级：

### 阶梯1: curl_cffi（TLS 指纹模拟）

```python
from curl_cffi import requests
s = requests.Session()
s.get('https://target.com/', impersonate='chrome120', timeout=15)
# 然后尝试 API 请求
r = s.get('https://target.com/api/endpoint', impersonate='chrome120')
```

**适用场景**: 仅 TLS 指纹检测的网站（Cloudflare 第一层）
**抖音实测结果**: 首页 200，acrawler JS 加密反爬挡 API（返回 200 空 body）

### 阶梯2: curl-impersonate（系统二进制）

```bash
curl-impersonate-chrome -s \
  -H 'User-Agent: Mozilla/5.0 ...' \
  --cookie-jar cookies.txt \
  'https://target.com/'
```

**适用场景**: TLS 指纹 + 基础 cookie 验证
**抖音实测结果**: 触发验证码中间页（CAPTCHA）

### 阶梯3: Playwright（浏览器自动化 + 反检测初始化脚本）

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=['--disable-blink-features=AutomationControlled']
    )
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 ... Chrome/120.0.0.0 ...',
        locale='zh-CN',
        timezone_id='Asia/Shanghai',
    )
    page = context.new_page()
    # 绕过 CDP/webdriver 检测
    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
        Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh'] });
        window.chrome = { runtime: {} };
    """)
    page.goto(url, wait_until='domcontentloaded')
```

**适用场景**: 页面级 JS 反爬、acrawler、验证码前
**抖音实测结果**: 无头模式被抖音超时拦截（IP 环境标记）

### 阶梯4: DrissionPage（浏览器自动化，指定已登录的 Chrome 实例）

```python
from DrissionPage import ChromiumPage
# 需要先指定已安装的 Chrome 路径
page = ChromiumPage()
page.set.cookies(cookies)  # 可通过已有浏览器导入
page.get(url)
```

**注意**: DrissionPage 需要找到 Chrome 可执行文件。WSL 默认找不到，需手动指定路径或使用 `chrome_path` 参数。
**抖音实测结果**: 本环境未成功启动（Chrome 未安装）

### 阶梯5: 方案B — 人工采集

当以上自动化手段全部失败时，切换人工方案：
1. 手机端手动浏览目标账号
2. 按「最多点赞」排序
3. 采集 20-30 条爆款数据（标题、点赞、评论、时长、发布时间）
4. 用于后续 RIA-TV 萃取分析

## 抖音/短视频平台反爬专项

| 工具 | 首页加载 | API 请求 | 视频列表 | 文案获取 |
|------|----------|----------|----------|----------|
| curl_cffi (chrome120) | ✅ 200 | ❌ 空 body | ❌ acrawler 拦截 | ❌ |
| curl-impersonate | ✅ 200 | ❌ CAPTCHA | ❌ | ❌ |
| Playwright 无头 | ❌ Timeout | ❌ | ❌ | ❌ |
| DrissionPage | ❌ 缺浏览器 | ❌ | ❌ | ❌ |

**抖音反爬机制总结**：
1. **acrawler 签名** — 所有 API 请求需要 `X-Bogus` 签名（动态 JS 生成）
2. **CAPTCHA 验证码** — 异常 IP 直接触发人机验证
3. **IP 信誉系统** — 公共云/机房 IP 被标记（WSL、阿里云等环境基本上不了）
4. **__ac_nonce** — 每次会话动态生成，需配合 acrawler 签名

**可行路线**（已验证）：
- 获取真实手机/PC 登录态 Cookie + acrawler 签名 SDK
- 抖音开放平台 OAuth API（需企业资质申请）
- 使用已登录的浏览器（非无头）+ 代理环境重试
- 第三方数据平台（蝉妈妈、新抖、飞瓜数据）付费获取

### 中国教育类网站爬虫
见 `references/chinese-education-site-scraping.md`。
百度文库有词汇表但需登录；Bing搜索结果不稳定；百度搜索触发验证码。
**推荐替代**：频率筛选法（从词频库中取高频词交集）而非在线搜索。

### 中国政府网站检索/抓取（地方财政局/公文通知）
见 `references/chinese-government-site-retrieval.md`（2026-08 实测）。
定位地方政务公文：**首选搜狗 sogou.com / 360 so.com（都能 requests+bs4 直抓中文政务结果，360 支持 site: 限定）**，
其次上海市政府统一检索 search.sh.gov.cn（必须浏览器，结果JS渲染）。
czj.sh.gov.cn 首页/文章页可 requests 直抓但栏目列表页返回 `Template not found json://{siteId}` 模板错误、
站内 was5 搜索 404；cn.bing 对中文政务长查询分词错乱，政务检索基本不可用；gov.cn 子域 DNS 拦。
**sogou/360 结果里的跳转链（/link、so.com/link?m=）requests 直解返回 400，须用浏览器打开结果页点击后取落地 URL。**
查不到行业自查/专项整治通知时用「特征判断法」（上位依据如沪财发〔2025〕8号网关公开）缩小范围并请用户提供红头文件，勿无限搜索。
上海市 16 区财政局站点地图（区级独立官网 reachability+栏目路径规律，含嘉定 caizheng.jiading.cn、青浦 /fina/ 等）见同文件「五·B」节。

### 微信公众号 / 视频号 检索
见 `references/chinese-wechat-content-retrieval.md`（2026-08 实测）。
行业专项自查/监管新政官网无公开页时，公众号转载是主要情报源：搜狗微信 weixin.sogou.com/weixin?type=2 **requests 可抓标题+正文长摘要**
（浏览器直开触发 antispider wx_sh2、/link?url= 跳转解不出 mp.weixin 地址，靠摘要收集即可）；**要拿可点击的 mp.weixin 直链给用户：用搜狗网页版 www.sogou.com/web?query=<标题> 直接抓 return 的 mp.weixin.qq.com/s 秒传链接；但秒传链接正文是 JS 模板壳，自动化环境读不到全文，勿承诺能读正文**；
视频号是微信封闭生态**进不了任何搜索引擎**，用 360 视频 tv.360kan.com 确认"无相关视频"即可排除该渠道。
公众号文号必须到官方源二次核对（尤其警惕标题相近的两个号，如财办会〔2026〕7号 vs 财会〔2026〕8号），核对不到的标注"公众号口径未确认"，勿直接引用。

## 新媒体平台检索现状与观察清单（2026.8.14 用户要求持续研究）

**各平台当前真实能力：**

| 平台 | 现状 | 判定 |
|:--|:--|:--|
| 抖音 | 短链→video id→browser+页面内fetch aweme API，拿标题/作者/数据/章节要点/视频转写 | ✅ 强 |
| B站 | 有公开搜索/API | ✅ 可用 |
| 公众号 | 搜狗微信抓标题+长摘要；mp.weixin 链接用手机UA+Referer拿全文 | ⚠️ 半强（搜索发现难，正文JS壳） |
| 视频号 | 封闭生态，进不了搜索引擎；仅browser打开sph分享链接看JS渲染标题 | ❌ 封闭 |
| 微博 | weibo.com/m.weibo.cn 反爬较强 | ⚠️ 受限 |
| 小红书 | 反爬极强，需登录+xsec_token签名 | ❌ 基本拿不到 |

**封闭/半封闭平台还可试的变通手段（按推荐序）：**
1. **分享链接 meta 解析（轻量通用）**：平台分享到微信/QQ的卡片页带 `og:title/description/image`，requests 直抓分享短链→落地页的 meta 标签，能拿标题、简介、封面，无需登录。适用于视频号/小红书/公众号/微博/抖音/B站所有带分享卡片的平台。**这是目前对封闭平台最轻量的手段**，尚未系统验证。
2. **浏览器打开分享链接看 JS 渲染页**：视频号（已验证能看标题）、小红书分享页有时可看。
3. **第三方数据/聚合平台（付费/注册）**：新榜（公众号/视频号/小红书）、西瓜数据（公众号）、千瓜/灰豚（小红书）、蝉妈妈/飞瓜（抖音/快手）——榜单、热门、部分搜索。
4. **开放平台 API（需企业资质+申请）**：抖音/微博/微信/B站开放平台——正规强手段，合规搜索拉取。
5. **RSS 桥（RSSHub）**：微博、B站、部分平台可通过 RSSHub 订阅/检索，绕部分限制。
6. **开源逆向工具（不稳定/有风险）**：xhs-api（小红书）、TikTokDownload 等——能用但不稳、可能违规，谨慎。
   > **2026-Q3 更新**：小红书开源采集生态持续活跃，以下项目被社区推荐（均需登录态 Cookie，xhs 库已封装 x-s/x-t 签名）：
   > - **xhs 库**（小红书数据采集，CSDN 2026-07 有教程，"xhs 让复杂 API 变简单"）
   > - **XHS-Downloader2**（github.com/JoeanAmier/XHS-Downloader）
   > - **RedNote MCP**（github.com/iFurySt/RedNote-MCP，小红书 MCP 服务）
   > - **Spider_XHS**（小红书数据运营+爬虫）
   > - 小红书网页版 Web API 逆向 2026 版可解 JSVMP 防护（CSDN 2026-03），但签名随版本变动，仍不稳、有合规风险，**谨慎评估后按需试用**。

**持续观察项（用户要求：一旦出现强手段必须提醒）：**
- [ ] 各平台**开放平台 API** 的搜索能力是否开放（尤其中小资质可申请）— **2026-Q3 无突破**：抖音/微博/微信开放平台仍企业资质导向、无公开免费搜索；视频号官方仅 channels.weixin.qq.com 视频号助手提供基础数据查询
- [x] 第三方数据平台是否新增**免费搜索/索引**通道 — **2026-Q3 无免费新增**：新榜/新红仍以付费投放、达人管理、竞品跟踪为主（商业产品），未开放免费搜索；新榜矩阵通聚合 10+ 平台（视频号/抖音/小红书等）但需付费
- [x] 是否出现**稳定开源逆向**方案（xhs-api 等成熟度）— **2026-Q3 部分进展（非强手段）**：小红书 xhs 库/XHS-Downloader2/RedNote MCP/Spider_XHS 持续活跃（需登录态 Cookie+签名），可用但签名随版本变动、仍不稳且有合规风险，**尚不足以稳定自动化抓取封闭平台全文/视频**
- [ ] 微信/腾讯对**视频号的外部索引**（微信视频号助手、搜一搜开放程度）— 仍封闭，进不了搜索引擎
- [ ] 分享链接 **og:meta 解析**在封闭平台（视频号/小红书）实测是否可行 — 尚未系统验证

**2026-Q3 季度调研结论**：本季度无「强手段」突破。唯一实质进展是**小红书开源采集工具生态活跃**（xhs 库/XHS-Downloader2/RedNote MCP/Spider_XHS），但均需登录态且签名易变，只能算「可按需试用」的中等手段，不足以替代方案 B 人工采集。

> 涉及新媒体检索任务时，先对照本表；本表能力变化/新手段出现 → 主动提醒用户。

## 爬虫调试流水账

| 日期 | 目标 | 尝试工具 | 结果 |
|------|------|----------|------|
| 2026-06-21 | 彭会计财税(抖音) | scrapling(缺patchright) → curl_cffi(200空body) → Playwright(超时) → DrissionPage(缺浏览器) → curl-impersonate(CAPTCHA) | ❌ 全失败，切换方案B |

各工具最新全景对照表见 `references/2026-07-scraping-tools-overview.md`（2026年7月20日更新，含GitHub Star数、版本、最新实测数据）。

## ⚠️ 已知坑点

### scrapling 缺 patchright 依赖
scrapling 0.4.9 的 `StealthyFetcher` 依赖 `patchright` 包。如果只 `pip install scrapling` 而未同时安装 `patchright`，会报：
```
ModuleNotFoundError: No module named 'patchright'
```
**修复**：`pip install patchright`（注：patchright 是 Playwright 的 fork，安装前需确认兼容性）

### DrissionPage 找不到 Chrome 可执行文件
```
FileNotFoundError: 未找到浏览器。
```
DrissionPage 默认自动检测 Chrome 路径。WSL 中如果没有安装 Chrome，需要：
1. 安装 Chrome 到 WSL（或使用 Chromium）
2. 或指定路径：`ChromiumPage(chrome_path='/path/to/chrome')`
3. 或连接到已运行的 Chrome 实例（`ChromiumPage(addr_or_opts=...)`）

## 完整安装记录

| 日期 | 操作 | 详情 |
|------|------|------|
| 2026-06-10 | 核心三件套（Playwright + Scrapy + BS4） | WSL 安装成功，Chromium 超时一次后重试通过 |
| 2026-06-16 | 状态检查 | Playwright ✅ 已装，DrissionPage/scrapling/curl ❌ |
| **2026-06-16** | **A方案决策** | **放弃独立 venv，全部装进 Hermes 主环境** |

## 验证脚本（scripts/verify-crawler-env.py）

```python
#!/usr/bin/env python3
"""
爬虫环境验证脚本 — 检测核心工具（Playwright + Scrapy + Requests/BS4）
及拓展工具（DrissionPage + scrapling + curl_cffi + curl-impersonate）

用法：
    python3 scripts/verify-crawler-env.py

返回码：0 = 核心全部通过, 1 = 核心有失败项
"""

import subprocess
import sys


def check_requests_bs4():
    """验证 Requests + BeautifulSoup"""
    try:
        import requests
        from bs4 import BeautifulSoup

        r = requests.get("https://www.baidu.com", timeout=5)
        soup = BeautifulSoup(r.text, "lxml")
        title = soup.title.text.strip()
        print(f"  ✅ Requests {requests.__version__} + BS4 OK (title: {title[:20]})")
        return True
    except Exception as e:
        print(f"  ❌ Requests/BS4 失败: {e}")
        return False


def check_scrapy():
    """验证 Scrapy CLI"""
    try:
        result = subprocess.run(
            ["scrapy", "version"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            ver = result.stdout.strip()
            print(f"  ✅ Scrapy {ver} OK")
            return True
        else:
            print(f"  ❌ Scrapy CLI 报错: {result.stderr.strip()}")
            return False
    except FileNotFoundError:
        print("  ❌ scrapy 命令未找到")
        return False
    except Exception as e:
        print(f"  ❌ Scrapy 检查异常: {e}")
        return False


def check_playwright():
    """验证 Playwright + Chromium 浏览器"""
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://www.baidu.com")
            title = page.title()
            browser.close()
        print(f"  ✅ Playwright OK (chromium, title: {title[:20]})")
        return True
    except ImportError:
        print("  ❌ playwright Python 包未安装")
        return False
    except Exception as e:
        msg = str(e)
        if "Executable doesn't exist" in msg:
            print("  ❌ Playwright 浏览器二进制文件未安装 (需运行: playwright install chromium)")
        elif "cannot open shared object file" in msg:
            print("  ❌ 系统依赖缺失 (需安装: libasound2, libgtk-3-0 等)")
        else:
            print(f"  ❌ Playwright 启动失败: {msg}")
        return False


def check_drissionpage():
    """验证 DrissionPage（可选拓展）"""
    try:
        import DrissionPage
        print(f"  ✅ DrissionPage {getattr(DrissionPage, '__version__', 'OK')}")
        return True
    except ImportError:
        print("  ⏭️   DrissionPage 未安装（可选拓展）")
        return None
    except Exception as e:
        print(f"  ⚠️   DrissionPage 异常: {e}")
        return None


def check_scrapling():
    """验证 scrapling（可选拓展）"""
    try:
        import scrapling
        print(f"  ✅ scrapling {getattr(scrapling, '__version__', 'OK')}")
        return True
    except ImportError:
        print("  ⏭️   scrapling 未安装（可选拓展）")
        return None
    except Exception as e:
        print(f"  ⚠️   scrapling 异常: {e}")
        return None


def check_curl_cffi():
    """验证 curl_cffi（可选拓展 — Python TLS 指纹伪装）"""
    try:
        import curl_cffi
        from curl_cffi import requests
        ver = getattr(curl_cffi, '__version__', 'OK')
        r = requests.get("https://httpbin.org/headers", impersonate="chrome110", timeout=10)
        ok = "✅" if r.status_code < 500 else "⚠️"
        print(f"  {ok} curl_cffi {ver} (httpbin status: {r.status_code})")
        return True
    except ImportError:
        print("  ⏭️   curl_cffi 未安装（可选拓展 — pip install curl_cffi）")
        return None
    except Exception as e:
        print(f"  ⚠️   curl_cffi 异常: {e}")
        return None


def check_curl_impersonate_binary():
    """验证 curl-impersonate 系统二进制（可选拓展）"""
    try:
        result = subprocess.run(
            ["curl-impersonate-chrome", "--version"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            ver = result.stdout.strip().split('\n')[0]
            print(f"  ✅ curl-impersonate-chrome {ver}")
            # 快速测试：访问一个 URL
            test = subprocess.run(
                ["curl-impersonate-chrome", "-sI", "--max-time", "5", "https://httpbin.org/headers"],
                capture_output=True, text=True, timeout=10
            )
            if test.returncode == 0:
                print(f"     快速测试通过 (HTTP {test.stdout.split()[1] if test.stdout else 'N/A'})")
            else:
                print(f"     ⚠️  快速测试失败: {test.stderr.strip()[:80]}")
            return True
        else:
            print(f"  ❌ curl-impersonate-chrome 返回异常: {result.stderr.strip()}")
            return False
    except FileNotFoundError:
        print("  ⏭️   curl-impersonate-chrome 未安装（可选系统工具）")
        return None
    except Exception as e:
        print(f"  ⚠️   curl-impersonate-chrome 检查异常: {e}")
        return None


def main():
    print("=" * 52)
    print("  爬虫工具 — 环境验证（核心 + 拓展）")
    print("=" * 52)

    core_results = [
        ("Requests + BeautifulSoup", check_requests_bs4()),
        ("Scrapy", check_scrapy()),
        ("Playwright", check_playwright()),
    ]

    extra_results = [
        ("DrissionPage", check_drissionpage()),
        ("scrapling", check_scrapling()),
        ("curl_cffi", check_curl_cffi()),
        ("curl-impersonate 系统二进制", check_curl_impersonate_binary()),
    ]

    print("=" * 52)
    core_passed = sum(1 for _, ok in core_results if ok)
    core_total = len(core_results)
    extra_installed = sum(1 for _, ok in extra_results if ok is True)
    extra_checked = sum(1 for _, ok in extra_results if ok is not None)

    if core_passed == core_total:
        print(f"  ✅ 核心全部通过 ({core_passed}/{core_total}) — 环境就绪")
    else:
        print(f"  ⚠️  核心 {core_passed}/{core_total} 通过 — 需修复以上失败项")

    if extra_installed > 0:
        print(f"  ✅ 拓展工具 {extra_installed}/{len(extra_results)} 已安装")
    else:
        print(f"  ℹ️  拓展工具 ({len(extra_results)}) 均未安装，按需安装")

    return 0 if core_passed == core_total else 1


if __name__ == "__main__":
    sys.exit(main())