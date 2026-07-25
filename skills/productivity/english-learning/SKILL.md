---
name: english-learning
description: 英语学习与翻译助手 — 中英互译、财税英语、日常英语学习
version: 1.1.0
author: Hermes Agent
---

# 英语学习与翻译 Skill

本技能用于协助中文用户进行英语学习与翻译，特别侧重财税行业场景。

## 功能概览

| 功能 | 说明 |
|------|------|
| 中英互译 | 精准翻译，保留专业术语 |
| 财税英语 | 会计/税务/审计/外贸术语与表达 |
| 英语学习 | 语法讲解、句型拆解、学习方法 |
| 口语练习 | 纠音建议、口语化改写 |
| 写作润色 | 邮件/报告/合同英文改写 |

---

## 翻译模式

### 1. 标准翻译

输入格式：`翻译 >>> 待翻译文本`

输出格式：
- **原文**：xxx
- **译文**：xxx
- **要点**：（如果有专业术语或特殊表达，标注说明）

### 2. 财税专业翻译

针对会计科目、税务条款、审计报告、外贸合同等场景，确保术语准确。

常见财税术语对照：

| 中文 | English |
|------|---------|
| 代理记账 | bookkeeping agency / outsourced bookkeeping |
| 税务合规 | tax compliance |
| 增值税专用发票 | special VAT invoice (special VAT invoice for deduction) |
| 企业所得税 | corporate income tax (CIT) |
| 个人所得税 | individual income tax (IIT) |
| 小规模纳税人 | small-scale taxpayer |
| 一般纳税人 | general taxpayer |
| 进项税抵扣 | input VAT deduction |
| 汇算清缴 | annual tax filing / final settlement |
| 高新技术企业 | High and New Technology Enterprise (HNTE) |
| 研发费用加计扣除 | R&D expense super deduction |
| 税务筹划 | tax planning |
| 税务稽查 | tax audit / tax inspection |
| 注销登记 | cancellation of registration |
| 海关监管代码 | customs supervisory code |
| 市场采购贸易 | market procurement trade |
| 出口退税 | export tax rebate / export refund |

### 3. 句子/段落翻译示例

输入：`财税翻译 >>> 一般纳税人可以开具增值税专用发票，小规模纳税人通常只能开具增值税普通发票。`

输出：
- **译文**：General taxpayers can issue special VAT invoices, while small-scale taxpayers can generally only issue ordinary VAT invoices.
- **要点**："增值税专用发票"译为 "special VAT invoice"，注意区分 "普通发票" ordinary VAT invoice。

---

## 英语学习模式

### 1. 语法讲解

输入格式：`语法 >>> 你的问题`

例如：`语法 >>> "should have done" 和 "must have done" 的区别`

输出：简明讲解 + 例句对比。

### 2. 句型拆解

输入格式：`拆句 >>> 英文句子`

逐层分析句子结构（主谓宾定状补），帮助理解长难句。

### 3. 口语化改写

输入格式：`口语 >>> 英文句子`

把正式/书面英语改成自然口语表达。

### 4. 写作润色

输入格式：`润色 >>> 你的英文草稿`

优化语法、用词、语气，给出修改说明。

---

## 词汇学习模式（Vocabulary Learning）

### 5. 艾宾浩斯记忆法（Ebbinghaus Spaced Repetition）

**核心理念：** 遗忘曲线是科学事实（20分钟忘42%，1小时忘56%，1天后忘74%），但"1/2/4/7/15天复习节奏"是后人推导的近似方案，非艾宾浩斯原版（原版使用无意义音节，与记单词不同）。

**实战价值与局限：**

| 优势 | 说明 |
|------|------|
| 规律可预期 | 不用动脑子想"今天复习啥"，按表走就行 |
| 迫近感制造行为 | 知道哪天该复习，比随缘背诵更容易坚持 |
| 间隔递增 | 1→2→4→7→15，比每天复习效率高得多 |

| 局限 | 说明 |
|------|------|
| 高峰期任务重 | 第15天左右一天要复习5-6个单元，每单元50词×6=300词 |
| 纯中英对照效果有限 | 真正记住需要语境+输出，光看释义填英文是"猜词"不是"用词" |
| 成人瓶颈 | 2500词能认 ≠ 2500词会用，输出才是真掌握 |

**一句话总结：** 艾宾浩斯计划表是一个好用的"复习提醒器"，不是记忆神器。执行比方法重要。

### 6. 词根词缀记忆法（Root & Affix Method）

**核心逻辑：** 英语单词80%由词根+前缀+后缀构成。掌握常见词根可大幅提升词汇解析和记忆效率。

**词根信息来源：**
- **etymonline.com** — 权威在线词源词典，免费可查
- **Python `etymology` 库** — 封装的词源查询接口
- **优词网 quword.com / 趣词 quword.com** — 中文词根词缀词典

**常见词根示例：**

| 词根 | 含义 | 例词 |
|------|------|------|
| spect | 看 | inspect, respect, prospect, spectator |
| port | 携带 | export, import, transport, portable |
| dict | 说 | dictate, predict, contradict, dictionary |
| duct/duc | 引导 | conduct, produce, introduce, reduce |
| struct | 建造 | construct, destroy, instruct, structure |
| tract | 拉 | attract, extract, contract, subtract |
| aud | 听 | audio, audience, auditorium |
| vis/vid | 看 | vision, visible, video, evidence |

### 7. 词汇数据来源获取（中国网络环境）

在中国网络环境中获取英语词汇列表（IELTS/TOEFL/四六级等）经常遇到各种渠道限制。详细实操指南见：

`references/vocabulary-source-acquisition-cn.md`

核心工作流：**搜狗搜索 → 筛选标题 → 让用户手动下载 → 我转格式**。不要硬耗5+次搜索请求。

### 已有本地数据（零成本可用）

- **en_50k.txt**：14441词含频率计数，本地已缓存。`grep -i "^word " ~/memories/en_50k.txt` 可查任意词频，零token成本。
- **高考3875词汇**：内建在 `vocab-memory-book` skill 的 `scripts/build_root.py`
- 当外部渠道不可达时，可用频率表（排名2000-8000）构建近似IELTS词表（但无中文释义，需用户补充）

## 词汇默写书生成工作流（针对高考/中考词汇）

**适用场景：** 用户有词汇列表（word + phonetic + definition），需要生成可打印的艾宾浩斯复习默写书。

**工作流：先试后全 → 15词实验版验收 → 全量铺量**
```python
# 第一步：解析词汇文件（每行格式：word [phonetic]  pos. definition）
# 第二步：选15个词根清晰的词做实验版（trial-first）
# 第三步：交付Word .docx验收 → 改到满意  
# 第四步：启动全量（3800+词，78单元×50词）
```

### 复习节奏（最终版 v9，2026-07-03 用户确认）
全量间隔为 `[1, 2, 4, 7, 15, 30]` 天（⚠️ Day 30 不是 Day 31，用户明确修正）。

每轮方向交替，不能全相同方向：

| 轮次 | 方向 | 版式 | 有✓□✗□? |
|:--:|:--:|:--|:--:|
| Day 1 学习 | **英→中** | 单栏2行卡片 | ❌ 无正确/错误行 |
| Day 2 复习① | **英→中** | 六栏 | ❌ 无✓□✗□ |
| Day 4 复习② | **中→英** | 六栏 | ❌ 无✓□✗□ |
| Day 7 复习③ | **音标→英+中** | 六栏 | ❌ 无✓□✗□ |
| Day 15 复习④ | **中→英**（仅⭐词） | 六栏 | ❌ 无✓□✗□ |
| Day 30 复习⑤ | **混合**（英→中 / 中→英 各半） | 六栏 | ❌ 无✓□✗□ |

### 第一轮学习特殊规则
- 不显示「正确/错误」行（用户要求，避免学习初始阶段被错误率打击）
- 每词2行卡片：词条行 | 写作指数行（第3行去掉）
- 中文释义+括号下划线**同一行**，右对齐
- 释义短时下划线自动**延伸到右边框**

### 非字母顺序（用户明确要求）
每个板块用独立随机种子打乱词序。字母顺序=按位置记词，是记忆作弊。
```python
random.seed(42)  # Day 2
random.seed(77)  # Day 4
random.seed(123) # Day 7
random.seed(555) # Day 15
random.seed(999) # Day 30
```

### 按词根（root）核心分组
⚠️ **绝不能按前缀分组**（如 ab-, ac-/ad- 只是首字母相同，词根本身无关）。
必须以词根（root）为核心，共享同一拉丁/希腊词根的词汇集中学习。前缀和后缀作为辅助拆解工具。

公式：`单词 = 前缀(prefix) + 词根(root) + 后缀(suffix)`

✅ 用户提供的正确示例：`pesticide = pest(瘟疫) + cide(杀)` — pest 和 cide 都是词根。
❌ 错误做法：`ab-组: abandon, abnormal, aboard` — 前缀一样但词根不同，不能放一起。

已验证的12组词根（完整数据见 `references/vocabulary-50-words-12-roots.md`）：
`tract / press / port / fer / cess-cede / spect / struct / rupt / mit-miss / dict / sist / pend-pens`

### 六栏紧凑排版（对标上海中考默写本）
参考样稿：`D:\360MoveData\Users\Admin\Desktop\上海中考英语单词_第2-3页.pdf`

```
┌─────┬─────────────┬──────────────┬─────┬─────────────┬──────────────┐
│ 序号│  原文       │  填空        │ 序号│  原文       │  填空        │
├─────┼─────────────┼──────────────┼─────┼─────────────┼──────────────┤
│  1  │ ★ abstract │ (＿＿＿＿)   │ 26  │ ★ express  │ (＿＿＿＿)   │
│  2  │ ★ attract  │ (＿＿＿＿)   │ 27  │ ★ impress  │ (＿＿＿＿)   │
```

列宽度（2026-07-03 v9 用户确认最终值）：
- `序号列 = Cm(0.25)` — 仅够显示"50"，不能再宽
- `内容列 = Cm(3.5)` — 显示英文/中文
- `填空列 = Cm(5.25)` — 剩余宽度全给填空
- `[Cm(0.25), Cm(3.5), Cm(5.25), Cm(0.25), Cm(3.5), Cm(5.25)]`

⚠️ 复习页**不显示 ✓□✗□**（用户要求去掉）。

### 页面标题
所有页面的第一行必须 **CENTER 居中排列**（用户明确要求，2026-07-03 v9）：
- `DAY 1  学习页` → 居中
- `DAY 2  英→中` → 居中
- 所有复习轮次以此类推

### 每页顶部表头
```python
# 仅3列：姓名 | 日期 | 正确数（无「正确率」！）
['姓名: ___________', '日期: ___________', '正确: ___/N']
```
⚠️ 用户明确要求**去掉正确率**（2026-07-03 v6）。

### 封面设计（蓝色海洋帆船风格，满铺全页）
- 页边距=0，背景表格撑满 A4 全宽（11906 dxa）
- 封面后必须 **add_section()** 创建新节，恢复内容页边距 0.8cm
- 颜色方案：深蓝底 `0A2463`（#0A2463），白字，金色副标题 `FFD766`
- 公司信息：苏州盈信企业管理有限公司 | 公司注册·专注财税二十五年 | 18912633863

封面结构：
```python
build_cover(doc)  # margins=0
new_sec = doc.add_section()  # 内容页新节
new_sec.top_margin = Cm(0.8); new_sec.left_margin = Cm(0.8)
```

### 写作指数数据来源
⚠️ **不要编造频率数据**（用户要求"客观不可臆造"）。

正确做法：下载公开英文词频库，本地 grep 查频次：
```python
# 下载 FrequencyWords 数据（零成本，14K词）
curl -sL "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2016/en/en_50k.txt"
# 查频次
grep -i "^abstract " freq_file.txt  # 返回: abstract 1264
# 转为1-5星：>40000=5星, >10000=4星, >4000=3星, >1500=2星, else=1星
```
完整 3800+ 词查一遍 = 本地 grep，**零 token 成本**。

### python-docx 路径陷阱
⚠️ 在 WSL 中运行 python-docx，路径**不能写** `D:\...` 或 `C:\...`。
必须用 `/mnt/c/Users/Admin/Desktop/...` 格式。
`D:\...` 写法会把反斜杠当成文件名的一部分，存到错误位置，Windows 找不到。

已验证的用户桌面（C盘主桌面，非 D盘）：
- WSL路径：`/mnt/c/Users/Admin/Desktop/`
- Windows路径：`C:\Users\Admin\Desktop\`

已验证的12组词根（50词实验版）保存于 `references/vocabulary-50-words-12-roots.md`。

**Trial-First 工作流（省token先用后扩）：**

当用户要求的设计较复杂（多页、多表格、多种设计元素）时，先出15词小样验证再全量生成：

```
Step 1: 确认词汇源文件格式和总词数
Step 2: 从词表头部取15个有代表性的词（优先选词根清晰、写作高频的词）
Step 3: 手动配齐 15 个词的完整信息：
        词根拆解 + 联想记忆 + 派生词 + 词组 + 写作频率 + ★标记
Step 4: 生成完整设计的Word文档（按 v2 布局，见下文）
Step 5: 交付验收
Step 6: 用户满意 → 全量生成（约78个单元×50词，词根自动匹配）
        不满意 → 调整后重复 Step 4
```

**什么时候用 Trial-First：**
- 设计复杂度高（多表格、多设计元素）
- 用户可能有未表达的排版偏好
- 全量生成耗时超过 30 秒

**Word 文档结构（v7 布局，2026-07-03 60词实验版验证）：**

```\n① 封面        — "一句实话" quote + 艾宾浩斯标注\n② 使用方法     — 说明 + 日程表（方向切换标红，Day 4/7切换方向）\n③ 📖 英→中学习页   — 单栏卡片，按词根分组排列，无正确/错误行\n④ 英→中 六栏复习   — Day 2\n⑤ 🖊 中→英 六栏    — Day 4\n⑥ 🔊 音标→英+中 六栏 — Day 7\n⑦ ★ 中→英 六栏     — Day 15（仅⭐高频词）\n⑧ 🎲 混合终测 六栏  — Day 31\n⑨ ✍ 高频写作词速查 — 按词根分组\n⑩ 封底           — "启动完整版" CTA\n```

**每页顶部（所有板块都有，颜色区分板块类型）：**\n\n```\n姓名: ___________  日期: ___________  正确: ___/N\n```\n⚠️ **不显示「正确率」**（用户明确要求去掉，2026-07-03 v6）\n\n**学习页（Day 1）—— 单栏卡片，维持现状，无正确/错误行：**\n\n| 行 | 左列 | 右列 |\n|:--:|:--|:--|\n| ① | ★ abstract [ˈæbstrækt] v. (蓝灰底 F0F4F8) | 抽象的（作品）；摘要  `(＿＿＿＿＿＿)` **同一行，右对齐** |\n| ② | 🔬 abstract = abs-(离开) + tract(拉) → 从具体中抽离 (蓝#2C3E50, 7.5pt italic) | _(空)_ |\n| ③ | 写作频率: ●●●○○ (灰) | ⭐ 高频词 (红 C0392B) |\n\n**复习页（Day 2+）—— 六栏紧凑排版（v7 新增，对标上海中考默写本）：**\n\n参考样稿：`D:\\360MoveData\\Users\\Admin\\Desktop\\上海中考英语单词_第2-3页.pdf`\n\n```\n┌─────┬─────────────┬──────────────┬─────┬─────────────┬──────────────┐\n│ 编号│  原文       │  填空        │ 编号│  原文       │  填空        │\n├─────┼─────────────┼──────────────┼─────┼─────────────┼──────────────┤\n│  1  │ ★ abstract │ (＿＿＿＿)✓□✗□│ 32  │ ★ express  │ (＿＿＿＿)✓□✗□│\n│  2  │ ★ attract  │ (＿＿＿＿)✓□✗□│ 33  │ ★ impress  │ (＿＿＿＿)✓□✗□│\n│ ... │            │              │ ... │            │              │\n└─────┴─────────────┴──────────────┴─────┴─────────────┴──────────────┘\n```\n\n每行 2 个词条，左栏 1-31 号，右栏 32-61 号。不同复习轮次切换原文列内容：\n\n| 轮次 | 原文列 | 填空列 |\n|:--:|:--|:--|\n| 英→中 | 英文单词 | 写中文 `(＿＿)` |\n| 中→英 | 中文释义 | 写英文 `(＿＿)` |\n| 音标→英+中 | 🔊音标 | 英`[＿＿]`中`[＿＿]` |\n| 混合 | 英文/中文交替 | 反向填空 |\n\n**六栏排版优势：** 相比单栏卡片，每页从约8词→约60词，省纸约85%。61词实验版仅需2页复习（vs 单栏需8页）。

**词数据完整结构：**

```python
WORD_ENTRY = {
    "word": "abandon",           # 主词条
    "phonetic": "[əˈbændən]",   # 音标（带方括号）
    "pos": "v.",                 # 词性
    "definition": "抛弃，舍弃，放弃",  # 中文释义
    "root": "a-(加强) + band(命令/控制) → 被命令离开",  # 词根拆解
    "memory": "a+band+on → 乐队(on)被抛弃解散",          # 联想记忆
    "derived": "abandoned a.被遗弃的; abandonment n.放弃",  # 派生词
    "phrases": "abandon hope 放弃希望; abandon ship 弃船",  # 词组搭配
    "star": True,                # True = 高频写作词，显示 ★
    "wf": 3                      # 写作频率 1-5
}
```

**高频写作词速查表结构：**
```
5 列:  ★ | 单词 | 释义 | 写作频率 | 词组举例
表头: 红底 C0392B
```

**设计要点：**
- ★ 标记高频写作词，红色标注（C0392B）
- 写作频率用 ●●●●○ 圆点图显示（wf: 1-5分）
- 词根拆解用蓝灰色（#557A95），联想记忆用灰色（#7F8C8D）
- 派生词用棕色（#8B4513），词组用深蓝（#2E4057）
- 乱序抽查页不加任何提示（纯测试）
- 封面用黄色背景 quote box（#FFF8E1 + #E6C300 border）
- 正确打钩行放在每个词最后（引导用户自检）

(已合并到上方，避免重复)
```

**全量生成（3800+词）：**
- 单元划分：50词/单元 → 78个单元（末单元25词）
- 词根信息：自动匹配常见词根词缀表（约200组），未匹配到的只显示词性和释义
- 高频写作词标记：基于考频数据或内置权重表
- 乱序抽查页：每10单元插一页，随机抽取20词
- 文档格式用 `productivity/word-documents` skill 的 python-docx 模板生成

**注意事项：**
- 默认仅出 .docx 版本，不出 Markdown（用户偏好）
- 文件放桌面路径 `/mnt/c/Users/Admin/Desktop/`（C盘主桌面）
- python-docx 路径要写 `/mnt/...` 格式，不能写 `D:\...`（WSL Python 路径陷阱）
- 用 trial-first 模式先出15词验收，再全量生成

**词汇文件格式（标准）：**
```
word [phonetic]  part_of_speech. definition
abandon [əˈbændən]  v.抛弃，舍弃，放弃
ability [əˈbɪlɪtɪ]  n. 能力；才能
```

(已合并到上方"复习节奏"章节，避免重复)

**实用设计建议：**
- 每10单元插一个"乱序抽查页"（打乱顺序，防止按位置记词）
- 末尾附"高频写作词表"（从总词表中挑出写作常用词，标记★）
- 封面写一句实话（让用户知道这是90天工程）
- 文档格式用 `word-documents` skill 的 python-docx 模板生成

**Word文档生成参考：** 具体docx生成代码见 `productivity/word-documents` skill，使用python-docx格式化表格+中文排版。

**注意事项：**
- 默认仅出 .docx 版本，不出 Markdown（用户偏好）
- **文件路径陷阱：** 在 WSL 中运行 python-docx，路径不能写 `D:\...` 或 `C:\...`。必须用 `/mnt/c/Users/Admin/Desktop/` 格式。`D:\...` 写法会把反斜杠当成文件名的一部分，存到错误位置，Windows 找不到。
- 用户桌面路径（已验证）：`/mnt/c/Users/Admin/Desktop/`（对应 Windows `C:\Users\Admin\Desktop\`）
- 不用 D 盘路径（即便物理存在，用户不认）
- 如果用户同时要求添加词根信息，优先从 `references/vocabulary-workbook-patterns.md` 的61词实验版根词根组数据中取，或从词汇文件扫描常见拉丁词根
- 词根信息自动查询只针对已掌握的词汇列表，不适用于新东方等版权书的词根内容（需购正版）

---

## 学习资源推荐

### 实用工具
- **查词**：https://www.collinsdictionary.com/（柯林斯词典，英英释义+例句）
- **搭配**：https://ludwig.guru/（查地道搭配和用法）
- **发音**：YouGlish（YouTube 真实语料发音，按口音筛选）
- **词源**：https://www.etymonline.com/cn（在线英语词源词典，词根词缀查词）
- **词根词缀**：https://www.quword.com/root（趣词词根词典，中文词根大全）
- **AI助手**：直接用本技能即可

### 词汇学习工具
- **Anki** — 开源间隔重复记忆软件，支持PC/手机
  - 桌面版：https://apps.ankiweb.net/
  - 手机版：各应用商店搜 AnkiDroid（安卓）/ AnkiMobile（iOS）
  - 词牌资源：https://ankiweb.net/shared/decks/（搜高考/高中英语）
- **桌面词汇文件生成**：见本技能 `词汇学习模式` 章节 + `references/vocabulary-workbook-patterns.md`
- **Word文档生成**：用 `productivity/word-documents` skill 的 python-docx 模板

### 财税英语参考资料
- IFRS/IAS 国际财务报告准则英文版
- IRS 官方出版物（美国税务英语）
- China Tax Alert / PwC Tax News（四大税务快讯中英双语）

---

## 学习建议（针对财税从业者）

1. **先读专业英文资料**：海关公告、税务总局英文版文件、IFRS准则
2. **关注高频术语**：先掌握税务/会计/外贸三类核心术语
3. **从阅读入手**：英文财税文章 → 理解后尝试英译中 → 再中译英
4. **每天15分钟**：比每周2小时更有效

---

## 使用示例

```
你 > 翻译 >>> 我们公司提供公司注册、代理记账和税务合规咨询服务。
我 > All in the skill output format.

你 > 财税翻译 >>> 研发费用加计扣除政策允许企业在计算应纳税所得额时，按照实际发生研发费用的100%加计扣除。
我 > Professional translation with term notes.

你 > 语法 >>> "comply with" 和 "comply to" 哪个对？
我 > "comply with" 才是正确的搭配，"comply to" 是错误的。
```
