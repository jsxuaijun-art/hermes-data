---
name: scraping-dispatch
description: 爬虫任务自主调度中枢。遇到任何"抓取/爬取/采集/取数/搜索网页"需求时，由 agent 按决策树自主选工具、自动执行、失败降级，不必每次从零摸索。聚合了 python-web-scraping-setup 的全部工具知识 + 真实环境状态。
---

# 爬虫任务自主调度 (Scraping-Dispatch)

## 触发条件
用户提出：抓取 / 爬取 / 采集 / 取数 / 下载网页 / 搜某个站的数据 / 批量拿内容。凡属取数，本 skill 自动接管，无需问用户选哪个工具。

## 第一步：判断来源类型（永远先做，不要直接钻进工具）
| 类型 | 特征 | 首选工具 |
|------|------|---------|
| 静态 HTML | 无 JS 渲染，右键源码能看到数据 | Requests+BS4 |
| 开放 API / JSON | 页面调接口 | curl_cffi / requests |
| JS 渲染 | 源码空、需浏览器执行 | Playwright / patchright(StealthyFetcher) |
| 大规模批量 | 上千页、需去重/管道 | Scrapy |
| 需登录态 | 数据在登录墙后 | DrissionPage(接管已登录Chrome) |
| 强反爬(抖音/小红书等) | 有签名/验证码/IP信誉 | 直接降级方案B人工，不硬磕 |

> 关键经验：先搜索发现（anysearch），再判断来源决定工具，比无脑走浏览器阶梯高效。2026.7.8 雅思词汇案例 = AnySearch 找到 GitHub 仓库 → GitHub API 两步拿全 2141 行，全程没用浏览器。

## 环境状态（2026-08-04 实装，Hermes 主环境 ~/.venv-hermes）
| 工具 | 状态 | 版本 | 备注 |
|------|------|------|------|
| Requests+BS4 | ✅ | 预装 | 静态站 |
| Scrapy | ✅ | 预装 | 大规模 |
| Playwright | ✅ | 1.60.0 | chromium-1223 缓存 |
| DrissionPage | ✅ | 4.1.1 | 需 Chrome 二进制，WSL 默认无 |
| scrapling | ✅ | 0.4.9 | Fetcher + StealthyFetcher 均可导入 |
| patchright | ✅ | 1.61.2 | chromium build 1228，StealthyFetcher 依赖 |
| curl_cffi | ✅ | 0.15.0 | TLS 指纹模拟 |
| curl-impersonate | ✅ | 已装 | 系统二进制 chrome 分支 |
| msgspec | ✅ | 0.21.1 | scrapling 依赖 |
| agent-reach | ✅ | 0.1.0 | LLM agent 渠道抓取(RSS/YouTube) |

## 反爬阶梯（遇强反爬按序尝试，每级最多 3 次，全败→方案B）
1. **curl_cffi** `impersonate='chrome120'` — 过 TLS 指纹第一层
2. **curl-impersonate** 系统二进制 — 过 TLS+基础 cookie
3. **patchright/StealthyFetcher** — 浏览器级隐身（最新补强项，见下）
4. **Playwright** 无头 + 反检测 init 脚本
5. **DrissionPage** 接管已登录 Chrome
6. **方案B 人工采集**（用户偏好，数据质量第一）

## patchright 用法（scrapling 隐身抓取，2026-08-04 实测打通）
```python
from scrapling.fetchers import StealthyFetcher
page = StealthyFetcher.fetch('https://target.com', headless=True, timeout=30000)
page.status            # HTTP 状态码
page.html_content      # 渲染后完整 HTML
page.text              # 页面纯文本
page.css('h1')         # CSS 选择器取节点
```
⚠️ scrapling 0.4.9 的 Response API：用 `page.text` / `page.html_content` / `page.css()`，**没有** `.title` 和 `.html` 属性（实测报 AttributeError）。referer 自动伪装成 google.com，隐身抓取链路已 2026-08-04 端到端验证成功。
前置依赖：`pip install patchright msgspec`，且 `python -m patchright install chromium` 已装（build 1228，镜像：`PLAYWRIGHT_DOWNLOAD_HOST=https://cdn.npmmirror.com/binaries/playwright`）。

## 代理坑（必须遵守）
本机存在残留代理配置指向 `172.23.96.1:7890`，但代理经常未就绪，会拖死一切网络操作。
- **pip 安装**：必须加 `--proxy '' --index-url https://pypi.tuna.tsinghua.edu.cn/simple`，否则连代理超时装不上。
- **浏览器下载**：`export PLAYWRIGHT_DOWNLOAD_HOST=https://cdn.npmmirror.com/binaries/playwright` + `unset http_proxy https_proxy all_proxy`。
- curl 直连清华/镜像通常 200，直接走直连最稳。

## 自主执行规范
1. 先探测目标（`curl -sI` 或 curl_cffi 首页状态码），确认可访问
2. 按决策树选工具，写脚本执行
3. 用 `execute_code` 或后台 terminal 跑，避免阻塞
4. 抓回数据立即验证条数/完整性，不空手交差
5. 全失败 → 输出完整表格报告 + 建议方案B，交给用户拍板

## 验证
```bash
python ~/.hermes/skills/software-development/python-web-scraping-setup/scripts/verify-crawler-env.py
```
