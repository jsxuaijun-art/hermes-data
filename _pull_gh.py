"""Fast GitHub API pull - enumerate with API, download from raw"""
import json, urllib.request, sys, os
from pathlib import Path

HOME = Path.home()
SYNC_DIR = HOME / "hermes-sync"
OWNER = "jsxuaijun-art"
REPO = "hermes-data"
BRANCH = "main"
API = f"https://api.github.com/repos/{OWNER}/{REPO}/contents"
RAW = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/{BRANCH}"

# API timeout
API_TIMEOUT = 10

def get_json(url):
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github.v3+json")
    try:
        with urllib.request.urlopen(req, timeout=API_TIMEOUT) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"  API GET failed: {e}", flush=True)
        return None

# Enumerate files first
files_to_download = []

print("Enumerating root...", flush=True)
root = get_json(f"{API}?ref={BRANCH}")
if root:
    for item in root:
        if item["type"] == "file" and item["name"].endswith((".md", ".yaml", ".yml", ".json", ".txt", ".gitignore")):
            files_to_download.append(item["name"])

for dirname in ["memories", "skills", "claw-memory", "claw_memories"]:
    print(f"Enumerating {dirname}/...", flush=True)
    items = get_json(f"{API}/{dirname}?ref={BRANCH}")
    if items and isinstance(items, list):
        for item in items:
            if item["type"] == "file":
                files_to_download.append(f"{dirname}/{item['name']}")

print(f"Total files to download: {len(files_to_download)}", flush=True)

# Download each file with individual timeout
downloaded = 0
failed = 0
for rpath in files_to_download:
    url = f"{RAW}/{rpath}"
    local = SYNC_DIR / rpath
    try:
        local.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(url, timeout=15) as resp:
            content = resp.read().decode("utf-8")
        local.write_text(content, encoding="utf-8")
        print(f"  * {rpath}", flush=True)
        downloaded += 1
    except Exception as e:
        print(f"  FAIL {rpath}: {e}", flush=True)
        failed += 1

print(f"\nDone: {downloaded} downloaded, {failed} failed", flush=True)
