---
name: office-welcome-screen
description: "编辑/更新办公室70寸欢迎屏设计稿（欢迎语/资质/LOGO）。"
version: 1.0.0
author: 徐爱军 (jsxuaijun-art); Hermes Agent 起草
license: internal
platforms: [windows, linux]
metadata:
  hermes:
    tags: [welcome-screen, 欢迎屏, 前台屏, 设计稿, logo]
---

# 办公室欢迎屏 Skill

编辑苏州盈信企业管理（苏州）有限公司办公室 70 寸一体机欢迎屏的设计稿。当前是一份 HTML（真实字体渲染，中文不乱码）→ 截图成 PNG 交付。

## When to Use
触发关键词（徐总指定）：**欢迎屏 / 欢迎光临 / 客户到访**；也含「欢迎语 / 前台屏 / 大屏 / 修改欢迎款」等词。徐总可能反复改文字、资质、LOGO、配色。

## 稳定文件位置（不会被 Hermes 升级清掉）
**Windows:** `C:\Users\Administrator\盈信欢迎屏\`
**WSL:** `/mnt/c/Users/Administrator/盈信欢迎屏/`
- `欢迎屏设计稿_可编辑.html` — 主源文件，改这个
- `欢迎屏效果图_当前版.png` — 最近一次渲染效果图
- `logo原图.png` — 原始 LOGO（白底+红图形）
- `logo透明红色.png` — 去白底去底线的纯红 LOGO（HTML 引用它）
- `欢迎屏文字稿.txt` — 文字内容与备选

## 当前设计（5 行结构）
```
苏州盈信企业管理有限公司                ← 顶部小字(左上)
欢迎光临 · 携手同行                      ← 主标题(最大)
高级会计师带队   会计从业二十五年         ← 资质一行(两者间距大)
税务合规 ｜ 代理记帐 ｜ 高端会计 ｜ 企业服务
专业诚信 值得托付 · 护航您的企业稳健发展   ← 收尾
LOGO 在右上角（透明红，缩至 ~105px）
```
公司名固定为「苏州盈信企业管理有限公司」（勿用旧名「盈信企业管理（苏州）有限公司」）。

## Procedure
1. 用 `patch` 编辑 `欢迎屏设计稿_可编辑.html` 里的文字 / 间距 / LOGO。
2. 渲染成图：`browser_navigate` 打开 `file:///mnt/c/Users/Administrator/盈信欢迎屏/欢迎屏设计稿_可编辑.html`，再 `browser_vision`（它即使分析失败也会返回 `screenshot_path`，用那个路径；browser_vision 自带的鉴权会报 "Request denied by Key Auth"，属正常，别追）。
3. 核验：把该截图路径 copy 到包目录后，**不要用 `vision_analyze`**（这台机器它会偶发把图发给不支持图的 deepseek-v4-flash 而 400）。改用 telecom Doubao 直连：POST `https://aigw.telecomjs.com/v1/chat/completions`，model=`Doubao-Seed-2.1-Pro`，key=`TELECOM_DOUBAO_KEY`（从 `~/.hermes/.env` 读取，勿写死/推送），把图片 base64 成 `data:image/png;base64,...` 放进 `image_url`。可随手裁剪右上角/中段放大核验局部。
4. 打包交付桌面：`/tmp/盈信欢迎屏/` 做打包目录，会把设计稿做个新版本 zip 放到 `C:\Users\Administrator\Desktop\盈信欢迎屏设计_vN_最终.zip`（N 递增）。桌面只留压缩包（交割纪律）。

## 常见修改点
- 换主标题意境词（第二行「携手同行」备选：互信共赢/携手共进/共创共赢/同心致远/敬请指教）——用户会点名，别自行换。
- 调 LOGO：改 `.logo { height:105px }`；要重做透明 logo 见 Pitfalls。
- 拉开两段资质间距：`<span class="cred" style="margin-left:80px;">`。
- 配色：深蓝底 `#0a1a2f` + 香槟金 `#c9a86a` + 白字。想改调 `background` / `colors`。

## Pitfalls
- **远端 HTML 源在升级时会被清**：`/home/administrator/hermes-agent/welcome_screen.html` 只是临时工作区，稳定源在 `C:\Users\Administrator\盈信欢迎屏\`。改的是后者。
- **桌面旧 zip 被 Windows 锁**：`rm` 会 Permission denied，删不掉就另存新版本号文件，让用户手动删旧的。
- **LOGO 去白底/去底边灰线**（Pillow）：把「低饱和且偏亮」（`max(r,g,b)-min < 60` 且 `min>150`）的像素 alpha 置 0，保留高饱和红。原 LOGO 底部有一条约 1-2px 灰白底边线 + 底部中央白点，都会被这个规则清掉。处理后给用户看效果图确认。
- 「代理记帐」是徐总明确指定的原文，**勿"好心"改成「代理记账」**，可口头提示一次即可。

## Verification
- 文字核对：视觉确认每行中文无乱码、无叠字、无溢出。
- LOGO：右上角清晰、无白边/灰边、与深蓝背景融合、不与装饰线重叠。
- 间距：两段资质明显分开。
- 交付：桌面生成新版本 zip（Windows 路径），报给用户。
