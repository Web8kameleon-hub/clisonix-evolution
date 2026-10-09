#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
  SERVICE DISCOVERY TEST ORCHESTRATOR
  Start all microservices and run E2E tests
═══════════════════════════════════════════════════════════════════

This script:
1. Starts Ocean Core (if not running)
2. Starts Backend API
3. Starts ALBA, ALBI, JONA collectors in parallel
4. Waits for all services to register
5. Runs comprehensive discovery tests
6. Provides detailed report

Usage:
    python orchestrate_discovery_tests.py
    python orchestrate_discovery_tests.py --services alba,albi,jona  # specific services
    python orchestrate_discovery_tests.py --cleanup  # stop all services
"""

import asyncio
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import httpx

# ═══════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

SERVICES = {
    "ocean-core": {
        "port": 8030,
        "cmd": "python ocean_api.py",
        "cwd": "ocean-core",
        "startup_only": False,
        "depends_on": []
    },
    "backend-api": {
        "port": 8000,
        "cmd": "python -m uvicorn main:app --port 8000 --host 0.0.0.0",
        "cwd": "apps/api",
        "startup_only": False,
        "depends_on": []
    },
    "alba": {
        "port": 5555,
        "cmd": "python alba_service_5555.py",
        "cwd": None,
        "startup_only": True,
        "depends_on": []
    },
    "albi": {
        "port": 6680,
        "cmd": "python albi_service_6680.py",
        "cwd": None,
        "startup_only": True,
        "depends_on": []
    },
    "jona": {
        "port": 7777,
        "cmd": "python jona_service_7777.py",
        "cwd": None,
        "startup_only": True,
        "depends_on": []
    },
}

# Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

# Global process tracking
RUNNING_PROCESSES: Dict[str, subprocess.Popen] = {}


# ═══════════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════════

def print_header(title):
    """Print section header"""
    print(f"\n{BOLD}{CYAN}{'='*70}{RESET}")
    print(f"{BOLD}{CYAN}{title:^70}{RESET}")
    print(f"{BOLD}{CYAN}{'='*70}{RESET}\n")


def print_status(service: str, status: str, message: str = ""):
    """Print service status"""
    msg = f" - {message}" if message else ""
    print(f"  {BOLD}[{service:15}]{RESET} {status}{msg}")


def print_line(char="─"):
    """Print separator line"""
    print(f"{CYAN}{char * 70}{RESET}")


async def check_port(port: int, timeout: float = 1.0) -> bool:
    """Check if port is responding"""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(f"http://localhost:{port}/health")
            return response.status_code == 200
    except:
        return False


# ═══════════════════════════════════════════════════════════════════
# SERVICE STARTUP
# ═══════════════════════════════════════════════════════════════════

def start_service(service_name: str, service_config: Dict) -> bool:
    """Start a single service"""
    global RUNNING_PROCESSES
    
    port = service_config["port"]
    cmd = service_config["cmd"]
    cwd = service_config["cwd"]
    
    # Build full working directory path
    if cwd:
        full_cwd = Path("c:/Users/Admin/Desktop/Clisonix-cloud") / cwd
    else:
        full_cwd = "c:/Users/Admin/Desktop/Clisonix-cloud"
    
    try:
        print_status(service_name, f"{YELLOW}Starting...{RESET}", f"Port {port}")
        
        # For Windows compatibility
        if sys.platform == "win32":
            process = subprocess.Popen(
                cmd,
                shell=True,
                cwd=str(full_cwd),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
            )
        else:
            process = subprocess.Popen(
                cmd.split(),
                cwd=str(full_cwd),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        
        RUNNING_PROCESSES[service_name] = process
        print_status(service_name, f"{GREEN}✅ Started{RESET}", f"PID {process.pid}")
        return True
    except Exception as e:
        print_status(service_name, f"{RED}❌ Failed{RESET}", str(e)[:50])
        return False


async def wait_for_service(service_name: str, port: int, max_wait: int = 30) -> bool:
    """Wait for service to become healthy"""
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        if await check_port(port):
            print_status(service_name, f"{GREEN}✅ Ready{RESET}", f"Port {port} responding")
            return True
        
        elapsed = int(time.time() - start_time)
        print_status(service_name, f"{YELLOW}Waiting...{RESET}", f"{elapsed}s / {max_wait}s")
        await asyncio.sleep(1)
    
    print_status(service_name, f"{RED}❌ Timeout{RESET}", f"Port {port} not responding after {max_wait}s")
    return False


async def startup_all_services(services_to_start: List[str] = None):
    """Start all configured services"""
    print_header("PHASE 1: STARTING MICROSERVICES")
    
    if services_to_start is None:
        services_to_start = list(SERVICES.keys())
    
    print(f"Services to start: {', '.join(services_to_start)}\n")
    
    # Start services with dependencies
    start_order = ["ocean-core", "backend-api", "alba", "albi", "jona"]
    started = []
    
    for service_name in start_order:
        if service_name not in services_to_start:
            continue
        
        config = SERVICES[service_name]
        
        # Check dependencies
        for dep in config.get("depends_on", []):
            if dep not in started:
                print_status(service_name, f"{RED}⚠️  Skipped{RESET}", f"Dependency {dep} not ready")
                continue
        
        if start_service(service_name, config):
            started.append(service_name)
            await asyncio.sleep(2)  # Give service time to initialize
    
    # Wait for all services
    print_line()
    print(f"\n{BOLD}Waiting for services to become ready...{RESET}\n")
    
    healthy = []
    for service_name in started:
        port = SERVICES[service_name]["port"]
        if await wait_for_service(service_name, port):
            healthy.append(service_name)
        await asyncio.sleep(1)
    
    print_line()
    print(f"\n{GREEN}{len(healthy)}/{len(started)} services healthy{RESET}\n")
    
    return len(healthy) == len(started)


# ═══════════════════════════════════════════════════════════════════
# DISCOVERY TEST RUNNER
# ═══════════════════════════════════════════════════════════════════

async def run_discovery_tests():
    """Run E2E discovery tests"""
    print_header("PHASE 2: RUNNING DISCOVERY TESTS")
    
    print("Launching test suite: test_firestore_discovery_e2e.py\n")
    
    try:
        result = subprocess.run(
            [sys.executable, "test_firestore_discovery_e2e.py"],
            cwd="c:\\Users\\Admin\\Desktop\\Clisonix-cloud",
            capture_output=False,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"{RED}Error running tests: {e}{RESET}")
        return False


# ═══════════════════════════════════════════════════════════════════
# CLEANUP
# ═══════════════════════════════════════════════════════════════════

def cleanup_services():
    """Stop all running services"""
    global RUNNING_PROCESSES
    
    print_header("CLEANUP: STOPPING ALL SERVICES")
    
    for service_name, process in RUNNING_PROCESSES.items():
        try:
            print_status(service_name, f"{YELLOW}Stopping...{RESET}")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            print_status(service_name, f"{GREEN}✅ Stopped{RESET}")
        except Exception as e:
            print_status(service_name, f"{RED}❌ Error{RESET}", str(e)[:40])
    
    RUNNING_PROCESSES.clear()


# ═══════════════════════════════════════════════════════════════════
# MAIN ORCHESTRATION
# ═══════════════════════════════════════════════════════════════════

async def main():
    """Main test orchestration"""
    print(f"\n{BOLD}{GREEN}")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 8 + "🚀 SERVICE DISCOVERY TEST ORCHESTRATOR" + " " * 22 + "║")
    print("╚" + "═" * 68 + "╝")
    print(f"{RESET}\n")
    
    try:
        # Parse command line arguments
        cleanup_only = "--cleanup" in sys.argv
        services_arg = next((s.split("=")[1] for s in sys.argv if s.startswith("--services=")), None)
        services_to_start = services_arg.split(",") if services_arg else None
        
        if cleanup_only:
            cleanup_services()
            return 0
        
        # Start services
        start_time = datetime.now()
        all_ready = await startup_all_services(services_to_start)
        
        if not all_ready:
            print(f"\n{YELLOW}⚠️  Some services failed to start. Running tests anyway...{RESET}")
        
        # Run tests
        await asyncio.sleep(2)  # Let services fully initialize
        tests_passed = await run_discovery_tests()
        
        # Summary
        print_header("ORCHESTRATION SUMMARY")
        
        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"  Total Time: {BOLD}{elapsed:.1f}s{RESET}")
        print(f"  Start Time: {start_time.strftime('%H:%M:%S')}")
        print(f"  Services Started: {BOLD}{len(RUNNING_PROCESSES)}{RESET}")
        
        if tests_passed:
            print(f"\n{GREEN}{BOLD}✅ ALL TESTS PASSED!{RESET}")
            print(f"   Firestore service discovery is fully operational.")
        else:
            print(f"\n{RED}{BOLD}❌ Some tests failed{RESET}")
            print(f"   Check output above for details.")
        
        print(f"\n{CYAN}Services still running. Press Ctrl+C to stop all services.{RESET}\n")
        
        # Keep services running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print(f"\n{YELLOW}Shutting down...{RESET}")
            cleanup_services()
            return 0 if tests_passed else 1
        
    except Exception as e:
        print(f"\n{RED}Fatal error: {e}{RESET}")
        cleanup_services()
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Interrupted by user{RESET}")
        cleanup_services()
        sys.exit(1)
