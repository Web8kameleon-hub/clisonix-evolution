#!/usr/bin/env python3
"""Generate daily public package catalog (npm, PyPI, Cargo/Carter)."""

from __future__ import annotations

import argparse
import datetime as dt
import importlib
import json
import re
from pathlib import Path
from typing import Any

try:
    TOMLLIB: Any = importlib.import_module("tomllib")
except Exception:
    TOMLLIB = None

EXCLUDE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".idea",
    ".vscode",
    ".vs",
    "external",
    "_imports",
}

API_SCAN_EXTENSIONS = {".py", ".js", ".ts", ".tsx", ".jsx"}
PROTOCOL_RE = re.compile(r"\b(https?|wss?|grpc|mqtt|redis|amqp|kafka)://[^\s'\"<>]+", re.IGNORECASE)
FASTAPI_ROUTE_RE = re.compile(
    r"@app\.(get|post|put|patch|delete|options|head)\(\s*[\"']([^\"']+)[\"']",
    re.IGNORECASE,
)
EXPRESS_ROUTE_RE = re.compile(
    r"\b(?:app|router)\.(get|post|put|patch|delete|options|head)\(\s*[\"']([^\"']+)[\"']",
    re.IGNORECASE,
)


def is_excluded(path: Path, root: Path) -> bool:
    try:
        rel_parts = path.relative_to(root).parts
    except Exception:
        return True
    return any(part in EXCLUDE_DIRS for part in rel_parts)


def split_dep(dep: str) -> tuple[str, str]:
    dep = dep.strip()
    m = re.match(r"^([A-Za-z0-9_.\-]+)\s*(.*)$", dep)
    if not m:
        return dep, "unspecified"
    name = m.group(1)
    version = m.group(2).strip() or "unspecified"
    return name, version


def collect_npm_packages(root: Path) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for path in root.rglob("package.json"):
        if is_excluded(path, root):
            continue
        try:
            pkg = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            continue

        for section in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
            deps = pkg.get(section) or {}
            if not isinstance(deps, dict):
                continue
            for name, version in deps.items():
                entries.append(
                    {
                        "file": str(path.relative_to(root)).replace("\\", "/"),
                        "ecosystem": "npm",
                        "section": section,
                        "name": str(name),
                        "version": str(version),
                    }
                )
    return entries


def parse_requirements_file(path: Path) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("-r") or line.startswith("--"):
            continue
        line = line.split("#", 1)[0].strip()
        m = re.match(r"^([A-Za-z0-9_.\-]+)\s*([<>=!~].+)?$", line)
        if m:
            out.append((m.group(1), (m.group(2) or "").strip() or "unspecified"))
    return out


def collect_pypi_packages(root: Path) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []

    for path in root.rglob("requirements*.txt"):
        if is_excluded(path, root):
            continue
        try:
            reqs = parse_requirements_file(path)
        except Exception:
            continue
        for name, version in reqs:
            entries.append(
                {
                    "file": str(path.relative_to(root)).replace("\\", "/"),
                    "ecosystem": "pypi",
                    "section": "requirements",
                    "name": name,
                    "version": version,
                }
            )

    if TOMLLIB is not None:
        for path in root.rglob("pyproject.toml"):
            if is_excluded(path, root):
                continue
            try:
                data = TOMLLIB.loads(path.read_text(encoding="utf-8", errors="ignore"))
            except Exception:
                continue
            if not isinstance(data, dict):
                continue

            project = data.get("project")
            if isinstance(project, dict):
                deps = project.get("dependencies") or []
                if isinstance(deps, list):
                    for dep in deps:
                        if isinstance(dep, str):
                            name, version = split_dep(dep)
                            entries.append(
                                {
                                    "file": str(path.relative_to(root)).replace("\\", "/"),
                                    "ecosystem": "pypi",
                                    "section": "project.dependencies",
                                    "name": name,
                                    "version": version,
                                }
                            )
                optional = project.get("optional-dependencies") or {}
                if isinstance(optional, dict):
                    for group, dep_list in optional.items():
                        if not isinstance(dep_list, list):
                            continue
                        for dep in dep_list:
                            if isinstance(dep, str):
                                name, version = split_dep(dep)
                                entries.append(
                                    {
                                        "file": str(path.relative_to(root)).replace("\\", "/"),
                                        "ecosystem": "pypi",
                                        "section": f"project.optional-dependencies.{group}",
                                        "name": name,
                                        "version": version,
                                    }
                                )
    return entries


def collect_cargo_packages(root: Path) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    if TOMLLIB is None:
        return entries

    for path in root.rglob("Cargo.toml"):
        if is_excluded(path, root):
            continue
        try:
            data = TOMLLIB.loads(path.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            continue
        if not isinstance(data, dict):
            continue

        for section in ("dependencies", "dev-dependencies", "build-dependencies"):
            deps = data.get(section)
            if not isinstance(deps, dict):
                continue
            for name, value in deps.items():
                version = "unspecified"
                if isinstance(value, str):
                    version = value
                elif isinstance(value, dict):
                    version = str(value.get("version", "unspecified"))
                entries.append(
                    {
                        "file": str(path.relative_to(root)).replace("\\", "/"),
                        "ecosystem": "cargo",
                        "section": section,
                        "name": str(name),
                        "version": version,
                    }
                )
    return entries


def summarize(items: list[dict[str, str]]) -> tuple[int, int]:
    names = {item["name"] for item in items}
    return len(items), len(names)


def collect_recursive_scan_stats(root: Path) -> dict[str, Any]:
    files = 0
    dirs: set[str] = set()
    max_depth = 0
    for path in root.rglob("*"):
        if is_excluded(path, root):
            continue
        try:
            rel = path.relative_to(root)
        except Exception:
            continue
        depth = len(rel.parts)
        if depth > max_depth:
            max_depth = depth
        if path.is_file():
            files += 1
            dirs.add(str(rel.parent).replace("\\", "/"))
    return {
        "files_scanned": files,
        "directories_scanned": len([d for d in dirs if d not in {"", "."}]),
        "max_depth": max_depth,
    }


def collect_api_routes(root: Path, limit: int = 500) -> list[dict[str, str]]:
    routes: list[dict[str, str]] = []
    for path in root.rglob("*"):
        if not path.is_file() or is_excluded(path, root):
            continue
        if path.suffix.lower() not in API_SCAN_EXTENSIONS:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        rel = str(path.relative_to(root)).replace("\\", "/")
        patterns = [FASTAPI_ROUTE_RE] if path.suffix.lower() == ".py" else [EXPRESS_ROUTE_RE]
        for line_no, line in enumerate(text.splitlines(), start=1):
            for pattern in patterns:
                for m in pattern.finditer(line):
                    method = str(m.group(1) or "").upper()
                    route = str(m.group(2) or "").strip()
                    if not method or not route:
                        continue
                    routes.append(
                        {
                            "method": method,
                            "route": route,
                            "file": rel,
                            "line": str(line_no),
                        }
                    )
                    if len(routes) >= limit:
                        return routes
    return routes


def collect_protocol_endpoints(root: Path, limit: int = 200) -> list[dict[str, str]]:
    endpoints: list[dict[str, str]] = []
    for path in root.rglob("*"):
        if not path.is_file() or is_excluded(path, root):
            continue
        if path.suffix.lower() not in API_SCAN_EXTENSIONS | {".yml", ".yaml", ".json", ".env", ".toml", ".md"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        rel = str(path.relative_to(root)).replace("\\", "/")
        for m in PROTOCOL_RE.finditer(text):
            url = m.group(0).strip()
            scheme = url.split(":", 1)[0].lower()
            endpoints.append({"protocol": scheme, "endpoint": url[:120], "file": rel})
            if len(endpoints) >= limit:
                return endpoints
    return endpoints


def list_existing_paths(root: Path, candidates: list[str]) -> list[str]:
    existing: list[str] = []
    for rel in candidates:
        p = root / rel
        if p.exists():
            existing.append(rel)
    return existing


def collect_named_paths(root: Path, keyword: str, limit: int = 50) -> list[str]:
    out: list[str] = []
    key = keyword.lower()
    for path in root.rglob("*"):
        if is_excluded(path, root):
            continue
        if key not in str(path).lower():
            continue
        if not path.is_file():
            continue
        out.append(str(path.relative_to(root)).replace("\\", "/"))
        if len(out) >= limit:
            break
    return out


def filter_routes(routes: list[dict[str, str]], terms: list[str], limit: int = 60) -> list[dict[str, str]]:
    terms_l = [t.lower() for t in terms]
    out: list[dict[str, str]] = []
    for route in routes:
        route_path = route.get("route", "").lower()
        route_file = route.get("file", "").lower()
        if any(term in route_path or term in route_file for term in terms_l):
            out.append(route)
            if len(out) >= limit:
                break
    return out


def build_growth_tracks(root: Path, routes: list[dict[str, str]]) -> dict[str, Any]:
    install_docs = list_existing_paths(
        root,
        [
            "README.md",
            "apps/web/README.md",
            "CLX_AI_INSTALLATION_GUIDE.md",
            "sdk/python/README.md",
            "sdk/typescript/README.md",
            "hardware/kloud-soc/README.md",
            "scripts/hardware/rust_node_agent/README.md",
        ],
    )
    license_docs = list_existing_paths(
        root,
        [
            "LICENSE",
            "clx-ai/LICENSE",
            "sdk/python/LICENSE",
            "sdk/typescript/LICENSE",
            "docs/legal/WWWMMM_IP_MEMO.md",
        ],
    )
    monetization_docs = list_existing_paths(
        root,
        [
            "docs/API_MONETIZATION_GUIDE.md",
            "MONETIZATION_30DAY_PLAN.md",
            "docs/BUSINESS_STRATEGY.md",
        ],
    )

    agimed_routes = filter_routes(routes, ["agimed"])
    iot_mesh_routes = filter_routes(routes, ["iot", "mesh"])
    mirror_routes = filter_routes(routes, ["mymirror", "mirror", "defence", "defense"])
    mirror_files = collect_named_paths(root, "mymirror")
    hardware_files = collect_named_paths(root, "hardware")

    return {
        "install_docs": install_docs,
        "api_tracks": {
            "agimed": agimed_routes,
            "iot_mesh": iot_mesh_routes,
            "mirror_defence": mirror_routes,
        },
        "hardware_tracks": {
            "hardware_paths": hardware_files,
            "mirror_paths": mirror_files,
        },
        "creator_protection": {
            "license_docs": license_docs,
            "monetization_docs": monetization_docs,
        },
    }


def top_unique(items: list[dict[str, str]], top_n: int = 20) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in sorted(items, key=lambda x: (x["name"], x["file"])):
        name = item["name"]
        if name in seen:
            continue
        seen.add(name)
        out.append(item)
        if len(out) >= top_n:
            break
    return out


def render_table(rows: list[list[str]], headers: list[str]) -> str:
    if not rows:
        return "_No data found._\n"
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines) + "\n"


def build_report(root: Path) -> str:
    ts = dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    npm = collect_npm_packages(root)
    pypi = collect_pypi_packages(root)
    cargo = collect_cargo_packages(root)
    routes = collect_api_routes(root)
    protocol_endpoints = collect_protocol_endpoints(root)
    scan_stats = collect_recursive_scan_stats(root)
    growth_tracks = build_growth_tracks(root, routes)

    npm_total, npm_unique = summarize(npm)
    pypi_total, pypi_unique = summarize(pypi)
    cargo_total, cargo_unique = summarize(cargo)
    route_total = len(routes)
    protocol_total = len({item["protocol"] for item in protocol_endpoints})

    lines: list[str] = []
    lines.append("# Daily Public Package Catalog")
    lines.append("")
    lines.append(f"Generated: {ts}")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- npm packages (records/unique): {npm_total}/{npm_unique}")
    lines.append(f"- PyPI packages (records/unique): {pypi_total}/{pypi_unique}")
    lines.append(f"- Cargo/Carter packages (records/unique): {cargo_total}/{cargo_unique}")
    lines.append(f"- API routes discovered: {route_total}")
    lines.append(f"- Protocols discovered: {protocol_total}")
    lines.append(f"- Recursive scan files/directories/depth: {scan_stats['files_scanned']}/{scan_stats['directories_scanned']}/{scan_stats['max_depth']}")
    lines.append("")

    lines.append("## Download & Integration Quick Links")
    npm_top = top_unique(npm, top_n=15)
    pypi_top = top_unique(pypi, top_n=15)
    cargo_top = top_unique(cargo, top_n=15)
    dl_rows: list[list[str]] = []
    for item in npm_top:
        dl_rows.append(["npm", item["name"], f"https://www.npmjs.com/package/{item['name']}", f"npm i {item['name']}"])
    for item in pypi_top:
        dl_rows.append(["pypi", item["name"], f"https://pypi.org/project/{item['name']}/", f"pip install {item['name']}"])
    for item in cargo_top:
        dl_rows.append(["cargo", item["name"], f"https://crates.io/crates/{item['name']}", f"cargo add {item['name']}"])
    lines.append(render_table(dl_rows, ["ecosystem", "package", "download_url", "install_command"]))

    lines.append("## API Inventory")
    api_rows = [[r["method"], r["route"], r["file"], r["line"]] for r in routes[:400]]
    lines.append(render_table(api_rows, ["method", "route", "file", "line"]))

    lines.append("## Protocol Matrix")
    protocol_rows = [[p["protocol"], p["endpoint"], p["file"]] for p in sorted(protocol_endpoints, key=lambda x: (x["protocol"], x["endpoint"]))[:250]]
    lines.append(render_table(protocol_rows, ["protocol", "endpoint", "file"]))

    lines.append("## CLX Mass Adoption Tracks")
    lines.append("### Install Paths")
    install_rows = [[p] for p in growth_tracks["install_docs"]]
    lines.append(render_table(install_rows, ["path"]))

    lines.append("### API: AGIMED")
    agimed_rows = [[r["method"], r["route"], r["file"], r["line"]] for r in growth_tracks["api_tracks"]["agimed"]]
    lines.append(render_table(agimed_rows, ["method", "route", "file", "line"]))

    lines.append("### API: IoT Mesh")
    iot_rows = [[r["method"], r["route"], r["file"], r["line"]] for r in growth_tracks["api_tracks"]["iot_mesh"]]
    lines.append(render_table(iot_rows, ["method", "route", "file", "line"]))

    lines.append("### MyMirror Defence")
    mirror_route_rows = [[r["method"], r["route"], r["file"], r["line"]] for r in growth_tracks["api_tracks"]["mirror_defence"]]
    lines.append(render_table(mirror_route_rows, ["method", "route", "file", "line"]))
    mirror_path_rows = [[p] for p in growth_tracks["hardware_tracks"]["mirror_paths"]]
    lines.append(render_table(mirror_path_rows, ["path"]))

    lines.append("### CLX Hardware & Chips")
    hardware_rows = [[p] for p in growth_tracks["hardware_tracks"]["hardware_paths"]]
    lines.append(render_table(hardware_rows, ["path"]))

    lines.append("### Creator License & Profit Protection")
    license_rows = [[p] for p in growth_tracks["creator_protection"]["license_docs"]]
    monetization_rows = [[p] for p in growth_tracks["creator_protection"]["monetization_docs"]]
    lines.append("License references:")
    lines.append(render_table(license_rows, ["path"]))
    lines.append("Monetization references:")
    lines.append(render_table(monetization_rows, ["path"]))

    lines.append("## npm Snapshot")
    npm_rows = [[i["name"], i["version"], i["section"], i["file"]] for i in sorted(npm, key=lambda x: (x["name"], x["file"]))[:500]]
    lines.append(render_table(npm_rows, ["name", "version", "section", "file"]))

    lines.append("## PyPI Snapshot")
    pypi_rows = [[i["name"], i["version"], i["section"], i["file"]] for i in sorted(pypi, key=lambda x: (x["name"], x["file"]))[:500]]
    lines.append(render_table(pypi_rows, ["name", "version", "section", "file"]))

    lines.append("## Cargo/Carter Snapshot")
    cargo_rows = [[i["name"], i["version"], i["section"], i["file"]] for i in sorted(cargo, key=lambda x: (x["name"], x["file"]))[:500]]
    lines.append(render_table(cargo_rows, ["name", "version", "section", "file"]))

    lines.append("## Notes")
    lines.append("- This report is intentionally package-only for public integration visibility.")
    lines.append("- No secret/key scanning is included in this workflow.")
    lines.append("- API/protocol sections are auto-extracted via recursive scan from source files.")
    lines.append("")
    return "\n".join(lines)


def build_payload(root: Path) -> dict[str, Any]:
    ts = dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    npm = collect_npm_packages(root)
    pypi = collect_pypi_packages(root)
    cargo = collect_cargo_packages(root)
    routes = collect_api_routes(root)
    protocols = collect_protocol_endpoints(root)
    scan_stats = collect_recursive_scan_stats(root)
    growth_tracks = build_growth_tracks(root, routes)

    npm_total, npm_unique = summarize(npm)
    pypi_total, pypi_unique = summarize(pypi)
    cargo_total, cargo_unique = summarize(cargo)

    return {
        "generated_at": ts,
        "summary": {
            "npm": {"records": npm_total, "unique": npm_unique},
            "pypi": {"records": pypi_total, "unique": pypi_unique},
            "cargo": {"records": cargo_total, "unique": cargo_unique},
            "api_routes_discovered": len(routes),
            "protocols_discovered": len({item["protocol"] for item in protocols}),
            "recursive_scan": scan_stats,
        },
        "top_download_links": {
            "npm": [
                {
                    "name": item["name"],
                    "version": item["version"],
                    "url": f"https://www.npmjs.com/package/{item['name']}",
                    "install": f"npm i {item['name']}",
                }
                for item in top_unique(npm, 20)
            ],
            "pypi": [
                {
                    "name": item["name"],
                    "version": item["version"],
                    "url": f"https://pypi.org/project/{item['name']}/",
                    "install": f"pip install {item['name']}",
                }
                for item in top_unique(pypi, 20)
            ],
            "cargo": [
                {
                    "name": item["name"],
                    "version": item["version"],
                    "url": f"https://crates.io/crates/{item['name']}",
                    "install": f"cargo add {item['name']}",
                }
                for item in top_unique(cargo, 20)
            ],
        },
        "api_inventory": routes[:300],
        "protocol_matrix": protocols[:200],
        "growth_tracks": growth_tracks,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--out", default=".github/reports/daily-package-catalog.md")
    parser.add_argument("--json-out", default="")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out = Path(args.out)
    if not out.is_absolute():
        out = root / out
    out.parent.mkdir(parents=True, exist_ok=True)

    out.write_text(build_report(root), encoding="utf-8")
    print(f"Report written: {out}")

    json_out_raw = (args.json_out or "").strip()
    if json_out_raw:
        json_out = Path(json_out_raw)
        if not json_out.is_absolute():
            json_out = root / json_out
        json_out.parent.mkdir(parents=True, exist_ok=True)
        payload = build_payload(root)
        json_out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"JSON written: {json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
