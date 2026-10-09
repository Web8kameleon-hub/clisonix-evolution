#!/bin/bash
echo "=== GET /api/ocean ==="
curl -s http://localhost:3000/api/ocean | python3 -c "
import json,sys
d=json.load(sys.stdin)
print('features:', d.get('features',[]))
print('mode:', d.get('behavior_profile',{}).get('mode'))
"

echo ""
echo "=== POST /api/ocean (Albanian question) ==="
curl -s --max-time 25 -X POST http://localhost:3000/api/ocean \
  -H 'Content-Type: application/json' \
  -d '{"question":"kush je ti dhe si mund te me ndihmosh"}' \
  | python3 -c "
import json,sys
d=json.load(sys.stdin)
print('keys:', list(d.keys()))
print('reply:', str(d.get('reply',''))[:250])
"

echo ""
echo "=== POST /api/ocean (research trigger: latest AI news) ==="
curl -s --max-time 30 -X POST http://localhost:3000/api/ocean \
  -H 'Content-Type: application/json' \
  -d '{"question":"latest news about AI 2026"}' \
  | python3 -c "
import json,sys
d=json.load(sys.stdin)
print('research:', bool(d.get('research')))
print('decision:', bool(d.get('decision_support')))
print('reply:', str(d.get('reply',''))[:250])
"

echo ""
echo "=== POST /api/ocean (decision trigger: medical) ==="
curl -s --max-time 30 -X POST http://localhost:3000/api/ocean \
  -H 'Content-Type: application/json' \
  -d '{"question":"should I take ibuprofen with this medication"}' \
  | python3 -c "
import json,sys
d=json.load(sys.stdin)
print('research:', bool(d.get('research')))
print('decision:', bool(d.get('decision_support')))
ds = d.get('decision_support',{})
print('situation:', ds.get('situationType','none'))
print('boundaries:', ds.get('boundaries',[])[:2])
"

echo ""
echo "=== GET /api/ocean/personas ==="
curl -s http://localhost:3000/api/ocean/personas \
  | python3 -c "
import json,sys
d=json.load(sys.stdin)
print('capabilities:', d.get('capabilities',{}))
print('personas count:', len(d.get('personas',[])))
"
