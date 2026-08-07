# Hermes v0.15.1 → v0.20.0 升级实录（2026.8.7，WSL2 + Windows Clash 代理）

## 目标

用户要求"升级到 v0.20"。官方 tag 为日期式（最新 v2026.8.3），其 pyproject.toml 内部版本号恰为 0.20.0 —— 即目标。

## 环境事实（本次实测）

- 运行目录：`~/hermes-agent`（**混合目录**：git 数据同步仓库 + hermes 源码 + 用户数据混在一起）
- git 仓库 remote 是 `git@github.com:jsxuaijun-art/hermes-data.git`（数据同步仓库，不是官方源）
- .gitignore 用白名单模式：`*` 排除一切，只 `!` 放行 SOUL.md、memories/、skills/、config.yaml 等 → **agent/、tools/、cli.py 等源码不在 git 里，可直接覆盖**
- venv 在 `~/hermes-agent/venv/`（Python 3.12.3）
- launcher 是 `~/hermes-agent/hermes`（shebang `#!/usr/bin/env python3`，**指向系统 python3 而非 venv** —— 升级后必须改）
- Windows Clash 只绑 127.0.0.1:7890（Allow LAN 关）→ WSL 内 172.x:7890 和 127.0.0.1:7890 都连不上；**唯一通路是 curl.exe（Windows 原生）走 127.0.0.1:7890**

## 完整步骤（验证可行）

### 1. 确认目标 tag + 内部版本

```bash
curl.exe -s --proxy "http://127.0.0.1:7890" 'https://api.github.com/repos/NousResearch/hermes-agent/tags?per_page=30'
curl.exe -s --proxy "http://127.0.0.1:7890" 'https://raw.githubusercontent.com/NousResearch/hermes-agent/v2026.8.3/pyproject.toml' | grep -m1 '^version'
# → version = "0.20.0" ✓ 确认目标
```

### 2. 下载官方 tarball（原装，走代理）

```bash
mkdir -p /mnt/e/hermes-upgrade && cd /mnt/e/hermes-upgrade
curl.exe -L -s --proxy "http://127.0.0.1:7890" -o hermes-v2026.8.3.tar.gz \
  'https://github.com/NousResearch/hermes-agent/archive/refs/tags/v2026.8.3.tar.gz'
ls -lh hermes-v2026.8.3.tar.gz   # 61MB（v0.20 比老版大很多）
```

### 3. 解压到 /tmp（Linux 文件系统）

```bash
cp /mnt/e/hermes-upgrade/hermes-v2026.8.3.tar.gz /tmp/
cd /tmp && tar xzf hermes-v2026.8.3.tar.gz    # 目录名 hermes-agent-2026.8.3
```

### 4. rsync 部署（排除用户数据，源码覆盖）

```bash
cd ~/hermes-agent
rsync -a --delete \
  --exclude='.git/' --exclude='venv/' --exclude='nul' \
  --exclude='SOUL.md' --exclude='SOUL_Pro.md' --exclude='SOUL_Edu.md' \
  --exclude='config.yaml' --exclude='memories/' --exclude='obsidian-vault/' \
  --exclude='claw-memory/' --exclude='outputs/' --exclude='scrapling/' \
  --exclude='sync-pull-wsl.sh' --exclude='sync-push-wsl.sh' \
  --exclude='_pull_gh.py' --exclude='_test_gh.py' --exclude='check_remote.py' \
  --exclude='test-output.md' --exclude='爬虫工具全景报告.txt' \
  --exclude='obsidian-vault-obsidian-vault-guide.md' \
  --exclude='README.md' --exclude='skills/' --exclude='plugins/' \
  --exclude='cron/README.md' --exclude='cron/daily_tax_intelligence.md' \
  --exclude='cron/weekly_tax_deep_dive.md' --exclude='cron/unified_tax_loader.py' \
  --exclude='cron/scripts/' \
  /tmp/hermes-agent-2026.8.3/ ~/hermes-agent/
# 注意：cron/ 是混合目录（源码 jobs.py/scheduler.py + 用户 md/脚本），用户文件必须排除
# 官方 cron/ 无 README.md，用户的 cron/README.md 是财税任务说明，保留

# plugins/ 单独合并（官方新插件 + 用户已有插件）：--ignore-existing 不覆盖用户版本
rsync -a --ignore-existing /tmp/hermes-agent-2026.8.3/plugins/ ~/hermes-agent/plugins/
# → 新增 image_gen、kanban、cron_providers 等官方插件，用户 example-dashboard 等保留
```

### 5. 安装依赖（必须 unset 代理环境变量）

```bash
cd ~/hermes-agent
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY   # 环境里残留 172.25.208.1:7890，不 unset 必超时
venv/bin/pip install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple --quiet
```

### 6. 修 launcher shebang（关键坑）

```bash
# 症状：./hermes --version 能跑（只 import argparse），但 ./hermes chat 报
#   ModuleNotFoundError: No module named 'httpx'
# 原因：launcher shebang 是 #!/usr/bin/env python3 → 用系统 python3，依赖装在 venv
# 修复：把 ~/hermes-agent/hermes 第一行改成
#!/home/administrator/hermes-agent/venv/bin/python
```

### 7. 验证

```bash
cd ~/hermes-agent && ./hermes --version
# → Hermes Agent v0.20.0 (2026.8.3) | Python: 3.12.3 | OpenAI SDK: 2.24.0
```

## 遗留事项

- config 版本 23 → 33：可跑 `hermes config migrate`（WSL 侧已完成）
- 依赖警告 pyopenssl 26.3.0 vs cryptography 48.0.1（非关键，一般不影响）
- ~~Windows 侧旧安装待升级~~ → 已于同日完成，见 `references/hermes-windows-side-upgrade.md`（v0.20.0，Python 3.11.15，venv 重建，config migrate 23→33）

## 教训

1. **诊断顺序**：先 `netstat -ano | findstr :7890` 看代理绑的是 127.0.0.1 还是 0.0.0.0 —— 只绑 127.0.0.1 就直接放弃 WSL 内代理方案，改用 curl.exe
2. **pip 装依赖前先 unset 代理**：本环境 http_proxy/https_proxy 残留指向不可达的 172.25.208.1:7890，任何 pip 都会 ConnectTimeout 死循环，unset 后走清华镜像秒装
3. **混合目录 rsync 排除清单是升级核心风险点**：漏掉 cron/ 用户文件、plugins/ 用户插件、obsidian-vault 等会覆盖用户数据；git ls-files + git check-ignore 可快速判断哪些目录是 git 跟踪的用户数据
4. **launcher shebang 必须验证**：--version 正常 ≠ chat 正常；--version 只 import argparse 路径，chat 才 import httpx 等真依赖
