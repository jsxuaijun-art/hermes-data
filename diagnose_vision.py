#!/usr/bin/env python3
"""Diagnose Hermes Agent vision setup — checks config, env vars, and provider resolution."""

import os, sys, json

def check_env(key, label=None):
    val = os.getenv(key)
    if val:
        masked = val[:8] + "..." + val[-4:] if len(val) > 20 else val[:8] + "..."
        print(f"  ✅ {label or key} = {masked}")
        return True
    else:
        print(f"  ❌ {label or key} = (not set)")
        return False

print("=== Env Vars ===")
check_env("OPENROUTER_API_KEY", "OPENROUTER_API_KEY")
check_env("ANTHROPIC_API_KEY", "ANTHROPIC_API_KEY")
check_env("OPENAI_API_KEY", "OPENAI_API_KEY")
check_env("AUXILIARY_VISION_MODEL", "AUXILIARY_VISION_MODEL (override)")

print("\n=== Config ===")
try:
    from hermes_cli.config import load_config, cfg_get
    cfg = load_config()
    vision = cfg_get(cfg, "auxiliary", "vision", default={})
    print(f"  provider:       {vision.get('provider', 'N/A')}")
    print(f"  model:          {vision.get('model', 'N/A')}")
    print(f"  base_url:       {vision.get('base_url', 'N/A')}")
    print(f"  timeout:        {vision.get('timeout', 'N/A')}")
    print(f"  download_timeout: {vision.get('download_timeout', 'N/A')}")

    img_mode = cfg_get(cfg, "agent", "image_input_mode", default="auto")
    print(f"  image_input_mode: {img_mode}")
except Exception as e:
    print(f"  ❌ Error loading config: {e}")

print("\n=== Vision Provider Resolution ===")
try:
    from agent.auxiliary_client import resolve_vision_provider_client
    provider, client, model = resolve_vision_provider_client()
    print(f"  Provider: {provider or 'NONE'}")
    print(f"  Model:    {model or 'NONE'}")
    print(f"  Ready:    {client is not None}")
    if provider:
        print(f"  Chain:    {' → '.join(str(p) for p in [provider, model])}")
except Exception as e:
    print(f"  ❌ Resolution failed: {e}")

print("\n=== Tool Check ===")
try:
    from tools.vision_tools import check_vision_requirements
    ok = check_vision_requirements()
    print(f"  vision_analyze available: {ok}")
except Exception as e:
    print(f"  ❌ Tool check failed: {e}")

print("\n=== Model Capabilities (DeepSeek) ===")
try:
    from agent.models_dev import get_model_capabilities
    caps = get_model_capabilities("deepseek", "deepseek-v4-flash")
    if caps:
        print(f"  supports_vision: {caps.supports_vision}")
        print(f"  supports_tools:  {caps.supports_tools}")
    else:
        print("  No capability metadata found for deepseek/deepseek-v4-flash")
except Exception as e:
    print(f"  ❌ Lookup failed: {e}")

print("\n=== Quick Fix ===")
if not os.getenv("OPENROUTER_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
    print("  💡 Neither OPENROUTER_API_KEY nor ANTHROPIC_API_KEY is set!")
    print("     Set one of these for vision to work:")
    print("     export OPENROUTER_API_KEY='sk-or-v1-...'")
    print("     OR")
    print("     export ANTHROPIC_API_KEY='sk-ant-...'")
elif os.getenv("OPENROUTER_API_KEY"):
    print("  ✅ OpenRouter key is set — vision should resolve via OpenRouter")
    print(f"     Default model: google/gemini-3-flash-preview")
    print("     Override with: export AUXILIARY_VISION_MODEL='google/gemini-2.5-flash-preview-04-17'")
    print("     Or set in config.yaml: auxiliary.vision.model")
