# Baidu Baike Content Audit & Edit Workflow

> Workflow for checking Baidu Baike (百度百科) entry edit status, inspecting section content, and managing multi-stage edits for Chinese SME company entries.

## Background

Baidu Baike edits go through a manual review process. Submitting an edit creates a "pending" version that a Baike editor must approve. Review can take hours to days.

Unlike editing a company's own website, Baike has:
- A review/approval process (edits get audited)
- Version history with rollback
- Reference/citation requirements with source verification
- Section-based structure with auto-generated TOC

## Checking Edit Approval Status

### Method: Browser Inspection (no login required)

**Step 1:** Navigate to the item page
```txt
https://baike.baidu.com/item/{URL-encoded company name}
```

**Step 2:** Use `browser_console` with inline JS to check if the target section is live:

```javascript
// Quick check — does the section heading text appear?
document.body.innerText.includes('所获荣誉')
// → true if the section exists on the page

// Extract the section content by slicing between two headings
let t = document.body.innerText;
let start = t.indexOf('所获荣誉');
t.slice(start, start + 2000)
// → Returns 2000 chars starting from the heading,
//   enough to capture the full section content
```

**Step 3:** Compare the extracted text with what was submitted:
- If the section content **matches** the submitted text → ✅ Edit was approved
- If the **old content** remains, or the section is **absent** → Still under review, rejected, or the edit hasn't been processed yet

**Step 4 (optional):** Check the stage/index of the section in the page's TOC:

```javascript
// Get section TOC entries
document.querySelectorAll('.para-title')
```

This helps confirm the section is in the correct position.

### Checking Edit History

```txt
https://baike.baidu.com/history/{URL-encoded name}
```

Note: The history page shows limited metadata (timestamps, editors). For detailed per-edit diff, log into Baidu Baike account and visit "我的贡献" (My Contributions).

## Multi-Stage Edit Workflow

For staged edits (building up a Baike entry section by section):

| Stage | Action | After Approval |
|-------|--------|---------------|
| 1 | Submit initial sections (basic info, company overview) | ✅ Verify section is live |
| 2 | Submit additional sections (honors, certifications) | ✅ Verify section content |
| 3 | Submit reference citations, fine-tune wording | ✅ Verify all references work |

**Why stage:** Smaller, targeted edits pass review faster. A single large edit with many changes is more likely to be scrutinized or rejected.

## Citation Source Requirements

Baidu Baike requires reliable sources. Common patterns:

| Source type | URL pattern | Notes |
|-------------|-------------|-------|
| Company official site | `https://company.com/page` | ✅ Must be accessible (SSL working) |
| Government portal | `*.gov.cn/...` | ✅ High authority, best for factual claims |
| News articles | Major outlets | ✅ Use for industry recognition / awards |
| Industry associations | Association websites | ✅ Good for membership / certification claims |

**Critical rules:**
- The **exact text** used in the Baike claim must appear verbatim on the referenced page
- If the company website is cited ([1] source), it must be accessible via HTTPS without SSL errors
- Citation URL should point to the specific sub-page containing the supporting text, not just the homepage

### Verifying a Citation Source

```bash
# Check SSL first
curl -sI --connect-timeout 10 https://company.com/page
# If SSL_PROTOCOL_ERROR → fix certificate before submitting

# Verify the claimed text appears on the page
curl -sL --connect-timeout 10 https://company.com/page | grep -c '目标文字'
# Should return ≥1
```

## Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Website SSL broken | Baike editor tags citation as invalid | Fix SSL certificate first, then resubmit |
| Claimed text not on cited page | Citation appears but doesn't prove the claim | Add the text to the website first, or cite a different source |
| Large single edit with many changes | Edit stuck in review for days | Break into smaller staged edits |
| Editing too frequently | Account flagged or throttled | Space edits at least 24-48 hours apart |
| Using promotional language ("最", "第一", "领先") | Edit rejected for non-neutral tone | Rewrite in factual, neutral language |
| Reference doesn't load in mainland China | International site blocked by GFW | Use mainland-accessible sources only |

## Related Tools

- **browser_console JavaScript inspection** — most reliable way to verify live Baike content without scraping
- **curl** — check website accessibility and verify citation text on referenced pages
- **nslookup/host** — verify DNS resolution if the website isn't reachable
- **Baidu Baike account "我的贡献"** — view edit history, re-submit rejected edits
