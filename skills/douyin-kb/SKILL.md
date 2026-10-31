---
name: douyin-kb
description: 把抖音收藏转成可检索知识卡片，存入 Obsidian。
version: 1.0.0
author: Hermes Agent (for 徐总/盈信)
license: MIT
metadata:
  hermes:
    tags: [douyin, 抖音, 知识库, obsidian, 收藏]
    category: productivity
    related_skills: [video-download, video-transcription, ima-skill]
triggers:
  - 收一个抖音 / 抖音收藏进库 / 把这条收进知识库
  - v.douyin.com / douyin.com/video/ (直接粘贴抖音链接即触发)
  - 在收藏库找 / 查收藏 / 抖音知识库
---

# 抖音收藏知识库 (douyin-kb) Skill

## When to Use

用户在对话中**直接粘贴一条抖音分享链接**（`v.douyin.com/短链` 或 `douyin.com/video/<id>`）时，自动走本流程，**无需用户再说"收一个抖音"**（快捷指令：粘贴即触发）。

把一条抖音视频：下载 → 转写 → 生成知识卡片 → 存入 Obsidian 主库 `30-Knowledge/抖音知识库/`。

**目标**：刷到有价值的内容照常收藏，丢链接给我，我自动整理成可检索的知识卡片
（一句话概括 + 核心要点 + 长视频章节拆分 + 原视频链接）。想查时说
「在收藏库找讲 XX 的视频」，我读卡片汇总返回。

**存储策略（2026-10-28 徐总确认）**：**vault 只存 .md 卡片文字 + 原视频链接，不存视频文件**。
下载的 mp4 / 抽出的 wav / 转写稿都只是处理过程临时文件，放在 `/tmp`，出卡后立即删除。
理由：视频体积大，存进去会撑爆 vault、拖垮 git/obsidian 同步；文字 + 原链接已含全部可检索信息，查看时一键跳转。

**数据边界**：本目录随 `obsidian_sync.sh` 推送 GitHub。**涉客户/涉税敏感内容不要走这里**，
敏感内容放私有区。知识库只存公开的财税知识/方法论。

## Prerequisites

- 转写引擎：持久化 venv `~/videoenv`（faster-whisper）。首次已配好；**若报
  `metadata_errors` 异常，是 av 被升到了 19.x 新版（移除了该参数），须钉回**：
  `~/videoenv/bin/pip install -q "av==12.3.0" -i https://pypi.tuna.tsinghua.edu.cn/simple`
- 下载依赖：`video-download` 的 yt-dlp / ffmpeg（`~/.local/bin/ffmpeg`）。
- Obsidian 目标目录：`/mnt/d/obsidian-vault/30-Knowledge/抖音知识库/`。

## How to Run

```bash
# 1. 下载（见「下载」节）
# 2. 转写成带时间戳文字稿
python3 ~/.hermes/skills/douyin-kb/scripts/transcribe.py /tmp/xx.mp4 \
  --size small --prompt "以下是财税/短视频口播内容字幕。"
# 3. 读文字稿 → 按 _卡片模板.md 生成知识卡片 → 写入目标目录
```

## Quick Reference

| 步骤 | 命令 / 动作 |
|---|---|
| 下载 | 见「下载」节（抖音通常要登录态） |
| 转写 | `python3 .../scripts/transcribe.py <mp4> --size small` |
| 卡片模板 | `<库>/_卡片模板.md`（frontmatter: title/source/date/tags/summary/chapters） |
| 卡片命名 | `YYYY-MM-DD-主题-关键词.md` |
| 索引 | 入库后把新卡登记进 `_MOC.md` 的「最近收藏」 |
| 检索 | 我读库内 .md，按 search_files 汇总返回 + 原链接 |

## Procedure

1. **拿链接**：用户给抖音分享链接（`v.douyin.com/短链` 或 `douyin.com/video/<id>`）。
2. **下载**：
   - 首选 `yt-dlp`，带登录态 cookies：`yt-dlp --cookies-from-browser chrome ...`（涉及账号，先经用户同意）。
   - 无登录态或 yt-dlp 失效时，走 `wechat-publish` 技能里验证过的「抖音获取步骤」：
     短链 curl 解析出 video id → 浏览器开带完整 share 参数的 URL → 页面内 fetch
     `aweme/detail` API 拿 `desc`/作者 → 用 `curl -A <UA> -H "Referer: https://www.douyin.com/"` 下载 MP4。
   - 下载到 `/tmp/<名>.mp4`，用 `ffprobe` 确认有 video+audio 两流。
3. **转写**：`transcribe.py` 抽音频 + faster-whisper（`--size small`，领域 prompt 减财税专名错字）；
   转写 `base` 快但错字多，重要内容建议 `small`。长视频先看时间戳断章。
4. **生成知识卡片**：读转写稿，按 `_卡片模板.md` 字段生成 `.md`（一句话概括=最抓眼球；要点 3~6 条；
   长视频按时间戳拆章节；`source` 填原抖音链接；tags 覆盖核心主题+延伸）。卡片正文按文案路由铁律走
   创作模型（豆包/kimi），主会话只做编排；**事实/数字以原视频口播为准，不脑补**（公众号数字溯源纪律同样适用）。
5. **入库**：`write_file` 写入 `/mnt/d/obsidian-vault/30-Knowledge/抖音知识库/YYYY-MM-DD-主题-关键词.md`；
   更新 `_MOC.md` 最新收藏 + 主题标签导航。
6. **交付**：回复路径用 Windows 盘符 `D:\obsidian-vault\30-Knowledge\抖音知识库\...`；附一句话概括 + 原链接。
7. **清理临时文件（必做）**：出卡并交付后，删除 `/tmp` 下的下载视频、抽出的 wav、转写 .md（如 `/tmp/douyin_*.mp4`、`/tmp/douyin_*_transcript.md`、`/tmp/*.wav`）。**vault 只保留 .md 卡片 + 原链接，不落任何视频/音频**。

## Pitfalls

- **av/faster-whisper 版本锁**：`~/videoenv` 装好后，若日后某工具把 `av` 升到 19.x，转写会报
  `open() got an unexpected keyword argument 'metadata_errors'`（新版 av 移除了该参数）。
  修复：`pip install "av==12.3.0"`（钉回）。别追着报错文本看，那是假线索。
- **测试音频是纯音/无语音时，文字稿为空属正常**（whisper 不产出空段）；拿真实口播测才是有效验证。
- **抖音下载多数要登录态**；yt-dlp 无 cookies 常失效。别硬编链接，用 cookies-from-browser 或
  wechat-publish 的浏览器+aweme API 路径。
- **whisper 专有名词错字**（如涉税术语），结合画面/已知文案校对后才当事实引用；政策条文以官方原文为准。
- **空输出别当失败**：`--size base` 对背景音乐强的口播可能漏字，需清晰口播用小 size/small。
- **隐私**：此目录会随 obsidian_sync push 上云，敏感内容严禁入库。

## Verification

- 转写脚本可跑通：`python3 .../transcribe.py <一串真实口播mp3>` → 输出的 .md 非空、有 `[t0-t1]` 时间戳。
- 卡片落盘后 `read_file` 校验 frontmatter 字段齐全、`source` 是原抖音链接。
- `search_files` 在该目录能搜到刚入库的关键词。
