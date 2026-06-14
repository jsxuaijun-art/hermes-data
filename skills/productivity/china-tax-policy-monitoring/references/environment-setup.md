# Scrapling 环境搭建与多机共享方案

## 本机安装（笔记本/办公室/家里 WSL）

```bash
python3 -m venv ~/scrapling-env
source ~/scrapling-env/bin/activate
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple scrapling[all]
playwright install chromium
```

## 阿里云 / 无头服务器安装

### 手动安装

```bash
python3 -m venv ~/scrapling-env
source ~/scrapling-env/bin/activate
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple scrapling curl_cffi
# 注意：阿里云连国外CDN极慢，playwright install chromium 可能超时
# 如果只需基础 Fetcher（HTTP请求），可以不装 Playwright
# 如果需要 StealthyFetcher（浏览器自动化），则需：
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple playwright
~/scrapling-env/bin/playwright install chromium
```

### 通过 SSH 自动部署（paramiko 模式）

从本机使用 Python paramiko 库远程部署到阿里云服务器的完整流程：

1. 本机安装 paramiko：`pip install paramiko`
2. 编写部署脚本，使用 SSHClient 连接阿里云
3. 远程执行命令：创建 venv、安装包、拉取仓库
4. 通过 SFTP 写入文件（比 shell heredoc 更可靠）
5. 验证运行

```python
import paramiko

host = "阿里云公网IP"
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=22, username="root", password="xxx")

# 执行远程命令
stdin, stdout, stderr = client.exec_command("命令", timeout=30)
exit_code = stdout.channel.recv_exit_status()
out = stdout.read().decode()

# 通过 SFTP 写入文件
sftp = client.open_sftp()
with sftp.open('/远程/路径/文件.py', 'wb') as f:
    f.write(script_content.encode('utf-8'))
sftp.chmod('/远程/路径/文件.py', 0o755)
sftp.close()

client.close()
```

> ⚠️ **阿里云部署坑：**
> - `scrapling[all]` 在阿里云下载极慢（400+个包），建议只装 `scrapling` + `curl_cffi`
> - Playwright Chromium 下载 ~170MB 从国外 CDN，可能超时。如遇超时，在本机下载后 scp 到阿里云
> - 基础 Fetcher（HTTP请求）不需要 Playwright，优先用这个模式
> - 使用 `stdout.channel.recv_exit_status()` 获取远程命令退出码，不要依赖 stdout 内容判空

## 共享目录（hermes-data/scrapling/）

```
hermes-data/scrapling/
├── setup.sh                  ← 新电脑一键安装
├── activate.sh               ← 快速激活环境
├── README.md                 ← 说明文档
└── scripts/
    ├── test-scrapling.py     ← 环境验证
    └── tax-policy-monitor.py ← 税务政策监控
```

## .gitignore 白名单

hermes-data 的 `.gitignore` 使用白名单模式，新增目录需添加：
```
!scrapling/
!scrapling/**
```

## Python 依赖陷阱

- **不要只装 `scrapling`**（本体），否则运行时报 `ModuleNotFoundError`
- **必须装 `scrapling[all]`**，会连带安装 `curl_cffi`, `browserforge`, `patchright` 等
- `scrapling[all]` 会重新安装 `playwright` 和 `patchright`（降版本），因此需要重新执行 `playwright install chromium`
- 最终版本链：scrapling 0.4.8 → playwright 1.59.0 + patchright 1.59.1 → Chromium v1217
