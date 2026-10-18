#!/usr/bin/env python3
"""
Port Manager — Menaxhim dinamik i portave
==========================================
Zbulon portat e lira, kontrollon konfliktet, alokon porta.
"""
import json
import re
import socket
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

REPO_ROOT = Path("/opt/clisonix.com")
STATE_FILE = REPO_ROOT / "tools/port_state.json"

# Zonat e portave
PORT_ZONES = {
    "system": (1, 1023),
    "standard": (1024, 7999),
    "clisonix-main": (8000, 8999),
    "clisonix-alt": (9000, 9999),
    "clisonix-high": (28000, 28999),      # ZONA E SIGURT
    "clisonix-isolated": (29000, 29999),
    "custom": (30000, 40000),
}


def is_port_free(port: int, host: str = "0.0.0.0") -> bool:
    """Kontrollo nëse porta është e lirë."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, port))
            return True
    except OSError:
        return False


def get_used_ports() -> Set[int]:
    """Merr të gjitha portat e zëna nga Docker."""
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Ports}}"],
            capture_output=True, text=True, timeout=10,
        )
        ports = set()
        for line in result.stdout.splitlines():
            for match in re.finditer(r"0\.0\.0\.0:(\d+)", line):
                ports.add(int(match.group(1)))
        return ports
    except Exception as e:
        print(f"⚠️ Error getting Docker ports: {e}")
        return set()


def get_host_used_ports() -> Set[int]:
    """Merr portat e zëna në host."""
    try:
        result = subprocess.run(
            ["ss", "-tln"], capture_output=True, text=True, timeout=10,
        )
        ports = set()
        for line in result.stdout.splitlines():
            for match in re.finditer(r":(\d+)\s", line):
                ports.add(int(match.group(1)))
        return ports
    except Exception:
        return set()


def find_free_port(
    zone: str = "clisonix-high",
    start_from: Optional[int] = None,
    max_attempts: int = 100,
) -> Optional[int]:
    """Gjej portën e parë të lirë në një zonë."""
    if zone not in PORT_ZONES:
        raise ValueError(f"Unknown zone: {zone}")

    low, high = PORT_ZONES[zone]
    start = start_from or low
    used = get_used_ports() | get_host_used_ports()

    for port in range(start, high + 1):
        if port not in used and is_port_free(port):
            return port

    return None


def check_port_conflicts() -> Dict[str, List]:
    """Kontrollo konflikte në compose files."""
    conflicts = {
        "duplicates": [],
        "reserved": [],
    }

    for compose_file in [
        "compose-hosting.yml",
        "docker-compose.75-services.yml",
        "docker-compose.unified.yml",
    ]:
        filepath = REPO_ROOT / compose_file
        if not filepath.exists():
            continue

        ports = {}
        for line in filepath.read_text().splitlines():
            for match in re.finditer(r'"(\d+):(\d+)"', line):
                host_port = int(match.group(1))
                ports.setdefault(host_port, []).append(line.strip())

        for port, lines in ports.items():
            if len(lines) > 1:
                conflicts["duplicates"].append({
                    "file": compose_file,
                    "port": port,
                    "count": len(lines),
                })

    return conflicts


def allocate_port(service: str, zone: str = "clisonix-high") -> Dict:
    """Aloko një portë të lirë për një service."""
    port = find_free_port(zone)
    if port is None:
        return {"status": "error", "message": f"No free port in {zone}"}

    # Ruaj në state
    state = {}
    if STATE_FILE.exists():
        state = json.loads(STATE_FILE.read_text())

    state[service] = {
        "port": port,
        "zone": zone,
        "allocated_at": datetime.utcnow().isoformat(),
    }

    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))

    return {"status": "ok", "service": service, "port": port, "zone": zone}


def main():
    """CLI."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  port_manager.py check              — Kontrollo konflikte")
        print("  port_manager.py free               — Gjej portë të lirë")
        print("  port_manager.py allocate SERVICE   — Aloko portë")
        print("  port_manager.py zones              — Listo zonat")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "check":
        conflicts = check_port_conflicts()
        print("=== KONFLIKTE ===")
        if conflicts["duplicates"]:
            for c in conflicts["duplicates"]:
                print(f"  ❌ {c['file']}: port {c['port']} ({c['count']} herë)")
        else:
            print("  ✅ Asnjë konflikt")
        return

    if cmd == "free":
        zone = sys.argv[2] if len(sys.argv) > 2 else "clisonix-high"
        port = find_free_port(zone)
        if port:
            print(f"✅ Port i lirë në {zone}: {port}")
        else:
            print(f"❌ Nuk ka port të lirë në {zone}")
        return

    if cmd == "allocate":
        if len(sys.argv) < 3:
            print("Usage: port_manager.py allocate SERVICE [ZONE]")
            sys.exit(1)
        service = sys.argv[2]
        zone = sys.argv[3] if len(sys.argv) > 3 else "clisonix-high"
        result = allocate_port(service, zone)
        print(json.dumps(result, indent=2))
        return

    if cmd == "zones":
        print("=== ZONAT ===")
        for name, (low, high) in PORT_ZONES.items():
            print(f"  {name}: {low}-{high}")
        return

    print(f"Unknown command: {cmd}")
    sys.exit(1)


if __name__ == "__main__":
    main()
