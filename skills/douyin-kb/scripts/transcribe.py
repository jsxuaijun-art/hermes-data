#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把本地视频/音频转成带时间戳的文字稿（faster-whisper，中文）。
用法:
  python transcribe.py <媒体文件> [-o out.md] [--size base|small] [--prompt "领域提示"]
输出: 默认 /tmp/<basename>_transcript.md，每行 [起-止] 文本；也打印到 stdout。
转写引擎在持久化 venv: ~/videoenv（faster-whisper，清华镜像装的）。
"""
import os, sys, argparse, subprocess, tempfile

VIDENV_PY = os.path.expanduser("~/videoenv/bin/python")
WORKER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_whisper_worker.py")
FFMPEG = "/home/administrator/.local/bin/ffmpeg"  # imageio-ffmpeg 静态二进制符号链接

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("media")
    ap.add_argument("-o", "--out")
    ap.add_argument("--size", default="base", choices=["base", "small", "medium"])
    ap.add_argument("--prompt", default="以下是财税/短视频口播内容字幕。")
    a = ap.parse_args()

    base = os.path.splitext(os.path.basename(a.media))[0]
    out = a.out or os.path.join("/tmp", base + "_transcript.md")
    wav = tempfile.mktemp(suffix=".wav")

    # 1) 抽音频：-vn 丢视频轨，单声道 16kHz（whisper 标准输入）
    print(f"[1/2] 抽音频 {os.path.basename(a.media)} → wav ...", file=sys.stderr)
    subprocess.run([FFMPEG, "-y", "-i", a.media, "-vn", "-ac", "1", "-ar", "16000", wav],
                   check=True, capture_output=True)

    # 2) 转写（走 videoenv；hf 走镜像，禁用 xet）
    print(f"[2/2] faster-whisper ({a.size}) 转写中 ...", file=sys.stderr)
    env = dict(os.environ)
    env["HF_ENDPOINT"] = "https://hf-mirror.com"
    env["HF_HUB_DISABLE_XET"] = "1"
    r = subprocess.run([VIDENV_PY, WORKER, wav, out, a.size, a.prompt], env=env)
    if r.returncode != 0:
        print("转写失败，见上方错误。首次运行会从 hf-mirror 下载模型（base≈74MB，small≈460MB）。",
              file=sys.stderr)
    else:
        print(f"✅ 文字稿已写入: {out}", file=sys.stderr)
    try:
        os.remove(wav)
    except OSError:
        pass
    sys.exit(r.returncode)

if __name__ == "__main__":
    main()
