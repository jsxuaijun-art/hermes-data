---
name: github
category: devops
description: Complete GitHub workflow skill — auth, PRs, issues, repos, code review, codebase inspection, and repo access. Covers both gh CLI and curl/git fallbacks for environments without gh.
version: 2.0.0
metadata:
  hermes:
    tags: [github, git, pull-requests, issues, code-review, authentication, repos]
    related_skills: [hermes-agent-sync, webhook-subscriptions]
---

# GitHub Operations — Umbrella Skill

## Overview

This umbrella skill covers all GitHub interactions the agent performs. Each major workflow is documented in its own reference file under `references/`. The shared **auth detection** and **owner/repo extraction** boilerplate lives here once instead of being duplicated.

## Quick Links

- `references/github-auth.md` — setup: HTTPS tokens, SSH keys, gh CLI login
- `references/repo-management.md` — clone, create, fork, releases, CI, secrets
- `references/issues.md` — create, triage, label, assign, search, close
- `references/pr-workflow.md` — branch → commit → PR → CI → merge
- `references/code-review.md` — review local changes, PRs, inline comments
- `references/github-api-cheatsheet.md` — curl API quick reference
- `references/ci-troubleshooting.md` — CI failure diagnostics
- `references/conventional-commits.md` — commit message format
- `references/windows-msys-git-pitfalls.md` — MSYS2/Git-Bash on Windows pitfalls
- `templates/bug-report.md` — issue template
- `templates/feature-request.md` — feature request template
- `templates/pr-body-bugfix.md` — PR body template (bugfix)
- `templates/pr-body-feature.md` — PR body template (feature)
- `scripts/gh-env.sh` — auth detection helper script

## Auth Detection (used by all subsections)

Use this before any GitHub operation that needs API access:

```bash
# Determine which auth method to use
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH="gh"
else
  AUTH="git"
  if [ -z "$GITHUB_TOKEN" ]; then
    if [ -f ~/.hermes/.env ] && grep -q "^GITHUB_TOKEN=" ~/.hermes/.env; then
      GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" ~/.hermes/.env | head -1 | cut -d= -f2 | tr -d '\n\r')
    elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
      GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
    fi
  fi
fi
echo "Using: $AUTH"

# Extract owner/repo from git remote
REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
echo "Owner: $OWNER, Repo: $REPO"
```

## Sub-skills (see references/)

| Skill | Purpose | File |
|-------|---------|------|
| **auth** | GitHub auth setup: HTTPS tokens, SSH keys, gh CLI login | `references/github-auth.md` |
| **PR workflow** | Branch, commit, open, CI, merge lifecycle | `references/github-pr-workflow.md` |
| **code review** | Review PR diffs, inline comments via gh or REST | `references/github-code-review.md` |
| **issues** | Create, triage, label, assign issues | `references/github-issues.md` |
| **repo management** | Clone, create, fork repos; manage remotes, releases, secrets | `references/github-repo-management.md` |
| **codebase inspection** | LOC, language breakdown, code/comment ratios via pygount | `references/codebase-inspection.md` |
| **repo access** | Browse tree, read files, download content; fallback strategies | `references/github-repo-access.md` |

## Fallback strategies

All GitHub skills support two access modes:
- **`gh` CLI** — richer API access, simpler auth. Use when available.
- **`git` + `curl`** — works anywhere `git` is installed. Uses `GITHUB_TOKEN` from `~/.hermes/.env` or `~/.git-credentials`.

For environments where `git clone` and `raw.githubusercontent.com` are blocked (restricted networks, Docker containers), see `references/github-repo-access.md` for advanced fallback strategies including CDN workarounds and shallow clones.

## Cross-Reference

### Hermes Config Sync (GitHub ↔ Local)

For using a GitHub repository as a sync hub for Hermes configuration files (SOUL.md, memories, skills):

- Repository pattern: a single GitHub repo (`OWNER/REPO`) acts as the cloud hub
- Sync scope: SOUL.md, SOUL_Pro.md, SOUL_Edu.md, config.yaml, README.md, memories/, skills/, claw-memory/ (defined by `.gitignore` whitelist)
- Pull strategy: try `git pull`, fall back to `git fetch --depth=1`, then to `git reset --hard origin/main`
- Push strategy: `git push`; if rejected (remote ahead), `git push --force` is acceptable for personal sync repos
- Local sync: `cp` files bidirectionally between the git repo directory and `~/.hermes/`
- Scheduling: use `cronjob` action=create with `script` pointing to `scripts/hermes-config-sync.sh`
- When local edits should take priority over GitHub (e.g., cron pushes from Windows), set `LOCAL_PRIORITY=true`

### git count-objects -v
```bash
# Shows garbage files from interrupted pack operations
git count-objects -v
# 'garbage: N' indicates orphaned tmp_pack files
# Usually safe to ignore on MSYS; they clear on reboot.
```

## Consolidated Sub-Skills

The former standalone sub-skills under `github/` directory — `github-auth`, `github-code-review`, `github-issues`, `github-pr-workflow`, `github-repo-management`, `codebase-inspection`, and `github-workflows` — were consolidated into this umbrella in 2026-06. Their content is already available under `references/` files listed above. Original directories preserved at `.archive/github/`.
