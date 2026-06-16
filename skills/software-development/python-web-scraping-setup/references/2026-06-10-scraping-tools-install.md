# 爬虫三件套安装记录（2026-06-10）

## 环境信息
- **环境**：WSL2 Ubuntu 22.04（Hermes Agent 运行环境）
- **Python**：3.12（.venv-hermes 虚拟环境）
- **三件套**：Playwright 1.60.0 + Scrapy 2.16.0 + Requests 2.33.1 + BeautifulSoup 4.14.3

## 安装结果

| 工具 | 状态 | 版本 | 备注 |
|------|------|------|------|
| Requests+BeautifulSoup | ✅ 已有 | 2.33.1 / 4.14.3 | 预装，直接可用 |
| Scrapy | ✅ 新装 | 2.16.0 | pip install scrapy 一路绿灯 |
| Playwright | ✅ 新装 | 1.60.0 | Python包 + chromium浏览器二进制 |

## 遇到的坑 & 修复

### 坑1：Playwright 浏览器二进制下载超时
- **症状**：`playwright install chromium` 下载到 80% 超时（180s 限制）
- **原因**：Chromium headless shell（113MB）下载慢
- **修复**：重试一次，设 timeout=300s 即可

### 坑2：libasound.so.2 缺失（WSL 特有）
- **症状**：启动 Playwright 时报错
  ```
  error while loading shared libraries: libasound.so.2: cannot open shared object file
  ```
- **原因**：WSL Ubuntu 最小化安装，缺少 alsa 音频库
- **修复**：
  ```bash
  sudo apt-get install -y libasound2
  ```
- **同时补装（防止后续缺其他库）**：
  ```bash
  sudo apt-get install -y libgtk-3-0 libgbm1 libasound2 libx11-xcb1 libnss3 libxcomposite1 libxcursor1 libxdamage1 libxi6 libxrandr2 libxss1 libxtst6
  ```

## 验证命令

```bash
# Requests + BS4
python3 -c "
import requests
from bs4 import BeautifulSoup
r = requests.get('https://www.baidu.com', timeout=5)
soup = BeautifulSoup(r.text, 'lxml')
print('Title:', soup.title.text.strip())
"

# Scrapy
scrapy version

# Playwright
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://www.baidu.com')
    print('Page title:', page.title())
    browser.close()
"
```

## 待办：阿里云服务器
- ⏳ 用户反馈阿里云上三件套中有一个装失败（具体哪个待确认）
- 暂无可直接 SSH 的信息，需手动检查或远程协助