---
name: github-workflows
description: "Complete GitHub operations: authentication setup, repository management, issue tracking, pull request lifecycle, and code review — all through gh CLI or git+curl fallback."
version: 1.0.0
author: Hermes Skill Curator
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [github, git, pull-requests, issues, code-review, ci-cd, authentication, repository-management]
    related_skills: [autonomous-coding-agents, subagent-driven-development]
---

# GitHub Workflows

Complete GitHub operations: authentication, repository management, issues, PR lifecycle, and code review. Every operation shows the `gh` CLI path first, then the plain `git` + `curl` fallback for machines without `gh`.

## Quick Links

- `references/github-auth.md` — setup: HTTPS tokens, SSH keys, gh CLI login
- `references/repo-management.md` — clone, create, fork, releases, CI, secrets
- `references/issues.md` — create, triage, label, assign, search, close
- `references/pr-workflow.md` — branch → commit → PR → CI → merge
- `references/code-review.md` — review local changes, PRs, inline comments
- `references/github-api-cheatsheet.md` — curl API quick reference
- `references/ci-troubleshooting.md` — CI failure diagnostics
- `references/conventional-commits.md` — commit message format
- `references/windows-msys-git-pitfalls.md` — MSYS2/Git-Bash on Windows: fetch-pack issues, garbage files, SSH timeout, force-push workarounds
- `templates/bug-report.md` — issue template
- `templates/feature-request.md` — feature request template
- `templates/pr-body-bugfix.md` — PR body template (bugfix)
- `templates/pr-body-feature.md` — PR body template (feature)
- `scripts/gh-env.sh` — auth detection helper script
- `scripts/hermes-config-sync.sh` — bidirectional sync: GitHub ↔ hermes-sync ↔ ~/.hermes, with MSYS Git fallbacks
- `references/windows-msys-git-pitfalls.md` — MSYS2/Git-Bash on Windows: fetch-pack issues, garbage files, SSH timeout, force-push workarounds

## Auth Detection (used by all subsections)

```bash
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
```

### Extracting Owner/Repo

```bash
REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
```

## 1. Authentication Setup

See `references/github-auth.md` for detailed setup covering:
- HTTPS with personal access token (recommended)
- SSH key authentication
- gh CLI OAuth login
- Troubleshooting common auth failures

## 2. Repository Management

See `references/repo-management.md` for:
- Cloning (various methods)
- Creating repos (new, from templates)
- Forking and keeping forks in sync
- Repository settings (edit visibility, topics, protection)
- Secrets management (GitHub Actions)
- Releases and release assets
- Gists
- CI workflow management (list, re-run, trigger)

## 3. Issue Tracking

See `references/issues.md` for:
- Viewing and searching issues
- Creating issues (with templates)
- Labeling, assignment, commenting
- Closing and reopening
- Triage workflows
- Bulk operations

## 4. Pull Request Workflow

See `references/pr-workflow.md` for:
- Branch creation and naming conventions
- Committing (conventional commits)
- Pushing and creating PRs
- Monitoring CI status (with polling)
- Auto-fixing CI failures
- Merging (squash, merge, rebase)
- Auto-merge enablement

## 5. Code Review

See `references/code-review.md` for:
- Reviewing local changes (pre-push)
- Reviewing PRs on GitHub
- Inline comments and formal reviews (approve/request changes/comment)
- Full review workflow: context → checkout → diff → checks → feedback
- Review checklist (correctness, security, quality, testing, performance, docs)
- Persistent environment setup and cleanup
- `references/review-output-template.md` — structured review output format

## Cross-Reference

### Hermes Config Sync (GitHub ↔ Local)

For using a GitHub repository as a sync hub for Hermes configuration files (SOUL.md, memories, skills):

- Repository pattern: a single GitHub repo (`OWNER/REPO`) acts as the cloud hub
- Sync scope: SOUL.md, SOUL_Pro.md, SOUL_Edu.md, config.yaml, README.md, memories/, skills/, claw-memory/ (defined by `.gitignore` whitelist)
- Pull strategy: try `git pull`, fall back to `git fetch --depth=1`, then to `git reset --hard origin/main` — see `references/windows-msys-git-pitfalls.md` for known transport issues on MSYS
- Push strategy: `git push`; if rejected (remote ahead), `git push --force` is acceptable for personal sync repos
- Local sync (*): `cp` files bidirectionally between the git repo directory and `~/.hermes/`
- Scheduling: use `cronjob` action=create with `script` pointing to `scripts/hermes-config-sync.sh`
- Cron example: `cronjob action=create name="hermes-sync" script=~/.hermes/skills/github/github-workflows/scripts/hermes-config-sync.sh schedule="every 2h" no_agent=true`
- When local edits should take priority over GitHub (e.g., cron pushes from Windows), set `LOCAL_PRIORITY=true`:
  ```bash
  LOCAL_PRIORITY=true bash ~/.hermes/skills/github/github-workflows/scripts/hermes-config-sync.sh
  ```

(*) The files in `~/.hermes/` are the live config that Hermes reads. The git repo directory is the sync staging area.

### git count-objects -v
```bash
# Shows garbage files from interrupted pack operations
git count-objects -v
# 'garbage: N' indicates orphaned tmp_pack files
# Usually safe to ignore on MSYS; they clear on reboot.
```

All subsections share the same `gh` API surface. Most `curl` API commands use `/repos/{owner}/{repo}/{resource}`. Common API patterns:
- GitHub API base: `https://api.github.com`
- Auth header: `Authorization: token $GITHUB_TOKEN`
- Pagination: add `?per_page=100&page=N`
