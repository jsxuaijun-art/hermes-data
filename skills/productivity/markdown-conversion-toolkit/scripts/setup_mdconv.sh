#!/usr/bin/env bash
# mdconv 一键安装脚本 —— markitdown[all] + tesseract(中英文OCR)
# 适用：WSL Ubuntu / 原生Linux。跨机器部署时在此机执行即可。
# 用法：bash setup_mdconv.sh
set -e

# 国内网络统一用清华镜像（pypi.org 在国内常超时不可达）
MIRROR="https://pypi.tuna.tsinghua.edu.cn/simple"
export PIP_INDEX_URL="$MIRROR"
export PIP_DISABLE_PIP_VERSION_CHECK=1   # 跳过 pip 自升级提示/卡顿

# ---- 0. 前置：检测/创建 Python venv ----
PY=""
if [ -d "$HOME/hermes-agent/venv" ]; then
  PY="$HOME/hermes-agent/venv/bin/python"
elif [ -d "$HOME/.hermes/venv" ]; then
  PY="$HOME/.hermes/venv/bin/python"
else
  echo "[INFO] 未发现现有 venv，创建 ~/.hermes/venv ..."
  python3 -m venv ~/.hermes/venv
  PY="$HOME/.hermes/venv/bin/python"
fi
echo "[OK] 使用解释器: $PY"

# ---- 1. 安装 markitdown[all] ----
echo "[1/3] 检查 markitdown ..."
if "$PY" -m pip show markitdown >/dev/null 2>&1; then
  echo "  已存在: $("$PY" -m pip show markitdown 2>/dev/null | grep -m1 Version)"
else
  echo "  安装 markitdown[all] ..."
  "$PY" -m pip install 'markitdown[all]'
  echo "  markitdown 安装完成"
fi

# ---- 2. 安装 tesseract 二进制 + 中文语言包 ----
echo "[2/3] 检查 tesseract (需 chi_sim+eng) ..."
TT="$("$PY" -c "import os;print(os.path.join(os.path.dirname(__import__('sys').executable),'tesseract'))" 2>/dev/null)"
if [ -x "$TT" ] && "$TT" --list-langs 2>/dev/null | grep -q chi_sim; then
  echo "  tesseract 已含中文: OK"
elif command -v tesseract >/dev/null 2>&1 && tesseract --list-langs 2>/dev/null | grep -q chi_sim; then
  echo "  系统 tesseract 已含中文: OK ($(tesseract --version 2>&1 | head -1))"
else
  echo "  安装 tesseract-binary（自带中文语言包）..."
  "$PY" -m pip install tesseract-binary
  echo "  完成（请确认 chi_sim 可用）"
fi

# ---- 3. 生成 mdconv 命令 ----
echo "[3/3] 生成 mdconv 命令 ..."
mkdir -p "$HOME/bin"
cat > "$HOME/bin/mdconv" <<'EOF'
#!/usr/bin/env bash
# mdconv - 统一文档/图片转 Markdown（markitdown + tesseract OCR）
set -e
PY=""
for c in "$HOME/hermes-agent/venv" "$HOME/.hermes/venv"; do
  [ -x "$c/bin/python" ] && PY="$c/bin/python" && break
done
[ -z "$PY" ] && PY=$(command -v python3)
ACT=$(dirname "$PY")/activate
[ -f "$ACT" ] && source "$ACT"

IMG_EXT='(png|jpg|jpeg|gif|bmp|webp|tif|tiff)'
out=""; args=()
while [ $# -gt 0 ]; do
  case "$1" in
    -o) out="$2"; shift 2;;
    --out) out="$2"; shift 2;;
    -h|--help) echo "用法: mdconv 输入文件/目录 [-o 输出.md]"; exit 0;;
    *) args+=("$1"); shift;;
  esac
done
input="${args[0]}"
[ -z "$input" ] && { echo "错误: 缺少输入文件"; exit 1; }

process_file() {
  local f="$1"; local ext="${f##*.}"; ext=$(echo "$ext" | tr '[:upper:]' '[:lower:]')
  if echo "$ext" | grep -Eq "^${IMG_EXT}$"; then
    tesseract "$f" stdout -l chi_sim+eng 2>/dev/null
  else
    markitdown "$f" 2>/dev/null
  fi
}
if [ -d "$input" ]; then
  for f in "$input"/*; do [ -f "$f" ] || continue; echo "===== $f ====="; process_file "$f"; echo ""; done
elif [ -n "$out" ]; then
  process_file "$input" > "$out"; echo "已写入: $out ($(wc -c < "$out") 字节)"
else
  process_file "$input"
fi
EOF
chmod +x "$HOME/bin/mdconv"

# ---- PATH 检查 ----
case ":$PATH:" in
  *":$HOME/bin:"*) echo "[OK] ~/bin 已在 PATH，mdconv 全局可用" ;;
  *) echo "[WARN] ~/bin 不在 PATH，请执行:"; echo '  echo '\''export PATH="$HOME/bin:$PATH"'\'' >> ~/.bashrc && source ~/.bashrc' ;;
esac

echo ""
echo "============================================"
echo "  安装完成！验证："
echo "  mdconv 文件.docx"
echo "  mdconv 图片.png   (tesseract 中文OCR)"
echo "============================================"
