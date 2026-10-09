#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
  ONE-BY-ONE SERVICE STARTUP (Interactive)
  Start each service individually and show full output
═══════════════════════════════════════════════════════════════════

Usage: python start_services_one_by_one.py
"""

import subprocess
import sys
import time
from pathlib import Path

# Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
RESET = "\033[0m"
BOLD = "\033[1m"

SERVICES = [
    {
        "name": "Ocean Core",
        "port": 8030,
        "cmd": "python ocean_api.py",
        "cwd": "ocean-core",
        "delay": 5,
    },
    {
        "name": "Backend API",
        "port": 8000,
        "cmd": "python -m uvicorn main:app --port 8000 --host 0.0.0.0 --reload",
        "cwd": "apps/api",
        "delay": 5,
    },
    {
        "name": "ALBA (5555)",
        "port": 5555,
        "cmd": "python alba_service_5555.py",
        "cwd": ".",
        "delay": 3,
    },
    {
        "name": "ALBI (6680)",
        "port": 6680,
        "cmd": "python albi_service_6680.py",
        "cwd": ".",
        "delay": 3,
    },
    {
        "name": "JONA (7777)",
        "port": 7777,
        "cmd": "python jona_service_7777.py",
        "cwd": ".",
        "delay": 3,
    },
]


def print_header(title):
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}{title:^70}{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")


def start_service_interactive(service, index):
    """Start a single service and show full output"""
    name = service["name"]
    cmd = service["cmd"]
    cwd = service["cwd"]
    port = service["port"]
    delay = service["delay"]

    print(f"{BOLD}{MAGENTA}[{index}/{len(SERVICES)}] Starting {name}{RESET}")
    print(f"    Port: {port}")
    print(f"    Command: {cmd}")
    print(f"    Directory: {cwd}\n")

    # Build full path
    if cwd == ".":
        full_cwd = "c:\\Users\\Admin\\Desktop\\Clisonix-cloud"
    else:
        full_cwd = f"c:\\Users\\Admin\\Desktop\\Clisonix-cloud\\{cwd}"

    try:
        print(f"{YELLOW}→ Starting in {delay} seconds (so you can read this)...{RESET}\n")
        time.sleep(delay)

        print(f"{YELLOW}{'─'*70}{RESET}")
        print(f"{YELLOW}OUTPUT:{RESET}\n")

        # Start process with visible output
        process = subprocess.Popen(
            cmd,
            shell=True,
            cwd=full_cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Combine stdout + stderr
            text=True,
            bufsize=1,  # Line buffered
        )

        # Show output for 5 seconds then ask
        start_time = time.time()
        lines_shown = 0
        max_output_time = 5

        try:
            while time.time() - start_time < max_output_time:
                line = process.stdout.readline()
                if line:
                    print(f"  {line.rstrip()}")
                    lines_shown += 1
                time.sleep(0.01)  # Small delay to prevent CPU spinning
        except:
            pass

        # Check if process is still running
        if process.poll() is None:
            print(f"\n{GREEN}✅ Process RUNNING (PID: {process.pid}){RESET}")
            print(f"{YELLOW}{'─'*70}{RESET}\n")

            # Ask user what to do
            response = input(
                f"{BOLD}[{name}] Continue to next service? (y/n/k): {RESET}"
            ).lower()

            if response == "k":
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
                print(f"{RED}✅ Killed {name}{RESET}\n")
                return "killed"
            elif response == "n":
                print(f"{YELLOW}Stopping here...{RESET}\n")
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
                return "stopped"
            else:
                # Keep running in background
                print(f"{GREEN}→ {name} running in background...{RESET}\n")
                return "running"

        else:
            # Process exited
            returncode = process.poll()
            print(f"\n{RED}❌ Process EXITED (Code: {returncode}){RESET}")

            # Show remaining output
            remaining = process.stdout.read()
            if remaining:
                print(f"\n{YELLOW}Remaining output:{RESET}")
                for line in remaining.split("\n")[-10:]:  # Last 10 lines
                    if line.strip():
                        print(f"  {RED}{line}{RESET}")

            print(f"{YELLOW}{'─'*70}{RESET}\n")

            response = input(
                f"{BOLD}[{name}] FAILED. Continue to next? (y/n): {RESET}"
            ).lower()
            if response == "n":
                return "stop"
            return "failed"

    except Exception as e:
        print(f"\n{RED}❌ Error starting {name}: {e}{RESET}\n")
        return "error"


def main():
    print(f"{BOLD}{MAGENTA}")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 12 + "🚀 ONE-BY-ONE SERVICE STARTUP" + " " * 26 + "║")
    print("╚" + "═" * 68 + "╝")
    print(f"{RESET}\n")

    print_header("INTERACTIVE SERVICE STARTUP")

    print(f"{BOLD}This will start services one by one.{RESET}")
    print(f"{BOLD}After each service starts, you can:{RESET}\n")
    print(f"  y - {GREEN}Continue to next service{RESET}")
    print(f"  n - {RED}Stop here{RESET}")
    print(f"  k - {YELLOW}Kill service and stop{RESET}\n")

    input(f"{BOLD}Press Enter to start...{RESET}")

    results = {}
    for i, service in enumerate(SERVICES, 1):
        result = start_service_interactive(service, i)
        results[service["name"]] = result

        if result == "stop":
            print(f"\n{YELLOW}Stopped by user{RESET}\n")
            break

    # Summary
    print_header("SUMMARY")

    for name, status in results.items():
        if status == "running":
            icon = f"{GREEN}✅{RESET}"
            label = "Running"
        elif status == "killed":
            icon = f"{YELLOW}⏹️{RESET}"
            label = "Killed"
        elif status == "stopped":
            icon = f"{YELLOW}⏹️{RESET}"
            label = "Stopped"
        elif status == "failed":
            icon = f"{RED}❌{RESET}"
            label = "Failed"
        else:
            icon = f"{RED}❌{RESET}"
            label = "Error"

        print(f"  {icon} {name:20} - {label}")

    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Interrupted by user{RESET}")
        sys.exit(1)
