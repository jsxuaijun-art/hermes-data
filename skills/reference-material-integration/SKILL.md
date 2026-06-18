---
name: reference-material-integration
description: Evaluate, cross-check, and integrate client-provided reference material into existing reports or deliverables. Handles conflicting data, identifies valuable additions, and produces a structured audit of what was adopted/rejected.
---

# Reference Material Integration Workflow

Use this when a user/client provides supplementary reference material (Word docs, copied text, search results, PDFs, articles) and asks you to merge it into an existing report or deliverable.

## Workflow

### Phase 1: Evaluate the Material

1. **Read the material carefully** — don't skim. Note specific claims, data points, and timestamps.
2. **Identify discrepancies with existing deliverables** — cross-reference dates, numbers, policy descriptions.
3. **Assess credibility**: Is the source clearly cited? Does it read like official policy, AI-generated summary, or personal notes?
4. **Flag anything that looks wrong**: typos, implausible numbers (e.g., "210万/年" for a market booth rental), contradictory statements.

### Phase 2: Cross-Check Discrepancies

1. For factual conflicts (dates, policy details), attempt a quick web search to verify:
   - Use targeted search queries with specific terms
   - Check multiple sources if possible
2. **If verification is impossible** (blocked search, no access):
   - Document both versions and note the discrepancy
   - Use inclusive language: "There are two accounts: X source says A, Y source says B"
   - Add a reconciliation note explaining the uncertainty

### Phase 3: Integrate into Report

1. **Read the full existing report** first — understand structure, tone, and what's already covered.
2. **Decide what to add** vs. **what to replace**:
   - Add: new sections, detailed procedures, deeper breakdowns
   - Replace: outdated info, errors, incomplete descriptions
3. **Merge, don't append** — the new info should feel native to the existing report, not tacked on.
4. **Maintain consistency** in tone (professional, actionable, direct) and formatting (table style, heading hierarchy).

### Phase 4: Deliver with Audit

After updating, always provide the user with a **structured audit of changes**:

```
## Report Update Complete ✅

### 🔴 Corrections Made
- [which errors were fixed]

### ✅ New Modules Added
| New Content | Source |
|------------|--------|
| [module name] | [user material | internal knowledge] |

### ⚠️ Conflicts Resolved / Not Adopted
| Conflict | Resolution |
|----------|-----------|
| [discrepancy] | [how it was handled] |

### ❌ Rejected / Flagged as Unreliable
- [item] — [reason]
```

## Pitfalls

- **Don't blindly trust user-provided data.** Users often paste AI-generated summaries (豆包, deepseek, etc.) which may contain hallucinations or outdated info.
- **Don't overwrite without reading first.** Always read the existing file completely to understand what's already there.
- **Don't silently "fix" user data.** If you change a number or date the user provided, flag it in the audit.
- **Watch for implausible numbers** (租金210万/年, 15天收汇时限 vs actual 90天) — AI summaries frequently hallucinate specific figures.
- **When in doubt about a conflict, preserve both versions** with a note rather than picking one arbitrarily.

## Example Audit Output

```
### 🔴 Corrected 1 error:
- 常熟试点时间 from "2015" → flagged as two possible timelines (2015 pilot inclusion vs. 2019 formal approval), added reconciliation note

### ✅ Added 5 new modules:
- 常熟服装城产业概况 (35 markets, 30k+ merchants)
- 备案主体三类分类
- 摊位问题三种解决方案 with pricing
- 收汇三渠道 + 银行清单

### ❌ Rejected 1 data point:
- "摊位费约210万/年" → changed to 2-10万/年 (plausible market rate; 210万 is almost certainly a typo)
```

## Related Skills

- writing-plans (for structured deliverable creation)
- report-writing (if you have one — for long-form deliverable structure)
