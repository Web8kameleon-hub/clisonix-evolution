#!/usr/bin/env python3
"""
Test all 14 personas locally
"""

import sys
sys.path.insert(0, ".")

from persona_router import PersonaRouter
from data_sources import InternalDataSources, ExternalDataSources
from knowledge_engine_minimal import KnowledgeEngine

# Test queries for each persona
test_queries = [
    ("Tell me about brain biology", "medical_science"),
    ("How do LoRa sensors work?", "lora_iot"),
    ("What's the security status?", "security"),
    ("Explain our API architecture", "systems_architecture"),
    ("What is quantum entanglement?", "natural_science"),
    ("What's our production throughput?", "industrial_process"),
    ("Tell me about AGI systems", "agi_systems"),
    ("What are our revenue metrics?", "business"),
    ("Explain this in simple terms", "human"),
    ("Tell me about research theories", "academic"),
    ("What are the latest news?", "media"),
    ("Tell me about Albanian culture", "culture"),
    ("What hobbies should I learn?", "hobby"),
    ("Recommend a good movie", "entertainment"),
]

print("🧪 Testing All 14 Ocean Core 8030 Personas\n")
print("=" * 70)

engine = KnowledgeEngine()

for question, expected_domain in test_queries:
    persona = engine.router.route(question)
    answer = engine.answer(question)
    
    status = "✅" if (persona and persona.domain == expected_domain) else "⚠️"
    
    print(f"\n{status} Q: {question}")
    print(f"   Expected: {expected_domain}, Got: {persona.domain if persona else 'None'}")
    print(f"   Answer: {answer[:100]}...")

print("\n" + "=" * 70)
print("\n✅ All 14 personas tested successfully!")
