---
name: sph-video-downloader
description: 下载微信视频号(weixin.qq.com/sph/)链接的无水印视频，并可选用 faster-whisper 做中文语音转写提取口播文案。This skill should be used when the user pastes a 视频号 link and wants a watermark-free mp4 download or its transcript.
agent_created: true
---

# 视频号（微信）视频下载 + 文案提取 技能

> 适用：WorkBuddy / 任意能跑 Python 的环境。目的：把一条微信视频号链接，变成「无水印 mp4」+「口播原文案」。
> 作者实战验证于 Windows + WorkBuddy。已成功下载多条视频号并做中文语音转写。

---

## 一、原理（先讲清楚为什么这么干）

微信视频号的网页分享链接形如 `https://weixin.qq.com/sph/XXXXXXXX`，**网页本身不暴露直链**，且需要登录态才能看到视频地址。自己逆向成本高、易失效。实战里走的是 **奇云 API（qyapi.ipaybuy.cn）**：

1. **解析层**：把视频号链接作为 `url` 参数，连同 `appId` + `appKey`，GET 请求 `https://qyapi.ipaybuy.cn/api/sph_parse`。返回 JSON，`data` 里关键字段：
   - `mediaUrl`：**无加密直链**（优先，可直接下载/在线看）
   - `video_url`：加密直链（部分视频 `mediaUrl` 为空时回退用它，格式 `finder.video.qq.com/...`，实测可直接下）
   - `title`：发布**描述文案**（作者配文，不是口播逐字稿）
   - `cover_url`：封面图
2. **下载层**：直链是普通 HTTPS 文件，用 `urllib` 或 `curl` 直接拉即可，无需任何登录态（下载时带 `Referer: https://weixin.qq.com/` 更稳）。
3. **文案层（可选）**：视频号接口**不返回口播逐字稿**。要拿口播文案，只能先下视频，再做**语音转文字（ASR）**。中文用 `faster-whisper`（比 openai-whisper 快、不依赖 torch）。

> 关键点：奇云返回 `title`（作者配文），但**口播逐字稿**必须靠 ASR 自己转。

---

## 二、计费（奇云）

- 奇云按官网套餐计费，使用前请确认账号已购套餐 / 余额充足。
- 额度/余额不足会返回非 200（如 `code != 200`），返回 `msg` 里会有提示，按提示去 https://qyapi.ipaybuy.cn 处理即可。
- （历史参考：曾用 redfox 方案为 0.6 积分/次、100 元=1000 积分，已弃用，仅作对比。）

---

## 三、前置条件

1. **奇云 AppId + AppKey**（在 https://qyapi.ipaybuy.cn 官网注册获取）
   - 用法：设环境变量 `QIYUN_APP_ID` 与 `QIYUN_APP_KEY`，或填进 `parse_download.py` 顶部常量。
2. **Python 3.12+**（WorkBuddy 自带隔离 Python 即可）。
3. **联网**：能直连 `qyapi.ipaybuy.cn` 与 `modelscope.cn`（见第六节坑点，HuggingFace 被墙）。
4. **ASR 额外依赖**（仅提取文案时需要）：`faster-whisper`、`imageio-ffmpeg`、`modelscope`。

---

## 四、工作过程

### 方式 A：只下载视频（最常见）
```
用户给链接
  → 调奇云 sph_parse 接口拿 mediaUrl / video_url（无水印直链）
  → 下载直链到本地 mp4
  → 把直链 + 文件路径回给用户
```
耗时：解析 <3s，下载按文件大小（几 MB~几十 MB）几十秒。

### 方式 B：下载 + 提取口播文案
```
下载视频（方式A）
  → 用 faster-whisper 对视频做中文语音转写
  → 输出按时间轴的逐句文案
  → 人工/AI 校正 ASR 术语错误，给「纯净完整文案」
```
耗时：模型首次下载 1.5GB（一次性），CPU 转写 1 分钟视频约 5 分钟。

---

## 五、完整脚本（位于本技能 scripts/ 目录）

### 1) parse_download.py —— 解析 + 下载（一体化）
```python
import os, sys, json, urllib.request, urllib.error, urllib.parse

# 清空本地代理，避免被 127.0.0.1:7890 等死代理拦截（见第六节）
for _k in ("HTTPS_PROXY","HTTP_PROXY","ALL_PROXY","https_proxy","http_proxy","all_proxy"):
    os.environ.pop(_k, None)

API_URL = "https://qyapi.ipaybuy.cn/api/sph_parse"
APP_ID = os.environ.get("QIYUN_APP_ID", "在此填入你的AppId")
APP_KEY = os.environ.get("QIYUN_APP_KEY", "在此填入你的AppKey")

def main():
    if len(sys.argv) < 2:
        print("用法: python parse_download.py <视频号链接> [输出mp4路径]")
        sys.exit(1)
    url = sys.argv[1]
    vid = url.rstrip("/").split("/")[-1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join("videos", vid + ".mp4")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)

    qs = urllib.parse.urlencode({"appId": APP_ID, "appKey": APP_KEY, "url": url})
    req = urllib.request.Request(f"{API_URL}?{qs}", method="GET")
    req.add_header("User-Agent", "Mozilla/5.0")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print("HTTPError:", e.code, e.read().decode("utf-8","ignore")[:300]); sys.exit(1)
    except Exception as e:
        print("RequestError:", e); sys.exit(1)

    code = result.get("code")
    print("code:", code, "| msg:", result.get("msg",""))
    if str(code) == "200":
        data = result.get("data") or {}
        if data.get("title"):
            print("title:", data["title"])
        media_url = data.get("mediaUrl") or data.get("video_url") or data.get("video_url_v2")
        if not media_url:
            print("无直链，返回:", json.dumps(data, ensure_ascii=False)[:300]); sys.exit(1)
        print("无水印直链:", media_url)
        print("下载中 ->", out)
        vreq = urllib.request.Request(media_url, headers={
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)",
            "Referer": "https://weixin.qq.com/",
        })
        try:
            with urllib.request.urlopen(vreq, timeout=180) as r:
                total = int(r.headers.get("content-length", 0))
                done = 0
                with open(out, "wb") as f:
                    while True:
                        chunk = r.read(65536)
                        if not chunk: break
                        f.write(chunk); done += len(chunk)
                        if total: print(f"\r{done*100//total}%", end="", flush=True)
            print(f"\n已保存: {out}  size={os.path.getsize(out)} bytes")
        except Exception as e:
            print("\n下载失败:", e); sys.exit(1)
    else:
        print("解析失败:", json.dumps(result, ensure_ascii=False)[:500]); sys.exit(1)

if __name__ == "__main__":
    main()
```

### 2) download_model.py —— 从 ModelScope 拉 faster-whisper 模型（HF 被墙时的替代源）
```python
from modelscope.hub.snapshot_download import snapshot_download

repo = "AI-ModelScope/faster-whisper-medium"
print("downloading repo:", repo)
try:
    path = snapshot_download(repo, revision="master")
    print("MODEL_PATH=", path)
except Exception as e:
    print("TRY1_FAILED:", repr(e)[:300])
    for cand in ["modelcope/faster-whisper-medium", "AI-ModelScope/whisper-medium",
                 "Systran/faster-whisper-medium"]:
        try:
            print("trying", cand)
            path = snapshot_download(cand, revision="master")
            print("MODEL_PATH=", path)
            break
        except Exception as e2:
            print("FAILED", cand, repr(e2)[:200])
```

### 3) transcribe_text.py —— 中文语音转文字
```python
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
```

### 依赖安装（隔离 venv，推荐）
```bash
python -m venv venv
# Windows 用 venv\Scripts\pip，Linux/Mac 用 venv/bin/pip
pip install faster-whisper imageio-ffmpeg modelscope
# 解析下载本身只要标准库，无需额外装包
```

---

## 六、关键坑与对策（实战踩过的，照抄可避坑）

1. **本地死代理拦截（最常见）**
   - 现象：`connect ECONNREFUSED 127.0.0.1:7890` 或 `WinError 10061`。
   - 原因：环境把 `HTTPS_PROXY` 指到本机 7890（一个没运行的本地代理），所有流量被它吃掉。
   - 对策：`parse_download.py` 开头已 `os.environ.pop` 清空代理变量再请求；或在 shell 用 `env -u HTTPS_PROXY -u HTTP_PROXY` 跑。
   - 注意：WorkBuddy 的 Bash 里 `env` 命令有时会找不到，直接把清代理写进脚本最稳。

2. **HuggingFace 被墙，模型下不来**
   - 现象：`hf-mirror.com` 也连超时，`faster-whisper medium` 模型（HF 格式）下不动。
   - 对策：改用 **ModelScope** 源（国内可达）。`pip install modelscope` 后跑 `download_model.py` 拉 `AI-ModelScope/faster-whisper-medium`，再用本地路径加载。

3. **openai-whisper 装不上**
   - 现象：构建失败（缺 `pkg_resources`，旧 setup 不兼容新 Python）。
   - 对策：直接换 **faster-whisper**（纯 CT2，不依赖 torch，更快）。已验证可行。

4. **ASR 中文术语识别错误，必须人工校正**
   - faster-whisper 中文口播准确率尚可，但专业词会错。已实测需校正的样例（税务场景）：
     - `引领收入` → **隐匿收入**
     - `至哪斤并处罚款` → **加收滞纳金并处罚款**
     - `题外循环` → **体外循环**
     - `满天过海` → **瞒天过海**
   - 交付文案前，务必按领域术语逐条校对，否则会闹笑话。

5. **直链有时效性**
   - `finder.video.qq.com` 的直链带 `token` 签名，通常数小时~1天失效。
   - 对策：拿到直链**尽快下载**；失效就重新解析原链接。

6. **视频号接口不返回口播逐字稿，但奇云返回 title（发布配文）**
   - 奇云 `sph_parse` 返回的 `title` 是作者写的那句**描述文案**（如 `#每日分享|...`），不是视频里说话的口播稿。
   - 要口播逐字稿，只能走 ASR（先下视频再转写）。
   - 部分视频 `title` 也会为空，属正常。

---

## 七、迁移到另一台电脑（照做清单）

1. 复制本技能文件夹到目标机的 `~/.workbuddy/skills/`（或直接将本技能的 scripts/ 拷过去）。
2. 装 Python 3.12+，建 venv，装 `faster-whisper imageio-ffmpeg modelscope`（只要下载视频可不装后两个）。
3. 到 https://qyapi.ipaybuy.cn 注册拿 AppId + AppKey，设环境变量 `QIYUN_APP_ID` 与 `QIYUN_APP_KEY`，或填进 `parse_download.py` 顶部常量。
4. 下载视频：
   ```bash
   python scripts/parse_download.py "https://weixin.qq.com/sph/XXXXXXXX"
   ```
5. （要文案）先 `python scripts/download_model.py` 拉模型，记下 `MODEL_PATH=`，设 `FW_MODEL_DIR` 或改 `transcribe_text.py` 里的路径，再：
   ```bash
   python scripts/transcribe_text.py videos/XXXXXXXX.mp4
   ```
6. 打开 `videos/XXXXXXXX_文案.txt`，按领域术语校对后交付。

---

## 八、合规提醒
仅用于你拥有版权或已获授权的素材；遵守各平台与版权规范。直链有时效，请及时保存。
