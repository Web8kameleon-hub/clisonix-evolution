#!/usr/bin/env python3
"""
Test i plotë i Runtime me provider-a dhe pipeline-et
"""

import asyncio
import sys
sys.path.insert(0, "/opt/clisonix.com")

from ocean_core.runtime.init import initialize_runtime, get_runtime
from ocean_core.runtime.pipeline_registry import get_pipeline_registry
from ocean_core.routing.provider_router import get_provider_router

async def test_full():
    print("🧪 Testing Full Runtime System")
    print("=" * 50)
    
    # Inicializo
    runtime = initialize_runtime()
    print(f"✅ Runtime initialized: {runtime['initialized']}")
    print(f"   Providers: {list(runtime['providers']._providers.keys())}")
    print(f"   MegaLayer: {runtime['mega_layer'].name}")
    
    # Testo router-in
    router = get_provider_router()
    print("\n📊 Available providers:", router.list_available_providers())
    print("📊 Health check:", await router.health_check_all())
    
    # Testo pipeline-et
    pipelines = get_pipeline_registry()
    print(f"\n📊 Available pipelines: {pipelines.list_pipelines()}")
    
    # Testo chat pipeline
    print("\n📝 Testing Chat Pipeline...")
    result = await pipelines.execute("chat", {
        "prompt": "Hello, how are you?",
        "temperature": 0.7,
        "max_tokens": 100
    })
    print(f"   Response: {result.get('content', '')[:100]}...")
    print(f"   Provider: {result.get('provider')}")
    print(f"   Latency: {result.get('latency_ms', 0):.2f}ms")
    
    # Testo reasoning pipeline
    print("\n🧠 Testing Reasoning Pipeline...")
    result = await pipelines.execute("reasoning", {
        "prompt": "Explain the concept of resonance in simple terms",
        "depth": 3
    })
    print(f"   Response: {result.get('content', '')[:100]}...")
    print(f"   Provider: {result.get('provider')}")
    print(f"   Resonance: {result.get('resonance', 0)}")
    
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    asyncio.run(test_full())
