# Investment Rubric

Use this reference when the user also wants a judgment call such as:

- Is this repo worth secondary development?
- Is this a good base to customize or adopt?
- Is this worth studying to learn the stack or architecture?

Score reuse and learning separately. They are not the same question.

Use this rubric during the first report. GitNexus can deepen the structural reasoning later, but it should not block the initial reuse or learning verdict.

## Reuse And Secondary-Development Fit

Check these signals:

1. Maintenance signals
- recent commits on the default branch
- working CI or at least maintained workflow files
- releases, tags, changelog, or upgrade notes when present
- active dependency versions or at least non-obsolete tooling

2. Extension shape
- clear package or module boundaries
- public interfaces, plugin hooks, adapters, or configuration seams
- limited hardcoded environment assumptions
- low coupling between core logic and delivery layer

3. Operational fit
- setup steps are reproducible
- environment variables and services are documented
- tests exist around the parts you would likely change
- examples or demo apps show intended extension paths

4. Risk flags
- abandoned or stale branch history
- generated code checked in without source generators
- large monolith with hidden side effects
- missing license for intended reuse
- scripts that assume one machine, one path, or one developer workflow

### Reuse Verdict Guide

- `recommended`: maintained enough, understandable, and extendable with manageable risk
- `conditional`: promising but requires cleanup, dependency updates, or architecture work first
- `not recommended`: brittle, stale, under-documented, or too coupled to justify building on directly

## Learning Value

Check these signals:

1. Code clarity
- descriptive names
- discoverable entrypoints
- small enough modules or well-scoped packages
- comments or docs where the design is not obvious

2. Teachability
- examples that mirror real use
- tests that reveal intended behavior
- architecture that demonstrates transferable patterns
- docs that connect concepts to commands or code paths

3. Representative quality
- uses modern but not overly magical tooling
- follows recognizable conventions for the ecosystem
- avoids too much generated boilerplate drowning out the interesting parts

4. Learning risks
- clever but opaque meta-frameworks
- too much custom tooling without explanation
- stale patterns no longer common in the ecosystem
- noisy monorepo setup with little instructional payoff

### Learning Verdict Guide

- `recommended`: clear, representative, and rich in transferable patterns
- `conditional`: useful if the learner already knows the basics or studies only selected areas
- `not recommended`: too opaque, stale, or noisy to be an efficient learning source

## Output Pattern

For reuse and learning, include:

1. verdict
2. 2 to 4 strongest positive signals
3. 1 to 3 main risks or caveats
4. brief recommendation on how to approach it

Examples:

- reuse: `conditional` because architecture is promising, but tests are sparse and setup is brittle
- learning: `recommended` because the repo has clear modules, examples, and representative tests
