# 阿里云爬虫工具部署记录（2026-06-16）

## 环境关键发现

| 项目 | 实际值 | 误以为（旧SKILL.md） |
|------|--------|---------------------|
| Hermes venv 路径 | `/usr/local/lib/hermes-agent/venv/` | `$HOME/.venv-hermes` / 系统 Python |
| Python 版本 | 3.11 | 3.10 |
| Hermes 启动方式 | `/usr/local/lib/hermes-agent/venv/bin/python -m hermes_cli.main gateway run` | — |
| 系统包管理器 | pip3 (system) + venv pip | — |
| SSH 登录 | `sshpass -p 'yx168168/*-' ssh root@47.103.27.171` | — |

## 安装过程

### 步骤

1. 拉取 latest 代码 → 发现 git 分支发散
2. `git fetch origin main && git reset --hard origin/main` 强制同步
3. 首次 run setup.sh → 装到系统 Python，验证失败
4. 手动装到 Hermes venv：
   ```bash
   HERMES_VENV=/usr/local/lib/hermes-agent/venv
   HERMES_PIP=$HERMES_VENV/bin/pip
   $HERMES_PIP install DrissionPage scrapling curl_cffi playwright
   ```

### 验证结果

```python
import DrissionPage  # OK v4.1.1.4
import scrapling    # OK v0.4.9
import curl_cffi    # OK v0.15.0
import playwright   # OK (sync_api 导入成功)
from playwright.sync_api import sync_playwright  # OK
```

Chromium 浏览器：1217 + 1223 双版本（之前已装）
curl-impersonate：系统二进制已装（v8.1.1）

## 坑记录

### 坑1：setup.sh 找不到 Hermes venv
- **症状**：输出"未检测到 Hermes 虚拟环境，使用系统 Python"
- **原因**：脚本只检查了 `$HOME/.venv-hermes`，阿里云的路径不同
- **修复**：手动指定 venv 路径安装
- **TODO**：修改 setup.sh 增加 `/usr/local/lib/hermes-agent/venv/` 检测

### 坑2：git 分支发散导致 pull 失败
- **症状**：`fatal: Need to specify how to reconcile divergent branches`
- **原因**：阿里云/opt/hermes-sync 有本地 commit 与 origin main 不同步
- **修复**：`git fetch origin main && git reset --hard origin/main`

### 坑3：importlib.metadata.version() 失败
- **症状**：验证脚本输出 ❌ 但实际上包已装好
- **原因**：venv 内有 `~etuptools` 损坏的 dist-info 目录
- **修复**：用 `import pkg; pkg.__version__` 替代 `importlib.metadata.version(pkg)`

## 阿里云 Git 仓库布局

| 路径 | 用途 | 认证方式 |
|------|------|---------|
| `/root/hermes-data/` | Git repo（ssh） | SSH key (坏了) |
| `/opt/hermes-sync/` | Git repo（https） | Token `[REDACTED]` ✅ |
| `/opt/hermes-data/` | Git repo（https 只读） | 无 token，只读 |

目前只有 `/opt/hermes-sync/` 能正常 push/pull。  
如果 `/root/hermes-data/` 的 SSH key 坏了，建议把 `/opt/hermes-sync/` 设为同步主目录。