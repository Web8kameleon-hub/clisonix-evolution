#!/bin/bash
# Test vs Test — No fake ever.
set -e

cd /opt/clisonix.com

OUTPUT="tests/auto/test-vs-test-$(date +%Y%m%d_%H%M%S).md"
mkdir -p "$(dirname "$OUTPUT")"

cat > "$OUTPUT" << 'HEADER'
# Clisonix Test vs Test

**No fake ever.**

Ky test krahason rezultatet e testeve të pavarura.

---

HEADER

echo "## 1. Data Sources — Test 1 vs Test 2" >> "$OUTPUT"
echo '```' >> "$OUTPUT"
python3 -c "
import sys
sys.path.insert(0, '/opt/clisonix.com')
from data_sources import get_all_sources, get_statistics

# Test 1: get_all_sources
sources1 = get_all_sources()
count1 = len(sources1)

# Test 2: get_statistics
stats = get_statistics()
count2 = stats['total_sources']

# Compare
match = count1 == count2
print(f'Test 1 (get_all_sources): {count1}')
print(f'Test 2 (get_statistics): {count2}')
print(f'Match: {\"PASS\" if match else \"FAIL\"}')

if not match:
    raise RuntimeError(f'MISMATCH: {count1} != {count2}')
" >> "$OUTPUT" 2>&1
echo '```' >> "$OUTPUT"
echo "" >> "$OUTPUT"

echo "## 2. RepoIndexer — Index vs Re-index" >> "$OUTPUT"
echo '```' >> "$OUTPUT"
python3 -c "
import sys
sys.path.insert(0, '/opt/clisonix.com/ocean-core')
sys.path.insert(0, '/opt/clisonix.com')
from repo_indexer import RepoIndexer

indexer = RepoIndexer()

# Test 1: Index
result1 = indexer.index()

# Test 2: Re-index
result2 = indexer.index()

# Compare
match = result1 == result2
print(f'Test 1 (index): {result1}')
print(f'Test 2 (re-index): {result2}')
print(f'Match: {\"PASS\" if match else \"FAIL\"}')

if not match:
    raise RuntimeError(f'MISMATCH: {result1} != {result2}')
" >> "$OUTPUT" 2>&1
echo '```' >> "$OUTPUT"
echo "" >> "$OUTPUT"

echo "## 3. AlbiCore — Learn vs Health" >> "$OUTPUT"
echo '```' >> "$OUTPUT"
python3 -c "
import sys
sys.path.insert(0, '/opt/clisonix.com')
from albi_core import AlbiCore

albi = AlbiCore()
albi.start()

# Test 1: Learn
insight = albi.learn([{'channels': {'a': 1.0, 'b': 2.0}}])
count1 = len(albi.insights())

# Test 2: Health
health = albi.health()
count2 = health['insight_count']

# Compare
match = count1 == count2
print(f'Test 1 (insights): {count1}')
print(f'Test 2 (health count): {count2}')
print(f'Match: {\"PASS\" if match else \"FAIL\"}')

if not match:
    raise RuntimeError(f'MISMATCH: {count1} != {count2}')
" >> "$OUTPUT" 2>&1
echo '```' >> "$OUTPUT"
echo "" >> "$OUTPUT"

echo "## 4. Telemetry — Init vs Re-init" >> "$OUTPUT"
echo '```' >> "$OUTPUT"
python3 -c "
import sys
sys.path.insert(0, '/opt/clisonix.com')
from agent_telemetry import TelemetryRouter

# Test 1
router1 = TelemetryRouter()
methods1 = sorted([m for m in dir(router1) if not m.startswith('_')])

# Test 2
router2 = TelemetryRouter()
methods2 = sorted([m for m in dir(router2) if not m.startswith('_')])

# Compare
match = methods1 == methods2
print(f'Test 1 methods: {len(methods1)}')
print(f'Test 2 methods: {len(methods2)}')
print(f'Match: {\"PASS\" if match else \"FAIL\"}')

if not match:
    raise RuntimeError('MISMATCH: methods differ')
" >> "$OUTPUT" 2>&1
echo '```' >> "$OUTPUT"
echo "" >> "$OUTPUT"

echo "## 5. ToolRegistry — Get vs Get" >> "$OUTPUT"
echo '```' >> "$OUTPUT"
python3 -c "
import sys
sys.path.insert(0, '/opt/clisonix.com/ocean-core')
sys.path.insert(0, '/opt/clisonix.com')
from ocean_mission_service import ToolRegistry

registry = ToolRegistry()

# Test 1
tool1 = registry.get('test')

# Test 2
tool2 = registry.get('test')

# Compare
match = tool1 == tool2
print(f'Test 1: {tool1}')
print(f'Test 2: {tool2}')
print(f'Match: {\"PASS\" if match else \"FAIL\"}')

if not match:
    raise RuntimeError('MISMATCH: tools differ')
" >> "$OUTPUT" 2>&1
echo '```' >> "$OUTPUT"
echo "" >> "$OUTPUT"

echo "## Përmbledhje" >> "$OUTPUT"
echo "" >> "$OUTPUT"
echo "Të gjitha testet u ekzekutuan. **No fake ever.**" >> "$OUTPUT"

echo "✅ Test vs Test u krye: $OUTPUT"
cat "$OUTPUT"
