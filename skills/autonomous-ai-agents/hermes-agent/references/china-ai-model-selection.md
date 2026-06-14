# China AI Model Selection for Tax/Finance Industry

Reference guide for selecting AI models when working in the Chinese tax/finance consulting industry (Company registration, bookkeeping, tax compliance, high-end accounting).

## Core Principle

For Chinese tax policy work, **domestic models edge ahead on policy knowledge breadth; foreign models edge ahead on reasoning depth.** The right answer depends on the task:

```
Policy research / fact-checking → Domestic models (DeepSeek) are more accurate
Complex scheme design / risk analysis → Foreign models (GPT) are stronger
International tax / cross-border → Foreign models have better coverage
Content creation (Chinese copy) → Domestic models are more natural
```

## Model Tiers (May 2026)

### Tier 1: DeepSeek V4 Pro
- **1.6T params, 49B activated** — dense enough to handle complex multi-factor tax planning
- 1M native context — can ingest full tax law documents
- Chinese policy coverage is excellent: knows specific announcements (e.g., 财政部税务总局公告2025年第1号)
- Pricing: promo ¥3/¥6 per M tokens (input/output), normally ~4x that
- **Best all-around choice for Chinese tax work** — balances capability, cost, and domestic policy accuracy

### Tier 2: DeepSeek V4 Flash
- **284B params, 13B activated** — the "lite" version of Pro, 1/4 the active parameters
- 1M native context (same as Pro)
- Price: ¥0.2~2 per M tokens (cached/uncached) — roughly 1/10 the cost of Pro
- **Best daily driver** — handles 80% of routine tax queries adequately
- Falls short on: complex multi-step reasoning, nuanced risk analysis, creative copywriting

### Tier 3: GPT-5.5 Pro
- Strongest reasoning, best structured output, most "human-like" Chinese writing
- Proven in financial services (audited 24,771 K-1 tax forms, finished 2 weeks early)
- Pricing: ~$5/$30 per M tokens — 10-30x more expensive than DeepSeek V4 Pro
- **Best for high-stakes client deliverables** — but the cost premium is steep

### Tier 4: Gemini 3.1 / 3.5
- Best multimodal (video/image/audio)
- Chinese copywriting quality lags behind DeepSeek and GPT
- Not recommended for tax/finance text work unless multimodal is needed
- Mid-range pricing (~$1.25/$5 per M tokens)

### Tier 5: Xiaomi MiMo V2.5
- Subscription-based Token Plan (¥39~659/month)
- Decent Chinese performance, multimodal support
- More expensive than DeepSeek for comparable quality
- Best reserved for users who need MiMo's specific ecosystem (IoT, voice, vision)

## Quick-Switch Strategies

### In-session toggle (fastest)
```
/model deepseek-v4-pro     # switch to Pro
/model deepseek-v4-flash   # switch back to Flash
```

### Profile-per-model (recommended for daily use)
```bash
hermes profile create pro --clone --description "复杂财税方案、重要文案"
hermes config set --profile pro model.default deepseek-v4-pro

# Usage:
hermes -p pro      # launch with Pro
hermes             # launch with Flash (default)
```

### Smart routing (automatic)
```bash
hermes config set smart_model_routing.enabled true
hermes config set smart_model_routing.cheap_model deepseek-v4-flash
```

Simple questions → cheap model automatically. Complex → expensive model.

## Price Reality Check

| Scenario | Flash/month | Pro/month | GPT-5.5/month |
|----------|------------|-----------|---------------|
| Light (~30M tokens) | ~¥30 | ~¥200 | ~¥3,000 |
| Medium (~100M tokens) | ~¥60 | ~¥600 | ~¥9,000 |
| Heavy (~300M tokens) | ~¥200 | ~¥2,000 | ~¥27,000 |

## Practical Recommendation for Tax/Finance

1. **Daily driver**: DeepSeek V4 Flash — cheap, fast, knows Chinese tax
2. **Critical work**: DeepSeek V4 Pro — switch via `/model` for complex cases
3. **Premium output**: GPT-5.5 Pro — for client-facing deliverables (if budget allows)
4. **Skip**: MiMo and Gemini for pure tax text work — no meaningful advantage over DeepSeek at higher cost

## Key Learning: "Domestic vs Foreign Tax Knowledge" Gap

A model trained mostly on Chinese data (DeepSeek) knows:
- 小规模纳税人月销售额10万免税
- 3%减按1%征收率延续
- 六税两费减半至2027年底
- 苏州工业园区地方税收返还政策
- 常熟1039市场采购贸易试点

A foreign model (GPT-5.5) more often:
- Gets announcement numbers wrong or confused
- Misses local/municipal-level policies
- But structures the overall analysis more logically

**For Chinese tax consulting, policy accuracy > reasoning elegance. This is why DeepSeek V4 Pro (or even Flash) is the pragmatic first choice.**
