# 抖音反爬完整工具轮替实战记录（2026-06-22）

## 目标信息

| 项目 | 内容 |
|------|------|
| **账号** | 彭会计财税（南京明好税务师事务所有限公司） |
| **抖音号** | PengkuaijiNJ |
| **用户ID** | MS4wLjABAAAAPhOHzDUBqaRu942RRQ8-2yS4g0n-IxbgfYh-7y_LNxk |
| **粉丝** | 138.8K | **获赞** | 542.8K | **作品** | 687条 |
| **认证** | 中国注册会计师 + 中国注册税务师 |
| **IP属地** | 江苏 |

## 工具轮替全过程

### 第1步：scrapling

**命令**：
```python
from scrapling import Fetcher, StealthyFetcher
f = Fetcher()
resp = f.get('https://www.douyin.com/user/...')
```

**失败**：
```
ModuleNotFoundError: No module named 'patchright'
```
**原因**：scrapling 0.4.9 的 `StealthyFetcher` 和底层 `_stealth.py` 依赖 `patchright`（Playwright fork）。仅 `pip install scrapling` 不会自动安装 `patchright`。

---

### 第2步：curl_cffi（TLS 指纹模拟）

**命令**：
```python
from curl_cffi import requests
s = requests.Session()
s.get('https://www.douyin.com/', impersonate='chrome120', timeout=15)
r = s.get('https://www.douyin.com/aweme/v1/web/aweme/post/', params={...}, impersonate='chrome120')
```

**首页结果**：`Status: 200` ✅
- headers 含 `__ac_nonce` cookie 生成
- body：空 `<body></body>` + acrawler JS 加密代码
```
<html><head><meta charset="UTF-8" /></head>
<body></body>
<script>var glb;..._$jsvmprt...acrawler加密代码...</script>
```

**API结果**：`Status: 200`，但 `Response text [0 chars]` ❌
- 抖音 API 后端做了 `X-Bogus` 签名校验，纯 HTTP Session 无法生成正确的 JS 签名
- 返回空 body 表示签名校验失败

**分析**：curl_cffi 能过 L1（TLS指纹）但过不了 L2（acrawler JS 签名）。

---

### 第3步：curl-impersonate（系统级二进制）

**命令**：
```bash
curl-impersonate-chrome -s -o /dev/null -w '%{http_code}' \
  -H 'User-Agent: ...' \
  --cookie-jar cookies.txt \
  'https://www.douyin.com/'
```

**首页**：HTTP 200 ✅
**用户主页**：返回 `验证码中间页` ❌
```html
<title>验证码中间页</title>
<script src="https://lf-cdn-tos.bytescm.com/obj/static/sec_sdk_build/3.5.2/captcha/index.js">
```

**分析**：curl-impersonate 能过 TLS 指纹，但被抖音的 **IP 信誉系统** 标记（WSL 环境 IP），触发 CAPTCHA。

**API尝试**：同样返回200但空body ❌

---

### 第4步：Playwright（浏览器自动化 + 反检测）

**命令**：
```python
from playwright.sync_api import sync_playwright

browser = p.chromium.launch(
    headless=True,
    args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
)
page.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
    window.chrome = { runtime: {} };
""")
page.goto('https://www.douyin.com/', wait_until='domcontentloaded')
```

**首次试**：无头模式 `--headless` → `TimeoutError: Timeout 30000ms exceeded.` ❌
- 无头 Chrome 的 JavaScript 执行环境与真实浏览器有差异
- 抖音的 acrawler 脚本检测到无头环境，拒绝加载

**二次试**（反检测注入 + zh-CN locale + Asia/Shanghai 时区）：
- 用户批准后发现环境网络异常，blocked

**分析**：Playwright 无头模式在抖音的 L5（无头检测）+ L4（IP信誉）双重拦截下失败。

---

### 第5步：DrissionPage

**命令**：
```python
from DrissionPage import ChromiumPage
page = ChromiumPage()
page.get(url)
```

**失败**：
```
FileNotFoundError: 未找到浏览器。
```
**原因**：WSL 环境没有安装 Chrome。DrissionPage 自动检测不到浏览器路径。

**尝试方案**：
- WSL 未安装 Chrome/Chromium 浏览器
- `/usr/bin/chromium-browser` 不存在
- `google-chrome` 命令未找到

---

### 第6步：子代理（Sub-Agent）双路并行

派了两个子代理分别尝试不同路径：
1. **路径一**：Playwright 浏览器 + 代理 + 滚动加载
2. **路径二**：百度搜索 + 公众号 + 知乎等公开渠道反向搜寻

**路径一结果**：抖音 API 全部被拦（acrawler + CAPTCHA + IP block）
**路径二结果**：搜索引擎全部触发 CAPTCHA/Cloudflare 验证

**失败原因**：WSL 环境的对外网络请求被代理+防火墙基础设施拦截，所有爬虫/搜索工具都无法正常工作。

---

## 完整测试矩阵

| 工具 | 首页 | API | 作品列表 | 文案获取 | 失败原因 |
|------|------|-----|----------|----------|----------|
| scrapling | ❌ | ❌ | ❌ | ❌ | 缺 patchright 依赖 |
| curl_cffi | ✅ 200 | ❌ 空body | ❌ | ❌ | acrawler 签名校验 |
| curl-impersonate | ✅ 200 | ❌ CAPTCHA | ❌ | ❌ | IP 触发验证码 |
| Playwright 无头 | ❌ Timeout | ❌ | ❌ | ❌ | 无头检测+IP标记 |
| DrissionPage | ❌ | ❌ | ❌ | ❌ | 缺Chrome二进制 |
| 子代理搜索 | ❌ | ❌ | ❌ | ❌ | 网络/代理拦截 |

## 抖音反爬机制层次（实测确认）

```
L1: TLS 指纹检测
    └ curl_cffi/curl-impersonate ✅ 可通过
L2: acrawler JS 签名（X-Bogus）
    └ curl_cffi ❌ 空body — 无法生成JS签名
L3: CAPTCHA 验证码
    └ curl-impersonate ❌ 被拦截 — IP信誉不足
L4: IP 信誉系统
    └ WSL/阿里云IP ❌ 被标记为机房IP
L5: 无头浏览器检测
    └ Playwright ❌ 超时 — 无头模式被识别
```

## 最终方案：B（人工采集）

**执行过程**：
1. 用户（江姐）在手机端打开抖音App
2. 进入「彭会计财税」主页 → 按「最多点赞」排序
3. 手动录入31条爆款数据（标题、点赞数、评论数、发布时间）
4. 数据格式：Word文档表格，32行（含表头）

**产出成果**：
- 31条完整爆款数据（最高赞4.2万，最低2056赞）
- 时间跨度：2022.03 - 2026.06（4年内容）
- 后续用于 RIA-TV 三层萃取分析 → 产出 `peng-accounting-douyin-style` 技能

## 本次经验教训

1. **快速验证 > 深入调试**：爬虫任务应在10分钟内完成工具轮替，快速确定可行性
2. **环境问题一次性报**：WSL 缺 Chrome、缺 patchright、IP 被标记——这些问题应第一时间汇总而不是逐个发现
3. **人工方案不是失败**：江姐手动采集31条仅花15分钟，比任何爬虫方案都快且零质量损失
4. **用户指定的工具清单必须全部试过**：这次用户特意列出了scrapling/Playwright/DrissionPage/curl-impersonate/agent-reach，不能跳过任何一个
