"""
TEST SPONTANEOUS CONVERSATION
=============================
Test the new spontaneous conversation mode with full context awareness.

This demonstrates multi-turn dialogue where the AI understands context
from previous exchanges and provides coherent, context-aware responses.
"""

import asyncio
import json
from specialized_chat_engine import SpecializedChatEngine


async def test_spontaneous_conversation():
    """Test spontaneous conversation with context awareness"""
    
    print("\n" + "="*80)
    print("SPONTANEOUS CONVERSATION TEST - CONTEXT AWARENESS")
    print("="*80)
    
    # Initialize the engine
    engine = SpecializedChatEngine()
    
    # Test scenario 1: Neuroscience conversation
    print("\n\n[SCENARIO 1: NEUROSCIENCE DEEP DIVE]")
    print("-" * 80)
    
    turns = [
        "How does the human brain work?",
        "Tell me more about synaptic plasticity",
        "How does this relate to learning and memory?",
        "What imaging techniques do you use to study this?"
    ]
    
    for i, query in enumerate(turns, 1):
        print(f"\n>>> TURN {i}: {query}")
        response = await engine.generate_spontaneous_response(query, use_context=True)
        
        print(f"  Domain: {response['domain']}")
        print(f"  Context Aware: {response['context_aware']}")
        print(f"  Turn Number: {response['turn_number']}")
        print(f"  Conversation Topic: {response['conversation_topic']}")
        print(f"  Answer: {response['answer'][:150]}...")
        print(f"  Follow-ups: {response['follow_up_topics'][:2]}")
    
    # Test scenario 2: Clear and start new conversation
    print("\n\n[SCENARIO 2: QUANTUM PHYSICS CONVERSATION (FRESH)]")
    print("-" * 80)
    
    engine.clear_history()
    
    turns_quantum = [
        "What is quantum computing?",
        "How do qubits work?",
        "What about quantum entanglement?"
    ]
    
    for i, query in enumerate(turns_quantum, 1):
        print(f"\n>>> TURN {i}: {query}")
        response = await engine.generate_spontaneous_response(query, use_context=True)
        
        print(f"  Domain: {response['domain']}")
        print(f"  Context Aware: {response['context_aware']}")
        print(f"  Turn Number: {response['turn_number']}")
        print(f"  Answer: {response['answer'][:150]}...")
    
    # Test scenario 3: AI/ML conversation with domain awareness
    print("\n\n[SCENARIO 3: AI/ML WITH CONTEXT CONTINUITY]")
    print("-" * 80)
    
    engine.clear_history()
    
    turns_ai = [
        "Explain deep learning",
        "How do transformers work?",
        "Why are they better than RNNs?",
        "Tell me about attention mechanisms"
    ]
    
    for i, query in enumerate(turns_ai, 1):
        print(f"\n>>> TURN {i}: {query}")
        response = await engine.generate_spontaneous_response(query, use_context=True)
        
        print(f"  Domain: {response['domain']}")
        print(f"  Context Aware: {response['context_aware']}")
        print(f"  Turn Number: {response['turn_number']}")
        print(f"  Confidence: {response['confidence'] * 100:.0f}%")
        
        # Print statistics at this point
        stats = engine.get_statistics()
        print(f"  Session Stats - Total messages: {stats['total_messages']}, "
              f"Domains: {list(stats['domains_discussed'].keys())}")
    
    # Print final conversation history
    print("\n\n[FULL CONVERSATION HISTORY]")
    print("-" * 80)
    history = engine.get_chat_history(limit=100)
    for msg in history:
        role = "USER" if msg['role'] == 'user' else "ASST"
        print(f"\n[{role}] {msg['content'][:100]}...")
    
    print("\n" + "="*80)
    print("TEST COMPLETED SUCCESSFULLY!")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(test_spontaneous_conversation())
