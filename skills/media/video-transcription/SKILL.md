---
name: video-transcription
description: 把本地视频/音频（mp4/mov/wav/mp3）转成文字稿。适用于分析竞品短视频、同行发布的视频内容、口播素材。含中国网络环境下的模型镜像加速方案。
tags:
  - 视频转写
  - 语音识别
  - 转录
  - ffmpeg
  - whisper
  - 竞品分析
---

# 本地视频/音频转文字稿

## 触发场景
- 用户发来一个 .mp4/.mov（本地视频），想了解视频里说了什么（尤其用户是做财税内容运营的，常分析竞品、同行、渠道发布的短视频）
- 需要把一段口播/访谈音频转成可检索、可改写、可对照文案的文字稿
- 想从抖音/视频号下载的视频里提取台词，用于改写创作

## 前置判断：先查 ffmpeg/ffprobe 是否可用
```bash
which ffprobe ffmpeg
```
WSL 上可能都没有。**不要先去装系统级 ffmpeg**（apt 源慢且可能污染环境）。
最省事的方案：用 `imageio-ffmpeg` 自带的静态 ffmpeg 二进制。

### 环境准备（已验证 2026.7，中国网络）
1. 建一个独立 venv（避免 PEP 668 报错，系统 pip 装第三方包会被拒）：
   ```bash
   python3 -m venv /tmp/videnv
   ```
2. 装 imageio-ffmpeg（自带 ffmpeg 可执行文件）。**国际 PyPI 可能超时，用清华镜像**：
   ```bash
   /tmp/videnv/bin/pip install imageio-ffmpeg -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```
3. 定位 ffmpeg 可执行文件：
   ```bash
   FFMPEG=/tmp/videnv/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2
   ```

## 第1步：读取视频元信息
```bash
"$FFMPEG" -i "file.mp4" 2>&1 | grep -E "Duration|Stream|Video|Audio"
```
会输出：时长、分辨率、帧率、是否竖屏（1080x1920=短视频竖屏）、音轨编码。

## 第2步：抽音频（把视频音轨转成 whisper 能吃的 wav）
```bash
"$FFMPEG" -y -i "file.mp4" -vn -ac 1 -ar 16000 /tmp/video_audio.wav
```
- `-vn` 丢弃视频轨只留音频，3分钟短视频抽出约5MB wav，几秒完成
- `-ac 1 -ar 16000` 单声道16kHz，whisper 的标准输入

## 第3步：装 faster-whisper 并转写
```bash
/tmp/videnv/bin/pip install faster-whisper -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### ⚠️ 中国网络关键坑：模型从 HuggingFace 下载会失败
直接 `WhisperModel('small')` 会报 `Network is unreachable` 或走 xet 协议报 401。
**必须设环境变量走 hf-mirror 镜像 + 禁用 xet**：
```bash
HF_ENDPOINT=https://hf-mirror.com HF_HUB_DISABLE_XET=1 /tmp/videnv/bin/python -c "
from faster_whisper import WhisperModel
model = WhisperModel('base', device='cpu', compute_type='int8')  # base 约74MB，small 约464MB
segments, info = model.transcribe('/tmp/video_audio.wav', language='zh', beam_size=5)
for seg in segments:
    print(f'[{seg.start:.1f}-{seg.end:.1f}] {seg.text}')
"
```
- 模型会缓存到 `~/.cache/huggingface/`，第二次以后不再下载
- `small` 准确度比 `base` 明显高，但首次下载大且慢，**若 base 够用先用 base**，或先 base 兜底再考虑 small
- 转写 3 分钟音频：base 约 2 分钟（含模型加载），small 更快但因为下载可能卡
- **行业术语提示（已验证有效）**：财税/医疗/法律等垂直领域视频，`transcribe` 时加 `initial_prompt="以下是税务合规科普视频字幕。"` 这类领域提示 + `vad_filter=True`，能明显减少专有名词错字（如"虚开发票""税额"）

## 第4步：校验转写准确性
- 对白/方言转写会有误差（尤其粤语、口音、行业专名）。实测「华侨电子厂」被听成「运连鞋场」。
- 转写结果要结合视频画面/已知文案判断，不能把 whisper 的错字当事实引用。
- 若用户已有对应文案/脚本，直接对比成片和脚本的出入（这本身就是常见需求：看拍出来的和写的有啥差别）。

## 输出
- 转写结果带时间戳 `[起-止]`，方便对齐画面
- 可写入 .md 交付，或继续用于改写创作 / 竞品分析

## 相关
- 若视频是 YouTube 链接，用 `youtube-content` skill 直接拿字幕，无需本流程
- 若需把转写稿加工成短视频文案，参考 `social-media/short-video-copywriting` 等 skill
