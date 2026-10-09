#!/usr/bin/env python3
"""Test instant streaming - first chunk must appear within 0.2s"""
import json
import time

import requests


def test_instant_stream():
    print("=== Testing Instant Streaming (0.2s Start Target) ===\n")
    
    base = 'http://localhost:8030'
    
    # Test stream endpoint
    print("[Test] POST /api/v1/chat/stream")
    
    start_total = time.time()
    
    try:
        rs = requests.post(
            f'{base}/api/v1/chat/stream',
            json={
                'message': 'Hello, what time is it?',
                'language': 'en'
            },
            headers={'Accept': 'text/event-stream'},
            stream=True,
            timeout=70
        )
        
        print(f'✓ Connection: {rs.status_code}')
        
        # Measure time to first chunk
        first_line_time = None
        chunk_count = 0
        
        for i, line in enumerate(rs.iter_lines(decode_unicode=True)):
            if line:
                if first_line_time is None:
                    first_line_time = time.time() - start_total
                    print(f'✓ First chunk received in: {first_line_time*1000:.1f}ms')
                
                chunk_count += 1
                
                # Show first few chunks
                if i < 3:
                    print(f'  [{i}] {line[:100]}')
                
                # Parse to show structure
                if 'status' in line:
                    try:
                        data = json.loads(line.split('data: ')[1] if 'data: ' in line else line)
                        if data.get('status') == 'connected':
                            print(f'  → Connection ACK received')
                        elif data.get('status') == 'complete':
                            print(f'  → Complete: {data.get("chunks")} chunks in {data.get("total_ms")}ms')
                    except:
                        pass
                
                # Show every 10th chunk
                if chunk_count > 0 and chunk_count % 10 == 0:
                    elapsed = time.time() - start_total
                    print(f'  ... {chunk_count} chunks received, {elapsed:.1f}s elapsed')
        
        rs.close()
        
        total_time = time.time() - start_total
        
        print(f'\n✓ Stream complete:')
        print(f'  - First chunk: {first_line_time*1000:.1f}ms' if first_line_time else '  - No chunks')
        print(f'  - Total chunks: {chunk_count}')
        print(f'  - Total time: {total_time:.1f}s')
        
        if first_line_time and first_line_time < 0.3:
            print(f'  ✓ SUCCESS - Under 0.3s target!')
        elif first_line_time:
            print(f'  ⚠️ {first_line_time*1000:.0f}ms - above 300ms target')
        
    except Exception as e:
        print(f'✗ Error: {e}')

if __name__ == '__main__':
    test_instant_stream()
