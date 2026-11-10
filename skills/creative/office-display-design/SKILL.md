---
name: office-display-design
description: Welcome screens & office signage via real-font HTML.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [welcome, signage, display, 欢迎屏, 大屏, 展板, 展示, 告示牌, screen]
    category: creative
---

# 办公展示屏与标识设计 (Office Display & Signage Design) Skill

覆盖办公室/公司的**文字关键型视觉展示**——前台/洽谈室欢迎屏、70寸一体机欢迎语、展板、告示牌、活动主视觉、形象墙。核心方法: **不走 AI 生图(中文正文必乱码),走「真实字体 HTML → 浏览器截图 → PNG」**,文字 100% 不糊不乱,分辨率精确可控,设计方可直接照着排版。

背景约束: 本机主模型为 deepseek-v4-flash(无原生视觉),"看图"全靠 auxiliary.vision。历史上 vision 曾因指向被 chudian 下架的 `deepseek-v4-flash-vision-exp`(404 已停用)而整链停摆;已修复并指向 telecom `Doubao-Seed-2.1-Pro`(aigw.telecomjs.com / `TELECOM_DOUBAO_KEY`,实测可读图)。检修/重指向方法见本技能 `references/vision-model-repoint.md`(诊断→直问网关模型列表→`hermes config set auxiliary.vision.*`→实弹验证→会话缓存坑)。若未来再看不了图,本技能保留**无视觉时的兜底验收法**——不要因为看不了图就放弃交付,也不要假装看过图。

## When to Use
- 用户要「欢迎屏 / 欢迎语 / 大屏展示 / 公司形象墙 / 展板 / 告示牌 / 活动主视觉」
- 需要交给设计师、或直接上屏的版式稿(主标题、业务列表、资质陈述是核心信息)
- 任何"文字即关键信息"的视觉物料

## Prerequisites
- 浏览器工具(browser_navigate / browser_vision)用于打开本地 HTML 并截图
- PIL 用于结构校验: `python3 -c "from PIL import Image; print(Image.open(f).size, Image.open(f).mode)"`
- 本机没有可用的 AI 生图 key 时更应直接走本路线(生图 key / 替代方案见 image-gen-cn)

## Quick Reference
- 目标画布: 商用大屏 / 70寸一体机 = **1920×1080**(16:9); 竖屏门牌 / 立牌 = 1080×1920
- 中文字体栈: `"Microsoft YaHei","PingFang SC","Noto Sans SC",sans-serif`
- 财税/商务稳重配色: 深蓝底 `#0a1a2f` + 金色点缀 `#c9a86a` + 米白正文 `#f4f7fb`(可换红金/白蓝)
- 截图自动落盘: `~/.hermes/cache/screenshots/browser_screenshot_*.png`
- 已有一份可改的完整 HTML: `templates/welcome_screen.html`
- LOGO 上屏: 左上品牌区 + 右上 LOGO 最稳; `<img class="logo" style="height:屏高12%;object-fit:contain">`(70寸约150px)。白底+正红纹样的 LOGO 在深蓝底上醒目协调,与左侧文字组同一水平线即平衡。**LOGO 带白底、想在深色底上彻底融入时,去白底只留图形**: `scripts/remove_white_bg.py <logo.png> [out.png] [--preview]`(PIL 近似白色转透明,min-channel 软阈值防白边,附深蓝合成预览与留存率验收)。最终排版参数见 `references/yingxin-welcome-screen.md`。

## Procedure
1. **先给文字稿(设计师稿)**: 3-5 行,简洁大气,主标题一行最大、副标/业务/收尾逐级缩小。给 2-3 个版本(3行/4行/5行),标出哪行最显眼、哪些数字属待核实。
2. **写 HTML**(可复制 `templates/welcome_screen.html` 改造):
   - `body` 固定 `width/height` = 目标分辨率,`overflow:hidden`
   - 结构: top 品牌区(中文全称+英文) → 主标题(最大字号) → 副标题(金色) → 业务一行(用 `｜` 分隔) → 收尾标语; 背景加同心圆环/微光装饰显大气
3. **渲染截图**: `browser_navigate file://<绝对路径>` 打开(截图自动落盘 `~/.hermes/cache/screenshots/browser_screenshot_*.png`)。
4. **看图验收(推荐)**: 用 `vision_analyze` 读截图把关——逐行念文字查乱码/叠字、查配色排版、验 LOGO 观感。若当前会话内部路由不稳、把图误发给主模型(纯文本模型报 `does not accept input types: image`),改用**直连多模态端点 POST base64 图**验收(封装好的自测脚本见本技能 `references/vision-model-repoint.md`,含手动 POST 片段),结果同样可靠。
5. **无视觉兜底验收**: 若 auxiliary.vision 停用,vision 调用会报错但**截图仍然生成**于 `~/.hermes/cache/screenshots/`——失败的是"肉眼验收"这一步,不是交付。用 PIL 校验目标尺寸 + RGB,文件有效即视为渲染成功(HTML 确定性高,文字不会乱码)。**务必在报错里找 `screenshot_path`**,别以为失败了。
6. **打包交付**: png(渲染稿) + html(源文件) + 文字稿.txt 先入同名文件夹 → `zip -rq` → 放到 Windows 桌面,只报 Windows 路径(`C:\Users\Administrator\Desktop\...zip`),删临时文件夹(交付纪律,见下)。
7. **如实汇报**: 未能亲眼看图时,明确告诉用户"辅助视觉模型停用,我没法亲验观感,请你打开 PNG 确认配色/布局",并给出改版入口(换配色 / 加 LOGO / 换成用户确认后的精确数字)。

## Pitfalls
- **AI 生图中文必乱码**: 含关键文案/数字的画面禁用 AI 生图(image-gen-cn 同样强调)。可让 AI 出"无字背景氛围图",文字用真实排版叠加。
- **主模型无原生视觉**: deepseek-v4-flash 看不了图,"看图"全走 auxiliary.vision(deepseek-v4-flash-vision-exp / 豆包等)。该模型可能停用——这是环境态,截图本身不受影响,用 PIL 结构验收替代即可。
- **不要假装看过图**: 视觉停用时的验收 = HTML 确定性 + PIL 尺寸,属"结构验收",观感验收必须交还用户。谎称看过会导致交付物未经真实复核。视觉可用(telecom Doubao)时优先看图验收(见 Procedure 第4步)。
- **LOGO 与底色冲突**: 深色底上若 LOGO 本身深色会看不清; 先渲染再用视觉模型确认。背景金环装饰线被 LOGO 白底遮挡属正常(装饰衬底在 LOGO 下层),无需处理。追求极致可把 LOGO 缩小 10–15% 使上下边与左侧文字组齐平。**LOGO 带白底、要彻底融入深色底(用户说「去掉白底/只要图标」)时,去白底只留图形**—— `scripts/remove_white_bg.py <logo.png> [out.png] [--preview]`(近似白色像素转透明 + pass 2 清扫灰/白残留;验收=「保留不透明像素占比」>0 + 平均RGB为图形固有色 + 深蓝合成预览 + 视觉模型确认无白边灰边;全浅/全透=阈值误杀,把 190 调近 225)。去底版存为独立资产(如 `logo_transparent.png`)供 PPT/名片/公众号复用。
- **「LOGO 下方一条白线」的根因**: 通常不是排版元素(如 `.top` 的 border 是金色不是白线),而是去白底后 PNG **最底边缘 ~1-2px 浅灰抗锯齿残留**(原白块的底边),在深色底上显成白线。`remove_white_bg.py` 已内建 pass 2 清扫(低饱和 AND 偏亮→透明);若仍见线,先直连视觉模型看「白底垫底」放大版定位残留位置/颜色,再补清扫或裁掉底缘 1-2px。详见 `references/yingxin-welcome-screen.md` v5 节。
- **事实纪律(对外物料)**: "十六年 / 服务逾千家 / 资质 / 团队人数"等具体数字无据不得编;确需占位就用醒目标注「待核实」,交付时逐条点名请用户替换。
- **交付纪律**: 桌面只留 zip 不留散件; `folder → zip → 删文件夹`; 中文文件名在 WSL 下 zip 正常(实测)。Word/图片被占用报 PermissionError 时勿重试,换名或关闭占用程序。

## Verification
- PIL 输出尺寸 = 目标分辨率且 `mode=RGB`
- `unzip -l <zip>` 应含 png + html + txt 三件
- 文字稿中所有「待核实」条目已逐条当面提醒用户核对

## References
- `references/yingxin-welcome-screen.md` — 盈信 70寸欢迎屏实战: 五版文案迭代、配色参数、LOGO 上屏参数、交付记录(可复用为新的欢迎屏底稿)
- `references/vision-model-repoint.md` — auxiliary.vision 模型被下架/读不了图的检修工作流(诊断→重指向→实弹验证→会话缓存坑),含手动 POST base64 图片段
