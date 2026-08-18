# Performance Tuning Reference

## Compression System

Controls how Hermes auto-compresses conversation context to stay within token limits.

```yaml
compression:
  enabled: true           # on/off
  threshold: 0.50         # 0.0-1.0: token % that triggers compression
  target_ratio: 0.20      # 0.0-1.0: compress down to this fraction
```

**How it works:**
1. Agent tracks token usage against model's context window
2. When usage reaches threshold (default: 50%), compression fires
3. Auxiliary model summarizes older messages to target_ratio (default: 20%)
4. Compressed summary replaces old messages in context

**Tuning guide:**
| Setting | Effect | When to change |
|---------|--------|----------------|
| threshold: 0.30 | Compress earlier | Long-running tasks that hit context limits |
| threshold: 0.70 | Compress later | Short tasks that don't need compression |
| target_ratio: 0.10 | More aggressive | DeepSeek/Gemini (large context) |
| target_ratio: 0.35 | More conservative | Tasks needing lots of history |

**Detection:** If the agent suddenly loses track of early conversation, compression may be too aggressive. Lower target_ratio or raise threshold.

---

## Toolset Overhead

Each enabled toolset adds JSON schemas to the system prompt. Real-world token cost:

| Toolset | ~Token cost | When to disable |
|---------|-------------|-----------------|
| web | ~800 tokens | Internal/offline work |
| browser | ~600 tokens | No browser automation needed |
| delegation | ~400 tokens | Not doing multi-step tasks |
| vision | ~300 tokens | Text-only tasks |
| image_gen | ~300 tokens | No image generation |
| cronjob | ~200 tokens | No scheduled tasks |
| todo | ~150 tokens | Simple conversations |
| memory | ~200 tokens | Search-only tasks |

**Expected savings:** Disabling 4-5 unused toolsets can save 1500-2500 tokens per API call.

**Quick prune for coding sessions:**
```bash
hermes tools disable web browser image_gen vision delegation cronjob todo
```

**Quick prune for chat/research:**
```bash
hermes tools disable terminal code_execution cronjob delegation
```

---

## Streaming vs Non-Streaming

```yaml
display:
  streaming: false    # wait for complete response
  # vs
  streaming: true     # token-by-token
```

- false: Lower total tokens, but user waits in silence
- true: Higher perceived speed, slightly more network overhead

Best practice: streaming: true for interactive chat, false for batch/automation.

---

## Model Strategy

**Single model vs multi-tier:**
- Default: one model for everything
- With delegation: main agent uses strong model, sub-agents use cheap model

```yaml
# Delegation model override
delegation:
  model: deepseek/deepseek-chat
  provider: deepseek
  max_iterations: 30
```

**Per-task auxiliary models** (each auxiliary can use a different provider):

```yaml
auxiliary:
  vision:
    provider: auto
    model: ''
  compression:
    provider: auto
  session_search:
    provider: auto
  curator:
    provider: auto
    timeout: 600
```

**Tip:** If a fast model handles all auxiliary tasks, set them explicitly to avoid the auto fallback.

---

## Delegation Depth Control

```yaml
delegation:
  max_iterations: 50    # per sub-agent
```

Each delegation call spawns a sub-agent running its own loop. Too deep = parallel costs stack.

Symptom of too deep: parent agent sits idle waiting for nested delegation calls. Fix: lower max_iterations.

---

## Checkpoints

```yaml
checkpoints:
  enabled: false
  max_snapshots: 50
```

Checkpoints save filesystem state before destructive operations. Off by default. Each checkpoint is a copy, so enable only when editing code that needs rollback safety.
