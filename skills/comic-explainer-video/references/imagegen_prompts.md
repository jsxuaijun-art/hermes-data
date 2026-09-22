# ImageGen 生图规范（紫漫解释风）

> 完整可用风格目录见 `references/styles.md`。本文件保留「紫漫解释风」的详细出图要点；若用户选择「黑板手绘风」，则改用该文件中的固定生图串。

本文件固定「紫漫解释风」的 AI 生图风格，确保不同主题、不同批次产出的画面**风格统一、可复用**，与原参考视频 `video(7).mp4` 一致。

---

## 一、固定风格串（每次生图必带，放在 prompt 末尾）

```
American comic book style, flat vector illustration, purple and lavender color palette, bold white outlines, minimal shading, clean solid background, horizontal composition, 1920x1080
```

- 尺寸建议 `1536x1024`（横版），质量 `high`。
- 主体居中或偏一侧，为**顶部声明条**和**底部字幕**预留空间（画面上下留白）。

---

## 二、分镜 → Prompt 映射模板

每个镜头用一句英文描述画面，再追加上面的固定风格串。结构：

```
[场景主体] + [动作/状态] + [情绪/氛围] + [固定风格串]
```

### 通用钩子镜头
> A [人物角色] at a desk looking at [手机/屏幕] showing "[超低价/夸张数字]" advertisement, expression [纠结/震惊/犹豫], American comic book style, flat vector illustration, purple and lavender color palette, bold white outlines, minimal shading, clean solid background, horizontal composition, 1920x1080

### 机制 / 风险链条镜头
> An open ledger book with misaligned numbers and a tilted balance scale, a red warning symbol about [缺失申报/偷工减料], American comic book style, flat vector illustration, purple and lavender palette with red accents, bold white outlines, minimal shading, clean solid background, horizontal composition, 1920x1080

### 后果 / 冲击镜头
> A small company building enveloped by a giant translucent data network from above, on the desk a red tax penalty notice and a stamp reading "[非正常户/罚款]", tense oppressive mood, American comic book style, flat vector illustration, purple palette with red accents, bold white outlines, minimal shading, clean solid background, horizontal composition, 1920x1080

### 趋势 / 数据镜头
> A downward line chart drawn on a purple backdrop with a small figure looking up at it worried, American comic book style, flat vector illustration, purple and lavender palette, bold white outlines, minimal shading, clean solid background, horizontal composition, 1920x1080

### 两极分化 / 机会镜头
> An hourglass where the top is crowded and the bottom sparse, two different figures on each side, hopeful vs anxious, American comic book style, flat vector illustration, purple and lavender palette, bold white outlines, minimal shading, clean solid background, horizontal composition, 1920x1080

---

## 三、出图要点（保证可拼接成视频）

1. **一致性**：所有镜头必须包含同一固定风格串，避免混用写实/水彩等其他画风。
2. **人物一致性**：同一视频里若反复出现某角色，在 prompt 中固定其描述（性别、衣着、发型、姿态），例如 `a young male entrepreneur in a blue shirt, short black hair`。
3. **留白**：画面上下各留约 15% 空白，用于后期叠加字幕与声明条。
4. **红色克制**：仅风险/警示元素用红，主色始终为紫，避免画面碎片化。
5. **数量规划**：按分镜表逐镜出图，PoC 可先出 3 张（钩子/机制/后果）验证风格，确认后再批量补齐。
