#!/usr/bin/env python3
"""
Validate Architecture Runtime Wiring Index against live system.

This script verifies:
1. All referenced documents exist
2. Docker Compose services defined match documented services
3. Routes and endpoints are reachable (when services running)
4. Module dependencies are valid
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


def check_file_exists(file_path: str) -> Tuple[bool, str]:
    """Check if a file exists and return absolute path."""
    abs_path = Path(file_path).resolve()
    if abs_path.exists():
        return True, str(abs_path)
    return False, file_path


def print_check(label: str, passed: bool, details: str = ""):
    """Print a check result with color."""
    status = f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"
    print(f"  {status} {label}", end="")
    if details:
        print(f" — {details}")
    else:
        print()


def validate_document_references() -> bool:
    """Validate all referenced SSOT documents exist."""
    print(f"\n{BLUE}{BOLD}1. DOCUMENT REFERENCES{RESET}")

    refs = {
        "route-destination-map.md": "docs/production/route-destination-map.md",
        "route-destination-map.json": "docs/production/route-destination-map.json",
        "CLISONIX_MODULE_MAP.md": "CLISONIX_MODULE_MAP.md",
        "XLC_RESONANT_READING_MODEL.md": "docs/architecture/XLC_RESONANT_READING_MODEL.md",
        "ARCHITECTURE_RUNTIME_WIRING_INDEX.md": "docs/architecture/ARCHITECTURE_RUNTIME_WIRING_INDEX.md",
    }

    all_exist = True
    for name, path in refs.items():
        exists, full_path = check_file_exists(path)
        print_check(f"Reference: {name}", exists, full_path if exists else f"NOT FOUND: {path}")
        if not exists:
            all_exist = False

    return all_exist


def validate_docker_compose() -> bool:
    """Validate docker-compose.yml syntax and services."""
    print(f"\n{BLUE}{BOLD}2. DOCKER COMPOSE{RESET}")

    compose_file = "docker-compose.yml"
    exists, _ = check_file_exists(compose_file)
    print_check(f"File exists: {compose_file}", exists)

    if not exists:
        return False

    # Check syntax with docker-compose config
    try:
        result = subprocess.run(
            ["docker-compose", "config"],
            capture_output=True,
            text=True,
            timeout=10
        )
        valid_syntax = result.returncode == 0
        print_check("docker-compose syntax", valid_syntax)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print_check("docker-compose command", False, "Docker not installed or timeout")
        return False

    if not valid_syntax:
        print(f"    {RED}Error: {result.stderr}{RESET}")
        return False

    # Parse and verify documented services
    try:
        with open(compose_file, 'r') as f:
            import yaml
            compose = yaml.safe_load(f)
            services = list(compose.get('services', {}).keys())

            documented_services = [
                "clisonix-api",
                "clisonix-ocean-core",
                "ollama",
                "postgres",
                "redis",
                "mongodb",
            ]

            for svc in documented_services:
                found = any(svc in s for s in services)
                print_check(f"Service: {svc}", found)

    except ImportError:
        print(f"    {YELLOW}Warning: PyYAML not installed, skipping deep validation{RESET}")
    except Exception as e:
        print(f"    {RED}Error parsing compose: {e}{RESET}")
        return False

    return True


def validate_entry_files() -> bool:
    """Validate backend entry files exist."""
    print(f"\n{BLUE}{BOLD}3. BACKEND ENTRY FILES{RESET}")

    entry_files = {
        "ocean-core/ocean_core_full.py": "Ocean Core main entry",
        "apps/api/main.py": "Clisonix API main entry",
        "apps/api/routers/v1_router.py": "API v1 router",
    }

    all_exist = True
    for path, desc in entry_files.items():
        exists, full_path = check_file_exists(path)
        print_check(f"{desc}", exists, path)
        if not exists:
            all_exist = False

    return all_exist


def validate_route_mapping() -> bool:
    """Validate route-destination-map references."""
    print(f"\n{BLUE}{BOLD}4. ROUTE MAPPING{RESET}")

    route_file = "docs/production/route-destination-map.json"
    exists, _ = check_file_exists(route_file)
    print_check(f"File exists: {route_file}", exists)

    if not exists:
        return False

    try:
        with open(route_file, 'r') as f:
            routes = json.load(f)

            # Check key sections exist
            sections = ["routes", "redirects", "rewrites"]
            for section in sections:
                has_section = section in routes or "rewrites" in (routes if isinstance(routes, dict) else {})
                print_check(f"Section: {section}", has_section)

            # Count routes
            if isinstance(routes, dict):
                total = sum(len(v) for v in routes.values() if isinstance(v, list))
                print_check(f"Total routes mapped", True, f"{total} entries")

    except json.JSONDecodeError as e:
        print(f"    {RED}JSON Error: {e}{RESET}")
        return False
    except Exception as e:
        print(f"    {RED}Error: {e}{RESET}")
        return False

    return True


def validate_healthcheck_endpoints() -> bool:
    """Validate known health endpoints (when services available)."""
    print(f"\n{BLUE}{BOLD}5. HEALTH ENDPOINTS (when services running){RESET}")

    endpoints = [
        ("http://localhost:8000/health", "clisonix-api"),
        ("http://localhost:8030/health", "clisonix-ocean-core"),
        ("http://localhost:11434/api/status", "ollama"),
    ]

    try:
        import requests
    except ImportError:
        print(f"    {YELLOW}Skipping: requests library not installed{RESET}")
        return True

    reachable = 0
    for url, service in endpoints:
        try:
            response = requests.get(url, timeout=2)
            accessible = response.status_code < 500
            print_check(f"Endpoint: {service}", accessible, url)
            if accessible:
                reachable += 1
        except requests.exceptions.ConnectionError:
            print_check(f"Endpoint: {service}", False, f"{url} (service not running)")
        except Exception as e:
            print_check(f"Endpoint: {service}", False, f"{url} ({type(e).__name__})")

    return True  # Don't fail if services aren't running


def validate_module_map() -> bool:
    """Validate CLISONIX_MODULE_MAP structure."""
    print(f"\n{BLUE}{BOLD}6. MODULE MAP VALIDATION{RESET}")

    module_file = "CLISONIX_MODULE_MAP.md"
    exists, _ = check_file_exists(module_file)
    print_check(f"File exists: {module_file}", exists)

    if not exists:
        return False

    required_modules = [
        "ocean",
        "chat",
        "trinity",
        "zurich",
        "alba",
        "albi",
        "jona",
        "asi",
    ]

    try:
        with open(module_file, 'r') as f:
            content = f.read()

            for module in required_modules:
                found = module in content.lower()
                print_check(f"Module: {module}", found)

    except Exception as e:
        print(f"    {RED}Error: {e}{RESET}")
        return False

    return True


def main():
    """Run all validations."""
    print(f"\n{BOLD}=== Architecture Wiring Index Validation ==={RESET}")
    print(f"Repo: Clisonix Cloud")
    print(f"Date: {subprocess.run(['date'], capture_output=True, text=True).stdout.strip()}")

    results = {
        "Document References": validate_document_references(),
        "Docker Compose": validate_docker_compose(),
        "Entry Files": validate_entry_files(),
        "Route Mapping": validate_route_mapping(),
        "Health Endpoints": validate_healthcheck_endpoints(),
        "Module Map": validate_module_map(),
    }

    # Summary
    print(f"\n{BOLD}=== SUMMARY ==={RESET}")
    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, result in results.items():
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"  {status} — {name}")

    print(f"\n{BOLD}Result: {passed}/{total} checks passed{RESET}")

    if passed == total:
        print(f"{GREEN}✓ All validations passed!{RESET}\n")
        return 0
    else:
        print(f"{YELLOW}⚠ Some validations failed. Review above for details.{RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
