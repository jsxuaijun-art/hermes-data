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

## Fallback: GitHub REST API (when clone/CDN fail)

### When to use
- `git clone` times out (network slowness, firewall restrictions)
- `raw.githubusercontent.com` is unreachable but `api.github.com` works
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

## Cross-Machine Hermes Data Sync

This skill now includes the cross-machine Hermes Agent sync workflow from the absorbed `hermes-agent-sync` skill (archived). See `references/hermes-data-sync.md` for:

- **Push**: WSL → GitHub private repo → other machine
- **Pull**: GitHub → WSL
- **SSH key setup**: WSL doesn't inherit Windows SSH keys — explicit copy needed
- **China network workarounds**: git proxy config, fetch+reset vs pull
- **.bat encoding pitfalls**: UTF-8 without BOM in WSL → cmd.exe parses as GBK
- **Recovery after reinstall**: GitHub has all core data

Also see `references/hermes-data-sync-extraction.md` for the specific technique of using the GitHub REST API to restore data when `git clone` and `raw.githubusercontent.com` are both unreachable.

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
