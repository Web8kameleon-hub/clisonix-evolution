#!/usr/bin/env bash
# Preview-or-execute helper for preparing replacements and showing git-filter-repo / BFG commands.
# This script does NOT perform destructive changes unless called with --execute.

set -euo pipefail

ROOT_DIR="$(dirname "${BASH_SOURCE[0]}")"
REPLACEMENTS="$ROOT_DIR/replacements.txt"

cat > "$REPLACEMENTS" <<'REPL'
# Replace common provider token patterns (review before executing)
# Format: literal==>REDACTED
# Example: sk_live_123abc==>REDACTED
sk_live_==>REDACTED
sk_test_==>REDACTED
pk_live_==>REDACTED
pk_test_==>REDACTED
whsec_==>REDACTED
PMAK-==>REDACTED
github_pat_==>REDACTED
linkedin_==>REDACTED
EA-==>REDACTED
REPL

echo "Prepared replacements template at: $REPLACEMENTS"

echo
echo "Preview: Commands to run (DO NOT RUN unless you are ready):"
cat <<'CMDS'
# Using git-filter-repo (recommended)
git clone --mirror <repo-url> repo-mirror.git
cd repo-mirror.git
git filter-repo --replace-text ../scripts/replacements.txt
git push --force

# Using BFG (alternate)
bfg --replace-text ../scripts/replacements.txt repo.git
cd repo.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force
CMDS

if [[ "${1-}" == "--execute" ]]; then
  echo "--execute passed. Aborting automatic execution for safety. Run the git-filter-repo command above manually after reviewing replacements.txt."
  exit 1
fi

echo "Done. Review $REPLACEMENTS before executing any history-rewrite command."
