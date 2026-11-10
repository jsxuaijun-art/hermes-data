---
name: official-screenshot-images
description: 配图用官方截图法——生图key不可用时给文章/素材取凭证与实景图。
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [配图, 截图, 官方, 凭证, 清税证明, 实景, 文章插图]
---

# 官方截图法配图（AI 生图不可用时的凭证/文件类配图兜底）

用户要正文配图，配图对象是**文字密集的凭证/文件/实景**（清税证明、发票样张、公告截图、办税大厅外景等）时，**别用 AI 生图**——凭证类含大量文字必乱码（同 wechat-comic-cells「文字错乱零容忍」铁律）。改用**官方截图法**：从官方政务/办税课件页抓取现成业务截图，贴题、全新、零乱码、无版权问题。2026.11 实测走通。

## When to Use
- 用户指定配图是某种凭证/文件/官方实景（清税证明、税务局外景、发票、公告、政务大厅等）。
- AI 生图 key 不可用（`SEEDREAM_API_KEY`/`DASHSCOPE_API_KEY` 未配，脚本直接 401——注意 `TELECOM_DOUBAO_KEY` 仅 vision 用，顶替生图也 401）。
- 想避开只能是"Ai 生成的场景图"而需要真实可信素材的场景。

## Prerequisites
- 浏览器工具可用（`browser_get_images` / `browser_navigate`）。
- 有视觉的后端可用（主模型无视觉时 `vision_analyze` 走 `auxiliary.vision`）。
- 发布环境：服务器 `root@47.103.27.171`，nginx 图片目录 `/var/www/html/images/`，wenyan serve 已运行（发布走 wechat-publish 流程）。

## Procedure
1. **定位官方原始页面**：税务类配图搜「纳税人学堂」课件页（例：`guangdong.chinatax.gov.cn/gdsw/fssw_nsrxt_kjxz/...` 的「注销登记（含清税申报）」课件，源=国家税务总局佛山税务局），这类课件页把全部业务操作截图内嵌在正文里。
2. **列图**：`browser_get_images` 拉取页内全部图片 URL；大尺寸图（612×356 档）通常是文书/《清税证明》样张，小图（554×22）多为分割线。
3. **下载**：`curl -L -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" <url> -o <out>.png`。
4. **逐张验证（必须）**：`vision_analyze` 确认画面是目标样张（《清税证明》要有大标题+税务公章+正文，而非系统操作提示/返回按钮页）再定图。
5. **命名上传**：`section_<主题>_<YYYYMMDD>.jpg` 传到服务器 `/var/www/html/images/`（见 Pitfall：需用户批准），文章内用 `![](http://localhost:8080/images/xxx.jpg)`。

### 实景类（办税服务厅/大楼外景）的来源与取舍
用户指定"税务局外景/办税厅实景"这类**实景照片**时，来源判断（2026.11 实测）：
- **官方税务官网不提供可直接热链的大楼外景实景图**。上海局(shanghai.chinatax.gov.cn)、总局(chinatax.gov.cn)首页全是领导活动/新闻图；图片新闻栏(tpxw)多为活动/内景；Bing 图片搜"税务局 办税服务厅 外景"无结果。别在官网首页漫无目的逛。
- **官方"办税服务厅启用/揭牌"新闻内嵌原图是最佳官方实景来源**。例：上海"智慧办税服务厅正式启用"新闻 `shanghai.chinatax.gov.cn/xwdt/jcdt/201904/t444936.html`，正文 3 张 `W0*.jpg` 为 Canon 单反高清、含"xx区税务局"标识+税务制服人员，贴题、全新、零重复。路径规律：`shanghai.chinatax.gov.cn/xwdt/jcdt/YYYYMM/t<id>.html` → 正文 `W0...jpg`。
- **找不到纯净"大楼外景"时，把"官方办税厅实景(内景，含税务标识)"作为方案 B 提交用户定夺**，别无限搜索——内景官方实景通核算作"税务局场景"配图完全贴题。需用户批准上传+发布时也一样先列方案再执行。

## Quick Reference
```bash
# 列页内图片
browser_get_images
# 下载（带 UA 防反爬）
curl -sL -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" "$URL" -o /tmp/tax.png
# 验证
vision_analyze(image_url=/tmp/tax.png, question="是否《清税证明》样张？有无标题/公章/正文？")
# 官方税务实景来源（办税厅启用/揭牌新闻）
#   上海局: https://shanghai.chinatax.gov.cn/xwdt/jcdt/YYYYMM/t<id>.html 正文 W0*.jpg
```

## Pitfalls
- **服务器 /var/www/html/images/ 写入需用户批准**：向 `root@47.103.27.171:/var/www/html/images/` 的 scp/ssh cp 会触发安全批准门，超时即 BLOCKED。**先向用户说明将上传哪些文件、获确认再执行**；不静默重试、不换命令绕过。
- **凭证类配图禁止 AI 生图**：文字必乱码；生图仅适合场景/人物/氛围类。
- **生图 key 缺失是 401 不是"未设置"**：`image_gen_seedream.py` 在 key 存在但不匹配时返回 HTTP 401；先 `grep -E "SEEDREAM|DASHSCOPE" ~/.hermes/.env` 确认 key 是否真的配了（配完需新开 session）。
- **vision 验证不可省**：主模型无视觉时必须让辅助视觉模型确认画面内容，否则可能把"操作提示截图"当样张用。
- **服务器图库文件名/标题不可信**：`section_tax*`、`cover_gov`、`taxhall` 等命名"税务/政务"的既有图经 vision 核验多为**室内场景**（办公桌面特写、会议、笔记本+眼镜、VR 体验），不是税务局大楼外景；取用前一律 vision_analyze 确认画面目标要素，勿因文件名是"税务"就直接用。

## Verification
- 下载后 `file <out>.png` 确认 PNG 头正常、尺寸符合预期（512×300+）。
- `vision_analyze` 返回的目标要素齐全（标题/公章/正文）。
- 服务器 curl 200 确认上传成功：`curl -s -o /dev/null -w "%{http_code}" http://47.103.27.171:8080/images/<file>.jpg`。
