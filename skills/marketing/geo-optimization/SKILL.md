---
name: geo-optimization
description: 生成式引擎优化（GEO）完整方法论 — 覆盖理论框架、内容工程、提示词模板、八大平台实操指南。让品牌信息被 AI 搜索采纳为"第一句话"。
triggers:
  - User asks about GEO / 生成式引擎优化 / AI搜索优化
  - User wants to optimize brand content for ChatGPT, DeepSeek, 豆包, Perplexity, Gemini
  - User mentions "AI搜索" or "AI引用" or "AI可见性"
  - User asks about EEAT / DSS principle / 信源模型
  - User wants to create GEO-optimized brand content or case studies
  - User mentions 趣搜科技 / 源易信息 / 艾瑞GEO白皮书
  - User mentions 315黑帽GEO or 品牌知识图谱 or 场景卡位
  - User asks about GEO for 财税行业 / 代理记账 / 企业服务
  - User asks about 财务顾问 / 共享财务总监 / 财税高端定位 GEO
  - User mentions 投鼠忌器 / 合规财税 / 企业合规内容叙事
  - User asks about 网易号 / 163平台 / 网易自媒体
  - User asks about 新浪财经头条 / 新浪财经 / sina财经
  - User asks about 腾讯新闻 / 企鹅号 / om.qq / 腾讯元宝内容布局
  - User asks about 搜狐号 / 搜狐自媒体
  - User asks about 百家号 / baijiahao / 百度百家号
  - User asks about 今日头条 / 头条号 / 字节跳动 / toutiao
  - User asks about 知乎 / zhihu
  - User asks about 公众号 / 微信公众号 / wechat / 腾讯元宝
  - User wants GEO 实施路线图 or 品牌诊断
---

# GEO（生成式引擎优化）方法论

> SEO 抢位置，GEO 抢"第一句话"。

当用户把问题交给 AI，TA 不再愿意点十个蓝色链接找答案，而是期待一个"像有经验的朋友那样"的汇总判断。谁让 AI 愿意在第一句话里提到谁，谁就赢。

**GEO 的本质：** 不是 SEO 的替代，而是升维——从"让网页被搜到"到"让品牌被 AI 采纳进答案"。

## 快速入口

**当用户提到 GEO 或任何平台名时：**

1. 加载本技能（`skill_view(name='marketing/geo-optimization')`）
2. 判断用户提到的平台，加载对应的参考指南（位于同目录的 `references/` 下）：

| 平台 | 指南文件 | 目的 AI |
|------|---------|---------|
| **百家号** | references/baijia-platform-guide.md | 文心一言 |
| **知乎** | references/zhihu-geo-strategy.md | DeepSeek |
| **网易号** | references/163-hao-platform-guide.md | DeepSeek、豆包 |
| **新浪财经头条** | references/sina-finance-guide.md | DeepSeek、豆包、文心 |
| **腾讯新闻/企鹅号** | references/tencent-om-guide.md（平台指南）+ references/tencent-om-article-templates.md（文章模板） | 腾讯元宝 |
| **搜狐号** | references/sohu-hao-platform-guide.md | 各平台均衡 |
| **今日头条** | references/toutiao-platform-guide.md | 豆包 |
| **微信公众号** | references/wechat-platform-guide.md | 腾讯元宝 |

3. 如果用户泛泛问 GEO 而不指定平台，用下文理论部分回答，并在结尾列出 8 个平台的简介和适用场景
4. **用户偏好：中文交流，直接给能用的方案，不说废话**

---

## 一、GEO 三把钥匙

### ① 可引用（Evidence-Ready）
AI 不会空口断言，需要可溯源的证据：
- 权威媒体/机构页面
- 专家与真实用户的稳定口径
- 官方页面的清晰表述
- 客观的对比与指标

**操作：** 在 PR、内容、站点上扔出去的一切，是否便于 AI 链接与引用？

### ② 可理解（Machine-Readable）
把关键信息语义化：
- Schema.org / JSON-LD 的结构标注
- FAQ 块、参数表、时间与地点、价格
- 适用人群与场景、常见问题与禁忌
- 第三方背书与证据链接

**顺序：** 先信息建模，再做结构化。

### ③ 可采纳（Answer-Ready）
GEO 的终点不是"被抓到"，而是"被采纳进答案里"：
- 提供可拿来就用的判断框架
- 场景 → 标准 → 选项 → 取舍 → 注意事项
- 把"可执行的提纲"写在官网、PR、知乎专栏、行业媒体上

**一句话：** 被看见靠证据，被听懂靠结构，被采纳靠框架。

---

## 二、DSS 原则（源易信息方法论）

| 维度 | 含义 | 操作要点 |
|------|------|---------|
| **D** - Depth of Semantics（语义深度） | 信息丰富、分析深入、逻辑严密 | 提供有见解、有价值的语料，而非简单罗列 |
| **S** - Supported Data（数据支撑） | 基于可验证的事实、可靠数据 | 具体案例、量化数据、明确证据 |
| **S** - Authority Source（权威信源） | 发布者/平台的专业性和权威性 | 公认的专业机构、行业地位、可信背书 |

**"白帽 GEO"原则：** 拒绝"信息投毒"和"黑帽"技巧，真实性为核心。

---

## 三、三级信源模型（趣搜科技）

| 级别 | 类型 | 示例 | AI 权重 |
|------|------|------|---------|
| **T1 - 权威层** | 政府官网、学术机构、主流媒体、企业官网 | 总局官网、Bloomberg、企业官网 | 最高 |
| **T2 - 讨论层** | 社交媒体、论坛、垂类媒体 | 知乎专栏、行业媒体、小红书 | 中等 |
| **T3 - 噪音层** | 无验证数据的营销内容 | 纯软文、无数据支撑的推广文 | 最低（AI 会主动降权） |

> AI 的"反洗稿"能力大幅增强：同一句话如果只在品牌官网上找到，第三方信源中无迹可寻，将被归入低置信度池。

---

## 四、GEO vs SEO 对比

| 维度 | SEO | GEO |
|------|-----|-----|
| 目标 | 让网页排到搜索首页 | 让品牌被 AI 采纳进答案 |
| 核心 | 关键词排名+外链 | 证据链+结构化+可采纳框架 |
| 用户行为 | 点击链接浏览 | 直接获得答案 |
| 内容形态 | 文章+页面 | 结构化知识+可验证事实 |
| 效果周期 | 相对稳定 | 渐进增长（AI 知识库更新有滞后） |
| 评估方式 | 排名+流量+点击率 | 提及率+首推率+引用率 |
| 预算投入 | 成熟市场，竞争激烈 | 早期红利，投入产出比高 |

---

## 五、GEO 内容工程五步法

```
信息纠偏 → 语义增强 → 权威建构 → 打通抓取路径 → 适配平台偏好
```

### 内容优化策略

**用户三层解读：**
1. 用户身份解读（你是谁）
2. 用户使用场景（在什么情境下）
3. AI 搜索意图（想解决什么问题）

### 结构化内容 Schema 标记

必须使用的结构化标记类型：`FAQ`、`HowTo`、`Product`、`Article`、`Organization`、`LocalBusiness`、`Review`

### 多平台分发策略

| AI 平台 | 内容偏好 | 建议渠道 |
|---------|---------|---------|
| 豆包（字节） | 抖音生态内容 | 抖音、火山引擎 |
| 文心一言（百度） | 百度生态内容 | 百度百科、百家号、百度知道 |
| DeepSeek | 高质量长文 | 知乎、专业媒体 |
| 腾讯元宝 | 微信生态 | 公众号、视频号 |
| 通义千问（阿里） | 电商+技术 | 阿里系平台 |

---

## 六、品牌知识图谱构建

### 构建步骤
1. **聚合分散知识：** 收集各部门的知识（产品手册、技术参数、专利、认证报告、白皮书等）
2. **建立实体关系网络：** 品牌 → 产品 → 功效/功能 → 人群 → 工艺/技术，层层关联
3. **结构化输出：** 用 Schema.org 标准标记，形成 AI 可自动抓取的品牌知识库

### 传播策略
- 分析不同平台在 AI 信源中的权重
- 将关键信息布局在 AI 信任的节点（T1 信源优先）
- 监测 AI 信源分布，动态调整分发策略

---

## 七、315 黑帽 GEO 警示

| 违规类型 | 操作手法 | 后果 |
|---------|---------|------|
| 信息污染 | 海量重复内容、批量生成虚假宣传 | 信息疲劳、误导公众 |
| AI 投毒 | 机器刷互动数据、复制权威内容、虚构用户评价 | 品牌高曝光低信任 |
| 低价竞争 | 低价不承诺效果、虚假排名、夸大效果 | 扰乱行业秩序 |

**白帽 GEO 的核心立场：** 真实性是品牌在 AI 时代最坚固的护城河。

---

## 八、效果评估体系

| 指标类型 | 具体指标 | 说明 |
|---------|---------|------|
| **AI 可见性** | 品牌提及率、首推率、前3推荐率、心智占有率 | 品牌在 AI 回答中的表现 |
| **内容层** | 内容引用率、AI 品牌情感倾向、AI 品牌卖点 | 内容被引用的质量 |
| **技术层** | AI 引用信源分布 | 各信源被引用的频率和权重 |
| **业务层** | AI 线索转化率、品牌官网访问率 | AI 到业务的转化 |

### 监测方法
- 调用 AI 平台的 API 获取用户问题
- 定时模拟搜索测试（每天固定问题集）
- DRRR 归因模型（Discover → Recognize → Recommend → Rank）

---

## 九、品牌 GEO 行动清单

### 诊断阶段
- [ ] 在主流 AI 平台搜索品牌名，记录提及率
- [ ] 在主流 AI 平台搜索核心业务关键词，记录排名
- [ ] 对比竞品在 AI 中的表现
- [ ] 检查官网是否有结构化数据（Schema.org）

### 优化阶段
- [ ] 官网添加 JSON-LD 结构化数据（Organization, FAQ, Product）
- [ ] 在权威媒体/行业媒体布局品牌内容
- [ ] 建立"可信来源密度"——同一信息在多个 T1 信源出现
- [ ] 准备可验证的量化数据（客户案例、认证资质、检测报告）
- [ ] 创建 FAQ 页面覆盖用户可能问的 20+ 问题

### 监测阶段
- [ ] 建立 AI 搜索关键词监控（每天/每周）
- [ ] 跟踪品牌提及率和首推率变化
- [ ] 根据 AI 反馈调整内容策略
- [ ] 关注 AI 平台算法更新

---

## 十、财税行业 GEO 实战

### 诊断现状
在豆包/元宝/DeepSeek/文心搜索"苏州代理记账""苏州注册公司""苏州财税公司推荐"等关键词，记录 AI 回答中提到的公司名、排名顺序。

### 构建信源资产
- **T1 信源：** 企业官网结构化优化 — Schema.org（Organization, LocalBusiness, FAQ）
- **T1 信源：** 知乎专栏、百度百科词条、行业协会、地方政府财税平台
- **T2 信源：** 抖音/视频号/小红书内容矩阵
- **关键：** 所有平台统一核心数据口径

### 内容工程
- 核心标签：高级会计师（稀缺性）、16年老公司（稳定性）、1000+客户（规模）、90%转介绍（口碑）
- 结构化内容：FAQ 格式覆盖老板常见问题
- 场景化内容：苏州老板"注册公司选哪家""代理记账对比""公司注销流程"
- 数据佐证：客户案例量化

### 分发策略
- 豆包偏好 → 抖音内容
- 文心偏好 → 百度百科、百家号
- DeepSeek偏好 → 知乎长文
- 元宝偏好 → 公众号、视频号

### 通用实施路线图
```
第1周：    诊断评估 → 明确差距和机会
第2-3周：  信源建设 → 优化 T1 信源，补全缺失信息
第4-6周：  内容工程 → 生产 GEO 优化内容并分发
第7-8周：  效果追踪 → 监测 AI 可见性变化，调整策略
持续：     迭代优化 → 根据数据反馈持续调整
```

---

## 十一、场景卡位四步法（趣搜科技方法论）

1. **诊断：** 品牌目前在各 AI 平台的可见度
2. **定位：** 确定品牌在哪些用户场景中最容易被提问
3. **卡位：** 在关键场景中布局 T1 级信源内容
4. **强化：** 通过多平台一致表述和数据验证加固信任

---

## 十二、提示词模板

本技能包含以下 prompt 模板文件（见 `templates/` 目录）：

| 文件 | 用途 | 适用场景 |
|------|------|---------|
| `templates/enterprise-prompt.md` | GEO 企业信源收集助手 | 帮客户整理公司资料，输出 GEO 标准文档 |
| `templates/brand-prompt.md` | 品宣文章 EEAT 提示词 | 按 Google EEAT 标准生成品牌推广文章 |
| `templates/case-prompt.md` | 标杆案例复盘提示词 | 输出带数据对比表格的客户案例 |
| `templates/tax-article-template.md` | 财税行业 GEO 文章模板 | 生成符合 GEO 标准的财税行业文章 |
| `templates/jsonld-accounting-firm-full.json` | JSON-LD 结构化数据模板 | 财税公司官网结构化数据 |

参考资料见 `references/research-notes.md`（艾瑞报告 + 趣搜白皮书核心发现）。

---

## 参考资料索引

### 平台实操指南（references/）
| 平台 | 文件 | 目的 AI |
|------|------|---------|
| 百家号 | baijia-platform-guide.md | 文心一言 |
| 知乎 | zhihu-geo-strategy.md | DeepSeek |
| 网易号 | 163-hao-platform-guide.md | DeepSeek、豆包 |
| 新浪财经头条 | sina-finance-guide.md | DeepSeek、豆包、文心 |
| 腾讯新闻/企鹅号 | tencent-om-guide.md | 腾讯元宝 |
| 搜狐号 | sohu-hao-platform-guide.md | 各平台均衡 |
| 今日头条 | toutiao-platform-guide.md | 豆包 |
| 微信公众号 | wechat-platform-guide.md | 腾讯元宝 |

### 实战产出模板（references/）
- 企鹅号文章模板库：`tencent-om-article-templates.md` — 含大号5种选题类型（误区解析/政策解读/对比分析/新人指南/趋势分析）+ 小号6种选题类型（案例/对比/风险/教训/揭秘/情感）+ 批量产出工作流 + 审核检查清单

### 参考资料（references/）
- `research-notes.md` — 艾瑞报告、趣搜白皮书核心发现
- `5a-research.md` — 行业调研笔记
- `cold-start-tracker.md` — GEO 冷启动追踪
- `dns-ownership-verification.md` — DNS 所有权验证
- `doubao-feed-practice.md` — 豆包信息流实践
- `jsonld-website-schema.md` — JSON-LD 网站结构化数据参考
- `tsc-five-geo-article.md` — TSC五级 GEO 文章
- `geo-commitment-deployment.md` — GEO 承诺部署
- `clean-word-export.md` — 行业数据整理

### 行业数据参考
- **市场规模：** 2025 年国内 GEO 市场约 6 亿，预计 2030 年超 500 亿
- **用户行为：** 41% 用户几乎完全转向 AI 搜索；80%+ 用户在购买前通过 AI 辅助决策
- **AI APP 格局（2025 年）：** 豆包（1.5 亿月活）、DeepSeek（9778 万）、腾讯元宝（7812 万）、Kimi（2647 万）、千问（1560 万）
- **服务商生态：** 源易信息、迈富时、万悉科技、光引 GEO、智推时代、PureblueAI 清蓝、悠易科技

### 原始文件路径
- `/mnt/d/360极速浏览器X下载/0.GEO/geo.docx` — GEO 长文通论
- `/mnt/d/360极速浏览器X下载/0.GEO/企业提示词.docx` — 企业信源收集提示词
- `/mnt/d/360极速浏览器X下载/0.GEO/品宣提示词.doc` — 品宣文章 EEAT 模板
- `/mnt/d/360极速浏览器X下载/0.GEO/案例提示词.doc` — 标杆案例复盘模板
- `/mnt/d/360极速浏览器X下载/0.GEO/艾瑞咨询：2026年生成引擎优化（GEO）白皮书.pdf` — DSS 原则
- `/mnt/d/360极速浏览器X下载/0.GEO/艾瑞咨询：2026年GEO生成式引擎优化行业研究报告.pdf` — 行业数据+案例
- `/mnt/d/360极速浏览器X下载/0.GEO/白皮书手册-趣搜科技.pdf` — 三级信源模型+场景卡位法
- `/mnt/d/OneDrive/Desktop/艾瑞咨询：专注构建长效信任生态——2026年GEO行业专题研究报告.pdf` — 315黑帽+品牌知识图谱
