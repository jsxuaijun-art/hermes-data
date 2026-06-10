# DeepSeek Vision in Hermes Agent — Research Report

## 1. Architecture Overview

Hermes Agent uses a **two-path** image handling system:

### Path A: Native Vision (for vision-capable main models)
- Images are attached as base64 `image_url` content parts directly in the user message
- Used when `supports_vision=True` in model capability metadata
- Works automatically for: Claude, GPT-4o, Gemini, Qwen-VL, etc.
- DeepSeek models **never** take this path (`supports_vision=False`)

### Path B: Text Fallback (for non-vision models like DeepSeek)
- `decide_image_input_mode()` returns `"text"` for DeepSeek
- Runner calls `_enrich_message_with_vision()` which invokes `vision_analyze_tool()`
- `vision_analyze_tool` calls `async_call_llm(task="vision")` → `resolve_vision_provider_client()`
- The auxiliary vision model analyzes the image and returns a text description
- The main model (DeepSeek) only sees the text description — never the raw pixels

### Vision Provider Resolution Chain (in order attempted)

```
resolve_vision_provider_client("vision")
  │
  ├── 1. Main model provider (if it supports vision) → SKIPPED for DeepSeek
  ├── 2. OpenRouter (if OPENROUTER_API_KEY is set)
  │     └── Default model: google/gemini-3-flash-preview (or as configured)
  ├── 3. Nous Portal (if authenticated)
  │     └── Default model: anthropic/claude-sonnet-4-20250514
  ├── 4. Anthropic native (if ANTHROPIC_API_KEY is set)
  │     └── Default model: claude-haiku-4-5-20251001
  ├── 5. Custom endpoint (if auxiliary.vision.base_url + api_key configured)
  │     └── Default model: gpt-4o-mini (or as configured)
  ├── 6. Codex OAuth (if authenticated)
  └── 7. ❌ FAILS — no vision available
```

---

## 2. Root Causes of "Vision识别不准" with DeepSeek

### Symptom A: No vision at all (vision_analyze tool fails)
- **Cause 1:** NO auxiliary vision provider configured  
  No `OPENROUTER_API_KEY`, no `ANTHROPIC_API_KEY`, no Nous auth, no `auxiliary.vision.base_url`
- **Cause 2:** OpenRouter credits exhausted (HTTP 402)
- **Cause 3:** Download timeout expired (default 30s) for large/slow images
- **Cause 4:** Model mismatch — `auxiliary.vision.model` set to a non-vision model

### Symptom B: Vision runs but gives bad descriptions
- **Cause 1:** Default vision model (gemini-3-flash-preview or claude-haiku) lacks detail for complex images
- **Cause 2:** Temperature too low (default 0.1) — produces bland descriptions
- **Cause 3:** Image too large → auto-resized → detail lost
- **Cause 4:** The `user_prompt` from `_enrich_message_with_vision` is generic ("Describe everything visible…") — no domain-specific prompting

### Symptom C: Vision results are inconsistent/rejected
- **Cause 1:** OpenRouter's model routing may use different underlying models
- **Cause 2:** Anthropic's native API may reject images >5MB
- **Cause 3:** API timeouts on slow vision models (default 120s)

---

## 3. Current Config Options (from DEFAULT_CONFIG)

```yaml
auxiliary:
  vision:
    provider: "auto"       # auto | openrouter | nous | codex | custom
    model: ""              # Override vision model (e.g. "google/gemini-2.5-flash")
    base_url: ""           # OpenAI-compatible base URL (takes precedence)
    api_key: ""            # API key for base_url (falls back to OPENAI_API_KEY)
    timeout: 120           # LLM API call timeout (seconds)
    extra_body: {}         # Provider-specific request fields
    download_timeout: 30   # Image HTTP download timeout (seconds)

agent:
  image_input_mode: "auto" # auto | native | text
```

Env var override: `AUXILIARY_VISION_MODEL` — overrides the vision model at runtime.

---

## 4. Recommended Fix & Optimization

### Step 1: Configure a Dedicated Vision Backend

**Option A: OpenRouter (easiest, works with any API key)**

```yaml
auxiliary:
  vision:
    provider: openrouter
    model: "google/gemini-2.5-flash-preview-04-17"   # Best quality:price ratio
    # OR: "anthropic/claude-sonnet-4-20250514"
    # OR: "openai/gpt-4o-mini"  (cheapest, decent)
```

Requires `OPENROUTER_API_KEY` env var to be set.

**Option B: Custom endpoint (for Chinese providers — Moonshot/Kimi, Zhipu GLM-4V, MiniMax, etc.)**

```yaml
auxiliary:
  vision:
    provider: custom
    model: "glm-4v-plus"          # or kimi-vision, etc.
    base_url: "https://open.bigmodel.cn/api/paas/v4"
    api_key: "your-zhipu-api-key"
```

**Option C: Anthropic native (best quality)**

```yaml
auxiliary:
  vision:
    provider: auto
    model: "claude-sonnet-4-20250514"
```
Requires `ANTHROPIC_API_KEY` env var.

### Step 2: Optimize Vision Parameters

```yaml
auxiliary:
  vision:
    timeout: 300               # Increase for complex/slow models
    download_timeout: 60       # Give more time for large images
    extra_body:
      temperature: 0.3         # Slightly higher for richer descriptions
      max_tokens: 4096         # Longer descriptions for complex images
```

### Step 3: Configure Image Input Mode

```yaml
agent:
  image_input_mode: "text"     # Force text mode for DeepSeek (default auto does this)
```

---

## 5. Third-Party Solutions (No Network Access Available — Based on Code Analysis)

Based on reading the Hermes Agent codebase, the following enhancement strategies are supported natively without external plugins:

### 5.1 Custom Vision Backend via OpenAI-Compatible Proxy
The `auxiliary.vision.provider: custom` path supports any OpenAI-compatible API. This means you can proxy vision through:
- **GLM-4V** (智谱): `base_url="https://open.bigmodel.cn/api/paas/v4"`
- **Moonshot/Kimi Vision**: `base_url="https://api.moonshot.cn/v1"`
- **MiniMax VL**: `base_url="https://api.minimax.chat/v1"`
- **Step-2 16K** (阶跃星辰): `base_url="https://api.stepfun.com/v1"`
- **Qwen-VL-Max** (阿里云): `base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"`
- **Hunyuan-Vision** (腾讯): `base_url="https://api.hunyuan.cloud.tencent.com/v1"`
- **Local LLaVA/Ollama**: `base_url="http://localhost:11434/v1"` with `model="llava"`

### 5.2 MCP Servers for Vision Enhancement
The codebase has `browser_vision` tool already — hints at MCP integration for screenshot analysis. If MCP servers are configured:
- `@anthropic/mcp-server-vision` — dedicated vision MCP server
- Filesystem-based MCP tools that call ImageMagick/GIMP scripts for OCR pre-processing

### 5.3 OCR Pre-processing (Most Practical Enhancement)
The biggest weakness of the current approach is that text in images is poorly captured. Solutions:
1. **Tesseract OCR** — add a pre-processing step before vision_analyze
2. **PaddleOCR** (百度) — best for Chinese text in images
3. **EasyOCR** — multi-language support

These can be integrated as a custom tool or within the vision tool pipeline.

---

## 6. Best Practice Recommendations

### Immediate Fixes (zero code changes)

1. **Set a strong auxiliary vision model:**
   ```bash
   export AUXILIARY_VISION_MODEL="google/gemini-2.5-flash-preview-04-17"
   ```
   or in config.yaml:
   ```yaml
   auxiliary:
     vision:
       model: "google/gemini-2.5-flash-preview-04-17"
   ```

2. **Ensure OpenRouter API key is set:**
   ```bash
   export OPENROUTER_API_KEY="sk-or-v1-..."
   ```
   This is the easiest path — OpenRouter handles billing and model routing automatically.

3. **Increase timeouts for complex images:**
   ```yaml
   auxiliary:
     vision:
       timeout: 300
       download_timeout: 120
   ```

4. **Always check vision is working:**
   ```bash
   # Test vision resolution
   python3 -c "
   import asyncio
   from tools.vision_tools import check_vision_requirements, vision_analyze_tool
   print('Vision available:', check_vision_requirements())
   "
   ```

### Medium-Term Improvements

5. **Add explicit `image_input_mode: text` in config** — ensures DeepSeek always uses the text fallback chain regardless of other settings.

6. **For Chinese text accuracy**, configure a Chinese vision model that handles CJK well:
   ```yaml
   auxiliary:
     vision:
       model: "qwen/qwen2.5-vl-72b-instruct"
       # OR: "stepfun/step-2-16k-vision" 
       # OR: "zhipu/glm-4v-plus"
   ```

### Long-Term Architecture Improvements

7. **Add an OCR pre-processing step** — create a `pipeline.py` that runs Tesseract/PaddleOCR on images BEFORE sending to the vision model. This dramatically improves text extraction accuracy.

8. **Use a local OCR-first approach**: Run PaddleOCR locally (works offline, fast), extract text, THEN use vision_analyze for visual context. This hybrid approach beats any single vision model for text-heavy images.

9. **Consider DeepSeek-VL (Janus)** as the main model switch if vision is critical — DeepSeek's own multimodal model (Janus/DeepSeek-VL2) does support images natively and could replace the DeepSeek-v4 + auxiliary vision combination entirely.

---

## 7. Debugging Commands

```bash
# Check what vision provider resolves
python3 -c "
import asyncio
from agent.auxiliary_client import resolve_vision_provider_client
provider, client, model = resolve_vision_provider_client()
print(f'Provider: {provider}')
print(f'Model: {model}')
print(f'Client ready: {client is not None}')
"

# Test vision directly
python3 -c "
import asyncio
from tools.vision_tools import vision_analyze_tool
result = asyncio.run(vision_analyze_tool(
    image_url='https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/300px-PNG_transparency_demonstration_1.png',
    user_prompt='Describe this image in detail'
))
print(result)
"

# Check current config
python3 -c "
from hermes_cli.config import load_config, cfg_get
cfg = load_config()
vision = cfg_get(cfg, 'auxiliary', 'vision', default={})
print('Vision config:', vision)
"
```
