# GitHub Issues Management

Create, search, triage, and manage GitHub issues. Each section shows `gh` first, then the `curl` fallback.

## Prerequisites

- Authenticated with GitHub (see `references/github-auth.md`)
- Inside a git repo with a GitHub remote, or specify the repo explicitly

## 1. Viewing Issues

**With gh:**
```bash
gh issue list
gh issue list --state open --label "bug"
gh issue list --assignee @me
gh issue list --search "authentication error" --state all
gh issue view 42
```

**With curl:**
```bash
# List open issues
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/issues?state=open&per_page=20" \
  | python3 -c "
import sys, json
for i in json.load(sys.stdin):
    if 'pull_request' not in i:
        labels = ', '.join(l['name'] for l in i['labels'])
        print(f'#{i[\"number\"]:5}  {i[\"state\"]:6}  {labels:30}  {i[\"title\"]}')"

# View a specific issue
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/issues/42 \
  | python3 -c "
import sys, json
i = json.load(sys.stdin)
labels = ', '.join(l['name'] for l in i['labels'])
assignees = ', '.join(a['login'] for a in i['assignees'])
print(f'#{i[\"number\"]}: {i[\"title\"]}')
print(f'State: {i[\"state\"]}  Labels: {labels}  Assignees: {assignees}')
print(f'Author: {i[\"user\"][\"login\"]}  Created: {i[\"created_at\"]}')
print(f'\n{i[\"body\"]}')"
```

## 2. Creating Issues

**With gh:**
```bash
gh issue create \
  --title "Login redirect ignores ?next= parameter" \
  --body "## Description\nAfter logging in, users always land on /dashboard.\n\n## Steps to Reproduce\n1. Navigate to /settings while logged out\n2. Get redirected to /login?next=/settings\n3. Log in\n4. Actual: redirected to /dashboard (should go to /settings)\n\n## Expected Behavior\nRespect the ?next= query parameter." \
  --label "bug,backend" \
  --assignee "username"
```

**With curl:**
```bash
curl -s -X POST -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/issues \
  -d '{"title": "Login redirect ignores ?next= parameter", "body": "## Description\nAfter logging in, users always land on /dashboard.\n\n## Steps to Reproduce\n1. ...", "labels": ["bug", "backend"], "assignees": ["username"]}'
```

## 3. Managing Issues

Add labels: `gh issue edit 42 --add-label "priority:high,bug"` or `POST /repos/{o}/{r}/issues/42/labels`
Assign: `gh issue edit 42 --add-assignee username` or `POST /repos/{o}/{r}/issues/42/assignees`
Comment: `gh issue comment 42 --body "..."` or `POST /repos/{o}/{r}/issues/42/comments`
Close: `gh issue close 42` or `PATCH /repos/{o}/{r}/issues/42 {"state": "closed"}`
Reopen: `gh issue reopen 42` or `PATCH /repos/{o}/{r}/issues/42 {"state": "open"}`

## 4. Issue Triage Workflow

1. List untriaged: `gh issue list --label "needs-triage" --state open`
2. Read and categorize each issue
3. Apply labels and priority
4. Assign if owner is clear
5. Comment with triage notes

## 5. Bulk Operations

```bash
# Close all issues with a specific label
gh issue list --label "wontfix" --json number --jq '.[].number' | \
  xargs -I {} gh issue close {} --reason "not planned"
```

## Issue Templates

See `templates/bug-report.md` and `templates/feature-request.md` in this skill.
