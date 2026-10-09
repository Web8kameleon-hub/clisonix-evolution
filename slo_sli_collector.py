#!/usr/bin/env python3
"""
CLISONIX SLO/SLI LIVE METRICS COLLECTOR
=========================================

Probes the 6 critical service /health endpoints, measures real latency,
and builds SLISnapshot objects that feed directly into SLOSLIGate.

Usage (CLI):
    python slo_sli_collector.py

Usage (programmatic):
    from slo_sli_collector import collect_all, collect_snapshot, SERVICE_CONFIG

    # Full report for all services
    report = collect_all()
    for result in report.gate_results:
        print(result.service_name, result.passed, result.severity)

    # Single service snapshot
    cfg   = SERVICE_CONFIG["backend_api"]
    snap  = collect_snapshot(cfg)

Environment variable overrides (useful in Docker / CI):
    OCEAN_HOST      default: 127.0.0.1
    API_HOST        default: 127.0.0.1
    OPENMIND_HOST   default: 127.0.0.1
    EXCEL_HOST      default: 127.0.0.1
    OLLAMA_HOST     default: 127.0.0.1
    TRANS_HOST      default: 127.0.0.1
    PROBE_COUNT     default: 10  (HTTP requests per service)
    PROBE_TIMEOUT   default: 3   (seconds per request)

Author: Clisonix Engineering
"""

from __future__ import annotations

import os
import time
import json
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from slo_sli_gate import (
    SLISnapshot,
    SLOGateResult,
    SLO_TARGETS,
    evaluate_services,
)


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT_PROBE_COUNT: int = 10
DEFAULT_PROBE_TIMEOUT: int = 3  # seconds

#: Number of HTTP probes per service (env override: PROBE_COUNT)
PROBE_COUNT: int = int(os.getenv("PROBE_COUNT", str(DEFAULT_PROBE_COUNT)))

#: Seconds before a probe times out (env override: PROBE_TIMEOUT)
PROBE_TIMEOUT: int = int(os.getenv("PROBE_TIMEOUT", str(DEFAULT_PROBE_TIMEOUT)))


@dataclass(frozen=True)
class ServiceConfig:
    """
    Network configuration for a single probed service.

    Attributes:
        key:   Snake-case key matching the SLO_TARGETS registry.
        host:  Hostname or IP to probe.
        port:  TCP port.
        path:  HTTP path for the health check (default: /health).
    """
    key: str
    host: str
    port: int
    path: str = "/health"

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}{self.path}"


def _build_service_config() -> Dict[str, ServiceConfig]:
    """Build service config, allowing per-service host overrides from env."""
    return {
        "ocean_core": ServiceConfig(
            key="ocean_core",
            host=os.getenv("OCEAN_HOST", "127.0.0.1"),
            port=SLO_TARGETS["ocean_core"].port,
        ),
        "backend_api": ServiceConfig(
            key="backend_api",
            host=os.getenv("API_HOST", "127.0.0.1"),
            port=SLO_TARGETS["backend_api"].port,
        ),
        "openmind": ServiceConfig(
            key="openmind",
            host=os.getenv("OPENMIND_HOST", "127.0.0.1"),
            port=SLO_TARGETS["openmind"].port,
        ),
        "excel_core": ServiceConfig(
            key="excel_core",
            host=os.getenv("EXCEL_HOST", "127.0.0.1"),
            port=SLO_TARGETS["excel_core"].port,
        ),
        "ollama": ServiceConfig(
            key="ollama",
            host=os.getenv("OLLAMA_HOST", "127.0.0.1"),
            port=SLO_TARGETS["ollama"].port,
        ),
        "translation": ServiceConfig(
            key="translation",
            host=os.getenv("TRANS_HOST", "127.0.0.1"),
            port=SLO_TARGETS["translation"].port,
        ),
    }


#: Service configuration dictionary (rebuilt on each import to respect env vars)
SERVICE_CONFIG: Dict[str, ServiceConfig] = _build_service_config()


# ═══════════════════════════════════════════════════════════════════════════════
# PROBE RESULT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ProbeResult:
    """
    Result of a single HTTP probe to a service's health endpoint.

    Attributes:
        success:          True when the request completed and returned a 2xx status.
        latency_ms:       Round-trip time in milliseconds (even for failures).
        status_code:      HTTP status code, or 0 on connection error.
        is_5xx:           True when status_code is in the 5xx range.
        dependency_health: Dependency health fraction parsed from the JSON body
                           (1.0 if not present / not parseable).
    """
    success: bool
    latency_ms: float
    status_code: int
    is_5xx: bool
    dependency_health: float


def _probe_once(url: str, timeout: int) -> ProbeResult:
    """Send a single HTTP GET to *url* and return a ProbeResult."""
    t0 = time.monotonic()
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            latency_ms = (time.monotonic() - t0) * 1000
            status_code = resp.status
            body_raw = resp.read()

        is_5xx = 500 <= status_code < 600
        success = 200 <= status_code < 300

        # Try to parse dependency health from the JSON body
        dep_health = _parse_dependency_health(body_raw)

        return ProbeResult(
            success=success,
            latency_ms=latency_ms,
            status_code=status_code,
            is_5xx=is_5xx,
            dependency_health=dep_health,
        )

    except urllib.error.HTTPError as exc:
        latency_ms = (time.monotonic() - t0) * 1000
        return ProbeResult(
            success=False,
            latency_ms=latency_ms,
            status_code=exc.code,
            is_5xx=(500 <= exc.code < 600),
            dependency_health=0.0,
        )

    except Exception:
        latency_ms = (time.monotonic() - t0) * 1000
        return ProbeResult(
            success=False,
            latency_ms=latency_ms,
            status_code=0,
            is_5xx=False,
            dependency_health=0.0,
        )


def _parse_dependency_health(body: bytes) -> float:
    """
    Extract a dependency health fraction (0–1) from a service health response.

    Expected JSON shapes (first match wins):
      {"dependency_health": 0.995}
      {"dependencies": {"healthy": 98, "total": 100}}
      {"upstream_health": 0.99}

    Falls back to 1.0 when none of these keys are present.
    """
    try:
        data = json.loads(body.decode("utf-8", errors="replace"))
    except (ValueError, AttributeError):
        return 1.0

    if "dependency_health" in data:
        val = float(data["dependency_health"])
        return max(0.0, min(1.0, val))

    if "upstream_health" in data:
        val = float(data["upstream_health"])
        return max(0.0, min(1.0, val))

    if "dependencies" in data and isinstance(data["dependencies"], dict):
        deps = data["dependencies"]
        total = deps.get("total", 0)
        healthy = deps.get("healthy", 0)
        if total > 0:
            return healthy / total

    return 1.0


def _latency_p95(latencies: List[float]) -> float:
    """Return the 95th-percentile latency from a list of samples (ms)."""
    if not latencies:
        return 0.0
    sorted_lat = sorted(latencies)
    idx = max(0, int(len(sorted_lat) * 0.95) - 1)
    return sorted_lat[idx]


# ═══════════════════════════════════════════════════════════════════════════════
# SNAPSHOT COLLECTION
# ═══════════════════════════════════════════════════════════════════════════════

def collect_snapshot(
    config: ServiceConfig,
    probe_count: int = PROBE_COUNT,
    probe_timeout: int = PROBE_TIMEOUT,
) -> SLISnapshot:
    """
    Probe a single service *probe_count* times and return an SLISnapshot.

    The window_minutes field is computed from the actual elapsed wall-clock time.
    When a service is completely unreachable every probe returns success=False,
    giving availability=0 and an appropriate burn-rate in the gate.

    Args:
        config:        Network configuration for the service.
        probe_count:   Number of HTTP probes to send.
        probe_timeout: Per-probe timeout in seconds.

    Returns:
        SLISnapshot ready for SLOSLIGate.evaluate().
    """
    probes: List[ProbeResult] = []
    t_start = time.monotonic()

    for _ in range(probe_count):
        probes.append(_probe_once(config.url, probe_timeout))

    window_minutes = max((time.monotonic() - t_start) / 60.0, 0.001)

    total = len(probes)
    successful = [p for p in probes if p.success]
    failed_5xx = [p for p in probes if p.is_5xx]

    availability = len(successful) / total
    error_rate = len(failed_5xx) / total
    latency_p95_ms = _latency_p95([p.latency_ms for p in probes])

    # Dependency health: average of all probes that returned parseable data.
    # Failed probes (connection refused, timeout) are always excluded from this
    # average because only 2xx probes carry a meaningful dependency health value.
    dep_samples = [p.dependency_health for p in probes if p.success]
    if dep_samples:
        dependency_health = sum(dep_samples) / len(dep_samples)
    else:
        dependency_health = 0.0

    return SLISnapshot(
        service_name=config.key,
        availability=availability,
        latency_p95_ms=latency_p95_ms,
        error_rate=error_rate,
        dependency_health=dependency_health,
        window_minutes=window_minutes,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# FULL REPORT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CollectorReport:
    """
    Aggregated report from probing all 6 critical services.

    Attributes:
        snapshots:    Raw SLI measurements, one per service.
        gate_results: SLOGateResult for each service.
        collected_at: ISO-8601 UTC timestamp.
        all_passed:   True only when every service passes its SLO gate.
    """
    snapshots: List[SLISnapshot]
    gate_results: List[SLOGateResult]
    collected_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @property
    def all_passed(self) -> bool:
        return all(r.passed for r in self.gate_results)

    @property
    def failing_services(self) -> List[SLOGateResult]:
        return [r for r in self.gate_results if not r.passed]

    @property
    def highest_severity(self) -> str:
        """Return the worst severity across all results (SEV-1 > SEV-2 > SEV-3 > OK)."""
        order = {"SEV-1": 0, "SEV-2": 1, "SEV-3": 2, "OK": 3}
        return min(self.gate_results, key=lambda r: order.get(r.severity, 3)).severity


def collect_all(
    service_config: Optional[Dict[str, ServiceConfig]] = None,
    probe_count: int = PROBE_COUNT,
    probe_timeout: int = PROBE_TIMEOUT,
    max_workers: int = 6,
) -> CollectorReport:
    """
    Probe all 6 critical services concurrently and return a CollectorReport.

    Args:
        service_config: Service configuration map (defaults to SERVICE_CONFIG).
        probe_count:    Number of HTTP probes per service.
        probe_timeout:  Per-probe timeout in seconds.
        max_workers:    Thread pool size for concurrent probing.

    Returns:
        CollectorReport containing per-service snapshots and gate results.
    """
    cfg_map = service_config or SERVICE_CONFIG
    snapshots: List[SLISnapshot] = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_key = {
            executor.submit(collect_snapshot, cfg, probe_count, probe_timeout): key
            for key, cfg in cfg_map.items()
        }
        for future in as_completed(future_to_key):
            snapshots.append(future.result())

    # Sort deterministically by key order from SLO_TARGETS
    key_order = list(SLO_TARGETS.keys())
    snapshots.sort(key=lambda s: key_order.index(s.service_name) if s.service_name in key_order else 99)

    gate_results = evaluate_services(snapshots)
    gate_results.sort(key=lambda r: key_order.index(r.service_name) if r.service_name in key_order else 99)

    return CollectorReport(snapshots=snapshots, gate_results=gate_results)


# ═══════════════════════════════════════════════════════════════════════════════
# CLI ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def _format_table(report: CollectorReport) -> str:
    """Render a human-readable table from a CollectorReport."""
    lines = [
        "╔═══════════════════════════════════════════════════════════════════════════════════╗",
        "║              CLISONIX — SLO/SLI LIVE GATE REPORT                               ║",
        f"║  Collected at: {report.collected_at:<65}║",
        "╠══════════════════╦════════╦══════════╦══════════╦═════════╦══════════╦════════╣",
        "║ Service          ║ Status ║ Avail    ║ Lat p95  ║ Err rt  ║ BurnRate ║ Sev    ║",
        "╠══════════════════╬════════╬══════════╬══════════╬═════════╬══════════╬════════╣",
    ]

    for snap, result in zip(report.snapshots, report.gate_results):
        target = SLO_TARGETS.get(snap.service_name)
        display = target.service_name if target else snap.service_name
        status = "✅ PASS" if result.passed else "❌ FAIL"
        avail = f"{snap.availability:.4%}"
        lat = f"{snap.latency_p95_ms:.0f}ms"
        err = f"{snap.error_rate:.2%}"
        burn = f"{result.burn_rate:.1f}×"
        sev = result.severity

        lines.append(
            f"║ {display:<16} ║ {status:<6} ║ {avail:<8} ║ {lat:<8} ║ {err:<7} ║ {burn:<8} ║ {sev:<6} ║"
        )

    lines.append(
        "╚══════════════════╩════════╩══════════╩══════════╩═════════╩══════════╩════════╝"
    )

    overall = "✅  ALL SERVICES PASSING" if report.all_passed else f"❌  GATE OPEN — {len(report.failing_services)} service(s) failing  [{report.highest_severity}]"
    lines.append(f"\nOverall: {overall}")

    if report.failing_services:
        lines.append("\nViolations:")
        for res in report.failing_services:
            for issue in res.issues:
                lines.append(f"  • {res.service_name}: {issue}")

    return "\n".join(lines)


if __name__ == "__main__":
    import sys

    print("Probing all 6 critical services …")
    print(f"  probe_count={PROBE_COUNT}  timeout={PROBE_TIMEOUT}s\n")

    report = collect_all()
    print(_format_table(report))

    sys.exit(0 if report.all_passed else 1)
