# External Skill Format Compatibility (Hermes Agent)

This reference documents how external skill-generation tools (book-to-skill, etc.) relate to Hermes Agent's skill system. Use when evaluating whether to install or adapt skills from non-Hermes sources.

## Typical External Skill Format

Tools like `virgiliojr94/book-to-skill` (6.7k⭐) and `apple-ouyang/book-to-skill` (58⭐) generate SKILL.md for Claude Code / GitHub Copilot CLI / Amp. Their output shape:

| Component | External | Hermes Required |
|-----------|----------|-----------------|
| Frontmatter | title+description only | name+description+version+author+license+metadata |
| Chapter structure | Separate files, on-demand load | Not natively supported — all in SKILL.md |
| Command triggers | `/skill-slug` prefix commands | Not supported — skill_view + tool-based |
| Deployment | File copy to agent's skills dir | `skill_manage(action='create')` or write_file |
| Verification | None | YAML frontmatter validator + format checks |

## Hermes-Specific Frontmatter Requirements

External tools skip these fields that Hermes' validator enforces:

```yaml
---
name: skill-slug                 # ≤64 chars, lowercase-hyphens
description: Use when <scenario>.  # ≤1024 chars
version: 1.0.0                   # recommended
author: User Name                # recommended
license: MIT                     # recommended
metadata:
  hermes:
    tags: [tag1, tag2]           # used for discovery
    related_skills: [skill-a]    # cross-references
---
```

Without these, the skill fails Hermes' `skill_structure` constraint.

## Adaptation Checklist

When importing an external skill:

- [ ] Add complete frontmatter (name, description, version, author, license, metadata)
- [ ] Ensure description starts with "Use when ..." trigger pattern
- [ ] Check total size ≤ 100,000 chars (aim for 8-15k)
- [ ] Remove command-trigger patterns (`/skill-slug`) — Hermes uses skill_view + tool-based discovery
- [ ] If the source has multiple files (chapters/, glossary.md, etc.), consolidate key content into references/ files under the Hermes skill
- [ ] Verify via local python check (yaml.safe_load frontmatter + size constraint)
- [ ] Deploy via `skill_manage(action='create')` — NOT file-drop into skills dir (that's Claude/Copilot pattern)

## When to Auto-Generate vs. Manually Create

| Factor | Auto-generate (book-to-skill) | Manual Create |
|--------|------------------------------|---------------|
| Book type | Methodology frameworks (WRAP, decision trees) | Domain expertise (tax, compliance, industry-specific) |
| Knowledge density | High-level patterns, repeatable | Nuanced, experience-based, region-specific |
| Quality control | Needs post-generation cleanup + frontmatter fix | Full control from start |
| Token efficiency | 24-51× savings vs raw text | Already optimized for skill format |
| Best for | Reference books, standards, internal docs | Your core expertise, practitioner knowledge |

**Rule of thumb for 江姐's 财税 context:** Books like 《原则》or《思考快与慢》are good auto-generate candidates (decision frameworks). Tax policies, compliance guides, and your own 16-year experience are better manually created — the tacit knowledge doesn't exist in any PDF.

## Tools Evaluated

### virgiliojr94/book-to-skill (⭐6756)
- Input: PDF/EPUB/DOCX/MD/HTML/RTF/MOBI
- Output: SKILL.md + chapters/ + glossary.md + patterns.md + cheatsheet.md
- Cost: ~$1/book (Claude Sonnet)
- Target: Claude Code / Copilot CLI / Amp
- Best for: Technical books, documentation folders, research clusters

### apple-ouyang/book-to-skill (⭐58)
- Input: PDF (via Claude Code)
- Output: SKILL.md with decision frameworks
- Pre-built skills: WRAP decisions, reality testing, tripwires
- Target: Claude Code
- Best for: Chinese-language business/decision books
- Note: Also has meta-skill `book-to-skill` for churning new books
