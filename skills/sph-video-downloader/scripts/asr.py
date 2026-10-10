#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""视频/音频 → 中文口播文案（自动提音频 + faster-whisper 转写）
用法:
  python3 asr.py <视频.mp4> [输出.txt] [模型目录] [--timeline]
默认（无特殊指令）：只输出**纯净全文**，无时间轴——徐总规约，勿加秒数。
加 --timeline 才输出带时间轴的逐句版 + 纯净全文。
默认模型目录: 环境变量 FW_MODEL_DIR → 否则 ~/.cache/faster-whisper/medium
(Hermes venv 已装 faster-whisper + imageio-ffmpeg; 模型用 dl_model_hfmirror.sh 拉)
"""
import os
import subprocess
import sys
from pathlib import Path

_argv = [a for a in sys.argv[1:] if a != "--timeline"]
want_timeline = "--timeline" in sys.argv
video = _argv[0]
out = _argv[1] if len(_argv) > 1 else str(Path(video).stem) + "_文案.txt"
model_dir = _argv[2] if len(_argv) > 2 else os.environ.get("FW_MODEL_DIR")
default_model = Path("/home/administrator/.cache/faster-whisper/medium")
if not model_dir:
    model_dir = str(default_model) if Path(default_model, "model.bin").exists() else None
if not model_dir or not Path(model_dir, "model.bin").exists():
    print("未找到模型(model.bin)；请先跑 dl_model_hfmirror.sh 下载一次，或设 FW_MODEL_DIR")
    sys.exit(2)

import imageio_ffmpeg
ff = imageio_ffmpeg.get_ffmpeg_exe()
wav = Path("/tmp/_asr_audio.wav")
print("音频提取:", video, "→", wav, flush=True)
r = subprocess.run([ff, "-y", "-i", video, "-vn", "-ac", "1", "-ar", "16000",
                    "-c:a", "pcm_s16le", str(wav)], capture_output=True, text=True)
if r.returncode != 0:
    print("音频提取失败:", r.stderr[-400:])
    sys.exit(1)

from faster_whisper import WhisperModel  # 延迟导入，缩启动
print("加载模型:", model_dir, flush=True)
model = WhisperModel(model_dir, device="cpu", compute_type="int8")

# 不用 faster-whisper 自带的 av 解码（PyAV>=19 删了 metadata_errors 参数会报错），
# 自己把 16k 单声道 wav 读成 float32 数组喂进去，彻底避开 av 版本兼容问题。
import wave
import numpy as np
with wave.open(str(wav), "rb") as w:
    audio = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
print("音频样本:", len(audio), "(约%.1f秒)" % (len(audio) / 16000.0), flush=True)
print("转写中 ...", flush=True)
segments, info = model.transcribe(audio, language="zh", beam_size=5, vad_filter=True)
lines, full = [], []
for s in segments:
    mm = int(s.start // 60); ss = int(s.start % 60)
    t = s.text.strip()
    lines.append(f"[{mm:02d}:{ss:02d}] {t}")
    full.append(t)
# 默认只输出纯净全文（徐总规约 2026-10-10：无特殊指令不要时间轴）；--timeline 才带逐句时间轴
if want_timeline:
    text = "\n".join(lines) + "\n\n===== 纯净全文 =====\n" + "".join(full)
else:
    text = "".join(full)
Path(out).write_text(text, encoding="utf-8")
print(f"已保存: {out}  ({len(lines)} 段{'，含时间轴' if want_timeline else '，纯净全文无时间轴'})", flush=True)
Path(wav).unlink(missing_ok=True)