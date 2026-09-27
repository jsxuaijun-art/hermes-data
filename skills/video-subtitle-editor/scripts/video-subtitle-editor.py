#!/usr/bin/env python3
"""
口播视频全功能字幕特效剪辑工具
使用方法: python3 video-subtitle-editor.py <输入视频路径> [输出路径]

默认输出: /tmp/output_final.mp4 (如果D盘可写则输出到 /mnt/d/output_final.mp4)
"""

import os, sys, json, math, random, subprocess, shutil
from pathlib import Path

# ── ffmpeg ──
FFMPEG_BIN = os.path.expanduser("~/.local/bin/ffmpeg")
FFPROBE_BIN = os.path.expanduser("~/.local/bin/ffprobe")
os.environ["IMAGEIO_FFMPEG_EXE"] = FFMPEG_BIN
os.environ["FFMPEG_BINARY"] = FFMPEG_BIN

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoFileClip, CompositeVideoClip, VideoClip
from moviepy.video.fx import FadeIn, FadeOut
from faster_whisper import WhisperModel
from faster_whisper.utils import download_model

# ═══════════════════════════════════════════════
#  配置
# ═══════════════════════════════════════════════
DEFAULT_OUTPUT = "/tmp/output_final.mp4"
# 如果 D 盘可写则用 D 盘
if os.access("/mnt/d/", os.W_OK):
    DEFAULT_OUTPUT = "/mnt/d/output_final.mp4"

INPUT_FILE = sys.argv[1] if len(sys.argv) > 1 else None
OUTPUT_FILE = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUTPUT
WHISPER_MODEL_DIR = "/tmp/whisper_base"

# 字体路径（Windows）
FONT_PATHS = {
    "msyh": "/mnt/c/Windows/Fonts/msyh.ttc",
    "msyhbd": "/mnt/c/Windows/Fonts/msyhbd.ttc",
    "simkai": "/mnt/c/Windows/Fonts/simkai.ttf",
    "simfang": "/mnt/c/Windows/Fonts/simfang.ttf",
    "STSONG": "/mnt/c/Windows/Fonts/STSONG.TTF",
    "STKAITI": "/mnt/c/Windows/Fonts/STKAITI.TTF",
    "STFANGSO": "/mnt/c/Windows/Fonts/STFANGSO.TTF",
}

def get_font(size=36, name="msyh"):
    path = FONT_PATHS.get(name, FONT_PATHS["msyh"])
    if not os.path.exists(path):
        path = FONT_PATHS["msyh"]
    return ImageFont.truetype(path, size)

def hsl_to_rgb(h, s, l):
    h = h % 360
    c = (1 - abs(2*l/255 - 1)) * s/255
    x = c * (1 - abs((h/60) % 2 - 1))
    m = l/255 - c/2
    if h < 60: r,g,b = c,x,0
    elif h < 120: r,g,b = x,c,0
    elif h < 180: r,g,b = 0,c,x
    elif h < 240: r,g,b = 0,x,c
    elif h < 300: r,g,b = x,0,c
    else: r,g,b = c,0,x
    return (int((r+m)*255), int((g+m)*255), int((b+m)*255))

# ═══════════════════════════════════════════════
#  Step 1: 语音转文字
# ═══════════════════════════════════════════════
def transcribe_video(video_path):
    print("🔄 正在转录音频...")
    os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
    _ = download_model("base", output_dir=WHISPER_MODEL_DIR, local_files_only=True)
    model = WhisperModel(WHISPER_MODEL_DIR, device="cpu", compute_type="int8")
    segments, info = model.transcribe(video_path, language="zh", beam_size=5)
    result = []
    for seg in segments:
        result.append({
            "start": seg.start,
            "end": seg.end,
            "text": seg.text.strip()
        })
        print(f"  [{seg.start:.1f}s-{seg.end:.1f}s] {seg.text}")
    return result

# ═══════════════════════════════════════════════
#  字幕效果（8种）
# ═══════════════════════════════════════════════
def _draw(text, font_name, size, colors, stroke, w, h, y_off=0):
    font = get_font(size, font_name)
    img = Image.new("RGBA", (w, h), (0,0,0,0))
    d = ImageDraw.Draw(img)
    bb = d.textbbox((0,0), text, font=font)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]
    bx = (w - tw)//2
    by = h - 150 + y_off
    c0 = colors[0] if not isinstance(colors[0], str) else hex_to_rgb(colors[0])
    if isinstance(stroke, str): stroke = hex_to_rgb(stroke)
    if len(colors) > 1 and len(text) > 1:
        ox = bx
        for i,ch in enumerate(text):
            ci = colors[i % len(colors)]
            if isinstance(ci, str): ci = hex_to_rgb(ci)
            cb = d.textbbox((0,0), ch, font=font)
            d.text((ox, by), ch, font=font, fill=ci, stroke_width=3, stroke_fill=stroke)
            ox += (cb[2]-cb[0])
    else:
        d.text((bx, by), text, font=font, fill=c0, stroke_width=3, stroke_fill=stroke)
    return np.array(img)

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0,2,4))

def _typing(text, s, e, w, h):
    dur = e - s
    def f(t):
        p = min(1, (t-s)/dur) if dur>0 else 1
        v = text[:max(1, int(len(text)*p))]
        return _draw(v, "msyhbd", 52, [(255,255,255)], (0,0,0), w, h)
    return VideoClip(f, duration=dur).with_start(s)

def _gradient(text, s, e, w, h):
    dur = e - s
    cs = [(255,107,107),(255,230,109),(78,205,196)]
    def f(t):
        return _draw(text, "msyhbd", 52, cs, (0,0,0), w, h)
    return VideoClip(f, duration=dur).with_start(s)

def _neon(text, s, e, w, h):
    dur, nc = e - s, [(255,0,255),(0,255,255),(255,102,0)]
    font = get_font(52, "msyhbd")
    def f(t):
        img = Image.new("RGBA", (w,h), (0,0,0,0))
        d = ImageDraw.Draw(img)
        bb = d.textbbox((0,0), text, font=font)
        tw, th = bb[2]-bb[0], bb[3]-bb[1]
        xp, yp = (w - tw)//2, h - 150
        ci = int(t*2) % len(nc)
        glow = nc[ci]
        for i in range(5,0,-1):
            a = max(10, int(50/i))
            d.text((xp-i*2, yp), text, font=font, fill=(*glow,a), stroke_width=i*3, stroke_fill=(*glow,a))
        d.text((xp, yp), text, font=font, fill=(255,255,255), stroke_width=2, stroke_fill=glow)
        return np.array(img)
    return VideoClip(f, duration=dur).with_start(s)

def _bounce(text, s, e, w, h):
    dur = e - s
    font = get_font(52, "msyhbd")
    def f(t):
        p = (t-s)/dur if dur>0 else 0
        img = Image.new("RGBA", (w,h), (0,0,0,0))
        d = ImageDraw.Draw(img)
        bnc = abs(math.sin(p*math.pi*4))*15
        bb = d.textbbox((0,0), text, font=font)
        tw, th = bb[2]-bb[0], bb[3]-bb[1]
        xp, yp = (w - tw)//2, h - 150 - bnc
        d.text((xp+3, yp+3+15), text, font=font, fill=(0,0,0,60))
        hue = int(p*360)%360
        mc = hsl_to_rgb(hue, 255, 153)
        d.text((xp, yp), text, font=font, fill=mc, stroke_width=2, stroke_fill=(0,0,0))
        return np.array(img)
    return VideoClip(f, duration=dur).with_start(s)

def _3d(text, s, e, w, h):
    dur = e - s
    font = get_font(52, "msyhbd")
    def f(t):
        img = Image.new("RGBA", (w,h), (0,0,0,0))
        d = ImageDraw.Draw(img)
        bb = d.textbbox((0,0), text, font=font)
        tw, th = bb[2]-bb[0], bb[3]-bb[1]
        xp, yp = (w - tw)//2, h - 150
        for o in range(8,0,-1): d.text((xp+o,yp+o), text, font=font, fill=(0,0,0,max(10,40-o*4)))
        d.text((xp, yp), text, font=font, fill=(255,215,0), stroke_width=1, stroke_fill=(139,105,20))
        return np.array(img)
    return VideoClip(f, duration=dur).with_start(s)

def _rainbow(text, s, e, w, h):
    dur = e - s
    font = get_font(52, "msyhbd")
    def f(t):
        img = Image.new("RGBA", (w,h), (0,0,0,0))
        d = ImageDraw.Draw(img)
        bb = d.textbbox((0,0), text, font=font)
        tw, th = bb[2]-bb[0], bb[3]-bb[1]
        bx, yp = (w - tw)//2, h - 150
        ox = bx
        for i,ch in enumerate(text):
            hue = int((i/len(text)*360 + t*60)%360)
            clr = hsl_to_rgb(hue, 255, 153)
            cb = d.textbbox((0,0), ch, font=font)
            d.text((ox,yp), ch, font=font, fill=clr, stroke_width=2, stroke_fill=(0,0,0))
            ox += (cb[2]-cb[0])
        return np.array(img)
    return VideoClip(f, duration=dur).with_start(s)

def _glow(text, s, e, w, h):
    dur = e - s
    font, gc = get_font(52, "msyhbd"), [(255,215,0),(255,107,107),(0,255,255),(255,0,255)]
    def f(t):
        img = Image.new("RGBA", (w,h), (0,0,0,0))
        d = ImageDraw.Draw(img)
        bb = d.textbbox((0,0), text, font=font)
        tw, th = bb[2]-bb[0], bb[3]-bb[1]
        xp, yp = (w - tw)//2, h - 150
        br = abs(math.sin(t*2))*0.5+0.5
        glow = gc[int(t*0.5)%len(gc)]
        for i in range(10,0,-2): d.text((xp,yp),text,font=font,fill=(*glow,max(5,int(20*br/i))),stroke_width=i,stroke_fill=(*glow,max(5,int(20*br/i))))
        d.text((xp, yp), text, font=font, fill=(255,255,255), stroke_width=1, stroke_fill=glow)
        return np.array(img)
    return VideoClip(f, duration=dur).with_start(s)

def _shake(text, s, e, w, h):
    dur = e - s
    font, rng = get_font(52, "msyhbd"), random.Random(42)
    def f(t):
        p = (t-s)/dur if dur>0 else 0
        img = Image.new("RGBA", (w,h), (0,0,0,0))
        d = ImageDraw.Draw(img)
        bb = d.textbbox((0,0), text, font=font)
        tw, th = bb[2]-bb[0], bb[3]-bb[1]
        bx, by = (w - tw)//2, h - 150
        if p < 0.3:
            si = int((1-p/0.3)*8)
            ox = rng.randint(-si,si) if si>0 else 0
            oy = rng.randint(-si,si) if si>0 else 0
        else: ox, oy = 0,0
        d.text((bx+ox,by+oy), text, font=font, fill=(min(255,int(255*(1-p*0.3))),100,100), stroke_width=3, stroke_fill=(0,0,0))
        return np.array(img)
    return VideoClip(f, duration=dur).with_start(s)

EFFECTS = [
    ("打字机效果", _typing), ("渐变颜色", _gradient),
    ("霓虹发光", _neon), ("弹跳动效", _bounce),
    ("3D立体", _3d), ("彩虹渐变", _rainbow),
    ("光晕呼吸", _glow), ("抖动强调", _shake),
]

def render_all_subtitles(segs, w, h):
    clips = []
    for i, sg in enumerate(segs):
        name, fn = EFFECTS[i % len(EFFECTS)]
        print(f"  [{i}] → {name}")
        clips.append(fn(sg["text"], sg["start"], sg["end"], w, h))
    return clips

# ═══════════════════════════════════════════════
#  进度条
# ═══════════════════════════════════════════════
def create_progress_bar(duration, w, h):
    bar_y, bar_w, bar_x = h - 40, w - 200, 100
    def f(t):
        img = Image.new("RGBA", (w,h), (0,0,0,0))
        d = ImageDraw.Draw(img)
        p = t/duration if duration>0 else 0
        cw = int(bar_w * p)
        d.rectangle([bar_x,bar_y,bar_x+bar_w,bar_y+6], fill=(255,255,255,40), outline=(255,255,255,60))
        if cw > 0:
            for i in range(cw):
                d.rectangle([bar_x+i,bar_y,bar_x+i+1,bar_y+6], fill=hsl_to_rgb(int(200+(i/bar_w)*80)%360,255,153))
        font = get_font(18, "msyh")
        d.text((bar_x+bar_w+15, bar_y-2), f"{int(t//60):02d}:{int(t%60):02d} / {int(duration//60):02d}:{int(duration%60):02d}", font=font, fill=(255,255,255,180))
        return np.array(img)
    return VideoClip(f, duration=duration)

# ═══════════════════════════════════════════════
#  主函数
# ═══════════════════════════════════════════════
def main():
    if not INPUT_FILE:
        print("❌ 请指定输入视频路径！")
        print(f"用法: python3 {sys.argv[0]} <输入视频> [输出路径]")
        sys.exit(1)
    if not os.path.exists(INPUT_FILE):
        print(f"❌ 视频文件不存在: {INPUT_FILE}")
        sys.exit(1)
    
    print("="*60)
    print("🎬 口播视频全功能剪辑工具 v2.0")
    print("="*60)
    
    print("\n📝 [1/6] 语音识别...")
    segs = transcribe_video(INPUT_FILE)
    if not segs:
        print("❌ 未识别到语音！"); return
    print(f"   共 {len(segs)} 条字幕")
    
    print("\n🎥 [2/6] 加载视频...")
    video = VideoFileClip(INPUT_FILE)
    print(f"   时长: {video.duration:.1f}s  分辨率: {video.w}x{video.h}")
    
    print("\n✨ [3/6] 生成字幕特效...")
    subs = render_all_subtitles(segs, video.w, video.h)
    print(f"   共 {len(subs)} 个特效字幕")
    
    print("\n📊 [4/6] 生成进度条...")
    bar = create_progress_bar(video.duration, video.w, video.h)
    
    print("\n🎬 [5/6] 合成输出...")
    video = video.with_effects([FadeIn(0.5), FadeOut(1.0)])
    from moviepy import CompositeVideoClip
    all_clips = [video] + subs + [bar]
    final = CompositeVideoClip(all_clips, size=(video.w, video.h))
    if final.audio:
        final = final.with_audio(final.audio)
    
    print(f"\n💾 [6/6] 导出 → {OUTPUT_FILE}")
    os.makedirs(os.path.dirname(OUTPUT_FILE) or ".", exist_ok=True)
    final.write_videofile(OUTPUT_FILE, codec="libx264", audio_codec="aac",
                          fps=30, preset="medium", ffmpeg_params=["-crf","22"],
                          threads=4, logger=None)
    sz = os.path.getsize(OUTPUT_FILE)/1024/1024
    print(f"\n✅ 完成！{OUTPUT_FILE}  ({sz:.1f} MB)")

if __name__ == "__main__":
    main()
