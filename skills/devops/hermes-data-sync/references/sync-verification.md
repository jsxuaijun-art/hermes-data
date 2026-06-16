# Sync Verification (同步后验证)

After running either 推送.bat or 拉取.bat, DON'T trust the "✓ 完成" message — verify.

## ⚠️ Step 0: Verify WSL Path Is Correct

The single most common sync failure: .bat script copies to `/root/.hermes/` but Hermes reads from `/home/dmin/.hermes/`.

```bash
# Check: does /root/.hermes/ exist?
ls /root/.hermes 2>/dev/null && echo "⚠️ /root/.hermes EXISTS — sync likely writing to wrong location!" || echo "✅ /root/.hermes does not exist (correct)"

# Verify actual Hermes home
stat ~/.hermes/SOUL.md | grep "Access: " | head -1
whoami
```

If `/root/.hermes/` exists and has files, the .bat scripts are writing to the wrong place. Fix `WSL_HOME` variable in the .bat.

## Quick Check (30 seconds)

Run in WSL:

```bash
cd /mnt/c/Users/Admin/hermes-sync

# 1. Git status
git status --short

# 2. Check variable consistency
echo "WSL_HOME should be /home/dmin — is it correct in your .bat?"

# 3. Compare key files
for f in SOUL.md SOUL_Pro.md SOUL_Edu.md config.yaml memories/MEMORY.md memories/USER.md; do
  repo_hash=$(git show HEAD:"$f" 2>/dev/null | md5sum | cut -d' ' -f1)
  wsl_path=""
  case "$f" in
    memories/*) wsl_path="$HOME/.hermes/$f" ;;
    *) wsl_path="$HOME/.hermes/$f" ;;
  esac
  wsl_hash=$(md5sum "$wsl_path" 2>/dev/null | cut -d' ' -f1)
  if [ "$repo_hash" = "NOT_EXIST" ] && [ -z "$wsl_hash" ]; then
    echo "⚠️ $f — 两边都不存在"
  elif [ "$repo_hash" = "NOT_EXIST" ]; then
    echo "📄 $f — 仅在 WSL 有"
  elif [ -z "$wsl_hash" ]; then
    echo "📄 $f — 仅在 Git 有"
  elif [ "$repo_hash" = "$wsl_hash" ]; then
    echo "✅ $f — 一致"
  else
    echo "❌ $f — 不同！"
  fi
done
```

## Known Drift Patterns

### Pattern 1: WSL has English default SOUL, Git has Chinese custom SOUL

**Detection**: `❌ SOUL.md — 不同！`
**Root cause**: Hermes Agent was reinstalled or started with default config, overwriting `~/.hermes/SOUL.md`
**Fix**: Run `Hermes同步-拉取.bat` to restore from git, or manually:
```bash
cp /mnt/c/Users/Admin/hermes-sync/SOUL.md ~/.hermes/SOUL.md
```

### Pattern 2: SOUL_Pro.md / SOUL_Edu.md in Git but not in WSL

**Detection**: `📄 SOUL_Pro.md — 仅在 Git 有`
**Root cause**: These files were committed from another PC but never copied to this WSL
**Fix**: Copy them over:
```bash
cp /mnt/c/Users/Admin/hermes-sync/SOUL_Pro.md ~/.hermes/
cp /mnt/c/Users/Admin/hermes-sync/SOUL_Edu.md ~/.hermes/
```

### Pattern 3: MEMORY.md / USER.md diverged

**Detection**: `❌ memories/MEMORY.md — 不同！`
**Root cause**: Both PCs added independent memories. This is NORMAL — the merge intentionally keeps both sides.
**Fix**: If the merge produced duplication (duplicate entries), clean up manually. Otherwise no action needed.

### Pattern 4: config.yaml differs

**Detection**: `❌ config.yaml — 不同！`
**Root cause**: Each PC has different config (API keys, models, etc.)
**Fix**: This file should NOT be blindly synced. Each PC keeps its own. If the sync overwrites it, restore:
```bash
# Restore from WSL's backup (if exists)
cp ~/.hermes/config.yaml.bak ~/.hermes/config.yaml
```

## Secret Leak Verification

After a history rewrite (token leaked into a commit):

```bash
cd /mnt/c/Users/Admin/hermes-sync
git log --all -p | grep -c "ghp_" && echo "⚠️ Token still in history!" || echo "✅ Clean"

# Also verify the remote (after force push):
git ls-remote origin main | cut -f1

# Confirm the specific file no longer has the token:
git show HEAD:claw-memory/2026-04-26.md | grep -i "ghp_" && echo "⚠️ FOUND" || echo "✅ Token removed"
```

## Full Diff (when you need to see what exactly changed)

```bash
cd /mnt/c/Users/Admin/hermes-sync

# Diffs for each key file
for f in SOUL.md config.yaml; do
  echo "=== $f ==="
  diff <(git show HEAD:"$f") "$HOME/.hermes/$f" | head -30
  echo
done
```
