# Xiaomi MiMo Provider Guide

## Overview

Xiaomi MiMo is an AI model provider supported by Hermes Agent. As of May 2026, MiMo switched from per-token pricing to a **Token Plan subscription model** (credits-based), with up to 99% price reduction for heavy users. No longer differentiates by context window length.

## Models Available in Hermes

| Model | Tier | Credits Multiplier | Use Case |
|-------|------|-------------------|----------|
| `mimo-v2.5-pro` | Flagship | 2x | Strongest intelligence, 1T params/42B active/1M context. Competes with Claude Opus4.6 |
| `mimo-v2.5` | Premium | 1x | Full-modal Agent, 1M context. Great value |
| `mimo-v2.5-tts` | Voice | 0x (free limited) | Speech synthesis |
| `mimo-v2-pro` | Flagship prev-gen | 2x | Strong Agent capabilities |
| `mimo-v2-omni` | Multimodal | 1x | Vision/audio/text understanding |
| `mimo-v2-flash` | Fast | — | Fast, light, simple tasks |
| `mimo-v2-tts` | Voice | 0x (free limited) | Speech synthesis |

## Token Plan Pricing (May 2026)

| Tier | Monthly | Credits | Annual (12% off) | Suitable For |
|------|---------|---------|-------------------|-------------|
| Lite | ¥39 | 60M | ¥411.84 (720M) | Trial, occasional use |
| Standard | ¥99 | 200M | ¥1,045.44 (2.4B) | Daily light use |
| Pro | ¥329 | 700M | ¥3,474.24 (8.4B) | Heavy daily use |
| Max | ¥659 | 1600M | ¥6,959.04 (19.2B) | All-day power user |

## Configuration

```bash
# Set provider
hermes config set provider default xiaomi

# Set model
hermes config set model.default mimo-v2.5   # or mimo-v2.5-pro

# API Key — get from https://platform.xiaomimimo.com
# Add to ~/.hermes/.env:
# XIAOMI_API_KEY=your_key_here
```

## Recommendation for Generic Use

- **Best value**: `mimo-v2.5` (1x credits, near-flagship performance)
- **Best quality**: `mimo-v2.5-pro` (2x credits, strongest)
- **Budget research tasks**: `mimo-v2-flash` (fast, cheap)
