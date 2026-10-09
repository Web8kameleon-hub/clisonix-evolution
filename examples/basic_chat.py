#!/usr/bin/env python3
"""
CLX-AI Basic Chat Example
Simple query processing with learning
"""

import asyncio

from clx import CLXCore


async def main():
    # Initialize CLX
    print("🚀 Initializing CLX...")
    clx = CLXCore(
        memory_dir=".clx_example",
        language="en",
        enable_security=True,
        enable_learning=True,
    )

    # Sample queries
    queries = [
        "Hello! How are you?",
        "What is machine learning?",
        "Hello there!",
        "Explain artificial intelligence",
        "Thanks for your help",
    ]

    print("\n📝 Processing queries...\n")

    for query in queries:
        print(f"👤 User: {query}")

        response = await clx.process_query(
            query,
            context={
                "language": "en",
                "endpoint": "/api/chat",
                "resonance_ndb": 100.0,
            }
        )

        print(f"🤖 CLX: {response['response']}")
        print(f"   Confidence: {response['confidence']:.2%}")
        print(f"   Pattern: {response['pattern_match']}")
        print()

    # Show status
    status = clx.get_status()
    print("\n📊 Session Status:")
    print(f"   Queries processed: {status['queries_processed']}")
    print(f"   Knowledge entries: {status['knowledge']['entries']}")
    print(f"   Languages: {status['knowledge']['languages']}")


if __name__ == "__main__":
    asyncio.run(main())
