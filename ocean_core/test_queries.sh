#!/bin/bash

echo "🧪 Testing Ocean Core 8030 - Multiple Query Types"
echo "=================================================="
echo ""

# Test 1: Laboratory Query
echo "✅ Test 1: Laboratory Query"
curl -s -X POST 'http://localhost:8030/api/query?question=What%20labs%20do%20we%20have' | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'   Intent: {data[\"intent\"]}')
print(f'   Confidence: {data[\"confidence\"]}')
print(f'   Findings: {len(data[\"key_findings\"])} items')
print(f'   Sources: {data[\"sources\"][\"internal\"]}')
"
echo ""

# Test 2: Agent Query
echo "✅ Test 2: Agent Query (ALBA, ALBI)"
curl -s -X POST 'http://localhost:8030/api/query?question=How%20are%20ALBA%20and%20ALBI%20performing' | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'   Intent: {data[\"intent\"]}')
print(f'   Confidence: {data[\"confidence\"]}')
print(f'   Findings: {len(data[\"key_findings\"])} items')
"
echo ""

# Test 3: Knowledge Query
echo "✅ Test 3: Knowledge Query (Consciousness)"
curl -s -X POST 'http://localhost:8030/api/query?question=What%20is%20consciousness' | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'   Intent: {data[\"intent\"]}')
print(f'   Confidence: {data[\"confidence\"]}')
print(f'   External sources used: {data[\"sources\"][\"external\"]}')
"
echo ""

# Test 4: System Query
echo "✅ Test 4: System Query (CPU, Memory)"
curl -s -X POST 'http://localhost:8030/api/query?question=What%20are%20system%20metrics%20and%20CPU%20status' | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'   Intent: {data[\"intent\"]}')
print(f'   Confidence: {data[\"confidence\"]}')
print(f'   Response time: {data[\"processing_time_ms\"]}ms')
"
echo ""
echo "=================================================="
echo "✅ All tests completed!"
