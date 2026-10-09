#!/usr/bin/env python3
"""Test language priority fix - universal 100+ languages support"""
import time

import requests

base = 'http://localhost:8030'
print('\n' + '='*70)
print('🌍 LANGUAGE PRIORITY TEST - 100+ Languages Support')
print('='*70 + '\n')

tests = [
    ('English', 'What is photosynthesis?', 'en'),
    ('Albanian (Shqip)', 'Çfarë është fotosinteza?', 'sq'),
    ('French (Français)', 'Quest-ce que la photosynthèse?', 'fr'),
    ('Spanish (Español)', '¿Qué es la fotosíntesis?', 'es'),
    ('German (Deutsch)', 'Was ist Photosynthese?', 'de'),
    ('Italian (Italiano)', 'Che cos\'è la fotosintesi?', 'it'),
    ('Portuguese', 'O que é fotossíntese?', 'pt'),
]

passed = 0
failed = 0

for lang_name, query, lang_code in tests:
    try:
        start = time.time()
        print(f'[{lang_name}] "{query[:40]}..."')
        
        r = requests.post(
            f'{base}/api/v1/chat',
            json={'message': query, 'language': lang_code},
            timeout=120
        )
        
        elapsed = time.time() - start
        
        if r.status_code == 200:
            data = r.json()
            detected = data.get('language_detected', '?')
            response_snippet = (data.get('response', '')[:70]).replace('\n', ' ')
            
            # Check if language matches
            status = '✓' if detected == lang_code else '⚠'
            print(f'  {status} Detected: {detected} | Time: {elapsed:.1f}s')
            print(f'  Response: {response_snippet}...\n')
            
            if detected == lang_code:
                passed += 1
            else:
                failed += 1
        else:
            print(f'  ✗ Error: HTTP {r.status_code}\n')
            failed += 1
            
    except Exception as e:
        print(f'  ✗ Exception: {str(e)[:100]}\n')
        failed += 1

print('='*70)
print(f'Results: {passed} passed, {failed} failed')
print('='*70 + '\n')

import sys

sys.exit(0 if failed == 0 else 1)
