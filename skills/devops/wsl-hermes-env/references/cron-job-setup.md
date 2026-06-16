# 三端同步 — 完整设置 + 脚本 + 故障排除

数据流向：**阿里云 ⇄ GitHub ⇄ WSL**

## 阿里云同步脚本

### 推送脚本（/root/.hermes/sync-push-cloud.sh）

```bash
#!/bin/bash
# ============================================
# 阿里云 → GitHub 推送（每30分钟 + 凌晨3点）
# 日志：/var/log/hermes-sync.log
# ============================================
LOG="/var/log/hermes-sync.log"
SYNC_DIR="/opt/hermes-sync"
HERMES_DIR="/root/.hermes"

echo "[$(date '+%Y-%m-%d %H:%M')] === PUSH START ===" >> "$LOG"

# 复制最新数据
cp -f "$HERMES_DIR/SOUL.md" "$SYNC_DIR/SOUL.md" 2>/dev/null
cp -f "$HERMES_DIR/SOUL_Pro.md" "$SYNC_DIR/SOUL_Pro.md" 2>/dev/null
cp -f "$HERMES_DIR/SOUL_Edu.md" "$SYNC_DIR/SOUL_Edu.md" 2>/dev/null
cp -f "$HERMES_DIR/config.yaml" "$SYNC_DIR/config.yaml" 2>/dev/null
rsync -a --delete "$HERMES_DIR/memories/" "$SYNC_DIR/memories/" 2>/dev/null
rsync -a --delete "$HERMES_DIR/skills/" "$SYNC_DIR/skills/" 2>/dev/null

# 提交并推送
cd "$SYNC_DIR"
git add -A
if git diff --cached --quiet; then
    echo "[$(date '+%Y-%m-%d %H:%M')] 无变更，跳过" >> "$LOG"
else
    git commit -m "sync 阿里云 $(date '+%a %Y/%m/%d %H:%M')" >> "$LOG" 2>&1
    git push origin main >> "$LOG" 2>&1 && echo "PUSH OK" >> "$LOG" || echo "PUSH FAIL" >> "$LOG"
fi

echo "[$(date '+%Y-%m-%d %H:%M')] === PUSH END ===" >> "$LOG"
```

### 拉取脚本（/root/.hermes/sync-pull-cloud.sh）

```bash
#!/bin/bash
# ============================================
# GitHub → 阿里云 拉取（凌晨4点）
# ============================================
SYNC_DIR="/opt/hermes-sync"
HERMES_DIR="/root/.hermes"

echo "[$(date)] === PULL START ==="
cd "$SYNC_DIR"
git pull origin main 2>&1

# 同步到 ~/.hermes/
cp -f "$SYNC_DIR/SOUL.md" "$HERMES_DIR/SOUL.md" 2>/dev/null
cp -f "$SYNC_DIR/SOUL_Pro.md" "$HERMES_DIR/SOUL_Pro.md" 2>/dev/null
cp -f "$SYNC_DIR/SOUL_Edu.md" "$HERMES_DIR/SOUL_Edu.md" 2>/dev/null
cp -f "$SYNC_DIR/config.yaml" "$HERMES_DIR/config.yaml" 2>/dev/null
rsync -a --delete "$SYNC_DIR/memories/" "$HERMES_DIR/memories/" 2>/dev/null
rsync -a --delete "$SYNC_DIR/skills/" "$HERMES_DIR/skills/" 2>/dev/null
echo "[$(date)] === PULL END ==="
```

### 阿里云 crontab

```bash
*/30 * * * * bash /root/.hermes/sync-push-cloud.sh    # 每30分推送
0 3 * * * bash /root/.hermes/sync-push-cloud.sh       # 凌晨3点冗余推送
0 4 * * * bash /root/.hermes/sync-pull-cloud.sh       # 凌晨4点拉取更新
```

## WSL 手动脚本

### 推送脚本（~/.hermes/sync-push-wsl.sh）

```bash
#!/bin/bash
# ============================================
# WSL → GitHub 手动推送（下班前）
# ============================================
set -e
SYNC_DIR="/mnt/c/Users/Admin/hermes-sync"
HERMES_DIR="/home/dmin/.hermes"

echo ">>> 复制 ~/.hermes/ 数据..."
cp -f "$HERMES_DIR/SOUL.md" "$SYNC_DIR/SOUL.md" 2>/dev/null || true
cp -f "$HERMES_DIR/config.yaml" "$SYNC_DIR/config.yaml" 2>/dev/null || true
rsync -a --delete "$HERMES_DIR/memories/" "$SYNC_DIR/memories/" 2>/dev/null || true
rsync -a --delete "$HERMES_DIR/skills/" "$SYNC_DIR/skills/" 2>/dev/null || true

cd "$SYNC_DIR"
git add -A
if git diff --cached --quiet; then
    echo "无变更"
else
    git commit -m "sync WSL端 $(date '+%a %Y/%m/%d %H:%M')"
    git push origin main
fi
```

### 拉取脚本（~/.hermes/sync-pull-wsl.sh）

```bash
#!/bin/bash
# ============================================
# GitHub → WSL 手动拉取（上班时）
# ============================================
set -e
SYNC_DIR="/mnt/c/Users/Admin/hermes-sync"
HERMES_DIR="/home/dmin/.hermes"

cd "$SYNC_DIR"
if ! git pull origin main; then
    echo "⚠️ git pull 失败（尝试 Windows Git Bash）"
    echo "  cd D:\\360MoveData\\Users\\Admin\\Desktop\\hermes-sync && git pull"
    exit 1
fi

cp -f "$SYNC_DIR/SOUL.md" "$HERMES_DIR/SOUL.md" 2>/dev/null || true
cp -f "$SYNC_DIR/config.yaml" "$HERMES_DIR/config.yaml" 2>/dev/null || true
rsync -a --delete "$SYNC_DIR/memories/" "$HERMES_DIR/memories/" 2>/dev/null || true
rsync -a --delete "$SYNC_DIR/skills/" "$HERMES_DIR/skills/" 2>/dev/null || true
echo "✅ 同步完成"
```

## 诊断与故障排除

### WSL git pull 超时（git timeout 但 curl 正常）

**现象**：`git pull origin main` 或 `git fetch origin main` 挂在等待状态，超时退出。同时 `curl` 到 github.com 返回 HTTP 200 正常。

**诊断**：
```bash
# 检查连通性
curl -s -o /dev/null -w "HTTP %{http_code}\n" --connect-timeout 10 https://api.github.com/repos/jsxuaijun-art/hermes-data

# 检查远程 URL
cd /mnt/c/Users/Admin/hermes-sync && git remote -v
```

**处理**：
1. 从 Windows Git Bash 中手工拉取
2. 调大 git 超时设置：`git config --global http.timeout 30 && git config --global http.lowSpeedLimit 1000`
3. 检查 token 是否过期（token 过期时 curl 仍可能通但 git 操作会挂）
4. 尝试关掉代理后再试

### SSH 密码连接（阿里云）

阿里云 ECS 使用密码认证（非密钥文件），`sshpass` 必须提前安装：

```bash
# 安装
sudo apt-get install -y sshpass

# 连接
sshpass -p 'yx168168/*-' ssh -o StrictHostKeyChecking=no root@47.103.27.171

# 执行单条命令（适合脚本内调用）
sshpass -p 'yx168168/*-' ssh root@47.103.27.171 'command'
```

### 仓库清理

**问题**：阿里云上曾有两个仓库同时存在（`/opt/hermes-sync/` 和 `/root/HermesAgent/`），导致混淆。

**处理**：统一使用 `/opt/hermes-sync/`，废弃 `/root/HermesAgent/`。废弃前确认该仓库无独有数据。

### 日志查看

```bash
# 阿里云
tail -f /var/log/hermes-sync.log

# 排除私密内容查看
tail -100 /var/log/hermes-sync.log | grep -v 'password\|token\|secret'
```

## 常见失效原因

| 失效场景 | 诊断方法 | 修复方案 |
|----------|----------|----------|
| crontab 有条目但仓库不存在 | `ls -la /opt/hermes-sync/.git` | `git clone https://... /opt/hermes-sync` |
| git push 认证失败 | `git push` 手动试 | 更新 token 或切换 SSH 密钥 |
| crontab 不执行 | `systemctl status cron` | `systemctl enable --now cron` |
| WSL git 超时 | 先测 curl，再测 git | 切 Windows Git Bash 替代 |
| 内存满无法写入 (2,200 char) | 更新时报错 | 替换同主题旧条目，压缩关键事实 |
