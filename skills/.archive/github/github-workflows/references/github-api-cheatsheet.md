# GitHub API Cheatsheet (curl)

Base URL: `https://api.github.com`
Auth: `-H "Authorization: token $GITHUB_TOKEN"`
Content type: `-H "Content-Type: application/json"`

## Repositories

| Action | Method | Endpoint |
|--------|--------|----------|
| List user repos | GET | `/user/repos?per_page=100&sort=updated` |
| List org repos | GET | `/orgs/{org}/repos` |
| View repo | GET | `/repos/{owner}/{repo}` |
| Edit repo | PATCH | `/repos/{owner}/{repo}` |
| Create repo (user) | POST | `/user/repos` |
| Create repo (org) | POST | `/orgs/{org}/repos` |
| Fork repo | POST | `/repos/{owner}/{repo}/forks` |
| Create from template | POST | `/repos/{owner}/{template-repo}/generate` |
| Set topics | PUT | `/repos/{owner}/{repo}/topics` |

## Issues

| Action | Method | Endpoint |
|--------|--------|----------|
| List | GET | `/repos/{owner}/{repo}/issues?state=open` |
| View | GET | `/repos/{owner}/{repo}/issues/{number}` |
| Create | POST | `/repos/{owner}/{repo}/issues` |
| Edit | PATCH | `/repos/{owner}/{repo}/issues/{number}` |
| Add labels | POST | `/repos/{owner}/{repo}/issues/{number}/labels` |
| Remove label | DELETE | `/repos/{owner}/{repo}/issues/{number}/labels/{name}` |
| List labels | GET | `/repos/{owner}/{repo}/labels` |
| Comment | POST | `/repos/{owner}/{repo}/issues/{number}/comments` |
| Add assignees | POST | `/repos/{owner}/{repo}/issues/{number}/assignees` |

## Pull Requests

| Action | Method | Endpoint |
|--------|--------|----------|
| List | GET | `/repos/{owner}/{repo}/pulls` |
| View | GET | `/repos/{owner}/{repo}/pulls/{number}` |
| Create | POST | `/repos/{owner}/{repo}/pulls` |
| List files | GET | `/repos/{owner}/{repo}/pulls/{number}/files` |
| Merge | PUT | `/repos/{owner}/{repo}/pulls/{number}/merge` |
| Request reviewers | POST | `/repos/{owner}/{repo}/pulls/{number}/requested_reviewers` |
| Get diff | GET | `/repos/{owner}/{repo}/pulls/{number}` (Accept: `application/vnd.github.diff`) |

## Reviews

| Action | Method | Endpoint |
|--------|--------|----------|
| Create review | POST | `/repos/{owner}/{repo}/pulls/{number}/reviews` |
| List reviews | GET | `/repos/{owner}/{repo}/pulls/{number}/reviews` |
| Create review comment | POST | `/repos/{owner}/{repo}/pulls/{number}/comments` |

## CI / Actions

| Action | Method | Endpoint |
|--------|--------|----------|
| List workflows | GET | `/repos/{owner}/{repo}/actions/workflows` |
| List runs | GET | `/repos/{owner}/{repo}/actions/runs` |
| View run | GET | `/repos/{owner}/{repo}/actions/runs/{run_id}` |
| Rerun | POST | `/repos/{owner}/{repo}/actions/runs/{run_id}/rerun` |
| Rerun failed jobs | POST | `/repos/{owner}/{repo}/actions/runs/{run_id}/rerun-failed-jobs` |
| Download logs | GET | `/repos/{owner}/{repo}/actions/runs/{run_id}/logs` |
| Trigger workflow | POST | `/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches` |
| List secrets | GET | `/repos/{owner}/{repo}/actions/secrets` |
| Set secret | PUT | `/repos/{owner}/{repo}/actions/secrets/{name}` (needs encrypted value) |

## Releases

| Action | Method | Endpoint |
|--------|--------|----------|
| List | GET | `/repos/{owner}/{repo}/releases` |
| Create | POST | `/repos/{owner}/{repo}/releases` |
| Upload asset | POST | `https://uploads.github.com/repos/{owner}/{repo}/releases/{id}/assets?name={filename}` |

## Search

| Scope | Endpoint |
|-------|----------|
| Issues | `GET /search/issues?q={query}+repo:{owner}/{repo}` |
| Repos | `GET /search/repositories?q={query}` |
| Code | `GET /search/code?q={query}+repo:{owner}/{repo}` |

## Utility

- Get current user: `GET /user`
- Commit status: `GET /repos/{owner}/{repo}/commits/{sha}/status`
- Check runs: `GET /repos/{owner}/{repo}/commits/{sha}/check-runs`
