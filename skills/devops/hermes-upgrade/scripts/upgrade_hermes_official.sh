#!/bin/bash
# Hermes 官方原版升级脚本 (template — adapt per machine before running)
# Run from OUTSIDE a live Hermes session (a running agent cannot rewrite its own
# source checkout). Usage: bash /root/upgrade_hermes_official.sh
set -e

cd /root/.hermes/hermes-agent

echo "=== 1/5 抓取官方 GitHub 最新代码 ==="
git remote get-url upstream 2>/dev/null || git remote add upstream https://github.com/NousResearch/hermes-agent.git
git fetch upstream main --quiet || echo "  (upstream fetch 失败，尝试直连...)"

echo "=== 2/5 将 origin 指向官方原版仓库 ==="
git remote set-url origin https://github.com/NousResearch/hermes-agent.git

echo "=== 3/5 切换到官方 GitHub 最新版本 (reset --hard origin/main) ==="
git fetch --quiet origin main
git reset --hard origin/main

echo "=== 4/5 重装 Python 依赖 ==="
if [ -f venv/bin/pip ]; then
  ./venv/bin/pip install -e . --quiet --disable-pip-version-check || ./venv/bin/pip install -e .
else
  pip install -e .
fi

echo "=== 5/5 验证版本 ==="
./venv/bin/python -c "from hermes_cli import __version__; print('Hermes 版本:', __version__)" 2>/dev/null || true
git log -1 --format='最新提交: %h %ad %s' --date=short

echo ""
echo "✅ 升级完成！现在请重新启动 Hermes："
echo "   hermes"
