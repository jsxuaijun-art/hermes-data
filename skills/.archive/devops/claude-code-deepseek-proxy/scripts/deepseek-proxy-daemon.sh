#!/bin/bash
# 静默启动 DeepSeek 代理（后台运行，日志写文件）
# 由 .bashrc 调用，自动检查是否已在运行
# 安装位置：/home/dmin/.local/bin/deepseek-proxy-daemon.sh

PIDFILE="/tmp/deepseek-proxy.pid"
LOGFILE="/tmp/deepseek-proxy.log"

# 检查是否已在运行
if [ -f "$PIDFILE" ]; then
  OLD_PID=$(cat "$PIDFILE")
  if kill -0 "$OLD_PID" 2>/dev/null; then
    exit 0
  fi
  rm -f "$PIDFILE"
fi

# 检查端口是否已被占用
if command -v ss &>/dev/null; then
  if ss -tlnp | grep -q ":3000 "; then
    exit 0
  fi
elif command -v lsof &>/dev/null; then
  if lsof -ti:3000 &>/dev/null; then
    exit 0
  fi
fi

# 启动代理
source ~/.hermes/.env 2>/dev/null || true
DEEPSEEK_KEY="$DEEPSEEK_API_KEY"

if [ -z "$DEEPSEEK_KEY" ]; then
  echo "[deepseek-proxy] WARNING: DEEPSEEK_API_KEY not found in ~/.hermes/.env" >> "$LOGFILE"
  exit 1
fi

cd /home/dmin/.npm/_npx/7fa4a753cadbb396/node_modules/anthropic-proxy 2>/dev/null || {
  echo "[deepseek-proxy] ERROR: anthropic-proxy not found" >> "$LOGFILE"
  exit 1
}

nohup env \
  ANTHROPIC_PROXY_BASE_URL="https://api.deepseek.com" \
  ANTHROPIC_PROXY_API_KEY="$DEEPSEEK_KEY" \
  COMPLETION_MODEL="deepseek-chat" \
  REASONING_MODEL="deepseek-chat" \
  PORT=3000 \
  node index.js >> "$LOGFILE" 2>&1 &

BGPID=$!
echo "$BGPID" > "$PIDFILE"

sleep 1
if kill -0 "$BGPID" 2>/dev/null; then
  echo "[deepseek-proxy] Started (PID $BGPID)" >> "$LOGFILE"
else
  echo "[deepseek-proxy] Failed to start" >> "$LOGFILE"
  rm -f "$PIDFILE"
fi
