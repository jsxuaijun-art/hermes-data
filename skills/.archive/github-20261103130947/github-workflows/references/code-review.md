# GitHub Code Review

Perform code reviews on local changes before pushing, or review open PRs on GitHub.

## 1. Reviewing Local Changes (Pre-Push)

```bash
# Overview
git diff main...HEAD --stat
git log main..HEAD --oneline

# Full diff
git diff main...HEAD

# File-by-file
git diff main...HEAD -- src/auth/login.py

# Check for common issues
git diff main...HEAD | grep -n "print(\|console\.log\|TODO\|FIXME\|HACK\|debugger"
git diff main...HEAD --stat | sort -t'|' -k2 -rn | head -10
git diff main...HEAD | grep -in "password\|secret\|api_key\|token.*=\|private_key"
git diff main...HEAD | grep -n "<<<<<<\|>>>>>>\|======="
```

## 2. Reviewing a Pull Request

**With gh:**
```bash
gh pr view 123
gh pr diff 123
gh pr diff 123 --name-only
gh pr checkout 123
```

**With git + curl:**
```bash
git fetch origin pull/123/head:pr-123
git checkout pr-123
# Now read_file, search_files, run tests
git diff main...pr-123
```

## 3. Posting Inline Reviews

**Single inline comment — with gh (via API):**
```bash
HEAD_SHA=$(gh pr view 123 --json headRefOid --jq '.headRefOid')
gh api repos/$OWNER/$REPO/pulls/123/comments \
  --method POST \
  -f body="Use parameterized queries here." \
  -f path="src/auth/login.py" \
  -f commit_id="[\"HEAD_SHA\"] \
  -f line=45 \
  -f side="RIGHT"
```

**Submit formal review:**
```bash
gh pr review 123 --approve --body "LGTM!"
gh pr review 123 --request-changes --body "See inline comments."
gh pr review 123 --comment --body "Some suggestions."
```

**With curl — atomic multi-comment review:**
```bash
HEAD_SHA=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['head']['sha'])")

curl -s -X POST -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/reviews \
  -d "{\"commit_id\": \"[\"HEAD_SHA]\", \"event\": \"COMMENT\", \"body\": \"Review from Hermes\", \"comments\": [{\"path\": \"src/auth.py\", \"line\": 45, \"body\": \"Critical: SQL injection risk.\"}]}"
```

Event values: `"APPROVE"`, `"REQUEST_CHANGES"`, `"COMMENT"`.

## 4. Review Checklist

### Correctness
- Does the code do what it claims?
- Edge cases (empty, null, large data, concurrent access)?
- Error paths handled gracefully?

### Security
- No hardcoded secrets or API keys
- Input validation on user inputs
- No SQL injection, XSS, path traversal
- Auth/authz checks where needed

### Code Quality
- Clear naming
- No unnecessary complexity or premature abstraction
- DRY — no duplicated logic
- Focused functions (single responsibility)

### Testing
- New code paths tested?
- Happy path AND error cases covered?
- Tests readable and maintainable?

### Performance
- No N+1 queries or unnecessary loops
- Appropriate caching
- No blocking in async code paths

### Documentation
- Public APIs documented
- Non-obvious logic has "why" comments
- README updated if behavior changed

## 5. Post-Review Cleanup

```bash
git checkout main
git branch -D pr-$PR_NUMBER
```
