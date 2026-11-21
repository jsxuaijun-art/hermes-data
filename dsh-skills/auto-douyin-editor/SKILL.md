---
name: auto-douyin-editor
version: "1.1.0"
description: "抖音口播短视频自动剪辑 Skill — 基于样本视频拆解的规律，自动将素材+文案剪辑成抖音风格竖屏口播视频"
author: "WorkBuddy Agent"
created: "2026-08-01"
tags: [video-editing, douyin, short-video, ffmpeg, automation]
trigger: 用户提到"自动剪辑""抖音剪辑""口播视频""按这个风格剪""帮我剪视频"等
agent_created: true
---

# 抖音口播短视频 — 自动剪辑 Skill

> 基于「剪辑样本.mp4」拆解出的可复用剪辑模板，适用于知识/资讯类口播短视频。

## 适用场景

- 知识科普 / 资讯解读 / 读书分享类竖屏短视频
- 主持人出镜 + 口播 + 文字叠加 + 弹幕评论
- 目标平台：抖音、视频号、快手等竖屏短内容平台
- **不适用于**: Vlog、剧情片、MV、产品展示等其他类型

### 与其他 skill 的分工（先判断再动手）

| 需求 | 用哪个 |
|------|--------|
| 有**真人口播素材**，要剪成竖屏抖音风 | **本 skill** |
| 无素材，要 **AI 生图 + 配音**做横屏漫画风科普片 | `comic-explainer-video` |
| 只要**文案/选题/涨粉算法**方法论 | Hermes 的 `short-video-copywriting`（含高赞泛粉与精准流量校准） |

**文案叙事结构库 T1–T6**（颠覆认知／趋势解释／反向机会／实用指南／人物故事／清单盘点）
统一维护在 `comic-explainer-video/references/methodology.md`，**本 skill 不复制一份**，需要时直接引用。

---

## 一、输出规格（固定参数）

| 参数 | 值 |
|------|-----|
| 分辨率 | **720 × 1584** (9:20 竖屏) |
| 帧率 | **30 fps** (恒定) |
| 视频编码 | H.264, CRF **18–20** |
| 音频编码 | AAC, **128 kbps**, 48kHz, 立体声 |
| 封装格式 | MP4 |
| 总时长 | **45–60 秒**（推荐 52s 左右） |
| 像素宽高比 | 方形像素 (1:1) |

---

## 二、五段式结构模板（核心规律）

```
时间轴:
[0s]═════════[15s]══[17s]═══════════[42s]═[44s]═════[53s]
 │ A. 钩子段   │ B.  │ C. 主体段      │ D.  │ E. 收尾段 │
 │ 14-16s(30%)│ 对比│ 24-26s(48%)    │ 转场│ 8-11s(16%)│
 └────────────┘ 2-3s └───────────────┘ 1-2s └──────────┘
```

### A 段：开场钩子（0 – ~15s）

**目的**: 前 3 秒抓住注意力，建立人设

**要求**:
- 必须以**问题/冲突/反常识陈述**开头（不要"大家好我是XX"）
- 示例：「诸君 你知道中国第一高楼在哪吗」「你绝对想不到...」
- 主造型 + 主背景画面
- 第 1 条大字文案在 0–3s 内出现

### B 段：对比插片（~15 – ~17s）

**目的**: 打破视觉单调，增加信息层次

**要求**:
- **换装或换背景**（二选一，最好都换）
- 内容上做对比/转折（"而更魔幻的是..."）
- 时长严格控制在 **2–3 秒**
- 配合一条过渡性大字文案

### C 段：主体内容（~17 – ~42s）

**目的**: 核心价值交付，建立信任感

**要求**:
- 回归主造型 + 主背景
- 信息密度最高的一段
- 开始出现**悬浮弹幕评论**（每 5–10s 一条）
- 大字文案每 4–8s 出现一条
- 底部字幕全程跟随

### D 段：转场特效（~42 – ~44s）

**目的**: 节奏转折信号，预告收尾

**要求**:
- 时长 **1–2 秒**
- 使用快速连切（3–6 次/秒内）或闪白/缩放转场
- 可配合亮度压暗效果

### E 段：收尾蒙太奇（~44 – ~53s）

**目的**: 升华主题，引导互动

**要求**:
- 每 2–3 秒切换一个背景画面（至少 3 个不同背景）
- 金句/行动号召作为最后一句文案
- 最后 1–2 秒可留 Logo 或关注引导画面

---

## 三、文字系统规范

### 3.1 核心大字（第 1 层）

```
位置:    画面垂直 55%–65%（中下部）
字号:    画面宽度 28%–33%
字体:    黑体/思源黑体 Bold
颜色:    白色 #FFFFFF
描边:    黑色 #000000, 3–4px
阴影:    可选, 2px blur
动画:    从下淡入 (fadeInUp), 0.3s ease-out
停留:    与对应语音等长（通常 2–4s）
对齐:    居中
最大行数: 2 行
```

**出现时机**: 与语音中的关键词/金句同步，每段 3–6 条。

### 3.2 底部字幕（第 2 层）

```
位置:    画面底部 18%–22%
字号:    画面宽度 5%–6%
字体:    思源黑体 Regular
颜色:    白色 #FFFFFF
背景:    半透明黑 rgba(0,0,0,0.5), 圆角
内边距:  左右 4%, 上下 2%
动画:    淡入淡出, 与语音句子同步
行高:    1.4
安全区:  不遮挡底部 UI 栏
```

### 3.3 悬浮弹幕（第 3 层）

```
位置:    画面上部 10%–35%（随机偏移）
字号:    画面宽度 4%–5%
颜色:    白色 或 彩色（模拟不同用户）
背景:    半透明深色 rgba(0,0,0,0.45)
样式:    圆角胶囊形
动画:    左右滑入 + 停留 3–5s + 淡出
频率:    C 段开始后每 5–10s 出现 1 条
数量:    全程 4–7 条
内容类型: 夸赞/提问/感叹/地域认同（如"深圳人报道！""讲得太好了👍"）
注意:    绝不遮挡主持人面部核心区域
```

---

## 四、UI 外框规范（模拟播放器界面）

> 如果需要生成带 UI 外框的成品，在视频上层叠加以下元素：

### 4.1 顶部栏
```
左侧: 返回键 "<"
中间: 进度条 (00:00 → 总时长)
右侧: 时间戳 + 倍速标识
最顶: 手机状态栏 (时间/电量/信号/5G)
高度: 占画面顶部 6–8%
透明度: 70–85%
```

### 4.2 底部互动栏
```
高度: 占画面底部 12–15%
元素从左到右:
  1. 圆形头像 (主播)
  2. 昵称 + "关注" 按钮
  3. 点赞数 (万为单位)
  4. 转发数
  5. 收藏数
  6. 评论数
浮动 CTA (可选): 直播预告横幅 + 预约按钮
```

---

## 五、ffmpeg 剪辑命令参考

### 5.1 基础输出命令

```bash
# 输出标准抖音竖屏视频
ffmpeg -y -i input.mp4 \
  -vf "scale=720:1584:force_original_aspect_ratio=decrease,pad=720:1584:(ow-iw)/2:(oh-ih)/2:black,fps=30" \
  -c:v libx264 -preset medium -crf 18 \
  -c:a aac -b:a 128k -ar 48000 -ac 2 \
  -movflags +faststart \
  output.mp4
```

### 5.2 字幕叠加（ASS 格式）

```bash
# 使用 ASS 字幕文件实现多层文字
ffmpeg -y -i video.mp4 -vf "ass=subtitles.ass" -c:v libx264 -crf 18 -c:a copy output.mp4
```

ASS 字幕模板示例（核心大字）：
```ass
[Script Info]
Title: Douyin Overlay
PlayResX: 720
PlayResY: 1584

[V4+Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Default,Microsoft YaHei Bold,200,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,2,40,40,400,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL,MarginR,MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:04.50,Default,,0,0,0,,{\an5\fad(200,100)}诸君 你知道中国第一高楼
```

### 5.3 多段拼接

```bash
# 先创建 concat 列表文件
cat > files.txt << 'EOF'
file 'segment_a.mp4'
file 'segment_b.mp4'
file 'segment_c.mp4'
file 'segment_d.mp4'
file 'segment_e.mp4'
EOF

# 安全拼接（需统一规格）
ffmpeg -y -f concat -safe 0 -i files.txt -c copy output.mp4
```

### 5.4 转场特效

```bash
# 快速闪白转场（D 段用）
ffmpeg -y -i input.mp4 -vf "tpad=start_duration=0.5:start_mode=color:color=white,fade=t=in:st=0:d=0.3" ...

# 缩放转场
ffmpeg -y -i input.mp4 -vf "zoompan=z='min(zoom+0.001,1.5)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=720x1584:fps=30" ...
```

---

## 六、自动剪辑工作流

当用户提供新素材时，按以下步骤执行：

### Step 1: 分析输入
```bash
# 1. 获取视频信息
ffprobe -v error -show_format -show_streams -print_format json INPUT_VIDEO > probe.json

# 2. 场景切点检测
ffmpeg -i INPUT_VIDEO -filter:v "select='gt(scene,0.15)',showinfo" -f null - 2>&1 | grep pts_time

# 3. 抽帧预览（每 2.5 秒一帧，拼成总览图）
ffmpeg -i INPUT_VIDEO -vf "fps=1/2.6,scale=200:-1,tile=10x2" -frames:v 1 preview.jpg
```

### Step 2: 语音 & 时间轴

**分两种情况，不要一律上 whisper：**

**情况 A（首选，已验证）——文案已有／需要新配音**：用 `edge-tts` 直接生成音频 **并同时导出 SRT 时间戳**，
跳过语音识别整环。时间轴天然精确，无需对齐。
```bash
edge-tts --voice zh-CN-YunxiNeural --text-file script.txt \
         --write-media audio.mp3 --write-subtitles audio.srt
```

**情况 B——必须从已有真人素材里扒文案**：才用 whisper。
```bash
ffmpeg -i INPUT_VIDEO -vn -acodec pcm_s16le -ar 16000 -ac 1 audio.wav
whisper audio.wav --language zh --model small --output_format srt --word_timestamps
```
> ⚠️ 实测 **faster-whisper 会因 HuggingFace 网络不通直接失败**（模型下载卡死）。
> 若环境无法访问 HF，走情况 A 或改用已缓存模型的 whisper.cpp。

### Step 3: 结构规划
根据五段式模板，将文案分配到 A/B/C/D/E 五个段落：
- A 段: 前 14–16s 的文案 → 提炼钩子问题
- B 段: 找一个适合做对比的句子（2–3s）
- C 段: 中间 24–26s 的主体内容
- D 段: 转折句（1–2s）
- E 段: 结尾金句 + 行动号召（8–11s）

### Step 4: 生成字幕文件
基于 Step 2 的时间轴数据，生成三层 ASS 字幕：
1. 核心大字（从文案中提炼 5–8 条关键句）
2. 底部完整字幕（逐句）
3. 弹幕评论（根据内容生成 4–7 条相关评论）

### Step 5: 合成输出
```bash
# 叠加字幕到视频
ffmpeg -y -i INPUT_VIDEO \
  -vf "ass=overlay.ass,scale=720:1584,fps=30" \
  -c:v libx264 -preset medium -crf 18 \
  -c:a aac -b:a 128k -ar 48000 -ac 2 \
  -movflags +faststart \
  OUTPUT_FINAL.mp4
```

### Step 6: 校验
```bash
# 检查输出规格
ffprobe -v error -show_format -show_streams OUTPUT_FINAL.mp4
# 确认: 分辨率 720x1584, 时长 45-60s, 编码 H.264+AAC
```

---

## 七、输入要求

用户需要提供：

| 必须 | 可选 |
|------|------|
| 口播原始视频（主持人出镜说话） | 背景图片/视频素材（用于替换背景） |
| — | 文案文本（如有，可加速处理） |
| — | 弹幕评论内容（可 AI 自动生成） |

**最低门槛**: 只需要一个口播视频文件，其余均可自动生成。

---

## 八、已验证的踩坑（2026-08-01 端到端实测，务必先看）

> 来源：「蝎子毒液」demo 实跑（720×1584 / 58s / 1.3MB / H.264 CRF18 + AAC 128k，管线跑通）。
> 这几条每一条都会让合成静默失败或渲染出错，**不要重踩**。

1. **ffmpeg `ass` 滤镜在 Windows 上对长路径有 bug** —— 会把 `original_size` 解析错，画面比例全乱。
   → **必须 `cd` 到工作目录后用相对路径**（`-vf "ass=overlay.ass"`），不要传绝对长路径。
2. **libass 不支持 ASS 的 `\move()` 标签** —— 不报错，直接把 `{\move(...)}` 当**普通文本渲染到画面上**。
   → 弹幕位移改用 **`MarginV` 定位 + `\fad()` 淡入淡出** 实现（见 3.3 节）。
3. **Python `subprocess` 把路径传给 ffmpeg 的 `ass` 滤镜会出问题**（转义层数对不上）。
   → 合成这一步**直接用 bash 执行 ffmpeg**，Python 只负责生成 `.ass` 文件。
4. **语音识别别默认用 faster-whisper** —— HuggingFace 不通时会卡死，见 Step 2 情况 A/B。

**验证标准**：不要凭"命令没报错"就宣布完成。必须 `ffprobe` 确认分辨率／时长／编码，并**实际播放一遍**看
三层文字是否都正常渲染（尤其检查有没有把 ASS 标签当文本画出来）。

---

## 九、注意事项

1. **安全区**: 重要文字和人物面部保持在画面中心 60% 区域内（各边留 20% 安全区给手机 UI 元素）
2. **文字密度**: 单帧文字不超过画面面积的 25%，避免视觉过载
3. **音频一致性**: 如多段拼接，确保各段音频音量一致（ normalization 到 -16 LUFS）
4. **版权**: 背景素材和字体需确认可商用
5. **适配**: 同一模板可微调适配视频号（9:16 = 1080×1920）和快手
