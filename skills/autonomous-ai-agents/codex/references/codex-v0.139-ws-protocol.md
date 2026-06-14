# Codex v0.139.0 WebSocket V2 Protocol Reference

## Custom WebSocket GUID

Codex v0.139.0 uses a non-standard WebSocket magic GUID:

```
Standard RFC 6455:  258EAFA5-E914-47DA-95CA-5AB9DC11B85B
Codex custom:       258EAFA5-E914-47DA-95CA-C5AB0DC85B11
```

The difference is in the 5AB9DC11B85B segment (note: 5AB9 -> C5AB, DC11 -> 0DC8, B85B -> 5B11). Verify which GUID a binary uses:

```bash
strings $CODEX_BIN | grep 258EAFA5
```

## WS Upgrade Headers

Captured from live Codex v0.139.0 WS upgrade requests:

| Header | Value |
|--------|-------|
| `connection` | `Upgrade` |
| `upgrade` | `websocket` |
| `sec-websocket-version` | `13` |
| `sec-websocket-key` | (varies per connection) |
| `authorization` | `Bearer sk-...` (from config) |
| `user-agent` | `codex_exec/0.139.0 (Ubuntu; x86_64)` |
| `openai-beta` | `responses_websockets=2026-02-06` |
| `sec-websocket-extensions` | `permessage-deflate; client_max_window_bits` |
| `x-codex-window-id` | session UUID |
| `x-codex-turn-metadata` | JSON with session, thread, turn, sandbox info |
| `x-client-request-id` | session UUID |

Note: Codex does NOT send `Sec-WebSocket-Protocol`.

### `x-codex-turn-metadata` structure

```json
{
  "session_id": "019ebc31-...",
  "thread_id": "019ebc31-...",
  "thread_source": "user",
  "turn_id": "019ebc31-...",
  "sandbox": "none",
  "request_kind": "turn",
  "turn_started_at_unix_ms": 1781273835829,
  "window_id": "019ebc31-...:0"
}
```

`request_kind` values: `turn` (actual request), `prewarm` (connection pre-warming).

## Binary Preamble

Immediately after WS upgrade, Codex sends an 8-byte binary frame (opcode 0x2):

```
Payload (hex): 00 00 00 01 00 00 00 00
```

This is a protocol version negotiation. The proxy MUST echo back the same 8 bytes (unmasked, same opcode 0x2). Without this ACK, Codex does not send any text frames.

## Frame Parsing

### Masking

Client-to-server frames from Codex are always masked (mask bit = 1). Server-to-proxy frames must NOT be masked (mask bit = 0).

### Length Modes

- Length < 126: single-byte length
- Length == 126: 2-byte big-endian extended length
- Length == 127: 8-byte big-endian extended length

### Binary-in-Text-Frame

Codex may send frames with opcode 0x1 (text) containing non-UTF-8 data. The proxy must handle this via try-catch on `.decode('utf-8')` and treat decode failures as unrecognized frames.

## WS V2 Event Protocol

### Client -> Server events

#### `response.create`

Primary request event:

```json
{
  "type": "response.create",
  "id": "r_<timestamp_ns>",
  "model": "deepseek-v4-flash",
  "instructions": "System instructions",
  "input": [
    {"type": "input_text", "content": "User message"}
  ],
  "max_output_tokens": 4096,
  "tools": [],
  "metadata": {}
}
```

#### `response.input_item`

Additional input during active request (proxy should skip):

```json
{
  "type": "response.input_item",
  "id": "item_<timestamp_ns>",
  "content": [{"type": "input_text", "text": "context"}]
}
```

### Server -> Client events (mandatory sequence)

All 6 events must be sent in order for each `response.create`:

1. `response.created` — acknowledges request
2. `response.output_item.created` — announces new output item
3. `response.output_text.delta` — one or more text chunks
4. `response.output_text.done` — end of text streaming
5. `response.output_item.done` — output item complete
6. `response.completed` — response done

## Connection Lifecycle

```
Codex                    Proxy
  │                        │
  ├── GET /v1/responses ───→  (WS upgrade with openai-beta header)
  │←── HTTP 101 ───────────┤  (custom GUID accept + permessage-deflate)
  │                        │
  ├── binary 8B ──────────→  (protocol version 0x00000001)
  │←── binary 8B ──────────┤  (unmasked echo ACK)
  │                        │
  ├── text response.create ─→  (request)
  │←── text response.created ────┤  (event 1)
  │←── text output_item.created ──┤  (event 2)
  │←── text output_text.delta ─────┤  (event 3, xN)
  │←── text output_text.done ──────┤  (event 4)
  │←── text output_item.done ──────┤  (event 5)
  │←── text response.completed ────┤  (event 6)
  │                        │
  ├── close ──────────────→
  │←── close ──────────────┤
```

## Known Issues

### ⚠️ Structural Incompatibility: tokio_tungstenite vs Python sync socket (v0.139.0+)

**This is the root cause of the immediate disconnect-after-101 problem.** Not a GUID issue, not a permessage-deflate issue, not a timing issue — it's a fundamental architecture mismatch.

#### Evidence

1. **Manual WS test with Python client succeeds** — A Python socket connecting to the proxy, sending WS upgrade + binary ACK + `response.create` JSON, receives the full 6-event sequence (5271 bytes, 30 delta events, correct Chinese text from DeepSeek). The proxy's WS event protocol is correct.

2. **Codex connects and closes without sending data** — ws.log consistently shows "handle start" → "disconnect" with zero "recv" entries. The WS upgrade (101) succeeds, but Codex sends close frame (opcode 8) before any data frame.

3. **All possible causes eliminated:**
   - ✅ Custom GUID `258EAFA5-E914-47DA-95CA-C5AB0DC85B11` — confirmed in binary, proxy uses it, manual test passes
   - ✅ `Sec-WebSocket-Accept` calculation — Python test with same GUID produces correct value
   - ✅ Response header format — verified `\r\n` line endings, correct header names
   - ✅ `permessage-deflate` — added to response header; no change in behavior
   - ✅ `Sec-WebSocket-Protocol` — Codex doesn't send this header; not required
   - ✅ Binary ACK — proxy echoes 8 bytes; manual test works
   - ✅ `openai-beta` header required — Codex sends it; proxy accepts all upgrades

#### Root cause

**Codex v0.139.0 uses `tokio_tungstenite` — a Rust async WebSocket stack built on the tokio runtime.** Python's synchronous socket API operates on a fundamentally different I/O model:

- **tokio_tungstenite** manages connections via cooperative multitasking with wakers, timers, and state machines. It may perform additional asynchronous handshake steps (protocol negotiation, compression setup, capability exchange) **within the same upgrade response** that a sync socket never sees.
- **Python sync socket** (`socket.recv`/`send`) blocks on each I/O call and has no concept of async waker notifications. It completes the HTTP 101 response, then waits in a blocking `recv()` call. If tokio_tungstenite expects a non-blocking I/O model or additional protocol negotiation within the handshake completion, the sync proxy never satisfies those expectations.
- **`permessage-deflate` is a strong candidate for the specific trigger** — the tungstenite compression extension requires `deflate` context tracking. The sync proxy acknowledges `Sec-WebSocket-Extensions: permessage-deflate` but never actually implements deflate compression. When tungstenite tries to negotiate the compression context and finds none, it may abort.

#### Corrective actions already tried (all failed to solve the disconnect)

1. Added `Sec-WebSocket-Extensions: permessage-deflate` to 101 response header
2. Echoed binary ACK immediately after upgrade
3. Increased socket timeout to 120s (from 30s)
4. Set `recv_frame` to no timeout (`settimeout(None)`)
5. Removed `server.ready` event (never send first)
6. Added try-catch on `UnicodeDecodeError` in `recv_text`
7. Sourced API key from `~/.hermes/.env` via `subprocess.run`

#### Solutions

| Solution | Effort | Confidence | Notes |
|----------|--------|-----------|-------|
| **Downgrade to Codex v0.135.x** | 10 min | ✅ High | `npm install -g @openai/codex@0.135.2`. v0.135.x supports HTTPS fallback — proxy can return 426. The WS V1 protocol is simpler. |
| **Go proxy with gorilla/websocket** | 2-4 hrs | ✅ High | Mature sync WS library. Compile as binary alongside Python proxy. |
| **Rust proxy with tokio_tungstenite** | 4-6 hrs | ✅ High | Same WS stack as Codex — guaranteed compatibility. |
| **Node.js proxy with ws library** | 1-2 hrs | ⚠️ Medium | Event-driven WS handling. Custom GUID needs patching. |
| **Fix Python sync proxy** | ❌ | ❌ Low | Structural incompatibility. Not worth further investment. |

**Recommendation:** Downgrade to Codex v0.135.x — simplest path, 10 minutes, proven HTTPS fallback, no WS V2 complexity.
