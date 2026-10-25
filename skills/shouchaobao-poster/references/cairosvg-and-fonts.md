# cairosvg + CJK 手写字体（参照）

## 手写中文字体（jsdelivr 可直连；google/fonts 与 fonts.gstatic.com 在 CN 不可达）
```bash
mkdir -p /usr/share/fonts/truetype/custom
for n in mashanzheng/MaShanZheng-Regular zcoolkuaile/ZCOOLKuaiLe-Regular zhimangxing/ZhiMangXing-Regular; do
  f=$(basename $n).ttf
  curl -L -o /usr/share/fonts/truetype/custom/$f "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/$n.ttf"
done
fc-cache -f
fc-list | grep -iE 'ma shan|zcool|zhi mang'
```
- Ma Shan Zheng（毛笔）— 粗犷大标题
- ZCOOL KuaiLe（圆润）— 活泼标题/标签
- Zhi Mang Xing（潦草连笔）— 点缀/小字
- 正文如需整洁用 `/usr/share/fonts/truetype/wqy/wqy-microhei-regular.ttf`（纯 TrueType，ReportLab 也能加载）。
- 这些字体都是 TrueType（magic `\x00\x01\x00\x00`），PIL/reportlab/toy 文本都能吃；Noto CJK 是 CFF/OTF，cairosvg 可但 reportlab/PIL 不行。

## 渲染（cairosvg / system python）
```bash
pip install cairosvg   # 装进 /usr/bin/python3，不是 execute_code 沙箱核
```
```python
# 在 execute_code 里这样调（system python 才有 cairosvg）：
import subprocess
PY = "/usr/bin/python3"
code = 'import cairosvg; '
code += 'cairosvg.svg2png(url="/p.svg", write_to="/o.png", output_width=3300, output_height=4668); '
code += 'cairosvg.svg2pdf(url="/p.svg", write_to="/o.pdf", output_width=1100, output_height=1556)'
subprocess.run([PY, "-c", code], check=True, capture_output=True, timeout=300)
```
小尺寸（900×1273）先渲染做快速自检，几秒内完成；再出 300dpi 大图。

## 无视觉时的验证
- 抽样统计颜色类别，确认非纯黑、关键色都在：
```python
from PIL import Image
from collections import Counter
im = Image.open("/o.png").convert("RGB"); w,h = im.size; px = im.load(); c = Counter()
for y in range(0,h,6):
  for x in range(0,w,6):
    p = px[x,y]; c[p]+=1
    if p[0]>150 and p[1]<95 and p[2]<95: reds+=1      # 旗/标题/灯笼
    if p[1]>110 and p[0]<120 and p[2]<120: greens+=1  # 山川场景
print(len(c), c.most_common(3))
```
- 验证手写体真渲染：同一字形分别用候选字体和 wqy 渲染，`sum(v<128 for v in gray.getdata())` 墨迹像素数必须不同。

## 排错速查
- 整页变黑 → 删掉含 feTurbulence/feColorMatrix 的满页 grain 滤镜。
- "not enough arguments for format string" → `<filter>` 里有字面 `%`，改用 f-string。
- execute_code 里 ImportError cairosvg → 用 `subprocess.run(["/usr/bin/python3",...])`。
