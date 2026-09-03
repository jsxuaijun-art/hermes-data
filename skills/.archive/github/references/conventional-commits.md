# Conventional Commits Quick Reference

Format: `type(scope): description`

## Types

| Type | When to use | Example |
|------|------------|---------|
| `feat` | New feature | `feat(auth): add OAuth2 login flow` |
| `fix` | Bug fix | `fix(api): handle null response from /users endpoint` |
| `refactor` | Code restructuring, no behavior change | `refactor(db): extract query builder into separate module` |
| `docs` | Documentation only | `docs: update API usage examples in README` |
| `test` | Adding or updating tests | `test(auth): add integration tests for token refresh` |
| `ci` | CI/CD configuration | `ci: add Python 3.12 to test matrix` |
| `chore` | Maintenance, dependencies, tooling | `chore: upgrade pytest to 8.x` |
| `perf` | Performance improvement | `perf(search): add index on users.email column` |

## Breaking Changes

Add `!` after type/scope: `feat(api)!: change authentication to use bearer tokens`
Or add `BREAKING CHANGE:` in the footer.

## Multi-line Body

Wrap at 72 characters. Use bullet points:
```
feat(auth): add JWT-based user authentication

- Add login/register endpoints with input validation
- Add User model with argon2 password hashing
- Add auth middleware for protected routes

Closes #42
```

## Linking Issues

`Closes #42`, `Fixes #42` (auto-close on merge), `Refs #42` (reference only).
