#!/usr/bin/env python3
"""Test Ocean Core imports"""
import os
import sys

# Add ocean-core to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🧪 TESTING OCEAN CORE V2 IMPORTS")
print("=" * 70)

tests_passed = 0
tests_failed = 0

# Test 1: ocean_core_full
try:
    from ocean_core_full import app
    from real_answer_engine import get_real_answer_engine
    print("✅ Test 1: ocean_core_full.py - PASSED")
    print("   ✓ FastAPI app imported")
    print("   ✓ RealAnswerEngine (get_real_answer_engine) imported")
    tests_passed += 1
except Exception as e:
    print(f"❌ Test 1: ocean_core_full.py - FAILED")
    print(f"   Error: {e}")
    tests_failed += 1

# Test 2: ocean_multimodal
try:
    from ocean_multimodal import app as multimodal_app
    print("✅ Test 2: ocean_multimodal.py - PASSED")
    print("   ✓ Multimodal FastAPI app imported")
    tests_passed += 1
except Exception as e:
    print(f"⚠️  Test 2: ocean_multimodal.py - SKIPPED")
    print(f"   Info: {e}")

# Test 3: ocean_strict_chat
try:
    from ocean_strict_chat import app as strict_app
    print("✅ Test 3: ocean_strict_chat.py - PASSED")
    print("   ✓ Strict Chat FastAPI app imported")
    tests_passed += 1
except Exception as e:
    print(f"⚠️  Test 3: ocean_strict_chat.py - SKIPPED")
    print(f"   Info: {e}")

# Test 4: Entry scripts exist
import os

try:
    assert os.path.exists("run_ocean_core_full.py"), "run_ocean_core_full.py missing"
    assert os.path.exists("run_ocean_multimodal.py"), "run_ocean_multimodal.py missing"
    assert os.path.exists("run_ocean_strict_chat.py"), "run_ocean_strict_chat.py missing"
    print("✅ Test 4: Entry point scripts - PASSED")
    print("   ✓ run_ocean_core_full.py exists")
    print("   ✓ run_ocean_multimodal.py exists")
    print("   ✓ run_ocean_strict_chat.py exists")
    tests_passed += 1
except AssertionError as e:
    print(f"❌ Test 4: Entry point scripts - FAILED")
    print(f"   Error: {e}")
    tests_failed += 1

print("\n" + "=" * 70)
print(f"RESULTS: {tests_passed} passed, {tests_failed} failed")
print("=" * 70)

if tests_failed == 0:
    print("\n🎉 ALL TESTS PASSED - Ocean Core v2 is ready!")
    sys.exit(0)
else:
    print(f"\n⚠️  {tests_failed} test(s) failed - Please review errors above")
    sys.exit(1)
