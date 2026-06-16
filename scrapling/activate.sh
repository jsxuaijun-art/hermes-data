#!/bin/bash
# 快速激活 Hermes 爬虫环境
# 用法: source activate.sh
#
# DrissionPage / scrapling / curl_cffi / Playwright 都在
# Hermes 主环境里，激活后可直接 import 使用

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -d "$HOME/.venv-hermes" ]; then
    source "$HOME/.venv-hermes/bin/activate"
    echo "✅ Hermes 爬虫环境已激活"
    echo "   脚本目录: $SCRIPT_DIR/scripts/"
    echo ""
    echo "   可用工具:"
    python3 -c "
import importlib
for p in ['DrissionPage','scrapling','curl_cffi','playwright']:
    try:
        v = importlib.metadata.version(p)
        print(f'     ✅ {p:15s} v{v}')
    except:
        print(f'     ❌ {p:15s} 未安装')
" 2>/dev/null
else
    echo "⚠️  未检测到 Hermes 虚拟环境"
    echo "   请运行: bash $SCRIPT_DIR/setup.sh"
fi