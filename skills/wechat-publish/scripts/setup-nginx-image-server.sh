#!/bin/bash
# wechat-publish 正文配图用 nginx 图片服务 — 一键安装/检查
# 用法: bash setup-nginx-image-server.sh [check|setup]
# 默认 check: 只检查不修改

set -e
ACTION="${1:-check}"

echo "=== nginx 图片服务 ==="

if [ "$ACTION" = "check" ]; then
    echo ">>> 检查 nginx 是否安装..."
    which nginx 2>/dev/null || { echo "❌ nginx 未安装，运行 $0 setup"; exit 1; }
    echo "   ✅ nginx installed"

    echo ">>> 检查 8080 端口监听..."
    if ss -tlnp | grep -q ':8080'; then
        echo "   ✅ 8080 端口正常"
    else
        echo "   ⚠️ 8080 端口未监听，运行 $0 setup"
        exit 1
    fi

    echo ">>> 检查图片目录..."
    ls /var/www/html/images/ 2>/dev/null || echo "   ⚠️ /var/www/html/images/ 目录不存在"
    echo "   ✅ 检查完成"
    exit 0
fi

if [ "$ACTION" = "setup" ]; then
    echo ">>> 配置 nginx 图片服务..."
    cat > /etc/nginx/sites-available/images << 'EOF'
server {
    listen 8080;
    root /var/www/html;
    index index.html;
    server_name _;
    location / {
        try_files $uri $uri/ =404;
        add_header Access-Control-Allow-Origin *;
    }
}
EOF
    ln -sf /etc/nginx/sites-available/images /etc/nginx/sites-enabled/images 2>/dev/null || true
    mkdir -p /var/www/html/images
    nginx -t && systemctl reload nginx
    echo "   ✅ 配置完成，图片目录: /var/www/html/images/"
    echo "   使用方式: markdown 中引用 http://127.0.0.1:8080/images/xxx.jpg"
fi
