---
name: shouchaobao-poster
description: Make a printable 手抄报/poster as A4 PDF with ReportLab.
---

# 手抄报 / 可打印中文海报生成

## 触发与交付
- 用户说"生成手抄报/海报/文档放桌面" → 先定位 Windows 桌面：`find /mnt/c/Users/*/Desktop -maxdepth 0`（WSL 用户名常是 jiangmin）。
- 交三份到桌面：`.pdf`（打印最佳，A4 单页矢量）+ `.png`（高清图，pdftoppm 渲染）+ `.html`（浏览器打开可改字改色）。
- 打印建议一并告诉用户：A4 纵向、实际尺寸 100%。

## 渲染路径（按可靠度排序）
1. **Python 生成 SVG → cairosvg 转 PNG(300dpi) + PDF —— 首选**。SVG 能画矢量插图（天安门/国旗/灯笼/气球/火箭/花/星），也支持手写字与渐变，画质最高。cairosvg 装在**系统 python** `/usr/bin/python3`；在 execute_code 里要用 `subprocess.run(["/usr/bin/python3","-c",code])`（沙箱内核没有，直接 ImportError）。详见 references/cairosvg-and-fonts.md。
2. **ReportLab canvas 直接矢量绘制**（纯文字/矩形、无丰富插图的稳定回退）。单页坐标完全可控。
3. 浏览器全页截图（browser_exec capture）—— 需要本机装了 Chromium（`npx playwright install --with-deps chromium`）；服务器/最小环境常没装，失败就回退到方案 1/2，不要卡住。
4. **不能用 LibreOffice 把 HTML 转 PDF** 来做布局海报 —— writer_web 过滤器不支持 CSS grid / 绝对定位，会把多栏叠成单栏、标题错位、内容溢成 2 页。只适合纯流式文本。

## SVG → cairosvg 渲染（画质最高的那条路）
- SVG 用 `viewBox="0 0 1100 1556"`（A4 纵向）。SVG `<head>`/defs 务必用 **f-string** 拼，别用 `%` 格式化 —— `<filter>` 里有字面 `%`（`width="140%"`、`flood-opacity="0.18"`）会让 `%` 格式化报 "not enough arguments"/unsupported format char。
- **cairosvg 渲染 feTurbulence+feColorMatrix 会整页变黑**：满页 `<rect filter="url(#grain)">`（feTurbulence+feColorMatrix）会把整张画布渲成纯黑。水彩/软边效果只用 `feGaussianBlur`、`feDropShadow` 和 radial/linear 渐变（已测：feDisplacementMap 描边、feGaussianBlur 光晕可用）。
- 中文字体走 fontconfig：装到 `/usr/share/fonts/truetype/custom/` 后 `fc-cache -f`。三个手写体（毛笔 马善政 Ma Shan Zheng / 圆润 站酷快乐体 ZCOOL KuaiLe / 潦草 之芒星 Zhi Mang Xing）下载地址见 references/cairosvg-and-fonts.md。正文较整洁时用 wqy-microhei。
- **验证手写体真渲染了**（否则退成黑体就没手写味）：同一字形分别用候选字体和 wqy 渲染，比较墨迹像素数，必须不同；`fc-list` 能列出不算数。
- 无视觉时版面验证：抽样像素确认非纯黑、各色系都在（红=旗/标题、绿=场景、金=星/太阳）；用 get_text/pdfinfo 核对文字齐全、单页。别硬等 vision。

## ReportLab + 中文（硬坑）
- 字体：reportlab **不能加载 CFF/OTF 轮廓的 CJK**（Noto CJK 的 .ttc/.otf 报 "postscript outlines are not supported"）。用纯 TrueType：`/usr/share/fonts/truetype/wqy/wqy-microhei-regular.ttf`。
- wqy-microhei 没有 emoji 字形（🎈🏮📖✍️💌 会画成空框 tofu）。装饰符号一律用几何/符号：`★ ● ◆ ♥`，连标题里的 emoji 也要去掉。
- 用 `pdfmetrics.stringWidth` 测**真实**宽度再换行。手抄报正文混有半角数字/年份，纯按字数断行会错位。

## 单页布局引擎（防溢出的关键步骤）
- A4 = 595.27 × 841.89 pt。左右两栏：栏宽 = (W − 2·margin − 栏距)/2，栏距约 14。
- 每块文字用 cwrap()（逐字累积 stringWidth，超内容宽就断行）算行数和高度；板块盒高 = 内容高 + 标题留白(约 34)。
- **整体缩放**：对候选 SCALE [1.0…0.68 步进 0.04]，量左右两栏总高，取两者都 ≤ 可用区（顶横幅底 ~ 底部签写栏顶）的最大 SCALE；重绘时所有 fs/lh 乘 SCALE。
- 常用 bug：元组/列表取内容下标取错（取到了颜色/类型）；`len()` 套在整型行数上报 "int has no len()" —— 行数别写成 1 再 len()。
- 完整可复制的引擎代码见 references/reportlab-cjk-layout.md。

## 无视觉时的验证
- 当前模型可能不支持图像，vision_analyze 会报 "does not accept input types: image"。**不要硬等，改用程序化验证**：
  - `pdfinfo xxx.pdf` → `Pages:` 必须 = 1；
  - `fitz.open(pdf)[0].get_text()` 确认所有板块文字都在；
  - 引擎量到的版面高度 ≤ 可用区即无溢出。

## 用户偏好（学校手抄报 —— 最终定型，勿再推倒重来）
- 中文交流；直接给能用的成品，少说废话。
- **章节边框 = 标准干净矩形**：纯色描边 + 顶部一整条同色标题栏（白字加粗标题）+ 圆角 + 淡投影。不要歪扭抖动边框，也不要千篇一律的纯编辑框。
- **页面插图要丰富**：天安门(标题徽章)、五星红旗、红灯笼、彩气球、和平鸽、太阳+光芒、云、火箭、奥运五环、烟花、花、星、底部青山绿水场景、班级/姓名/日期签写框。
- 标题可用圆润/毛笔手写体（ZCOOL KuaiLe / Ma Shan Zheng）显活泼，但**保持矩形框**、不歪边框。
- 教训：用户否掉了"工整整齐的制式表格"，也否掉了"歪七扭八的手工剪贴"。能让他满意的方向 = 干净矩形 + 插图堆满。被要求"再改"时，往"加/修插图"走，别往"更歪的边框"走。
