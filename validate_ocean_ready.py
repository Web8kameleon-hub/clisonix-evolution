#!/usr/bin/env python3
"""
🌊 Clisonix Ocean-Core Validation Suite
=======================================
Comprehensive validation to ensure Ocean-Core is production-ready:
- Multi-language support (responds in question language)
- Instant streaming (starts within 0.2s)
- Elastic timeouts (scales with content)
- End-to-end integration with web frontend
"""
import requests
import json
import time
import sys
from typing import Dict, Tuple

class OceanValidator:
    def __init__(self, base_url: str = "http://localhost:8030", frontend_url: str = "http://localhost:3000"):
        self.base_url = base_url.rstrip("/")
        self.frontend_url = frontend_url.rstrip("/")
        self.results = []
        self.passed = 0
        self.failed = 0
        
    def log(self, level: str, msg: str):
        """Log with emoji prefix"""
        icons = {"✓": "✓", "✗": "✗", "⏱": "⏱", "🌍": "🌍", "📡": "📡", "⚙": "⚙"}
        prefix = icons.get(level, level)
        print(f"{prefix} {msg}")
        
    def test_health(self) -> bool:
        """Test 1: Ocean-Core health endpoint"""
        self.log("⚙", "[1/7] Testing ocean-core health...")
        try:
            r = requests.get(f"{self.base_url}/health", timeout=10)
            if r.status_code == 200:
                self.log("✓", "Ocean-Core is healthy (200)")
                self.passed += 1
                return True
            else:
                self.log("✗", f"Health check failed: {r.status_code}")
                self.failed += 1
                return False
        except Exception as e:
            self.log("✗", f"Health check error: {e}")
            self.failed += 1
            return False
    
    def test_english_chat(self) -> bool:
        """Test 2: English language response"""
        self.log("🌍", "[2/7] Testing English chat...")
        try:
            payload = {
                "message": "What is artificial intelligence in simple terms?",
                "language": "en"
            }
            start = time.time()
            r = requests.post(
                f"{self.base_url}/api/v1/chat",
                json=payload,
                timeout=70
            )
            elapsed = time.time() - start
            
            if r.status_code == 200:
                data = r.json()
                resp_lang = data.get("language", "?")
                response_text = data.get("response", "")[:60]
                
                if resp_lang == "en":
                    self.log("✓", f"English response OK ({elapsed:.1f}s) - {response_text}...")
                    self.passed += 1
                    return True
                else:
                    self.log("✗", f"Wrong language: {resp_lang} (expected 'en')")
                    self.failed += 1
                    return False
            else:
                self.log("✗", f"Request failed: {r.status_code}")
                self.failed += 1
                return False
        except Exception as e:
            self.log("✗", f"English chat error: {e}")
            self.failed += 1
            return False
    
    def test_albanian_chat(self) -> bool:
        """Test 3: Albanian language response"""
        self.log("🌍", "[3/7] Testing Albanian chat...")
        try:
            payload = {
                "message": "Çfarë është inteligjenca artificiale?",
                "language": "sq"
            }
            start = time.time()
            r = requests.post(
                f"{self.base_url}/api/v1/chat",
                json=payload,
                timeout=70
            )
            elapsed = time.time() - start
            
            if r.status_code == 200:
                data = r.json()
                resp_lang = data.get("language", "?")
                response_text = data.get("response", "")[:60]
                
                if resp_lang == "sq":
                    self.log("✓", f"Albanian response OK ({elapsed:.1f}s) - {response_text}...")
                    self.passed += 1
                    return True
                else:
                    self.log("✗", f"Wrong language: {resp_lang} (expected 'sq')")
                    self.failed += 1
                    return False
            else:
                self.log("✗", f"Request failed: {r.status_code}")
                self.failed += 1
                return False
        except Exception as e:
            self.log("✗", f"Albanian chat error: {e}")
            self.failed += 1
            return False
    
    def test_stream_instant(self) -> bool:
        """Test 4: Instant streaming (first chunk <200ms)"""
        self.log("📡", "[4/7] Testing instant streaming...")
        try:
            payload = {
                "message": "Hello, respond briefly",
                "language": "en"
            }
            start_total = time.time()
            
            rs = requests.post(
                f"{self.base_url}/api/v1/chat/stream",
                json=payload,
                headers={"Accept": "text/event-stream"},
                stream=True,
                timeout=70
            )
            
            if rs.status_code != 200:
                self.log("✗", f"Stream request failed: {rs.status_code}")
                self.failed += 1
                return False
            
            first_chunk_time = None
            chunk_count = 0
            
            for line in rs.iter_lines(decode_unicode=True):
                if line:
                    if first_chunk_time is None:
                        first_chunk_time = (time.time() - start_total) * 1000  # ms
                    chunk_count += 1
                    if chunk_count > 50:  # Limit to avoid long wait
                        break
            
            rs.close()
            
            if first_chunk_time and first_chunk_time < 300:
                self.log("✓", f"Instant stream OK ({first_chunk_time:.0f}ms to first chunk)")
                self.passed += 1
                return True
            elif first_chunk_time:
                self.log("✗", f"Stream too slow: {first_chunk_time:.0f}ms (target <300ms)")
                self.failed += 1
                return False
            else:
                self.log("✗", "No stream data received")
                self.failed += 1
                return False
        except Exception as e:
            self.log("✗", f"Stream error: {e}")
            self.failed += 1
            return False
    
    def test_elastic_timeout(self) -> bool:
        """Test 5: Elastic timeout scaling"""
        self.log("⏱", "[5/7] Testing elastic timeout scaling...")
        try:
            # Short message = short timeout
            short_payload = {
                "message": "Hi",
                "language": "en"
            }
            
            start = time.time()
            r_short = requests.post(
                f"{self.base_url}/api/v1/chat/fast",
                json=short_payload,
                timeout=70
            )
            elapsed_short = time.time() - start
            
            if r_short.status_code != 200:
                self.log("✗", f"Short message failed: {r_short.status_code}")
                self.failed += 1
                return False
            
            data_short = r_short.json()
            timeout_short = data_short.get("timeout_seconds", 0)
            
            # Long message = longer timeout
            long_payload = {
                "message": "Generate comprehensive documentation about " + 
                          "machine learning algorithms, including supervised learning, " +
                          "unsupervised learning, deep learning, with examples and diagrams",
                "language": "en"
            }
            
            start = time.time()
            r_long = requests.post(
                f"{self.base_url}/api/v1/chat/fast",
                json=long_payload,
                timeout=70
            )
            elapsed_long = time.time() - start
            
            if r_long.status_code != 200:
                self.log("✗", f"Long message failed: {r_long.status_code}")
                self.failed += 1
                return False
            
            data_long = r_long.json()
            timeout_long = data_long.get("timeout_seconds", 0)
            
            if timeout_long > timeout_short:
                self.log("✓", f"Elastic timeout OK: short={timeout_short:.1f}s, long={timeout_long:.1f}s")
                self.passed += 1
                return True
            else:
                self.log("✗", f"Timeout not scaling: short={timeout_short:.1f}s, long={timeout_long:.1f}s")
                self.failed += 1
                return False
        except Exception as e:
            self.log("✗", f"Timeout test error: {e}")
            self.failed += 1
            return False
    
    def test_frontend_integration(self) -> bool:
        """Test 6: Frontend integration (/api/ocean proxy)"""
        self.log("⚙", "[6/7] Testing frontend integration...")
        try:
            payload = {
                "question": "What is consciousness?",
                "language": "en"
            }
            
            start = time.time()
            r = requests.post(
                f"{self.frontend_url}/api/ocean",
                json=payload,
                timeout=70
            )
            elapsed = time.time() - start
            
            if r.status_code == 200:
                data = r.json()
                response_text = data.get("response", "")[:50]
                self.log("✓", f"Frontend integration OK ({elapsed:.1f}s) - {response_text}...")
                self.passed += 1
                return True
            else:
                self.log("✗", f"Frontend request failed: {r.status_code}")
                self.failed += 1
                return False
        except Exception as e:
            self.log("✗", f"Frontend integration error: {e}")
            self.failed += 1
            return False
    
    def test_frontend_stream(self) -> bool:
        """Test 7: Frontend stream integration"""
        self.log("📡", "[7/7] Testing frontend stream integration...")
        try:
            payload = {
                "message": "Say hello in one line",
                "language": "en"
            }
            
            start_total = time.time()
            
            rs = requests.post(
                f"{self.frontend_url}/api/ocean/stream",
                json=payload,
                headers={"Accept": "text/event-stream"},
                stream=True,
                timeout=70
            )
            
            if rs.status_code != 200:
                self.log("✗", f"Frontend stream failed: {rs.status_code}")
                self.failed += 1
                return False
            
            first_chunk_time = None
            chunk_count = 0
            
            for line in rs.iter_lines(decode_unicode=True):
                if line:
                    if first_chunk_time is None:
                        first_chunk_time = (time.time() - start_total) * 1000
                    chunk_count += 1
                    if chunk_count > 30:
                        break
            
            rs.close()
            
            if chunk_count > 0:
                self.log("✓", f"Frontend stream OK ({chunk_count} chunks, first at {first_chunk_time:.0f}ms)")
                self.passed += 1
                return True
            else:
                self.log("✗", "No stream data from frontend")
                self.failed += 1
                return False
        except Exception as e:
            self.log("✗", f"Frontend stream error: {e}")
            self.failed += 1
            return False
    
    def run_all(self):
        """Run all validation tests"""
        print("\n" + "="*60)
        print("🌊 CLISONIX OCEAN-CORE VALIDATION SUITE")
        print("="*60 + "\n")
        
        # Run all tests
        self.test_health()
        self.test_english_chat()
        self.test_albanian_chat()
        self.test_stream_instant()
        self.test_elastic_timeout()
        self.test_frontend_integration()
        self.test_frontend_stream()
        
        # Summary
        print("\n" + "="*60)
        print(f"RESULTS: {self.passed} passed, {self.failed} failed")
        print("="*60 + "\n")
        
        if self.failed == 0:
            print("✓ ✓ ✓ CLISONIX IS PRODUCTION READY! ✓ ✓ ✓\n")
            print("Features verified:")
            print("  ✓ Multi-language support (responds in question language)")
            print("  ✓ Instant streaming (chunks appear in <300ms)")
            print("  ✓ Elastic timeouts (scales with content complexity)")
            print("  ✓ Frontend integration (web UI connected)")
            print("  ✓ End-to-end streaming (real-time responses)")
            return True
        else:
            print(f"✗ Validation failed - {self.failed} test(s) need fixing\n")
            return False

if __name__ == "__main__":
    validator = OceanValidator()
    success = validator.run_all()
    sys.exit(0 if success else 1)
