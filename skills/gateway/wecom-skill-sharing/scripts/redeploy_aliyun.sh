#!/usr/bin/env bash
# 重新部署 hermes-data-app 到阿里云（改完 app.py/模板后一键同步+重启+健康检查）
# 用法: bash scripts/redeploy_aliyun.sh [本地应用目录]
set -euo pipefail

SERVER="root@47.103.27.171"
APP="${1:-/home/administrator/hermes-data-app}"
REMOTE="/opt/hermes-data-app"
PORT="${PORT:-8000}"

echo "==> scp 应用文件到 $SERVER:$REMOTE"
scp -o ConnectTimeout=10 "$APP/app.py" "$APP/qingshui_risk_engine.py" "$APP/requirements.txt" "$SERVER:$REMOTE/"
scp -o ConnectTimeout=10 -r "$APP/templates/" "$SERVER:$REMOTE/"

echo "==> 重启服务 + 健康检查"
ssh -o ConnectTimeout=10 "$SERVER" "systemctl restart hermes-diag.service && sleep 2 && \
  systemctl is-active hermes-diag.service && \
  curl -s -o /dev/null -w \"localhost:$PORT HTTP %{http_code}\n\" http://localhost:$PORT/"

echo "==> 外网检查（若失败=安全组未放行 $PORT 端口）"
curl -s -o /dev/null -m 8 -w "external http://$SERVER:$PORT HTTP %{http_code}\n" "http://$(echo $SERVER | sed 's/.*@//'):$PORT/" || echo "external: FAILED (check 安全组)"
