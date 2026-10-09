#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "docs" / "production" / "canonical"
REPORT_PATH = ROOT / "docs" / "production" / "CLISONIX_CANONICAL_MANIFEST.md"

SKIP_DIRS = {
    ".git",
    ".next",
    ".vs",
    "node_modules",
    "__pycache__",
    ".venv",
    ".venv313",
    "venv",
    "env",
    "env1",
    "env2",
    "env3",
    "backups",
    "external",
    "_imports",
    "_profile_repos",
    "kloud-soc-clean",
    ".mypy_cache",
    ".pytest_cache",
}

SIGNAL_HINTS = {
    "signal",
    "signals",
    "telemetry",
    "stream",
    "webhook",
    "heartbeat",
    "pulse",
    "metrics",
    "status",
    "event",
    "events",
}


@dataclass
class FileEntry:
    path: str
    size_bytes: int
    extension: str


@dataclass
class EndpointEntry:
    method: str
    route: str
    source_file: str
    source_type: str


@dataclass
class ServiceEntry:
    compose_file: str
    service: str


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def walk_files() -> list[FileEntry]:
    entries: list[FileEntry] = []
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        entries.append(
            FileEntry(
                path=rel(p),
                size_bytes=p.stat().st_size,
                extension=p.suffix.lower(),
            )
        )
    entries.sort(key=lambda x: x.path)
    return entries


def list_compose_files() -> list[Path]:
    files = [
        p
        for p in ROOT.rglob("docker-compose*.yml")
        if p.is_file() and not any(part in SKIP_DIRS for part in p.parts)
    ]
    files.sort()
    return files


def parse_compose_services(compose_file: Path) -> list[ServiceEntry]:
    text = compose_file.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()

    in_services = False
    base_indent = None
    services: list[ServiceEntry] = []

    for raw in lines:
        line = raw.rstrip("\n")
        if not line.strip() or line.strip().startswith("#"):
            continue

        if re.match(r"^services\s*:\s*$", line):
            in_services = True
            base_indent = None
            continue

        if not in_services:
            continue

        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()

        if base_indent is None and re.match(r"^[A-Za-z0-9_.-]+\s*:\s*$", stripped):
            base_indent = indent

        if base_indent is None:
            continue

        if indent < base_indent:
            break

        if indent == base_indent and re.match(r"^[A-Za-z0-9_.-]+\s*:\s*$", stripped):
            service_name = stripped.split(":", 1)[0].strip()
            services.append(ServiceEntry(compose_file=rel(compose_file), service=service_name))

    return services


def py_endpoints(file_path: Path) -> Iterable[EndpointEntry]:
    text = file_path.read_text(encoding="utf-8", errors="ignore")
    pattern = re.compile(
        r"@(?:[A-Za-z_][A-Za-z0-9_]*\.)?(get|post|put|delete|patch|options|head)\(\s*[\"\']([^\"\']+)[\"\']",
        re.IGNORECASE,
    )
    for method, route in pattern.findall(text):
        yield EndpointEntry(
            method=method.upper(),
            route=route,
            source_file=rel(file_path),
            source_type="python",
        )


def next_api_base_from_path(file_path: Path) -> str:
    s = rel(file_path)
    prefix = "apps/web/app/api/"
    if not s.startswith(prefix):
        return ""

    rest = s[len(prefix) :]
    if not rest.endswith("/route.ts"):
        return ""

    rest = rest[: -len("/route.ts")]
    parts = rest.split("/")
    normalized: list[str] = []
    for part in parts:
        if part.startswith("[[...") and part.endswith("]]"):
            normalized.append(":" + part[5:-2] + "*")
        elif part.startswith("[...") and part.endswith("]"):
            normalized.append(":" + part[4:-1] + "*")
        elif part.startswith("[") and part.endswith("]"):
            normalized.append(":" + part[1:-1])
        else:
            normalized.append(part)
    return "/api/" + "/".join(normalized)


def ts_endpoints(file_path: Path) -> Iterable[EndpointEntry]:
    text = file_path.read_text(encoding="utf-8", errors="ignore")
    base = next_api_base_from_path(file_path)
    if not base:
        return

    for method in ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]:
        if re.search(rf"export\s+async\s+function\s+{method}\s*\(", text):
            yield EndpointEntry(
                method=method,
                route=base,
                source_file=rel(file_path),
                source_type="next-route",
            )


def collect_endpoints() -> list[EndpointEntry]:
    endpoints: list[EndpointEntry] = []
    for p in ROOT.rglob("*.py"):
        if p.is_file() and not any(part in SKIP_DIRS for part in p.parts):
            endpoints.extend(py_endpoints(p))

    for p in ROOT.rglob("route.ts"):
        if p.is_file() and not any(part in SKIP_DIRS for part in p.parts):
            endpoints.extend(ts_endpoints(p))

    unique = {(e.method, e.route, e.source_file, e.source_type): e for e in endpoints}
    out = list(unique.values())
    out.sort(key=lambda x: (x.route, x.method, x.source_file))
    return out


def collect_signal_surfaces(endpoints: list[EndpointEntry]) -> list[EndpointEntry]:
    out: list[EndpointEntry] = []
    for e in endpoints:
        low = f"{e.route} {e.source_file}".lower()
        if any(h in low for h in SIGNAL_HINTS):
            out.append(e)
    out.sort(key=lambda x: (x.route, x.method, x.source_file))
    return out


def ext_distribution(files: list[FileEntry]) -> list[tuple[str, int]]:
    counts: dict[str, int] = {}
    for f in files:
        ext = f.extension or "[no-ext]"
        counts[ext] = counts.get(ext, 0) + 1
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")


def write_report(
    files: list[FileEntry],
    services: list[ServiceEntry],
    endpoints: list[EndpointEntry],
    signals: list[EndpointEntry],
) -> None:
    generated_at = datetime.now(timezone.utc).isoformat()
    ext_top = ext_distribution(files)[:25]
    service_files = sorted({s.compose_file for s in services})

    lines: list[str] = []
    lines.append("# CLISONIX Canonical Platform Manifest")
    lines.append("")
    lines.append("Generated automatically from repository state.")
    lines.append("")
    lines.append(f"- Generated at (UTC): {generated_at}")
    lines.append(f"- Total files: {len(files)}")
    lines.append(f"- Total services (compose): {len(services)}")
    lines.append(f"- Total endpoints: {len(endpoints)}")
    lines.append(f"- Total signal-related surfaces: {len(signals)}")
    lines.append("")
    lines.append("## Canonical Inventories")
    lines.append("")
    lines.append("- docs/production/canonical/files_inventory.json")
    lines.append("- docs/production/canonical/services_inventory.json")
    lines.append("- docs/production/canonical/endpoints_inventory.json")
    lines.append("- docs/production/canonical/signals_inventory.json")
    lines.append("")
    lines.append("## Service Sources")
    lines.append("")
    for f in service_files:
        lines.append(f"- {f}")
    lines.append("")
    lines.append("## Top File Extensions")
    lines.append("")
    lines.append("| Extension | Count |")
    lines.append("|---|---:|")
    for ext, count in ext_top:
        lines.append(f"| {ext} | {count} |")
    lines.append("")
    lines.append("## Largest Files (Top 50)")
    lines.append("")
    lines.append("| File | Size (bytes) |")
    lines.append("|---|---:|")
    for f in sorted(files, key=lambda x: x.size_bytes, reverse=True)[:50]:
        lines.append(f"| {f.path} | {f.size_bytes} |")
    lines.append("")
    lines.append("## Endpoint Coverage Snapshot (Top 200)")
    lines.append("")
    lines.append("| Method | Route | Source | Type |")
    lines.append("|---|---|---|---|")
    for e in endpoints[:200]:
        lines.append(f"| {e.method} | {e.route} | {e.source_file} | {e.source_type} |")
    lines.append("")
    lines.append("## Signal Surfaces Snapshot (Top 200)")
    lines.append("")
    lines.append("| Method | Route | Source |")
    lines.append("|---|---|---|")
    for e in signals[:200]:
        lines.append(f"| {e.method} | {e.route} | {e.source_file} |")
    lines.append("")
    lines.append("## Integrity Policy")
    lines.append("")
    lines.append("- No fake data fallback in inventories.")
    lines.append("- Inventories are generated from real files only.")
    lines.append("- Re-run script after each structural change.")

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    files = walk_files()
    compose_files = list_compose_files()
    services: list[ServiceEntry] = []
    for cf in compose_files:
        services.extend(parse_compose_services(cf))

    # Keep deterministic order and de-duplicate service tuples.
    unique_services = {
        (s.compose_file, s.service): s for s in services
    }
    services = list(unique_services.values())
    services.sort(key=lambda x: (x.compose_file, x.service))

    endpoints = collect_endpoints()
    signals = collect_signal_surfaces(endpoints)

    write_json(OUTPUT_DIR / "files_inventory.json", [asdict(f) for f in files])
    write_json(OUTPUT_DIR / "services_inventory.json", [asdict(s) for s in services])
    write_json(OUTPUT_DIR / "endpoints_inventory.json", [asdict(e) for e in endpoints])
    write_json(OUTPUT_DIR / "signals_inventory.json", [asdict(s) for s in signals])
    write_report(files, services, endpoints, signals)

    print(f"Generated: {REPORT_PATH.relative_to(ROOT)}")
    print(f"Generated: {(OUTPUT_DIR / 'files_inventory.json').relative_to(ROOT)}")
    print(f"Generated: {(OUTPUT_DIR / 'services_inventory.json').relative_to(ROOT)}")
    print(f"Generated: {(OUTPUT_DIR / 'endpoints_inventory.json').relative_to(ROOT)}")
    print(f"Generated: {(OUTPUT_DIR / 'signals_inventory.json').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
