# Analysis Checklist

Use this reference when the repository is under-documented, spans multiple ecosystems, or has several runnable surfaces.

## Evidence Order

1. Read DeepWiki structure and the most relevant overview or architecture pages first.
2. Read `README*`, top-level docs pages, and any quick-start section.
3. Read manifests and task files to confirm the ecosystem and canonical commands.
4. Read `examples/`, `demo/`, `cmd/`, `bin/`, `src/`, `apps/`, and `packages/` to see how the repo is actually used.
5. Read tests to confirm expected behavior and supported workflows.
6. Read CI workflows only when version support, setup steps, or official commands remain unclear.

## Repo Type Checks

- Call it a `library` when the repo exposes importable packages, SDK surfaces, or public APIs.
- Call it a `CLI` when manifests define binaries, command routers, or executable entrypoints.
- Call it an `application` when the main goal is to run a server, UI, service, or worker.
- Call it a `starter/template` when the repo mostly scaffolds new projects.
- Call it `infrastructure` when the repo centers on deployment, automation, IaC, or workflow orchestration.
- Call it a `monorepo` when there are multiple apps or packages with separate responsibilities.

## Ecosystem Probes

### Python

- Inspect `pyproject.toml`, `setup.py`, `setup.cfg`, `requirements*.txt`, and `tox.ini`.
- Look for `[project.scripts]`, `tool.poetry.scripts`, console entrypoints, and `src/<package>`.
- Common usage evidence: `python -m package`, `uv run`, `pytest`, notebooks, or docs examples.

### Node.js

- Inspect `package.json`, workspaces, lockfiles, `turbo.json`, and task runners.
- Read `scripts`, `bin`, `exports`, and package names.
- Common usage evidence: `npm run`, `pnpm`, `yarn`, CLI bins, Next.js/Vite config, or example apps.

### Rust

- Inspect `Cargo.toml`, `[[bin]]`, `[lib]`, workspace members, and examples.
- Common usage evidence: `cargo run --bin ...`, `cargo test`, crate features, or docs examples.

### Go

- Inspect `go.mod`, `cmd/`, `main.go`, internal packages, and Cobra or urfave/cli wiring.
- Common usage evidence: `go run ./cmd/...`, `go test ./...`, service boot files, or sample configs.

### JVM

- Inspect `pom.xml`, `build.gradle*`, wrapper files, and `src/main`.
- Common usage evidence: Spring Boot plugins, application configs, Gradle tasks, or CLI main classes.

### Containers and Infra

- Inspect `Dockerfile`, compose files, Helm charts, Terraform, Pulumi, and `.github/workflows`.
- Confirm whether the repo is meant to run locally, deploy remotely, or serve as glue automation.

## Output Scaffold

Use a compact structure:

1. One-paragraph summary of what the repo does.
2. Main use cases with concrete examples.
3. How to install, run, or integrate it.
4. Key folders, packages, or entrypoints.
5. Risks, prerequisites, and unclear areas.
6. Reuse verdict: worth building on or not, with reasons.
7. Learning verdict: worth studying or not, with reasons.
8. Evidence list with `confirmed` vs `inferred` distinctions.
9. GitNexus follow-up option: indexed vs not-indexed, with no auto deep dive.
10. If indexed, include the current GitNexus mode: semantic-enhanced vs keyword/graph.

## Ambiguity Rules

- If the repo exposes both a library and an app, say which one appears primary and why.
- If the README is missing or weak, rely more on manifests, examples, tests, and CI.
- If the project looks abandoned, mention stale dependencies, old workflows, or missing releases as signals rather than making a hard claim.
- If setup commands are inconsistent across files, surface the conflict instead of picking one silently.
- If code quality is mixed, separate `good reference to learn from` from `good base to extend`.
- Always finish the first report before offering GitNexus depth, unless the user explicitly requested GitNexus in the same turn.
