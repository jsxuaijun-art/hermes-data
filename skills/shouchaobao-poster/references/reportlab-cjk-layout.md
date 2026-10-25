# ReportLab 中文单页布局引擎（测宽 + 自动缩放）

可复制的骨架：量出每块文字真实高度 → 选缩放因子使左右两栏都装进可用区 → 以同一测量函数绘制。**绘制与测量必须共用同一套函数**，否则改一处漏一处就错位。

## 字体注册
```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont('WQY', '/usr/share/fonts/truetype/wqy/wqy-microhei-regular.ttf'))
# reportlab 不能加载 Noto CJK 的 .ttc/.otf（CFF 轮廓报 "postscript outlines are not supported"）
```

## 按真实宽度换行（不要按字数）
```python
def cwrap(text, fs, maxw):
    lines, cur, w = [], '', 0
    for ch in text:
        cw = pdfmetrics.stringWidth(ch, 'WQY', fs)
        if w + cw > maxw and cur:
            lines.append(cur); cur, w = ch, cw
        else:
            cur += ch; w += cw
    if cur: lines.append(cur)
    return lines
```

## 每块高度（block_height）+ 板块高
块类型与高度：
- `para(text,fs,lh)` → `len(cwrap(text,fs,COLCONT))*lh`
- `bullet(text,fs,lh)` → 星号占 `fs+5` 宽，只剩 `COLCONT-(fs+6)` 可排文字
- `head` → 单行 `lh`；`center` → 同 para；`deco` → 自身高度
- `timeline(rows,fs,lh)` → 每行 `sum(len(cwrap(txt,fs,COLCONT-62))*lh + 2)`，竖向参考线长度用总行数算
- `poem(text,author,fs,lh)` → `(len(cwrap(text))+len(cwrap(author)))*(lh) + 14`（引号另占行内缩进）

板块盒高 = 内容高 + 约 34（标题胶囊留白）。板块间再留 ~10。

## 缩放因子选择（保证单页无溢出）
```python
AVAIL = TOP - BOTTOM          # 顶横幅底 ~ 底部签写栏顶
SCALE = 1.0
for cs in [1.0,0.96,0.92,0.88,0.84,0.80,0.76,0.72,0.68]:
    SCALE = cs
    lh = col_total(LSPEC); rh = col_total(RSPEC)
    if lh <= AVAIL and rh <= AVAIL:
        break
# 绘制时所有 fs、lh 都乘 SCALE，box 高用同一 section_height() 重算
```

## 单页确认（无视觉时的验证）
```bash
pdfinfo xxx.pdf | grep Pages        # 必须 = 1
# python fitz:  d[0].get_text() 检查所有板块文字都在
```

## 结构约定（数据驱动，避免散乱堆坐标）
- 每栏 = 板块列表；每板块 = `(标题, 边框色, 底色, [块,...])`。
- 画板块函数先 `section_height()` 定盒高，再画盒子 → 标题胶囊 → 逐块 on top-26 起排。
- 两栏对称：`Lx=M`，`Rx=M+COLW+GW`，COLW=(W-2M-GW)/2，GW≈14。

## 易踩 bug
- 叠代里取「内容」下标取错（元组 `(标题,edge,bg,content)` 内容在 [3] 不是 [2]，[2] 是 bg 颜色 → "Color object is not iterable"）。
- `len()` 套在整型上行数 → "object of type int has no len()"。行数别预写成 1。
- 忘乘 SCALE 的地方导致盒高与文字量不一致 → 用同一函数出高度就不会漂移。
