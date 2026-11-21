# 抖音视频素材 → 公众号文章 完整工作流

## 场景
用户给抖音分享链接（如 `https://v.douyin.com/kNEDBLNusLY/`），要求据此创作公众号文章。
素材类型：抖音短视频（区别于视频号/YouTube，需单独流程获取内容）。

## 1. 解析短链接拿视频ID
```bash
curl -s -o /dev/null -w "%{url_effective}\n" -L "https://v.douyin.com/XXXX/" \
  -A "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) ... Safari/604.1"
# → https://www.douyin.com/video/<VIDEO_ID>
```

## 2. 打开视频页拿完整信息
`browser_navigate` 直接访问 `https://www.douyin.com/video/<VIDEO_ID>`（比 iesdouyin 分享页更稳）。
页面渲染后可见：标题 h1、点赞/评论/收藏/转发数、发布时间、评论区、"大家都在搜"。
注意：未登录访问会被重定向到精选页+登录墙，多试一次带完整参数的分享链接或直接 /video/<ID> 路径。

## 3. 页面内 fetch API 拿结构化数据（关键）
在 browser_console 里执行（页面内 fetch 带 cookie，成功率远高于外部 curl）：
```js
await fetch('/aweme/v1/web/aweme/detail/?aweme_id=<VIDEO_ID>&aid=6383&version_name=23.5.0', {headers:{'Accept':'application/json'}}).then(r=>r.json())
```
返回 `aweme_detail`：`desc`（标题）、`author.nickname`、`author.account_cert_info`（官方认证信息！如"国家税务总局税收宣传中心"）、`create_time`、`statistics`（digg/comment/collect/share）、`text_extra`（话题）、`video.duration`（毫秒）。
⚠️ 判断素材权威性时看 author 认证，官方账号内容可放心引用。

## 4. 下载视频 + 转写口播（创作依据）
- 视频 URL：browser_console 里 `document.querySelector('video').currentSrc`
- 下载：`curl -L "<url>" -H "Referer: https://www.douyin.com/"`（必须带 Referer）
- 提音频 + 转写（WSL 无 ffmpeg 且 sudo 要密码时的免 sudo 方案）：
```bash
python3 -m venv /tmp/whisper-venv
PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple /tmp/whisper-venv/bin/pip install faster-whisper imageio-ffmpeg
FFMPEG=$(/tmp/whisper-venv/bin/python -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())")
"$FFMPEG" -y -i v.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 a.wav
# 转写脚本：
from faster_whisper import WhisperModel
m = WhisperModel("small", device="cpu", compute_type="int8")
segments, info = m.transcribe("a.wav", language="zh", vad_filter=True, initial_prompt="以下是税务合规科普视频字幕。")
```
`imageio-ffmpeg` 自带 johnvansickle 静态 ffmpeg 二进制，无需 sudo 安装系统 ffmpeg。

## 5. 封面图：官方视频抽帧（AI图乱码时的最佳方案）
- **AI 生成中文场景图（chudian `image-01`）通病**：画面文字全是乱码（"未用草""夫宝及旅"之类），不适合正式封面。提示词加"墙上没有文字和标志"可减少但仍无法根除。
- **推荐方案：从官方视频抽帧裁剪** —— 绝对原创、绝对贴题、绝不重复（满足配图铁律）：
```bash
FFMPEG -ss 60 -i v.mp4 -frames:v 1 -q:v 1 frame.jpg   # 抽多个时间点选最佳
FFMPEG -y -i frame.jpg -vf "crop=1080:608:0:420" -q:v 2 cover.jpg  # 竖屏1080x1920裁横版
```
- 选帧依据：用视觉模型确认画面内容（本机主模型无 vision 时，直连 chudian API 视觉模型，见 scripts 说明）。
- 本例成果：用官方视频第60秒《发票管理办法》第二十一条法规原文画面（蓝底白字政务风）做封面，完美贴合"虚开发票"主题。

## 6. chudian 图像生成 API（备用方案）
```bash
curl -s https://llm.chudian.site/v1/images/generations \
  -H "Authorization: Bearer $API_KEY" -H "Content-Type: application/json" \
  -d '{"model":"image-01","prompt":"中国办税服务大厅，蓝色制服工作人员...","size":"1024x1024","n":5}'
```
返回 OSS URL 列表，直接 curl 下载。API key 从 `~/.hermes/config.yaml` 的 `api_key` 字段取。

## 铁律关联
- 封面/配图必须全新、主题相关、段落严格对应（见 SKILL.md「第2步：配图」铁律）
- 严禁 AI 幻觉：文章事实以转写稿为准，政策条文引用官方视频原文（如《发票管理办法》第二十一条），不确定不写
