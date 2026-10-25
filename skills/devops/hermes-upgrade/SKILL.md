---
name: hermes-upgrade
category: devops
description: Upgrade a git-installed Hermes to the latest version.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, upgrade, update, devops]
    related_skills: [hermes-agent-sync, hermes-data-sync]
triggers:
  - User asks to upgrade or update Hermes to the latest version
  - User wants to switch Hermes from a third-party mirror back to the official GitHub source (原版)
  - hermes version reports commits behind and the user wants to act on it
---

# Upgrading a self-hosted (git-installed) Hermes Agent

## When to Use

User asks to upgrade/update Hermes itself to the latest version, or wants to
restore the official GitHub source (原版) when a third-party mirror is the
origin. Not for data sync — that is `hermes-agent-sync` / `hermes-data-sync`.

Hermes is usually installed from source into `~/.hermes/hermes-agent/` (the
`install.sh` method). This skill covers upgrading THAT form — not pip, not the
Docker image, and not cross-machine data sync (see `hermes-agent-sync` /
`hermes-data-sync` for those).

## Diagnose the install first

```bash
hermes --version              # version + date
hermes version                # ALSO reports install method + "X commits behind" + upstream hash
cd ~/.hermes/hermes-agent && git remote -v   # WHICH source is origin? upstream?
which hermes && head -1 $(which hermes)      # launcher is a script → confirms git/venv install
grep -m1 '^version' pyproject.toml           # real version string
```

Key facts about a git install:
- Source lives in `~/.hermes/hermes-agent/`.
- The `hermes` launcher at `~/.local/bin/hermes` is a small script whose shebang
  points into `~/.hermes/hermes-agent/venv/bin/python3`. `pip show hermes`
  yields nothing — the package is used from the source dir, not installed to
  site-packages as a normal editable package you'd query.
- Each remote may be a different lineage. Do NOT assume `origin` == official.

## Determine the OFFICIAL latest version

`hermes version` reports "commits behind" **relative to whatever `origin`
points at**. If origin is a third-party mirror (e.g. `cnb.cool/...-mirror.git`),
that count is meaningless for "is there an official update?".

Official latest = `upstream` remote (or any remote url ending
`github.com/NousResearch/hermes-agent.git`). Compare the version string across
remotes:

```bash
git fetch upstream main            # upstream = official GitHub (may need timeout)
git show upstream/main:pyproject.toml | grep -m1 '^version'
git rev-list --count HEAD..upstream/main    # how many official commits behind
git rev-list --count HEAD..origin/main      # how many behind the mirror (may differ!)
```

Conclusion pattern to give the user:
- "官方最新版本号仍是 X.Y.Z" if `pyproject.toml` version matches local.
- Separate the TWO axes: version number vs commit count. A big "commits behind"
  does NOT mean a higher version exists — it can be patch-level churn on the
  same version. Confirm from `pyproject.toml`, never from the commit count alone.

## The critical guard: you CANNOT rewrite the live checkout in-session

Hermes blocks `git reset` / destructive checkout on
`/root/.hermes/hermes-agent` **while the agent is running from that directory**,
because rewriting the source would mix module versions in the live process. The
security layer rejects it with a message telling you to use a separate
worktree / run externally / restart.

So the upgrade CANNOT be completed inside a running Hermes session. Correct flow:

1. Investigate everything read-only (remotes, versions, cleanliness) in-session.
2. Write an external upgrade **script** to a path OUTSIDE the source dir
   (e.g. `/root/upgrade_hermes_official.sh`).
3. Ask the user to exit Hermes (`/exit` or Ctrl+C), run the script in the WSL
   terminal, then relaunch `hermes`.
4. Have the script re-verify version + commit after reset.

Before handing to the user, confirm the tree is clean (`git status --porcelain`
empty) — `git reset --hard` is only safe when there are no uncommitted changes.
If dirty, say so; do NOT reset over uncommitted work.

## Switching to the OFFICIAL source (原版) when origin is a mirror

If `git remote get-url origin` points at a third-party mirror and the user wants
the original, the script must:
- `git fetch --quiet origin main`
- `git remote set-url origin https://github.com/NousResearch/hermes-agent.git`
  (re-point origin at the official repo so future `hermes update` pulls official)
- `git reset --hard origin/main`
- reinstall deps: `./venv/bin/pip install -e . --quiet` (git installs keep deps
  inside `venv/`)

The user preference documented for this environment: **prefer the official
GitHub original over third-party mirrors.**

## WSL / network notes

- The Windows-side proxy at `127.0.0.1:7890` is unreachable FROM WSL — ignore it
  for WSL operations (it's a Windows-loopback address).
- Direct `git fetch` / `git ls-remote` to `github.com` over https generally works
  from WSL even without a proxy, so no proxy is needed for the git-based upgrade.
- `raw.githubusercontent.com` and `api.github.com` can route/limit differently
  (CDN vs API); prefer git fetch over listing tags when tag enumeration times
  out, and bound long commands with a timeout.
- `git ls-remote --tags upstream` can time out because the repo has thousands of
  tags; fetching the single `main` branch is fast and sufficient for version
  checks.

## Reference script

`scripts/upgrade_hermes_official.sh` — known-good template: fetch official main,
re-point origin at official GitHub, `reset --hard`, reinstall venv deps, verify.
Copy (don't blindly run) and adapt per machine, then run it from OUTSIDE a
live Hermes session.
