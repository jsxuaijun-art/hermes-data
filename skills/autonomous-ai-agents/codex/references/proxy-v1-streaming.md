# Proxy v1: 426 Fallback + Streaming HTTP (Current)

## When to use this mode

- Codex v0.135.x–v0.138.x (HTTPS fallback present)
- Target: any Chat Completions API (DeepSeek, OpenRouter, etc.)
- This is the **stable, working mode**

## Architecture

```
Codex CLI                    Proxy                        DeepSeek
  │                           │                             │
  ├── WS GET /v1/responses ──→│                             │
  │←── HTTP 426 Upgrade ──────┤ (reject WS)                │
  │   Required                │                             │
  │                           │                             │
  ├── WS retry ×4 ───────────→│  (v0.135.x behavior)       │
  │←── 426 ×4 ───────────────┤                             │
  │                           │                             │
  ├── HTTPS POST /v1/responses→│                            │
  │   {model, input,          │                             │
  │    instructions, tools,   │                             │
  │    stream: true}          │                             │
  │                           │                             │
  │                           ├── POST /v1/chat/completions─→│
  │                           │   {model, messages:[        │
  │                           │    {role:system, content},  │
  │                           │    {role:user, content}],   │
  │                           │    stream: true}            │
  │                           │←── SSE chunks ─────────────┤
  │                           │   (delta content)          │
  │                           │                             │
  │←── Chunked HTTP stream ───┤                             │
  │   output_text.delta ×N    │                             │
  │   output_text.done        │                             │
  │   output_item.done        │                             │
  │   response.completed      │                             │
```

## Key translate() mappings

| Responses API field | Chat Completions API field | Implementation |
|---|---|---|
| `instructions` | `messages[0].role = "system"` | `msgs.append({'role': 'system', 'content': instructions})` |
| `input[]` (list) | `messages[N].role = "user"/"assistant"` | Reads `item.role`, `item.content` |
| `input[].content` (array) | Concatenated text | Flattens `[{type, text}]` → `''.join(c.text)` |
| `input[].role = "developer"` | `role = "system"` | Explicit `if role == 'developer': role = 'system'` |
| `tools` (array) | **Not forwarded** | Chat Completions API triggers 400 if format mismatches |
| `stream` (bool) | `stream: true` | Always true for streaming mode |

## Chunked HTTP response format

```json
HTTP/1.1 200 OK
Content-Type: application/json
Transfer-Encoding: chunked
Connection: close

3a
{"type":"response.output_text.delta","response_id":"r_123","item_id":"r_123_item_0","delta":"Hello"}
0


```

## Known issues

### response.completed.usage must include token counts

Codex v0.135.x parses response.completed strictly. An empty usage: {} causes:

failed to parse ResponseCompleted: missing field `input_tokens`

This triggers 5 reconnection attempts before giving up. Fix: estimate tokens from message lengths:

```python
in_tok = max(1, sum(len(m.get('content','')) for m in msgs) // 3)
out_tok = max(1, len(text) // 3)
'usage': {'input_tokens': in_tok, 'output_tokens': out_tok, 'total_tokens': in_tok + out_tok}
```

### handle() must read the full HTTP request itself

Don't pass data=b'' from the accept loop. Read inside the handler:

```python
def handle(s):
    buf = b''
    while b'\r\n\r\n' not in buf:
        c = s.recv(8192)
        if not c: return
        buf += c
```

1. role: developer -> 400 - Map to role: system in translate().
2. Content arrays -> 400 - Flatten content blocks.
3. DeepSeek high demand - Retry.
4. API key 401 - Check key validity.
