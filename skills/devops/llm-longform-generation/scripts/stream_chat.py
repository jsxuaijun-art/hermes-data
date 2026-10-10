#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Provider-agnostic streaming chat caller for LONG-FORM LLM output.

Why streaming: a gateway often caps the response time of a NON-streaming call,
so a long generation (several hundred+ chars) gets cut off mid-flight. With
stream=true the first bytes come back immediately and the connection stays
alive, so long drafts complete reliably.

Usage:
    python3 stream_chat.py --base-url https://aigw.telecomjs.com/v1 \
        --model Doubao-Seed-2.1-Pro --key-env TELECOM_DOUBAO_KEY \
        --brief /tmp/brief.txt --out /tmp/draft.txt \
        [--system /tmp/system.txt] [--temperature 0.8] [--timeout 300]

Secrets: pass the ENV VAR NAME via --key-env; the value is read from the
environment, falling back to ~/.hermes/.env. Never inline a key in a script
or commit it — those artifacts get synced to remote repos.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


def load_env_file():
    """Load ~/.hermes/.env without overwriting real env vars."""
    envf = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")) / ".env"
    if not envf.exists():
        return
    for line in envf.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def stream_chat(base_url, model, api_key, messages, temperature, timeout):
    """Yield content deltas from an OpenAI-compatible streaming endpoint."""
    url = base_url.rstrip("/") + "/chat/completions"
    body = json.dumps({
        "model": model,
        "messages": messages,
        "stream": True,                       # the fix: stream to survive long generations
        "temperature": temperature,
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        for raw in resp:
            line = raw.decode("utf-8", "ignore").strip()
            if not line.startswith("data:"):
                continue          # blank lines / SSE comments / heartbeats
            data = line[5:].strip()
            if data == "[DONE]":
                return
            try:
                delta = json.loads(data)["choices"][0].get("delta", {}).get("content") or ""
            except (json.JSONDecodeError, KeyError, IndexError, TypeError):
                continue          # tolerate malformed keep-alive frames
            if delta:
                yield delta


def main():
    p = argparse.ArgumentParser(description="Streaming caller for long-form LLM output.")
    p.add_argument("--base-url", required=True)
    p.add_argument("--model", required=True)
    p.add_argument("--key-env", required=True, help="ENV VAR NAME holding the API key")
    p.add_argument("--brief", required=True, help="file with the full user prompt")
    p.add_argument("--out", required=True, help="file to write the generated text to")
    p.add_argument("--system", help="optional file with the system prompt")
    p.add_argument("--temperature", type=float, default=0.8)
    p.add_argument("--timeout", type=int, default=300, help="read timeout (s); keep generous")
    a = p.parse_args()

    load_env_file()
    api_key = os.environ.get(a.key_env, "")
    if not api_key:
        print(f"ERROR: {a.key_env} not set (checked env and ~/.hermes/.env)", file=sys.stderr)
        return 1

    brief = Path(a.brief).read_text(encoding="utf-8")
    messages = []
    if a.system:
        messages.append({"role": "system", "content": Path(a.system).read_text(encoding="utf-8")})
    messages.append({"role": "user", "content": brief})

    print("=== streaming ===", file=sys.stderr, flush=True)
    chunks = []
    try:
        for delta in stream_chat(a.base_url, a.model, api_key, messages, a.temperature, a.timeout):
            chunks.append(delta)
            sys.stdout.write(delta)
            sys.stdout.flush()
    except urllib.error.HTTPError as e:
        print(f"\nERROR: HTTP {e.code} — {e.read().decode('utf-8', 'ignore')[:400]}", file=sys.stderr)
        return 1

    text = "".join(chunks)
    if not text.strip():
        print("\nERROR: empty response (check model name / channel availability)", file=sys.stderr)
        return 1
    Path(a.out).write_text(text, encoding="utf-8")
    print(f"\n\n=== saved: {a.out} ({len(text)} chars) ===", file=sys.stderr, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
