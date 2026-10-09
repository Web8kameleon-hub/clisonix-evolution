#!/usr/bin/env python3
"""
OCEAN-CORE DIAGNOSTIC SCRIPT
============================
Validates the Ocean-Core service, Ollama connectivity, and end-to-end flow.
"""

import json
import sys
import time
import requests
from datetime import datetime


def test_ollama():
    """Test direct Ollama connectivity"""
    print("\n" + "="*60)
    print("[1/5] Testing Ollama Service")
    print("="*60)
    
    try:
        # Test Ollama models endpoint
        r = requests.get('http://ollama:11434/api/tags', timeout=5)
        if r.status_code == 200:
            data = r.json()
            models = [m['name'] for m in data.get('models', [])]
            print(f"✅ Ollama is running")
            print(f"   Available models: {', '.join(models) if models else 'None'}")
            return True
        else:
            print(f"❌ Ollama returned status {r.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        return False


def test_ollama_generate():
    """Test Ollama's generate capability"""
    print("\n" + "="*60)
    print("[2/5] Testing Ollama Generate")
    print("="*60)
    
    try:
        start = time.time()
        r = requests.post(
            'http://ollama:11434/api/generate',
            json={
                'model': 'llama3.2:3b',
                'prompt': 'hello',
                'stream': False,
                'raw': True
            },
            timeout=60
        )
        elapsed = time.time() - start
        
        if r.status_code == 200:
            data = r.json()
            response_text = data.get('response', '')[:100]
            print(f"✅ Ollama generate works")
            print(f"   Response time: {elapsed:.1f}s")
            print(f"   Response sample: {response_text}...")
            return True
        else:
            print(f"❌ Ollama generate failed: {r.status_code}")
            print(f"   Response: {r.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Ollama generate error: {e}")
        return False


def test_ocean_core_health():
    """Test Ocean-Core health endpoint"""
    print("\n" + "="*60)
    print("[3/5] Testing Ocean-Core Health")
    print("="*60)
    
    try:
        r = requests.get('http://clisonix-ocean-core:8030/api/v1/status', timeout=5)
        if r.status_code == 200:
            print(f"✅ Ocean-Core is running")
            try:
                data = r.json()
                print(f"   Status: {data.get('status', 'unknown')}")
            except:
                pass
            return True
        else:
            print(f"❌ Ocean-Core health check failed: {r.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ocean-Core connection failed: {e}")
        return False


def test_ocean_chat():
    """Test Ocean-Core chat endpoint"""
    print("\n" + "="*60)
    print("[4/5] Testing Ocean-Core Chat Endpoint")
    print("="*60)
    
    try:
        start = time.time()
        r = requests.post(
            'http://clisonix-ocean-core:8030/api/v1/chat',
            json={'message': 'What is 2+2?', 'language': 'en'},
            timeout=60
        )
        elapsed = time.time() - start
        
        print(f"Response time: {elapsed:.1f}s")
        
        if r.status_code == 200:
            try:
                data = r.json()
                response = data.get('response', '')[:150]
                print(f"✅ Chat endpoint works")
                print(f"   Response preview: {response}...")
                print(f"   Confidence: {data.get('confidence', 'N/A')}")
                return True
            except Exception as e:
                print(f"❌ Invalid JSON response: {e}")
                print(f"   Raw response: {r.text[:200]}")
                return False
        else:
            print(f"❌ Chat endpoint failed: {r.status_code}")
            print(f"   Response: {r.text[:300]}")
            return False
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"❌ Chat endpoint error: {e}")
        return False


def test_frontend_proxy():
    """Test frontend proxy to Ocean-Core"""
    print("\n" + "="*60)
    print("[5/5] Testing Frontend Proxy")
    print("="*60)
    
    try:
        start = time.time()
        r = requests.post(
            'http://clisonix-web:3000/api/ocean',
            json={'question': 'Hello', 'language': 'en'},
            timeout=60
        )
        elapsed = time.time() - start
        
        print(f"Response time: {elapsed:.1f}s")
        
        if r.status_code == 200:
            print(f"✅ Frontend proxy works")
            try:
                data = r.json()
                response = (data.get('response') or 
                           data.get('ocean_response') or 
                           data.get('persona_answer') or 
                           '')[:150]
                print(f"   Response preview: {response}...")
            except:
                print(f"   Response: {r.text[:200]}")
            return True
        else:
            print(f"❌ Proxy failed: {r.status_code}")
            print(f"   Response: {r.text[:300]}")
            return False
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"❌ Proxy error: {e}")
        return False


def main():
    print("\n🔍 OCEAN-CORE DIAGNOSTIC SUITE")
    print(f"Started: {datetime.now().isoformat()}")
    
    results = []
    results.append(("Ollama Service", test_ollama()))
    results.append(("Ollama Generate", test_ollama_generate()))
    results.append(("Ocean-Core Health", test_ocean_core_health()))
    results.append(("Ocean-Core Chat", test_ocean_chat()))
    results.append(("Frontend Proxy", test_frontend_proxy()))
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:8} | {name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All systems operational!")
        return 0
    else:
        print("\n⚠️  Some tests failed. See details above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
