# 进阶爬虫工具跨平台安装状态（2026-06-16）

## 环境信息

| 项目 | 详情 |
|------|------|
| **WSL 本地** | Ubuntu 22.04, Python 3.12, Hermes Agent |
| **阿里云** | 47.103.27.171, root/yx168168/*- |
| **SSH 命令** | `sshpass -p 'yx168168/*-' ssh root@47.103.27.171 "command"` |
| **检查时间** | 2026-06-16 21:56 |

## 安装状态

| 工具 | WSL 本地 | 阿里云 | 安装方式 |
|------|----------|--------|----------|
| **Playwright** | ✅ 1.60.0 + Chromium (1223) | ❌ 未安装 | `pip install playwright` + `playwright install chromium` |
| **DrissionPage** | ❌ 未安装 | ❌ 未安装 | `pip install DrissionPage` |
| **scrapling** | ❌ 未安装 | ❌ 未安装 | `pip install scrapling` |
| **curl-impersonate** | ❌ 未安装 | ❌ 未安装 | 系统级编译安装（git clone → configure → make） |
| **curl** | ✅ /usr/bin/curl | ✅ 7.81.0 | 系统自带 |

## WSL Playwright 细节

- Python 包：playwright 1.60.0
- Chromium 浏览器路径：`/home/dmin/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome`
- Launch 验证通过（headless 模式抓取百度页面成功）

## 阿里云基础信息（2026-06-16）

Python 环境中没有任何爬虫相关 pip 包（Playwright/DrissionPage/scrapling 均未安装）。
仅系统 curl 可用（curl 7.81.0）。

## 按需安装建议

如果需要上反爬对抗项目，推荐安装顺序：
1. DrissionPage（pip 直装，无系统依赖，无二进制）
2. scrapling（pip 直装，无系统依赖，无二进制）
3. curl-impersonate（编译较耗时，仅在遇到 Cloudflare WAF 时需要）
4. Playwright（已有 Chromium，阿里云需额外装系统依赖）