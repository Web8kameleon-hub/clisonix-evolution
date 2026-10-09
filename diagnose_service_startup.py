#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
  SERVICE STARTUP DIAGNOSTIC
  Test each service individually to find startup issues
═══════════════════════════════════════════════════════════════════

Usage: python diagnose_service_startup.py
"""

import asyncio
import subprocess
import sys
import time
from pathlib import Path

import httpx

# Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

SERVICES = [
    {
        "name": "Ocean Core",
        "cmd": "python ocean_api.py",
        "cwd": "ocean-core",
        "port": 8030,
    },
    {
        "name": "Backend API",
        "cmd": "python -m uvicorn main:app --port 8000",
        "cwd": "apps/api",
        "port": 8000,
    },
    {
        "name": "ALBA",
        "cmd": "python alba_service_5555.py",
        "cwd": ".",
        "port": 5555,
    },
    {
        "name": "ALBI",
        "cmd": "python albi_service_6680.py",
        "cwd": ".",
        "port": 6680,
    },
    {
        "name": "JONA",
        "cmd": "python jona_service_7777.py",
        "cwd": ".",
        "port": 7777,
    },
]


def print_header(title):
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}{title:^70}{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")


def test_service(service):
    """Test a single service startup"""
    name = service["name"]
    cmd = service["cmd"]
    cwd = service["cwd"]
    port = service["port"]

    print(f"\n{BOLD}Testing: {name}{RESET}")
    print(f"├─ Command: {cmd}")
    print(f"├─ CWD: {cwd}")
    print(f"└─ Port: {port}")

    # Build full path
    if cwd == ".":
        full_cwd = "c:\\Users\\Admin\\Desktop\\Clisonix-cloud"
    else:
        full_cwd = f"c:\\Users\\Admin\\Desktop\\Clisonix-cloud\\{cwd}"

    print(f"\n  {YELLOW}Starting service...{RESET}")

    try:
        # Start process with output visible
        process = subprocess.Popen(
            cmd,
            shell=True,
            cwd=full_cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Wait 3 seconds for startup
        try:
            stdout, stderr = process.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            # Process still running after 3 seconds - good sign
            print(f"  {GREEN}✅ Process started (PID: {process.pid}){RESET}")

            # Try health check
            time.sleep(2)
            try:
                resp = httpx.get(f"http://localhost:{port}/health", timeout=2)
                if resp.status_code == 200:
                    print(f"  {GREEN}✅ Health check SUCCESS{RESET}")
                else:
                    print(
                        f"  {RED}❌ Health check returned {resp.status_code}{RESET}"
                    )
            except Exception as e:
                print(f"  {RED}❌ Health check FAILED: {str(e)[:50]}{RESET}")

            # Kill process
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()

            return True

        # Process exited quickly - error
        if stderr:
            print(f"  {RED}❌ Process exited with error:{RESET}")
            error_lines = stderr.split("\n")[:10]  # First 10 lines
            for line in error_lines:
                if line.strip():
                    print(f"     {RED}{line[:80]}{RESET}")
        else:
            print(f"  {RED}❌ Process exited immediately (no output){RESET}")

        return False

    except Exception as e:
        print(f"  {RED}❌ Failed to start: {str(e)[:80]}{RESET}")
        return False


async def main():
    print(f"{BOLD}{BLUE}")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "🔍 SERVICE STARTUP DIAGNOSTIC" + " " * 23 + "║")
    print("╚" + "═" * 68 + "╝")
    print(f"{RESET}\n")

    print_header("PHASE 1: TESTING EACH SERVICE")

    results = {}
    for service in SERVICES:
        results[service["name"]] = test_service(service)
        time.sleep(1)

    # Summary
    print_header("DIAGNOSTIC SUMMARY")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for service_name, status in results.items():
        icon = f"{GREEN}✅{RESET}" if status else f"{RED}❌{RESET}"
        print(f"  {icon} {service_name}")

    print(f"\n  {BOLD}Result: {passed}/{total} services can start{RESET}\n")

    if passed == total:
        print(f"{GREEN}{'='*70}{RESET}")
        print(f"{GREEN}All services can start successfully!{RESET}")
        print(f"{GREEN}You can now run: python orchestrate_discovery_tests.py{RESET}")
        print(f"{GREEN}{'='*70}{RESET}\n")
        return 0
    else:
        print(f"{RED}{'='*70}{RESET}")
        print(f"{RED}Some services failed to start.{RESET}")
        print(f"{RED}Check errors above to see what's wrong.{RESET}")
        print(f"{RED}{'='*70}{RESET}\n")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Diagnostic cancelled{RESET}")
        sys.exit(1)
