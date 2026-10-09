#!/usr/bin/env python3
"""Generate one unified OpenAPI spec by discovering multiple Clisonix APIs.

Scans configured hosts/ports, fetches /openapi.json (or /api/openapi.json),
and merges paths/components into a single OpenAPI document.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import requests

DEFAULT_HOSTS = [
    "127.0.0.1",
    "localhost",
    "clisonix-api",
    "clisonix-reporting",
    "clisonix-ocean-core",
    "clisonix-alba",
    "clisonix-albi",
    "clisonix-jona",
]

DEFAULT_PORTS = [8000, 8001, 8002, 8010, 8030, 5555, 6680, 7777]
DEFAULT_PATHS = ["/openapi.json", "/api/openapi.json"]

COMPONENT_CATEGORIES = [
    "schemas",
    "parameters",
    "responses",
    "requestBodies",
    "headers",
    "securitySchemes",
    "examples",
    "links",
    "callbacks",
]


@dataclass
class DiscoveredSpec:
    service_name: str
    source_url: str
    spec: Dict[str, Any]


def _csv_env(name: str, fallback: Iterable[str]) -> List[str]:
    raw = (os.getenv(name) or "").strip()
    if not raw:
        return list(fallback)
    values = [v.strip() for v in raw.split(",") if v.strip()]
    return values or list(fallback)


def _csv_int_env(name: str, fallback: Iterable[int]) -> List[int]:
    raw = (os.getenv(name) or "").strip()
    if not raw:
        return list(fallback)
    values: List[int] = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        try:
            values.append(int(item))
        except ValueError:
            continue
    return values or list(fallback)


def _normalize_name(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_").lower()
    return normalized or "service"


def _build_service_name(host: str, port: int) -> str:
    host_name = _normalize_name(host.replace("http://", "").replace("https://", ""))
    return f"{host_name}_{port}"


def _parse_service_urls(raw_items: List[str]) -> List[Tuple[str, str]]:
    parsed: List[Tuple[str, str]] = []
    for item in raw_items:
        if "=" in item:
            name, url = item.split("=", 1)
            name = _normalize_name(name)
            url = url.strip()
        else:
            url = item.strip()
            name = _normalize_name(url)
        if not url:
            continue
        parsed.append((name, url.rstrip("/")))
    return parsed


def _discover_openapi(
    hosts: List[str],
    ports: List[int],
    paths: List[str],
    service_urls: List[Tuple[str, str]],
    timeout: float,
) -> List[DiscoveredSpec]:
    discovered: List[DiscoveredSpec] = []
    seen_sources: set[str] = set()

    candidates: List[Tuple[str, str]] = []
    for service_name, base_url in service_urls:
        candidates.append((service_name, base_url))

    for host in hosts:
        host = host.strip()
        if not host:
            continue
        if host.startswith("http://") or host.startswith("https://"):
            for port in ports:
                scheme_host = host.rstrip("/")
                candidates.append((_build_service_name(scheme_host, port), f"{scheme_host}:{port}"))
        else:
            for port in ports:
                candidates.append((_build_service_name(host, port), f"http://{host}:{port}"))

    for service_name, base_url in candidates:
        for path in paths:
            if not path.startswith("/"):
                path = "/" + path
            endpoint = f"{base_url}{path}"
            if endpoint in seen_sources:
                continue
            seen_sources.add(endpoint)

            try:
                response = requests.get(endpoint, timeout=timeout)
            except Exception:
                continue

            if response.status_code != 200:
                continue

            try:
                payload = response.json()
            except Exception:
                continue

            if not isinstance(payload, dict) or "openapi" not in payload or "paths" not in payload:
                continue

            discovered.append(
                DiscoveredSpec(
                    service_name=service_name,
                    source_url=endpoint,
                    spec=payload,
                )
            )
            break

    return discovered


def _rewrite_refs(value: Any, ref_maps: Dict[str, Dict[str, str]]) -> Any:
    if isinstance(value, dict):
        rewritten: Dict[str, Any] = {}
        for key, val in value.items():
            if key == "$ref" and isinstance(val, str) and val.startswith("#/components/"):
                parts = val.split("/")
                if len(parts) == 4:
                    category = parts[2]
                    old_name = parts[3]
                    new_name = ref_maps.get(category, {}).get(old_name)
                    if new_name:
                        rewritten[key] = f"#/components/{category}/{new_name}"
                        continue
            rewritten[key] = _rewrite_refs(val, ref_maps)
        return rewritten
    if isinstance(value, list):
        return [_rewrite_refs(item, ref_maps) for item in value]
    return value


def _ensure_operation_ids(path_item: Dict[str, Any], service_prefix: str) -> None:
    for method, operation in path_item.items():
        if not isinstance(operation, dict):
            continue
        if method.lower() not in {"get", "post", "put", "patch", "delete", "head", "options", "trace"}:
            continue
        op_id = str(operation.get("operationId") or "").strip()
        if op_id:
            operation["operationId"] = f"{service_prefix}_{op_id}"


def _merge_specs(discovered: List[DiscoveredSpec]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {
        "openapi": "3.1.0",
        "info": {
            "title": "Clisonix Unified Multi-Port API",
            "version": datetime.now(timezone.utc).strftime("%Y.%m.%d.%H%M%S"),
            "description": "Unified OpenAPI generated from multiple Clisonix service ports.",
        },
        "servers": [],
        "paths": {},
        "components": {cat: {} for cat in COMPONENT_CATEGORIES},
        "tags": [],
        "x-generated-at": datetime.now(timezone.utc).isoformat(),
        "x-services": [],
        "x-conflicts": [],
    }

    used_tags: set[str] = set()

    for item in discovered:
        spec = item.spec
        service_prefix = _normalize_name(item.service_name)

        merged["x-services"].append(
            {
                "service": item.service_name,
                "source": item.source_url,
                "title": spec.get("info", {}).get("title", "unknown"),
                "version": spec.get("info", {}).get("version", "unknown"),
                "paths": len(spec.get("paths", {}) or {}),
            }
        )

        merged["servers"].append({"url": item.source_url.rsplit("/", 1)[0], "description": item.service_name})

        # Build per-service component rename maps.
        ref_maps: Dict[str, Dict[str, str]] = {cat: {} for cat in COMPONENT_CATEGORIES}
        source_components = spec.get("components") if isinstance(spec.get("components"), dict) else {}

        for category in COMPONENT_CATEGORIES:
            source_items = source_components.get(category)
            if not isinstance(source_items, dict):
                continue
            for old_name, schema in source_items.items():
                new_name = f"{service_prefix}__{old_name}"
                ref_maps[category][old_name] = new_name
                merged["components"][category][new_name] = _rewrite_refs(copy.deepcopy(schema), ref_maps)

        # Merge tags with service prefix to keep docs clear.
        for tag in spec.get("tags", []) or []:
            if not isinstance(tag, dict):
                continue
            name = str(tag.get("name") or "").strip()
            if not name:
                continue
            merged_name = f"{service_prefix}:{name}"
            if merged_name in used_tags:
                continue
            used_tags.add(merged_name)
            tag_copy = copy.deepcopy(tag)
            tag_copy["name"] = merged_name
            merged["tags"].append(tag_copy)

        # Merge paths and rewrite refs + operationIds.
        source_paths = spec.get("paths") if isinstance(spec.get("paths"), dict) else {}
        for path, path_item in source_paths.items():
            if not isinstance(path_item, dict):
                continue

            rewritten_item = _rewrite_refs(copy.deepcopy(path_item), ref_maps)

            # Prefix tags inside operations to match merged tag names.
            for method, op in rewritten_item.items():
                if not isinstance(op, dict):
                    continue
                tags = op.get("tags")
                if isinstance(tags, list):
                    op["tags"] = [f"{service_prefix}:{t}" for t in tags]

            _ensure_operation_ids(rewritten_item, service_prefix)
            rewritten_item["x-source-service"] = item.service_name
            rewritten_item["x-source-openapi"] = item.source_url

            if path not in merged["paths"]:
                merged["paths"][path] = rewritten_item
                continue

            namespaced_path = f"/{service_prefix}{path if path.startswith('/') else '/' + path}"
            if namespaced_path in merged["paths"]:
                namespaced_path = f"{namespaced_path}__dup"

            merged["paths"][namespaced_path] = rewritten_item
            merged["x-conflicts"].append(
                {
                    "path": path,
                    "resolved_as": namespaced_path,
                    "service": item.service_name,
                }
            )

    return merged


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate unified OpenAPI from multi-port services.")
    parser.add_argument("--hosts", default=",".join(_csv_env("OPENAPI_DISCOVERY_HOSTS", DEFAULT_HOSTS)))
    parser.add_argument("--ports", default=",".join(str(p) for p in _csv_int_env("OPENAPI_DISCOVERY_PORTS", DEFAULT_PORTS)))
    parser.add_argument("--paths", default=",".join(_csv_env("OPENAPI_DISCOVERY_PATHS", DEFAULT_PATHS)))
    parser.add_argument(
        "--service-urls",
        default=os.getenv("OPENAPI_SERVICE_URLS", ""),
        help="Comma-separated name=url pairs (or raw URLs), e.g. api=http://127.0.0.1:8000",
    )
    parser.add_argument("--timeout", type=float, default=float(os.getenv("OPENAPI_DISCOVERY_TIMEOUT", "2.5")))
    parser.add_argument(
        "--output",
        default=os.getenv("OPENAPI_AGGREGATE_OUTPUT", "openapi.unified.json"),
        help="Output JSON file",
    )
    parser.add_argument("--fail-if-empty", action="store_true", help="Return non-zero if no specs discovered")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()

    hosts = [h.strip() for h in args.hosts.split(",") if h.strip()]
    ports = [int(p.strip()) for p in args.ports.split(",") if p.strip()]
    paths = [p.strip() for p in args.paths.split(",") if p.strip()]
    service_url_items = [item.strip() for item in args.service_urls.split(",") if item.strip()]
    service_urls = _parse_service_urls(service_url_items)

    discovered = _discover_openapi(
        hosts=hosts,
        ports=ports,
        paths=paths,
        service_urls=service_urls,
        timeout=args.timeout,
    )

    if not discovered:
        print("No OpenAPI specs discovered.")
        if args.fail_if_empty:
            return 2

    merged = _merge_specs(discovered)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Discovered specs: {len(discovered)}")
    for spec in discovered:
        title = spec.spec.get("info", {}).get("title", "unknown")
        print(f" - {spec.service_name}: {spec.source_url} ({title})")
    print(f"Merged paths: {len(merged.get('paths', {}))}")
    print(f"Output: {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
