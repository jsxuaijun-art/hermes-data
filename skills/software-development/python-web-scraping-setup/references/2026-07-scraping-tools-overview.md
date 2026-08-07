# 爬虫工具全景对照表（2026年7月版）

基于2026年7月20日搜索和实测整理。

## 工具速查

| 工具 | GitHub | Stars | 最新版本 | 开发者 | 协议 |
|------|--------|-------|---------|--------|------|
| Scrapling | D4Vinci/Scrapling | ~23K | v0.3.x (2026) | D4Vinci | 未明确 |
| DrissionPage | g1879/DrissionPage | ~5.4K (Gitee) | v4.1.1.4 / v5.0.0b0 | g1879 | 个人免费/商业需授权 |
| Playwright | microsoft/playwright-python | ~14.8K | v1.61.0 (2026-06-29) | Microsoft | Apache-2.0 |
| curl_cffi | yifeikong/curl_cffi | — | — | yifeikong | MIT |
| curl-impersonate | lwthiker/curl-impersonate | — | v0.6.1 (2025) | lwthiker | MIT |

## 核心定位

- **Scrapling**: 自适应智能爬虫。解析器从网站变化中学习，元素自动重新定位。StealthyFetcher 基于 patchright (Playwright fork) 开箱绕过反爬。内置爬虫框架(并发/暂停/代理轮换)。需 `pip install scrapling patchright`。
- **DrissionPage**: 国产全自研双模式。浏览器模式(控制Chromium) + 请求模式(HTTP直发)，不依赖WebDriver。极简语法，跨iframe操作。适合日常快速抓取。
- **Playwright**: 微软亲儿子，三浏览器(Chromium+Firefox+WebKit)。同步+异步双API。内置反检测(inject init script)，Trace Viewer，v1.61新增WebAuthn和Web Storage API。WSL需装12个系统依赖库。
- **curl_cffi**: Python版TLS指纹伪装(JA3/JA4)。pip安装即用，API类requests。过Cloudflare第一层，但过不了JS签名(如抖音acrawler返回200空body)。
- **curl-impersonate**: 系统级全栈伪装(修改libcurl源码)。TLS+HTTP/2完全模拟浏览器。GitHub Release从中国下载困难。最终底牌但仍可能触发CAPTCHA。

## 反爬实战阶梯 (由简到繁)

```
① curl_cffi          → TLS指纹检测 (过Cloudflare一层)
② curl-impersonate   → 系统级伪装 (但触CAPTCHA)
③ Playwright         → 浏览器自动化 + JS反检测注入
④ DrissionPage       → 指定已登录Chrome实例
⑤ 方案B(人工采集)    → 数据质量第一
```

## 选型三句话

1. 能直接访问的 -> DrissionPage
2. 要渲染JS的 -> Playwright
3. 都搞不定的 -> 方案B(人工采集，数据质量第一)
