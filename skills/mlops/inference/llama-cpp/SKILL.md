---
name: llama-cpp
<<<<<<< LOCAL (this PC)
description: Runs LLM inference on CPU, Apple Silicon, and consumer GPUs without NVIDIA hardware. Use for edge deployment, M1/M2/M3 Macs, AMD/Intel GPUs, or when CUDA is unavailable. Supports GGUF quantization (1.5-8 bit) for reduced memory and 4-10× speedup vs PyTorch on CPU.
version: 1.0.0
=======
description: llama.cpp local GGUF inference + HF Hub model discovery.
version: 2.1.2
>>>>>>> REPO (github)
author: Orchestra Research
license: MIT
<<<<<<< LOCAL (this PC)
dependencies: [llama-cpp-python]
=======
dependencies: [llama-cpp-python>=0.2.0]
platforms: [linux, macos, windows]
>>>>>>> REPO (github)
metadata:
  hermes:
<<<<<<< LOCAL (this PC)
    tags: [Inference Serving, Llama.cpp, CPU Inference, Apple Silicon, Edge Deployment, GGUF, Quantization, Non-NVIDIA, AMD GPUs, Intel GPUs, Embedded]
=======
    tags: [llama.cpp, GGUF, Quantization, Hugging Face Hub, CPU Inference, Apple Silicon, Edge Deployment, AMD GPUs, Intel GPUs, NVIDIA, URL-first]
---
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
---
=======
# llama.cpp + GGUF
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
# llama.cpp
=======
Use this skill for local GGUF inference, quant selection, or Hugging Face repo discovery for llama.cpp.
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
Pure C/C++ LLM inference with minimal dependencies, optimized for CPUs and non-NVIDIA hardware.
=======
## When to use
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
## When to use llama.cpp
=======
- Run local models on CPU, Apple Silicon, CUDA, ROCm, or Intel GPUs
- Find the right GGUF for a specific Hugging Face repo
- Build a `llama-server` or `llama-cli` command from the Hub
- Search the Hub for models that already support llama.cpp
- Enumerate available `.gguf` files and sizes for a repo
- Decide between Q4/Q5/Q6/IQ variants for the user's RAM or VRAM
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
**Use llama.cpp when:**
- Running on CPU-only machines
- Deploying on Apple Silicon (M1/M2/M3/M4)
- Using AMD or Intel GPUs (no CUDA)
- Edge deployment (Raspberry Pi, embedded systems)
- Need simple deployment without Docker/Python
=======
## Model Discovery workflow
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
**Use TensorRT-LLM instead when:**
- Have NVIDIA GPUs (A100/H100)
- Need maximum throughput (100K+ tok/s)
- Running in datacenter with CUDA
=======
Prefer URL workflows before asking for `hf`, Python, or custom scripts.
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
**Use vLLM instead when:**
- Have NVIDIA GPUs
- Need Python-first API
- Want PagedAttention
=======
1. Search for candidate repos on the Hub:
   - Base: `https://huggingface.co/models?apps=llama.cpp&sort=trending`
   - Add `search=<term>` for a model family
   - Add `num_parameters=min:0,max:24B` or similar when the user has size constraints
2. Open the repo with the llama.cpp local-app view:
   - `https://huggingface.co/<repo>?local-app=llama.cpp`
3. Treat the local-app snippet as the source of truth when it is visible:
   - copy the exact `llama-server` or `llama-cli` command
   - report the recommended quant exactly as HF shows it
4. Read the same `?local-app=llama.cpp` URL as page text or HTML and extract the section under `Hardware compatibility`:
   - prefer its exact quant labels and sizes over generic tables
   - keep repo-specific labels such as `UD-Q4_K_M` or `IQ4_NL_XL`
   - if that section is not visible in the fetched page source, say so and fall back to the tree API plus generic quant guidance
5. Query the tree API to confirm what actually exists:
   - `https://huggingface.co/api/models/<repo>/tree/main?recursive=true`
   - keep entries where `type` is `file` and `path` ends with `.gguf`
   - use `path` and `size` as the source of truth for filenames and byte sizes
   - separate quantized checkpoints from `mmproj-*.gguf` projector files and `BF16/` shard files
   - use `https://huggingface.co/<repo>/tree/main` only as a human fallback
6. If the local-app snippet is not text-visible, reconstruct the command from the repo plus the chosen quant:
   - shorthand quant selection: `llama-server -hf <repo>:<QUANT>`
   - exact-file fallback: `llama-server --hf-repo <repo> --hf-file <filename.gguf>`
7. Only suggest conversion from Transformers weights if the repo does not already expose GGUF files.
>>>>>>> REPO (github)

## Quick start

<<<<<<< LOCAL (this PC)
### Installation
=======
### Install llama.cpp
>>>>>>> REPO (github)

```bash
<<<<<<< LOCAL (this PC)
# macOS/Linux
=======
# macOS / Linux (simplest)
>>>>>>> REPO (github)
brew install llama.cpp
```

```bash
winget install llama.cpp
```

<<<<<<< LOCAL (this PC)
# Or build from source
git clone https://github.com/ggerganov/llama.cpp
=======
```bash
git clone https://github.com/ggml-org/llama.cpp
>>>>>>> REPO (github)
cd llama.cpp
<<<<<<< LOCAL (this PC)
make
=======
cmake -B build
cmake --build build --config Release
```
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
# With Metal (Apple Silicon)
make LLAMA_METAL=1
=======
### Run directly from the Hugging Face Hub
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
# With CUDA (NVIDIA)
make LLAMA_CUDA=1

# With ROCm (AMD)
make LLAMA_HIP=1
=======
```bash
llama-cli -hf bartowski/Llama-3.2-3B-Instruct-GGUF:Q8_0
>>>>>>> REPO (github)
```

### Download model

```bash
<<<<<<< LOCAL (this PC)
# Download from HuggingFace (GGUF format)
huggingface-cli download \
    TheBloke/Llama-2-7B-Chat-GGUF \
    llama-2-7b-chat.Q4_K_M.gguf \
    --local-dir models/
=======
llama-server -hf bartowski/Llama-3.2-3B-Instruct-GGUF:Q8_0
```
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
# Or convert from HuggingFace
python convert_hf_to_gguf.py models/llama-2-7b-chat/
```
=======
### Run an exact GGUF file from the Hub
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
### Run inference
=======
Use this when the tree API shows custom file naming or the exact HF snippet is missing.
>>>>>>> REPO (github)

```bash
<<<<<<< LOCAL (this PC)
# Simple chat
./llama-cli \
    -m models/llama-2-7b-chat.Q4_K_M.gguf \
    -p "Explain quantum computing" \
    -n 256  # Max tokens

# Interactive chat
./llama-cli \
    -m models/llama-2-7b-chat.Q4_K_M.gguf \
    --interactive
=======
llama-server \
    --hf-repo microsoft/Phi-3-mini-4k-instruct-gguf \
    --hf-file Phi-3-mini-4k-instruct-q4.gguf \
    -c 4096
>>>>>>> REPO (github)
```

<<<<<<< LOCAL (this PC)
### Server mode
=======
### OpenAI-compatible server check
>>>>>>> REPO (github)

```bash
# Start OpenAI-compatible server
./llama-server \
    -m models/llama-2-7b-chat.Q4_K_M.gguf \
    --host 0.0.0.0 \
    --port 8080 \
    -ngl 32  # Offload 32 layers to GPU

# Client request
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
<<<<<<< LOCAL (this PC)
    "model": "llama-2-7b-chat",
    "messages": [{"role": "user", "content": "Hello!"}],
    "temperature": 0.7,
    "max_tokens": 100
=======
    "messages": [
      {"role": "user", "content": "Write a limerick about Python exceptions"}
    ]
>>>>>>> REPO (github)
  }'
```

<<<<<<< LOCAL (this PC)
## Quantization formats
=======
## Python bindings (llama-cpp-python)
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
### GGUF format overview
=======
`pip install llama-cpp-python` (CUDA: `CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python --force-reinstall --no-cache-dir`; Metal: `CMAKE_ARGS="-DGGML_METAL=on" ...`).
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
| Format | Bits | Size (7B) | Speed | Quality | Use Case |
|--------|------|-----------|-------|---------|----------|
| **Q4_K_M** | 4.5 | 4.1 GB | Fast | Good | **Recommended default** |
| Q4_K_S | 4.3 | 3.9 GB | Faster | Lower | Speed critical |
| Q5_K_M | 5.5 | 4.8 GB | Medium | Better | Quality critical |
| Q6_K | 6.5 | 5.5 GB | Slower | Best | Maximum quality |
| Q8_0 | 8.0 | 7.0 GB | Slow | Excellent | Minimal degradation |
| Q2_K | 2.5 | 2.7 GB | Fastest | Poor | Testing only |
=======
### Basic generation
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
### Choosing quantization
=======
```python
from llama_cpp import Llama
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
```bash
# General use (balanced)
Q4_K_M  # 4-bit, medium quality
=======
llm = Llama(
    model_path="./model-q4_k_m.gguf",
    n_ctx=4096,
    n_gpu_layers=35,     # 0 for CPU, 99 to offload everything
    n_threads=8,
)
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
# Maximum speed (more degradation)
Q2_K or Q3_K_M

# Maximum quality (slower)
Q6_K or Q8_0

# Very large models (70B, 405B)
Q3_K_M or Q4_K_S  # Lower bits to fit in memory
=======
out = llm("What is machine learning?", max_tokens=256, temperature=0.7)
print(out["choices"][0]["text"])
>>>>>>> REPO (github)
```

<<<<<<< LOCAL (this PC)
## Hardware acceleration
=======
### Chat + streaming
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
### Apple Silicon (Metal)
=======
```python
llm = Llama(
    model_path="./model-q4_k_m.gguf",
    n_ctx=4096,
    n_gpu_layers=35,
    chat_format="llama-3",   # or "chatml", "mistral", etc.
)
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
```bash
# Build with Metal
make LLAMA_METAL=1
=======
resp = llm.create_chat_completion(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is Python?"},
    ],
    max_tokens=256,
)
print(resp["choices"][0]["message"]["content"])
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
# Run with GPU acceleration (automatic)
./llama-cli -m model.gguf -ngl 999  # Offload all layers

# Performance: M3 Max 40-60 tokens/sec (Llama 2-7B Q4_K_M)
=======
# Streaming
for chunk in llm("Explain quantum computing:", max_tokens=256, stream=True):
    print(chunk["choices"][0]["text"], end="", flush=True)
>>>>>>> REPO (github)
```

<<<<<<< LOCAL (this PC)
### NVIDIA GPUs (CUDA)
=======
### Embeddings
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
```bash
# Build with CUDA
make LLAMA_CUDA=1

# Offload layers to GPU
./llama-cli -m model.gguf -ngl 35  # Offload 35/40 layers

# Hybrid CPU+GPU for large models
./llama-cli -m llama-70b.Q4_K_M.gguf -ngl 20  # GPU: 20 layers, CPU: rest
=======
```python
llm = Llama(model_path="./model-q4_k_m.gguf", embedding=True, n_gpu_layers=35)
vec = llm.embed("This is a test sentence.")
print(f"Embedding dimension: {len(vec)}")
>>>>>>> REPO (github)
```

<<<<<<< LOCAL (this PC)
### AMD GPUs (ROCm)
=======
You can also load a GGUF straight from the Hub:
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
```bash
# Build with ROCm
make LLAMA_HIP=1

# Run with AMD GPU
./llama-cli -m model.gguf -ngl 999
=======
```python
llm = Llama.from_pretrained(
    repo_id="bartowski/Llama-3.2-3B-Instruct-GGUF",
    filename="*Q4_K_M.gguf",
    n_gpu_layers=35,
)
>>>>>>> REPO (github)
```

<<<<<<< LOCAL (this PC)
## Common patterns
=======
## Choosing a quant
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
### Batch processing
=======
Use the Hub page first, generic heuristics second.
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
```bash
# Process multiple prompts from file
cat prompts.txt | ./llama-cli \
    -m model.gguf \
    --batch-size 512 \
    -n 100
```
=======
- Prefer the exact quant that HF marks as compatible for the user's hardware profile.
- For general chat, start with `Q4_K_M`.
- For code or technical work, prefer `Q5_K_M` or `Q6_K` if memory allows.
- For very tight RAM budgets, consider `Q3_K_M`, `IQ` variants, or `Q2` variants only if the user explicitly prioritizes fit over quality.
- For multimodal repos, mention `mmproj-*.gguf` separately. The projector is not the main model file.
- Do not normalize repo-native labels. If the page says `UD-Q4_K_M`, report `UD-Q4_K_M`.
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
### Constrained generation
=======
## Extracting available GGUFs from a repo
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
```bash
# JSON output with grammar
./llama-cli \
    -m model.gguf \
    -p "Generate a person: " \
    --grammar-file grammars/json.gbnf
=======
When the user asks what GGUFs exist, return:
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
# Outputs valid JSON only
```
=======
- filename
- file size
- quant label
- whether it is a main model or an auxiliary projector
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
### Context size
=======
Ignore unless requested:
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
```bash
# Increase context (default 512)
./llama-cli \
    -m model.gguf \
    -c 4096  # 4K context window
=======
- README
- BF16 shard files
- imatrix blobs or calibration artifacts
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
# Very long context (if model supports)
./llama-cli -m model.gguf -c 32768  # 32K context
```
=======
Use the tree API for this step:
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
## Performance benchmarks
=======
- `https://huggingface.co/api/models/<repo>/tree/main?recursive=true`
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
### CPU performance (Llama 2-7B Q4_K_M)
=======
For a repo like `unsloth/Qwen3.6-35B-A3B-GGUF`, the local-app page can show quant chips such as `UD-Q4_K_M`, `UD-Q5_K_M`, `UD-Q6_K`, and `Q8_0`, while the tree API exposes exact file paths such as `Qwen3.6-35B-A3B-UD-Q4_K_M.gguf` and `Qwen3.6-35B-A3B-Q8_0.gguf` with byte sizes. Use the tree API to turn a quant label into an exact filename.
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
| CPU | Threads | Speed | Cost |
|-----|---------|-------|------|
| Apple M3 Max | 16 | 50 tok/s | $0 (local) |
| AMD Ryzen 9 7950X | 32 | 35 tok/s | $0.50/hour |
| Intel i9-13900K | 32 | 30 tok/s | $0.40/hour |
| AWS c7i.16xlarge | 64 | 40 tok/s | $2.88/hour |
=======
## Search patterns
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
### GPU acceleration (Llama 2-7B Q4_K_M)
=======
Use these URL shapes directly:
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
| GPU | Speed | vs CPU | Cost |
|-----|-------|--------|------|
| NVIDIA RTX 4090 | 120 tok/s | 3-4× | $0 (local) |
| NVIDIA A10 | 80 tok/s | 2-3× | $1.00/hour |
| AMD MI250 | 70 tok/s | 2× | $2.00/hour |
| Apple M3 Max (Metal) | 50 tok/s | ~Same | $0 (local) |
=======
```text
https://huggingface.co/models?apps=llama.cpp&sort=trending
https://huggingface.co/models?search=<term>&apps=llama.cpp&sort=trending
https://huggingface.co/models?search=<term>&apps=llama.cpp&num_parameters=min:0,max:24B&sort=trending
https://huggingface.co/<repo>?local-app=llama.cpp
https://huggingface.co/api/models/<repo>/tree/main?recursive=true
https://huggingface.co/<repo>/tree/main
```
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
## Supported models
=======
## Output format
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
**LLaMA family**:
- Llama 2 (7B, 13B, 70B)
- Llama 3 (8B, 70B, 405B)
- Code Llama
=======
When answering discovery requests, prefer a compact structured result like:
>>>>>>> REPO (github)

<<<<<<< LOCAL (this PC)
**Mistral family**:
- Mistral 7B
- Mixtral 8x7B, 8x22B

**Other**:
- Falcon, BLOOM, GPT-J
- Phi-3, Gemma, Qwen
- LLaVA (vision), Whisper (audio)

**Find models**: https://huggingface.co/models?library=gguf
=======
```text
Repo: <repo>
Recommended quant from HF: <label> (<size>)
llama-server: <command>
Other GGUFs:
- <filename> - <size>
- <filename> - <size>
Source URLs:
- <local-app URL>
- <tree API URL>
```
>>>>>>> REPO (github)

## References

<<<<<<< LOCAL (this PC)
- **[Quantization Guide](references/quantization.md)** - GGUF formats, conversion, quality comparison
- **[Server Deployment](references/server.md)** - API endpoints, Docker, monitoring
- **[Optimization](references/optimization.md)** - Performance tuning, hybrid CPU+GPU
=======
- **[hub-discovery.md](references/hub-discovery.md)** - URL-only Hugging Face workflows, search patterns, GGUF extraction, and command reconstruction
- **[advanced-usage.md](references/advanced-usage.md)** — speculative decoding, batched inference, grammar-constrained generation, LoRA, multi-GPU, custom builds, benchmark scripts
- **[quantization.md](references/quantization.md)** — quant quality tradeoffs, when to use Q4/Q5/Q6/IQ, model size scaling, imatrix
- **[server.md](references/server.md)** — direct-from-Hub server launch, OpenAI API endpoints, Docker deployment, NGINX load balancing, monitoring
- **[optimization.md](references/optimization.md)** — CPU threading, BLAS, GPU offload heuristics, batch tuning, benchmarks
- **[troubleshooting.md](references/troubleshooting.md)** — install/convert/quantize/inference/server issues, Apple Silicon, debugging
>>>>>>> REPO (github)

## Resources

<<<<<<< LOCAL (this PC)
- **GitHub**: https://github.com/ggerganov/llama.cpp
- **Models**: https://huggingface.co/models?library=gguf
- **Discord**: https://discord.gg/llama-cpp


=======
- **GitHub**: https://github.com/ggml-org/llama.cpp
- **Hugging Face GGUF + llama.cpp docs**: https://huggingface.co/docs/hub/gguf-llamacpp
- **Hugging Face Local Apps docs**: https://huggingface.co/docs/hub/main/local-apps
- **Hugging Face Local Agents docs**: https://huggingface.co/docs/hub/agents-local
- **Example local-app page**: https://huggingface.co/unsloth/Qwen3.6-35B-A3B-GGUF?local-app=llama.cpp
- **Example tree API**: https://huggingface.co/api/models/unsloth/Qwen3.6-35B-A3B-GGUF/tree/main?recursive=true
- **Example llama.cpp search**: https://huggingface.co/models?num_parameters=min:0,max:24B&apps=llama.cpp&sort=trending
- **License**: MIT
>>>>>>> REPO (github)
