#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLX BRAIN - Quick Start Example
Demonstra përdorimin e sistemit kognitiv
"""

import asyncio
import json
from datetime import datetime, timezone


# Example 1: Direct Processing
def example_direct_processing():
    """Direct brain processing"""
    print("\n" + "="*70)
    print("📖 Example 1: Direct Processing")
    print("="*70)

    from services.clx_brain import CLXBrain

    # Create brain
    brain = CLXBrain(emri="Example-Brain")

    # Process input
    result = brain.procesoj({
        "input": "Krijoni një ide të re për produktin",
        "kreativ": True,
        "hapësirë": 0.8,
        "ndikim": 0.5,
    })

    print(f"✅ Vendim: {result['vendim']['veprim']}")
    print(f"📊 Gjendja Mendore: {result['gjendja']['mendore']}")
    print(f"⚡ Energjia: {result['gjendja']['energji']}")
    print(f"🧠 Neurone Aktive: {result['metrikat']['neurone_aktive']}")
    print(f"⏱️  Koha Procesimi: {result['metrikat']['koha_procesimit_ms']:.2f}ms")


# Example 2: Learning
def example_learning():
    """Learning from experience"""
    print("\n" + "="*70)
    print("📖 Example 2: Learning from Experience")
    print("="*70)

    from services.clx_brain import CLXBrain

    brain = CLXBrain()

    # Process first
    result1 = brain.procesoj({"kreativ": True, "hapësirë": 0.7})
    print(f"1️⃣  Rezultati i parë: {result1['vendim']['veprim']}")

    # Learn from success
    brain.mëso({
        "tipi": "debate_outcome",
        "eksperiencë": {
            "success": True,
            "neurone_aktivizuar": ["kreativ", "analitik"],
            "lidhje_e_re": {
                "burimi": "kreativ",
                "destinacioni": "veprim",
                "pesha": 0.8
            }
        }
    })

    print(f"📚 Sistemi mësoi nga sukses")

    # Elasticity improved
    print(f"📈 Elasticiteti i ri: {brain.rrjeti.elasticiteti:.3f}")


# Example 3: Ethical Decision Making
def example_ethical_decisions():
    """Ethical filtering"""
    print("\n" + "="*70)
    print("📖 Example 3: Ethical Decision Making")
    print("="*70)

    from services.clx_brain import CLXBrain, VleraEtike

    brain = CLXBrain()

    # Decision that could harm
    konteksti = {
        "veprim": "fshi",
        "demtim": True,  # ⚠️ Harmful
        "transparent": False,  # ⚠️ Not transparent
        "i_drejte": True,
    }

    result = brain.procesoj(konteksti)

    print("❌ Vendim fillestar:")
    print(f"   - I pranueshem: {result['vendim'].get('i_pranueshem', '?')}")
    print(f"   - Shkelje: {result['vendim'].get('shkelje', [])}")

    # Ethical recommendation
    if 'rekomandim' in result['vendim']:
        print(f"💡 Rekomandim: {result['vendim']['rekomandim']}")


# Example 4: Neuron Status
def example_neuron_status():
    """Check neuron status"""
    print("\n" + "="*70)
    print("📖 Example 4: Neural Network Status")
    print("="*70)

    from services.clx_brain import CLXBrain

    brain = CLXBrain()

    # Process something to activate neurons
    brain.procesoj({
        "vizual": 0.5,
        "analitik": True,
        "fokus": True,
    })

    # Check status
    status = brain.status()

    print(f"🧠 Neurone Total: {status['neurone_total']}")
    print(f"🔗 Lidhje Totale: {status['lidhje_total']}")
    print(f"📊 Gjendja Mendore: {status['gjendja_mendore']}")
    print(f"⚡ Energjia: {status['energjia']:.2f}")
    print(f"📈 Elasticiteti: {status['elasticiteti']:.2f}")
    print(f"📚 Rregulla Totale: {status['rregulla_total']}")


# Example 5: History
def example_processing_history():
    """View processing history"""
    print("\n" + "="*70)
    print("📖 Example 5: Processing History")
    print("="*70)

    from services.clx_brain import CLXBrain

    brain = CLXBrain()

    # Process multiple inputs
    for i in range(3):
        brain.procesoj({
            "input": f"Request {i+1}",
            "ndikim": 0.5 + (i * 0.1),
        })

    # View history
    print(f"📜 Historiku: {len(brain.kujtesa)} entries")

    for i, entry in enumerate(brain.kujtesa[-3:], 1):
        print(f"\n  {i}. Koha: {entry['koha']}")
        print(f"     Gjendja: {entry['gjendja_mendore']}")
        print(f"     Vendim: {entry['vendim'].get('veprim', 'unknown')}")


# Example 6: Decision Rules
def example_decision_rules():
    """View decision rules"""
    print("\n" + "="*70)
    print("📖 Example 6: Decision Rules")
    print("="*70)

    from services.clx_brain import CLXBrain

    brain = CLXBrain()

    print(f"📋 Rregulla të Vendimmarrjes:")

    for rule in brain.motori_vendimmarrjes.rregullat:
        print(f"\n  • {rule.emri}")
        print(f"    - Pesha: {rule.pesha:.2f}")
        print(f"    - Prioriteti: {rule.prioriteti}")
        print(f"    - Përdorimet: {rule.përdorimet}")
        print(f"    - Suksesi: {rule.suksesi:.2f}")


# Example 7: Integration Example
async def example_ocean_integration():
    """Ocean-Core integration"""
    print("\n" + "="*70)
    print("📖 Example 7: Ocean-Core Integration")
    print("="*70)

    try:
        from services.clx_brain.ocean_integration import OceanRedisIntegration

        integration = OceanRedisIntegration()
        await integration.initialize()

        # Store debate metrics
        await integration.store_debate_metrics("debate_123", {
            "duration_ms": 1500,
            "token_count": 500,
            "confidence": 0.95,
        })

        print("✅ Debate metrics stored in Redis Unlimited")

        # Store decision
        await integration.store_debate_decision("debate_123", {
            "outcome": "resolved",
            "confidence": 0.92,
        })

        print("✅ Decision stored with cognitive processing")

        # Get history
        history = await integration.get_debate_history("debate_123")
        print(f"📜 Debate history: {history['message_count']} messages")

        await integration.close()

    except Exception as e:
        print(f"⚠️  Integration example (Redis required): {e}")


# Example 8: API Usage
def example_api_usage():
    """API usage examples"""
    print("\n" + "="*70)
    print("📖 Example 8: REST API Usage")
    print("="*70)

    print("""
    🚀 Start the service:
        docker run -p 9999:9999 clisonix/clx-brain:latest

    💡 Initialize brain:
        POST http://localhost:9999/brain/initialize

    🧠 Process input:
        POST http://localhost:9999/brain/process
        Body: {
            "input_data": {"kreativ": true, "ndikim": 0.5},
            "context": {}
        }

    📚 Learn:
        POST http://localhost:9999/brain/learn
        Body: {
            "tipi": "experience",
            "eksperiencë": {"success": true}
        }

    📊 Get status:
        GET http://localhost:9999/brain/status

    📈 Get metrics:
        GET http://localhost:9999/brain/metrics

    🔌 WebSocket stream:
        ws://localhost:9999/brain/stream
    """)


# Example 9: Performance
def example_performance():
    """Performance characteristics"""
    print("\n" + "="*70)
    print("📖 Example 9: Performance Characteristics")
    print("="*70)

    import time

    from services.clx_brain import CLXBrain

    brain = CLXBrain()

    # Benchmark
    start = time.perf_counter()

    for i in range(100):
        brain.procesoj({
            "input": f"Request {i}",
            "ndikim": 0.5,
        })

    elapsed = time.perf_counter() - start
    avg_ms = (elapsed / 100) * 1000

    print(f"📊 Benchmark Results (100 iterations):")
    print(f"   - Koha Totale: {elapsed:.2f}s")
    print(f"   - Mesatare: {avg_ms:.2f}ms per request")
    print(f"   - Throughput: {100/elapsed:.0f} requests/sec")
    print(f"\n📈 System Status After Benchmark:")

    status = brain.status()
    print(f"   - Neurone Aktive: {status.get('neurone_total', 0)}")
    print(f"   - Energjia: {status.get('energjia', 0):.2f}")
    print(f"   - Historiku: {status.get('kujtesa_total', 0)} entries")


# Main
if __name__ == "__main__":
    print("\n" + "🧠"*35)
    print("CLX BRAIN - Quick Start Examples")
    print("Sistemi Kognitiv i Clisonix")
    print("🧠"*35)

    try:
        # Run examples
        example_direct_processing()
        example_learning()
        example_ethical_decisions()
        example_neuron_status()
        example_processing_history()
        example_decision_rules()
        example_performance()

        # Async example
        print("\n⏳ Running async example (requires Redis)...")
        try:
            asyncio.run(example_ocean_integration())
        except Exception as e:
            print(f"⚠️  Skipping Redis example: {e}")

        # API info
        example_api_usage()

        print("\n" + "="*70)
        print("✅ All examples completed!")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
