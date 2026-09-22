# GitHub Pull Request Workflow

Complete guide for managing the PR lifecycle: branch, commit, open, CI, merge.

## 1. Branch Creation

```bash
git fetch origin
git checkout main && git pull origin main
git checkout -b feat/add-user-authentication
```

Branch naming: `feat/`, `fix/`, `refactor/`, `docs/`, `ci/` prefix.

## 2. Committing

```bash
git add src/auth.py tests/test_auth.py
git commit -m "feat: add JWT-based user authentication

- Add login/register endpoints
- Add auth middleware
- Add unit tests"
```

Conventional commit types: `feat`, `fix`, `refactor`, `docs`, `test`, `ci`, `chore`, `perf`.

## 3. Pushing and Creating a PR

```bash
git push -u origin HEAD
```

**With gh:**
```bash
gh pr create --title "feat: ..." --body "## Summary\n..." --label "enhancement"
```

Options: `--draft`, `--reviewer user1,user2`, `--label`, `--base develop`.

**With git + curl:**
```bash
BRANCH=$(git branch --show-current)
curl -s -X POST -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls \
  -d "{\"title\": \"feat: ...\", \"body\": \"## Summary\", \"head\": \"$BRANCH\", \"base\": \"main\"}"
```

## 4. Monitoring CI Status

**With gh:** `gh pr checks` or `gh pr checks --watch`

**With curl:** Poll `${OWNER}/${REPO}/commits/${SHA}/status` and `${SHA}/check-runs`.

**Polling loop:**
```bash
SHA=$(git rev-parse HEAD)
for i in $(seq 1 20); do
  STATUS=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
    https://api.github.com/repos/$OWNER/$REPO/commits/$SHA/status \
    | python3 -c "import sys,json; print(json.load(sys.stdin)['state'])")
  echo "Check $i: $STATUS"
  [ "$STATUS" = "success" ] || [ "$STATUS" = "failure" ] && break
  sleep 30
done
```

## 5. Auto-Fixing CI Failures

1. Get failure details: `gh run list --branch $(git branch --show-current) --limit 5` then `gh run view <RUN_ID> --log-failed`
2. Fix and push: `git add <files> && git commit -m "fix: ..." && git push`
3. Re-check CI. Repeat up to 3 attempts, then ask user.

## 6. Merging

**With gh:** `gh pr merge --squash --delete-branch`
**With curl:** `PUT /repos/{owner}/{repo}/pulls/{number}/merge {"merge_method": "squash"}`

Merge methods: `squash` (cleanest for feature branches), `merge` (merge commit), `rebase`.

After merge: `git checkout main && git pull && git branch -D <branch>`

### Auto-Merge (gh)
`gh pr merge --auto --squash --delete-branch`

## 7. PR Command Reference

| Action | gh | curl |
|--------|-----|------|
| List my PRs | `gh pr list --author @me` | `GET /repos/{o}/{r}/pulls` |
| View PR diff | `gh pr diff` | `git diff main...HEAD` (local) |
| Add comment | `gh pr comment N --body "..."` | `POST /repos/{o}/{r}/issues/N/comments` |
| Request review | `gh pr edit N --add-reviewer user` | `POST /repos/{o}/{r}/pulls/N/requested_reviewers` |
| Close PR | `gh pr close N` | `PATCH /repos/{o}/{r}/pulls/N {"state":"closed"}` |
| Check out someone's PR | `gh pr checkout N` | `git fetch origin pull/N/head:pr-N && git checkout pr-N` |
