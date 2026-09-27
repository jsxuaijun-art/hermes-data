---
name: wechat-comic-cells
description: 公众号「图文分镜」生成器——把财税实战口径/政策解读做成竖版分镜图插入公众号文章。支持多风格：漫画风(扁平插画+对话气泡)、MBE卡通风(粗描边圆润)、极简信息卡风(白底黑框红点缀)。文字一律用真实字体排版，绝对清晰零错乱。触发词：「漫画」「分镜」「图文漫画」「政策图解」「换个风格」「做个xxx风格的」「风格02/03」。
version: 1.1.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [comic, manga, wechat, 公众号, 分镜, 图文, html-render]
---

# 公众号漫画图文分镜生成器（路线A：扁平插画 + 对话气泡）

把财税实战口径/政策解读做成「扁平插画风格 + 对话气泡」的竖版漫画分镜，可直接插入公众号文章。核心优势：**文字用真实字体排版，绝对清晰、零错乱**（AI生图漫画的文字会乱码，这是路线A最强的点）。

## 何时使用
用户说「漫画」「分镜」「图文漫画」「政策图解」「做个漫画风格的」「把xxx做成漫画」时触发。用户会用主题或一小段文案给输入。

## 核心技术栈（路线A，已验证）
- **渲染**：服务器 root@47.103.27.171 上装好的 **weasyprint 69**（本地无渲染工具、sudo需密码，一切在服务器做）。
- **中文字体**：文泉驿正黑 WenQuanYi Zen Hei（服务器已有，免费商用）。
- **画面**：CSS 色块背景 + 圆形色块角色（SVG内联绘制卡通人物）+ 对话气泡。**不依赖任何外部图片/素材库，无版权风险。**
- **HTML→PNG 管道**：weasyprint `HTML(x).write_pdf(x.pdf)` → ghostscript `gs -q -dNOPAUSE -dBATCH -sDEVICE=png16m -r96 -dUseCropBox -sOutputFile=out.png in.pdf`。
- **尺寸控制**：`@page { size: 900px HEIGHTpx; margin: 0; }` 精确控制每格宽高（手机竖屏约 900 宽）。
- **验证**：RapidOCR（本地 `/tmp/ocr-venv` 或系统级已装 `rapidocr_onnxruntime`）识别渲染出的PNG文字，确认零错乱（置信度应 >0.9）。

## 关键路径 & 命令
```bash
# 1. 写分镜HTML到本地 /tmp/xxx.html
# 2. 传到服务器
scp /tmp/xxx.html root@47.103.27.171:/tmp/
# 3. 服务器渲染
ssh root@47.103.27.171 'cd /tmp && python3 -c "
from weasyprint import HTML
HTML(\"xxx.html\").write_pdf(\"xxx.pdf\")
" && gs -q -dNOPAUSE -dBATCH -sDEVICE=png16m -r96 -dUseCropBox -sOutputFile=xxx.png xxx.pdf'
# 4. (可选)下载回本地验证
scp root@47.103.27.171:/tmp/xxx.png /tmp/xxx.png
# 5. RapidOCR验证文字
python3 -c "from rapidocr_onnxruntime import RapidOCR; ocr=RapidOCR(); r,_=ocr(\"/tmp/xxx.png\"); [print(f\"[{c:.2f}] {t}\") for b,t,c in r or []]"
# 6. 上传到服务器图片目录供文章用
ssh root@47.103.27.171 'cp /tmp/xxx.png /var/www/html/images/xxx.png'
```

## 分镜类型模板（布局固定，只填文字/角色）
1. **封面格** `cover`：顶部橙红标题条（大标题+副标题）+ 双角色对话气泡 + 底部主题脚注。900×560。
2. **口诀/对比格** `tip`：顶部标题条 + 红绿双栏对比卡（✖不能 / ✔可以）+ 脚注。900×620。适合「X可不可以」「对比口诀」类内容。
3. **剧情对话格** `scene`：多格气泡对话，2-4个角色依次说话。
4. **警示格** `warn`：红色印章 + 醒目警示文案（红线类内容）。

## 角色库（SVG内联卡通人物，保持系列风格统一）
| 角色 | 脚本name | 外观 | 说话人标注色 |
|------|---------|------|------------|
| 江姐（女会计师） | jie | 红衫、棕长发 | #B71C1C |
| 徐总（男老板） | boss | 蓝衫、黑短发+红领带 | #1565C0 |
| 傻老板（客户提问） | customer | 黄衫、褐发、张嘴困惑 | #F9A825 |
| 李会计（同行） | lawyer | 绿衫、戴眼镜 | #2E7D32 |

角色SVG写法：见本skill `templates/char-svg.md`。核心：`<svg viewBox="0 0 100 120">` 圆头(cx50 cy42 r30) + 发型(path) + 眼睛(circle) + 嘴(path) + 身体(rect rx12) + 领带/围巾(path)。

## 配色基调（全系列统一）
- 背景 `#FFF7E6`（暖橙）
- 主色 `#BF360C`（深橙红，标题条/气泡边框/文字深棕`#3E2723`）
- 说话人标注色：查角色库表
- 对比格：红`#E53935`/`#FFEBEE`，绿`#2E7D32`/`#E8F5E9`

## 验证技巧（主模型无视觉时如何"看到"画面）

本环境主模型 deepseek-v4-flash 不支持图片输入，无法直接"看"渲染结果。两条互补的验证通道，缺一不可：

**① RapidOCR 验文字（验证"文字零错乱"铁律）：**
```python
from rapidocr_onnxruntime import RapidOCR; ocr=RapidOCR(); r,_=ocr("/tmp/xxx.png")
[print(f"[{c:.2f}] {t}") for b,t,c in r or []]
```
置信度应 >0.9。重点核对：标题条文字、每段气泡台词、对比卡内容、脚注是否都在且无乱码。检查是否有文字被裁剪/溢出出格（OCR识别到奇怪的中断词往往就是这一格）。

**② 像素采样验图形（验证 SVG 人物/色块是否真的渲染出来）：**
OCR只认文字不认图形，必须用 PIL 采样主色确认人物和气泡就位。按你写进SVG/CSS的预期色值核对：
```python
from PIL import Image; from collections import Counter
im=Image.open('/tmp/xxx.png').convert('RGB'); px=im.load()
region=im.crop((left,top,right,bottom))   # 对每个角色的预期坐标区采样
cnt=Counter()
for y in range(region.size[1]):
    for x in range(region.size[0]):
        cnt[region.getpixel((x,y))]+=1
for c,n in cnt.most_common(8): print(f'#{c[0]:02X}{c[1]:02X}{c[2]:02X} x{n}')
```
核对点：人物肤色（如`#F8C471`）、衣物色（蓝`#1565C0`/红`#E53935`/绿`#2E7D32`）、气泡白底`#FFFFFF`、气泡边框色、背景`#FFF7E6`、对比格红绿双卡。**如果预期色没出现在对应区域，说明该元素没渲染/定位错了**——不要凭"结构对了"放过。

**配色核对表（本系列写死，可作为每格像素验证的期望值）：**
- 背景 `#FFF7E6`，主色/标题条 `#BF360C`
- jie 肤`#F5CBA7`衣`#E53935`，boss 肤`#F8C471`衣`#1565C0`
- customer 肤`#FDEBD0`衣`#F9A825`，lawyer 肤`#E8D5B7`衣`#2E7D32`
- 对比格：红`#E53935`/`#B71C1C`（左"不能"），绿`#2E7D32`/`#1B5E20`（右"可以"）

## 公众号集成（发布）

本skill的完整流水线已在真实生产验证过：4格分镜（封面cover→口诀tip→剧情scene→警示warn）全按模板生成、RapidOCR+像素双验证通过、组装成真实公众号文章发布进草稿箱成功（Media ID: ZIKXbXZdS_X3B-GDVk11B8qYSI_uyfVxzBQBZVdtIRA4or85RakowXHc9pvfzIiK）。文章=文字段落+分镜图混排，每张分镜前配一段对应文字说明。后续主题直接照此流程走。

- 分镜PNG传到 `/var/www/html/images/`，在 wechat-publish 文章md中用 `![](http://localhost:8080/images/xxx.png)` 插入（每张分镜前配一段对应文字说明）。
- 分镜图片宽度建议 900px（手机全屏），正文用居中式。
- 组装文章用 wechat-publish skill：frontmatter（title/author「苏州盈信企业管理」/cover用`http://localhost:8080/images/xxx.png`/abstract/reading_time）+ 文字段落与分镜图混排 + 文末话题标签5-8个 + 公司介绍 + 定稿CTA三动作（红色加粗加大），然后 wenyan publish 进草稿箱。

## 完整流程（一次做对）
1. **定题材**：从实战经验库（business-registration-advisor 等skill的 references/实战经验-窗口口径.md）选真实口径，或用户给定主题。
2. **写脚本**：把主题拆成 2-4 格分镜剧本（封面→剧情→口诀→警示），明确每格的角色+台词。
3. **生成分镜**：按分镜类型模板写HTML（复制模板改文字），逐一渲染。
4. **验证**：每格RapidOCR验文字零错乱 + 尺寸正确。
5. **发布**：传服务器，插入 wechat-publish 文章。遵守公众号铁律（话题标签5-8个、CTA三动作、配图不用历史图）。

## 路线B（后续）
真·AI漫画需要可用的图像生成key（image_generate工具）。当前环境key已脱敏不可用，先走路线A。路线B时用 baoyu-comic skill。

## Pitfalls
- **weasyprint 新版无 `write_png`**，必须 write_pdf + 用 gs 转 PNG。不要 `HTML.write_png`。
- **weasyprint 67 起 `--use-crop-box` 交给 gs 的 `-dUseCropBox`**，否则会有多余白边/页边距。用 `@page margin:0` + `-dUseCropBox` 组合精确裁切。
- **文字错乱零容忍**：每次必须 RapidOCR 验证，置信度 <0.9 要检查（可能是文字重叠、被裁剪、字体缺失）。
- **SVG人物**：weasyprint 支持内联SVG，但 `viewBox` 需配合 width/height 属性才缩放正确。
- **气泡里的 `::before` 伪元素箭头** weasyprint 支持不佳，改用独立 `.arrow` div + CSS border 三角形（已验证稳定）。
- **`display:flex`** 支持有限，复杂布局用 `position:absolute` 精确定位，别依赖flex。
- **linear-gradient 支持**：weasyprint **已验证支持元素背景渐变**（标题条用了 `linear-gradient(90deg,#BF360C,#E65100)`，像素采样确认多档橙色梯度渲染正确）。可放心用；但渐变文字颜色、多背景叠加这些更复杂的用法未验证，保守起见复杂场景用纯色。
- **中文换行**：气泡文字按 `int(bw/22)` 估算行数设高度，字数多要留足高度防止溢出出格。
- **服务器磁盘**：40G剩12G，够用但别堆积，用完清理 /tmp。
