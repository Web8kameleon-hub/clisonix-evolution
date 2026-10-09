#!/usr/bin/env bash
set -euo pipefail

# One-command local ship helper.
# Default behavior:
# 1) commit all staged/unstaged changes
# 2) push to main
# 3) rely on GitHub Actions chain: CI green -> auto deploy

MESSAGE="${1:-chore: automated ship}"
BRANCH="${BRANCH:-main}"
NO_COMMIT="${NO_COMMIT:-0}"
NO_PUSH="${NO_PUSH:-0}"

step() {
  printf "\n==> %s\n" "$1"
}

step "Checking git repository"
git rev-parse --is-inside-work-tree >/dev/null

if [[ "$NO_COMMIT" != "1" ]]; then
  if [[ -n "$(git status --porcelain)" ]]; then
    step "Creating commit"
    git add -A
    git commit -m "$MESSAGE"
  else
    echo "No local changes to commit."
  fi
fi

if [[ "$NO_PUSH" != "1" ]]; then
  step "Pushing branch $BRANCH"
  git push origin "$BRANCH"
fi

step "Done"
echo "Automation chain active: push -> CI green -> auto deploy"
