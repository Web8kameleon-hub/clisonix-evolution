#!/bin/bash
# Changelog automatik nga git log.
set -e

cd /opt/clisonix.com

OUTPUT="changelog/CHANGELOG-AUTO.md"
mkdir -p "$(dirname "$OUTPUT")"

# Header
cat > "$OUTPUT" << 'HEADER'
# Clisonix Changelog — Auto-Generated

**No fake ever.**

Ky changelog gjenerohet automatikisht nga git log.

---

HEADER

# 1. Commits nga 2026
echo "## 2026" >> "$OUTPUT"
echo "" >> "$OUTPUT"
git log --since="2026-01-01" --pretty=format:"- **%ad** — %s (\`%h\`)" --date=short >> "$OUTPUT" 2>/dev/null || echo "Nuk ka commits" >> "$OUTPUT"
echo "" >> "$OUTPUT"
echo "" >> "$OUTPUT"

# 2. Commits nga 2025
echo "## 2025" >> "$OUTPUT"
echo "" >> "$OUTPUT"
git log --since="2025-01-01" --until="2025-12-31" --pretty=format:"- **%ad** — %s (\`%h\`)" --date=short >> "$OUTPUT" 2>/dev/null || echo "Nuk ka commits" >> "$OUTPUT"
echo "" >> "$OUTPUT"
echo "" >> "$OUTPUT"

# 3. Commits nga 2024
echo "## 2024" >> "$OUTPUT"
echo "" >> "$OUTPUT"
git log --since="2024-01-01" --until="2024-12-31" --pretty=format:"- **%ad** — %s (\`%h\`)" --date=short >> "$OUTPUT" 2>/dev/null || echo "Nuk ka commits" >> "$OUTPUT"
echo "" >> "$OUTPUT"
echo "" >> "$OUTPUT"

# 4. Statistika
echo "## Statistika" >> "$OUTPUT"
echo "" >> "$OUTPUT"
TOTAL=$(git log --oneline | wc -l)
echo "- Total commits: $TOTAL" >> "$OUTPUT"
echo "- Autorë: $(git log --format='%an' | sort -u | wc -l)" >> "$OUTPUT"
echo "- Dega: $(git branch --show-current)" >> "$OUTPUT"
echo "- Last commit: $(git log -1 --format='%ad %s' --date=short)" >> "$OUTPUT"

echo "✅ Changelog u krijua: $OUTPUT"
wc -l "$OUTPUT"
