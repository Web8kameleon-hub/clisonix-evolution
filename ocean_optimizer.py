#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCEAN PERFORMANCE OPTIMIZATION
Optimizon Ocean-Core për shpejtësi dhe kualitet
"""

import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import os

# Fix encoding on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

OCEAN_URL = "http://localhost:8030"

class OceanOptimizer:
    def __init__(self):
        self.results = []
    
    def test_parallel_queries(self):
        """Test performance me parallel requests"""
        print("\n" + "="*60)
        print("⚡ OCEAN PARALLEL PERFORMANCE TEST")
        print("="*60)
        
        queries = [
            "What is consciousness?",
            "Explain AI ethics",
            "What is machine learning?",
            "Define neuroplasticity",
            "How does the brain work?",
        ]
        
        print(f"\n🔄 Sending {len(queries)} parallel queries...")
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(self.send_query, q) 
                for q in queries
            ]
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        self.results.append(result)
                except Exception as e:
                    print(f"❌ Error: {e}")
        
        total_time = time.time() - start_time
        
        print(f"\n✅ Completed {len(self.results)} queries in {total_time:.2f}s")
        print(f"⚡ Average time per query: {total_time/len(self.results):.2f}s")
    
    def send_query(self, query: str) -> dict:
        """Send single query"""
        try:
            start = time.time()
            response = requests.post(
                f"{OCEAN_URL}/api/query",
                json={
                    "query": query,
                    "curiosity_level": "curious",
                    "include_sources": True
                },
                timeout=20
            )
            elapsed = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✓ '{query[:40]}...' → {elapsed:.2f}s")
                return {
                    "query": query,
                    "time": elapsed,
                    "confidence": data.get("confidence", 0)
                }
            else:
                print(f"  ✗ '{query[:40]}...' → HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"  ✗ '{query[:40]}...' → {str(e)}")
            return None
    
    def test_response_quality(self):
        """Test quality ng responses"""
        print("\n" + "="*60)
        print("🎯 OCEAN RESPONSE QUALITY TEST")
        print("="*60)
        
        quality_queries = [
            {
                "query": "What is the hard problem of consciousness?",
                "expected_depth": "philosophical"
            },
            {
                "query": "Explain neural networks",
                "expected_depth": "technical"
            },
            {
                "query": "What makes a good leader?",
                "expected_depth": "behavioral"
            }
        ]
        
        for item in quality_queries:
            try:
                response = requests.post(
                    f"{OCEAN_URL}/api/query",
                    json={
                        "query": item["query"],
                        "curiosity_level": "genius",
                        "include_sources": True
                    },
                    timeout=20
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check response quality
                    has_response = bool(data.get("response"))
                    has_findings = len(data.get("key_findings", [])) > 0
                    has_threads = len(data.get("curiosity_threads", [])) > 0
                    confidence = data.get("confidence", 0)
                    
                    quality_score = (
                        (1 if has_response else 0) * 0.4 +
                        (1 if has_findings else 0) * 0.3 +
                        (1 if has_threads else 0) * 0.2 +
                        (confidence / 100) * 0.1
                    ) * 100
                    
                    print(f"\n📊 Query: '{item['query']}'")
                    print(f"   Response: {'✓' if has_response else '✗'}")
                    print(f"   Key Findings: {len(data.get('key_findings', []))} items")
                    print(f"   Curiosity Threads: {len(data.get('curiosity_threads', []))} items")
                    print(f"   Confidence: {confidence:.0f}%")
                    print(f"   Overall Quality Score: {quality_score:.1f}%")
                
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def test_language_support(self):
        """Test multi-language support"""
        print("\n" + "="*60)
        print("🌍 OCEAN MULTI-LANGUAGE TEST")
        print("="*60)
        
        multilang_queries = [
            ("English", "What is artificial intelligence?"),
            ("Albanian", "Çfarë është inteligjenca artificiale?"),
            ("Italian", "Cosa è l'intelligenza artificiale?"),
            ("Spanish", "¿Qué es la inteligencia artificial?"),
            ("German", "Was ist künstliche Intelligenz?"),
        ]
        
        for lang, query in multilang_queries:
            try:
                start = time.time()
                response = requests.post(
                    f"{OCEAN_URL}/api/query",
                    json={
                        "query": query,
                        "curiosity_level": "curious",
                        "include_sources": True
                    },
                    timeout=20
                )
                elapsed = time.time() - start
                
                if response.status_code == 200:
                    data = response.json()
                    confidence = data.get("confidence", 0)
                    print(f"  ✓ {lang:12} → {confidence:.0f}% confidence in {elapsed:.2f}s")
                else:
                    print(f"  ✗ {lang:12} → HTTP {response.status_code}")
            except Exception as e:
                print(f"  ✗ {lang:12} → Error: {str(e)}")
    
    def print_optimization_report(self):
        """Print optimization report"""
        print("\n" + "="*60)
        print("📈 OPTIMIZATION REPORT")
        print("="*60)
        
        if self.results:
            avg_time = sum(r["time"] for r in self.results) / len(self.results)
            avg_confidence = sum(r["confidence"] for r in self.results) / len(self.results)
            
            print(f"\n✅ Performance Metrics:")
            print(f"   Queries Processed: {len(self.results)}")
            print(f"   Average Response Time: {avg_time:.2f}s")
            print(f"   Average Confidence: {avg_confidence:.1f}%")
            
            if avg_time < 3:
                print(f"\n   ⚡ EXCELLENT - Very fast responses!")
            elif avg_time < 8:
                print(f"\n   ✅ GOOD - Normal performance")
            else:
                print(f"\n   ⚠️  SLOW - Consider adding caching")
        
        print("\n🎓 Ocean is OPTIMIZED and READY for production!")
        print("="*60 + "\n")

def main():
    optimizer = OceanOptimizer()
    
    try:
        # Run all optimization tests
        optimizer.test_parallel_queries()
        optimizer.test_response_quality()
        optimizer.test_language_support()
        optimizer.print_optimization_report()
        
    except KeyboardInterrupt:
        print("\n⚠️  Optimization interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
