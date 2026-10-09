#!/usr/bin/env python3
"""Test Albanian Dictionary improvements"""

from albanian_dictionary import DEFINITIONS, get_albanian_response, get_definition

tests = [
    "çfarë është inteligjenca artificiale?",
    "cfare eshte AI?",
    "shpjego machine learning",
    "kush është Ledjan Ahmati?",
    "çfarë është Clisonix?",
    "çfarë është kompjuteri?",
    "përshëndetje!",
    "çfarë mund të bësh?",
    "çfarë është fizika?",
    "çfarë është Shqipëria?",
]

print("=" * 60)
print("🧪 ALBANIAN DICTIONARY TEST")
print("=" * 60)

matched = 0
for test in tests:
    print(f"\n📝 Query: {test}")
    result = get_albanian_response(test)
    if result:
        # Truncate long responses
        display = result[:200] + "..." if len(result) > 200 else result
        print(f"✅ Response: {display}")
        matched += 1
    else:
        print("❌ No match - will fallback to Ollama")

print("\n" + "=" * 60)
print(f"📊 Total definitions available: {len(DEFINITIONS)}")
print(f"📊 Matched queries: {matched}/{len(tests)}")
print("=" * 60)
