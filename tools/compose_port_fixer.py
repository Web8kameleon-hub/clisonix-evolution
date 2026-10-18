#!/usr/bin/env python3
"""
Compose Port Fixer — Rregullim dinamik i portave në compose
=============================================================
Zbulon konflikte, alokon porta të lira, rregullon compose files.
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from port_manager import find_free_port, get_used_ports, get_host_used_ports

REPO_ROOT = Path("/opt/clisonix.com")


def find_conflicts(compose_file: Path) -> List[Dict]:
    """Gjej konflikte në një compose file."""
    if not compose_file.exists():
        return []

    conflicts = []
    services = {}
    current_service = None

    for line_no, line in enumerate(compose_file.read_text().splitlines(), 1):
        # Gjej service
        match = re.match(r"^  ([a-z][a-z0-9_-]*):", line)
        if match:
            current_service = match.group(1)
            services.setdefault(current_service, {"ports": [], "lines": []})

        # Gjej port
        port_match = re.search(r'"?(\d+):(\d+)"?', line)
        if port_match and current_service:
            host_port = int(port_match.group(1))
            services[current_service]["ports"].append({
                "host_port": host_port,
                "container_port": int(port_match.group(2)),
                "line": line_no,
                "raw": line,
            })

    # Gjej portat e përsëritura
    port_to_services = {}
    for svc, info in services.items():
        for p in info["ports"]:
            port_to_services.setdefault(p["host_port"], []).append(svc)

    for port, svcs in port_to_services.items():
        if len(svcs) > 1:
            conflicts.append({
                "port": port,
                "services": svcs,
            })

    return conflicts


def fix_compose_file(
    compose_file: Path,
    dry_run: bool = False,
) -> Dict:
    """Rregullo konfliktet në një compose file."""
    if not compose_file.exists():
        return {"status": "error", "message": "File not found"}

    conflicts = find_conflicts(compose_file)
    if not conflicts:
        return {"status": "ok", "message": "No conflicts", "changes": 0}

    content = compose_file.read_text()
    used_ports = get_used_ports() | get_host_used_ports()
    changes = []

    for conflict in conflicts:
        port = conflict["port"]
        services = conflict["services"]

        # Mbaj shërbimin e parë, ndrysho të tjerët
        for svc in services[1:]:
            new_port = find_free_port("clisonix-high", start_from=28000)
            if new_port is None:
                continue

            # Ndrysho vetëm brenda bllokut të service
            pattern = (
                rf'(^  {re.escape(svc)}:.*?ports:\s*\n\s*-\s*["\']?){port}(:)(\d+)(["\']?)'
            )
            replacement = rf"\g<1>{new_port}\g<2>\g<3>\g<4>"

            new_content = re.sub(
                pattern, replacement, content,
                count=1, flags=re.MULTILINE | re.DOTALL,
            )

            if new_content != content:
                changes.append({
                    "service": svc,
                    "old_port": port,
                    "new_port": new_port,
                })
                content = new_content
                used_ports.add(new_port)

    if changes and not dry_run:
        # Backup
        backup = compose_file.with_suffix(
            compose_file.suffix + f".bak-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        )
        backup.write_text(compose_file.read_text())
        compose_file.write_text(content)

    return {
        "status": "ok",
        "file": str(compose_file),
        "changes": len(changes),
        "details": changes,
        "dry_run": dry_run,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  compose_port_fixer.py check [FILE]   — Kontrollo konflikte")
        print("  compose_port_fixer.py fix [FILE]     — Rregullo konflikte")
        print("  compose_port_fixer.py fix-all        — Rregullo të gjitha")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "check":
        files = [sys.argv[2]] if len(sys.argv) > 2 else [
            "compose-hosting.yml",
            "docker-compose.75-services.yml",
            "docker-compose.unified.yml",
        ]
        for f in files:
            filepath = REPO_ROOT / f
            conflicts = find_conflicts(filepath)
            print(f"\n=== {f} ===")
            if conflicts:
                for c in conflicts:
                    print(f"  ❌ Port {c['port']}: {c['services']}")
            else:
                print("  ✅ Asnjë konflikt")
        return

    if cmd == "fix":
        if len(sys.argv) < 3:
            print("Usage: compose_port_fixer.py fix FILE")
            sys.exit(1)
        result = fix_compose_file(REPO_ROOT / sys.argv[2])
        print(json.dumps(result, indent=2))
        return

    if cmd == "fix-all":
        files = [
            "compose-hosting.yml",
            "docker-compose.75-services.yml",
            "docker-compose.unified.yml",
        ]
        for f in files:
            result = fix_compose_file(REPO_ROOT / f)
            print(json.dumps(result, indent=2))
        return

    print(f"Unknown command: {cmd}")
    sys.exit(1)


if __name__ == "__main__":
    main()
