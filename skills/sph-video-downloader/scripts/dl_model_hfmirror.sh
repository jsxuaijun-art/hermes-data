#!/bin/bash
# 下载 faster-whisper-medium 模型（经 hf-mirror.com 国内镜像）
# 注意：ModelScope 的 AI-ModelScope/faster-whisper-medium 已 404，改用 hf-mirror 直拉 Systran 官方。
D="${FW_MODEL_DIR:-/home/administrator/.cache/faster-whisper/medium}"
B=https://hf-mirror.com/Systran/faster-whisper-medium/resolve/main
mkdir -p "$D"
echo "target: $D"
for f in config.json tokenizer.json vocabulary.txt; do
  curl -sL -m 120 -o "$D/$f" "$B/$f" && echo "  ok $f $(stat -c%s "$D/$f" 2>/dev/null) bytes" || echo "  FAIL $f"
done
echo "downloading model.bin (约1.5GB, 断点续传)..."
curl -L -C - --retry 8 --retry-delay 3 --retry-all-errors -m 1700 \
  -o "$D/model.bin" "$B/model.bin" -w "  http=%{http_code} downloaded=%{size_download}\n"
echo "model.bin size: $(stat -c%s "$D/model.bin" 2>/dev/null) bytes"