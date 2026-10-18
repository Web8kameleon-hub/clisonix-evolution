#!/bin/bash
# Benchmarks reale — No fake ever.
set -e

cd /opt/clisonix.com

OUTPUT="benchmarks/results/benchmark-$(date +%Y%m%d_%H%M%S).md"
mkdir -p "$(dirname "$OUTPUT")"

cat > "$OUTPUT" << 'HEADER'
# Clisonix Benchmarks — Real Results

**No fake ever.**

Ky benchmark mat performancën reale të sistemeve.

---

HEADER

echo "## 1. Data Sources" >> "$OUTPUT"
echo '```' >> "$OUTPUT"
python3 -c "
import sys, time
sys.path.insert(0, '/opt/clisonix.com')
from data_sources import get_all_sources, get_statistics

start = time.time()
all_sources = get_all_sources()
load_time = (time.time() - start) * 1000

start = time.time()
stats = get_statistics()
stats_time = (time.time() - start) * 1000

print(f'Total sources: {len(all_sources)}')
print(f'API sources: {stats[\"api_sources\"]}')
print(f'Countries: {stats[\"countries_covered\"]}')
print(f'Load time: {load_time:.2f}ms')
print(f'Stats time: {stats_time:.2f}ms')
" >> "$OUTPUT" 2>&1
echo '```' >> "$OUTPUT"
echo "" >> "$OUTPUT"

echo "## 2. Repo Indexer" >> "$OUTPUT"
echo '```' >> "$OUTPUT"
python3 -c "
import sys, time
sys.path.insert(0, '/opt/clisonix.com/ocean-core')
sys.path.insert(0, '/opt/clisonix.com')
from repo_indexer import RepoIndexer

start = time.time()
indexer = RepoIndexer()
result = indexer.index()
index_time = (time.time() - start) * 1000

start = time.time()
results = indexer.search('clisonix', limit=20)
search_time = (time.time() - start) * 1000

print(f'Files: {result[\"files\"]}')
print(f'Chunks: {result[\"chunks\"]}')
print(f'Words: {result[\"words\"]}')
print(f'Index time: {index_time:.2f}ms')
print(f'Search time: {search_time:.2f}ms')
print(f'Search results: {len(results)}')
" >> "$OUTPUT" 2>&1
echo '```' >> "$OUTPUT"
echo "" >> "$OUTPUT"

echo "## 3. AlbiCore" >> "$OUTPUT"
echo '```' >> "$OUTPUT"
python3 -c "
import sys, time
sys.path.insert(0, '/opt/clisonix.com')
from albi_core import AlbiCore

start = time.time()
albi = AlbiCore()
albi.start()
start_time = (time.time() - start) * 1000

frames = [{'channels': {'alpha': 0.5 + i*0.01, 'beta': 0.8 + i*0.01}} for i in range(1000)]

start = time.time()
insight = albi.learn(frames)
learn_time = (time.time() - start) * 1000

health = albi.health()
print(f'Status: {health[\"status\"]}')
print(f'Start time: {start_time:.2f}ms')
print(f'Learn 1000 frames: {learn_time:.2f}ms')
print(f'Insight count: {health[\"insight_count\"]}')
" >> "$OUTPUT" 2>&1
echo '```' >> "$OUTPUT"
echo "" >> "$OUTPUT"

echo "## 4. TelemetryRouter" >> "$OUTPUT"
echo '```' >> "$OUTPUT"
python3 -c "
import sys, time
sys.path.insert(0, '/opt/clisonix.com')
from agent_telemetry import TelemetryRouter

start = time.time()
router = TelemetryRouter()
init_time = (time.time() - start) * 1000

print(f'Init time: {init_time:.2f}ms')
print(f'Methods: {len([m for m in dir(router) if not m.startswith(\"_\")])}')
" >> "$OUTPUT" 2>&1
echo '```' >> "$OUTPUT"
echo "" >> "$OUTPUT"

echo "## 5. ToolRegistry" >> "$OUTPUT"
echo '```' >> "$OUTPUT"
python3 -c "
import sys, time
sys.path.insert(0, '/opt/clisonix.com/ocean-core')
sys.path.insert(0, '/opt/clisonix.com')
from ocean_mission_service import ToolRegistry

start = time.time()
registry = ToolRegistry()
init_time = (time.time() - start) * 1000

print(f'Init time: {init_time:.2f}ms')
print(f'Methods: {len([m for m in dir(registry) if not m.startswith(\"_\")])}')
" >> "$OUTPUT" 2>&1
echo '```' >> "$OUTPUT"
echo "" >> "$OUTPUT"

echo "## 6. System" >> "$OUTPUT"
echo '```' >> "$OUTPUT"
echo "Python: $(python3 --version)" >> "$OUTPUT"
echo "CPU: $(nproc) cores" >> "$OUTPUT"
echo "Memory: $(free -h | grep Mem | awk '{print $2}')" >> "$OUTPUT"
echo "Disk: $(df -h /opt | tail -1 | awk '{print $2 " total, " $4 " free"}')" >> "$OUTPUT"
echo '```' >> "$OUTPUT"

echo "✅ Benchmarks u kryen: $OUTPUT"
cat "$OUTPUT"
