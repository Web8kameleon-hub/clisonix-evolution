#!/usr/bin/env python3
"""Generate a no-fake Clisonix capability and module truth matrix."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "apps/web/app/modules/modules-catalog.ts"
APP_ROOT = ROOT / "apps/web/app"
COMPOSE = ROOT / "compose-hosting.yml"
DEFAULT_JSON = ROOT / "docs/production/runtime/capability-truth.json"
DEFAULT_MD = ROOT / "docs/production/runtime/capability-truth.md"


@dataclass
class ModuleTruth:
    module_id: str
    name: str
    href: str
    source_path: str | None
    source_exists: bool
    api_references: list[str]
    live_status: int | None
    state: str
    reason: str


def _catalog_objects(text: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for block in re.findall(r"\{\s*id:\s*[\"'].*?\n\s*\}", text, re.S):
        item: dict[str, str] = {}
        for key in ("id", "name", "href", "category"):
            match = re.search(rf"{key}:\s*[\"']([^\"']+)[\"']", block)
            if match:
                item[key] = match.group(1)
        if {"id", "name", "href"} <= item.keys():
            entries.append(item)
    return entries


def _source_for_href(href: str) -> Path | None:
    if href.startswith("http://") or href.startswith("https://"):
        return None
    route = href.split("?", 1)[0].strip("/")
    return APP_ROOT / route / "page.tsx" if route else APP_ROOT / "page.tsx"


def _api_refs(path: Path | None) -> list[str]:
    if path is None or not path.is_file():
        return []
    text = path.read_text(encoding="utf-8", errors="ignore")
    refs = set(re.findall(r"[\"'](/api/[A-Za-z0-9_./:{}*?=&-]+)[\"']", text))
    return sorted(refs)


def _http_status(url: str, timeout: float) -> int | None:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Clisonix-Runtime-Truth/1.0"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return int(response.status)
    except urllib.error.HTTPError as exc:
        return int(exc.code)
    except (urllib.error.URLError, TimeoutError, ValueError):
        return None


def _module_truth(base_url: str | None, timeout: float) -> list[ModuleTruth]:
    entries = _catalog_objects(CATALOG.read_text(encoding="utf-8"))
    truths: list[ModuleTruth] = []
    for entry in entries:
        href = entry["href"]
        source = _source_for_href(href)
        exists = bool(source and source.is_file())
        refs = _api_refs(source)
        status: int | None = None
        if base_url:
            target = href if href.startswith(("http://", "https://")) else base_url.rstrip("/") + href
            # localhost links are never valid client-facing production routes.
            if not target.startswith("http://localhost"):
                status = _http_status(target, timeout)

        if href.startswith("http://localhost"):
            state, reason = "broken_route", "client-facing catalog link points to localhost"
        elif not exists and not href.startswith(("http://", "https://")):
            state, reason = "missing_source", "catalog route has no page.tsx"
        elif base_url and status is None:
            state, reason = "unreachable", "production request failed or timed out"
        elif base_url and status is not None and status >= 400:
            state, reason = "unavailable", f"production returned HTTP {status}"
        elif refs:
            state, reason = "wired_unverified", "page is reachable and references APIs; functional probe still required"
        else:
            state, reason = "reachable_unverified", "page is reachable but no module-specific API contract was detected"

        truths.append(
            ModuleTruth(
                module_id=entry["id"],
                name=entry["name"],
                href=href,
                source_path=source.relative_to(ROOT).as_posix() if source else None,
                source_exists=exists,
                api_references=refs,
                live_status=status,
                state=state,
                reason=reason,
            )
        )
    return truths


def _compose_services() -> list[str]:
    if not COMPOSE.is_file():
        return []
    services: list[str] = []
    in_services = False
    for line in COMPOSE.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line == "services:":
            in_services = True
            continue
        if not in_services:
            continue
        match = re.match(r"^  ([A-Za-z0-9_.-]+):\s*$", line)
        if match:
            services.append(match.group(1))
        elif line and not line.startswith((" ", "#")):
            break
    return sorted(set(services))


def _docker_services(enabled: bool) -> list[str]:
    if not enabled:
        return []
    try:
        result = subprocess.run(
            ["docker", "service", "ls", "--format", "{{.Name}}"],
            check=True,
            capture_output=True,
            text=True,
            timeout=20,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    return sorted({line.strip() for line in result.stdout.splitlines() if line.strip()})


def _named_capabilities(configured: set[str], deployed: set[str]) -> list[dict[str, Any]]:
    specs = {
        "gram": {
            "paths": ["packages/gram", "gram"],
            "services": ["gram"],
        },
        "orchestrator": {
            "paths": [
                "ocean-core/ocean_orchestrator.py",
                "ocean-core/response_orchestrator.py",
                "backend/system/smart_orchestrator.py",
                "services/orchestrator",
            ],
            "services": ["orchestrator", "orchestra", "saas-orchestrator"],
        },
        "ocean": {
            "paths": ["ocean-core/ocean_core_full.py"],
            "services": ["ocean-core"],
        },
        "clx": {
            "paths": ["sdk/python/clx", "clx_agent.py", "clx_i_service.py"],
            "services": ["clx-agent", "clx-i", "clx-hybrid"],
        },
        "kloud": {
            "paths": ["services/kloud_bridge", "services/kloud_upstream_runtime"],
            "services": ["kloud-bridge", "kloud-upstream-runtime"],
        },
    }
    result: list[dict[str, Any]] = []
    for name, spec in specs.items():
        paths = [p for p in spec["paths"] if (ROOT / p).exists()]
        configured_services = [s for s in spec["services"] if s in configured]
        deployed_services = [
            full for full in deployed
            if any(full == s or full.endswith("_" + s) for s in spec["services"])
        ]
        if deployed_services:
            state = "deployed_unverified"
        elif configured_services:
            state = "configured_not_proven_deployed"
        elif paths:
            state = "source_only"
        else:
            state = "missing"
        result.append(
            {
                "capability": name,
                "state": state,
                "source_paths": paths,
                "configured_services": configured_services,
                "deployed_services": deployed_services,
            }
        )
    return result



def _authority_inventory() -> dict[str, Any]:
    """Read platform-owned registries without promoting them to runtime truth."""
    city_registry_path = ROOT / "config/city-labs.registry.json"
    city_registry: dict[str, Any] = {}
    if city_registry_path.is_file():
        city_registry = json.loads(city_registry_path.read_text(encoding="utf-8"))

    historical_registry_path = ROOT / "registry_export.json"
    historical_registry: dict[str, Any] = {}
    if historical_registry_path.is_file():
        historical_registry = json.loads(
            historical_registry_path.read_text(encoding="utf-8")
        )

    skip_parts = {".git", ".vs", "node_modules", ".next", "__pycache__"}
    engine_files = sorted(
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file()
        and "engine" in path.name.lower()
        and not any(part in skip_parts for part in path.parts)
    )
    orchestrator_files = sorted(
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file()
        and "orchestrat" in path.as_posix().lower()
        and not any(part in skip_parts for part in path.parts)
    )

    pillar_roots = ["all_pillars", "generated_medical_pillars", "lagter_pillars"]
    pillar_counts = {
        root: sum(1 for path in (ROOT / root).rglob("*") if path.is_file())
        if (ROOT / root).is_dir()
        else 0
        for root in pillar_roots
    }
    gram_root = ROOT / "packages/gram"
    gram_files = (
        sorted(path.relative_to(ROOT).as_posix() for path in gram_root.rglob("*") if path.is_file())
        if gram_root.is_dir()
        else []
    )

    historical_summary = historical_registry.get("summary", {})
    return {
        "policy": {
            "path": "NO_FAKE_DATA_POLICY.md",
            "present": (ROOT / "NO_FAKE_DATA_POLICY.md").is_file(),
        },
        "city_labs_registry": {
            "path": "config/city-labs.registry.json",
            "schema": city_registry.get("schema"),
            "declared_labs": len(city_registry.get("labs", [])),
            "classification": "canonical_declaration_not_runtime_health",
        },
        "historical_auto_registry": {
            "path": "registry_export.json",
            "generated": historical_registry.get("generated"),
            "declared_services": historical_summary.get("total_services"),
            "declared_functions": historical_summary.get("total_functions"),
            "declared_endpoints": historical_summary.get("total_endpoints"),
            "classification": "historical_snapshot_not_runtime_health",
        },
        "pillars": {
            "roots": pillar_counts,
            "classification": "stored_artifacts_not_deployed_services",
        },
        "engines": {
            "discovered_files": len(engine_files),
            "paths": engine_files,
            "classification": "source_inventory_not_runtime_health",
        },
        "orchestrators": {
            "discovered_files": len(orchestrator_files),
            "paths": orchestrator_files,
            "classification": "source_inventory_not_runtime_health",
        },
        "gram": {
            "root": "packages/gram",
            "discovered_files": len(gram_files),
            "paths": gram_files,
            "classification": "source_inventory_not_runtime_health",
        },
    }


def _write_report(payload: dict[str, Any], path: Path) -> None:
    modules = payload["modules"]
    summary = payload["module_summary"]
    lines = [
        "# Clisonix Runtime Capability Truth",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "States are evidence levels, not marketing labels. A reachable page is not automatically a functional service.",
        "",
        "## Module summary",
        "",
    ]
    for key in sorted(summary):
        lines.append(f"- {key}: {summary[key]}")
    authority = payload["authority_inventory"]
    lines += [
        "",
        "## Canonical authority inventory",
        "",
        f"- City laboratories declared: {authority['city_labs_registry']['declared_labs']}",
        f"- Historical registry generated: {authority['historical_auto_registry']['generated']}",
        f"- Engine source files discovered: {authority['engines']['discovered_files']}",
        f"- Orchestrator source files discovered: {authority['orchestrators']['discovered_files']}",
        f"- Gram source files discovered: {authority['gram']['discovered_files']}",
        "- Pillar artifacts: " + ", ".join(
            f"{name}={count}" for name, count in authority["pillars"]["roots"].items()
        ),
        "",
    ]
    lines += [
        "",
        "## Named capabilities",
        "",
        "| Capability | State | Source | Configured | Deployed |",
        "|---|---|---|---|---|",
    ]
    for item in payload["named_capabilities"]:
        lines.append(
            "| {capability} | {state} | {source} | {configured} | {deployed} |".format(
                capability=item["capability"],
                state=item["state"],
                source=", ".join(item["source_paths"]) or "—",
                configured=", ".join(item["configured_services"]) or "—",
                deployed=", ".join(item["deployed_services"]) or "—",
            )
        )
    lines += [
        "",
        "## UI modules",
        "",
        "| Module | Route | HTTP | State | Evidence |",
        "|---|---|---:|---|---|",
    ]
    for item in modules:
        lines.append(
            f"| {item['name']} | {item['href']} | {item['live_status'] or '—'} | "
            f"{item['state']} | {item['reason']} |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="")
    parser.add_argument("--timeout", type=float, default=12.0)
    parser.add_argument("--docker", action="store_true")
    parser.add_argument("--root", type=Path)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MD)
    parser.add_argument("--service-inventory", type=Path)
    parser.add_argument("--runtime-snapshot", type=Path)
    args = parser.parse_args()

    if args.service_inventory or args.runtime_snapshot:
        if not (args.service_inventory and args.runtime_snapshot):
            parser.error("--service-inventory and --runtime-snapshot must be used together")
        inventory = json.loads(args.service_inventory.read_text(encoding="utf-8-sig"))
        runtime = json.loads(args.runtime_snapshot.read_text(encoding="utf-8-sig"))
        payload = quarantine_manifest(inventory, runtime)
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(payload["summary"]))
        return

    if args.root:
        global ROOT, CATALOG, APP_ROOT, COMPOSE
        ROOT = args.root.resolve()
        CATALOG = ROOT / "apps/web/app/modules/modules-catalog.ts"
        APP_ROOT = ROOT / "apps/web/app"
        COMPOSE = ROOT / "compose-hosting.yml"

    modules = [asdict(item) for item in _module_truth(args.base_url or None, args.timeout)]
    summary: dict[str, int] = {}
    for item in modules:
        summary[item["state"]] = summary.get(item["state"], 0) + 1

    configured = set(_compose_services())
    deployed = set(_docker_services(args.docker))
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "base_url": args.base_url or None,
        "docker_inspected": args.docker,
        "definitions": {
            "source_only": "code exists; deployment is not proven",
            "configured_not_proven_deployed": "compose config exists; running service is not proven",
            "deployed_unverified": "Swarm service exists; functional request is still required",
            "wired_unverified": "UI page and API references exist; output correctness is unproven",
            "reachable_unverified": "UI page responds; service behavior is unproven",
            "functional": "reserved for a successful capability-specific real-data probe",
        },
        "module_summary": summary,
        "modules": modules,
        "configured_service_count": len(configured),
        "deployed_service_count": len(deployed),
        "named_capabilities": _named_capabilities(configured, deployed),
        "authority_inventory": _authority_inventory(),
    }
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    _write_report(payload, args.markdown_output)
    print(json.dumps({
        "module_summary": summary,
        "configured_service_count": len(configured),
        "deployed_service_count": len(deployed),
        "json": str(args.json_output),
        "markdown": str(args.markdown_output),
    }, indent=2))


def quarantine_manifest(inventory: dict[str, Any], runtime: dict[str, Any]) -> dict[str, Any]:
    """Prepare a deny-by-default review manifest, never infer execution from health.

    This inventory mode cannot promote a service to REAL. It does not modify routes.
    Functional probes and trusted execution evidence are required for promotion.
    """
    rows = []
    matched = set()
    for service in inventory["services"]:
        instances = []
        for index, container in enumerate(runtime["containers"]):
            same_owner = container.get("runtime_owner") == service.get("runtime_owner")
            if same_owner and container.get("service") == service["service"]:
                instances.append(container)
                matched.add(index)
        rows.append({
            **service,
            "classification": "UNKNOWN",
            "production_access": "DENY",
            "routing_action": "QUARANTINE",
            "reason": "No capability-specific execution evidence; container health is insufficient",
            "observed_instances": instances,
            "execution_evidence": [],
        })
    for index, container in enumerate(runtime["containers"]):
        if index not in matched:
            rows.append({
                "service": container.get("service") or container["container"],
                "runtime_owner": container.get("runtime_owner"),
                "dependencies": None,
                "endpoint": None,
                "classification": "UNKNOWN",
                "production_access": "DENY",
                "routing_action": "QUARANTINE",
                "reason": "Runtime instance is not matched to the declared project/service",
                "observed_instances": [container],
                "execution_evidence": [],
            })
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "review_only",
        "routing_enforced": False,
        "runtime_checked_at": runtime["checked_at"],
        "runtime_revision": runtime.get("revision"),
        "inventory_source": inventory.get("source"),
        "summary": {"declared": len(inventory["services"]), "entries": len(rows),
                    "REAL": 0, "UNKNOWN": len(rows), "SIMULATED": 0, "DEAD": 0},
        "services": rows,
    }


if __name__ == "__main__":
    main()
