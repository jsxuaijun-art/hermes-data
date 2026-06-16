# Hermes 爬虫工具集

Hermes Agent 的爬虫/自动化工具环境，装在 **Hermes 主 Python 环境**里（`~/.venv-hermes/`），技能和脚本可直接 `import` 调用。

## 包含工具

| 工具 | 用途 | 安装方式 |
|------|------|----------|
| **DrissionPage** | 多线程/多标签浏览器自动化（类似 Selenium 但更快） | pip |
| **scrapling** | 自适应智能爬虫（55K+ Stars） | pip |
| **curl_cffi** | TLS 指纹模拟（curl-impersonate Python 版） | pip |
| **Playwright** | 微软浏览器自动化（多浏览器支持） | pip |
| **curl-impersonate** | 系统级 curl 指纹模拟二进制 | 系统安装 |

## 环境要求

- Python 3.10+
- Linux / WSL
- Git（用于同步）

## 新电脑部署（三步走）

```bash
git pull                          # 1. 拉取最新安装脚本
cd hermes-data/scrapling
bash setup.sh                     # 2. 一键安装所有工具
```

`setup.sh` 自动完成：
1. 检测 Hermes 主环境 `~/.venv-hermes/`（未找到则用系统 Python）
2. 安装 DrissionPage + scrapling + curl_cffi + Playwright
3. 安装 Playwright Chromium 浏览器
4. 安装 curl-impersonate 系统二进制
5. 验证所有工具就绪

## 测试

```bash
cd hermes-data/scrapling
source ~/.venv-hermes/bin/activate  # 激活 Hermes 环境
python scripts/test-scrapling.py    # 运行验证
```

## 目录结构

```
hermes-data/
├── scrapling/           ← 本目录（git 同步）
│   ├── setup.sh         ← 新电脑一键安装脚本
│   ├── activate.sh      ← 快速激活 Hermes 环境
│   ├── README.md        ← 本文件
│   └── scripts/         ← 爬虫脚本（所有机器共享）
│       ├── test-scrapling.py    ← 环境验证
│       └── ...                   ← 后续添加的爬虫任务
```

## 多机共享方案

| 项目 | 同步方式 | 说明 |
|------|---------|------|
| 爬虫脚本 (scripts/) | ✅ GitHub (hermes-data) | 写一次，所有机器 `git pull` |
| 安装脚本 (setup.sh) | ✅ GitHub (hermes-data) | 一次配置，多机复用 |
| Hermes 技能包装 | ✅ GitHub (hermes-data skills/) | 封装成 Hermes 命令 |
| Python 包 | ❌ 每台 `bash setup.sh` | 平台依赖，不能 git 同步 |
| Chromium 浏览器 | ❌ setup.sh 自动装 | ~170MB |
| curl-impersonate 二进制 | ❌ setup.sh 自动装 | TLS 指纹模拟 |

## 税务应用场景（待开发）

- 财政部/税务总局公告监控
- 苏州工业园区政策更新追踪
- 同行服务内容与定价采集
- 客户企业工商信息批量查询