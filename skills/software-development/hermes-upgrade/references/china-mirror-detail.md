# China Network / Mirror Detail (WSL)

Context for this user: Hermes runs inside WSL (Ubuntu), source at `~/.hermes/hermes-agent`, with a local Chinese-localization patch on `hermes_cli/setup.py` (a `prompt_yes_no` zh translation + `_SETUP_TRANSLATIONS` / `_translate_setup_text` / `_orig_print` helpers). Direct PyPI is painfully slow (~30 kB/s or constant "Connection timed out").

## Why PyPI stalls

`hermes update` reinstalls `[all]` deps. Without a mirror, pip/uv sits below 1% CPU for many minutes while `~/.cache/pip` barely grows — that's a stalled network pipe, not busy computation. Kill it and re-run with a mirror.

## Mirror vars to export before `hermes update`

```bash
export UV_DEFAULT_INDEX="https://pypi.tuna.tsinghua.edu.cn/simple/"
export UV_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple/"
export PIP_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple/"
export PIP_TRUSTED_HOST="pypi.tuna.tsinghua.edu.cn"
hermes update --yes --backup
```

Must be exported in the SAME shell that runs the update. `hermes update` invokes `uv pip install -e .[all]` with `uv_env = {**os.environ, ...}`, so uv inherits these. `PIP_INDEX_URL` also covers the fallback bare-`pip` path.

Alternative mirror: `https://mirrors.aliyun.com/pypi/simple/`.

## Tailoring to this user's checkout

⚠️ **IMPORTANT (v0.20.1 experience): "committed so autostash doesn't touch it" is WRONG.** Although the zh patch is a normal commit (not stashed), `hermes update`'s **"Syncing fork" step runs `git reset --hard origin/main`**, which THROWS the local-only committed patch OFF `main` — the working tree reverts to plain upstream and the patch is lost from the branch. (The commit remains in the object store; recover per the main SKILL.md "Patch Recovery" section.) So ALWAYS verify the patch after every update, even for commits.

Steps after every update:
```bash
grep -cn "_translate_setup_text\|_SETUP_TRANSLATIONS\|_orig_print" hermes_cli/setup.py
```
Returns >=1 when the localization is intact (upstream has 0 of these markers). If it returns 0, the patch was dropped — re-apply it (see main SKILL.md "Patch Recovery" section).

**The zh setup.py patch is also a live GitHub thing:** this user has a separate fork mirrored as `origin` at cnb.cool, plus `upstream` = GitHub. `hermes update` first fetches `upstream main`, then rebases/merge, then **tries to push to `origin` (cnb.cool) with no credential helper → hangs at `Username for 'https://cnb.cool':`**. Ctrl+C to skip; it does not affect the update.

- A past big jump (v0.15 → v0.20, 1600+ commits) hit a `git stash pop` content conflict in `prompt_yes_no` because upstream added an `is_noninteractive()` early-return. Resolution was to keep BOTH the upstream `is_noninteractive()` guard AND the local zh translation lines, then `python -m py_compile hermes_cli/setup.py`, `git commit`, `git stash drop`.

## Rollback

`hermes update` keeps its own `--backup` zip, but an extra lightweight rollback point before updating:
```bash
mkdir -p ~/hermes_backup_$(date +%Y%m%d_%H%M%S)
SNAP=~/hermes_backup_$(date +%Y%m%d_%H%M%S)
git -C ~/.hermes/hermes-agent bundle create "$SNAP/hermes.bundle" --all
git -C ~/.hermes/hermes-agent rev-parse HEAD > "$SNAP/CURRENT_COMMIT.txt"
# restore later with:
# git -C ~/.hermes/hermes-agent fetch <path>/hermes.bundle main
# git -C ~/.hermes/hermes-agent reset --hard FETCH_HEAD
```
