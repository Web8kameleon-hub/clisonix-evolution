#!/usr/bin/env python3
"""Quick test script for Ocean Orchestrator"""
import sys

sys.path.insert(0, '.')

print('=' * 60)
print('OCEAN ORCHESTRATOR - UNIT TESTS')
print('=' * 60)
print()

# Test 1: Import
print('[1/6] Import modules...', end=' ')
try:
    from ocean_orchestrator import SERVICES, HealthChecker, IntentRouter, ServiceConfig
    print('✅ PASS')
except Exception as e:
    print(f'❌ FAIL: {e}')
    sys.exit(1)

# Test 2: ServiceConfig
print('[2/6] ServiceConfig defaults...', end=' ')
svc = ServiceConfig(name='Test', host='localhost', port=8080)
assert svc.timeout == 30.0, 'Bad timeout'
assert svc.is_healthy == False, 'Bad is_healthy'
assert svc.health_path == '/health', 'Bad health_path'
print('✅ PASS')

# Test 3: IntentRouter
print('[3/6] IntentRouter routing...', end=' ')
router = IntentRouter(SERVICES)
r1 = router.route('analyze brain eeg signals')
r2 = router.route('what is the weather today')
r3 = router.route('random question')
assert 'alba' in r1, f'EEG should route to alba, got {r1}'
assert r3 == ['ollama'], f'Unknown should route to ollama, got {r3}'
print('✅ PASS')

# Test 4: No forbidden patterns
print('[4/6] No forbidden patterns...', end=' ')
import inspect

import ocean_orchestrator

source = inspect.getsource(ocean_orchestrator)
forbidden = [
    'keep_alive": -1',
    "'keep_alive': -1",
    'num_predict": 4096',
]
for pattern in forbidden:
    if pattern in source:
        print(f'❌ FAIL: Found forbidden pattern')
        sys.exit(1)
print('✅ PASS')

# Test 5: Limited iterations
print('[5/6] Health checker has max_iterations...', end=' ')
src = inspect.getsource(ocean_orchestrator.HealthChecker.run_background_checks)
assert 'max_iterations' in src, 'No max_iterations!'
assert 'while iteration < max_iterations' in src, 'Not limited loop!'
print('✅ PASS')

# Test 6: Services configured
print('[6/6] Services registered...', end=' ')
assert len(SERVICES) >= 5, f'Too few services: {len(SERVICES)}'
assert 'ollama' in SERVICES, 'Missing ollama'
assert 'alba' in SERVICES, 'Missing alba'
print(f'✅ PASS ({len(SERVICES)} services)')

print()
print('=' * 60)
print('ALL TESTS PASSED! ✅')
print('=' * 60)
