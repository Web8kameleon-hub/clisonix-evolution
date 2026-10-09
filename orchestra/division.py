"""
orchestra.division
===================
OrchestraDivision — async orchestrator that runs all 7 signal probes
concurrently and returns a consolidated DivisionReport.

Usage
-----
    import asyncio
    from orchestra import OrchestraDivision

    division = OrchestraDivision()
    report   = await division.run()
    print(report.to_dict())

Env vars (all optional)
-----------------------
  ORCHESTRA_TIMEOUT_S     per-probe timeout in seconds (default: 15)
  ORCHESTRA_DOMAINS       comma-separated subset to run (default: all)
                          e.g. "repo,hetzner,cache"
"""
from __future__ import annotations

import asyncio
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Dict, List, Optional

from orchestra.models import DivisionReport, ProbeResult, SignalStatus
from orchestra.probes import (
    cache,
    clients,
    cloudflare,
    git_profile,
    gitignore,
    hetzner,
    repo,
)

log = logging.getLogger("orchestra.division")

_TIMEOUT_S = float(os.getenv("ORCHESTRA_TIMEOUT_S", "15"))
_DOMAINS   = [d.strip() for d in os.getenv("ORCHESTRA_DOMAINS", "").split(",") if d.strip()]

# Registry: domain name → probe module with a run() function
_PROBE_REGISTRY: Dict[str, object] = {
    "repo":        repo,
    "hetzner":     hetzner,
    "cloudflare":  cloudflare,
    "git_profile": git_profile,
    "gitignore":   gitignore,
    "cache":       cache,
    "clients":     clients,
}


class OrchestraDivision:
    """
    Concurrent signal orchestrator for all Clisonix domain probes.

    Each probe runs in its own thread (probes are sync I/O) under a
    thread-pool, wrapped with asyncio.wait_for for timeout enforcement.
    """

    def __init__(
        self,
        timeout_s: float = _TIMEOUT_S,
        domains: Optional[List[str]] = None,
    ) -> None:
        self.timeout_s = timeout_s
        self.domains   = domains or _DOMAINS or list(_PROBE_REGISTRY.keys())
        self._executor = ThreadPoolExecutor(
            max_workers=len(self.domains),
            thread_name_prefix="orchestra-probe",
        )

    # ── public API ─────────────────────────────────────────────────────────────

    async def run(self) -> DivisionReport:
        """Run all configured domain probes concurrently."""
        report = DivisionReport()
        loop   = asyncio.get_event_loop()

        tasks: Dict[str, asyncio.Future] = {}
        for domain in self.domains:
            probe_mod = _PROBE_REGISTRY.get(domain)
            if probe_mod is None:
                log.warning("Unknown probe domain '%s' — skipping", domain)
                report.warnings.append(f"Unknown probe domain: {domain}")
                continue
            tasks[domain] = asyncio.ensure_future(
                asyncio.wait_for(
                    loop.run_in_executor(self._executor, probe_mod.run),
                    timeout=self.timeout_s,
                )
            )

        total_start = time.monotonic()
        for domain, task in tasks.items():
            try:
                result: ProbeResult = await task
                report.probes.append(result)
                log.info("[%s] %s — %s (%.0fms)",
                         domain, result.status.value, result.message, result.latency_ms)
            except asyncio.TimeoutError:
                log.error("[%s] timed out after %.1fs", domain, self.timeout_s)
                report.probes.append(ProbeResult(
                    domain  = domain,
                    status  = SignalStatus.ERROR,
                    message = f"probe timed out after {self.timeout_s}s",
                ))
                report.errors.append(f"{domain}: timed out")
            except Exception as exc:
                log.exception("[%s] unhandled exception: %s", domain, exc)
                report.probes.append(ProbeResult(
                    domain  = domain,
                    status  = SignalStatus.ERROR,
                    message = f"unhandled exception: {exc}",
                ))
                report.errors.append(f"{domain}: {exc}")

        elapsed = (time.monotonic() - total_start) * 1000
        log.info("OrchestraDivision completed in %.0fms — overall=%s",
                 elapsed, report.compute_overall().value)
        report.overall = report.compute_overall()
        return report

    async def run_domain(self, domain: str) -> ProbeResult:
        """Run a single domain probe."""
        probe_mod = _PROBE_REGISTRY.get(domain)
        if probe_mod is None:
            return ProbeResult(
                domain  = domain,
                status  = SignalStatus.ERROR,
                message = f"Unknown probe domain: {domain}",
            )
        loop = asyncio.get_event_loop()
        try:
            return await asyncio.wait_for(
                loop.run_in_executor(self._executor, probe_mod.run),
                timeout=self.timeout_s,
            )
        except asyncio.TimeoutError:
            return ProbeResult(
                domain  = domain,
                status  = SignalStatus.ERROR,
                message = f"probe timed out after {self.timeout_s}s",
            )

    def shutdown(self) -> None:
        self._executor.shutdown(wait=False)

    # ── context manager ────────────────────────────────────────────────────────

    async def __aenter__(self) -> "OrchestraDivision":
        return self

    async def __aexit__(self, *_) -> None:
        self.shutdown()
