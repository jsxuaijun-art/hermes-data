#!/usr/bin/env bash
# hermes-verify: 网易163邮箱凭据直连探测脚本
# 用途：绕过 himalaya，直连 imap.163.com 看服务器对授权码的真实响应。
#       a1 OK  = 授权码有效；a1 NO LOGIN Login error or password error = 凭据不被认可。
# 用法：bash probe-163-imap.sh <完整邮箱地址> <16位授权码>
# 注意：授权码会出现在命令行，脚本内勿回显；用完后建议轮换。
set -u
EMAIL="${1:?用法: $0 <邮箱> <授权码>}"
AUTHCODE="${2:?用法: $0 <邮箱> <授权码>}"

timeout 15 bash -c '
openssl s_client -connect imap.163.com:993 -quiet 2>/dev/null <<EOF
a1 LOGIN '"$EMAIL"' '"$AUTHCODE"'
a2 LOGOUT
EOF
' 2>&1 | grep -E 'a1 OK|a1 NO|a1 BAD' | head -5

echo "---"
echo "解读：a1 OK => 授权码有效，回 himalaya 配置验证；a1 NO => 服务未开/授权码错/已重置，须回 mail.163.com 重新生成。"
