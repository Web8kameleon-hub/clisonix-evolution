#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


@dataclass
class CheckFailure:
    code: str
    message: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def parse_services(compose_file: Path) -> dict[str, dict[str, bool]]:
    data: dict[str, dict[str, bool]] = {}
    if not compose_file.exists():
        return data

    lines = read_text(compose_file).splitlines()
    in_services = False
    current_service: str | None = None

    for line in lines:
        if not in_services:
            if re.match(r"^services\s*:\s*$", line):
                in_services = True
            continue

        if not line.strip() or line.strip().startswith("#"):
            continue

        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()

        if indent == 0:
            break

        if indent == 2 and re.match(r"^[A-Za-z0-9_.-]+\s*:\s*$", stripped):
            current_service = stripped.split(":", 1)[0].strip()
            data[current_service] = {"healthcheck": False, "container_name": False}
            continue

        if current_service and indent == 4:
            if stripped.startswith("healthcheck:"):
                data[current_service]["healthcheck"] = True
            if stripped.startswith("container_name:"):
                data[current_service]["container_name"] = True

    return data


def collect_container_names(compose_file: Path) -> list[str]:
    names: list[str] = []
    if not compose_file.exists():
        return names

    for line in read_text(compose_file).splitlines():
        m = re.match(r"^\s{4}container_name\s*:\s*['\"]?([^'\"\s]+)['\"]?\s*$", line)
        if m:
            names.append(m.group(1).strip())
    return names


def has_regex(path: Path, pattern: str) -> bool:
    if not path.exists():
        return False
    return re.search(pattern, read_text(path), flags=re.MULTILINE | re.IGNORECASE) is not None


def main() -> int:
    failures: list[CheckFailure] = []

    compose_deploy = ROOT / "docker-compose.75-services.yml"
    compose_full = ROOT / "docker-compose.yml"

    deploy_services = parse_services(compose_deploy)
    full_services = parse_services(compose_full)

    if not compose_deploy.exists():
        failures.append(CheckFailure("MISSING_DEPLOY_COMPOSE", f"Missing {compose_deploy.relative_to(ROOT)}"))
    if not compose_full.exists():
        failures.append(CheckFailure("MISSING_FULL_COMPOSE", f"Missing {compose_full.relative_to(ROOT)}"))

    critical_deploy_services = [
        "web",
        "api",
        "ocean-core",
        "user-management",
        "ocean-core-multimodal",
        "kloud-upstream-runtime",
        "kloud-bridge",
        "curiosity",
    ]

    for service in critical_deploy_services:
        if service not in deploy_services:
            failures.append(
                CheckFailure(
                    "MISSING_CRITICAL_DEPLOY_SERVICE",
                    f"Service '{service}' is missing in {compose_deploy.relative_to(ROOT)}",
                )
            )

    health_required = [
        "web",
        "api",
        "ocean-core",
        "user-management",
        "ocean-core-multimodal",
        "kloud-upstream-runtime",
        "kloud-bridge",
        "curiosity",
    ]
    for service in health_required:
        if service in deploy_services and not deploy_services[service].get("healthcheck", False):
            failures.append(
                CheckFailure(
                    "MISSING_HEALTHCHECK",
                    f"Service '{service}' has no healthcheck in {compose_deploy.relative_to(ROOT)}",
                )
            )

    # Detect duplicate container names in deployment compose.
    container_names = collect_container_names(compose_deploy)
    seen: set[str] = set()
    dups: set[str] = set()
    for name in container_names:
        if name in seen:
            dups.add(name)
        seen.add(name)
    for dup in sorted(dups):
        failures.append(
            CheckFailure(
                "DUPLICATE_CONTAINER_NAME",
                f"Duplicate container_name '{dup}' in {compose_deploy.relative_to(ROOT)}",
            )
        )

    # Critical route files that must exist.
    required_files = [
        ROOT / "apps/web/app/api/zurich/route.ts",
        ROOT / "apps/web/app/api/debate/route.ts",
        ROOT / "apps/web/app/api/debate/stream/route.ts",
        ROOT / "apps/web/app/api/kloud-bridge/[...path]/route.ts",
        ROOT / "apps/web/app/api/ocean/[...path]/route.ts",
        ROOT / "apps/web/app/api/proxy/health/route.ts",
        ROOT / "apps/web/app/api/proxy/system-metrics/route.ts",
        ROOT / "apps/web/app/api/proxy/user-data-sources/route.ts",
        ROOT / "apps/web/app/api/proxy/user-summary/route.ts",
        ROOT / "apps/api/main.py",
        ROOT / "services/kloud_bridge/main.py",
        ROOT / "ocean-core/ocean_core_full.py",
    ]
    for path in required_files:
        if not path.exists():
            failures.append(CheckFailure("MISSING_CRITICAL_FILE", f"Missing required file: {path.relative_to(ROOT)}"))

    # Critical endpoint contracts by regex.
    endpoint_contracts = [
        (ROOT / "apps/api/main.py", r"@app\.get\(\s*[\"']?/health[\"']?"),
        (ROOT / "apps/api/main.py", r"@app\.(get|post)\(\s*[\"']?/api/zurich[\"']?\s*\)"),
        (ROOT / "services/kloud_bridge/main.py", r"@app\.get\(\s*[\"']?/health[\"']?"),
        (ROOT / "services/kloud_bridge/main.py", r"@app\.get\(\s*[\"']?/status[\"']?"),
        (ROOT / "services/kloud_bridge/main.py", r"/hardware/nodes/register"),
        (ROOT / "services/kloud_bridge/main.py", r"/hardware/mesh/status"),
        (ROOT / "ocean-core/ocean_core_full.py", r"@app\.get\(\s*[\"']?/health[\"']?"),
        (ROOT / "ocean-core/ocean_core_full.py", r"/api/v1/nanogrid/status"),
    ]

    for file_path, pattern in endpoint_contracts:
        if not has_regex(file_path, pattern):
            failures.append(
                CheckFailure(
                    "MISSING_ENDPOINT_CONTRACT",
                    f"Missing endpoint contract in {file_path.relative_to(ROOT)} for pattern: {pattern}",
                )
            )

    # Ensure default deploy workflow includes critical services in its default service list.
    deploy_workflow = ROOT / ".github/workflows/auto-deploy-all-green.yml"
    if deploy_workflow.exists():
        wf_text = read_text(deploy_workflow)
        for svc in [
            "ocean-core-multimodal",
            "kloud-upstream-runtime",
            "kloud-bridge",
            "curiosity",
        ]:
            if svc not in wf_text:
                failures.append(
                    CheckFailure(
                        "MISSING_DEPLOY_WORKFLOW_SERVICE",
                        f"Service '{svc}' not referenced in auto deploy workflow defaults",
                    )
                )
    else:
        failures.append(CheckFailure("MISSING_DEPLOY_WORKFLOW", "Missing .github/workflows/auto-deploy-all-green.yml"))

    report = {
        "ok": len(failures) == 0,
        "checked_at": "runtime",
        "deploy_compose": str(compose_deploy.relative_to(ROOT)),
        "full_compose": str(compose_full.relative_to(ROOT)),
        "deploy_service_count": len(deploy_services),
        "full_service_count": len(full_services),
        "failures": [f.__dict__ for f in failures],
    }

    out = ROOT / "docs" / "production" / "canonical" / "repo_integrity_guard_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=True), encoding="utf-8")

    if failures:
        print("[REPO-INTEGRITY-GUARD] FAIL")
        for f in failures:
            print(f"- {f.code}: {f.message}")
        print(f"Report: {out.relative_to(ROOT)}")
        return 1

    print("[REPO-INTEGRITY-GUARD] PASS")
    print(f"Report: {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
