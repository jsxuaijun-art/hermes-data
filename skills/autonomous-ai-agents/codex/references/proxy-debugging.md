# Proxy Debugging: Codex v0.139.0 WS V2 Translation Proxy

## V1 Mode: 426 Fallback + Streaming HTTP

### `messages[1].role: unknown variant 'developer'` (400)

**Symptom:** Codex sends POST but DeepSeek returns 400 with:
```
messages[1].role: unknown variant `developer`, expected one of `system`, `user`, `assistant`, `tool`, `latest_reminder`
```

**Cause:** Codex v0.135.x sends some messages with `"role": "developer"` (Responses API role). DeepSeek's Chat Completions API doesn't recognize it.

**Fix:** In `translate()`, map developer → system:
```python
if role == 'developer':
    role = 'system'
```

### Content array in input (400)

**Symptom:** 400 no specific error (or generic parse failure).

**Cause:** Codex sends `input` as list of items, each with `content` that can be:
- A string (e.g. `"hi"`)
- An array of content objects (e.g. `[{"type": "input_text", "text": "..."}]`)

The translate function must handle both:
```python
if isinstance(content, list):
    text = ''.join(c.get('text', '') for c in content if isinstance(c, dict) and 'text' in c)
else:
    text = str(content) if content else ''
```

### Instructions as system message

**Cause:** Codex v0.135.x sends `instructions` as a separate top-level field (not part of `input`). The proxy must add it as a system message:
```python
if instructions:
    msgs.append({'role': 'system', 'content': instructions})
```

### Streaming response from DeepSeek

The proxy now sends `stream=True` to DeepSeek and converts SSE chunks to chunked HTTP events for Codex:

```python
# DeepSeek -> proxy: SSE streaming (data: {...} deltas)
# Proxy -> Codex: chunked HTTP (output_text.delta events)
```

Logging: POST done shows `{(addr)}: POST done {len(full_text)}b`

## Common Proxy Bugs Encountered During Development

### 1. `NameError: name 'time' is not defined`

**Symptom:** POST handler crashes with NameError when calling `time.time_ns()`.
**Cause:** `import time` was optimized out during refactoring (removed from the import block).
**Fix:** Always keep `import time` in the proxy's import list. It's used by `call_ds` for request ID generation.

### 2. `UnicodeDecodeError` in `recv_text`

**Symptom:** Proxy crashes when receiving a text frame (opcode 0x1) whose payload is not valid UTF-8.
**Cause:** Codex may send non-UTF-8 data in text frames (binary control data or protocol negotiation).
**Fix:** Wrap `.decode('utf-8')` in try-except and treat decode failures as unrecognized frames (skip/continue).

```python
# bad.json is not necessarily JSON decode error - could be UTF-8 decode error
try:
    text = p.decode('utf-8')
except UnicodeDecodeError:
    # Binary-in-text-frame: skip this frame
    continue
```

### 3. `ImportError` from subprocess env

**Symptom:** Proxy starts but errors with "DEEPSEEK_API_KEY missing" even though the key is set in `~/.hermes/.env`.
**Cause:** The proxy uses `subprocess.run('source ... && echo ...')` to read the env file. The `shell=True` flag must be used for `source` to work. Without it, the subprocess does not inherit the parent shell.
**Fix:** Use explicit `['bash', '-c', 'source ...']` rather than relying on `shell=True`.

### 4. Binary frame ACK missing

**Symptom:** Codex sends binary frame but gets no ACK -> connection hangs or closes.
**Cause:** The proxy's `recv_text` only handles opcode 0x1 (text) and 0x8 (close). Opcode 0x2 (binary) is not handled.
**Fix:** In the main recv loop, handle opcode 0x2 by echoing the same payload back and continuing.

```python
if op == 2:
    self.send_frame(2, p)  # echo back same binary payload
    continue
```

### 5. Socket timeout on DeepSeek API calls

**Symptom:** Proxy sends text events but Codex times out waiting for `response.completed`.
**Cause:** DeepSeek's streaming API can take >30s for long-context responses. The proxy's `recv` timeout was set to 30s.
**Fix:** Set socket timeout to 120s or None (infinite wait for WS reads).

## WS Event Format Pitfalls

### Missing events in the sequence

When building the 6-event WS V2 response sequence, the most common errors:

| Missing/Bad Event | Symptom |
|-------------------|---------|
| Missing `response.output_item.created` | Codex hangs waiting for item start |
| Missing `output_text.done` | Codex waits for stream end signal |
| Missing `output_item.done` | Codex waits for item completion |
| `input` field missing in `response.completed` | Codex may fail response assembly |
| Wrong `item_id` in `output_text.delta` | Events are ignored, no text shown |

### Event `item_id` naming convention

All items and sub-items must share a consistent ID hierarchy:

```
response_id:       "r_<timestamp_ns>"
item_id:           "r_<timestamp_ns>_item_0"
item_type:         "message"
content[].type:    "output_text"
```

If using multiple output items, increment the item index: `_item_0`, `_item_1`, etc.

## Logging

The proxy uses two log files:

- `/tmp/serve.log` — HTTP request/response logging, WS upgrade headers
- `/tmp/ws.log` — WS connection lifecycle: handle start, recv bytes, disconnect

Both are opened with `open(filename, 'a')` from the handler functions. When debugging, clear them with:

```bash
: > /tmp/ws.log; : > /tmp/serve.log
```

The `serve` function logs WS upgrade requests with full headers using `json.dumps(hdrs)`. The `handle` function logs each received text frame length.

## Step Table for Proxy Troubleshooting

| Step | Test | Expected | If fails |
|------|------|----------|----------|
| 1 | `ss -tlnp \| grep 9090` | LISTEN | Start proxy |
| 2 | `curl http://127.0.0.1:9090/v1/models` | JSON or 404 | Proxy not listening |
| 3 | Manual WS test (see SKILL.md) | 6 events received | Check GUID/handshake |
| 4 | `cat /tmp/ws.log` | "recv ...b" for Codex connection | WS handshake issue |
| 5 | `cat /tmp/serve.log` | "WS upgrade" with headers | Headers show Codex version |
