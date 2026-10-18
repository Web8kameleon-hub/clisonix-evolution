#!/bin/bash
# Commit automatik — No fake ever.
set -e

cd /opt/clisonix.com

# 1. Kontrollo ndryshimet
CHANGES=$(git status --short | wc -l)
if [ "$CHANGES" -eq 0 ]; then
    echo "Nuk ka ndryshime për commit"
    exit 0
fi

# 2. Gjenero mesazhin
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
FILES=$(git status --short | head -20)

# 3. Commit
git add -A
git commit -m "auto: $TIMESTAMP

Changed files: $CHANGES

$FILES

No fake ever." || echo "Nuk ka ndryshime për commit"

echo "✅ Commit u krye"
git log -1 --oneline
