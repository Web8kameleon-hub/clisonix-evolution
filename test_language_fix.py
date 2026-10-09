#!/usr/bin/env python3
"""Language priority test - verify responses in correct language"""
import sys

import requests

base = 'http://localhost:8030'
print('\n🌍 Language Priority Test (System Prompt Fix)\n')

tests = [
    ('English', 'How does the human brain work?', 'en'),
    ('Albanian', 'Si funksionon truri i njeriut?', 'sq'),
    ('French', 'Comment fonctionne le cerveau humain?', 'fr'),
]

passed = 0
failed = 0

for label, query, expected_lang in tests:
    try:
        print(f'[{label}] "{query[:35]}..."')
        r = requests.post(
            f'{base}/api/v1/chat',
            json={'message': query, 'language': expected_lang},
            timeout=70
        )
        
        if r.status_code == 200:
            data = r.json()
            resp_lang = data.get('language')
            response = data.get('response', '')[:100]
            
            # Language detection keywords
            keywords = {
                'en': ['is', 'the', 'of', 'and', 'to', 'brain', 'work', 'function'],
                'sq': ['është', 'të', 'dhe', 'truri', 'punon', 'funksionon'],
                'fr': ['est', 'le', 'et', 'cerveau', 'comment', 'fonctionne']
            }
            
            # Count keywords from response
            detected_lang = None
            max_count = 0
            for lang, keywords_list in keywords.items():
                count = sum(1 for kw in keywords_list if kw in response.lower())
                if count > max_count:
                    max_count = count
                    detected_lang = lang
            
            if resp_lang == expected_lang:
                print(f'  ✓ Metadata language: {resp_lang}')
                passed += 1
            else:
                print(f'  ✗ Metadata says {resp_lang} (expected {expected_lang})')
                failed += 1
            
            print(f'  Detected language: {detected_lang}')
            print(f'  Response: {response}...\n')
        else:
            print(f'  ✗ Error: {r.status_code}\n')
            failed += 1
    except Exception as e:
        print(f'  ✗ Exception: {e}\n')
        failed += 1

print(f'Results: {passed} passed, {failed} failed')
sys.exit(0 if failed == 0 else 1)
