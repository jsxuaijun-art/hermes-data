---
name: hermes-upgrade
description: "Update Hermes safely (guard, external exec, PyPI mirror)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes-agent, update, upgrade, pip, mirror, pypl, uv, maintenance]
    related_skills: [hermes-agent, python-debugpy]
---

# Hermes Agent Update / Upgrade

Use this skill when the user asks to update Hermes (`hermes update`), when `hermes update --check` reports commits behind, or when upgrading the agent across a large version jump.

## When to Use

- User runs `hermes update` / `hermes version` and sees "Update available"
- A big version jump is pending (e.g. v0.20 → latest, hundreds/thousands of commits)
- The local checkout carries a local patch (setup.py localization, etc.) that might conflict with upstream
- PyPI/PyPI-mirror install stalls during update
- You need to update the running Hermes instance's source code

## Critical: Safety Guard Blocks In-Place Source Changes

Hermes deliberately protects a **live (running) checkout**. These git operations are BLOCKED by the agent guard while inside a session running from that checkout:

- `git rebase` / `git rebase --onto` — blocked
- `git merge` — blocked
- `git checkout` — blocked (even in a temp clone whose mirror points at the live repo)
- The guard detects this by repo identity, not just the directory path — even `git clone --mirror ~/.hermes/hermes-agent` then `git checkout` under `/tmp` is still blocked.

The guard message: *"Blocked: `<cmd>` would rewrite Hermes's live source checkout ... Use a separate worktree or temporary clone. To change this checkout, stop Hermes, run the command externally, then restart Hermes."*

**Consequence:** You (the agent) CANNOT update the live checkout from inside the session. The correct flow is to hand the user a script/command to run **externally in their own terminal**, then restart Hermes. Do not burn turns trying `git fetch`/`merge`/`rebase`/`checkout` against the live repo — they will all be blocked.

Note: read-only ops are fine — `git fetch`, `git show`, `git log`, `git status`, `git merge-tree --write-tree`, `git rev-parse HEAD`.

## Pre-Update Verification (before handing off)

Confirm a local patch will survive the merge BEFORE telling the user to update:

1. **Check upstream didn't touch the patched file:**
   ```bash
   cd ~/.hermes/hermes-agent
   git log --oneline HEAD..origin/main -- <patched_file>   # count of commits touching it
   ```
   If zero, the patch is safe — merge will keep it.

2. **Dry-run the merge without touching the working tree:**
   ```bash
   git merge-tree --write-tree origin/main HEAD   # exit 0 + a tree hash = merge is clean
   ```
   This does NOT write to the checkout, so the guard does not fire.

3. **Confirm patch markers still intended to survive:**
   ```bash
   grep -c "_translate_setup_text" hermes_cli/setup.py   # >=1 means the zh patch is present in local
   git show origin/main:<patched_file> | grep -c "<sentinel>"   # 0 means upstream has no such patch
   ```

## The PyPI Mirror Env-Var Trick

`hermes update` reinstalls deps via `uv pip install -e .[all]`. It builds the uv env as `uv_env = {**os.environ, ...}` — i.e. **uv inherits the parent shell's environment variables**. So you can force the mirror by exporting the standard uv/pip index vars BEFORE running the update (no Hermes source edit needed):

```bash
export UV_DEFAULT_INDEX="https://pypi.tuna.tsinghua.edu.cn/simple/"
export UV_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple/"
export PIP_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple/"
export PIP_TRUSTED_HOST="pypi.tuna.tsinghua.edu.cn"
hermes update --yes --backup
```

Why 4 vars: `UV_DEFAULT_INDEX` / `UV_INDEX_URL` are uv-native; `PIP_INDEX_URL` / `PIP_TRUSTED_HOST` cover the fallback `python -m pip` path (`_install_python_dependencies_with_optional_fallback`). This is the ~100× speedup that turns a 30+ min stuck PyPI install into seconds (see `references/china-mirror-detail.md`).

**useful flags:** `--yes/-y` assumes yes on interactive prompts (config migration, stash restore); `--backup` forces a FULL pre-update zip backup; `--no-backup` skips; `--check` reports commits behind without installing; `--branch NAME` / `--force`.

## Handoff Pattern

Because the update must run externally and is interactive, prepare a self-contained script in `/tmp` (or give exact commands) that:

1. Snapshot a rollback point (`git bundle create ~/hermes_backup_<ts>/hermes.bundle --all` + `git rev-parse HEAD > CURRENT_COMMIT.txt`) — lighter and fully reversible vs copying the whole repo.
2. Export the 4 mirror vars above.
3. Run `hermes update --yes --backup` in the foreground (needs a real terminal).
4. Verify the local patch survived: `grep -c '<sentinel>' <patched_file>`.

Then instruct the user to: exit the session → `bash /tmp/<script>.sh` → relaunch `hermes`.

Tell the user what answers to give if prompted (config migration / stash restore → `y`; patch conflict → keep local).

## Pitfalls

- **Don't try `git checkout`/`merge`/`rebase` on the live repo from inside the session** — every one is blocked by the guard. Hand off to an external terminal instead.
- **The guard follows repo identity, not path.** A temp clone whose origin is the live repo still triggers it. Stop fighting it; use the external-execution handoff.
- **Mirror vars must be exported in the SAME shell that runs `hermes update`**, because uv/pip read them from the environment at that point.
- **Confirm the mirror mechanism is wired correctly before the user runs it** — uv here is bootstrapped by `install_python_dependencies` into `$HERMES_HOME/bin/uv`, so it may not exist yet; the env vars are inherited regardless.
- **A big jump can edit files the local patch touched.** Always run the pre-update verification (above) first. If upstream DID touch the patched function, tell the user a patch-merge conflict is possible and they should keep local.
- **💥 fork-sync runs `git reset --hard origin/main` and SILENTLY DROPS local-only commits** (reflog shows `reset: moving to origin/main`). Even a committed-but-local-only patch (like the zh setup.py patch) is thrown off `main`; the working tree then reverts to plain upstream. The commit is NOT deleted — it still lives in the git object store, so recovery is possible (see Patch Recovery below).
- **💥 fork-sync hangs at `Username for 'https://cnb.cool':`** — the remote `origin` points at the cnb.cool China mirror, and the fork-sync step tries to `git push` (needs auth; no credential helper configured). This is a blocking interactive credential prompt. **Just Ctrl+C it** — fork-sync only mirrors your local branch back to the remote, it does NOT affect the update result. (Read-only `git ls-remote` still works anonymously.)

## Patch Recovery (zh setup.py localization, lost after update)

The zh patch commit is `e1a189d05b04f82728744c0b45d836f99dea15c4f` (70 insertions, 9 deletions). After an update wipes it, restore from the object store:

```bash
cd ~/.hermes/hermes-agent
git show e1a189d05b04f82728744c0b45d836f99dea15c4f > /tmp/patch-full.diff
git apply --check /tmp/patch-full.diff      # succeeds; only a harmless offset like "-89 lines"
git apply /tmp/patch-full.diff
venv/bin/python -m py_compile hermes_cli/setup.py   # verify syntax
git add hermes_cli/setup.py && git commit -m "chore: restore zh setup patch (re-applied onto vX.Y.Z)"
```

Why it re-applies cleanly: upstream does NOT touch `prompt_yes_no` nor the `_translate_setup_text`/`_SETUP_TRANSLATIONS`/`_orig_print` helper region, so the diff applies with only a line-offset. Confirmed via `git merge-tree --write-tree origin/main <base>` exit 0.

**Anchors against future loss:**
- tag: `git tag -f zh-setup-patch` points at the patched commit.
- file backup: `~/hermes_zh_setup_patch.diff` lives OUTSIDE the repo (not swept by git cleanup).
- After any update, verify: `grep -c "_translate_setup_text" hermes_cli/setup.py` → must be ≥1.

## Related

- `hermes-agent` skill: full CLI config, `hermes update` reference, troubleshooting. (Re-run the update's post-pull steps with the mirror if `hermes update` times out mid-install.)
- `references/china-mirror-detail.md` — China-network specifics for this user's WSL setup.
