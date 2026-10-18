#!/usr/bin/env python3
"""Compare the current production Compose manifest with running containers."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


def declared_services(path: Path) -> dict[str, str]:
    services: dict[str, str] = {}
    in_services = False
    current: str | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line == "services:":
            in_services = True
            continue
        if not in_services:
            continue
        if line and not line[0].isspace():
            break
        service = re.fullmatch(r"  ([\w.-]+):\s*", line)
        if service:
            current = service.group(1)
            services[current] = f"clisonix-{current}"
        elif current:
            container = re.fullmatch(r"    container_name:\s*['\"]?([^'\"\s]+)['\"]?\s*", line)
            if container:
                services[current] = container.group(1)
    return services


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compose", type=Path, default=Path("compose-hosting.yml"))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    services = declared_services(args.compose)
    if not services:
        parser.error(f"No services found in {args.compose}")
    result = subprocess.run(
        ["docker", "ps", "--format", "{{.Names}}"],
        check=True, capture_output=True, text=True,
    )
    running = set(result.stdout.splitlines())
    missing = {service: name for service, name in services.items() if name not in running}
    report = {
        "declared_services": len(services),
        "running_containers_total": len(running),
        "running_compose_containers": len(services) - len(missing),
        "missing_compose_containers": missing,
    }
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"Compose: {len(services)} declared, {report['running_compose_containers']} running, {len(missing)} missing")
        print(f"Docker: {len(running)} containers running in total (includes Swarm and other stacks)")
        for service, name in sorted(missing.items()):
            print(f"MISSING {service}: {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
