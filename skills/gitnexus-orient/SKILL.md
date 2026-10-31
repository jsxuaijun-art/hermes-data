---
name: github-repo-orient
description: Clone or refresh a GitHub repository locally, use DeepWiki for a fast architecture overview, inspect local docs, manifests, examples, entrypoints, and maintenance signals, then explain what the project is for, what problems it solves, and how to install, run, or integrate it. Return a structured Simplified Chinese report by default, assess whether the repo looks worth secondary development, adoption, or learning, and then ask whether the user wants deeper GitNexus analysis. Use when a user shares a GitHub repo URL or owner/repo slug and wants to know what the repo is used for, how to use it, how to run it locally, whether it is an app, library, CLI, starter, or infrastructure project, or whether it looks worth building on top of or studying.
---

# GitHub Repo Orient

## Overview

Use this skill to turn a GitHub repository link into a grounded orientation pass. Clone the repo into `D:\github_inbox\<owner>\<repo>` by default, get a fast DeepWiki overview, verify the important claims from local repo evidence, and explain the repo in practical terms instead of only paraphrasing the README.

## Workflow

1. Normalize the repository input and clone or refresh it locally with:

```bash
python scripts/clone_or_update_repo.py REPO_INPUT
```

By default, the helper uses `D:\github_inbox\<owner>\<repo>`. If the user explicitly passes `--base-dir`, use that override instead.

2. Run DeepWiki first for a fast orientation pass:
- `read_wiki_structure` to see whether the repository already has useful architecture pages
- `read_wiki_contents` for the most relevant overview, architecture, components, build, or development sections
- `ask_question` only when one important gap remains after reading the wiki pages

3. Read local evidence in this order:
- `README*` and top-level docs pages
- manifests and task files such as `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `pom.xml`, `Dockerfile`, compose files, `Makefile`, `justfile`, `Taskfile`
- `examples/`, `demo/`, `docs/`, `cmd/`, `bin/`, `src/`, `apps/`, `packages/`, `tests/`
- CI workflow files when supported versions or setup expectations are unclear

4. Classify the repo before explaining it. Decide whether it is mainly:
- an end-user application
- a CLI or automation tool
- a library or SDK
- a starter, template, or boilerplate
- a plugin or integration
- an infrastructure or configuration repo

If it spans multiple categories, say so explicitly instead of forcing a single label.

5. Extract practical usage details:
- what problem the repo solves
- who it is for
- the main use cases
- the fastest local run path
- install, build, test, and integration commands
- environment variables, services, or external dependencies

6. Evaluate reuse and learning fit separately:
- reuse fit: extension points, modularity, configurability, dependency health, maintenance signals
- learning fit: clarity of architecture, code quality, tests, examples, and whether the repo teaches transferable patterns
- risks: stale dependencies, missing docs, weak tests, generated code, unclear ownership, or tightly coupled structure

7. Before mentioning GitNexus follow-up options, check whether the repo is already indexed:
- call `mcp__gitnexus__list_repos`
- compare the cloned repo path such as `D:\github_inbox\<owner>\<repo>` and the repo slug against the indexed repo list
- inspect `stats.embeddings` for the matched indexed repo
- treat `gotnexus` as `GitNexus` if the user uses the typo
- do not run GitNexus deep analysis yet unless the user explicitly asked for it in the same request

8. Verify lightly when cheap and safe:
- prefer documented read-only commands such as `--help`, `make -n`, script listing, or command discovery from repo files
- avoid long dependency installs or running unknown services unless the user asks for a deeper hands-on setup
- if you did not execute something, mark it as inferred from repo files

## GitNexus Decision Rules

Use GitNexus as a second-stage enhancement, not as a prerequisite for the first report.

- Always finish the first Chinese report from DeepWiki plus local repo evidence.
- Always append a GitNexus follow-up option after that first report.
- If the repo appears in `list_repos` and `stats.embeddings > 0`, say that the repo is in `semantic-enhanced mode` and use the `indexed_semantic` follow-up prompt from `references/gitnexus-followup.json`.
- If the repo appears in `list_repos` and `stats.embeddings == 0`, say that the repo is in `keyword/graph mode` and use the `indexed_graph_only` follow-up prompt from `references/gitnexus-followup.json`.
- If the repo does not appear in `list_repos`, use the `not_indexed` follow-up prompt from `references/gitnexus-followup.json`.
- If the repo is indexed but has no embeddings, also read `references/gitnexus-embedding-setup.md` and include a short enablement note with PowerShell examples and the preservation warning.
- Only continue into GitNexus tools after the user confirms they want a deeper pass, unless the user explicitly requested GitNexus depth in the same turn.
- Once the user opts in, read `references/deep-analysis-playbook.md` and follow its tool order.

## Embedding Mode Rules

Treat GitNexus mode detection as part of the second-stage handoff.

- `stats.embeddings > 0` means semantic search is available. Tell the user the repo is in `semantic-enhanced mode`.
- `stats.embeddings == 0` means GitNexus can still help through keywords plus graph structure, but semantic retrieval is not active. Tell the user the repo is in `keyword/graph mode`.
- Do not describe BM25 plus graph mode as semantic search.
- If embeddings are absent, tell the user they can enable them by re-running GitNexus analysis with `--embeddings`.
- If you mention re-analysis, also warn that re-running `gitnexus analyze` without `--embeddings` will remove previously generated embeddings.

## Reporting Rules

Default response language: Simplified Chinese unless the user explicitly asks for another language.

Lead with a short summary paragraph, then cover these sections in order:

- one-line conclusion
- repo purpose: what the project is for and why it exists
- use cases: 3 to 5 concrete scenarios
- how to use: install, run, or integrate steps with concrete commands when available
- tech stack and layout: ecosystem, important folders, and entrypoints
- caveats: config, external services, maturity gaps, or unclear documentation
- worth building on: verdict plus reasons
- worth learning from: verdict plus reasons
- evidence: key files or commands used for the analysis
- gitnexus mode: if indexed, state whether the repo is in `semantic-enhanced mode` or `keyword/graph mode`
- deep-analysis option: append the exact Chinese follow-up prompt from `references/gitnexus-followup.json`

Do not just echo the README. Cross-check claims against manifests, scripts, examples, and source layout.

If the repo is a monorepo, add a short package-by-package summary before the final verdicts.

Use clear confidence language:

- `confirmed` when directly supported by docs, manifests, or executed commands
- `inferred` when deduced from structure, naming, tests, or source organization

Use a verdict ladder for both reuse and learning:

- `recommended`: strong positive signals and low structural risk
- `conditional`: useful but only with clear tradeoffs or cleanup work
- `not recommended`: weak maintenance or architecture signals for the stated purpose

## Quick Heuristics

- `package.json` with `bin`, `commander`, or `yargs` usually indicates a CLI
- `pyproject.toml` plus `src/<name>` and `examples/` often indicates a library or tool
- `cmd/` in Go or multiple Rust bins usually indicates runnable programs
- `templates/`, `boilerplate`, `starter`, or scaffold scripts often indicate a starter repo
- lots of Docker, Helm, Terraform, or workflow files with little app code often indicates infrastructure automation
- multiple package roots such as `apps/` and `packages/` usually indicate a monorepo; summarize the main packages instead of pretending it is a single app
- clear interfaces, adapters, plugins, or well-separated packages usually improve secondary-development fit
- concise examples, good tests, and readable naming usually improve learning value even when the repo is small

## Bundled Resources

- Run `scripts/clone_or_update_repo.py` first for deterministic clone/update behavior and a quick repo fingerprint.
- Read `references/analysis-checklist.md` when the repo is under-documented, multi-language, or hard to classify.
- Read `references/deep-analysis-playbook.md` when the user opts into GitNexus depth after the first report.
- Read `references/gitnexus-embedding-setup.md` when the repo is indexed but `stats.embeddings == 0`.
- Read `references/gitnexus-followup.json` for the exact indexed vs not-indexed Chinese follow-up text. The file uses JSON unicode escapes; decode them before replying.
- Read `references/investment-rubric.md` when you need to judge whether the repo is worth extending, adopting, or learning from.

## Notes

- Prefer shallow clones first. Full history is rarely needed for orientation work.
- Keep repos in `D:\github_inbox` unless the user explicitly asks to copy one into the current workspace.
- If the user shares a subpage URL such as `/tree/...`, `/blob/...`, `/pull/...`, or `/issues/...`, extract the owner and repo first, then orient the repository itself.
- Separate `good code to learn from` from `good base to build on`. A repo can score high on one and only medium on the other.
- The first report should stand on its own. GitNexus is the optional next layer for execution flow, symbol graph, route map, and impact analysis.
