#!/usr/bin/env bash
set -euo pipefail

# Auto chain: commit -> push -> remote pull -> full rebuild -> unhealthy report
# Usage:
#   scripts/auto_sync_hetzner.sh "your commit message"
# Env overrides:
#   REMOTE_HOST=hetzner-new
#   REMOTE_DIR=/root/Clisonix-cloud
#   BRANCH=main
#   COMPOSE_FILE=docker-compose.yml

REMOTE_HOST="${REMOTE_HOST:-hetzner-new}"
REMOTE_DIR="${REMOTE_DIR:-/root/Clisonix-cloud}"
CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo main)"
BRANCH="${BRANCH:-$CURRENT_BRANCH}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
ENV_FILE="${ENV_FILE:-.env}"
export GIT_SSH_COMMAND="${GIT_SSH_COMMAND:-ssh -o StrictHostKeyChecking=accept-new}"

if ! command -v git >/dev/null 2>&1; then
  echo "❌ git is required"
  exit 1
fi

if ! command -v ssh >/dev/null 2>&1; then
  echo "❌ ssh is required"
  exit 1
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "❌ run this script from inside the repository"
  exit 1
fi

COMMIT_MESSAGE="${1:-auto: sync and rebuild}"

CHANGED_FILES="$(git status --porcelain 2>/dev/null || true)"
if [[ -n "$CHANGED_FILES" ]]; then
  echo "📝 Staging and committing local changes..."
  git add -A 2>/dev/null || true
  git commit -m "$COMMIT_MESSAGE"
else
  echo "ℹ️ No local changes to commit. Continuing with push/deploy."
fi

if ! git ls-remote origin -h >/dev/null 2>&1; then
  echo "❌ GitHub authentication is not configured for this machine."
  echo "   Add this public key to GitHub (SSH keys or repo deploy key with write access):"
  echo "   $HOME/.ssh/hetzner-deploy.pub"
  echo "   Then re-run this script."
  exit 1
fi

echo "⬆️ Pushing to origin/$BRANCH..."
git push origin "$BRANCH"

echo "🚀 Running remote sync + full rebuild on $REMOTE_HOST..."
echo "ℹ️ Target: branch=$BRANCH dir=$REMOTE_DIR compose=$COMPOSE_FILE env=$ENV_FILE"
ssh "$REMOTE_HOST" "set -euo pipefail; \
  mkdir -p '$REMOTE_DIR'; \
  cd '$REMOTE_DIR'; \
  echo '--- Extra deployment directories on remote ---'; \
  for d in /root/Clisonix-cloud /root/clisonix-cloud /opt/clisonix /opt/clisonix-cloud; do \
    if [ -d \"\$d\" ] && [ \"\$d\" != '$REMOTE_DIR' ]; then echo \"warn:\$d\"; fi; \
  done; \
  git fetch origin '$BRANCH'; \
  git checkout '$BRANCH' 2>/dev/null || git checkout -b '$BRANCH' 'origin/$BRANCH'; \
  git reset --hard 'origin/$BRANCH'; \
  test -f '$ENV_FILE' && echo 'env_file_present=yes' || echo 'env_file_present=no'; \
  export CLISONIX_ENV_FILE='$ENV_FILE'; \
  docker compose -f '$COMPOSE_FILE' config >/dev/null; \
  docker compose -f '$COMPOSE_FILE' up -d --build --remove-orphans; \
  docker compose -f '$COMPOSE_FILE' restart nginx; \
  echo '--- Unhealthy containers (if any) ---'; \
  docker ps --filter 'health=unhealthy' --format '{{.Names}}\\t{{.Status}}'"

UNHEALTHY_OUTPUT="$(ssh "$REMOTE_HOST" "docker ps --filter 'health=unhealthy' --format '{{.Names}}'")"
if [[ -n "$UNHEALTHY_OUTPUT" ]]; then
  echo "❌ Deployment completed but unhealthy containers remain:"
  echo "$UNHEALTHY_OUTPUT"
  exit 2
fi

echo "✅ Auto sync completed: commit/push/rebuild finished and no unhealthy containers detected."
