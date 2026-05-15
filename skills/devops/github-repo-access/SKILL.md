---
name: github-repo-access
category: devops
description: Access and extract data from GitHub repositories — browse tree, read files, download content — including fallback strategies when standard methods (git clone, raw.githubusercontent.com CDN) are unavailable due to network restrictions or timeouts.
triggers:
  - User asks to read/extract data from a GitHub repo
  - git clone fails or times out
  - raw.githubusercontent.com content is unreachable
  - Need to inspect repo contents without cloning
---

# GitHub Repo Access

## Standard Approach (works most of the time)

### Clone with depth limit
```bash
git clone --depth 1 <repo-url> <target-dir>
```
- `--depth 1` skips history, fastest clone
- Use `--single-branch` if only one branch needed

### Read a single file (raw CDN)
```bash
curl -s "https://raw.githubusercontent.com/<owner>/<repo>/<branch>/<path>"
```

## Fallback A: WSL — Windows git.exe via PowerShell (when WSL clone fails)

**Scope: WSL (Windows Subsystem for Linux) environments only.** When `git clone` times out from inside WSL but you have Windows git installed on the host.

### When to use
- `git clone` hangs / disconnects from WSL (common from China, restricted networks, WSL2 NAT routing issues)
- `powershell.exe` is available (always in WSL)
- Windows git.exe is installed (`C:\Program Files\Git\bin\git.exe`)
- `api.github.com` may also be unreachable from WSL (REST fallback doesn't help either)

### How it works

WSL can call Windows executables directly. Windows git.exe uses the **Windows network stack** (proxy, VPN, routing), which often works when WSL's Linux network stack fails. Since this is a direct clone (not REST API), you get the full repo tree, not just file-by-file.

### Steps

```bash
# 1. Clone via PowerShell → Windows git.exe
powershell.exe -Command "& 'C:\Program Files\Git\bin\git.exe' clone --depth 1 https://github.com/<owner>/<repo>.git C:\Users\<WindowsUser>\<target-dir>"

# 2. Copy from Windows path to WSL
cp -r /mnt/c/Users/<WindowsUser>/<target-dir> ~/<target-dir>

# 3. (Optional) Clean up Windows copy
powershell.exe -Command "Remove-Item -Recurse -Force 'C:\Users\<WindowsUser>\<target-dir>'"
```

### Real example (from session)

```bash
# Windows git through PowerShell — works when WSL git times out
powershell.exe -Command "& 'C:\Program Files\Git\bin\git.exe' clone --depth 1 https://github.com/garrytan/gstack.git C:\Users\Administrator\gstack"

# Wait for completion in WSL
# Then copy from Windows to WSL
cp -r /mnt/c/Users/Administrator/gstack ~/gstack
```

### Pitfalls
- **Timeout duration**: PowerShell defaults to infinite wait; use `Start-Process -NoNewWindow -Wait` if you need a timeout
- **Large repos**: `--depth 1` is essential — without it Windows git may also time out on full history
- **Copy timing**: Wait for clone to finish before copying (check exit code via `$LASTEXITCODE`)
- **Cleanup**: Always remove the Windows-side clone copy if not needed — it won't auto-delete
- **No auth passthrough**: If the repo requires auth, Windows git.exe will prompt for credentials in its own window; use `git clone https://TOKEN@github.com/...` style URLs for automation
- **WSL distro name**: Default is `Ubuntu-22.04` or `Ubuntu` — pass `-d <DistroName>` to `wsl` if running from Windows side
- **`&` in PowerShell**: The `&` (call operator) is required when the path to git.exe contains spaces; always wrap the path in quotes

### When NOT to use this

- Working on a native Linux machine (no WSL) → use REST API fallback below
- PowerShell or cmd.exe not available → use REST API fallback below
- The repo is tiny and you only need one file → `curl` on raw CDN or REST API are faster

---

## Fallback B: GitHub REST API (when clone/CDN fail)

### When to use
- `git clone` times out on a native Linux system (no Windows host to fall back to)
- `raw.githubusercontent.com` is unreachable but `api.github.com` works
- Both WSL git AND Windows git.exe fail
- You only need to browse/inspect files, not clone the full history

### 1. List the repo tree (recursive)
```bash
curl -s "https://api.github.com/repos/<owner>/<repo>/git/trees/<branch>?recursive=1" \
  | jq '.tree[] | "\(.type) \(.path)"' -r
```
Or with Python:
```python
import json, urllib.request
url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
data = json.loads(urllib.request.urlopen(url).read())
for item in data['tree']:
    print(f"{item['type']:4s} {item['path']}")
```

### 2. List top-level directory
```bash
curl -s "https://api.github.com/repos/<owner>/<repo>/contents/"
```

### 3. Read a specific file (base64-encoded)
```bash
curl -s "https://api.github.com/repos/<owner>/<repo>/contents/<path>" \
  | jq -r '.content' | base64 -d
```
With Python:
```python
import json, base64, urllib.request
url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
data = json.loads(urllib.request.urlopen(url).read())
content = base64.b64decode(data["content"]).decode("utf-8")
```

### 4. Bulk download multiple files (Python)
```python
import json, base64, urllib.request

files = ["README.md", "config.yaml", "path/to/file.md"]
for f in files:
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{f}"
    with urllib.request.urlopen(url, timeout=15) as resp:
        data = json.loads(resp.read())
        content = base64.b64decode(data["content"]).decode("utf-8")
        # content now has the file text
```

## API Notes
- **Rate limit**: Unauthenticated: 60 req/hr. Authenticated: 5,000 req/hr
- **Authentication**: Add header `Authorization: Bearer <token>` for higher limits
- **Large repos**: Recursive tree may be truncated if too large; paginate or use tree SHA
- **Binary files**: Contents API returns base64; for very large files use the blob API instead

## Safer Bulk Download Pattern (no pipe-to-interpreter)

Instead of `curl | python3` (triggers security scanners), use `execute_code` with `urllib.request`:

```python
# Inside execute_code block - no shell piping needed
import json, base64, urllib.request

files = ["README.md", "config.yaml", "path/to/file.md"]
for f in files:
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{f}"
    with urllib.request.urlopen(url, timeout=15) as resp:
        data = json.loads(resp.read())
        content = base64.b64decode(data["content"]).decode("utf-8")
        print(f"FILE: {f}  ({data['size']} bytes)")
        print(content[:3000])
```

This avoids shell pipelines entirely and works within the agent's native `execute_code` tool.

## Pitfalls
- `raw.githubusercontent.com` may be reachable when `api.github.com` is not, and vice versa — try both
- Base64 content from the API includes `\n` every 60 chars — `base64.b64decode()` in Python handles this automatically; `jq -r` strips it
- Recursive tree (`?recursive=1`) is limited to ~100,000 entries; beyond that, paginate by subtree SHA
- Git clone over `https://` with token in URL: `https://TOKEN@github.com/owner/repo.git` — avoid shell history leakage
