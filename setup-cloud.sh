#!/bin/bash
# 在阿里云 Hermes 服务器上运行：bash setup-cloud.sh
# 先 SSH 登录阿里云，把本机 HermesAgent 同步到云端

set -e

# 1. 配置 git
git config --global user.name "jsxuaijun-art"
git config --global user.email "jsxuaijun-art@users.noreply.github.com"

# 2. 克隆仓库
cd /root
if [ ! -d "HermesAgent" ]; then
    git clone git@github.com:jsxuaijun-art/hermes-data.git HermesAgent
fi

cd /root/HermesAgent

# 3. 如果 SSH key 没配，用 token 方式（先检查有没有key）
if [ ! -f ~/.ssh/id_ed25519 ]; then
    echo "=== 请先配置 SSH key 或使用 HTTPS ==="
    echo "方案A: ssh-keygen -t ed25519 -C 'jsxuaijun-art'"
    echo "      然后把公钥加到 GitHub Settings -> SSH keys"
    echo "方案B: 用 HTTPS + token"
    echo "      git remote set-url origin https://jsxuaijun-art:TOKEN@github.com/jsxuaijun-art/hermes-data.git"
    exit 1
fi

# 4. 设置同步脚本
cat > /root/sync-hermes-cloud.sh << 'SYNC'
#!/bin/bash
# 阿里云 Hermes 同步脚本
# 每次有新的记忆/技能时运行，或定时运行

set -e
cd /root/HermesAgent

# 从云端 Hermes 复制数据
cp /root/.hermes/memories/MEMORY.md ./memories/ 2>/dev/null || true
cp /root/.hermes/memories/USER.md ./memories/ 2>/dev/null || true
cp /root/.hermes/SOUL.md ./ 2>/dev/null || true
rsync -a --delete /root/.hermes/skills/ ./skills/ 2>/dev/null || true

# 推送到 GitHub
git add -A
if ! git diff --cached --quiet; then
    git commit -m "sync: Cloud Hermes memories & skills $(date '+%Y-%m-%d %H:%M')"
    git push origin main || git push origin master
    echo "云端 -> GitHub 推送完成"
fi

# 拉取本机的最新数据
git fetch origin
git reset --hard origin/main || git reset --hard origin/master

# 写回云端 Hermes
cp ./memories/MEMORY.md /root/.hermes/memories/ 2>/dev/null || true
cp ./memories/USER.md /root/.hermes/memories/ 2>/dev/null || true
cp ./SOUL.md /root/.hermes/ 2>/dev/null || true
rsync -a --delete ./skills/ /root/.hermes/skills/ 2>/dev/null || true

echo "双向同步完成"
SYNC

chmod +x /root/sync-hermes-cloud.sh

# 5. 设置定时任务（每天凌晨3点自动同步）
(crontab -l 2>/dev/null; echo "0 3 * * * /root/sync-hermes-cloud.sh >> /root/hermes-sync.log 2>&1") | crontab -

echo "阿里云端配置完成！"
echo "手动同步运行: bash /root/sync-hermes-cloud.sh"
