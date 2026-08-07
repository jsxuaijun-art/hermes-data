# WSL 视频/音频转写流水线（中国网络环境实测通过 2026.7.31）

用户经常把短视频成片（mp4）或文案（docx）放在 **D:\OneDrive\Desktop**（即 `/mnt/d/OneDrive/Desktop/`），要求读取内容。docx 直接 python-docx 读；mp4 需要抽音轨 + whisper 转写。

## 一键路径速查

```
D:\OneDrive\Desktop\xxx.mp4  →  /mnt/d/OneDrive/Desktop/xxx.mp4
venv:        /tmp/videnv
ffmpeg 二进制: /tmp/videnv/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2
音频:        /tmp/video_audio.wav
```

## 环境前提（已踩过的坑，直接照做）

1. **系统没有 ffmpeg/ffprobe**（`command not found`）→ 不要 apt install（慢且权限麻烦），用 `imageio-ffmpeg` pip 包自带的静态 ffmpeg 二进制，功能完整（抽音轨、读元信息都够）。
2. **系统 pip 被 PEP 668 拦**（`externally-managed-environment`）→ 必须建 venv：
   ```bash
   python3 -m venv /tmp/videnv
   /tmp/videnv/bin/pip install ... 
   ```
   不要用 `--break-system-packages`（污染系统环境）。
3. **files.pythonhosted.org 超时**（Read timed out）→ pip 必须走清华镜像：
   ```bash
   /tmp/videnv/bin/pip install imageio-ffmpeg faster-whisper -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```
4. **HuggingFace 直连 Network unreachable** → 必须设 `HF_ENDPOINT=https://hf-mirror.com`。
5. **hf-mirror 走 xet 协议报 401**（`cas-server.xethub.hf.co ... 401 Unauthorized`）→ 追加 `HF_HUB_DISABLE_XET=1` 强制普通 HTTP 下载。这是最容易卡住的坑。
6. **模型大小与超时**：`small` 约 464MB，国内镜像下载也超 600s 命令超时；`base` 约 74MB，~115s 加载完成，中文可用。**默认用 base**，只有 base 质量明显不够时才试 small（放 background + notify_on_complete）。
   - faster-whisper 模型缓存在 `~/.cache/huggingface/hub/`，下过一次以后复用（`du -sh` 可见 464M 说明 small 已部分/全部落地）。

## 完整命令序列（实测通过）

```bash
# 1. 建 venv + 装包（清华镜像）
python3 -m venv /tmp/videnv
/tmp/videnv/bin/pip install imageio-ffmpeg faster-whisper -i https://pypi.tuna.tsinghua.edu.cn/simple

# 2. 读视频元信息（时长/分辨率/音轨）
FFMPEG=/tmp/videnv/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2
"$FFMPEG" -i "/mnt/d/OneDrive/Desktop/xxx.mp4" 2>&1 | grep -E "Duration|Stream"

# 3. 抽音轨（单声道 16k wav，whisper 友好）
"$FFMPEG" -y -i "/mnt/d/OneDrive/Desktop/xxx.mp4" -vn -ac 1 -ar 16000 /tmp/video_audio.wav

# 4. 转写（hf-mirror + 禁 xet + base 模型 CPU int8）
cd /tmp && HF_ENDPOINT=https://hf-mirror.com HF_HUB_DISABLE_XET=1 /tmp/videnv/bin/python -c "
from faster_whisper import WhisperModel
model = WhisperModel('base', device='cpu', compute_type='int8')
segments, info = model.transcribe('/tmp/video_audio.wav', language='zh', beam_size=5)
for seg in segments:
    print(f'[{seg.start:.1f}-{seg.end:.1f}] {seg.text}')
"
```

## 已知局限

- **base 模型对粤语口音/方言识别有误差**：本会话把「广东深圳华侨电子厂」听成「广东东管运连鞋场」、「黄桥生」听成「黄巧声」。剧情走向能还原，但关键名词（厂名、人名、公司名）要结合用户提供的 docx 文案核对——**成片通常对应 docx 的某一版**，用转写文本 + docx 对比即可确定拍的是哪版（开头有无铺垫、结尾是否留白等）。
- 3 分钟视频 base 转写约 1-2 分钟（CPU），可接受；更长的视频建议 small 模型放后台。

## docx 文案读取

```bash
python3 -c "
from docx import Document
doc = Document('/mnt/d/OneDrive/Desktop/xxx.docx')
for p in doc.paragraphs:
    if p.text.strip(): print(p.text)
"
```
对比多个版本（如「新文案.docx」vs「新文案 - 副本.docx」）时注意文件名里的修改时间（`ls -la`），副本通常是用户最新改的版本。
