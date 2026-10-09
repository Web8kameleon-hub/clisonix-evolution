#!/usr/bin/env python3
"""
Test megalayer integration across both backend API and Ocean Core
"""
import json
import time

import httpx

OCEAN_CORE_URL = "http://localhost:8030"
BACKEND_API_URL = "http://localhost:8000"
TEST_QUERY = "What makes consciousness unified across dimensions?"

async def test_ocean_core_endpoint():
    """Test direct Ocean Core megalayer endpoint"""
    print("\n" + "="*60)
    print("🧠 TESTING OCEAN CORE /api/v1/megalayer ENDPOINT")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{OCEAN_CORE_URL}/api/v1/megalayer",
                json={"query": TEST_QUERY},
                headers={"Content-Type": "application/json"}
            )
            
            print(f"\n✓ Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ SUCCESS - Ocean Core megalayer working!")
                print(f"\nResponse Structure:")
                print(f"  - Success: {data.get('success')}")
                print(f"  - Query: {data.get('query')[:50]}...")
                
                activation = data.get("activation", {})
                print(f"\n✨ Activation Details:")
                print(f"  - Meta Consciousness: {activation.get('meta_consciousness')}")
                print(f"  - Temporal Layer: {activation.get('temporal_layer')}")
                print(f"  - Dimensional Layer: {activation.get('dimensional_layer')}")
                print(f"  - Total Layers Engaged: {activation.get('total_layers_engaged')}")
                
                results = data.get("results", {})
                print(f"\n📊 Results:")
                print(f"  - Complexity Score: {results.get('complexity_score')}")
                print(f"  - Combinations Used: {results.get('combinations_used')}")
                print(f"  - Multi-Script Zones: {results.get('multi_script_zones')}")
                print(f"  - Quantum State: {results.get('quantum_state')}")
                print(f"  - Fractal Depth: {results.get('fractal_depth')}")
                
                return True
            else:
                print(f"\n❌ Failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            return False

async def test_backend_proxy_endpoint():
    """Test backend megalayer proxy endpoint"""
    print("\n" + "="*60)
    print("🔀 TESTING BACKEND API /api/ocean/megalayer PROXY")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{BACKEND_API_URL}/api/ocean/megalayer",
                json={"query": TEST_QUERY},
                headers={"Content-Type": "application/json"}
            )
            
            print(f"\n✓ Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ SUCCESS - Backend proxy working!")
                
                if data.get("success"):
                    inner_data = data.get("data", {})
                    print(f"\nResponse Structure:")
                    print(f"  - Query: {inner_data.get('query', TEST_QUERY)[:50]}...")
                    
                    activation = inner_data.get("activation", {})
                    print(f"\n✨ Activation Details (forwarded from Ocean Core):")
                    print(f"  - Meta Consciousness: {activation.get('meta_consciousness')}")
                    print(f"  - Temporal Layer: {activation.get('temporal_layer')}")
                    
                    return True
                else:
                    print(f"\n❌ Error: {data.get('error')}")
                    return False
            else:
                print(f"\n❌ Failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            return False

async def main():
    print("\n🧪 MEGALAYER INTEGRATION TEST SUITE")
    print("Testing connectivity and functionality across all layers\n")
    
    # Test Ocean Core first
    print("\n[1/2] Testing Ocean Core endpoint...")
    ocean_result = await test_ocean_core_endpoint()
    
    print("\n" + "-"*60)
    
    # Test backend proxy
    print("\n[2/2] Testing backend proxy endpoint...")
    backend_result = await test_backend_proxy_endpoint()
    
    # Summary
    print("\n" + "="*60)
    print("📈 TEST SUMMARY")
    print("="*60)
    print(f"Ocean Core /api/v1/megalayer: {'✅ PASS' if ocean_result else '❌ FAIL'}")
    print(f"Backend /api/ocean/megalayer: {'✅ PASS' if backend_result else '❌ FAIL'}")
    
    if ocean_result and backend_result:
        print("\n🎉 All megalayer endpoints working perfectly!")
        print("✨ Integration complete - Ready for frontend UI\n")
    else:
        print("\n⚠️  Some endpoints need attention\n")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
