import os, sys
VIDEO = sys.argv[1] if len(sys.argv) > 1 else r"videos\input.mp4"
OUT = sys.argv[2] if len(sys.argv) > 2 else VIDEO.rsplit(".", 1)[0] + "_文案.txt"
# 模型路径：先 download_model.py 拉到本地，再用此路径；可设环境变量 FW_MODEL_DIR
MODEL_DIR = os.environ.get("FW_MODEL_DIR",
    r"C:\Users\Admin\.cache\modelscope\models\Systran--faster-whisper-medium\snapshots\master")

import imageio_ffmpeg
ffmpeg_dir = os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe())
os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")

from faster_whisper import WhisperModel
print("loading model ...", MODEL_DIR)
model = WhisperModel(MODEL_DIR, device="cpu", compute_type="int8")
print("transcribing ...")
segments, info = model.transcribe(VIDEO, language="zh", beam_size=5, vad_filter=True)
print(f"lang={info.language} prob={info.language_probability:.2f}")

lines = []
for seg in segments:
    t0 = seg.start; mm = int(t0 // 60); ss = int(t0 % 60)
    lines.append(f"[{mm:02d}:{ss:02d}] {seg.text}")
text = "\n".join(lines)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(text)
print(f"\nsaved: {OUT} ({len(lines)} segments)")
