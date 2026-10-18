#!/usr/bin/env python3
"""Evaluate every Compose module, then derive MALI's project map from evidence."""
from __future__ import annotations

import argparse
import asyncio
import json
import statistics
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

import yaml


def load_compose(path: Path) -> dict[str, Any]:
    completed = subprocess.run(
        ["docker", "compose", "-f", str(path), "config", "--format", "json"],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode == 0:
        return json.loads(completed.stdout)
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def source_checks(root: Path, definition: dict[str, Any]) -> dict[str, Any]:
    build = definition.get("build")
    if isinstance(build, str):
        context, dockerfile = build, "Dockerfile"
    elif isinstance(build, dict):
        context = str(build.get("context", "."))
        dockerfile = str(build.get("dockerfile", "Dockerfile"))
    else:
        return {
            "declared": True,
            "source_context_exists": None,
            "dockerfile_exists": None,
            "image_declared": bool(definition.get("image")),
        }
    context_path = (root / context).resolve()
    return {
        "declared": True,
        "source_context_exists": context_path.exists(),
        "dockerfile_exists": (context_path / dockerfile).exists(),
        "image_declared": bool(definition.get("image")),
    }


def grade(checks: dict[str, Any], runtime: dict[str, Any]) -> tuple[str, int]:
    applicable = [value for value in checks.values() if isinstance(value, bool)]
    static_ratio = sum(applicable) / max(len(applicable), 1)
    runtime_ok = runtime.get("healthy") is True
    runtime_tested = runtime.get("tested") is True
    score = round(static_ratio * 55 + (45 if runtime_ok else 0))
    if runtime_ok and score >= 90:
        return "A", score
    if runtime_ok and score >= 75:
        return "B", score
    if runtime_tested:
        return "F", score
    return "UNVERIFIED", score


async def probe(url: str, attempts: int, timeout: float) -> dict[str, Any]:
    samples: list[float] = []
    statuses: list[int] = []
    errors: list[str] = []
    for _ in range(attempts):
        started = time.perf_counter()
        try:
            response = await asyncio.to_thread(urlopen, url, timeout=timeout)
            statuses.append(response.status)
            response.read(256)
            samples.append((time.perf_counter() - started) * 1000)
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            errors.append(str(exc))
    healthy = len(samples) == attempts and all(200 <= status < 400 for status in statuses)
    return {
        "tested": True,
        "healthy": healthy,
        "attempts": attempts,
        "successes": len(samples),
        "status_codes": statuses,
        "latency_ms": {
            "min": round(min(samples), 2) if samples else None,
            "median": round(statistics.median(samples), 2) if samples else None,
            "max": round(max(samples), 2) if samples else None,
        },
        "errors": errors[-3:],
    }


async def probe_container(definition: dict[str, Any]) -> dict[str, Any]:
    container = definition.get("container_name")
    if not container:
        return {"tested": False, "healthy": None}
    completed = await asyncio.to_thread(
        subprocess.run,
        ["docker", "container", "inspect", "--format", "{{json .State}}", str(container)],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        return {
            "tested": True,
            "healthy": False,
            "probe_kind": "docker-process",
            "container": container,
            "errors": [completed.stderr.strip() or "container not found"],
        }
    state = json.loads(completed.stdout)
    health = (state.get("Health") or {}).get("Status")
    healthy = state.get("Running") is True and health in (None, "healthy")
    return {
        "tested": True,
        "healthy": healthy,
        "probe_kind": "docker-process",
        "container": container,
        "running": state.get("Running"),
        "health_status": health,
    }


def default_health_url(module_id: str, definition: dict[str, Any]) -> str | None:
    ports = definition.get("ports") or []
    if not ports:
        return None
    first = ports[0]
    if isinstance(first, str):
        host_port = first.split(":")[0]
    elif isinstance(first, dict):
        host_port = str(first.get("published", ""))
    else:
        return None
    return f"http://127.0.0.1:{host_port}/health" if host_port else None


async def evaluate(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any]]:
    root = Path(args.root).resolve()
    compose = load_compose(root / args.compose)
    services: dict[str, dict[str, Any]] = compose.get("services", {})
    overrides = json.loads(Path(args.runtime_urls).read_text()) if args.runtime_urls else {}
    results: dict[str, Any] = {}

    for module_id in sorted(services):
        definition = services[module_id]
        dependencies = definition.get("depends_on") or []
        if isinstance(dependencies, dict):
            dependencies = list(dependencies)
        checks = source_checks(root, definition)
        checks["healthcheck_declared"] = bool(definition.get("healthcheck"))
        checks["dependencies_resolve"] = all(item in services for item in dependencies)
        url = overrides.get(module_id) or (default_health_url(module_id, definition) if args.probe_local else None)
        if url:
            runtime = await probe(url, args.attempts, args.timeout)
        elif args.probe_local and definition.get("healthcheck"):
            runtime = await probe_container(definition)
        else:
            runtime = {"tested": False, "healthy": None}
        module_grade, score = grade(checks, runtime)
        results[module_id] = {
            "module_id": module_id,
            "checks": checks,
            "runtime": runtime,
            "grade": module_grade,
            "score": score,
            "dependencies": dependencies,
            "service": module_id,
            "health_url": url,
            "source_references": {
                key.removeprefix("mali.source."): value
                for key, value in (definition.get("labels") or {}).items()
                if key.startswith("mali.source.")
            },
        }

    generated_at = datetime.now(timezone.utc).isoformat()
    evidence = {
        "spec_version": "mali.module-evaluation/v1",
        "generated_at": generated_at,
        "compose": args.compose,
        "module_count": len(results),
        "runtime_tested": sum(v["runtime"]["tested"] for v in results.values()),
        "grade_counts": {key: sum(v["grade"] == key for v in results.values()) for key in ("A", "B", "F", "UNVERIFIED")},
        "modules": results,
    }
    project_map = {
        "spec_version": "clisonix.project-map/v1",
        "generated_from": "mali.module-evaluation/v1",
        "generated_at": generated_at,
        "project": "clisonix-platform",
        "central_orchestrator": "intelligence-lab",
        "signal_stream": "clisonix:signals:v1",
        "modules": results,
    }
    return evidence, project_map


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--compose", default="docker-compose.yml")
    parser.add_argument("--runtime-urls")
    parser.add_argument("--probe-local", action="store_true")
    parser.add_argument("--attempts", type=int, default=3)
    parser.add_argument("--timeout", type=float, default=3.0)
    parser.add_argument("--evidence", default="artifacts/mali/module-evaluation.json")
    parser.add_argument("--project-map", default="services/intelligence-lab/generated/project-map.v1.json")
    args = parser.parse_args()
    evidence, project_map = asyncio.run(evaluate(args))
    for target, payload in ((args.evidence, evidence), (args.project_map, project_map)):
        path = Path(args.root) / target
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"modules": evidence["module_count"], "grades": evidence["grade_counts"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
