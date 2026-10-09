#!/usr/bin/env python3
"""
Test të gjitha modelet Ollama dhe Ocean Core routes
"""
import asyncio
import httpx
import time

OLLAMA_URL = "http://localhost:11434"
OCEAN_CORE_URL = "http://localhost:8030"

async def list_models():
    """Lista e modeleve të disponueshme"""
    async with httpx.AsyncClient(timeout=10) as c:
        try:
            r = await c.get(f"{OLLAMA_URL}/api/tags")
            if r.status_code == 200:
                return [m["name"] for m in r.json().get("models", [])]
        except Exception as e:
            print(f"Ollama error: {e}")
    return []

async def test_model(model: str, query: str):
    """Testo një model specifik"""
    # Test ALL models including large ones
    
    async with httpx.AsyncClient(timeout=120) as c:  # 2 min timeout for large models
        try:
            start = time.perf_counter()
            r = await c.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": model,
                    "prompt": query,
                    "stream": False,
                    "options": {"num_predict": 100}
                }
            )
            elapsed = (time.perf_counter() - start) * 1000
            
            if r.status_code == 200:
                data = r.json()
                return {
                    "success": True,
                    "response": data.get("response", "")[:200],
                    "time_ms": elapsed
                }
            return {"success": False, "error": f"Status {r.status_code}"}
        except asyncio.CancelledError:
            return {"success": False, "error": "Cancelled"}
        except Exception as e:
            return {"success": False, "error": str(e)[:50]}

async def test_ocean_core():
    """Testo Ocean Core routes"""
    async with httpx.AsyncClient(timeout=30) as c:
        routes = [
            ("GET", "/health", None),
            ("GET", "/api/v1/status", None),
            ("POST", "/api/v1/chat", {"message": "Kush je ti?"}),
        ]
        
        print("\n" + "=" * 60)
        print("OCEAN CORE 8030 - ROUTES TEST")
        print("=" * 60)
        
        for method, path, body in routes:
            try:
                start = time.perf_counter()
                if method == "GET":
                    r = await c.get(f"{OCEAN_CORE_URL}{path}")
                else:
                    r = await c.post(f"{OCEAN_CORE_URL}{path}", json=body)
                elapsed = (time.perf_counter() - start) * 1000
                
                status = "✅" if r.status_code == 200 else "❌"
                print(f"{status} {method} {path} - {r.status_code} ({elapsed:.0f}ms)")
                
                if path == "/api/v1/chat" and r.status_code == 200:
                    data = r.json()
                    resp = data.get("response", "")[:150]
                    print(f"   💬 {resp}...")
            except Exception as e:
                print(f"❌ {method} {path} - Error: {e}")

async def main():
    print("=" * 60)
    print("TEST TË GJITHA MODELET OLLAMA")
    print("=" * 60)
    
    models = await list_models()
    if not models:
        print("❌ Ollama nuk u gjet ose nuk ka modele")
        return
    
    print(f"\n📦 Gjetur {len(models)} modele:")
    for m in models:
        print(f"   • {m}")
    
    # Test çdo model me pyetje shqip
    query = "Kush je ti? Përgjigju shkurt."
    
    print("\n" + "=" * 60)
    print(f"TEST ÇDDO MODEL ME: '{query}'")
    print("=" * 60)
    
    for model in models:
        print(f"\n🔄 Duke testuar: {model}")
        result = await test_model(model, query)
        
        if result["success"]:
            print(f"   ⏱️  Koha: {result['time_ms']:.0f}ms")
            print(f"   💬 {result['response'][:150]}...")
        else:
            print(f"   ❌ Error: {result['error']}")
    
    # Test Ocean Core
    await test_ocean_core()
    
    print("\n" + "=" * 60)
    print("✅ TEST KOMPLET!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
