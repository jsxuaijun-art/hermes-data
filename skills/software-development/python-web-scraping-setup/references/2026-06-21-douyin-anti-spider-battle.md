# 抖音反爬实战记录（2026-06-21）

## 目标信息

| 项目 | 内容 |
|------|------|
| **账号** | 彭会计财税（南京明好税务师事务所有限公司） |
| **抖音号** | PengkuaijiNJ |
| **用户ID** | MS4wLjABAAAAPhOHzDUBqaRu942RRQ8-2yS4g0n-IxbgfYh-7y_LNxk |
| **主页** | https://www.douyin.com/user/MS4wLjABAAAAPhOHzDUBqaRu942RRQ8-2yS4g0n-IxbgfYh-7y_LNxk |
| **粉丝** | 138.8K |
| **获赞** | 542.8K |
| **作品** | 687条 |
| **关注** | 105 |
| **IP属地** | 江苏 |
| **认证** | 南京明好税务师事务所有限公司（注会+注税双证） |

## 爬虫工具轮替结果

### 工具1: scrapling（自适应智能爬虫）

```python
from scrapling import Fetcher, StealthyFetcher
f = Fetcher()
resp = f.get(url)
```

**失败原因**: `patchright` 依赖缺失
```
ModuleNotFoundError: No module named 'patchright'
```
**修复方法**: `pip install patchright`

---

### 工具2: curl_cffi（Python TLS 指纹模拟）

```python
from curl_cffi import requests
s = requests.Session()
s.get('https://www.douyin.com/', impersonate='chrome120', timeout=15)
r = s.get('https://www.douyin.com/aweme/v1/web/aweme/post/', params={...}, impersonate='chrome120')
```

**结果**: 首页 200 ✅, API 200 空 body ❌
```
Home status: 200, cookies: {...}
API status: 200
Response text [0 chars]:   # 空body!
```

**原因**: 抖音 API 需要 acrawler 签名（`X-Bogus` 参数），纯 HTTP 请求无法生成此签名。

---

### 工具3: curl-impersonate（系统级二进制）

```bash
curl-impersonate-chrome ... 'https://www.douyin.com/user/...'
```

**结果**: 触发验证码中间页 ❌
```html
<title>验证码中间页</title>
<script src="https://lf-cdn-tos.bytescm.com/obj/static/sec_sdk_build/3.5.2/captcha/index.js">
```

---

### 工具4: Playwright（浏览器自动化 + 反检测注入）

```python
context = browser.new_context(
    viewport={'width': 1920, 'height': 1080},
    user_agent='Mozilla/5.0 ... Chrome/120.0.0.0 ...',
    locale='zh-CN',
    timezone_id='Asia/Shanghai',
)
page.add_init_script("""...""")  # 抹掉 webdriver 痕迹
```

**结果**: 超时 ❌（无头模式被抖音拦截，IP 环境已被标记）
```
TimeoutError: Page.goto: Timeout 30000ms exceeded.
```

---

### 工具5: DrissionPage（指定已安装 Chrome）

```python
from DrissionPage import ChromiumPage
page = ChromiumPage()
```

**结果**: 找不到 Chrome 可执行文件 ❌
```
FileNotFoundError: 未找到浏览器。
```

**原因**: WSL 环境没有安装 Chrome 浏览器。

---

## 抖音反爬机制归纳

| 层次 | 检测手段 | 绕过难度 |
|------|----------|----------|
| L1 | TLS 指纹 | ⭐ 低（curl_cffi/curl-impersonate 可过） |
| L2 | acrawler JS 签名（X-Bogus） | ⭐⭐⭐ 高（需执行 JS 生成签名） |
| L3 | CAPTCHA 验证码 | ⭐⭐⭐⭐⭐ 极高（需商业化验证码解决方案） |
| L4 | IP 信誉系统 | ⭐⭐⭐⭐（机房 IP 被标，需住宅代理） |
| L5 | 无头浏览器检测 | ⭐⭐⭐（可用 stealth 插件绕过，但抖音检测力强） |

## 可行方案（按推荐排序）

### 方案A: 实机登录态 + acrawler SDK
- 获取真实手机/PC 登录态的 Cookie
- 配合 `https://github.com/BSTester/TikTok-Anti-Law` 或 `https://github.com/RedOps-Lab/TikTok-Signature` 生成 acrawler 签名
- **优势**: 能拿到完整数据
- **劣势**: 签名 SDK 维护成本高

### 方案B: 抖音开放平台 OAuth API
- 申请抖音开发者账号 + 企业资质
- 通过 OAuth 获取 access_token
- 调用官方 `/aweme/v1/web/aweme/post/` 等接口
- **优势**: 合法合规，稳定
- **劣势**: 需要企业资质，有一定门槛

### 方案C: 第三方数据平台付费
- 蝉妈妈、新抖、飞瓜数据、考古加
- 很多平台有账号维度公开分析功能
- **优势**: 即开即用，无技术门槛
- **劣势**: 需付费

### 方案D: 人工采集 + 手动录入
- 手机端浏览目标账号 → 按「最多点赞」排序
- 采集字段：标题、点赞数、评论数、时长、发布时间
- **优势**: 零技术门槛，保证数据质量
- **劣势**: 需要人力，20-30条约15分钟

## 本次实战总结

> **结论**: Python 自动化爬虫（无登录态纯 HTTP）在当前抖音反爬体系下基本不可行。WSL/阿里云等云环境 IP 已被标记为高风险，进一步增加了难度。

> **最佳实践**: 对于需要分析抖音账号的财税行业竞品调研，推荐「人工采集（方案D）」作为日常方案，「第三方平台（方案C）」作为深度方案。
