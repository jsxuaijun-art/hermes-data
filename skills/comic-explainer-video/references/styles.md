# 动画风格目录

`comic-explainer-video` skill 支持多种画风。每次接到制作命令时，**必须先询问用户选择哪一种风格**，再按对应风格的固定生图串生成画面，确保整批画面统一。

---

## 1. 紫漫解释风（Purple Comic Explainer）

**来源**：原 `video(7).mp4`（律师行业去泡沫化视频）。

**视觉特征**：
- 背景：浅紫 / 薰衣草纯色背景，明亮。
- 人物/物体：美式漫画风，平涂矢量插画，粗白色描边，极少阴影。
- 强调色：黄色字幕高亮，红色点缀风险/警示元素。
- 整体感觉：像商业漫画书的一页，信息密度高、现代感强。

**适合主题**：行业科普、风险警示、趋势解读、反共识观点、实用避坑指南。

**固定生图串（每次必带）**：
```
American comic book style, flat vector illustration, purple and lavender color palette, bold white outlines, minimal shading, clean solid background, horizontal composition, 1920x1080
```

**样例 prompt（钩子镜头）**：
```
A young businessman at a desk looking at a smartphone showing "99 yuan bookkeeping" advertisement, expression conflicted between temptation and worry, American comic book style, flat vector illustration, purple and lavender color palette, bold white outlines, minimal shading, clean solid background, horizontal composition, 1920x1080
```

---

## 2. 黑板手绘风（Chalkboard Hand-drawn）

**来源**：`video(22).mp4`（人、鸡、米的隐喻寓言）。

**视觉特征**：
- 背景：深灰 / 墨绿黑板底色（dark slate / chalkboard green），大面积留白。
- 人物/物体：白色手绘线条小人，圆头、极简表情（或五官省略），肢体语言夸张。
- 强调色：极少色彩，仅用金黄/米黄点缀关键物品（如米粒）。
- 整体感觉：黑板涂鸦、简笔手绘、哲理寓言、讲道理的轻动画。

**适合主题**：哲理隐喻、人际关系、人性观察、情绪管理、轻寓言故事、心理学概念。

**固定生图串（每次必带）**：
```
Chalkboard hand-drawn animation style, white line-art characters on a dark slate green background, minimalist doodle, simple stick-figure-like people with round heads and expressive body language, minimal color accents only golden yellow for key objects, clean composition, horizontal 1920x1080
```

**样例 prompt（钩子镜头）**：
```
A simple white line-art man running angrily after a white line-art chicken on a dark slate green chalkboard background, motion lines, minimalist doodle, expressive body language, chalkboard hand-drawn animation style, horizontal 1920x1080
```

---

## 风格选择指引

| 用户想做的内容 | 推荐风格 | 原因 |
|---|---|---|
| 行业趋势 / 风险警示 / 反共识 | 紫漫解释风 | 色彩鲜明、信息密度高、适合数据和警示 |
| 人性道理 / 人际隐喻 / 轻寓言 | 黑板手绘风 | 留白多、手绘感强、更适合讲故事和讲理 |
| 用户明确指定"像 video(7)" | 紫漫解释风 | 直接对应 |
| 用户明确指定"像 video(22)" | 黑板手绘风 | 直接对应 |

**注意**：同一支视频只能使用一种风格，禁止混用。
