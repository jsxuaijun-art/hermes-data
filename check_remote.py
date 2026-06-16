#!/usr/bin/env python3
"""Check remote HEAD SHA"""
import json, urllib.request, sys

url = 'https://api.github.com/repos/jsxuaijun-art/hermes-data/git/ref/heads/main'
req = urllib.request.Request(url, headers={'Accept': 'application/vnd.github.v3+json'})
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        d = json.loads(resp.read())
        print(f"Remote HEAD SHA: {d['object']['sha']}")
except Exception as e:
    print(f"Error: {e}")
sys.exit(0)
