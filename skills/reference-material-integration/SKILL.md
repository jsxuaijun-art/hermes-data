---
name: reference-material-integration
description: Evaluate, cross-check, and integrate client-provided reference material into existing reports or deliverables. Handles conflicting data, identifies valuable additions, and produces a structured audit of what was adopted/rejected.
---

# Reference Material Integration Workflow

Use this when a user/client provides supplementary reference material (Word docs, copied text, search results, PDFs, articles) and asks you to merge it into an existing report or deliverable.

## ⚠️ Pre-requisite: Reading .docx Files (Pure Stdlib)

python-docx is often unavailable in WSL/container environments (pip install may time out due to network issues). **Never rely on it.** Use pure stdlib instead:

```python
import zipfile, xml.etree.ElementTree as ET

path = '/path/to/file.docx'
z = zipfile.ZipFile(path, 'r')
xml_content = z.read('word/document.xml')
root = ET.fromstring(xml_content)
ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

texts = []
for p in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
    para_text = ''
    for t in p.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
        if t.text:
            para_text += t.text
    texts.append(para_text)
print('\n'.join(texts))
```

**Pitfall:** Table cell text will appear concatenated. For tables, you may need to detect `<w:tbl>` elements and iterate `<w:tc>` (cell) elements to preserve structure. The simple paragraph extraction above is sufficient for most confirmed-info-list docx files.

## Full Workflow (7 Phases)

### Phase 0: Extract & Structure Client Information

When the user says "I've filled in the info, read it and generate a report":

1. **Read the .docx** using pure stdlib (see above)
2. **Read the existing case file** from `references/<case-name>.txt`
3. **Identify** which items are newly confirmed vs. still pending vs. changed
4. **Classify** by priority (P0=core, P1=important, P2=optimization)
5. **Cross-reference** new info with existing analysis: does it confirm or change the recommended path?

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

### Phase 5: Risk Escalation Handling (when new info changes risk profile)

When the user provides a new piece of client info that **significantly escalates risk** (e.g., "POS进私人账户" → 偷漏税嫌疑, "社保零参保" → 社保欠缴):

1. **Immediately reclassify the item** as 🔴🔴 紧急
2. **Restructure the implementation plan** into TWO phases:
   - **Phase 1 (Emergency, <1 month):** Stop the bleeding, urgent compliance fixes
   - **Phase 2 (Standard, 1-2 months):** Architectural landing, optimization
3. **Draft client communication language FIRST** — the exact words the user should say to the client when calling about the problem
4. **Then update the formal deliverable** (report, risk matrix, timeline)

**Pitfall:** Do not just update the report and present it silently. The user needs to CALL the client about emergencies before sending documents. Give them the script first.

### Phase 6: Proactive Value-Add (post-delivery)

After delivering the main report, **do not stop at "here's the deliverable."** Proactively offer the next actionable layer:

1. **Risk/cost quantification** — "需要我帮你做补救成本测算/估算表吗？"
2. **Client communication language** — draft the words the user should say on the call
3. **Next-step reminders** — "明天启动时我主动提醒你推这件事"

**This approach was explicitly praised by the user** (2026.5.14: "你的建议非常好，以后要保持" / "主动解决问题的态度很值得称赞"). Always scan for one more thing you can do before signing off.

### Phase 7: Generate Client Deliverable

After analysis, produce the final deliverable in **dual format** (this user's explicit preference):

1. **Terminal output** — structured tables using box_maker.py from workbuddy-output skill:
   ```python
   exec(open('/home/administrator/.hermes/skills/creative/workbuddy-output/scripts/box_maker.py').read())
   grid = make_grid_table(headers, rows)
   box = make_box('Title', ['line1', 'line2'])
   ```
2. **.docx file** on user's desktop (`/mnt/d/360MoveData/Users/Admin/Desktop/`) — use pure stdlib (generate-docx-without-python-docx skill) since python-docx is unavailable

**Standard report structure** for 财税全案/税务筹划方案:

```
1. 公司架构全景（架构图 + 关键参数）
2. 已确认信息清单（表格，标注P0/P1/P2 + 状态）
3. 分税种分析（增值税/所得税/个税/社保/返利逐项）
4. 风险矩阵（优先级排序，含整改建议）
5. 方案对比（多方案，含推荐/排除理由）
6. 实施路线图（按时间线，6~8步）
7. 关键法规索引（文号 + 适用场景）
8. 下一步行动（你和客户各自做什么）
```

**Multi-layer priority encoding:**
- 🔴 高 = affects compliance/fundamentals — act now
- 🟡 中 = affects optimization — act soon
- 🟢 低 = affects efficiency — plan later

**Pitfall:** Always update the case file (`references/<case-name>.txt`) after generating the report, so the next session starts from the latest state.

## Pitfalls

- **Don't blindly trust user-provided data.** Users often paste AI-generated summaries (豆包, deepseek, etc.) which may contain hallucinations or outdated info.
- **Don't overwrite without reading first.** Always read the existing file completely to understand what's already there.
- **Don't silently "fix" user data.** If you change a number or date the user provided, flag it in the audit.
- **Watch for implausible numbers** (租金210万/年, 15天收汇时限 vs actual 90天) — AI summaries frequently hallucinate specific figures.
- **When in doubt about a conflict, preserve both versions** with a note rather than picking one arbitrarily.
- **Never assume python-docx is available.** In WSL environments pip install often times out on github/pypi. Always use pure stdlib (zipfile + xml.etree.ElementTree) for .docx reading.
- **Dual-format delivery is preferred for this user.** Terminal tables alone are not sufficient — also generate .docx on desktop. The docx is what the user actually opens and sends to clients.
- **Update the case/reference file after each session.** If you don't write back the updated state, the next session starts from stale data.
- **Don't skip the 3-layer priority encoding** (P0/P1/P2, 🔴/🟡/🟢). Without it, the user has to re-prioritize your work.

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
- generate-docx-without-python-docx (for .docx output when python-docx is unavailable)
- workbuddy-output (for terminal tables using box_maker.py)
- table-formatter (alternative table formatting)

## Reference Files

- `references/nt-kaman-workflow-example.md` — worked example of the full workflow (reading docx → cross-referencing → generating tax scheme → dual-format delivery)
- `references/case-nt-sports-rev1.md` — real session trace: info evolution, risk escalation handling, two-phase restructuring, proactive value-add pattern. See Phase 5-6 workflow in action.
