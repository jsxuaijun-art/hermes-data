#!/bin/bash
# ============================================================
# Scrapling 环境一键安装脚本
# 用法: bash setup.sh
# 说明: 在 ~/scrapling-env 下创建独立 Python 虚拟环境
#       安装 Scrapling + Playwright + Chromium 浏览器
#       和其他电脑共享的爬虫脚本放在同目录 scripts/ 下
# ============================================================

set -e

echo "🚀 开始安装 Scrapling 环境..."

# 1. 获取当前脚本所在目录（即 hermes-data/scrapling/）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 2. 创建虚拟环境
if [ ! -d "$HOME/scrapling-env" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv "$HOME/scrapling-env"
else
    echo "✅ 虚拟环境已存在"
fi

# 3. 安装 Scrapling（全部依赖）
echo "📥 安装 Scrapling (全部依赖)..."
source "$HOME/scrapling-env/bin/activate"
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple scrapling[all] 2>&1 | tail -5

# 4. 安装 Playwright Chromium 浏览器
echo "🌐 安装 Chromium 浏览器..."
playwright install chromium 2>&1 | tail -5

echo ""
echo "✅ Scrapling 环境安装完成！"
echo ""
echo "使用方法："
echo "  source ~/scrapling-env/bin/activate   # 激活环境"
echo "  python scripts/xxx.py                 # 运行爬虫脚本"
echo "  deactivate                            # 退出环境"
echo ""
echo "共享的爬虫脚本目录："
echo "  $SCRIPT_DIR/scripts/"
