#!/usr/bin/env python3
"""
CLX-AI Learning Loop Example
Continuous learning for 1 hour
"""

import asyncio

from clx import CLXCore


async def main():
    print("🧠 CLX-AI Learning Loop Example")
    print("=" * 50)

    # Initialize CLX with learning enabled
    clx = CLXCore(
        memory_dir=".clx_learning",
        language="en",
        enable_learning=True,
    )

    print("\n📚 Starting 1-hour learning session...\n")

    # Start learning (1 hour for demo, use 4*3600 for 4 hours)
    learning_task = asyncio.create_task(
        clx.start_learning(duration_seconds=3600)
    )

    # Monitor progress
    while not learning_task.done():
        status = clx.get_status()
        print(f"📈 Knowledge entries: {status['knowledge']['entries']}")
        print(f"   Learning active: {status['learning']['active']}")
        if status['learning']['stats']:
            print(f"   Avg confidence: {status['learning']['stats'].get('avg_confidence', 0):.2%}")
        print()

        # Check every 10 seconds
        await asyncio.sleep(10)

    await learning_task

    # Final stats
    print("\n✅ Learning Complete!")
    final_status = clx.get_status()
    print(f"   Total learned: {final_status['knowledge']['entries']}")
    print(f"   Avg confidence: {final_status['learning']['stats'].get('avg_confidence', 0):.2%}")


if __name__ == "__main__":
    asyncio.run(main())
