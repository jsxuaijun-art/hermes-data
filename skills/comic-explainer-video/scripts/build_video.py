#!/usr/bin/env python3
"""comic-explainer-video · 成片合成脚本

输入一个 manifest JSON，输出一条 1920x1080 横版短视频：
  每个 shot = 一张图 + 一段旁白（edge-tts 配音 + 自动字幕）
  自动叠加：缓慢缩放动画、黄色关键词字幕、顶部合规声明条
  最后拼接所有镜头成片。

依赖：
  - ffmpeg（需在 PATH）
  - edge-tts（建议装在 managed venv：python -m pip install edge-tts）
  - 中文字体（默认 C:/Windows/Fonts/simhei.ttf，其他系统请改 FONT_FILE）

manifest 示例：
{
  "disclaimer": "内容仅供参考，具体以官方政策为准",
  "voice": "zh-CN-YunyangNeural",
  "shots": [
    {"image": "shot1.png", "text": "你明明知道便宜没好货。", "zoom": "in"},
    {"image": "shot2.png", "text": "低价是怎么低下去的？", "zoom": "none"}
  ]
}

用法：
  python build_video.py manifest.json -o output.mp4
"""
import argparse
import json
import os
import subprocess
import sys

FONT_FILE = "C:/Windows/Fonts/simhei.ttf"
FPS = 30

SUBTITLE_STYLE = (
    "FontSize=42,FontName=SimHei,PrimaryColour=&H00FFFF&,"
    "OutlineColour=&H000000&,BackColour=&H80000000&,Bold=1,"
    "Outline=3,Shadow=2,Alignment=2,MarginV=70"
)


def run(cmd):
    print("+ " + " ".join(cmd))
    subprocess.run(cmd, check=True)


def vtt_to_srt(vtt_path, srt_path):
    """把 edge-tts 产出的 .vtt 转成 ffmpeg subtitles 可用的 .srt。"""
    with open(vtt_path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    cues = []
    buf = []
    for line in lines:
        if line.strip() == "WEBVTT" or line.strip().startswith("NOTE"):
            continue
        if line.strip() == "":
            if buf:
                cues.append(buf)
                buf = []
        else:
            buf.append(line)
    if buf:
        cues.append(buf)
    out = []
    idx = 1
    for cue in cues:
        # 找到含 --> 的行作为时间轴
        txt = [l for l in cue if "-->" not in l]
        times = [l for l in cue if "-->" in l]
        if not times:
            continue
        t = times[0].replace(".", ",")
        out.append(str(idx))
        out.append(t)
        out.extend(txt)
        out.append("")
        idx += 1
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))


def gen_audio(text, mp3_path, vtt_path, voice):
    try:
        import edge_tts  # noqa: F401
    except ImportError:
        sys.exit("未找到 edge_tts，请先安装：python -m pip install edge-tts")
    run([
        sys.executable, "-m", "edge_tts",
        "-t", text, "-v", voice,
        "--write-media", mp3_path,
        "--write-subtitles", vtt_path,
    ])


def clip_duration(mp3_path):
    out = subprocess.check_output([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        mp3_path,
    ])
    return float(out.strip())


def build_shot(img_path, mp3_path, srt_path, out_clip, disclaimer_file, zoom):
    dur = clip_duration(mp3_path)
    frames = max(int(dur * FPS), 1)
    base_vf = "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080"
    if zoom == "in":
        base_vf += (
            f",zoompan=z='min(zoom+0.0015,1.2)':d={frames}:s=1920x1080:fps={FPS}"
            ":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        )
    base_vf += ",format=yuv420p"
    srt_posix = srt_path.replace("\\", "/")
    vf = (
        base_vf + ","
        f"subtitles='{srt_posix}':force_style='{SUBTITLE_STYLE}'"
    )
    if disclaimer_file:
        vf += (
            f",drawtext=fontfile='{FONT_FILE}':textfile='{disclaimer_file}'"
            ":fontcolor=white:fontsize=24:x=30:y=30:box=1:boxcolor=black@0.5"
        )
    run([
        "ffmpeg", "-y", "-loop", "1", "-i", img_path, "-i", mp3_path,
        "-vf", vf, "-shortest",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", out_clip,
    ])
    return dur


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest", help="manifest JSON 路径")
    ap.add_argument("-o", "--output", default="final.mp4")
    args = ap.parse_args()

    base = os.path.dirname(os.path.abspath(args.manifest))
    with open(args.manifest, encoding="utf-8") as f:
        cfg = json.load(f)

    voice = cfg.get("voice", "zh-CN-YunyangNeural")
    disclaimer = cfg.get("disclaimer", "")
    disclaimer_file = None
    if disclaimer:
        disclaimer_file = os.path.join(base, "_disclaimer.txt")
        with open(disclaimer_file, "w", encoding="utf-8") as f:
            f.write(disclaimer)

    clips = []
    for i, shot in enumerate(cfg.get("shots", [])):
        img = os.path.join(base, shot["image"])
        text = shot["text"]
        zoom = shot.get("zoom", "in")
        mp3 = os.path.join(base, f"seg{i+1}.mp3")
        vtt = os.path.join(base, f"seg{i+1}.vtt")
        srt = os.path.join(base, f"seg{i+1}.srt")
        clip = os.path.join(base, f"clip{i+1}.mp4")

        print(f"\n=== 镜头 {i+1}/{len(cfg['shots'])} ===")
        gen_audio(text, mp3, vtt, voice)
        vtt_to_srt(vtt, srt)
        dur = build_shot(img, mp3, srt, clip, disclaimer_file, zoom)
        print(f"镜头 {i+1} 完成，时长 {dur:.1f}s")
        clips.append(clip)

    # 拼接（同参数，流拷贝）
    list_file = os.path.join(base, "_concat.txt")
    with open(list_file, "w", encoding="utf-8") as f:
        for c in clips:
            f.write(f"file '{os.path.abspath(c).replace(chr(92), '/')}'\n")
    run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", list_file, "-c", "copy", args.output,
    ])
    print(f"\n✅ 成片已生成：{args.output}")


if __name__ == "__main__":
    main()
