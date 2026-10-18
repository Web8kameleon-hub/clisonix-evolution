#!/usr/bin/env bash
set -euo pipefail

REPO="${1:?repo path required}"
GRAM_ID="${2:?gram id required}"
GRAM_TYPE="${3:?gram type required}"

if [ ! -d "$REPO/.git" ]; then
    echo "ERROR: not a git repository: $REPO"
    exit 1
fi

TARGET="$REPO/gram"

if [ -e "$TARGET/manifest.yaml" ]; then
    echo "SKIP: GRAM already configured in $REPO"
    exit 0
fi

mkdir -p "$TARGET"

cat > "$TARGET/manifest.yaml" <<EOF
version: gram-node/v1

gram:
  id: $GRAM_ID
  type: $GRAM_TYPE

  capabilities: []

  signals: []

  discovery:
    health: ""
    status: ""

  federation:
    enabled: true
EOF

cat > "$TARGET/README.md" <<EOF
# GRAM Adapter

GRAM node: $GRAM_ID

Type: $GRAM_TYPE

This repository does not embed GRAM core.

It participates in the shared GRAM fabric through this adapter.
EOF

echo "INSTALLED: $GRAM_ID -> $REPO"
