#!/bin/bash
# ===================================================================
# 小智AI ESP32 服务端 一键部署脚本 (阿里云 4核4G3M / Ubuntu24.04)
# 镜像: ghcr.nju.edu.cn/xinnan-tech/xiaozhi-esp32-server:server_latest
# 流程: 装Docker(若需) -> 写配置(已内置API Key) -> 下语音模型 -> 拉镜像 -> 启动
# 用法: bash deploy-aliyun.sh   (在服务器 $HOME 下执行即可)
# ===================================================================
set -e

echo "===== 0) 环境准备 ====="
SUDO=""
if [ "$(id -u)" -ne 0 ]; then SUDO="sudo"; fi

echo "===== 1) 检查/安装 Docker ====="
if ! command -v docker >/dev/null 2>&1; then
  echo "未检测到 Docker，开始安装..."
  $SUDO apt-get update -y
  $SUDO apt-get install -y docker.io docker-compose-plugin
  $SUDO systemctl enable --now docker
else
  echo "Docker 已安装: $($SUDO docker --version 2>/dev/null || docker --version)，跳过安装。"
fi

WORK_DIR="$HOME/xiaozhi-deploy"
mkdir -p "$WORK_DIR/data" "$WORK_DIR/models/SenseVoiceSmall"
cd "$WORK_DIR"

echo "===== 2) 获取公网 IP（多源兜底） ====="
get_public_ip() {
  local ip=""
  for url in \
    "http://metadata.tencent.com/latest/meta-data/public-ipv4" \
    "https://api.ipify.org" \
    "https://ifconfig.me" \
    "https://icanhazip.com" ; do
    ip=$(curl -s -m 8 "$url" 2>/dev/null | grep -oE '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | head -1)
    if [ -n "$ip" ]; then echo "$ip"; return; fi
  done
}
PUBLIC_IP=$(get_public_ip)
echo "检测到公网 IP: ${PUBLIC_IP:-<未获取到>}"

echo "===== 3) 写入配置文件 data/.config.yaml ====="
cat > data/.config.yaml <<'CONFIG_EOF'
server:
  ip: 0.0.0.0
  port: 8000
  http_port: 8003
  websocket: ws://__PUBLIC_IP__:8000/xiaozhi/v1/
  vision_explain: http://__PUBLIC_IP__:8003/mcp/vision/explain
  timezone_offset: +8

prompt: |
  你是「盈信税务陪伴助手」，由苏州盈信企业管理有限公司（创始人江敏，高级会计师，二十余年财税服务经验）打造的智能陪伴助手。
  你的定位：用通俗易懂的中文，为中小企业主、创业者、代理记账同行解答财税、工商、税务合规相关问题。
  语气亲切、专业、耐心，像一位经验丰富又平易近人的财税顾问。
  涉及具体税额计算时，先给结论，再拆解计算过程，必要时用表格呈现。
  知识边界：聚焦中国税法、增值税、企业所得税、个人所得税、小规模纳税人政策、发票管理、工商登记等。
  政策会更新，涉及最新优惠或具体申报口径，以官方公告或提示用户咨询当地税务机关为准；不提供违法避税建议。
  支持语音对话、打字聊天、联网查询最新政策、识别用户发来的发票/报表图片并给针对性建议。

selected_module:
  VAD: SileroVAD
  ASR: FunASR
  LLM: MyDeepSeek
  TTS: EdgeTTS
  Memory: nomem
  Intent: nointent

VAD:
  SileroVAD:
    type: silero
    threshold: 0.5
    threshold_low: 0.3
    model_dir: models/snakers4_silero-vad
    min_silence_duration_ms: 200

ASR:
  FunASR:
    type: fun_local
    model_dir: models/SenseVoiceSmall
    output_dir: tmp/

TTS:
  EdgeTTS:
    type: edge
    voice: zh-CN-XiaoxiaoNeural
    output_dir: tmp/

LLM:
  MyDeepSeek:
    type: openai
    base_url: https://llm.chudian.site/v1
    url: https://llm.chudian.site/v1
    model_name: deepseek-v4-flash
    api_key: sk-ag-a55f4fac26108dcff9ff47589317ab0b
    temperature: 0.7
    max_tokens: 2000

Memory:
  nomem:
    enable: false

Intent:
  nointent:
    enable: false
CONFIG_EOF

if [ -n "$PUBLIC_IP" ]; then
  sed -i "s/__PUBLIC_IP__/$PUBLIC_IP/g" data/.config.yaml
else
  echo "⚠️ 未能自动获取公网IP，先用占位符写入，稍后必须手动替换！"
fi
if grep -q "__PUBLIC_IP__" data/.config.yaml; then
  echo "⚠️ 警告：配置中仍存在 __PUBLIC_IP__ 占位符！"
  echo "   请手动编辑 data/.config.yaml，把所有 __PUBLIC_IP__ 替换为你的服务器公网IP后重启容器。"
else
  echo "已将公网 IP 写入配置。"
fi

echo "===== 4) 写入 docker-compose.yml ====="
cat > docker-compose.yml <<'COMPOSE_EOF'
services:
  xiaozhi-esp32-server:
    image: ghcr.nju.edu.cn/xinnan-tech/xiaozhi-esp32-server:server_latest
    container_name: xiaozhi-esp32-server
    restart: always
    security_opt:
      - seccomp:unconfined
    environment:
      - TZ=Asia/Shanghai
    ports:
      - "8000:8000"
      - "8003:8003"
    volumes:
      - ./data:/opt/xiaozhi-esp32-server/data
      - ./models/SenseVoiceSmall/model.pt:/opt/xiaozhi-esp32-server/models/SenseVoiceSmall/model.pt
COMPOSE_EOF

echo "===== 5) 下载 SenseVoiceSmall 语音识别模型(约940M) ====="
if [ ! -f models/SenseVoiceSmall/model.pt ]; then
  set +e
  echo "开始下载, 请耐心等待(3M带宽可能需几十分钟)..."
  wget -c -O models/SenseVoiceSmall/model.pt "https://www.modelscope.cn/models/iic/SenseVoiceSmall/resolve/master/model.pt"
  if [ ! -s models/SenseVoiceSmall/model.pt ]; then
    wget -c -O models/SenseVoiceSmall/model.pt "https://modelscope.cn/models/iic/SenseVoiceSmall/resolve/master/model.pt"
  fi
  set -e
  if [ ! -s models/SenseVoiceSmall/model.pt ]; then
    echo "⚠️ 模型下载失败。容器仍可启动，但语音识别不可用。"
    echo "   请手动下载 model.pt 放到 $WORK_DIR/models/SenseVoiceSmall/ 后重启: $SUDO docker compose restart"
  else
    echo "模型下载完成: $(du -h models/SenseVoiceSmall/model.pt | cut -f1)"
  fi
else
  echo "模型已存在，跳过下载。"
fi

echo "===== 6) 拉取镜像并启动容器 ====="
$SUDO docker compose pull
$SUDO docker compose up -d

echo ""
echo "===== 部署完成 ====="
echo "工作目录: $WORK_DIR"
echo "查看状态: $SUDO docker ps --filter name=xiaozhi-esp32-server"
echo "查看日志: $SUDO docker logs -f xiaozhi-esp32-server"
echo ""
echo "下一步:"
echo " 1) 腾讯云控制台防火墙放行 8000 和 8003 端口 (TCP)"
echo " 2) 浏览器打开 https://xiaozhi.me 烧录固件到 ESP32 (服务端类型选 '小智')"
echo " 3) 设备配网时 WebSocket 地址填: ws://${PUBLIC_IP:-你的公网IP}:8000/xiaozhi/v1/"
echo " 4) 喊『小智小智』开始对话"
