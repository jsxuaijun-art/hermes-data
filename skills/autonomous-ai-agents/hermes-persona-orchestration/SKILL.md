---
name: hermes-persona-orchestration
description: >
  Onboard into and serve a user who maintains a hermes-data sync repository
  containing SOUL.md persona profiles, persistent memories, custom config, and
  a synced skills directory across multiple devices. Covers: proactive discovery
  of hermes-data repos, multi-profile loading (Pro/Edu), cross-device sync
  awareness, domain-specific persona application, and memory-vs-skill separation.
---

# Hermes Persona Orchestration

## When to Use This Skill

- User session starts and you're unsure who the user is — **check for a hermes-data repo first**, don't ask.
- User has a sync repo pattern (hermes-data on GitHub) with SOUL.md + memories/ + config.yaml
- User switches between multiple persona modes (e.g., Pro for work, Edu for tutoring)
- User works across multiple devices (home/office) and syncs via GitHub
- User has a domain-specific persona (tax/finance, marketing, education, etc.)

## Core Principle

**Ask the repo, not the user.** When a user says "do you know what I do?" or "read these files and apply them", you should have already done this at session start. The hermes-data repo *is* the onboarding doc.

## Proactive Discovery

At the start of any session with this user type:

1. **Check for hermes-data repo** at common locations:
   - Windows: `C:\Users\<username>\Documents\GitHub\hermes-data\`
   - WSL: `/mnt/c/Users/<username>/Documents/GitHub/hermes-data/`
   - Also check `C:\Users\<username>\hermes-sync\` or desktop `HermesAgent\` folder
   - Also check `~/.hermes/` for SOUL.md (the local working copy)

2. **Read in this priority order:**
   ```
   SOUL.md (or SOUL_Pro.md)   →  Main persona (how to behave)
   memories/                   →  Persistent knowledge (who user is)
   config.yaml                 →  Technical setup (model, tools, device)
   memories/*.md              →  Domain details (company, cases, projects)
   SOUL_Edu.md (if present)   →  Secondary persona (known but not active)
   ```

3. **Extract the persona contract** from SOUL.md:
   - Core identity and role
   - Language and output style preferences
   - Mandatory output mechanisms (e.g., "if marketing question, always give N topics + 1 copy + conversion guide")
   - Constraints and principles

4. **Store critical user fact** immediately in memory to prevent future re-asking:
   - Which profile is active (Pro, Edu, custom)
   - Domain and industry
   - Company name and role
   - Key preferences
   - Device context (home vs office)

## Repo Structure Pattern

```
hermes-data/
├── README.md               # Sync instructions
├── config.yaml             # Hermes Agent config
├── SOUL.md                 # Primary persona (Pro/work mode)
├── SOUL_Pro.md             # Same as SOUL.md (Pro alias)
├── SOUL_Edu.md             # Education persona (tutoring mode)
├── .gitignore              # Excludes .env, sessions.db, logs
├── .git/                   # Git repository
├── memories/
│   ├── MEMORY.md           # Long-term knowledge base
│   ├── USER.md             # User profile (evolves over time)
│   └── *.md                # Domain/project-specific memories
├── claw-memory/
│   └── MEMORY.md           # Cross-agent memory (WorkBuddy/Claw)
├── skills/
│   ├── .hub/               # Hub metadata
│   ├── .bundled_manifest
│   ├── <category>/
│   │   └── <skill>/
│   │       └── SKILL.md    # Installed/managed skills
│   └── ... (mirror of Hermes Agent built-in skills)
```

## Multi-Profile Switching

When the user mentions education/tutoring/child context:

1. Switch to SOUL_Edu.md persona
2. Note: this changes your tone, approach, and constraints completely
3. The SOUL_Edu.md typically shifts from "result-driven expert" to "learning coach + thinking guide"

When the user mentions business/marketing/work context:

1. Ensure SOUL.md / SOUL_Pro.md is active
2. This persona typically demands: direct results over explanations, Chinese output, mandatory marketing output for content questions

## Cross-Device Sync Awareness

### Standard Sync

- User may switch between home PC and office PC
- hermes-data repo is cloned on both devices
- SOUL.md, memories/, config.yaml are synced via `git push/pull`
- .env (API keys) and sessions.db are NOT synced (excluded via .gitignore)
- The sync scripts are typically `Hermes同步-推送.bat` and `Hermes同步-拉取.bat` on the Windows desktop
- When on a new device, if repo is at `C:\Users\<username>\Desktop\HermesAgent\` or similar, that's likely the office machine

### Extending hermes-data with Non-Hermes Tooling

The hermes-data repo doesn't have to contain only Hermes config. It can also hold scripts, tools, and documentation that get synced across devices.

```
hermes-data/
├── scrapling/              ← Example: web scraping environment
│   ├── setup.sh            ← One-shot install on each machine
│   ├── activate.sh         ← Activate the standalone venv
│   ├── README.md           ← Multi-machine sharing instructions
│   └── scripts/            ← Python scripts (synced via git)
│       ├── test-scrapling.py
│       └── ...
```

**Rules for this pattern:**
1. **Binary packages cannot be synced** — Scrapling + Playwright + Chromium must be `pip install`ed on each machine individually
2. **Scripts CAN be synced** — put them in `hermes-data/<tool>/scripts/` and all machines get them via `git pull`
3. **Include a `setup.sh`** — other machines run it to bootstrap the environment
4. **Use standalone Python venvs** (`~/tool-env/`) — never install into the Hermes venv to avoid dependency conflicts
5. **Update `.gitignore`** — the repo uses a whitelist (`*` then `!path/`), so new tool directories must be added explicitly

## Domain-Specific Application

This skill supports any domain-specific SOUL.md, not just tax/finance. The key patterns are:

1. **Dual role definition** — expert in domain + growth/marketing operator for that domain
2. **Mandatory output triggers** — specific question types that force structured multi-part responses
3. **Content standards** — hooks, density, risk/benefit framing, conversion design
4. **Style constraints** — language, tone, audience, verbosity limits

## Memory vs. Skill Discipline

| Type | What it holds | Example |
|------|--------------|---------|
| **Memory** | Who the user is, their current situation, state of operations | "江敏 is manager, runs 苏州盈信, 24yr tax veteran" |
| **Skill** | How to do a class of task for this user | "When user has hermes-data repo, read SOUL.md before asking who they are" |

- **Memory** is for facts that describe the user and their environment
- **Skill** is for procedures, workflows, and patterns of how to handle recurring situations
- When a user corrects how you handled a task → update the relevant **skill**, not just memory
- When you discover a new user fact → update **memory**, not skill

## Session Recovery After Interruption

When a user accidentally exits Hermes (Ctrl+C) and re-enters, their session context is lost. Don't ask "what were we doing" — use session_search to find it.

### Recovery procedure

```python
# Step 1: Browse recent sessions
session_search()  # no args = chronological list with previews

# Step 2: Query for their task topic
session_search(query="<topic-keywords>")

# Step 3: Scroll into the right session to find the last exchange
session_search(session_id="<id>", around_message_id=<msg_id>, window=15)
```

### Key patterns

- **Most recent session is usually the one** — browse first, query only if it's unclear.
- **bookend_end shows last exchange** — the last 3 user+assistant messages are where they left off.
- **Summarize, don't dump** — tell the user concisely what was being discussed and ask "continue or switch?"

## Pitfalls

- **Don't ask "who are you" before checking repo.** User experience: frustrating. Always check `hermes-data/` first.
- **Don't confuse SOUL.md with memory.** SOUL.md defines *how to behave*; memories define *who the user is and what they know*. Load both.
- **Don't assume home vs office.** Check the Windows username path. `C:\Users\Admin` is typically office; `C:\Users\jsxuaijun` is typically home.
- **Don't overwrite memories.** The `memories/MEMORY.md` and `memories/USER.md` are the user's canonical knowledge base. Add to it, don't replace.
- **When user says "读取/熟悉/应用这些文件"** — this means: read everything, extract the persona contract, apply it immediately, and confirm to the user what you now know.
- **Profile switching may require config.yaml changes** — SOUL_Edu.md might need different model/tool settings. Check config.yaml for hints.
- **After user accidentally exits (Ctrl+C), don't ask "what were we doing"** — use `session_search()` to find and summarize their last session. They'll confirm or correct.
- **When adding non-Hermes tooling to hermes-data, update .gitignore** — the whitelist will silently exclude new directories.
