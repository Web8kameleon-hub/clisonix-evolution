#!/usr/bin/env python3
import json
import sys

import requests

try:
    data = {
        "message": "What is the capital of Albania?",
        "user_id": "test_user"
    }
    
    print("🔵 Testing Curiosity Ocean on http://localhost:8030...")
    print(f"📤 Sending: {data}")
    print("⏳ Waiting for response...")
    
    response = requests.post(
        'http://localhost:8030/api/v1/chat',
        json=data,
        timeout=60
    )
    
    print(f"✅ Response status: {response.status_code}")
    result = response.json()
    print("\n📥 Response:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
