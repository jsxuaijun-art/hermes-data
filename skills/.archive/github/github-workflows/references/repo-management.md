# GitHub Repository Management

Create, clone, fork, configure, and manage repositories.

## 1. Cloning

```bash
git clone https://github.com/owner/repo-name.git
git clone --depth 1 https://github.com/owner/repo.git        # shallow
git clone --branch develop https://github.com/owner/repo.git # specific branch
```

**Shortcut:** `gh repo clone owner/repo-name`

## 2. Creating Repositories

**With gh:**
```bash
gh repo create my-new-project --public --clone
gh repo create my-org/my-project --public --clone
gh repo create my-project --source . --public --push          # from existing local dir
```

**With curl:**
```bash
curl -s -X POST -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user/repos \
  -d '{"name": "my-new-project", "private": false, "auto_init": true}'
```

## 3. Forking

**With gh:** `gh repo fork owner/repo-name --clone`

**With git + curl:** POST `/repos/{owner}/{repo}/forks`, then `git clone`, then `git remote add upstream https://github.com/owner/repo.git`

**Sync fork:** `git fetch upstream && git merge upstream/main && git push origin main`

## 4. Repository Information

**With gh:**
```bash
gh repo view owner/repo-name
gh repo list --limit 20
gh search repos "machine learning" --language python --sort stars
```

## 5. Repository Settings

**With gh:** `gh repo edit --description "..." --visibility public`
**With curl:** `PATCH /repos/{owner}/{repo}`

## 6. Branch Protection

```bash
curl -s -X PUT -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/branches/main/protection \
  -d '{"required_status_checks": {"strict": true, "contexts": ["ci/test", "ci/lint"]}, "enforce_admins": false, "required_pull_request_reviews": {"required_approving_review_count": 1}, "restrictions": null}'
```

## 7. Secrets Management (Actions)

**With gh:** `gh secret set API_KEY --body "your-secret-value"`
**With curl:** Requires encrypting with repo's public key (see `references/github-api-cheatsheet.md`).

## 8. Releases

**With gh:**
```bash
gh release create v1.0.0 --title "v1.0.0" --generate-notes
gh release create v1.0.0 ./dist/binary --title "v1.0.0"
gh release list
gh release download v1.0.0 --dir ./downloads
```

## 9. Actions Workflows

**With gh:**
```bash
gh workflow list
gh run list --limit 10
gh run view <RUN_ID>
gh run rerun <RUN_ID>
gh workflow run ci.yml --ref main
```

## 10. Gists

**With gh:** `gh gist create script.py --public --desc "Useful script"`
**With curl:** `POST /gists`

## Quick Reference

| Action | gh |
|--------|-----|
| Clone | `gh repo clone owner/repo` |
| Create | `gh repo create name --public` |
| Fork | `gh repo fork owner/repo --clone` |
| View | `gh repo view owner/repo` |
| Edit | `gh repo edit --description "..."` |
| Release | `gh release create v1.0.0` |
| List workflows | `gh workflow list` |
| Rerun CI | `gh run rerun ID` |
| Set secret | `gh secret set KEY --body "val"` |
