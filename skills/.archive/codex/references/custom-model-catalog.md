# Custom Model Catalog for Codex CLI (DeepSeek Chat)

## Context

Session 2026.06.06 — Set up Codex CLI v0.134.0 with DeepSeek Chat via ccswitch proxy (`127.0.0.1:11435/v1`). Codex complained:

```
Model metadata for `deepseek-chat` not found. Defaulting to fallback metadata; this can degrade performance and cause issues.
```

## Root Cause

Codex maintains a built-in model catalog (`codex debug models`) listing known models (GPT-5.5, GPT-5.4, etc.) with their context_window, truncation_policy, tool support flags, etc. `deepseek-chat` is not in that list. Without a custom catalog entry, Codex uses a conservative fallback, potentially limiting context window and disabling features.

## Solution

1. Created `~/.codex/model_catalog.json` with a minimal but complete model entry
2. Added `model_catalog_json = "/home/dmin/.codex/model_catalog.json"` to `~/.codex/config.toml`

## Schema Requirements (Codex v0.134.0)

Based on `strings` analysis of the binary and trial-and-error debugging:

**Required fields** (all top-level, no optional skips):
- `slug`, `display_name`, `description`, `shell_type`, `visibility`
- `supported_in_api` (bool), `priority` (int)
- `default_reasoning_level` (string: "low"/"medium"/"high")
- `supported_reasoning_levels` (array of `{effort, description}`)
- `additional_speed_tiers` (array), `service_tiers` (array)
- `base_instructions` (string — **cannot be null**, use `""`)
- `supports_reasoning_summaries` (bool), `default_reasoning_summary` (string)
- `support_verbosity` (bool), `default_verbosity` (string: "low")
- `apply_patch_tool_type` (string), `web_search_tool_type` (string)
- `truncation_policy` (object: `{mode: string, limit: int}`)
- `supports_parallel_tool_calls` (bool), `supports_image_detail_original` (bool)
- `context_window` (int), `max_context_window` (int)
- `effective_context_window_percent` (int, 0-100)
- `experimental_supported_tools` (array), `input_modalities` (array of strings)
- `supports_search_tool` (bool)

**Null is not accepted** for any string field — the parser exits with `invalid type: null, expected a string`.

## Verification

```bash
# Before fix
codex doctor  # ❌ config could not be loaded if catalog is wrong
codex debug models  # empty output on parse error

# After fix
codex doctor  # ✓ config loaded
codex debug models  # {"models":[{"slug":"deepseek-chat",...}]}
codex exec "echo hello"  # No more "model metadata not found" warning
```

## Related

- Codex config docs: https://developers.openai.com/codex
- DeepSeek API: https://api-docs.deepseek.com
