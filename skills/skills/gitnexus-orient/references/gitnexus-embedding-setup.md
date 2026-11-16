# GitNexus Embedding Setup

Use this reference when the repo is already indexed in GitNexus but `stats.embeddings == 0`.

## What To Tell The User

Explain that GitNexus is still usable in `关键词/图谱模式`, but natural-language retrieval from `query` will be weaker because semantic embeddings are not present.

Then offer two enablement paths:

1. local embeddings
2. remote OpenAI-compatible embeddings

## Local Embeddings

Use this when the user just wants embeddings turned on and does not need a remote API.

PowerShell:

```powershell
cd D:\github_inbox\<owner>\<repo>
npx gitnexus analyze --embeddings
```

This is the simplest path. It is slower than plain indexing, but it does not require API key setup.

## Remote OpenAI-Compatible Embeddings

Use this when the user wants API-backed embeddings or is already using an OpenAI-compatible embeddings endpoint.

PowerShell template:

```powershell
$env:GITNEXUS_EMBEDDING_URL = "https://api.openai.com/v1"
$env:GITNEXUS_EMBEDDING_MODEL = "<your-embedding-model>"
$env:GITNEXUS_EMBEDDING_DIMS = "<your-model-dimensions>"
$env:GITNEXUS_EMBEDDING_API_KEY = $env:OPENAI_API_KEY
cd D:\github_inbox\<owner>\<repo>
npx gitnexus analyze --embeddings
```

Rules:

- `GITNEXUS_EMBEDDING_URL` and `GITNEXUS_EMBEDDING_MODEL` are the actual switches that turn on HTTP embedding mode.
- `GITNEXUS_EMBEDDING_API_KEY` is optional in GitNexus, but should be set when the endpoint requires authentication.
- If the user already has `OPENAI_API_KEY`, reusing it for `GITNEXUS_EMBEDDING_API_KEY` is the cleanest setup.
- `GITNEXUS_EMBEDDING_DIMS` must match the embedding vector size returned by the chosen model.

## Important Warning

Always warn about this when talking about re-indexing:

- Running `gitnexus analyze` without `--embeddings` will remove previously generated embeddings.
- If the repo already had embeddings and the user wants to preserve them, they must include `--embeddings` on future re-analysis runs.

## Suggested Chinese Wording

Use concise wording like this:

`当前仓库已经被 GitNexus 索引，但还没有 embeddings，所以现在属于关键词/图谱模式。你仍然可以继续做结构级分析；如果你想让自然语言检索更强，可以重新执行 gitnexus analyze --embeddings。若你希望走 API 方式，我也可以按你现有的 OPENAI_API_KEY 帮你配一套 GITNEXUS_EMBEDDING_* 环境变量。`
