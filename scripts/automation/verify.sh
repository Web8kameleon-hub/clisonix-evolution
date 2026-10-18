#!/bin/bash
# Verifikim final — No fake ever.
set -e

cd /opt/clisonix.com

echo "=========================================="
echo "VERIFIKIM FINAL — CLISONIX"
echo "=========================================="
echo ""

# 1. Struktura
echo "=== 1. STRUKTURA ==="
for dir in benchmarks edge-cases changelog wiki stepstones history scripts/automation tests/auto; do
    if [ -d "$dir" ]; then
        echo "✅ $dir"
    else
        echo "❌ $dir — MUNGON"
    fi
done
echo ""

# 2. Git
echo "=== 2. GIT ==="
echo "Dega: $(git branch --show-current)"
echo "Commits: $(git log --oneline | wc -l)"
echo "Tag-e: $(git tag | wc -l)"
echo "Status: $(git status --short | wc -l) files changed"
echo ""

# 3. Data
echo "=== 3. DATA ==="
python3 -c "
import sys
sys.path.insert(0, '/opt/clisonix.com')
from data_sources import get_all_sources, get_statistics
sources = get_all_sources()
stats = get_statistics()
print(f'Data sources: {len(sources)}')
print(f'API sources: {stats[\"api_sources\"]}')
print(f'Countries: {stats[\"countries_covered\"]}')
" 2>/dev/null || echo "❌ Data sources — GABIM"
echo ""

# 4. Index
echo "=== 4. INDEX ==="
python3 -c "
import sys
sys.path.insert(0, '/opt/clisonix.com/ocean-core')
sys.path.insert(0, '/opt/clisonix.com')
from repo_indexer import RepoIndexer
indexer = RepoIndexer()
result = indexer.index()
print(f'Files: {result[\"files\"]}')
print(f'Chunks: {result[\"chunks\"]}')
print(f'Words: {result[\"words\"]}')
" 2>/dev/null || echo "❌ Index — GABIM"
echo ""

# 5. Components
echo "=== 5. COMPONENTS ==="
python3 -c "
import sys
sys.path.insert(0, '/opt/clisonix.com/ocean-core')
sys.path.insert(0, '/opt/clisonix.com')

# AlbiCore
from albi_core import AlbiCore
albi = AlbiCore()
albi.start()
print(f'AlbiCore: {albi.health()[\"status\"]}')

# TelemetryRouter
from agent_telemetry import TelemetryRouter
router = TelemetryRouter()
print(f'TelemetryRouter: OK')

# ToolRegistry
from ocean_mission_service import ToolRegistry
registry = ToolRegistry()
print(f'ToolRegistry: OK')
" 2>/dev/null || echo "❌ Components — GABIM"
echo ""

# 6. No Fake Ever
echo "=== 6. NO FAKE EVER ==="
PLACEHOLDERS=$(grep -rn "placeholder\|TODO\|FIXME\|NotImplementedError" \
    --include="*.py" \
    --exclude-dir=".venv" \
    --exclude-dir="node_modules" \
    --exclude-dir="__pycache__" \
    --exclude-dir="tests" \
    --exclude-dir="test" \
    . 2>/dev/null | grep -v "no fake\|no_fake\|Never produce fake\|Do not output" | wc -l)
echo "Placeholder real: $PLACEHOLDERS"
echo ""

echo "=========================================="
echo "VERIFIKIMI PËRFUNDOI"
echo "=========================================="
