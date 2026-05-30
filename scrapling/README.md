# Scrapling 爬虫工具集

基于 [Scrapling](https://github.com/D4Vinci/Scrapling)（55K+ Stars）的财税行业爬虫脚本集合。

## 环境要求

- Python 3.10+
- Linux / WSL

## 快速安装（新电脑）

```bash
cd hermes-data/scrapling
bash setup.sh
```

自动完成：创建虚拟环境 → 安装 Scrapling + Playwright + Chromium

## 激活环境

```bash
source ~/scrapling-env/bin/activate
```

## 目录结构

```
scrapling/
├── setup.sh        ← 新电脑一键安装脚本（共享到 GitHub）
├── activate.sh     ← 快速激活环境
├── README.md       ← 本文件
└── scripts/        ← 爬虫脚本（所有机器共享）
    ├── test-scrapling.py    ← 环境验证
    └── ...                   ← 后续添加的爬虫任务
```

## 多机共享方案

| 项目 | 同步方式 | 说明 |
|------|---------|------|
| 爬虫脚本 (scripts/) | ✅ GitHub (hermes-data) | 写一次，所有机器 git pull |
| 爬虫 Cron 任务 | ✅ GitHub (hermes-data config) | Hermes 配置同步 |
| Hermes 技能包装 | ✅ GitHub (hermes-data skills/) | 可封装成 Hermes 命令 |
| Scrapling Python 包 | ❌ 每台机器单独 pip 装 | 二进制包，平台依赖 |
| Chromium 浏览器 | ❌ 每台机器单独安装 | ~170MB，平台依赖 |

**新电脑部署三步走：**

```bash
git pull                                      # 1. 拉取脚本
bash hermes-data/scrapling/setup.sh           # 2. 装环境
source ~/scrapling-env/bin/activate           # 3. 激活
```

## 税务应用场景（待开发）

- 财政部/税务总局公告监控
- 苏州工业园区政策更新追踪
- 同行服务内容与定价采集
- 客户企业工商信息批量查询
