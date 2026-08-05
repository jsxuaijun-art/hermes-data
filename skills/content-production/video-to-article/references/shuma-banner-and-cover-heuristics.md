# shuma 章节序号横幅 + 无识图封面启发式验收 — 2026.8.5 实战验证

生产案例：视频号《对公账户收入不如实申报》，国家税务总局官方号，2026-08-05 发表于「盈信税务0」草稿箱。

## shuma 数字序号横幅的使用（用户指定用法）

用户从 `shuma/` 文件夹调用了 **6 张数字横幅图**，指定当**章节序号**展示（不是当具体数字）。

**图片特征**：白底长条 1920×281（远宽于高的横幅/装饰条），tesseract OCR 识别出内容为数字 01-06。

**角色分配（6章节约完美匹配）**：
- shumabanner_01/02/03 → 上半篇三个"手法"小节
- shumabanner_04/05/06 → 下半篇三个"实操"小节（自查清单/补救三步/日常铁律）

**上传**：
```bash
SRC="/mnt/d/360MoveData/Users/Admin/Desktop/shuma"
n=1
for f in "$SRC"/*.jpg; do
  base64 "$f" | ssh -o StrictHostKeyChecking=no root@47.103.27.171 "base64 -d > /var/www/html/images/shumabanner_0${n}.jpg"
  n=$((n+1))
done
```
正文引用：`![章节序号01](http://127.0.0.1:8080/images/shumabanner_01.jpg)`

**⚠️ OCR 歧义陷阱**：图3 tesseract 给出 03 或 035 两个结果。**必须人工向用户确认**（用户确认是 03），不能靠 OCR 自行断定。遇到单张图片数字有歧义，先问再传。

## 02 刘润红蓝撞色风格配套使用

- 上半篇章节标题前缀用红色 `#FF2941`，下半篇用蓝色 `#0052FF`
- 手法名/关键数字/法律后果用红色强调
- 3列表格用 `overflow-x:auto` 包裹防手机溢出
- 该风格 CSS 在服务器 `/etc/wenyan/themes/02-liurun-honglan.css`，发布时 `-c` 指定

## 无识图模型时的封面启发式验收

当驱动模型不支持识图（vision_analyze 也报"模型不支持 image 输入"）时，PIL 像素分析把关：

```python
from PIL import Image
from collections import Counter
im = Image.open('/tmp/cand.jpg').convert('RGB')
small = im.resize((80,60)); px = list(small.getdata())
total = len(px)
skin = sum(1 for r,g,b in px
           if r>95 and g>40 and b>20 and (max(r,g,b)-min(r,g,b))>15
           and abs(r-g)>15 and r>g and r>b)
skin_pct = skin/total*100           # >12% ⇒ 疑似人物肖像 ⇒ 弃用
cnt = Counter((r//40*40,g//40*40,b//40*40) for r,g,b in px)
top_colors = cnt.most_common(5)     # 单色>80% ⇒ 疑似纯色块 ⇒ 弃用
```

本案例结果：肤色2%（非肖像）、主色灰(120,120,120)74%（中性办公风）、竖版800×1200 → 判定可用。

**边界（诚实告知）**：启发式只能排除明显风险（人像/纯色块），**不能替代肉眼**。仍建议向用户明示"我看不了图，请在后台确认封面是否合适"。

## 已发布

- 标题（用户3选1选了提问悬念式）："公账上的钱不申报，税局是怎么发现的？"
- Media ID: ZIKXbXZdS_X3B-GDVk11ByF9Ryu8HZfX2eOrVFN5OGwqmfduUJi_tGklSWfB5MrN
- 结构：上半篇三违规手法(shuma01-03) + 下半篇自查补救铁律(shuma04-06) + GEO段落 + 品牌落款 + CTA
- 发布命令用 `-c /etc/wenyan/themes/02-liurun-honglan.css`
