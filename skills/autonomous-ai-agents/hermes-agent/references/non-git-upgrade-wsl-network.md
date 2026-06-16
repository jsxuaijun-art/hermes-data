# Non-Git Hermes Upgrade: WSL2 Network Resilience

## Context

Upgrade Hermes Agent from a **non-git installation** (tarball/`setup-hermes.sh`) in a **WSL2 environment** with a **slow/unreliable GitHub connection** (~20-30KB/s, frequent drops).

## Upgrade Workflow Overview

```
1. Download tarball (pick fastest path)
2. Verify Python version → install Python 3.11+ if needed
3. Extract to Linux-native filesystem (/tmp)
4. Create new Python 3.11 venv
5. pip install -e . from /tmp (NOT from NTFS)
6. Copy tools/ + skills/ + plugins/ to Windows project dir
7. Update start script
8. Verify
```

## Step 0: Discover Windows Proxy (Clash/TUN/Clash.Meta)

If Windows has a proxy running (Clash, Clash Verge, etc.), WSL can use it for much faster downloads.

```bash
# 1. Get Windows host IP from WSL's default route
WIN_IP=$(ip route | grep default | awk '{print $3}')
echo "Windows IP: $WIN_IP"

# 2. Test proxy (default Clash port is 7890)
export http_proxy="http://$WIN_IP:7890"
export https_proxy="http://$WIN_IP:7890"
curl -sI --proxy "$http_proxy" "https://google.com" | head -1
# Expected: HTTP/2 200
```

**Troubleshooting:**
- **HTTP 000 (connection refused):** Clash may have "Allow LAN" turned OFF → enable it in Clash settings
- **Wrong port:** Check Windows Registry: `reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyServer`
- **Windows firewall:** WSL may be blocked; try `172.x.x.x:7890` instead of `127.0.0.1:7890`

---

## Step 1: Download Tarball

### Option A: Proxy (FASTEST — 1.3MB/s, 20s) ⭐

After verifying proxy is reachable:

```bash
cd /path/to/new-timestamped-directory
WIN_IP=$(ip route | grep default | awk '{print $3}')
PROXY="http://$WIN_IP:7890"

curl -L --max-time 600 \
  --proxy "$PROXY" \
  "https://github.com/NousResearch/hermes-agent/archive/refs/tags/v<TAG>.tar.gz" \
  -o hermes-source.tar.gz

# Verify
ls -lh hermes-source.tar.gz    # Should be ~28MB
file hermes-source.tar.gz       # gzip compressed data
```

### Option B: Manual browser download (100% reliable)

```bash
# 1. Open Windows browser → paste URL:
#    https://github.com/NousResearch/hermes-agent/archive/refs/tags/v<TAG>.tar.gz
# 2. Save to Desktop (auto-named v<TAG>.tar.gz)
# 3. Copy to WSL:
cp /mnt/c/Users/<WindowsUser>/Desktop/v<TAG>.tar.gz /path/to/target/
mv v<TAG>.tar.gz hermes-source.tar.gz
```

### Option C: wget resume loop (~38KB/s)

wget may outperform curl in some WSL2 environments:

```bash
cd /path/to/target-dir
rm -f hermes-source.tar.gz

for i in $(seq 1 20); do
  echo "=== Attempt $i ==="
  wget --continue --tries=3 --timeout=120 --retry-connrefused \
    --read-timeout=120 \
    "https://github.com/NousResearch/hermes-agent/archive/refs/tags/v<TAG>.tar.gz" \
    -O hermes-source.tar.gz 2>&1 | tail -5

  if [ -f hermes-source.tar.gz ]; then
    size=$(stat -c%s hermes-source.tar.gz 2>/dev/null || stat -f%z hermes-source.tar.gz)
    echo "Size: $size bytes"
    if [ "$size" -gt 27000000 ]; then
      echo "Download complete!"
      break
    fi
  fi
  sleep 5
done
```

### Option D: curl resume loop (~20-30KB/s)

```bash
cd /path/to/target-dir
rm -f hermes-source.tar.gz

for i in $(seq 1 20); do
  echo "=== Attempt $i ==="
  curl -L --max-time 1800 --retry 3 --retry-delay 5 \
    -C - \
    "https://github.com/NousResearch/hermes-agent/archive/refs/tags/v<TAG>.tar.gz" \
    -o hermes-source.tar.gz 2>&1 | tail -5

  if [ -f hermes-source.tar.gz ]; then
    size=$(stat -c%s hermes-source.tar.gz)
    echo "Size: $size bytes"
    if [ "$size" -gt 27000000 ]; then
      echo "Download complete!"
      break
    fi
  fi
  sleep 5
done
```

### What Didn't Work

| Approach | Result | Root Cause |
|----------|--------|-----------|
| `curl --http1.1` | SSL EOF | GitHub CDN forces HTTP/2 |
| `curl.exe` (Windows) | Connection reset | WSL bridge + Windows firewall |
| `curl --limit-rate 100k` | More drops, slower | TCP window can't grow |
| Chinese mirrors (ghproxy, etc.) | Timeout | DNS/firewall or geo-restriction |
| `pip install hermes-agent` | Package not found | Not on PyPI |
| `hermes update` | Not a git repo | Requires git installation |
| `hermes update --check` | Same error | Not a useful diagnostic on non-git |

---

## Session-Specific Observations (2026.5.28)

From a live upgrade attempt of v0.12.0 → v2026.5.16 in WSL2 + China network:

### What Worked vs What Didn't

| Approach | Result | Details |
|----------|--------|---------|
| `curl -sL` to GitHub API (`/releases/latest`) | Works | Returns JSON with `tag_name`. 30s timeout sufficient. |
| `curl -sI` redirect URL check (`/releases/latest`) | Timeout | Redirect resolution hangs. Use API endpoint instead. |
| `wget` to tarball URL | SSL failure | `Unable to establish SSL connection` — GitHub forces HTTP/2, wget can't negotiate. |
| `curl` direct to tarball URL | Connection timeout | 135s timeout on port 443. Connection drops before any byte transfers. |
| `codeload.github.com` | User blocked | Alternative CDN URL, same network layer. |
| Browser download on Windows | User option | Most reliable contingency. |

### Key Observations

1. **API endpoint is more resilient than raw download URL.** `api.github.com/repos/.../releases/latest` connects and returns data when raw tarball URLs time out. Use API for version checks, not for tarball download.

2. **Background process output buffering is unreliable in bash loops.** The retry-loop script's `2>&1` to `tail` did not produce visible stdout in the agent's process log. For long-running downloads, use a single curl command with long `--max-time` and check file size afterward.

3. **No Chinese mirror worked** (ghproxy.com, fastgit, etc.). Same result as earlier testing — all time out.

### Recommended Pre-Flight Sequence (for this environment)

```bash
# 1. Check current version + project path
hermes --version

# 2. Git or tarball?
ls -la /path/to/hermes-agent/.git 2>/dev/null && echo GIT || echo TARBALL

# 3. Get latest version via API (more reliable than redirect)
curl -sL --max-time 30 'https://api.github.com/repos/NousResearch/hermes-agent/releases/latest' | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tag_name'))"
```

Then if tarball install + no proxy available → **Option B (manual browser download)** is the only reliable path.

---

## Step 2: Check Python Version

**v0.14.0 requires Python ≥ 3.11.** Ubuntu 22.04 ships Python 3.10 by default.

```bash
python3 --version   # If 3.10.x, install 3.11

sudo apt-get install -y python3.11 python3.11-venv python3.11-dev
# Verify
python3.11 --version
```

---

## Step 3: Extract Tarball

⚠️ **Critical: Extract to `/tmp` (Linux tmpfs), NOT to Windows NTFS.** NTFS extraction is slow and can timeout for 72MB+ archives.

```bash
cd /tmp
tar xzf /path/to/hermes-source.tar.gz
# Creates directory: hermes-agent-<TAG>/

# Verify extraction is COMPLETE — check key directories exist
ls /tmp/hermes-agent-<TAG>/tools/*.py | head -5   # Should show many files
find /tmp/hermes-agent-<TAG>/ -type f | wc -l      # Expect ~1000+ files
```

**If tar extraction timed out (exit 124):** The extraction is partial. Re-extract or do targeted recovery:

```bash
# Option A: Re-extract to a clean /tmp
rm -rf /tmp/hermes-agent-<TAG>
tar xzf /path/to/hermes-source.tar.gz -C /tmp/

# Option B: Supplement missing directories from the tarball
# (e.g., if tools/ directory is missing)
cd /tmp/hermes-agent-<TAG>
tar xzf /path/to/hermes-source.tar.gz \
  --strip-components=1 \
  "hermes-agent-<TAG>/tools/"
```

---

## Step 4: Create Python 3.11 venv & Install

⚠️ **Critical: Do NOT run `pip install -e .` from the Windows NTFS directory.** Setuptools tries POSIX operations (chmod, symlink, etc.) that NTFS doesn't support, causing `[Errno 1] Operation not permitted`.

```bash
# Create fresh venv with Python 3.11 (NOT from existing 3.10 venv)
python3.11 -m venv /home/<user>/.venv-hermes-311

# Activate and upgrade pip
source /home/<user>/.venv-hermes-311/bin/activate
pip install --upgrade pip setuptools wheel

# Install from /tmp (Linux native filesystem)
cd /tmp/hermes-agent-<TAG>
pip install -e .

# Verify
python -m hermes_cli.main --version
# Expected: Hermes Agent v0.14.0 (2026.5.16) | Python: 3.11.x
```

**Note about `/tmp` persistence:** Editable installs from `/tmp` will break on reboot (tmpfs is cleared). Either:
- Keep a copy of the source in a persistent location (e.g., `/home/<user>/` or Windows NTFS project dir)
- Accept that `/reset` (reinstall) is needed after reboot
- After install, the venv's site-packages contain a `.pth` link file — if `/tmp` is cleaned, reinstall from the Windows source dir

---

## Step 5: Sync to Windows Project Directory

If you keep the project files in a Windows directory (e.g., `D:\...`), sync the source after extraction:

```bash
# Source is on /tmp — copy tools/, skills/, plugins/ to Windows dir
mkdir -p /mnt/c/Users/<user>/.../hermes-agent-<TAG>/tools/
cp -r /tmp/hermes-agent-<TAG>/tools/* /mnt/c/Users/<user>/.../hermes-agent-<TAG>/tools/

# Do the same for any other missing directories
```

---

## Step 6: Update Launch Script

Update `start-hermes.sh` or equivalent:

```bash
#!/bin/bash
source ~/.venv-hermes-311/bin/activate               # ← NEW venv
cd /mnt/c/Users/.../hermes-agent-<TAG>/               # ← NEW directory
export PYTHONPATH=$PWD:$PYTHONPATH
```

---

## Step 7: Verify

```bash
source ~/.venv-hermes-311/bin/activate
cd /path/to/project-dir

# Check version
python -m hermes_cli.main --version

# Test actual agent initialization
python -m hermes_cli.main chat -q "说'测试通过'就结束" -Q
# Expected: session_id + "测试通过"
```

---

## Version Compatibility Notes

| Old v0.12.0 | New v0.14.0 | Impact |
|-------------|-------------|--------|
| Python 3.10 | Python ≥ 3.11 | Must create new venv |
| `-z PROMPT` (query) | `-q PROMPT` (query) | CLI argument renamed |
| `--quiet` | `-Q` flag | Short flag added |
| CheckpointManager `max_total_size_mb` | Renamed/removed | Config auto-migration |
| Config schema | Updated `_config_version` | Run `hermes config migrate` |

---

## Symptom → Fix Quick Reference

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `tar: Cannot utime: Operation not permitted` | Extracting on NTFS, harmless | Ignore (warnings, not errors) |
| `[Errno 1] Operation not permitted` in pip install | pip install from NTFS | Move source to /tmp, re-install |
| `CheckpointManager.__init__() got unexpected keyword` | Config mismatch / missing `tools/checkpoint_manager.py` | Re-extract tools/ from tarball |
| `Failed to initialize agent` after pip install | Incomplete extraction | Verify all directories exist |
| Proxy `HTTP 200` but download slow | Normal through proxy at 1.3MB/s is fine | Accept speed |
| `python -m hermes_cli.main --version` works but chat fails | Installed from NTFS dir | Reinstall from /tmp |

---

## Cloud Server (Alibaba Cloud ECS) Upgrade

When the Gateway runs on a remote cloud server (e.g., Alibaba Cloud ECS), the upgrade approach changes in key ways.

### Pre-Flight SSH Access

```bash
# Install sshpass for password-automated SSH
sudo apt-get install -y sshpass

# Test connection
sshpass -p 'your_password' ssh -o StrictHostKeyChecking=accept-new root@<PUBLIC_IP> "hostname"

# If successful, all subsequent commands can be:
sshpass -p 'your_password' ssh root@<PUBLIC_IP> "<command>"
```

### ⚠️ Critical: fail2ban

**Cloud servers almost always have fail2ban running.** Each failed SSH attempt increments the ban counter. After 3-5 failures, your IP gets blocked for minutes/hours.

```bash
# Symptom: first attempt → "Permission denied"  (wrong password or user)
# Subsequent attempts → "Connection refused"    (IP is BANNED)
```

**How to recover:**
1. Have the server owner SSH in directly and run:
   ```bash
   fail2ban-client set sshd unbanip <YOUR_PUBLIC_IP>
   ```
2. Or wait for the ban to expire (typically 10-30 minutes)
3. Or switch to SSH key authentication (recommended for automation)

**To avoid the ban loop:**
- Verify password AND username BEFORE running automated loops
- Default Ubuntu username on Alibaba Cloud is `root`
- One wrong attempt is OK; 5+ consecutive = ban
- Start with `sshpass -p 'password' ssh -o ConnectTimeout=5 root@IP "echo ok"` — single attempt, no loop

### Gateway-Specific Steps

Cloud Gateway upgrades have a **service interruption** — users connected to the bot will drop.

**Before upgrade:**
```bash
# 1. Check current gateway process
sshpass -p 'password' ssh root@<IP> "ps aux | grep -i 'hermes\\|gateway'"

# 2. Check how it's deployed
sshpass -p 'password' ssh root@<IP> "systemctl status hermes-gateway" 2>/dev/null || \
sshpass -p 'password' ssh root@<IP> "docker ps | grep hermes" 2>/dev/null || \
sshpass -p 'password' ssh root@<IP> "screen -ls" 2>/dev/null

# 3. Plan downtime window
echo "Notify users? Run during low-traffic hours?"
```

**Upgrade (same steps as local, but over SSH):**
```bash
# Download via ECS's own network (often faster than WSL!)
sshpass -p 'password' ssh root@<IP> "curl -L -o /tmp/hermes-source.tar.gz \\
  https://github.com/NousResearch/hermes-agent/archive/refs/tags/v2026.5.16.tar.gz"

# Or use proxy if ECS has restricted access
sshpass -p 'password' ssh root@<IP> "curl -L --proxy http://<proxy>:<port> -o /tmp/hermes-source.tar.gz ..."
```

**After upgrade:**
```bash
# Stop old gateway
sshpass -p 'password' ssh root@<IP> "systemctl stop hermes-gateway"

# Start new gateway (verify first!)
sshpass -p 'password' ssh root@<IP> "cd /path/to/new-version && source ~/.venv-hermes-311/bin/activate && hermes gateway"

# Monitor logs
sshpass -p 'password' ssh root@<IP> "journalctl -u hermes-gateway -f"
```

### Key Differences: Local vs Cloud

| Aspect | Local (WSL) | Cloud (ECS) |
|--------|-------------|-------------|
| Network | Proxy needed (Clash 7890) | Direct or faster proxy |
| Download speed | 1.3MB/s (proxy) | Usually 5-50MB/s |
| Service impact | Just you | Users get disconnected |
| Access | Direct terminal | SSH (fail2ban risk) |
| Restart | Simple script | systemd/docker/screen |
| Python install | `sudo apt install python3.11` | Same (Ubuntu) |
| /tmp persistence | Reboot = lost | Same (but ECS rarely reboots) |

---

## Environment Details

- WSL2 + Ubuntu 22.04 on Windows 11
- Network: China-based, github.com reachable but slow (~20-30KB/s)
- Git protocol: Blocked (DNS/port); SSH: no keys
- Current venv: `~/.venv-hermes` (Python 3.10)
- New venv: `~/.venv-hermes-311` (Python 3.11)
- Proxy: Clash/Mihomo on Windows, port 7890, LAN access required
- Cloud ECS: Alibaba Cloud lightweight server, Ubuntu 22.04, fail2ban active, password auth
