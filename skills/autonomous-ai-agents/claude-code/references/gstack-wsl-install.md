# gstack — WSL Installation & Integration Guide

[gstack](https://github.com/garrytan/gstack) (97K⭐) is a collection of 47 software engineering skills for Claude Code (shipping, design, review, QA, planning, etc.).

## Architecture

```
Hermes Agent
  └─ delegate_task(acp_command='claude')
       └─ Claude Code (Windows npm package)
            └─ skills/  ← installed at C:\Users\<user>\.claude\skills\
                 ├─ ship/SKILL.md
                 ├─ review/SKILL.md
                 ├─ autoplan/SKILL.md
                 ├─ ...
```

## Installation Steps (WSL-specific)

### Prerequisites
- Node.js v20+ (for `npm`)
- Claude Code installed: `npm install -g @anthropic-ai/claude-code`
- Git, Bun (see below)

### Step 1: Install Bun

Bun is required for gstack's build step. Standard `curl ... | bash` often times out on WSL. Use npm instead:

```bash
npm install -g bun
```

Verify: `bun --version` (v1.3.x+)

### Step 2: Clone gstack

WSL → GitHub clone frequently times out (`fetch-pack: unexpected disconnect`). Workaround: use Windows-side Git via PowerShell:

```powershell
# In PowerShell (NOT WSL)
git clone --depth 1 https://github.com/garrytan/gstack.git C:\Users\<user>\gstack
```

Then copy to WSL:
```bash
cp -r /mnt/c/Users/<user>/gstack ~/gstack
```

Alternatively try WSL git with HTTP/1.1:
```bash
git -c http.version=HTTP/1.1 -c http.postBuffer=524288000 clone --depth 1 https://github.com/garrytan/gstack.git ~/gstack
```
(May still time out — PowerShell route is more reliable.)

### Step 3: Build gstack

```bash
cd ~/gstack
bun install --frozen-lockfile
bun run build
```

### Step 4: Install Skills to Claude Code

The `./setup` script handles registration — but on WSL it hangs at Playwright Chromium download (167MB, slow network).

**Workaround: Manual install.** Claude Code (Windows npm package) reads skills from the Windows filesystem at `C:\Users\<user>\.claude\skills\`, NOT the WSL `~/.claude/` path.

```bash
GSTACK_SRC=~/gstack
CLAUDE_SKILLS="/mnt/c/Users/Administrator/.claude/skills"
mkdir -p "$CLAUDE_SKILLS"

# Copy each skill's SKILL.md
for d in "$GSTACK_SRC"/*/; do
  [ -f "$d/SKILL.md" ] || continue
  skill=$(basename "$d")
  mkdir -p "$CLAUDE_SKILLS/$skill"
  cp "$d/SKILL.md" "$CLAUDE_SKILLS/$skill/SKILL.md"
done

# Also copy the root gstack SKILL.md
mkdir -p "$CLAUDE_SKILLS/gstack"
cp "$GSTACK_SRC/SKILL.md" "$CLAUDE_SKILLS/gstack/SKILL.md"
```

Expected result: 47 skill directories with SKILL.md files.

### Step 5: Verify Installation

```bash
# From WSL
ls /mnt/c/Users/Administrator/.claude/skills/ | wc -l
# Should return 47

# Quick test from Claude Code (requires login first)
claude -p "list the skills available to you" --max-turns 1
```

**Note:** First-time Claude Code usage requires `/login` (browser OAuth or `ANTHROPIC_API_KEY`).

### Optional: Install Playwright Chromium

Browser features (browse skill, open-gstack-browser) require Chromium. On WSL with slow network, this may time out. Skip unless needed:

```bash
cd ~/gstack && npx playwright install chromium
# 167MB download — expect 5+ minutes on slow connections
```

## Using gstack with Hermes

gstack is a **Claude Code** skill set. From Hermes, you spawn a Claude Code session that has access to these skills:

### Via delegate_task (print mode — preferred)
```python
terminal(
    command='claude -p "Use /ship to prepare the release" --allowedTools "Read,Edit,Bash" --max-turns 10',
    workdir="/path/to/project",
    timeout=120
)
```

### Via tmux (interactive mode)
```python
terminal(command="tmux new-session -d -s gstack-session -x 140 -y 40")
terminal(command="tmux send-keys -t gstack-session 'cd /path/to/project && claude' Enter")
# Handle trust dialog
terminal(command="sleep 5 && tmux send-keys -t gstack-session Enter")
# Use gstack skill
terminal(command="tmux send-keys -t gstack-session '/review' Enter")
```

## Key gstack Skills

| Skill | Usage |
|-------|-------|
| `/ship` | Prepare and execute release |
| `/autoplan` | Autonomous task decomposition and planning |
| `/review` | Code review with analysis |
| `/qa` | Test planning and execution |
| `/design-review` | Architecture and design review |
| `/plan-ceo-review` | CEO-level strategic plan review |
| `/context-save` | Save session context for later restore |
| `/context-restore` | Restore saved session context |
| `/browse` | Web browsing and research |
| `/skillify` | Convert project knowledge into a reusable skill |

## Pitfalls

1. **WSL symlinks don't work for Windows Claude Code.** The Windows npm binary reads `C:\Users\<user>\.claude\skills\`, not the WSL path. Symlinks from WSL → Windows paths are unreliable. Use `cp` (copy) instead.
2. **Playwright Chromium is 167MB** and frequently times out on WSL networks. Skip unless you need browse/open-gstack-browser skills.
3. **Claude Code requires login** even when called from WSL. Run `claude` once and complete `/login` first.
4. **Skills are plain SKILL.md files** — Claude Code reads them as natural-language guidance, not executable code. gstack's `bin/` directory provides supporting scripts that skills reference at runtime.
5. **Skill autoloading is implicit** — Claude Code auto-loads skills based on conversation context, not explicit commands. The `/` slash commands make them explicit.
