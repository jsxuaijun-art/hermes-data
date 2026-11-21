#!/usr/bin/env python3
"""Streaming caller for long-form kimi output (公众号出稿用).
Usage: stream_kimi.py <prompt_file> <out_file> [model]

Channel is RESOLVED from ~/.hermes/config.yaml providers, not hardcoded:
- finds the provider whose models name contains 'kimi' (e.g. telecom-kimi27),
  uses its key_env + first model name + base_url.
- expands ${VAR} key via os.environ / ~/.hermes/.env.
- kimi rejects temperature (400), and long drafts need stream=true + max_tokens,
  so this script sends NO temperature and max_tokens=24000.
"""
import os, sys, json, re, urllib.request, urllib.parse
from pathlib import Path


def load_env_file():
    envf = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")) / ".env"
    if envf.exists():
        for line in envf.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def read_config():
    cfgf = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")) / "config.yaml"
    if not cfgf.exists():
        return {}
    # minimal YAML subset parse: enough for the providers: block
    providers = {}
    cur = None
    for line in cfgf.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = line.strip()
        if re.match(r"^providers:\s*$", s):
            continue
        m = re.match(r"^  ([\w-]+):\s*$", s)
        if m:
            cur = m.group(1); providers[cur] = {}; continue
        if cur is None:
            continue
        m = re.match(r"^    (base_url|key_env):\s*(.+?)\s*$", s)
        if m:
            providers[cur][m.group(1)] = m.group(2).strip().strip('"').strip("'")
        m = re.match(r"^    models:\s*$", s)
        if m:
            providers[cur]["models"] = []
            continue
        m = re.match(r"^      ([\w.:-]+):\s*$", s)
        if m and "models" in providers[cur]:
            providers[cur]["models"].append(m.group(1))
    return providers


def resolve_channel():
    """Return (base_url, model, key_env) from config.yaml, else sane defaults."""
    providers = read_config()
    for name, cfg in providers.items():
        mods = cfg.get("models") or []
        if any("kimi" in m.lower() for m in mods) and cfg.get("key_env"):
            return (cfg.get("base_url", "https://aigw.telecomjs.com/v1"),
                    mods[0], cfg["key_env"])
    return ("https://aigw.telecomjs.com/v1", "kimi-k2.7-code", "KIMI27_API_KEY")


prompt_file, out_file = sys.argv[1], sys.argv[2]
base_url, model, key_env = resolve_channel()
if len(sys.argv) > 3:
    model = sys.argv[3]

load_env_file()
key = os.environ.get(key_env, "")
key = key.replace("${%s}" % key_env, os.environ.get(key_env, "")).replace("${", "").replace("}", "") if key.startswith("${") else key
if not key or key.startswith("${"):
    print(f"ERROR: config resolved key_env={key_env} but key is empty/unexpanded", file=sys.stderr)
    sys.exit(1)

prompt = open(prompt_file, encoding="utf-8").read()
payload = {
    "model": model,
    "stream": True,
    "max_tokens": 24000,   # kimi rejects temperature; max_tokens prevents cut-off
    "messages": [
        {"role": "system", "content": "你是一位深耕财税内容多年的资深公众号主笔，文风务实、有分寸、善用场景与对比，绝不编造政策与数据。"},
        {"role": "user", "content": prompt},
    ],
}
req = urllib.request.Request(
    base_url.rstrip("/") + "/chat/completions",
    data=json.dumps(payload).encode(),
    headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
)
buf = []
try:
    with urllib.request.urlopen(req, timeout=600) as r:
        for raw in r:
            line = raw.decode("utf-8", "ignore").strip()
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if data == "[DONE]":
                break
            try:
                obj = json.loads(data)
                delta = obj["choices"][0]["delta"].get("content") or ""
            except Exception:
                continue
            if delta:
                buf.append(delta)
                sys.stderr.write(delta)
                sys.stderr.flush()
except Exception as e:
    print(f"\nERROR: {e}", file=sys.stderr)
    sys.exit(1)
text = "".join(buf)
if not text.strip():
    print("\nERROR: empty response (channel/model may be rotated; check config.yaml providers)", file=sys.stderr)
    sys.exit(1)
open(out_file, "w", encoding="utf-8").write(text)
print(f"\n[OK] {len(text)} chars -> {out_file} (model={model})")
