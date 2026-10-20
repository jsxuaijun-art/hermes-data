#!/bin/bash
# gh-env.sh — Auth detection helper for GitHub workflows
# Source this file at the start of any GitHub operation:
#   source "$(dirname "$0")/gh-env.sh"

detect_github_auth() {
  if command -v gh &>/dev/null && gh auth status &>/dev/null; then
    echo "gh"
  elif [ -n "$GITHUB_TOKEN" ]; then
    echo "token-env"
  elif [ -f ~/.hermes/.env ] && grep -q "^GITHUB_TOKEN=" ~/.hermes/.env; then
    export GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" ~/.hermes/.env | head -1 | cut -d= -f2 | tr -d '\n\r')
    echo "token-dotenv"
  elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
    export GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
    echo "token-git-credentials"
  else
    echo "none"
    return 1
  fi
}

export_github_owner_repo() {
  if [ -z "$REMOTE_URL" ]; then
    REMOTE_URL=$(git remote get-url origin)
  fi
  OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
  export OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
  export REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
}
