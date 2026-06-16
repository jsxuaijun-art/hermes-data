---
name: python-web-scraping-setup
description: Cross-platform web scraping environment setup — DrissionPage, scrapling, curl_cffi, Playwright, curl-impersonate. Covers WSL (Hermes venv) + Aliyun (system Python) dual-env deployment, shared scripts via GitHub, and environment verification.
---

# Python 爬虫环境设置

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
| **scrapling** | 🔧 拓展 | 自适应智能爬虫（55K+ Stars） | pip 直装 |
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