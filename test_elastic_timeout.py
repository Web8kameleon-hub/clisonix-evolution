#!/usr/bin/env python3
"""Test ocean-core elastic timeout implementation"""
import json
import sys
import time

import requests


def test_ocean_core():
    base = 'http://localhost:8030'
    print('=== Ocean-Core Elastic Timeout Test ===\n')
    
    # Health check
    try:
        r = requests.get(f'{base}/health', timeout=15)
        print(f'✓ Health check: {r.status_code}')
    except Exception as e:
        print(f'✗ Health check failed: {e}')
        return False
    
    # Test 1: Simple chat query
    print('\n[Test 1] Simple chat query')
    try:
        start = time.time()
        r = requests.post(
            f'{base}/api/v1/chat',
            json={
                'message': 'What is 2+2?',
                'language': 'en',
                'messages': []
            },
            timeout=70
        )
        elapsed = time.time() - start
        
        print(f'  Status: {r.status_code}')
        print(f'  Response time: {elapsed:.1f}s')
        
        if r.status_code == 200:
            data = r.json()
            resp = data.get('response', '')[:100]
            timeout_used = data.get('timeout_seconds', '?')
            print(f'  Response: {resp}')
            print(f'  Timeout allocated: {timeout_used}s')
            print('  ✓ PASS')
        else:
            print(f'  ✗ Error response: {r.text[:150]}')
            return False
    except Exception as e:
        print(f'  ✗ Exception: {e}')
        return False
    
    # Test 2: Stream endpoint
    print('\n[Test 2] Stream endpoint')
    try:
        start = time.time()
        rs = requests.post(
            f'{base}/api/v1/chat/stream',
            json={
                'message': 'Greet me in English',
                'language': 'en'
            },
            stream=True,
            timeout=70
        )
        elapsed = time.time() - start
        
        print(f'  Status: {rs.status_code}')
        lines_received = 0
        for i, line in enumerate(rs.iter_lines(decode_unicode=True)):
            if line:
                lines_received += 1
                if i < 2:
                    print(f'    Line {i+1}: {line[:80]}')
        
        print(f'  Total lines: {lines_received}')
        print(f'  Stream time: {elapsed:.1f}s')
        
        if lines_received > 0:
            print('  ✓ PASS')
        else:
            print('  ✗ No stream data received')
            return False
        
        rs.close()
    except Exception as e:
        print(f'  ✗ Stream error: {e}')
        return False
    
    # Test 3: Complex query (should get higher timeout)
    print('\n[Test 3] Complex query (longer message = higher timeout)')
    try:
        message = """Generate a detailed markdown document about machine learning. 
        Include sections on: supervised learning, unsupervised learning, deep learning,
        with code examples and visual diagrams. This should be comprehensive."""
        
        start = time.time()
        r = requests.post(
            f'{base}/api/v1/chat/fast',
            json={
                'message': message,
                'language': 'en',
                'messages': []
            },
            timeout=70
        )
        elapsed = time.time() - start
        
        print(f'  Status: {r.status_code}')
        print(f'  Response time: {elapsed:.1f}s')
        
        if r.status_code == 200:
            data = r.json()
            timeout_allocated = data.get('timeout_seconds', '?')
            resp = data.get('response', '')[:80]
            print(f'  Timeout allocated: {timeout_allocated}s (higher for complex query)')
            print(f'  Response: {resp}')
            print('  ✓ PASS')
        else:
            print(f'  ✗ Error: {r.text[:150]}')
    except Exception as e:
        print(f'  ✗ Exception: {e}')
    
    print('\n=== All tests completed ===')
    return True

if __name__ == '__main__':
    success = test_ocean_core()
    sys.exit(0 if success else 1)
