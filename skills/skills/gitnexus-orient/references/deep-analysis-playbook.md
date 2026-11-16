# Deep Analysis Playbook

Use this reference only after the first Chinese report is complete and the user wants GitNexus depth.

## Goal

Produce a second-stage deep analysis that complements the first report. Do not repeat the full orientation report. Focus on structure, execution flow, routes, and change-risk insights that are hard to get from README and manifests alone.

## Readiness Check

1. Call `mcp__gitnexus__list_repos`.
2. Resolve the indexed repo using this order:
- explicit user binding such as `GitNexus repo: <name-or-path>`
- exact match on cloned local path
- unique basename match on the repo folder name
3. Inspect `stats.embeddings` for the resolved repo and tell the user which mode is active:
- `stats.embeddings > 0` => `语义增强模式`
- `stats.embeddings == 0` => `关键词/图谱模式`
4. If you cannot resolve a single indexed repo, stop and use the `not_indexed` follow-up prompt instead of guessing.

## Tool Order

1. `mcp__gitnexus__query`
- Use it first to identify the main flows, modules, or packages related to the repo's purpose.
- Ask about the repository at a high level, for example existing auth flow, API execution path, CLI entrypoints, or main application startup.

2. `mcp__gitnexus__context`
- Use it on 2 to 4 important symbols or modules found by `query`.
- Prefer entrypoints, orchestrators, service facades, or core library abstractions.

3. Conditional route and API tools
- For web or API repos, run `mcp__gitnexus__route_map`.
- If response shape consistency matters, run `mcp__gitnexus__shape_check` or `mcp__gitnexus__api_impact`.
- Skip route tools for CLI-only or library-only repositories.

4. Conditional change-risk tools
- When discussing extension points or secondary-development fit, run `mcp__gitnexus__impact`.
- Use `direction=upstream` on one or two likely extension points to estimate coupling and blast radius.

## Deep Report Boundaries

The second-stage GitNexus report should focus on:

- key execution flows
- core symbol or module relationships
- route and API surface, when applicable
- likely extension points
- coupling, impact radius, or fragile areas

Do not re-explain basic install steps unless GitNexus reveals a contradiction with the first report.

## Output Shape

Keep the GitNexus follow-up concise:

1. short summary of what the deep pass clarified
2. key flows or module relationships
3. route or API notes when relevant
4. extension points and risk areas
5. recommended next debugging or modification targets

## Confidence Rules

- Treat GitNexus as structural evidence, not runtime proof.
- When `stats.embeddings == 0`, expect weaker natural-language retrieval from `query` and lean more on explicit symbol, route, and file hints.
- Keep install, environment, and command claims grounded in local repo files or executed commands.
- If GitNexus conflicts with docs, surface the conflict instead of silently picking one side.
