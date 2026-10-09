#!/usr/bin/env python3
"""
CLX-AI High Operations Learning Runner (10-min phases)

Purpose:
- Enterprise-grade continuous learning every 10 minutes.
- Multi-phase ingestion from local workspace, git intelligence, and live APIs.
- No fake data: only real successful payloads are learned.

Default behavior:
- Run a 4-hour session (24 cycles x 10 min).
- Persist cycle checkpoints after each phase.
"""

from __future__ import annotations

import argparse
import asyncio
import importlib.metadata
import json
import logging
import os
import subprocess
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from clx import CLXCore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("clx-high-ops")

MANIFEST_GLOBS = [
    "**/requirements*.txt",
    "**/pyproject.toml",
    "**/package.json",
    "**/Cargo.toml",
    "**/*.md",
]

HIGH_VALUE_CODE_GLOBS = [
    "ocean-core/xlc/*.py",
    "ocean-core/*xlc*.py",
    "services/**/api.py",
    "apps/api/**/*.py",
]

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "target",
    "__pycache__",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_write_json(path: Path, payload: Dict[str, Any]) -> None:
    """Write JSON atomically to avoid partial/corrupt files after power loss."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    tmp.replace(path)


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def compute_dynamic_confidence(kind: str, response: str, source: str = "", status_code: Optional[int] = None) -> float:
    """Deterministic confidence scoring from real payload characteristics."""
    base_by_kind = {
        "installed_packages": 0.94,
        "local_material": 0.89,
        "high_value_code": 0.92,
        "git": 0.91,
        "api": 0.90,
    }
    score = base_by_kind.get(kind, 0.9)

    payload = (response or "").strip()
    size = len(payload)
    lowered = payload.lower()

    if size > 12000:
        score += 0.03
    elif size > 3500:
        score += 0.02
    elif size > 800:
        score += 0.01
    elif size < 120:
        score -= 0.02

    if payload.startswith("{") or payload.startswith("["):
        score += 0.01

    if "error" in lowered or "exception" in lowered or "traceback" in lowered:
        score -= 0.04

    if kind == "api":
        if status_code is not None:
            if 200 <= status_code < 300:
                score += 0.02
            elif status_code >= 500:
                score -= 0.05
            elif status_code >= 400:
                score -= 0.03
        if "https://www.clisonix.com" in source:
            score += 0.01

    if kind == "git" and "## " in payload:
        score += 0.01

    return round(_clamp(score, 0.75, 0.99), 4)


def http_json(method: str, url: str, payload: Optional[Dict[str, Any]] = None, timeout: int = 12) -> Tuple[Optional[int], Optional[Dict[str, Any]], Optional[str]]:
    body = None
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
    }
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")

    req = Request(url=url, method=method.upper(), headers=headers, data=body)

    try:
        with urlopen(req, timeout=timeout) as response:
            status = int(getattr(response, "status", 200))
            raw = response.read().decode("utf-8", errors="replace").strip()
            if not raw:
                return status, None, None
            try:
                return status, json.loads(raw), None
            except json.JSONDecodeError:
                return status, None, f"non-json:{raw[:200]}"
    except HTTPError as err:
        raw = err.read().decode("utf-8", errors="replace") if err.fp else ""
        return int(err.code), None, f"http_error:{raw[:200]}"
    except URLError as err:
        return None, None, f"url_error:{err}"
    except Exception as err:  # noqa: BLE001
        return None, None, f"unexpected_error:{err}"


def safe_git(cwd: Path, args: List[str]) -> Tuple[bool, str]:
    try:
        res = subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        if res.returncode != 0:
            return False, (res.stderr or res.stdout or "").strip()[:500]
        return True, (res.stdout or "").strip()
    except Exception as err:  # noqa: BLE001
        return False, f"git_exception:{err}"


def collect_installed_packages(limit: int = 600) -> List[Dict[str, str]]:
    packages: List[Dict[str, str]] = []
    for dist in importlib.metadata.distributions():
        name = dist.metadata["Name"] if "Name" in dist.metadata else "unknown"
        version = dist.version or "unknown"
        packages.append({"name": str(name), "version": str(version)})
    packages.sort(key=lambda x: x["name"].lower())
    return packages[:limit]


def collect_local_material(workspace_root: Path, max_files: int = 500, max_bytes: int = 15000) -> List[Dict[str, str]]:
    items: List[Dict[str, str]] = []
    seen: set[str] = set()

    for pattern in MANIFEST_GLOBS:
        for p in workspace_root.glob(pattern):
            if len(items) >= max_files:
                return items
            if not p.is_file():
                continue
            try:
                rel = p.relative_to(workspace_root)
            except ValueError:
                continue
            if {part.lower() for part in rel.parts} & EXCLUDED_DIRS:
                continue
            key = str(p.resolve())
            if key in seen:
                continue
            seen.add(key)
            try:
                content = p.read_text(encoding="utf-8", errors="replace")[:max_bytes].strip()
            except OSError:
                continue
            if not content:
                continue
            items.append({"path": str(rel).replace("\\", "/"), "content": content})

    return items


def collect_high_value_code(workspace_root: Path, max_files: int = 120, max_bytes: int = 24000) -> List[Dict[str, str]]:
    items: List[Dict[str, str]] = []
    seen: set[str] = set()

    for pattern in HIGH_VALUE_CODE_GLOBS:
        for p in workspace_root.glob(pattern):
            if len(items) >= max_files:
                return items
            if not p.is_file():
                continue
            try:
                rel = p.relative_to(workspace_root)
            except ValueError:
                continue
            key = str(p.resolve())
            if key in seen:
                continue
            seen.add(key)
            try:
                content = p.read_text(encoding="utf-8", errors="replace")[:max_bytes].strip()
            except OSError:
                continue
            if not content:
                continue
            items.append({"path": str(rel).replace("\\", "/"), "content": content})

    return items


def build_ops_probe_catalog() -> List[Tuple[str, str, str, Optional[Dict[str, Any]]]]:
    probes: List[Tuple[str, str, str, Optional[Dict[str, Any]]]] = []

    bases = [
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8030",
        "https://www.clisonix.com",
    ]

    get_paths = [
        "/api/health",
        "/api/ocean/health",
        "/api/ocean/status",
        "/api/curiosity/health",
        "/api/auth/providers",
        "/xlc/health",
    ]

    for base in bases:
        for path in get_paths:
            probes.append(("GET", f"{base}{path}", f"ops_probe:{path}", None))

    post_questions = [
        "DeepThink and provide an operations plan.",
        "What changed in CLX security runtime recently?",
        "Summarize current readiness risks in one paragraph.",
    ]

    post_targets = [
        "http://127.0.0.1:3000/api/ocean/curiosity",
        "https://www.clisonix.com/api/ocean/curiosity",
    ]

    for target in post_targets:
        for q in post_questions:
            probes.append(("POST", target, f"ops_curiosity:{q}", {"question": q}))

    return probes


async def learn_record(clx: CLXCore, query: str, response: str, sources: List[str], confidence: float, source_counter: Counter) -> None:
    learning_engine = clx.learning
    if learning_engine is None:
        raise RuntimeError("CLX learning engine is not available")

    await learning_engine.learn_from_response(
        query=query,
        response=response,
        sources=sources,
        confidence=confidence,
        language="en",
    )
    clx.knowledge.add(
        {
            "query": query,
            "response": response,
            "confidence": confidence,
            "sources": sources,
            "language": "en",
        }
    )
    for s in sources:
        source_counter[s] += 1


async def run_cycle(
    clx: CLXCore,
    workspace_root: Path,
    source_counter: Counter,
    local_max_files: int,
    local_max_bytes: int,
    code_max_files: int,
    code_max_bytes: int,
) -> Dict[str, int]:
    metrics = {
        "local_learned": 0,
        "code_learned": 0,
        "git_learned": 0,
        "api_attempted": 0,
        "api_learned": 0,
        "api_errors": 0,
    }

    # Phase 1: Local ecosystem ingest
    installed = collect_installed_packages(limit=800)
    if installed:
        installed_response = json.dumps({"installed_packages": installed}, ensure_ascii=False)
        await learn_record(
            clx,
            query="ops:local_python_installed_packages",
            response=installed_response,
            sources=["local:importlib.metadata"],
            confidence=compute_dynamic_confidence("installed_packages", installed_response, "local:importlib.metadata"),
            source_counter=source_counter,
        )
        metrics["local_learned"] += 1

    local_docs = collect_local_material(workspace_root, max_files=local_max_files, max_bytes=local_max_bytes)
    for item in local_docs:
        await learn_record(
            clx,
            query=f"ops:local_material:{item['path']}",
            response=item["content"],
            sources=[f"local:{item['path']}"],
            confidence=compute_dynamic_confidence("local_material", item["content"], f"local:{item['path']}"),
            source_counter=source_counter,
        )
        metrics["local_learned"] += 1

    # Phase 1b: High-value code ingest (XLC/core/APIs)
    high_value_code = collect_high_value_code(workspace_root, max_files=code_max_files, max_bytes=code_max_bytes)
    for item in high_value_code:
        await learn_record(
            clx,
            query=f"ops:high_value_code:{item['path']}",
            response=item["content"],
            sources=[f"code:{item['path']}"],
            confidence=compute_dynamic_confidence("high_value_code", item["content"], f"code:{item['path']}"),
            source_counter=source_counter,
        )
        metrics["code_learned"] += 1

    # Phase 2: Git intelligence ingest
    git_queries = [
        ["status", "--short", "--branch"],
        ["log", "--oneline", "--decorate", "-n", "120"],
        ["branch", "-vv"],
        ["remote", "-v"],
    ]
    for args in git_queries:
        ok, out = safe_git(workspace_root, args)
        if ok and out:
            source = f"git:{' '.join(args)}"
            await learn_record(
                clx,
                query=f"ops:git:{' '.join(args)}",
                response=out,
                sources=[source],
                confidence=compute_dynamic_confidence("git", out, source),
                source_counter=source_counter,
            )
            metrics["git_learned"] += 1

    # Phase 3: Live API probing ingest
    for method, url, query, payload in build_ops_probe_catalog():
        metrics["api_attempted"] += 1
        status, data, err = await asyncio.to_thread(http_json, method, url, payload, 12)
        if err or data is None:
            metrics["api_errors"] += 1
            continue
        if status is None or status < 200 or status >= 300:
            metrics["api_errors"] += 1
            continue

        api_response = json.dumps(data, ensure_ascii=False)
        source = f"{method} {url}"
        await learn_record(
            clx,
            query=query,
            response=api_response,
            sources=[source],
            confidence=compute_dynamic_confidence("api", api_response, source, status_code=status),
            source_counter=source_counter,
        )
        metrics["api_learned"] += 1

    return metrics


async def run_high_ops(
    cycle_interval_seconds: int,
    total_duration_seconds: int,
    memory_dir: str,
    workspace_root: Path,
    report_file: str,
    max_cycles: int,
    local_max_files: int,
    local_max_bytes: int,
    code_max_files: int,
    code_max_bytes: int,
    snapshots_dir: str,
) -> None:
    clx = CLXCore(memory_dir=memory_dir, language="en", enable_security=True, enable_learning=True)

    report_path = Path(report_file)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    snapshots_path = Path(snapshots_dir)
    snapshots_path.mkdir(parents=True, exist_ok=True)

    started_at = utc_now()
    t_start = time.time()
    t_end = t_start + total_duration_seconds if total_duration_seconds > 0 else float("inf")

    source_counter: Counter = Counter()
    cycle = 0
    total_metrics = {
        "local_learned": 0,
        "code_learned": 0,
        "git_learned": 0,
        "api_attempted": 0,
        "api_learned": 0,
        "api_errors": 0,
    }

    logger.info("high_ops_start interval=%ss duration=%ss max_cycles=%s", cycle_interval_seconds, total_duration_seconds, max_cycles)

    while time.time() < t_end:
        if max_cycles > 0 and cycle >= max_cycles:
            break

        cycle += 1
        cycle_started_at = utc_now()
        c0 = time.time()

        metrics = await run_cycle(
            clx,
            workspace_root,
            source_counter,
            local_max_files=local_max_files,
            local_max_bytes=local_max_bytes,
            code_max_files=code_max_files,
            code_max_bytes=code_max_bytes,
        )
        for k, v in metrics.items():
            total_metrics[k] += v

        status = clx.get_status()
        checkpoint = {
            "cycle": cycle,
            "cycle_started_at": cycle_started_at,
            "cycle_ended_at": utc_now(),
            "cycle_seconds": round(time.time() - c0, 3),
            "metrics": metrics,
            "knowledge_entries": status.get("knowledge", {}).get("entries", 0),
            "learning_stats": status.get("learning", {}).get("stats", {}),
            "top_sources": source_counter.most_common(25),
        }

        report_payload = {
            "started_at": started_at,
            "last_updated_at": utc_now(),
            "mode": "high-ops-10min-phases",
            "interval_seconds": cycle_interval_seconds,
            "duration_seconds": total_duration_seconds,
            "max_cycles": max_cycles,
            "workspace_root": str(workspace_root),
            "memory_dir": memory_dir,
            "cycles_completed": cycle,
            "totals": total_metrics,
            "checkpoint": checkpoint,
        }
        atomic_write_json(report_path, report_payload)
        atomic_write_json(snapshots_path / f"cycle_{cycle:04d}.json", report_payload)

        logger.info(
            "cycle=%s local=%s code=%s git=%s api=%s/%s errors=%s knowledge=%s",
            cycle,
            metrics["local_learned"],
            metrics["code_learned"],
            metrics["git_learned"],
            metrics["api_learned"],
            metrics["api_attempted"],
            metrics["api_errors"],
            checkpoint["knowledge_entries"],
        )

        sleep_for = max(0, cycle_interval_seconds - int(time.time() - c0))
        if sleep_for > 0 and time.time() < t_end:
            await asyncio.sleep(sleep_for)

    final_status = clx.get_status()
    final_payload = {
        "started_at": started_at,
        "ended_at": utc_now(),
        "mode": "high-ops-10min-phases",
        "interval_seconds": cycle_interval_seconds,
        "duration_seconds": total_duration_seconds,
        "max_cycles": max_cycles,
        "workspace_root": str(workspace_root),
        "memory_dir": memory_dir,
        "cycles_completed": cycle,
        "totals": total_metrics,
        "knowledge_entries": final_status.get("knowledge", {}).get("entries", 0),
        "learning_stats": final_status.get("learning", {}).get("stats", {}),
        "top_sources": source_counter.most_common(40),
    }
    atomic_write_json(report_path, final_payload)
    atomic_write_json(snapshots_path / "final_report.json", final_payload)
    logger.info("high_ops_complete cycles=%s report=%s", cycle, report_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CLX high operations learning runner with 10-minute phased cycles")
    parser.add_argument("--interval-seconds", type=int, default=600, help="Cycle interval in seconds (default: 600 = 10 min)")
    parser.add_argument("--duration-seconds", type=int, default=4 * 3600, help="Total duration in seconds (default: 4h)")
    parser.add_argument("--max-cycles", type=int, default=0, help="Stop after N cycles (0 = unlimited until duration)")
    parser.add_argument("--memory-dir", type=str, default=".clx_ops", help="Memory directory path")
    parser.add_argument("--workspace-root", type=str, default=".", help="Workspace root to crawl")
    parser.add_argument("--report-file", type=str, default=".clx_ops/final_report.json", help="Final/checkpoint report file path")
    parser.add_argument("--snapshots-dir", type=str, default=".clx_ops/snapshots", help="Per-cycle JSON snapshots directory")
    parser.add_argument("--local-max-files", type=int, default=700, help="Max local manifest/docs files per cycle")
    parser.add_argument("--local-max-bytes", type=int, default=18000, help="Max bytes per local file")
    parser.add_argument("--code-max-files", type=int, default=180, help="Max high-value code files per cycle")
    parser.add_argument("--code-max-bytes", type=int, default=28000, help="Max bytes per code file")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    workspace_root = Path(args.workspace_root).resolve()
    asyncio.run(
        run_high_ops(
            cycle_interval_seconds=max(60, int(args.interval_seconds)),
            total_duration_seconds=max(0, int(args.duration_seconds)),
            memory_dir=args.memory_dir,
            workspace_root=workspace_root,
            report_file=args.report_file,
            max_cycles=max(0, int(args.max_cycles)),
            local_max_files=max(20, int(args.local_max_files)),
            local_max_bytes=max(2000, int(args.local_max_bytes)),
            code_max_files=max(10, int(args.code_max_files)),
            code_max_bytes=max(4000, int(args.code_max_bytes)),
            snapshots_dir=args.snapshots_dir,
        )
    )


if __name__ == "__main__":
    main()
