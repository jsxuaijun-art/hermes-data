---
name: chinese-legal-research
description: Chinese law legal research, case retrieval from 裁判文书网, and legal document drafting (代理词/起诉状/辩护意见). Covers software/IT contract disputes, consumer protection, and general civil-commercial litigation.
---

# Chinese Legal Research & Document Drafting

Use this when the user asks about legal issues, court cases, or needs legal documents drafted in Chinese law context.

## Workflow

### Phase 1: Legal Analysis

1. **Identify the legal relationship** — what kind of contract/obligation is at play (买卖合同, 服务合同, 软件许可, etc.)
2. **Pinpoint the breach** — what did the other party promise vs. what did they do?
3. **Map to Civil Code articles:**
   - 第509条 (全面履行)
   - 第577条 (违约责任)
   - 第582条 (补救措施: 修理/重作/更换/退货)
   - 第496-497条 (格式条款无效)
   - 第7条 (诚信原则)
4. **Assess the remedy sought** — is the user asking for 退费, 更换, 赔偿? Ensure it maps to a recognized remedy under 民法典第582条

### Phase 2: Case Law Search Strategy

**Primary target: 中国裁判文书网 (https://wenshu.court.gov.cn/)**

⚠️ **Critical limitation: The wenshu website has heavy anti-scraping protection (CAPTCHA, dynamic JS rendering, IP rate limiting, API token validation). CLI-based automated searches (curl, wget) against the site or its API will fail.** Do NOT waste time trying to reverse-engineer the API.

**Effective search approaches (in priority order):**

| Method | How | Success Rate |
|--------|-----|--------------|
| Manual browser search | User opens wenshu.court.gov.cn in browser and searches directly | ✅ Best |
| Search engines with site: | Bing/Sogou with `site:wenshu.court.gov.cn 关键词` | ⚠️ Low - deep pages not indexed |
| Legal news/analysis sites | 中国法院网, 北大法宝(pkulaw), lawtime.cn, 律霸网 | ⚠️ Case analysis, not original judgments |
| Law firm articles | Many law firms publish case analysis blogs | ✅ Good for principles |

**Effective search keywords for software/IT disputes:**
- 终身使用权, 终身授权, 永久许可
- 软件 停止服务 违约
- 终身会员 停用 判决
- 格式条款 无效 软件
- 合同目的 不能实现 软件

#### Fallback Chain: When Primary Case Search Fails

Even with specific court name + defendant name, you may not find direct precedents on wenshu. Do NOT give up — use this fallback chain instead:

| Step | What to do | Purpose | Priority |
|------|-----------|---------|----------|
| 1 | **Retrieve opponent's EULA/Terms** from their own website via curl | Find the exact clauses they'll use as defense (格式条款中的终止权) | 🥇 First |
| 2 | **Search complaint platforms** (黑猫投诉 tousu.sina.com.cn, Zhihu) for user narratives | Understand pain points, real user experiences, and how the software stopped working | 🥈 High |
| 3 | **Use Bing instead of Baidu/Sogou** — Bing often has better results for Chinese legal issues | More reliable indexing of legal-related pages | 🥈 High |
| 4 | **Check opponent's parent company** for related lawsuits (天眼查/企查查/启信宝) | See if the same defendant has been sued before for similar issues | 🥉 If accessible |
| 5 | **Ask user for screenshots** of purchase page, EULA at time of purchase, cancellation notice | Direct user-provided evidence is better than any search result | 🥇 Critical |
| 6 | **Build case on legal principles + analogous case types** (not fabricated numbers) | Good legal reasoning and 类案参照 beats silence | ✅ Always do this |

**The key insight**: in a software/终身授权 dispute, the opponent's own EULA (freely available on their website) is often the single most valuable piece of evidence — it documents the exact clauses they'll rely on, and you can attack those clauses directly in your brief.

### Phase 3: Document Drafting (代理词/起诉状)

Follow the **三阶支撑结构** for all legal arguments:

```
法条依据 + 类案判例 + 分析结论
```

**Agent's role:**
- Draft the legal document with proper Chinese court format
- Include citations to Civil Code articles
- Reference relevant case principles (use the `references/` directory for known case patterns)
- If no specific case was found, note this and explain the legal principle independently

**Recommended document structure for a 代理词 (软件/IT纠纷):**

```
标题 + 案号信息
一、基本事实（简明扼要，突出被告的终身承诺 vs 单方停服）
二、核心法律论证
   (一) 根本违约 — 民法典第509条 + 第577条
        • "终身"是合同实质性条款，非广告用语
        • 合同目的已完全落空（第563条）
   (二) 格式条款无效 — 民法典第496条 + 第497条
        • 单方终止权 = 排除消费者主要权利
        • 未尽合理提示说明义务
   (三) "更换"有法可依 — 民法典第582条
        • 更换是法定补救措施
        • 三重优势论证：对原告（有替代不落空）
          对被告（损失可控）对法庭（最小影响方案）
   (四) 违反诚信原则 — 民法典第7条
三、对被告可能抗辩的预判与回应 — 4组预判+回应
      每组格式：预判原文（加引号）+ 独立回应段落
      常见4种抗辩（见下方表格）
四、最终请求
附：类案参考说明（3个类案表格，含案型、案由、裁判要点）
实操建议（庭前准备 → 换货方案 → 调解策略）
```

**Key drafting principles:**
- Focus on 合同目的落空 (frustration of contract purpose) — strongest argument
- Emphasize 诚信原则 if the other party's conduct was commercially unfair
- If the user's remedy is modest (更换而非退费), highlight this as evidence of good faith — put this in its own subsection and spell out the "three advantages" (对原告、对被告、对法庭)
- Anticipate the other party's defenses (格式条款, 不可抗力, etc.) and preemptively rebut them — use a dedicated section for this

**Preemptive defense anticipation (软件/IT纠纷常见抗辩):**

| 被告可能说 | 你的回应 | 法条依据 |
|-----------|---------|---------|
| "用户协议约定了可随时终止服务" | 格式条款无效，排除了原告主要权利 | 第497条 |
| "终身使用指安装包，不包括服务" | 同时承诺了"终身维护服务"，且"终身"在消费语境包含持续可用 | 第7条诚信原则 |
| "行业惯例，旧版本逐步停止支持" | 行业惯例 ≠ 法律豁免，被告以"终身"定价就应匹配终身义务 | 第509条全面履行 |
| "软件是国外公司产品，与中国经销商无关" | 原告与经销商直接交易，经销商应对销售产品持续可用性负责 | 合同相对性原则 |
| "用户协议中有免责条款" | 免责条款未以合理方式提示说明，不构成合同内容 | 第496条 |

### Phase 4: Deliver

Present the document as:
1. Final-form legal document (代理词/起诉状/辩护意见)
2. Followed by a brief **实操建议** section with courtroom-ready tips covering:
   - **庭前准备清单**：保留购买凭证、被告承诺截图、停服公告截图、软件异常记录、被告准确全称
   - **更换/赔偿具体方案**：明确要求替换什么产品，备选方案（退款折算）
   - **调解策略建议**：可接受的底线、退一步的折中方案
3. Offer to convert to .docx for desktop

## Known Case Patterns (Software/IT)

### Pattern A: 终身VIP/终身服务被单方终止
- Legal principle: "终身" in a contract is a clear term of service duration
- 民法典: 第509条 (全面履行), 第577条 (违约)
- Remedy: 更换/退款/赔偿 (民法典第582条)
- Common defense: 格式条款中的"有权终止"
- Rebuttal: 民法典第497条 (格式条款无效)

### Pattern B: 软件单方停止技术支持
- Legal principle: 持续提供技术保障是合同目的核心要素
- 民法典: 第509条, 第563条 (合同目的不能实现)
- Remedy: 更换等同价值替代产品

## Pitfalls

- ❌ **Don't try to scrape wenshu.court.gov.cn** — it won't work from CLI. Anti-scraping is too sophisticated.
- ❌ **Don't cite fabricated case numbers** — if you didn't retrieve a real case, say so. Never invent a (202X) number.
- ❌ **Don't give pure legal theory without practical application** — always tie back to the user's specific facts.
- ⚠️ **Legal databases (北大法宝, 威科先行) are subscription-only** — don't promise access you don't have.
- ✅ **Do offer to write the document** even without a perfect case match — good legal reasoning beats silence.

## Related Skills

- reference-material-integration (for evaluating client-provided legal docs)
- word-documents (for converting legal docs to .docx format)

## Reference Files

- `references/software-license-case-patterns.md` — 软件/IT合同纠纷类案裁判要点
- `references/wenshu-court-anti-scrape-notes.md` — 裁判文书网爬取限制及替代方案
- `references/session-2026-05-13-MindMaster.md` — 实战案例：MindMaster终身使用权纠纷（含对方EULA关键条款、搜索策略、论证框架）
