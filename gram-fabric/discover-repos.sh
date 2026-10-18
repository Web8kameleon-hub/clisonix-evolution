#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-$HOME}"

echo "GRAM ECOSYSTEM DISCOVERY"
echo "root=$ROOT"
echo

find "$ROOT" \
  -maxdepth 4 \
  -type d \
  -name .git \
  2>/dev/null |
while read -r gitdir; do

    repo="$(dirname "$gitdir")"

    origin="$(
      git -C "$repo" remote get-url origin 2>/dev/null || true
    )"

    branch="$(
      git -C "$repo" branch --show-current 2>/dev/null || true
    )"

    printf '%s\t%s\t%s\n' \
      "$repo" \
      "$branch" \
      "$origin"
done
