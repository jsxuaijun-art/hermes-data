# Cross-Machine Hermes Agent Data Sync (absorbed from `hermes-agent-sync`)

This reference documents bidirectional sync of Hermes Agent data (SOUL.md, memories, skills, config) across machines via a private GitHub repo. Absorbed from the standalone `hermes-agent-sync` skill (archived). Also see `hermes-data-sync-extraction.md` for the repo restoration use case.

## Architecture

```
办公室 WSL ~/.hermes/  ↔  Windows sync directory  ↔  GitHub private repo  ↔  家里电脑
```

## Files synced (bidirectional)

| File/Dir | Purpose |
|----------|---------|
| `SOUL*.md` | AI identity definition |
| `config.yaml` | Hermes Agent configuration |
| `memories/` | Memory files (MEMORY.md, USER.md) |
| `skills/` | Custom skill packages |

**NOT synced**: `.env` (API keys differ per machine), `sessions/` (large), `state.db`, `logs/`, `caches/`, `checkpoints/`

## Initial setup (one time per machine)

### 1. SSH key setup
```powershell
# Check Windows SSH keys
ls C:\Users\<WindowsUser>\.ssh\

# Copy to WSL (WSL does NOT inherit Windows SSH keys!)
wsl -d <DistroName> -- bash -c "
  mkdir -p ~/.ssh
  cp /mnt/c/Users/<WindowsUser>/.ssh/id_ed25519 ~/.ssh/
  cp /mnt/c/Users/<WindowsUser>/.ssh/id_ed25519.pub ~/.ssh/
  chmod 600 ~/.ssh/id_ed25519
"
# Verify
wsl -d <DistroName> -- ssh -T git@github.com
```

### 2. Create private GitHub repo & clone
```powershell
git clone git@github.com:<Owner>/<Repo>.git /path/to/sync/dir
```

### 3. Initial fill direction
- **WSL has data → push to sync dir**: copy from WSL to sync dir, then git push
- **Sync dir has data → pull to WSL**: git pull, then copy to WSL `~/.hermes/`

## Daily operations

### Push (WSL → GitHub)
```powershell
# Step 1: Copy WSL data to Windows sync dir
wsl -d <DistroName> -- bash -c "
  cp -f ~/.hermes/SOUL*.md /mnt/c/Users/<WindowsUser>/Desktop/HermesAgent/
  cp -rf ~/.hermes/memories/*.md /mnt/c/Users/<WindowsUser>/Desktop/HermesAgent/memories/
  cp -rf ~/.hermes/skills/* /mnt/c/Users/<WindowsUser>/Desktop/HermesAgent/skills/
  cp -f ~/.hermes/config.yaml /mnt/c/Users/<WindowsUser>/Desktop/HermesAgent/
"

# Step 2: Git commit + push (in Windows cmd.exe)
cd /d C:\Users\<WindowsUser>\Desktop\HermesAgent
git add -A
git commit -m "sync %date:~0,10% %time:~0,5%"
wsl -d <DistroName> -- bash -c "cd /mnt/c/Users/<WindowsUser>/Desktop/HermesAgent && git push origin main"
```

### Pull (GitHub → WSL)
```powershell
# Step 1: Pull from GitHub
cd /d C:\Users\<WindowsUser>\Desktop\HermesAgent
wsl -d <DistroName> -- bash -c "cd /mnt/c/Users/<WindowsUser>/Desktop/HermesAgent && git pull origin main"

# Step 2: Copy to WSL
wsl -d <DistroName> -- bash -c "
  cp -f /mnt/c/Users/<WindowsUser>/Desktop/HermesAgent/SOUL*.md ~/.hermes/
  cp -rf /mnt/c/Users/<WindowsUser>/Desktop/HermesAgent/memories/*.md ~/.hermes/memories/
  cp -rf /mnt/c/Users/<WindowsUser>/Desktop/HermesAgent/skills/* ~/.hermes/skills/
  cp -f /mnt/c/Users/<WindowsUser>/Desktop/HermesAgent/config.yaml ~/.hermes/
"
```

## Critical pitfalls

### SSH key isolation
Windows SSH keys are NOT shared with WSL. Must `cp` manually and `chmod 600`.

### Chinese encoding in .bat files
`write_file` creates UTF-8 without BOM; cmd.exe parses as GBK. Chinese/Unicode box chars become garbled. **Only reliable fix**: pure ASCII in .bat files (no Chinese, no box-drawing chars).

### Git proxy in China
Windows has proxy (Clash/V2Ray on 127.0.0.1:7890), but WSL2 NAT can't reach localhost proxy. **Run git from Windows cmd.exe**, not WSL:
```
git config http.proxy http://127.0.0.1:7890
git config https.proxy http://127.0.0.1:7890
```

### Use fetch+reset instead of pull
Multi-device sync creates frequent merge conflicts. Use `git fetch origin main && git reset --hard origin/main` to overwrite cleanly.

### .gitignore ordering
Exclusion rules (`*`) go FIRST, then whitelist rules (`!xxx`). Wrong order means whitelisted files still get excluded.

### Single-line bash -c for .bat
cmd.exe doesn't support multiline `"..."` strings. Use `&&` or `;` to chain commands:
```
wsl -d Ubuntu -- bash -c "cp -f X Y; cp -f A B"
```

### Desktop path redirection
Desktop may be at `D:\360MoveData\Users\<User>\Desktop\` or similar. Use `dir /b Desktop` or `find /mnt -name "HermesAgent" -type d` to find it.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Recv failure: Connection was reset` | No git proxy | `git config http.proxy http://127.0.0.1:7890` |
| `WSL_E_DISTRO_NOT_FOUND` | Wrong WSL name | `wsl -l -v` to check |
| Garbled text in .bat | UTF-8/GBK mismatch | Use pure ASCII |
| Merge conflicts (CONFLICT) | Multi-device edits | Use `fetch + reset --hard` |
| Token prompt every time | No credential helper | `git config credential.helper store --file .git/credentials` |

## Recovery after system reinstall

All core data lives on GitHub. Reinstall process:
1. Install WSL + Hermes Agent (5 min)
2. Clone the sync repo (1 min)
3. Copy SOUL.md + memories + skills + config.yaml to `~/.hermes/` (1 min)

Lost: `sessions/` (chat history) and `.env` (get API keys from provider dashboards)
