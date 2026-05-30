# Git History Repair for hermes-data-sync

## Scenario: Divergent Branches After Cross-PC Edits

When office PC pushed 15 commits and home PC has local uncommitted changes:

### Step-by-step resolution

```bash
cd /mnt/c/Users/Admin/hermes-sync

# 1. Commit local changes first
git add -A
git commit -m "sync $(date +%Y-%m-%d)"

# 2. Try pull with merge (--no-rebase) for divergent branches
# Use --no-edit to avoid editor prompt
GIT_EDITOR=true git pull --no-rebase origin main --no-edit

# 3. If untracked files conflict:
# Remote has files your local repo doesn't know about
git add <conflicting-untracked-files>
git commit -m "local additions before merge"
GIT_EDITOR=true git pull --no-rebase origin main --no-edit

# 4. Resolve merge conflicts manually:
# For additive files (MEMORY.md, USER.md): merge content from both sides
# Remove conflict markers (<<<<<<<, =======, >>>>>>>) and keep all content
git add -A
GIT_EDITOR=true git commit --no-edit

# 5. Push
git push origin main
```

## Scenario: GitHub Push Protection (token leaked in history)

When a GitHub Token was accidentally committed (e.g., in claw-memory/2026-04-26.md):

### Option A: Allow the secret (quickest, for already-revoked tokens)
1. Open the URL from the error message (e.g., `https://github.com/<repo>/security/secret-scanning/unblock-secret/<id>`)
2. If token is still active, go to https://github.com/settings/tokens and delete it first
3. Check "I understand the risks"
4. Click "Allow secret and push"
5. `git push origin main` again

### Option B: Rebase the history to remove the token (preferred, cleaner history)

This is the recommended approach — it permanently removes the secret from the git log.

**Prerequisite**: Clean the worktree first if there are modified files.

```bash
# If worktree is dirty with hundreds of files (stash times out):
git checkout -f main              # Force checkout, discards working changes
# (Only safe if changes are already committed elsewhere, or are synced artifacts)

# IF there's a leftover from a previous broken rebase:
rm -rf .git/rebase-merge
```

**Step 1 — Find the base commit (the clean one before the bad commit):**

```bash
git log --oneline
# Example output:
# ca03eb2 Merge branch 'main'
# 5f89716 local additions before merge
# b3f1070 sync 2026-05-06        ← this has the token
# bbfda01 sync 2026-04-27        ← base: clean commit before the bad one
```

**Step 2 — Start rebase with `--rebase-merges`** (CRITICAL: use this flag when there are merge commits in the history, otherwise the merge structure gets flattened and commits are lost):

```bash
# Use GIT_SEQUENCE_EDITOR to auto-change 'pick b3f1070' to 'edit b3f1070'
GIT_SEQUENCE_EDITOR="sed -i 's/^pick b3f1070/edit b3f1070/'" \
  git rebase -i --rebase-merges bbfda01
```

The `--rebase-merges` flag preserves merge commits by using `label`, `reset`, and `merge` commands in the todo list instead of flattening.

**Step 3 — When rebase stops at the bad commit, edit the file(s):**

```bash
# Remove the token from the file
# Edit with your preferred method
sed -i 's/ghp_[A-Za-z0-9]*/***REMOVED***/g' claw-memory/2026-04-26.md

# Stage and amend
git add claw-memory/2026-04-26.md
git commit --amend --no-edit

# Continue the rebase
git rebase --continue
```

**Step 4 — Handle rebase conflicts (expected when replaying a merge commit):**

```bash
# Check which files conflict
git diff --name-only --diff-filter=U

# If the same conflicts were already resolved in a previous merge commit (ca03eb2 etc.):
# Checkout the resolved versions from that commit via reflog
git checkout <old-merge-commit-hash> -- README.md memories/MEMORY.md memories/USER.md

# Stage and continue
git add -A
GIT_EDITOR=true git rebase --continue
```

**Step 5 — Force push (required because commit IDs changed):**

```bash
git push --force origin main
```

⚠️ Only use `--force` on a private repo where you're the sole contributor. After force push, all other clones must `git pull --rebase` or re-clone.

## Troubleshooting Rebase Issues

### Leftover `.git/rebase-merge` directory
Symptom: `fatal: It seems that there is already a rebase-merge directory`
Fix: `rm -rf .git/rebase-merge`

### Rebase timed out in the middle
Symptom: Process is killed after timeout, leaving rebase in "stopped" state
Fix: `GIT_EDITOR=true git rebase --abort` (use GIT_EDITOR=true to avoid editor prompt)

### `git stash` times out on large repo
Symptom: Stash appears to save but then times out. Worktree still dirty.
Fix: Use `git checkout -f <branch>` to forcibly switch and discard changes.
⚠️ Only do this when changes are already committed elsewhere or are sync artifacts that will be regenerated.

### Merge commit conflicts during rebase
Symptom: `Could not apply <hash>... onto # Merge branch 'main'`
Fix: If you already resolved this exact merge conflict before, check out the resolved files from the old merge commit via `git checkout <hash> -- <files>` (the commit still exists in reflog even after rebase).
