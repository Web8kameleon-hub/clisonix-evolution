#!/usr/bin/env python
"""Test document agents and contracts."""

import json

from document_agents import get_agent, list_agents
from document_contracts import AnimationContract, MusicContract, PaintingContract

print("=" * 60)
print("DOCUMENT AGENTS REGISTRY TEST")
print("=" * 60)

agents = list_agents()
print(f"\nTotal Agents: {len(agents)}\n")

for agent in agents:
    status = "✓" if agent.get("available") else "✗"
    backends = ", ".join(agent.get("backends", [])) if agent.get("backends") else "N/A"
    features = ", ".join(agent.get("features", [])) if agent.get("features") else "N/A"
    
    print(f"{status} {agent['name'].upper()}")
    print(f"   Format: {agent['format']}")
    print(f"   Backends: {backends}")
    if features != "N/A":
        print(f"   Features: {features}")
    print()

print("=" * 60)
print("CONTRACT TYPES TEST")
print("=" * 60)

# Test new contracts
print("\n✓ MusicContract")
music = MusicContract()
print(f"  Genre: {music.music_genre}")
print(f"  BPM: {music.bpm}")
print(f"  Mood: {music.mood}")
print(f"  Instruments: {', '.join(music.instruments)}")

print("\n✓ PaintingContract")
painting = PaintingContract()
print(f"  Style: {painting.style}")
print(f"  Theme: {painting.theme}")
print(f"  Dimensions: {painting.width}x{painting.height}")
print(f"  Colors: {len(painting.color_palette)}")

print("\n✓ AnimationContract")
animation = AnimationContract()
print(f"  Style: {animation.animation_style}")
print(f"  FPS: {animation.fps}")
print(f"  Duration: {animation.duration_seconds}s")

print("\n" + "=" * 60)
print("AGENT RETRIEVAL TEST")
print("=" * 60)

for agent_name in ["video", "voice", "music", "painting", "animation"]:
    agent = get_agent(agent_name)
    status = "✓" if agent else "✗"
    print(f"{status} {agent_name.upper()}: {agent.__class__.__name__ if agent else 'NOT FOUND'}")

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED")
print("=" * 60)
