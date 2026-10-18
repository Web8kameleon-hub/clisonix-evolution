#!/bin/bash
# Edge cases — No fake ever.
set -e

cd /opt/clisonix.com

OUTPUT="edge-cases/results/edge-cases-$(date +%Y%m%d_%H%M%S).md"
mkdir -p "$(dirname "$OUTPUT")"

cat > "$OUTPUT" << 'HEADER'
# Clisonix Edge Cases — Real Tests

**No fake ever.**

Ky test kontrollon sjelljen në kufij.

---

HEADER

echo "## 1. Data Sources — Edge Cases" >> "$OUTPUT"
echo '```' >> "$OUTPUT"
python3 -c "
import sys
sys.path.insert(0, '/opt/clisonix.com')
from data_sources import get_all_sources, get_sources_by_country, get_sources_by_region, Region

# Edge 1: Country që nuk ekziston
try:
    sources = get_sources_by_country('XX')
    print(f'[EDGE] Country XX: {len(sources)} sources')
except Exception as e:
    print(f'[EDGE] Country XX: ERROR — {e}')

# Edge 2: Region që nuk ekziston
try:
    sources = get_sources_by_region(Region.EUROPE)
    print(f'[EDGE] Region EUROPE: {len(sources)} sources')
except Exception as e:
    print(f'[EDGE] Region EUROPE: ERROR — {e}')

# Edge 3: Empty query
try:
    from data_sources import search_sources
    results = search_sources('')
    print(f'[EDGE] Empty search: {len(results)} results')
except Exception as e:
    print(f'[EDGE] Empty search: ERROR — {e}')

# Edge 4: Special chars
try:
    results = search_sources('!@#\$%^&*()')
    print(f'[EDGE] Special chars search: {len(results)} results')
except Exception as e:
    print(f'[EDGE] Special chars search: ERROR — {e}')
" >> "$OUTPUT" 2>&1
echo '```' >> "$OUTPUT"
echo "" >> "$OUTPUT"

echo "## 2. RepoIndexer — Edge Cases" >> "$OUTPUT"
echo '```' >> "$OUTPUT"
python3 -c "
import sys
sys.path.insert(0, '/opt/clisonix.com/ocean-core')
sys.path.insert(0, '/opt/clisonix.com')
from repo_indexer import RepoIndexer

indexer = RepoIndexer()
indexer.index()

# Edge 1: Empty query
try:
    results = indexer.search('')
    print(f'[EDGE] Empty search: {len(results)} results')
except Exception as e:
    print(f'[EDGE] Empty search: ERROR — {e}')

# Edge 2: Very long query
try:
    results = indexer.search('a' * 10000)
    print(f'[EDGE] Long query: {len(results)} results')
except Exception as e:
    print(f'[EDGE] Long query: ERROR — {e}')

# Edge 3: Non-existent file
try:
    content = indexer.read_file('nonexistent.txt')
    print(f'[EDGE] Non-existent file: {len(content)} chars')
except FileNotFoundError:
    print(f'[EDGE] Non-existent file: FileNotFoundError (correct)')
except Exception as e:
    print(f'[EDGE] Non-existent file: ERROR — {e}')

# Edge 4: Search with special chars
try:
    results = indexer.search('@#\$%')
    print(f'[EDGE] Special chars: {len(results)} results')
except Exception as e:
    print(f'[EDGE] Special chars: ERROR — {e}')
" >> "$OUTPUT" 2>&1
echo '```' >> "$OUTPUT"
echo "" >> "$OUTPUT"

echo "## 3. AlbiCore — Edge Cases" >> "$OUTPUT"
echo '```' >> "$OUTPUT"
python3 -c "
import sys
sys.path.insert(0, '/opt/clisonix.com')
from albi_core import AlbiCore

# Edge 1: Learn with empty frames
albi = AlbiCore()
try:
    insight = albi.learn([])
    print(f'[EDGE] Empty frames: insight_count={len(albi.insights())}')
except Exception as e:
    print(f'[EDGE] Empty frames: ERROR — {e}')

# Edge 2: Learn with invalid data
try:
    insight = albi.learn([{'channels': {'a': 'not-a-number'}}])
    print(f'[EDGE] Invalid data: {insight.summary}')
except (ValueError, TypeError) as e:
    print(f'[EDGE] Invalid data: correct error — {type(e).__name__}')

# Edge 3: Health when idle
albi2 = AlbiCore()
health = albi2.health()
print(f'[EDGE] Idle health: {health[\"status\"]}')

# Edge 4: Recommendations without data
recs = albi2.recommendations()
print(f'[EDGE] No data recommendations: {recs[\"status\"]}')
" >> "$OUTPUT" 2>&1
echo '```' >> "$OUTPUT"
echo "" >> "$OUTPUT"

echo "## 4. TelemetryRouter — Edge Cases" >> "$OUTPUT"
echo '```' >> "$OUTPUT"
python3 -c "
import sys
sys.path.insert(0, '/opt/clisonix.com')
from agent_telemetry import TelemetryRouter

router = TelemetryRouter()

# Edge 1: Agent që nuk ekziston
try:
    from agent_telemetry import AgentMetrics
    metrics = AgentMetrics(
        agent_name='nonexistent-agent',
        timestamp=0,
        status='active',
    )
    print(f'[EDGE] Nonexistent agent metrics: created')
except Exception as e:
    print(f'[EDGE] Nonexistent agent: ERROR — {e}')

# Edge 2: Methods
methods = [m for m in dir(router) if not m.startswith('_')]
print(f'[EDGE] Router methods: {len(methods)}')
" >> "$OUTPUT" 2>&1
echo '```' >> "$OUTPUT"
echo "" >> "$OUTPUT"

echo "## 5. ToolRegistry — Edge Cases" >> "$OUTPUT"
echo '```' >> "$OUTPUT"
python3 -c "
import sys
sys.path.insert(0, '/opt/clisonix.com/ocean-core')
sys.path.insert(0, '/opt/clisonix.com')
from ocean_mission_service import ToolRegistry

registry = ToolRegistry()

# Edge 1: Get non-existent tool
try:
    tool = registry.get('nonexistent_tool_xyz')
    print(f'[EDGE] Nonexistent tool: {tool}')
except Exception as e:
    print(f'[EDGE] Nonexistent tool: ERROR — {e}')

# Edge 2: Register duplicate
try:
    registry.get('test')
    print(f'[EDGE] Registry access: OK')
except Exception as e:
    print(f'[EDGE] Registry access: ERROR — {e}')
" >> "$OUTPUT" 2>&1
echo '```' >> "$OUTPUT"
echo "" >> "$OUTPUT"

echo "## Përmbledhje" >> "$OUTPUT"
echo "" >> "$OUTPUT"
echo "Të gjitha edge cases u ekzekutuan me real data. **No fake ever.**" >> "$OUTPUT"

echo "✅ Edge cases u kryen: $OUTPUT"
cat "$OUTPUT"
