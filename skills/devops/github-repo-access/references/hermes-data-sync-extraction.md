# Session Reference: Extracting hermes-data Sync Repo

## Scenario
Extract data from `jsxuaijun-art/hermes-data` — a private repo used for cross-machine Hermes Agent data sync (SOUL.md, memories, skills, config).

## Constraints Encountered
- `git clone --depth 1` — timed out (>120s)
- `raw.githubusercontent.com` — unreachable (curl timeout after 10s)
- `api.github.com` — reachable and responsive (<5s)

## Working Technique
GitHub REST API for both tree browsing and file content extraction.

### Step 1: Recursive tree listing
```bash
curl -s "https://api.github.com/repos/jsxuaijun-art/hermes-data/git/trees/main?recursive=1"
```
Parsed with Python to get full file listing (type + path).

### Step 2: Bulk file download (Python)
```python
import json, base64, urllib.request

files = ["README.md", "SOUL.md", "config.yaml", ...]
for f in files:
    url = f"https://api.github.com/repos/jsxuaijun-art/hermes-data/contents/{f}"
    with urllib.request.urlopen(url, timeout=15) as resp:
        data = json.loads(resp.read())
        content = base64.b64decode(data["content"]).decode("utf-8")
        print(f"FILE: {f}  ({data['size']} bytes)")
        print(content[:3000])
```

### Files Extracted (22 files total)
- README.md — cross-machine sync guide (bat scripts for push/pull)
- SOUL.md, SOUL_Pro.md — 财税营销获客 AI 身份 (强制输出机制: 短视频选题+文案+转化引导)
- SOUL_Edu.md — 初中生辅导 AI 身份
- config.yaml — Hermes Agent full config (DeepSeek provider, terminal, browser, etc.)
- claw-memory/MEMORY.md — long-term memory (公司信息、项目记录)
- claw-memory/2026-04-25.md — Hermes Agent v0.10.0 installation log
- claw-memory/2026-04-26.md — data sync setup log
- memories/MEMORY.md — 用户工作记忆 (财税行业、1039报告、Word排版技巧)
- memories/USER.md — 用户信息 (江敏/江姐, 盈信, 高级会计师, 多设备)
- memories/workbuddy-office-setup.md — 办公室PC配置

## Connection Pattern
| Destination | Status | Notes |
|------------|--------|-------|
| api.github.com | ✅ Works | REST API, unauthenticated (60 req/hr limit) |
| raw.githubusercontent.com | ❌ Timeout | Content CDN blocked/delayed |
| github.com (git clone) | ❌ Timeout | HTTPS git protocol slow |

Notable: API calls work but the content CDN and git protocol both fail — suggests DNS/route for `raw.githubusercontent.com` and git traffic is restricted but `api.github.com` is on a different route.
