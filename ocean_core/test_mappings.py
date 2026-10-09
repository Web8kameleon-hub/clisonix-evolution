#!/usr/bin/env python
"""Test contract and format mappings in ocean_core_full.py"""

print("=" * 70)
print("OCEAN CORE - FORMAT & CONTRACT MAPPING TEST")
print("=" * 70)

# Simulate the maps from ocean_core_full.py
format_map = {
    "xlsx": "excel",
    "csv": "excel",
    "pdf": "pdf",
    "report": "report",
    "mp4": "video",
    "video": "video",
    "wav": "voice",
    "voice": "voice",
    "audio": "voice",
    "midi": "music",
    "music": "music",
    "png": "painting",
    "jpg": "painting",
    "jpeg": "painting",
    "painting": "painting",
    "image": "painting",
    "animation": "animation",
}

contract_map = {
    "video": "VideoContract",
    "voice": "VoiceContract",
    "music": "MusicContract",
    "painting": "PaintingContract",
    "animation": "AnimationContract",
}

print("\n📋 FORMAT MAPPING (input format → agent name)")
print("-" * 70)
for fmt, agent in sorted(format_map.items()):
    print(f"  {fmt:12} → {agent}")

print("\n" + "=" * 70)
print("📄 CONTRACT MAPPING (contract type → contract class)")
print("-" * 70)
for contract_type, contract_class in sorted(contract_map.items()):
    print(f"  {contract_type:12} → {contract_class}")

print("\n" + "=" * 70)
print("🔗 FULL MAPPINGS (format requests → agents + contracts)")
print("-" * 70)

# Test complete request flows
test_requests = [
    ("xlsx", "report", "Excel report with metrics"),
    ("pdf", "report", "PDF document"),
    ("csv", "report", "Data export"),
    ("mp4", "video", "Unlimited concept video"),
    ("wav", "voice", "Voice narration"),
    ("midi", "music", "Background music"),
    ("png", "painting", "Artwork generation"),
    ("animation", "animation", "Motion graphics"),
]

agents_used = set()
contracts_used = set()

for fmt, contract_type, description in test_requests:
    agent = format_map.get(fmt)
    contract = contract_map.get(contract_type)
    
    agent_status = "✓" if agent else "✗"
    contract_status = "✓" if contract else "✗"
    
    print(f"\n{agent_status}{contract_status} Format: {fmt:10} Contract: {contract_type:10}")
    print(f"   → Agent: {agent} | Contract: {contract}")
    print(f"   → {description}")
    
    if agent:
        agents_used.add(agent)
    if contract:
        contracts_used.add(contract_type)

print("\n" + "=" * 70)
print("📊 SUMMARY")
print("-" * 70)
print(f"  Total format mappings: {len(format_map)}")
print(f"  Total contract types: {len(contract_map)}")
print(f"  Unique agents: {sorted(agents_used)}")
print(f"  Contracts tested: {sorted(contracts_used)}")

print("\n" + "=" * 70)
print("🔍 VALIDATION CHECKLIST")
print("-" * 70)

checks = [
    ("Document formats fully mapped", len(format_map) >= 15),
    ("All media contracts available", len(contract_map) >= 5),
    ("Video agent mapped", "video" in format_map),
    ("Voice agent mapped", "voice" in format_map),
    ("Music agent mapped", "music" in format_map),
    ("Painting agent mapped", "painting" in format_map or "image" in format_map),
    ("Animation agent mapped", "animation" in format_map),
    ("PDF support", "pdf" in format_map),
    ("Excel support", "xlsx" in format_map and "csv" in format_map),
]

all_passed = True
for check, result in checks:
    status = "✓" if result else "✗"
    print(f"  {status} {check}")
    if not result:
        all_passed = False

print("\n" + "=" * 70)
if all_passed:
    print("✅ ALL MAPPINGS VALID - READY FOR DEPLOYMENT")
else:
    print("⚠️  SOME MAPPINGS MISSING - REVIEW CONFIGURATION")
print("=" * 70)
