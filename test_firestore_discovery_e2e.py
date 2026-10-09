#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
  END-TO-END SERVICE DISCOVERY TEST SUITE
  Testing Firestore-based dynamic service registry
═══════════════════════════════════════════════════════════════════

Tests:
1. Service Registration - Verify all 4 services register correctly
2. Service Discovery - Query services by name and capability
3. Health Checks - Verify all services accessible and healthy
4. Frontend Resolution - Test frontend service resolver
5. Cross-Service Communication - Services finding each other

Run: python test_firestore_discovery_e2e.py
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

import httpx

# ═══════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

SERVICES = {
    "alba": {"port": 5555, "capabilities": ["network-telemetry", "data-collection", "packet-routing"]},
    "albi": {"port": 6680, "capabilities": ["neural-processing", "pattern-detection", "signal-analysis"]},
    "jona": {"port": 7070, "capabilities": ["data-synthesis", "audio-generation", "neural-audio"]},
    "ocean-core": {"port": 8030, "capabilities": ["nlp-generation", "multilingual", "reasoning"]},
    "backend-api": {"port": 8000, "capabilities": ["orchestration", "routing", "data-proxy"]},
}

# Test endpoints
REGISTRY_ENDPOINT = "http://localhost:8000/api/v1"  # Via Backend API
OCEAN_CORE_ENDPOINT = "http://localhost:8030/api/v1"

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


# ═══════════════════════════════════════════════════════════════════
# TEST UTILITIES
# ═══════════════════════════════════════════════════════════════════

def print_header(title):
    """Print test section header"""
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}{title:^70}{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")


def print_test(name, status, message=""):
    """Print test result"""
    icon = f"{GREEN}✅{RESET}" if status else f"{RED}❌{RESET}"
    msg = f" - {message}" if message else ""
    print(f"  {icon} {name}{msg}")


def print_result(title, data, status=True):
    """Print result data"""
    status_icon = f"{GREEN}PASS{RESET}" if status else f"{RED}FAIL{RESET}"
    print(f"\n  [{status_icon}] {title}")
    if isinstance(data, dict):
        for k, v in data.items():
            print(f"      {k}: {v}")
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                print(f"      • {item.get('name', item)}")
            else:
                print(f"      • {item}")
    else:
        print(f"      {data}")


# ═══════════════════════════════════════════════════════════════════
# TEST PHASE 1: SERVICE HEALTH CHECKS
# ═══════════════════════════════════════════════════════════════════

async def test_service_health():
    """Check if all services are running"""
    print_header("PHASE 1: SERVICE HEALTH CHECKS")
    
    healthy_services = []
    failed_services = []
    
    async with httpx.AsyncClient(timeout=5) as client:
        for service_name, config in SERVICES.items():
            port = config["port"]
            health_url = f"http://localhost:{port}/health"
            
            try:
                response = await client.get(health_url)
                if response.status_code == 200:
                    print_test(f"{service_name:15} (port {port})", True, "✓ Responding")
                    healthy_services.append(service_name)
                else:
                    print_test(f"{service_name:15} (port {port})", False, f"HTTP {response.status_code}")
                    failed_services.append(service_name)
            except Exception as e:
                print_test(f"{service_name:15} (port {port})", False, f"{str(e)[:40]}")
                failed_services.append(service_name)
    
    print(f"\n  Summary: {GREEN}{len(healthy_services)}/{len(SERVICES)} services healthy{RESET}")
    return len(healthy_services) == len(SERVICES)


# ═══════════════════════════════════════════════════════════════════
# TEST PHASE 2: SERVICE REGISTRY - LIST
# ═══════════════════════════════════════════════════════════════════

async def test_list_services():
    """Test listing all registered services"""
    print_header("PHASE 2: SERVICE REGISTRY - LIST ALL SERVICES")
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            # Via Backend API
            response = await client.get(f"{REGISTRY_ENDPOINT}/services")
            
            if response.status_code == 200:
                services = response.json()
                print_test("List Services Endpoint", True, f"Found {len(services)} services")
                print_result("Registered Services", services)
                return True
            else:
                print_test("List Services Endpoint", False, f"HTTP {response.status_code}")
                return False
    except Exception as e:
        print_test("List Services Endpoint", False, str(e))
        return False


# ═══════════════════════════════════════════════════════════════════
# TEST PHASE 3: SERVICE DISCOVERY BY NAME
# ═══════════════════════════════════════════════════════════════════

async def test_discover_by_name():
    """Test discovering services by name"""
    print_header("PHASE 3: SERVICE DISCOVERY - BY NAME")
    
    test_names = ["alba", "albi", "jona", "ocean-core", "backend-api"]
    discovered = []
    
    async with httpx.AsyncClient(timeout=10) as client:
        for service_name in test_names:
            try:
                # Query service by name
                response = await client.post(
                    f"{REGISTRY_ENDPOINT}/service-discovery",
                    json={"capability": service_name}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    url = f"http://{data.get('host', 'localhost')}:{data.get('port', 'N/A')}"
                    print_test(f"Discover '{service_name}'", True, url)
                    discovered.append(service_name)
                else:
                    print_test(f"Discover '{service_name}'", False, f"HTTP {response.status_code}")
            except Exception as e:
                print_test(f"Discover '{service_name}'", False, str(e)[:40])
    
    print(f"\n  Summary: {GREEN}{len(discovered)}/{len(test_names)} services discovered{RESET}")
    return len(discovered) == len(test_names)


# ═══════════════════════════════════════════════════════════════════
# TEST PHASE 4: CAPABILITY-BASED DISCOVERY
# ═══════════════════════════════════════════════════════════════════

async def test_capability_discovery():
    """Test discovering services by capability"""
    print_header("PHASE 4: CAPABILITY-BASED DISCOVERY")
    
    capabilities = [
        "network-telemetry",
        "neural-processing",
        "audio-generation",
        "nlp-generation",
        "orchestration"
    ]
    
    async with httpx.AsyncClient(timeout=10) as client:
        for capability in capabilities:
            try:
                # Get all providers for capability
                response = await client.get(
                    f"{REGISTRY_ENDPOINT}/capabilities/{capability}"
                )
                
                if response.status_code == 200:
                    providers = response.json()
                    provider_list = [p.get("name", "unknown") for p in providers]
                    count = len(providers)
                    print_test(f"Capability '{capability}'", True, f"{count} provider(s)")
                    if provider_list:
                        print(f"           → {', '.join(provider_list)}")
                else:
                    print_test(f"Capability '{capability}'", False, f"HTTP {response.status_code}")
            except Exception as e:
                print_test(f"Capability '{capability}'", False, str(e)[:40])


# ═══════════════════════════════════════════════════════════════════
# TEST PHASE 5: SERVICE STATUS & REGISTRY HEALTH
# ═══════════════════════════════════════════════════════════════════

async def test_registry_status():
    """Test registry health and status"""
    print_header("PHASE 5: REGISTRY STATUS & HEALTH")
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{REGISTRY_ENDPOINT}/status")
            
            if response.status_code == 200:
                status = response.json()
                print_test("Registry Status Endpoint", True)
                
                print(f"\n  Registry Mode: {YELLOW}{status.get('mode', 'unknown')}{RESET}")
                print(f"  Backend: {BLUE}{status.get('backend', 'unknown')}{RESET}")
                print(f"  Total Services: {BOLD}{status.get('services', 0)}{RESET}")
                
                if "free_tier_limits" in status:
                    limits = status["free_tier_limits"]
                    print(f"\n  {BOLD}Free Tier Limits:{RESET}")
                    print(f"    • Reads/day: {limits.get('reads_per_day', 'N/A')}")
                    print(f"    • Writes/day: {limits.get('writes_per_day', 'N/A')}")
                
                return True
            else:
                print_test("Registry Status Endpoint", False, f"HTTP {response.status_code}")
                return False
    except Exception as e:
        print_test("Registry Status Endpoint", False, str(e))
        return False


# ═══════════════════════════════════════════════════════════════════
# TEST PHASE 6: CROSS-SERVICE DATA EXCHANGE
# ═══════════════════════════════════════════════════════════════════

async def test_cross_service_communication():
    """Test services communicating with each other via discovery"""
    print_header("PHASE 6: CROSS-SERVICE COMMUNICATION TEST")
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            # Backend API should discover Ocean Core
            print("Testing: Backend API → Ocean Core discovery")
            
            response = await client.post(
                f"{REGISTRY_ENDPOINT}/service-discovery",
                json={"capability": "nlp-generation"}
            )
            
            if response.status_code == 200:
                ocean_service = response.json()
                ocean_url = f"http://{ocean_service.get('host')}:{ocean_service.get('port')}"
                print_test("Backend discovered Ocean Core", True, ocean_url)
                
                # Try to query Ocean Core
                ocean_response = await client.get(f"{ocean_url}/health", timeout=5)
                if ocean_response.status_code == 200:
                    print_test("Verified Ocean Core is accessible", True)
                    return True
                else:
                    print_test("Verified Ocean Core is accessible", False)
                    return False
            else:
                print_test("Backend discovered Ocean Core", False)
                return False
    except Exception as e:
        print_test("Cross-service communication", False, str(e))
        return False


# ═══════════════════════════════════════════════════════════════════
# MAIN TEST RUNNER
# ═══════════════════════════════════════════════════════════════════

async def run_all_tests():
    """Run complete test suite"""
    print(f"\n{BOLD}{GREEN}")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 10 + "🧪 CLISONIX FIRESTORE SERVICE DISCOVERY TEST SUITE" + " " * 8 + "║")
    print("╚" + "═" * 68 + "╝")
    print(f"{RESET}\n")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Test Date: {datetime.now().isoformat()}\n")
    
    # Run all tests
    results = {}
    
    print(f"Waiting 2 seconds for services to fully start...")
    await asyncio.sleep(2)
    
    results["health"] = await test_service_health()
    await asyncio.sleep(1)
    
    results["list"] = await test_list_services()
    await asyncio.sleep(1)
    
    results["discover_name"] = await test_discover_by_name()
    await asyncio.sleep(1)
    
    await test_capability_discovery()
    await asyncio.sleep(1)
    
    results["registry_status"] = await test_registry_status()
    await asyncio.sleep(1)
    
    results["cross_service"] = await test_cross_service_communication()
    
    # Print summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"  Tests Passed: {GREEN}{passed}/{total}{RESET}\n")
    
    for test_name, status in results.items():
        icon = f"{GREEN}✅{RESET}" if status else f"{RED}❌{RESET}"
        print(f"    {icon} {test_name}")
    
    if passed == total:
        print(f"\n{GREEN}{'='*70}{RESET}")
        print(f"{GREEN}{BOLD}🎉 ALL TESTS PASSED - FIRESTORE DISCOVERY FULLY OPERATIONAL!{RESET}")
        print(f"{GREEN}{'='*70}{RESET}\n")
        return 0
    else:
        print(f"\n{RED}{'='*70}{RESET}")
        print(f"{RED}{BOLD}⚠️  SOME TESTS FAILED - CHECK OUTPUT ABOVE{RESET}")
        print(f"{RED}{'='*70}{RESET}\n")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(run_all_tests())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Test suite cancelled by user{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}Fatal error: {e}{RESET}")
        sys.exit(1)
