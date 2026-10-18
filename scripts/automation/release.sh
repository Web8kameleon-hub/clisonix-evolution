#!/bin/bash
# Release automatik nga tag.
set -e

cd /opt/clisonix.com

VERSION=${1:-$(date +"v%Y.%m.%d")}
OUTPUT="changelog/releases/$VERSION.md"
mkdir -p "$(dirname "$OUTPUT")"

echo "Krijoj release: $VERSION"

# Measured live, not hardcoded — a stale number here would itself violate
# the no-fake-data policy this script exists to enforce.
SUMMARY=$(python3 -c "
import sys
sys.path.insert(0, '/opt/clisonix.com')
sys.path.insert(0, '/opt/clisonix.com/ocean-core')
lines = []
try:
    from data_sources import get_all_sources, get_statistics
    stats = get_statistics()
    lines.append(f\"- Data sources: {stats['total_sources']} burime reale\")
except Exception as e:
    lines.append(f'- Data sources: E PADISPONUESHME — {e}')
try:
    from repo_indexer import RepoIndexer
    result = RepoIndexer().index()
    lines.append(f\"- Repo index: {result['files']} file, {result['chunks']} chunks, {result['words']} fjalë\")
except Exception as e:
    lines.append(f'- Repo index: E PADISPONUESHME — {e}')
try:
    from albi_core import AlbiCore
    albi = AlbiCore()
    albi.start()
    lines.append(f\"- AlbiCore: {albi.health()['status']}\")
except Exception as e:
    lines.append(f'- AlbiCore: E PADISPONUESHME — {e}')
try:
    from agent_telemetry import TelemetryRouter
    TelemetryRouter()
    lines.append('- TelemetryRouter: OK')
except Exception as e:
    lines.append(f'- TelemetryRouter: E PADISPONUESHME — {e}')
try:
    from ocean_mission_service import ToolRegistry
    ToolRegistry()
    lines.append('- ToolRegistry: OK')
except Exception as e:
    lines.append(f'- ToolRegistry: E PADISPONUESHME — {e}')
print(chr(10).join(lines))
" 2>&1)

cat > "$OUTPUT" << HEADER
# Clisonix Release $VERSION

**Data:** $(date +"%Y-%m-%d")
**Dega:** $(git branch --show-current)
**Commit:** $(git log -1 --format='%h')

---

## Përmbledhje

Ky release përfshin (matur live, jo të fiksuara):

$SUMMARY

**No fake ever.**

---

## Commits që nga release i fundit

HEADER

# Commits që nga tag i fundit
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
if [ -n "$LAST_TAG" ]; then
    git log "$LAST_TAG"..HEAD --pretty=format:"- **%ad** — %s (\`%h\`)" --date=short >> "$OUTPUT"
else
    git log --pretty=format:"- **%ad** — %s (\`%h\`)" --date=short -20 >> "$OUTPUT"
fi
echo "" >> "$OUTPUT"
echo "" >> "$OUTPUT"

# Statistika
echo "## Statistika" >> "$OUTPUT"
echo "" >> "$OUTPUT"
echo "- Files: $(find . -type f -not -path '*/node_modules/*' -not -path '*/.git/*' 2>/dev/null | wc -l)" >> "$OUTPUT"
echo "- Teste: $(find . -name 'test_*.py' -not -path '*/node_modules/*' 2>/dev/null | wc -l)" >> "$OUTPUT"
echo "- Bridges: $(find . -name '*bridge*.py' -not -path '*/node_modules/*' 2>/dev/null | wc -l)" >> "$OUTPUT"

echo "✅ Release u krijua: $OUTPUT"
cat "$OUTPUT"
