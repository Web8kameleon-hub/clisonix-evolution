#!/usr/bin/env python3
"""
Hardcoded to Env — Konverto portat hardcoded në variable
=========================================================
Skanon compose files, gjen porta, krijon variables në .env.
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

REPO_ROOT = Path("/opt/clisonix.com")
ENV_FILE = REPO_ROOT / ".env"


def get_service_for_line(lines: List[str], line_no: int) -> str:
    """Gjej emrin e service për një rresht."""
    for i in range(line_no, -1, -1):
        match = re.match(r"^  ([a-z][a-z0-9_-]*):", lines[i])
        if match:
            return match.group(1)
    return "unknown"


def scan_compose(filepath: Path) -> List[Dict]:
    """Skanon një compose file për porta hardcoded."""
    if not filepath.exists():
        return []

    lines = filepath.read_text().splitlines()
    results = []

    for line_no, line in enumerate(lines, 1):
        match = re.search(r'"?(\d+):(\d+)"?', line)
        if match:
            host_port = int(match.group(1))
            container_port = int(match.group(2))

            # Vetëm nëse nuk ka variable
            if "$" in line:
                continue

            service = get_service_for_line(lines, line_no - 1)
            results.append({
                "file": str(filepath.relative_to(REPO_ROOT)),
                "line": line_no,
                "service": service,
                "host_port": host_port,
                "container_port": container_port,
                "raw": line.strip(),
            })

    return results


def generate_env_vars(entries: List[Dict]) -> Dict[str, str]:
    """Gjenero variables për .env."""
    env_vars = {}

    for entry in entries:
        service = entry["service"]
        host_port = entry["host_port"]

        # Krijo emër variable
        var_name = f"{service.upper().replace('-', '_')}_PORT"
        env_vars[var_name] = str(host_port)

    return env_vars


def update_env_file(env_vars: Dict[str, str], dry_run: bool = False) -> Dict:
    """Përditëso .env me variables."""
    if not ENV_FILE.exists():
        return {"status": "error", "message": ".env not found"}

    content = ENV_FILE.read_text()
    lines = content.splitlines()

    # Gjej variables ekzistuese
    existing = {}
    for i, line in enumerate(lines):
        match = re.match(r"^([A-Z_]+_PORT)=(.*)$", line)
        if match:
            existing[match.group(1)] = (i, match.group(2))

    # Krijo blloк të re
    new_vars = {}
    for name, value in env_vars.items():
        if name not in existing:
            new_vars[name] = value

    if not new_vars:
        return {"status": "ok", "message": "No new vars", "added": 0}

    if not dry_run:
        # Backup
        backup = ENV_FILE.with_suffix(
            ENV_FILE.suffix + f".bak-ports-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        )
        backup.write_text(content)

        # Shto blloк të re
        new_block = ["", "# === PORT ALLOCATIONS (auto-generated) ==="]
        for name, value in sorted(new_vars.items()):
            new_block.append(f"{name}={value}")

        new_content = content + "\n".join(new_block) + "\n"
        ENV_FILE.write_text(new_content)

    return {
        "status": "ok",
        "added": len(new_vars),
        "vars": new_vars,
        "dry_run": dry_run,
    }


def convert_compose_file(filepath: Path, dry_run: bool = False) -> Dict:
    """Konverto portat në variable."""
    if not filepath.exists():
        return {"status": "error", "message": "File not found"}

    content = filepath.read_text()
    lines = content.splitlines()
    changes = []

    for i, line in enumerate(lines):
        match = re.search(r'"?([a-z-]+):"?\s*$|"?(\d+):(\d+)"?', line)
        # Gjej port mapping
        port_match = re.search(r'^(\s*-\s*)"?(\d+):(\d+)"?\s*$', line)
        if not port_match:
            continue

        indent = port_match.group(1)
        host_port = port_match.group(2)
        container_port = port_match.group(3)

        # Gjej service
        service = get_service_for_line(lines, i)
        var_name = f"{service.upper().replace('-', '_')}_PORT"

        # Krijo linjë të re
        new_line = f'{indent}"${{{var_name}:-{host_port}}}:{container_port}"'

        if new_line != line:
            changes.append({
                "line": i + 1,
                "old": line.strip(),
                "new": new_line.strip(),
                "service": service,
            })
            lines[i] = new_line

    if changes and not dry_run:
        backup = filepath.with_suffix(
            filepath.suffix + f".bak-ports-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        )
        backup.write_text(filepath.read_text())
        filepath.write_text("\n".join(lines))

    return {
        "status": "ok",
        "file": str(filepath.relative_to(REPO_ROOT)),
        "changes": len(changes),
        "details": changes[:20],
        "dry_run": dry_run,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  hardcoded_to_env.py scan                — Skano porta hardcoded")
        print("  hardcoded_to_env.py generate-env        — Gjenero variables")
        print("  hardcoded_to_env.py convert FILE        — Konverto file")
        print("  hardcoded_to_env.py convert-all         — Konverto të gjitha")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "scan":
        files = [
            "compose-hosting.yml",
            "docker-compose.75-services.yml",
            "docker-compose.unified.yml",
        ]
        all_entries = []
        for f in files:
            entries = scan_compose(REPO_ROOT / f)
            all_entries.extend(entries)

        print(f"Total ports hardcoded: {len(all_entries)}")
        print()
        for e in all_entries[:40]:
            print(f"  {e['file']}:{e['line']} [{e['service']}] {e['host_port']}:{e['container_port']}")
        return

    if cmd == "generate-env":
        files = [
            "compose-hosting.yml",
            "docker-compose.75-services.yml",
            "docker-compose.unified.yml",
        ]
        all_entries = []
        for f in files:
            all_entries.extend(scan_compose(REPO_ROOT / f))

        env_vars = generate_env_vars(all_entries)
        result = update_env_file(env_vars)
        print(json.dumps(result, indent=2))
        return

    if cmd == "convert":
        if len(sys.argv) < 3:
            print("Usage: hardcoded_to_env.py convert FILE")
            sys.exit(1)
        result = convert_compose_file(REPO_ROOT / sys.argv[2], dry_run=True)
        print(json.dumps(result, indent=2))
        return

    if cmd == "convert-all":
        files = [
            "compose-hosting.yml",
            "docker-compose.75-services.yml",
            "docker-compose.unified.yml",
        ]
        for f in files:
            result = convert_compose_file(REPO_ROOT / f, dry_run=True)
            print(json.dumps(result, indent=2))
        return

    print(f"Unknown command: {cmd}")
    sys.exit(1)


if __name__ == "__main__":
    main()
