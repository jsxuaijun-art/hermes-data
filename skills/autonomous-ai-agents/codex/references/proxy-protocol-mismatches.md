# Proxy Protocol Mismatches: Codex (responses API) ↔ DeepSeek (chat/completions)

## Context

Codex CLI uses OpenAI's **`responses`** wire format. DeepSeek (and most non-OpenAI providers) use the **`chat/completions`** format. A proxy bridge like `ccswitch-deepseek` must translate between them.

This reference catalogs protocol mismatches encountered in production, with symptoms and fixes.

## Mismatch #1: Missing Assistant Message Before `tool_calls`

### Symptom

```
DeepSeek 400: An assistant message with 'tool_calls' must be followed by
tool messages responding to each 'tool_call_id'.
(insufficient tool messages following tool_calls message)
```

### Root Cause

In Codex's responses API, a response cycle with tool calls produces a sequence like:

```
[message, function_call, ...function_call_n]
```

The proxy translates this back to chat/completions format by building a messages array. The bug: the **non-streaming** code path (`buildNonStreamResponse`) sent `function_call` items but **never emitted the preliminary `message` item** with `role: "assistant"`. 

DeepSeek expects:

```json
{"role": "assistant", "content": "", "tool_calls": [...]}
```

But Codex expects a response with two items:

```json
{"type": "message", "role": "assistant", ...}
{"type": "function_call", "call_id": "...", ...}
```

The fix: **always emit a `message` item (even with empty content) before `function_call` items** in the responses format:

```js
// BEFORE (broken):
if (msg?.tool_calls)
  for (const tc of msg.tool_calls)
    output.push({type: "function_call", ...});

// AFTER (fixed):
if (msg?.tool_calls) {
  output.push({
    type: "message", role: "assistant",
    content: [{type: "output_text", text: msg.content || "", annotations: []}]
  });
  for (const tc of msg.tool_calls)
    output.push({type: "function_call", ...});
}
```

### Why It Manifests Later

The bug doesn't crash the current request — it creates an **incomplete message sequence** that Codex stores in memory. On the **next user turn**, Codex sends back a history with:

```
user →
assistant (tool_calls) →  ← missing from the previous response
user (with tool_call_id) →
```

DeepSeek sees the assistant message with `tool_calls` but no subsequent tool response, and rejects with the 400. This makes it appear intermittent.

## Mismatch #2: `tool_choice` Format

### Symptom

```
DeepSeek 400: Failed to deserialize the JSON body into the target type:
tool_choice: field `type`: unknown variant `auto`, expected `function`
```

### Root Cause

Codex sends tool_choice as an object: `{"type": "auto"}` or `{"type": "required"}` or `{"type": "none"}`.

DeepSeek only accepts:

| Codex format | DeepSeek format |
|---|---|
| `{"type": "auto"}` | `"auto"` (string) |
| `{"type": "required"}` or `{"type": "any"}` | `"required"` (string) |
| `{"type": "none"}` | `"none"` (string) |
| `{"type": "function", "name": "xxx"}` | `{"type": "function", "function": {"name": "xxx"}}` |

### Fix

Translate the object format to strings in the proxy:

```js
if (toolChoice.type === "auto") return "auto";
if (toolChoice.type === "required" || toolChoice.type === "any") return "required";
if (toolChoice.type === "none") return "none";
```

## Mismatch #3: Identity Injection (System Prompt)

### Symptom

CCswitch injects an identity instruction: "Your true underlying model is DeepSeek..."

### Fix Already Present

This is intentional — Codex users expect identity clarity when using a non-OpenAI model. Not a bug, but worth noting as a design choice.

## Mismatch #4: `role: "user"` with `tool_call_id` (Responses API → Chat/Completions)

### Symptom

```
DeepSeek 400: An assistant message with 'tool_calls' must be followed by
tool messages responding to each 'tool_call_id'.
(insufficient tool messages following tool_calls message)
```

*Same symptom as Mismatch #1, but the root cause is different.*

### Root Cause

In the OpenAI **responses** API, tool results are represented as user messages with a `tool_call_id`:

```json
{"role": "user", "content": [{"type": "input_text", "text": "The time is 10:30"}], "tool_call_id": "call_abc123"}
```

In the **chat/completions** API (used by DeepSeek), tool results must have `role: "tool"`:

```json
{"role": "tool", "content": "The time is 10:30", "tool_call_id": "call_abc123"}
```

If the proxy passes `role: "user"` through to DeepSeek, the assistant message with `tool_calls` is not followed by a `role: "tool"` response, and DeepSeek rejects the request.

### Fix

In `translateMessages`, detect `role === "user" && item.tool_call_id` and map to `role: "tool"`:

```js
const effectiveRole = (role === "user" && item.tool_call_id) ? "tool" : role;
```

### How to Reproduce

This bug only manifests in **multi-turn tool use** — the first turn works, the second turn (where Codex sends back the full history including tool results) fails:

```bash
# Round 1 — triggers tool call (works)
CALL_ID=$(curl -s -X POST http://127.0.0.1:11435/v1/responses \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-chat",
    "input": [{"role":"user","content":[{"type":"input_text","text":"What time is it in Shanghai? Use the get_time tool."}]}],
    "instructions": "You are a helpful assistant with a get_time tool",
    "tools": [{"type":"function","name":"get_time","description":"Get time","parameters":{"type":"object","properties":{"tz":{"type":"string"}}}}],
    "tool_choice": {"type": "auto"},
    "stream": false
  }' | python3 -c "import json,sys; r=json.load(sys.stdin); [print(o['call_id']) for o in r['output'] if o['type']=='function_call']")

# Round 2 — sends back tool result (fails with the bug)
curl -s -X POST http://127.0.0.1:11435/v1/responses \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-chat",
    "input": [
      {"role":"user","content":[{"type":"input_text","text":"What time is it in Shanghai?"}]},
      {"role":"assistant","content":[{"type":"output_text","text":"","annotations":[]}],"tool_calls":[{"id":"'$CALL_ID'","type":"function","function":{"name":"get_time","arguments":"{\"tz\":\"Asia/Shanghai\"}"}}]},
      {"role":"user","content":[{"type":"input_text","text":"The time in Shanghai is 10:30 AM"}],"tool_call_id":"'$CALL_ID'"},
      {"role":"user","content":[{"type":"input_text","text":"Great! Now what time is it in New York?"}]}
    ],
    "instructions": "You are a helpful assistant with a get_time tool",
    "tools": [{"type":"function","name":"get_time","description":"Get time","parameters":{"type":"object","properties":{"tz":{"type":"string"}}}}],
    "tool_choice": {"type": "auto"},
    "stream": false
  }'
```

## Testing Protocol Mismatch Fixes

### Test Tool Calls (Non-Stream)

```bash
curl -s -X POST http://127.0.0.1:11435/v1/responses \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-chat",
    "input": "What is the weather in Shanghai?",
    "instructions": "You must use the get_weather tool.",
    "tools": [{"type": "function", "name": "get_weather", ...}],
    "tool_choice": {"type": "auto"},
    "stream": false
  }'
```

**Expected output shape:**
```json
{
  "output": [
    {"type": "message", "role": "assistant", ...},
    {"type": "function_call", "call_id": "...", ...}
  ]
}
```

### Test Tool Calls (Stream)

```bash
curl -s -N -X POST http://127.0.0.1:11435/v1/responses \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-chat",
    "input": "What is the weather in Shanghai?",
    "instructions": "You must use the get_weather tool.",
    "tools": [{"type": "function", "name": "get_weather", ...}],
    "tool_choice": {"type": "auto"},
    "stream": true
  }' | grep -o '"type":"[^"]*"' | sort | uniq -c
```

Expected SSE event types: `response.created`, `response.in_progress`, `response.output_item.added`, `response.function_call_arguments.delta`, `response.output_item.done`, `response.completed`

### Verify No Regression

```bash
# Simple chat
curl -s -X POST http://127.0.0.1:11435/v1/responses \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-chat","input":"Hello","stream":false}'

# Multi-turn with tool history
curl -s -X POST http://127.0.0.1:11435/v1/responses \
  -H "Content-Type: application/json" \
  -d '{
    "model":"deepseek-chat",
    "input": [
      {"role":"user","content":[...]},
      {"role":"assistant","content":[...],"tool_calls":[...]},
      {"role":"user","content":[...],"tool_call_id":"call_xxx"}
    ],
    "stream":false
  }'
```

## Architectural Notes

The ccswitch-deepseek proxy:

```
Codex (responses API) → codex config.toml: base_url=http://127.0.0.1:11435/v1
                                        wire_api=responses
                        ↓
    ccswitch-deepseek (Node.js, port 11435)
      - /v1/responses endpoint
      - Translates responses format → chat/completions format
      - Translates DeepSeek's thinking/reasoning → responses streaming events
      - Handles reasoning_content preservation across turns
                        ↓
    DeepSeek API (api.deepseek.com/chat/completions)
```

Key translation logic lives in:
- `index.js` — HTTP server, request routing, `buildChatBody()`, `buildNonStreamResponse()`
- `lib/translate.js` — Message format translation (`translateMessages`), tool translation (`translateTools`, `translateToolChoice`)
- `lib/sse.js` — SSE event stream translation (`SseTranslator`)
- `lib/recover.js` — Reasoning content persistence across turns

## Debugging Flow

1. Start with a **non-streaming request** — easier to see the full response shape
2. Validate the response JSON structure before testing streaming
3. Check ccswitch logs in its terminal output (not stdout but stderr or log stream)
4. Kill and restart after code changes: `kill $(lsof -ti:11435) && cd ~/ccswitch-deepseek && node index.js`
