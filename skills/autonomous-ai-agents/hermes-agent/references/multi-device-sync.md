# Multi-Device Hermes Data Sync

Use a private GitHub repo to sync `~/.hermes/` data (SOUL.md, memories, skills, config.yaml) across multiple machines. This pattern works for any number of devices — home PC, office PC, laptops, etc.

## Architecture

```
Device A (在家)               Device B (办公室)           Device C (笔记本)
   │                              │                           │
   ├── push.bat ──────┐          ├── push.bat ──────┐        ├── push.bat ──────┐
   │                  ▼          │                  ▼        │                  ▼
   │             GitHub ◄────────┘             GitHub ◄──────┘             GitHub
   │                  │                         │                           │
   └───────► pull.bat │          └───────► pull.bat │        └───────► pull.bat │
                      │                         │                           │
                      ▼                         ▼                           ▼
                 Local data                Local data                   Local data
```

## Encoding Pitfall: .bat Files with Chinese Characters

**Critical:** If your `.bat` files contain Chinese characters, box-drawing symbols (`═`, `┌`, `└`, `│`, `─`), or Unicode symbols (`✓`, `⚠`, `✅`), cmd.exe will likely garble them.

**Why:** cmd.exe parses the file using the system's ANSI code page (GBK on Chinese Windows). UTF-8-encoded non-ASCII bytes get misinterpreted as GBK multi-byte sequences, producing mojibake (`晲鈺愨`) that can even "eat" ASCII characters from adjacent lines.

**What doesn't reliably fix it:**
- `chcp 65001` — runs too late; the file is already parsed by then
- UTF-8 BOM (`EF BB BF`) — some Windows versions still read the BOM as literal text (`锘緻echo`)

**Bulletproof fix: Pure ASCII only.** Use English text, `=` / `-` for separators, and `[OK]` / `[FAIL]` / `[INFO]` for status indicators. Or write the scripts in PowerShell instead — it handles UTF-8 natively.

The template scripts below are written in **pure ASCII** specifically for this reason. If you adapt them, do NOT add Chinese text, box art, or Unicode symbols.

## WSL Distro Name Pitfall

**Common mistake:** The WSL distribution name is rarely what you expect.

The default Ubuntu WSL distro can be named `Ubuntu`, `Ubuntu-22.04`, `Ubuntu22.04`, `Ubuntu-24.04`, or `Ubuntu24.04` — it depends on how it was installed (Microsoft Store vs `wsl --install` vs manual).

**Always check first:**

```batch
wsl -l -v
```

This shows the exact name (e.g., `Ubuntu22.04`). Copy-paste it into your `set WSL_DISTRO=...` line.

**Troubleshooting:** If `wsl -d MyDistro -- bash -c "..."` gives `WSL_E_DISTRO_NOT_FOUND`, the name is wrong. Run `wsl -l -v` to find the correct one.

## Proxy Pitfall: Windows Proxy Doesn't Reach WSL

**Background:** If you use a proxy tool on Windows (Clash, V2Ray, Shadowsocks, etc.), it runs on the Windows host. WSL2 has its own virtual network — `127.0.0.1` in WSL is **not** the same as `127.0.0.1` on Windows.

**Symptom:** WSL shows warning `检测到 localhost 代理配置，但未镜像到 WSL` and `git pull` inside WSL hangs or times out.

**Fix: Run git operations on the Windows side, not inside WSL.**

Do this:
```batch
:: GOOD — git runs on Windows (proxy works), only file copy uses WSL
cd /d "%SYNC_DIR%"
git pull origin main --rebase     ← Windows git, respects your proxy
wsl -d %WSL_DISTRO% -- bash -c "cp ..."  ← Only file operations in WSL
```

Not this:
```batch
:: BAD — git runs inside WSL, can't reach Windows proxy
wsl -d %WSL_DISTRO% -- bash -c "cd /mnt/... && git pull origin main"
```

**Alternative:** You can mirror the proxy to WSL by adding these to WSL's `~/.bashrc`:
```bash
# Find the Windows host's IP from inside WSL
host_ip=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')
export http_proxy="http://$host_ip:7890"
export https_proxy="http://$host_ip:7890"
```

**Caveat:** The nameserver IP from `/etc/resolv.conf` is not always the Windows host IP. In some WSL2 configurations, it shows a gateway address (`10.255.255.254`) that doesn't forward to the Windows host's proxy. The actual Windows host IP is the **default gateway**, found via `ip route | grep default` (e.g., `172.23.144.1`). If the resolv.conf approach doesn't work, try the default gateway instead.

But overall, running git on the Windows side is more reliable than trying to proxy through WSL.

---

## Key Rule: Pull Before Push (Always)

The single most important rule to avoid git conflicts:

```batch
:: WRONG — will fail if another device pushed first
git add -A
git commit -m "..."
git push origin main           ← REJECTED! Remote has new commits

:: CORRECT — pull (rebase) before commit
git pull origin main --rebase  ← Get latest, rebase local on top
git add -A
git commit -m "..."
git push origin main           ← Works
```

Without `git pull` first, pushing machine B after machine A will get:
```
! [rejected] main -> main (fetch first)
error: failed to push some refs
```

### Even Better: Use `fetch + reset` for Pull Scripts

For a **pull-only script** (you want your local copy to match GitHub exactly, discarding any local drift), use `git fetch` + `git reset --hard` instead of `git pull`. This **completely avoids merge conflicts**:

```batch
:: BETTER than git pull for sync — no merge, no conflicts
cd /d "%SYNC_DIR%"
git fetch origin main
git reset --hard origin/main    ← local = remote, discard any uncommitted changes
```

This is ideal for the pull script because:
- Never blocks on merge conflicts
- Works even if local files got modified by accident
- Single deterministic outcome: exact match to remote

The push script should still do a `fetch + reset` first (to get the latest remote state), then re-apply WSL data, then commit+push — this ensures you push on top of the absolute latest remote head. See the push template below for this pattern.

## General Web Access from WSL in China

Beyond git sync, Hermes Agent's `web` and `search` toolsets also fail from WSL when the Windows proxy isn't configured. This affects:

- **Bing for Chinese educational content**: Returns tourism/gaming results instead of educational resources (e.g. "星空" matches the Starfield game, not music scores). Site-specific searches (`site:wenku.baidu.com`) may return empty.
- **Baidu**: Blocks automated requests with captcha ("百度安全验证") — no programmatic access.
- **Google**: Unreachable from mainland China networks.
- **Sogou/360**: Same captcha restrictions.
- **Bilibili API**: Returns HTTP 412 (Precondition Failed) for many queries.
- **YouTube**: Unreachable from mainland China.
- **PowerShell from WSL**: Also blocked — `System.Net.WebClient.DownloadString` times out.

**What does work:**
- Microsoft Bing (cn.bing.com) for non-specific web searches of English/western content
- DuckDuckGo lite — may work but returns poor Chinese results
- Direct HTTP to some sites (Baidu static pages) — returns captcha
- Pinterest, Microsoft support, and similar non-Chinese western sites

**Workaround: Proxy the search from Windows directly.**
If the user needs to search Chinese educational resources (Wenku, Baidu, Jyeoo, Docin):
1. Provide specific search keywords they can paste into their Windows browser
2. Use `delegate_task` with `web`/`search` toolsets — the subagent **may** have different network access but in practice shares the same WSL network stack and will also fail
3. Best option: give the user exact keywords and let them search from their browser

**Typical search pattern for Chinese educational content:**
```
百度文库搜: "闵行区 七年级 数学 期末试卷 2024"
菁优网搜: "闵行 七下 数学 期末"
Direct URL: https://wenku.baidu.com/search?word=闵行区七年级数学期末
```

This template uses a **fetch+reset+reapply** pattern to avoid conflicts: reset to latest remote, then re-copy WSL data on top, commit, and push.

```batch
@echo off
chcp 65001 >nul
title Hermes Sync - Push

setlocal enabledelayedexpansion

set SYNC_DIR=C:\Users\USERNAME\hermes-sync
set DEVICE_NAME=office-pc
set NOW=%date:~0,10% %time:~0,5%

:: Point git to stored token
cd /d "%SYNC_DIR%"
git config credential.helper "store --file .git/credentials" 2>nul

:: [1] Copy from WSL (only file ops in WSL)
echo [1/4] Copying from WSL Hermes directory...
wsl -d %WSL_DISTRO% -- bash -c "
  cp -f /root/.hermes/SOUL.md /mnt/c/Users/USERNAME/hermes-sync/
  cp -f /root/.hermes/SOUL_Pro.md /mnt/c/Users/USERNAME/hermes-sync/
  cp -f /root/.hermes/SOUL_Edu.md /mnt/c/Users/USERNAME/hermes-sync/
  mkdir -p /mnt/c/Users/USERNAME/hermes-sync/memories
  cp -rf /root/.hermes/memories/* /mnt/c/Users/USERNAME/hermes-sync/memories/
  mkdir -p /mnt/c/Users/USERNAME/hermes-sync/skills
  cp -rf /root/.hermes/skills/* /mnt/c/Users/USERNAME/hermes-sync/skills/
  cp -f /root/.hermes/config.yaml /mnt/c/Users/USERNAME/hermes-sync/
"

:: [2] Fetch + reset to latest (Windows side — uses your proxy)
echo [2/4] Syncing to latest GitHub version...
cd /d "%SYNC_DIR%"
git fetch origin main
if errorlevel 1 (echo FETCH FAILED - check proxy/network & pause & exit /b)
git reset --hard origin/main

:: [3] Re-copy from WSL after reset (so our changes are on top of latest)
echo [3/4] Re-applying WSL data...
wsl -d %WSL_DISTRO% -- bash -c "
  cp -f /root/.hermes/SOUL.md /mnt/c/Users/USERNAME/hermes-sync/
  cp -f /root/.hermes/SOUL_Pro.md /mnt/c/Users/USERNAME/hermes-sync/
  cp -f /root/.hermes/SOUL_Edu.md /mnt/c/Users/USERNAME/hermes-sync/
  mkdir -p /mnt/c/Users/USERNAME/hermes-sync/memories
  cp -rf /root/.hermes/memories/* /mnt/c/Users/USERNAME/hermes-sync/memories/
  mkdir -p /mnt/c/Users/USERNAME/hermes-sync/skills
  cp -rf /root/.hermes/skills/* /mnt/c/Users/USERNAME/hermes-sync/skills/
  cp -f /root/.hermes/config.yaml /mnt/c/Users/USERNAME/hermes-sync/
"

:: [4] Commit and push
echo [4/4] Committing and pushing...
git add -A
git commit -m "sync %DEVICE_NAME% %NOW%"
if errorlevel 1 (echo [INFO] Nothing new to commit)
git push origin main
if errorlevel 1 (echo PUSH FAILED - check token & pause & exit /b)

echo Sync complete.
pause
```

## Script Template (pull.bat) — Pure ASCII Only!

This template uses `git fetch + git reset` to **avoid merge conflicts**. The local copy is forced to match GitHub exactly.

```batch
@echo off
chcp 65001 >nul
title Hermes Sync - Pull

setlocal enabledelayedexpansion

set SYNC_DIR=C:\Users\USERNAME\hermes-sync
set DEVICE_NAME=my-device
set NOW=%date:~0,10% %time:~0,5%

:: Point git to stored token
cd /d "%SYNC_DIR%"
git config credential.helper "store --file .git/credentials" 2>nul

:: [1] Fetch + reset to match GitHub exactly (no merge conflicts)
echo [1/2] Syncing from GitHub...
cd /d "%SYNC_DIR%"
git fetch origin main
if errorlevel 1 (echo FETCH FAILED - check proxy/network & pause & exit /b)
git reset --hard origin/main
echo   [OK] Local data matches GitHub

:: [2] Copy to WSL (only file ops in WSL)
echo [2/2] Copying to WSL Hermes directory...
wsl -d %WSL_DISTRO% -- bash -c "
  cp -f /mnt/c/Users/USERNAME/hermes-sync/SOUL.md /root/.hermes/
  cp -f /mnt/c/Users/USERNAME/hermes-sync/SOUL_Pro.md /root/.hermes/
  cp -f /mnt/c/Users/USERNAME/hermes-sync/SOUL_Edu.md /root/.hermes/
  mkdir -p /root/.hermes/memories
  cp -rf /mnt/c/Users/USERNAME/hermes-sync/memories/* /root/.hermes/memories/
  mkdir -p /root/.hermes/skills
  cp -rf /mnt/c/Users/USERNAME/hermes-sync/skills/* /root/.hermes/skills/
  cp -f /mnt/c/Users/USERNAME/hermes-sync/config.yaml /root/.hermes/
"

echo Pull complete.
pause
```

## Authentication

### Option A: GitHub Token (store in .git/credentials)

```batch
:: One-time setup
git config credential.helper "store --file .git/credentials"
echo https://USERNAME:TOKEN@github.com > .git\credentials
```

Token needs `repo` scope. Generate at: https://github.com/settings/tokens

### Pitfall: Git user.name/user.email not set

On a fresh Windows system, `git commit` may fail because `user.name` and `user.email` aren't configured:

```
*** Please tell me who you are.
Run
  git config --global user.email "you@example.com"
  git config --global user.name "Your Name"
```

Fix per-machine (one-time):
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

Or set per-repo (in the batch file):
```batch
git config user.name "Device Sync"
git config user.email "sync@local"
```

### Option B: SSH Key (per-machine)

Generate a key pair per device, add the public key to GitHub:

```bash
ssh-keygen -t ed25519 -C "your-email@example.com"
cat ~/.ssh/id_ed25519.pub  # Add this to GitHub → Settings → SSH keys
```

Then change remote to SSH:
```bash
git remote set-url origin git@github.com:USERNAME/hermes-data.git
```

## What to Sync vs What to Skip

| Sync | Don't Sync |
|------|------------|
| SOUL.md, SOUL_Pro.md, SOUL_Edu.md | sessions/ (session transcripts, ~/.hermes/sessions/) |
| memories/ (MEMORY.md, USER.md) | logs/ (gateway/error logs) |
| skills/ (all installed skills) | .env (contains API keys!) |
| config.yaml | .git/credentials (per-machine) |
| claw-memory/ (if present) | large media/cache files |

## Conflict Resolution

If `git pull --rebase` fails with conflicts:

1. Open the repo folder (e.g. `C:\Users\USERNAME\hermes-sync`)
2. Right-click → **Git Bash Here**
3. `git status` — shows which files conflict
4. `git mergetool` or manually edit + `git add` + `git rebase --continue`
5. Then `git push`

Three-way merge tools (recommended): VS Code, WinMerge, Meld.

## Per-Device Commit Messages

Tag each device's commits for traceability:

```bash
# Device-specific commit message
git commit -m "sync 台式机-家里 2026-05-01 22:30"
git commit -m "sync 笔记本 2026-05-02 09:15"
```

Quick tip: define the device name as a variable at the top of each push.bat so it's set once and reused.
