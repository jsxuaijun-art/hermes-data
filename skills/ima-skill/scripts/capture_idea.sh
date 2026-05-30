#!/bin/bash
# capture_idea — 快速捕捉灵感，追加到 IMA 💡灵感记录（同一笔记持续追加）
#
# 用法:
#   capture_idea "今天想到一个节税思路..."
#   echo "某个想法" | capture_idea
#   capture_idea "$(cat idea.txt)"
#
# 环境要求: node, ~/.config/ima/{client_id,api_key}
# 依赖: ima-skill 下的 ima_api.cjs
#
# 文件位置: 本脚本是 ima-skill 的 scripts/ 文件，建议也链接到 ~/.local/bin/ 便于全局调用：
#   ln -sf "$(dirname "$0")/capture_idea.sh" ~/.local/bin/capture_idea

set -euo pipefail

NOTE_ID="7460975158506091"  # 💡灵感记录 笔记固定 ID
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# === 读取凭证 ===
if [ -f ~/.config/ima/client_id ] && [ -f ~/.config/ima/api_key ]; then
    CLIENT_ID=$(cat ~/.config/ima/client_id | tr -d '[:space:]')
    API_KEY=$(cat ~/.config/ima/api_key | tr -d '[:space:]')
else
    CLIENT_ID="${IMA_OPENAPI_CLIENTID:-}"
    API_KEY="${IMA_OPENAPI_APIKEY:-}"
fi

if [ -z "$CLIENT_ID" ] || [ -z "$API_KEY" ]; then
    echo "❌ 缺少 IMA 凭证。请配置 ~/.config/ima/client_id + api_key 或设置环境变量 IMA_OPENAPI_CLIENTID / IMA_OPENAPI_APIKEY" >&2
    exit 1
fi

# === 读入内容 ===
if [ $# -ge 1 ]; then
    CONTENT="$1"
elif [ ! -t 0 ]; then
    CONTENT=$(cat)
else
    echo "❌ 用法: capture_idea \"灵感内容\" 或通过管道传入内容" >&2
    exit 1
fi

if [ -z "$CONTENT" ]; then
    echo "❌ 内容为空，跳过保存" >&2
    exit 1
fi

# === 构建请求 ===
OPTS=$(printf '{"clientId":"%s","apiKey":"%s"}' "$CLIENT_ID" "$API_KEY")

# 追加内容带时间戳分隔
BODY=$(printf '{"note_id":"%s","content_format":1,"content":"\n---\n## 💡 %s\n%s\n"}' \
    "$NOTE_ID" "$TIMESTAMP" "$(echo "$CONTENT" | sed 's/"/\\"/g')")

# === 找 ima_api.cjs ===
SKILL_DIR=""
for dir in "$HOME/.hermes/skills/ima-skill" "${HERMES_HOME:-$HOME/.hermes}/skills/ima-skill" "/usr/share/hermes/skills/ima-skill"; do
    if [ -f "$dir/ima_api.cjs" ]; then
        SKILL_DIR="$dir"
        break
    fi
done

if [ -z "$SKILL_DIR" ]; then
    echo "❌ 找不到 ima_api.cjs（ima-skill 未安装）" >&2
    exit 1
fi

# === 调用 API ===
if ! resp=$(node "$SKILL_DIR/ima_api.cjs" "openapi/note/v1/append_doc" "$BODY" "$OPTS" 2>/tmp/ima_err); then
    err_json=$(cat /tmp/ima_err)
    err_msg=$(echo "$err_json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('msg','未知错误'))" 2>/dev/null || echo "$err_json")
    echo "❌ 保存灵感失败: $err_msg" >&2
    exit 1
fi

code=$(echo "$resp" | python3 -c "import sys,json; print(json.load(sys.stdin).get('code',-1))" 2>/dev/null)
if [ "$code" = "0" ]; then
    echo "✅ 灵感已保存 → 💡灵感记录"
else
    msg=$(echo "$resp" | python3 -c "import sys,json; print(json.load(sys.stdin).get('msg','未知错误'))" 2>/dev/null || echo "未知")
    echo "❌ 保存灵感失败 (code=$code): $msg" >&2
    exit 1
fi
