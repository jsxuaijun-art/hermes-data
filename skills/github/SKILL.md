---
name: github
<<<<<<< LOCAL (this PC)
category: devops
description: Complete GitHub workflow skill — auth, PRs, issues, repos, code review, codebase inspection, and repo access. Covers both gh CLI and curl/git fallbacks for environments without gh.
version: 2.0.0
metadata:
  hermes:
    tags: [github, git, pull-requests, issues, code-review, authentication, repos]
    related_skills: [hermes-agent-sync, webhook-subscriptions]
=======
description: "Interact with GitHub using the `gh` CLI. Use `gh issue`, `gh pr`, `gh run`, and `gh api` for issues, PRs, CI runs, and advanced queries."
description_zh: "管理 GitHub Issues、PR 和 CI"
description_en: "Manage GitHub issues, PRs, and CI runs"
version: 1.0.0
>>>>>>> REPO (github)
---

<<<<<<< LOCAL (this PC)
# GitHub Operations — Umbrella Skill
=======
# GitHub Skill
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
## Overview
=======
Use the `gh` CLI to interact with GitHub. Always specify `--repo owner/repo` when not in a git directory, or use URLs directly.
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
This umbrella skill covers all GitHub interactions the agent performs. Each major workflow is documented in its own reference file under `references/`. The shared **auth detection** and **owner/repo extraction** boilerplate lives here once instead of being duplicated across 7 files.
=======
## Pull Requests
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
## Quick Auth Detection (shared)
=======
Check CI status on a PR:
```bash
gh pr checks 55 --repo owner/repo
```
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
Use this before any GitHub operation that needs API access:
=======
List recent workflow runs:
```bash
gh run list --repo owner/repo --limit 10
```
>>>>>>> REPO (github)

View a run and see which steps failed:
```bash
<<<<<<< LOCAL (this PC)
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
=======
gh run view <run-id> --repo owner/repo
```
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
# Extract owner/repo from git remote
REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
echo "Owner: $OWNER, Repo: $REPO"
=======
View logs for failed steps only:
```bash
gh run view <run-id> --repo owner/repo --log-failed
>>>>>>> REPO (github)
```

## API for Advanced Queries

<<<<<<< LOCAL (this PC)
## Sub-skills (see references/)
=======
The `gh api` command is useful for accessing data not available through other subcommands.
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
| Skill | Purpose | File |
|-------|---------|------|
| **auth** | GitHub auth setup: HTTPS tokens, SSH keys, gh CLI login | `references/github-auth.md` |
| **PR workflow** | Branch, commit, open, CI, merge lifecycle | `references/github-pr-workflow.md` |
| **code review** | Review PR diffs, inline comments via gh or REST | `references/github-code-review.md` |
| **issues** | Create, triage, label, assign issues | `references/github-issues.md` |
| **repo management** | Clone, create, fork repos; manage remotes, releases, secrets | `references/github-repo-management.md` |
| **codebase inspection** | LOC, language breakdown, code/comment ratios via pygount | `references/codebase-inspection.md` |
| **repo access** | Browse tree, read files, download content; fallback strategies | `references/github-repo-access.md` |
=======
Get PR with specific fields:
```bash
gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'
```
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
## Fallback strategies
=======
## JSON Output
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
All GitHub skills support two access modes:
- **`gh` CLI** — richer API access, simpler auth. Use when available.
- **`git` + `curl`** — works anywhere `git` is installed. Uses `GITHUB_TOKEN` from `~/.hermes/.env` or `~/.git-credentials`.
=======
Most commands support `--json` for structured output.  You can use `--jq` to filter:
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
For environments where `git clone` and `raw.githubusercontent.com` are blocked (restricted networks, Docker containers), see `references/github-repo-access.md` for advanced fallback strategies including CDN workarounds and shallow clones.
=======
```bash
gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'
```
>>>>>>> REPO (github)
