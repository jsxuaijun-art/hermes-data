import urllib.request
import json
import sys

req = urllib.request.Request('https://api.github.com/repos/jsxuaijun-art/hermes-data/contents?ref=main')
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        print('Status:', r.status)
        data = json.loads(r.read())
        for item in data[:5]:
            print(f"  {item['name']} ({item['type']})")
        print(f"Total items: {len(data)}")
except Exception as e:
    print('Error:', type(e).__name__, str(e)[:200])
