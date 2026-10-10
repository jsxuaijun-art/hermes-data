---
name: video-download
category: media
description: 用 yt-dlp 下载网络视频（B站/抖音/YouTube 等）到本地。
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [video, download, yt-dlp, bilibili, 素材]
    category: media
    related_skills: [video-transcription, sph-video-downloader, embedded-captions, auto-douyin-editor]
triggers:
  - 下载视频 / 下这个视频 / 存素材 / 视频链接
  - bilibili / B站 / 抖音 / youtube 视频下载
  - 竞品视频 / 同行视频 素材
  - yt-dlp
---

# 视频下载 (video-download) Skill

## 概述

用 yt-dlp 从网络平台（B站/抖音/YouTube 等上千站点）下载视频到本地。用户场景：分析竞品/同行短视频、存视频素材、给转文字稿提供本地文件。下载只是取件步骤——下一步转文字/加字幕/剪辑分别见 `video-transcription` / `embedded-captions` / `auto-douyin-editor`。

## When to Use

- 用户说"下这个视频 / 把这个B站/抖音链接的素材存下来"
- 分析竞品短视频需要本地文件（先下载再转写/拆解）
- 批量存素材做选题库

## Prerequisites

- WSL 环境已装 yt-dlp（Hermes venv）+ ffmpeg（~/.local/bin 符号链接），安装细节见 `wsl-hermes-env` §7.2（无 sudo，全走 pip 清华镜像）。
- 自检：`/home/administrator/hermes-agent/venv/bin/yt-dlp --version`、`~/.local/bin/ffmpeg -version`。
- 未装时先用 wsl-hermes-env §7.2 配方装好再跑。Windows 独立版用 `winget install --id yt-dlp.yt-dlp -e`（2026-10 实测可用，落在 `...\AppData\Local\Microsoft\WinGet\Links\yt-dlp.exe`，自动合并走 Windows 侧已有 ffmpeg 8.1，无需 `--ffmpeg-location`）——注意 `winget` 是 Windows 专属命令，**必须在 Windows PowerShell 里跑**，在 WSL bash 里报 `Command 'winget' not found`；也可用 `powershell.exe -Command "..."` 代跑。仅「手动直连 GitHub 下 exe」才易断，下到一半的残缺 exe 必须删除，防误运行。
- 用户要 Windows 独立版时：`winget` 是 Windows 专属命令，**在 WSL bash 里不存在**（报 Command 'winget' not found）——指引用户去「开始菜单搜 PowerShell」里跑，或用 `powershell.exe -Command` 代跑。直连 GitHub 下到一半的残缺 yt-dlp.exe 必须删除，防误运行。

## How to Run

```bash
V=/home/administrator/hermes-agent/venv/bin
$V/yt-dlp --ffmpeg-location /home/administrator/.local/bin \
  -f "bv*[height<=480]+ba/b[height<=480]" \
  -o "/tmp/out.%(ext)s" "<视频链接>"
```

## Quick Reference

| 目的 | 命令 |
|---|---|
| 列出清晰度档位 | `yt-dlp -F <url>` |
| Windows PowerShell 里跑（winget 版） | `yt-dlp -f 'bv*[height<=480]+ba/b[height<=480]' "链接"`（-f 表达式用单引号包住，`<` 才不被 PS 误解析） |
| 下载并自动合并（最常用） | `yt-dlp --ffmpeg-location ~/.local/bin -f "bv*[height<=480]+ba/b[height<=480]" -o "out.%(ext)s" <url>` |
| 只取音频 mp3 | `yt-dlp -x --audio-format mp3 <url>` |
| 只看信息不下载 | `yt-dlp -s --print "%(title)s | %(extractor)s" <url>` |
| 需要登录态（大会员/需登录平台） | 加 `--cookies-from-browser chrome`（涉及账号，让用户决定） |

## Procedure

1. 拿到链接，先 `-F` 看清晰度档位，顺便确认站点被支持（会显示 extractor 名）。
2. 选档：通用 `bv*[height<=480]+ba/b[height<=480]`（省流量、够转写/分析）；要高清改 height 值（免费档最高普通 1080P）。
3. 下载：**必须带 `--ffmpeg-location ~/.local/bin`**，否则 B站等 DASH 站点不合并，得到无声视频。
4. 验证：`ffmpeg -i out.mp4` 应有 Duration + 视频流 + 音频流。
5. 交付：cp 到 Windows 盘符目录（`C:\Users\Administrator\...`），回复一律用盘符路径。

## Pitfalls

- B站视频 = 画面/声音分离的 DASH 流，不合并只有画面流；合并要求目录里有名为 `ffmpeg` 的二进制（imageio 自带的文件名不叫 ffmpeg，必须先 ln -sf，见 wsl-hermes-env §7.2）。
- B站 4K/1080P 高码率需大会员，日志明说 `premium member`；未登录只能到普通 1080P/720P。
- B站**短时间连发多次会触发风控**：报 `ERROR: [BiliBili] ...: No video formats found!`——当同链接先前下过、`-F` 又能列档位时，这是限流不是安装坏。停 30~60 秒重试即恢复；批量下载加 `--sleep-requests 2`（或 `--sleep-interval`）降频。别急着重装或换工具。
- 抖音/视频号等平台频繁要求登录态/cookies；无登录态下不来说明，如实报"该平台需账号态"，别硬编链接。
- 视频号无水印专用流程见 `sph-video-downloader`；本技能是通用平台路径，不替代它。
- 下载超时/网络问题：B站国内直连即可（约 3-4MB/s），YouTube 在境内需代理。

## Verification

- 产物 mp4 可播放：`ffprobe -v error -show_entries stream=codec_type,codec_name -show_entries format=duration,size -of default=noprint_wrappers=1 out.mp4` → 应列出 video+audio 两条流与正确时长（比读 `ffmpeg -i` 的 stderr 更好解析，Windows 侧 ffprobe 同命令通用）。
- 交付路径为盘符（C:\...），用户能直接双击。

## References

- 环境安装、ffmpeg 符号链接、跨系统合并陷阱：`wsl-hermes-env` §7
- 下载后的本地处理：`video-transcription`（转文字稿）、`embedded-captions`（加字幕）