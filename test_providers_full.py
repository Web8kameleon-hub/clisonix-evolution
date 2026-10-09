#!/usr/bin/env python3
import asyncio
import sys
sys.path.insert(0, "/opt/clisonix.com")
from ocean_core.providers.init import initialize_all_providers, health_check_all
from ocean_core.providers.base import ProviderRequest

async def test_all():
    print("🧪 Testing ALL Providers...")
    registry = initialize_all_providers()
    health = await health_check_all()
    for name, status in health.items():
        print(f"   {name}: {status.value}")
    for p in registry.list_providers():
        print(f"\n📝 Testing {p}...")
        try:
            resp = await registry.generate(ProviderRequest(prompt="Say hello in one sentence"), p)
            print(f"   ✅ {resp.provider}: {str(resp.content)[:80]}...")
            print(f"   ⚡ Latency: {resp.latency_ms:.2f}ms")
        except Exception as e:
            print(f"   ❌ {p}: {e}")
    for provider in registry._providers.values():
        if hasattr(provider, 'close'):
            await provider.close()
    print("\n✅ Test complete!")

if __name__ == "__main__":
    asyncio.run(test_all())
