---
name: video-subtitle-editor
description: 全功能口播视频(口播视频)字幕特效编辑工具。使用语音识别(faster-whisper)将视频语音转为字幕，自动应用8种轮播动态特效(打字机/渐变/霓虹/弹跳/3D立体/彩虹/光晕/抖动)，合成进度条和淡入淡出效果。使用场景：(1)给口播视频添加个性化动态字幕 (2)制作带特效的社交媒体短视频 (3)批量处理口播素材。触发词包括但不限于：口播、字幕、视频剪辑、subtitle、特效字幕。
---

# 口播视频字幕特效编辑器

## 工作流程

使用 `scripts/video-subtitle-editor.py` 脚本处理口播视频。

### 环境依赖（仅需一次安装）

```bash
# 安装依赖
pip3 install moviepy faster-whisper opencv-python-headless Pillow numpy

# 下载 ffmpeg（脚本自动使用）
# 如无法访问外网，从镜像站下载 ffmpeg
wget -q --show-progress "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-n7.1-linux64-gpl-7.1.tar.xz" -O /tmp/ffmpeg.tar.xz
tar -xf /tmp/ffmpeg.tar.xz -C /tmp/
cp /tmp/ffmpeg-n7.1-linux64-gpl-7.1/bin/ffmpeg /tmp/ffmpeg-n7.1-linux64-gpl-7.1/bin/ffprobe ~/.local/bin/
chmod +x ~/.local/bin/ffmpeg ~/.local/bin/ffprobe

# 下载 whisper 模型（首次使用）
export HF_ENDPOINT=https://hf-mirror.com
python3 -c "from faster_whisper.utils import download_model; download_model('base', output_dir='/tmp/whisper_base')"
```

### 使用命令

```bash
# 基本用法
python3 scripts/video-subtitle-editor.py <输入视频路径> [输出路径]

# 示例：处理口播视频，输出到 /tmp
python3 scripts/video-subtitle-editor.py /path/to/koubo.mp4 /tmp/output.mp4
```

如果未指定输出路径，默认输出到 `/tmp/output_final.mp4`。

## 8 种字幕特效（按轮播顺序）

| 序号 | 特效名称 | 描述 |
|------|---------|------|
| 1 | 打字机效果 | 文字逐字出现，常用于开场 |
| 2 | 渐变颜色 | 三色渐变（红→黄→青） |
| 3 | 霓虹发光 | 彩色霓虹灯管效果，颜色循环变化 |
| 4 | 弹跳动效 | 文字上下弹跳，色相随进度变化 |
| 5 | 3D立体 | 金色立体阴影层次感 |
| 6 | 彩虹渐变 | 逐字彩虹色流动 |
| 7 | 光晕呼吸 | 光晕呼吸式脉动发光 |
| 8 | 抖动强调 | 前30%抖动，红色强调 |

每条字幕依次轮换使用不同的特效。

## 附加组件

- **进度条**：底部动态渐变进度条，显示当前时间/总时间
- **淡入淡出**：视频开头0.5s淡入，结尾1s淡出

## 输出格式

- 视频编码：H.264
- 音频编码：AAC
- 分辨率：与原视频一致
- 帧率：30fps
- 品质：CRF 22

## Windows/WSL 注意事项

1. **D 盘输出**：WSL 中 `/mnt/d/` 通常是只读的，输出建议先放到 `/tmp/`，然后手动复制
2. **字体**：脚本自动使用 Windows 字体 `/mnt/c/Windows/Fonts/` 下的微软雅黑等
3. **Whisper 模型下载**：如遇网络问题，设置 `HF_ENDPOINT=https://hf-mirror.com` 使用镜像
4. **ffmpeg**：脚本优先使用 `~/.local/bin/ffmpeg`，如不存在则尝试系统路径
5. **Windows Python**：建议在 WSL 内运行（Python 3.10-3.12），Windows 本机 Python 3.14 可能因依赖兼容性问题无法直接安装

## 文件结构

```
video-subtitle-editor/
├── SKILL.md
└── scripts/
    └── video-subtitle-editor.py
```

## 已知限制

- 仅支持中文语音识别（whisper base模型）
- 字幕位置固定（底部居中）
- 每条字幕分配一种特效（轮播），不可手动指定
- 需要 Python 3.8+ 环境（推荐 3.10-3.12）
- 处理长视频（>10分钟）时内存消耗较大

## 故障排除

- **"No module named 'moviepy'"** → 运行 `pip3 install moviepy`
- **ffmpeg 找不到** → 检查 `~/.local/bin/ffmpeg` 是否存在，或设置环境变量
- **Whisper 模型下载失败** → 设置 `HF_ENDPOINT=https://hf-mirror.com`
- **输出文件损坏** → 检查磁盘空间，尝试降低 CRF 值（如 `-crf 28`）
