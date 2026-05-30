#!/bin/bash
# 快速激活 Scrapling 环境
# 用法: source activate.sh
# 激活后可以直接运行 scripts/ 下的爬虫脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$HOME/scrapling-env/bin/activate"
echo "✅ Scrapling 环境已激活 (v$(python3 -c 'import importlib; print(importlib.metadata.version(\"scrapling\"))' 2>/dev/null || echo '?'))"
echo "📁 脚本目录: $SCRIPT_DIR/scripts/"
