#!/bin/bash
# ============================================================
# Hermes 爬虫工具集 — 环境一键安装脚本
# 用法: bash setup.sh
# 说明: 将 DrissionPage + scrapling + curl_cffi + Playwright
#        + curl-impersonate 系统二进制安装到 Hermes 主环境
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── 1. 定位 Hermes Python 环境 ──────────────────────────────
if [ -d "$HOME/.venv-hermes" ]; then
    HERMES_PYTHON="$HOME/.venv-hermes/bin/python3"
    HERMES_PIP="$HOME/.venv-hermes/bin/pip"
    echo "🔍 检测到 Hermes 虚拟环境: $HOME/.venv-hermes"
    source "$HOME/.venv-hermes/bin/activate"
else
    HERMES_PYTHON="$(which python3)"
    HERMES_PIP="pip3"
    echo "🔍 未检测到 Hermes 虚拟环境，使用系统 Python: $HERMES_PYTHON"
fi

PYTHON_VER=$($HERMES_PYTHON --version 2>&1)
echo "   Python版本: $PYTHON_VER"

# ── 2. Pip 镜像 ─────────────────────────────────────────────
PIP_MIRROR="https://pypi.tuna.tsinghua.edu.cn/simple"
PIP_OPTS="-i $PIP_MIRROR --timeout 60"

# ── 3. 安装 Python 包 ───────────────────────────────────────
echo ""
echo "📥 [1/5] 安装 DrissionPage..."
$HERMES_PIP install $PIP_OPTS DrissionPage 2>&1 | grep -E "^(Successfully|ERROR|WARNING)" || echo "   已是最新"

echo "📥 [2/5] 安装 scrapling..."
$HERMES_PIP install $PIP_OPTS scrapling 2>&1 | grep -E "^(Successfully|ERROR|WARNING)" || echo "   已是最新"

echo "📥 [3/5] 安装 curl_cffi..."
$HERMES_PIP install $PIP_OPTS curl_cffi 2>&1 | grep -E "^(Successfully|ERROR|WARNING)" || echo "   已是最新"

echo "📥 [4/5] 安装 Playwright..."
$HERMES_PIP install $PIP_OPTS playwright 2>&1 | grep -E "^(Successfully|ERROR|WARNING)" || echo "   已是最新"

# ── 4. 安装 Chromium 浏览器 ─────────────────────────────────
echo ""
echo "🌐 [5/5] 安装 Chromium 浏览器（Playwright）..."
$HERMES_PYTHON -m playwright install chromium 2>&1 | tail -3

# ── 5. 安装 curl-impersonate 系统二进制 ─────────────────────
echo ""
echo "⬇️  安装 curl-impersonate 系统二进制..."
CURL_IMP_URL="https://github.com/lwthiker/curl-impersonate/releases/download/v0.6.1/curl-impersonate-v0.6.1.x86_64-linux-gnu.tar.gz"
CURL_IMP_TGZ="/tmp/curl-imp.tar.gz"

if command -v curl-impersonate-chrome &>/dev/null; then
    echo "   ✅ curl-impersonate 已安装，跳过"
else
    echo "   尝试从 GitHub 下载..."
    # 先试 Python requests（走代理，更可靠）
    $HERMES_PYTHON -c "
import requests, tarfile, os, shutil
url = '$CURL_IMP_URL'
path = '$CURL_IMP_TGZ'
try:
    r = requests.get(url, timeout=120, stream=True)
    if r.status_code == 200 and len(r.content) > 1000:
        with open(path, 'wb') as f:
            f.write(r.content)
        with tarfile.open(path, 'r:gz') as tar:
            tar.extractall('/tmp/')
        for fname in os.listdir('/tmp/'):
            if fname.startswith('curl-impersonate') or fname.startswith('curl_chrome') or fname.startswith('curl_edge') or fname.startswith('curl_ff') or fname.startswith('curl_safari'):
                src = os.path.join('/tmp/', fname)
                if os.path.isfile(src):
                    shutil.copy2(src, '/usr/local/bin/' + fname)
                    os.chmod('/usr/local/bin/' + fname, 0o755)
        print('   ✅ curl-impersonate 系统二进制安装完成')
    else:
        print('   ⚠️  GitHub 下载失败 (HTTP {})，请手动安装'.format(r.status_code))
except Exception as e:
    print('   ⚠️  下载失败: {}'.format(e))
    print('   请手动下载安装: https://github.com/lwthiker/curl-impersonate/releases')
" 2>&1
fi

# ── 6. 验证 ──────────────────────────────────────────────────
echo ""
echo "═" 50
echo "   🔍 验证安装结果"
echo "═" 50

$HERMES_PYTHON -c "
import importlib, sys
pkgs = ['DrissionPage', 'scrapling', 'curl_cffi', 'playwright']
ok = True
for p in pkgs:
    try:
        v = importlib.metadata.version(p)
        print(f'   ✅ {p:<15s} v{v}')
    except:
        print(f'   ❌ {p:<15s} 未安装')
        ok = False
sys.exit(0 if ok else 1)
" 2>&1

echo ""
echo "   🔍 curl-impersonate 系统二进制:"
if command -v curl-impersonate-chrome &>/dev/null; then
    echo "   ✅ 已安装 ($(curl-impersonate-chrome --version 2>&1 | head -1))"
    echo "   可用指纹版本:"
    for f in /usr/local/bin/curl_chrome* /usr/local/bin/curl_ff* /usr/local/bin/curl_edge* /usr/local/bin/curl_safari*; do
        echo "     $(basename $f)"
    done
else
    echo "   ⚠️  未安装（不影响 Python 使用，curl_cffi 已提供同等能力）"
fi

echo ""
echo "═══════════════════════════════════════════════════"
echo "   ✅ 全部完成！"
echo ""
echo "   共享爬虫脚本目录:"
echo "     $SCRIPT_DIR/scripts/"
echo ""
echo "   新电脑部署:"
echo "     git pull  # 拉取最新脚本"
echo "     bash scrapling/setup.sh  # 一键安装"
echo "═══════════════════════════════════════════════════"