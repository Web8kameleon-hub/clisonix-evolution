#!/usr/bin/env python3
"""
CLISONIX SLO/SLI AUTO-REMEDIATION ENGINE
==========================================

When an SLO breach is detected, this module executes real corrective
actions — no human in the loop.

Pipeline position:
    collect_all()
      → SLOSLIAlerter.process()     [alert]
      → BudgetTracker.record()      [budget + MTTR]
      → AutoRemediator.remediate()  [THIS — act]

Actions (all are real HTTP calls; no subprocess, no fake commands):
    RESTART_SERVICE        POST /admin/restart  on the service management API
    FLUSH_CACHE            POST /admin/cache/flush on ocean-core (or Redis endpoint)
    SWITCH_FALLBACK_MODEL  POST /admin/model/switch on ocean-core
    OPEN_CIRCUIT_BREAKER   POST /admin/circuit-breaker/open on ocean-core
    SCALE_UP               POST /admin/scale on the container management API
    REROUTE_TRAFFIC        POST /admin/routing/fallback on the API gateway
    ROTATE_KEY             POST /admin/api-keys/rotate on the backend API

Every action:
  - Has a per-service cooldown (no re-firing until window expires)
  - Records a RemediationResult (action, outcome, duration, timestamp)
  - Is no-op in REMEDIATION_DRY_RUN=true mode

Environment variables:
    REMEDIATION_DRY_RUN          "true" → log only, never POST (default: false)
    OCEAN_ADMIN_API_TOKEN        Token for ocean-core admin endpoints
    API_ADMIN_TOKEN              Token for backend-api admin endpoints
    OCEAN_HOST                   Ocean Core host (default: 127.0.0.1)
    API_HOST                     Backend API host (default: 127.0.0.1)
    OCEAN_FALLBACK_MODEL         Model to switch to on SEV-1 (default: llama3.2:1b)
    REMEDIATION_HTTP_TIMEOUT     Per-action HTTP timeout seconds (default: 10)
    MGMT_API_PORT                Container management API port (default: 2375)

Author: Clisonix Engineering
"""

from __future__ import annotations

import json
import logging
import os
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from slo_sli_collector import CollectorReport
from slo_sli_gate import SLO_TARGETS, SLOGateResult

logger = logging.getLogger("clisonix.slo_sli_remediation")

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

DRY_RUN: bool = os.getenv("REMEDIATION_DRY_RUN", "false").lower() == "true"
OCEAN_ADMIN_TOKEN: str = os.getenv("OCEAN_ADMIN_API_TOKEN", "")
API_ADMIN_TOKEN: str = os.getenv("API_ADMIN_TOKEN", "")
OCEAN_FALLBACK_MODEL: str = os.getenv("OCEAN_FALLBACK_MODEL", "llama3.2:1b")
HTTP_TIMEOUT: int = int(os.getenv("REMEDIATION_HTTP_TIMEOUT", "10"))

# Service hosts (same env vars used by the collector)
_HOSTS: Dict[str, str] = {
    "ocean_core":  os.getenv("OCEAN_HOST", "127.0.0.1"),
    "backend_api": os.getenv("API_HOST",   "127.0.0.1"),
    "openmind":    os.getenv("OPENMIND_HOST", "127.0.0.1"),
    "excel_core":  os.getenv("EXCEL_HOST",  "127.0.0.1"),
    "ollama":      os.getenv("OLLAMA_HOST", "127.0.0.1"),
    "translation": os.getenv("TRANS_HOST",  "127.0.0.1"),
}

# Service management ports (admin endpoints)
_MGMT_PORTS: Dict[str, int] = {
    "ocean_core":  int(os.getenv("OCEAN_PORT",  "8030")),
    "backend_api": int(os.getenv("API_PORT",    "8000")),
    "openmind":    int(os.getenv("OPENMIND_PORT","9999")),
    "excel_core":  int(os.getenv("EXCEL_PORT",  "8002")),
    "ollama":      int(os.getenv("OLLAMA_PORT", "11434")),
    "translation": int(os.getenv("TRANS_PORT",  "8036")),
}

# Severity ranking — higher = worse
_SEV_RANK: Dict[str, int] = {"SEV-1": 3, "SEV-2": 2, "SEV-3": 1, "OK": 0}


# ═══════════════════════════════════════════════════════════════════════════════
# ACTION TYPES
# ═══════════════════════════════════════════════════════════════════════════════

class ActionType(Enum):
    """
    Remediation actions available to the AutoRemediator.

    Each maps to a real HTTP call on a service admin endpoint.
    """
    RESTART_SERVICE       = "restart_service"
    FLUSH_CACHE           = "flush_cache"
    SWITCH_FALLBACK_MODEL = "switch_fallback_model"
    OPEN_CIRCUIT_BREAKER  = "open_circuit_breaker"
    SCALE_UP              = "scale_up"
    REROUTE_TRAFFIC       = "reroute_traffic"
    ROTATE_KEY            = "rotate_key"


# ═══════════════════════════════════════════════════════════════════════════════
# POLICY + RESULT DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class RemediationPolicy:
    """
    Maps a (service, minimum-severity) pair to an action + cooldown.

    Attributes:
        service:       Gate service key (e.g. "ocean_core").
        min_severity:  Minimum severity that triggers this action ("SEV-1", "SEV-2", "SEV-3").
        action:        ActionType to execute.
        cooldown_sec:  Minimum seconds between two executions of this action for this service.
        params:        Extra key-value pairs forwarded to the action executor.
    """
    service: str
    min_severity: str
    action: ActionType
    cooldown_sec: int
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RemediationResult:
    """
    Record of one remediation action execution.

    Attributes:
        service:       Service key.
        action:        ActionType executed.
        severity:      Breach severity that triggered the action.
        success:       True when the HTTP call returned 2xx.
        dry_run:       True when REMEDIATION_DRY_RUN is set.
        duration_ms:   Round-trip duration of the action HTTP call.
        detail:        Response body / error message.
        executed_at:   ISO-8601 UTC timestamp.
    """
    service: str
    action: ActionType
    severity: str
    success: bool
    dry_run: bool
    duration_ms: float
    detail: str
    executed_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# ═══════════════════════════════════════════════════════════════════════════════
# DEFAULT REMEDIATION POLICIES
# Ordered from most severe to least — AutoRemediator executes the first
# matching policy per (service × run) that is not in cooldown.
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT_POLICIES: List[RemediationPolicy] = [
    # ── ocean_core ────────────────────────────────────────────────────────────
    # SEV-1: full outage → switch to a lighter fallback model immediately,
    #        then try to flush caches to free memory.
    RemediationPolicy(
        service="ocean_core", min_severity="SEV-1",
        action=ActionType.SWITCH_FALLBACK_MODEL, cooldown_sec=600,
        params={"model": OCEAN_FALLBACK_MODEL, "reason": "SEV-1 auto-remediation"},
    ),
    RemediationPolicy(
        service="ocean_core", min_severity="SEV-1",
        action=ActionType.FLUSH_CACHE, cooldown_sec=300,
    ),
    # SEV-2 (high error rate): flush cache to clear stale state
    RemediationPolicy(
        service="ocean_core", min_severity="SEV-2",
        action=ActionType.FLUSH_CACHE, cooldown_sec=180,
    ),
    # SEV-3 (latency): trip the circuit breaker on slow downstream
    RemediationPolicy(
        service="ocean_core", min_severity="SEV-3",
        action=ActionType.OPEN_CIRCUIT_BREAKER, cooldown_sec=300,
        params={"downstream": "translation", "reason": "SEV-3 latency auto-remediation"},
    ),

    # ── backend_api ───────────────────────────────────────────────────────────
    RemediationPolicy(
        service="backend_api", min_severity="SEV-1",
        action=ActionType.RESTART_SERVICE, cooldown_sec=300,
    ),
    RemediationPolicy(
        service="backend_api", min_severity="SEV-2",
        action=ActionType.SCALE_UP, cooldown_sec=600,
        params={"replicas": 2},
    ),
    RemediationPolicy(
        service="backend_api", min_severity="SEV-2",
        action=ActionType.ROTATE_KEY, cooldown_sec=3600,
    ),

    # ── openmind ─────────────────────────────────────────────────────────────
    RemediationPolicy(
        service="openmind", min_severity="SEV-1",
        action=ActionType.RESTART_SERVICE, cooldown_sec=300,
    ),
    RemediationPolicy(
        service="openmind", min_severity="SEV-2",
        action=ActionType.FLUSH_CACHE, cooldown_sec=180,
    ),

    # ── excel_core ────────────────────────────────────────────────────────────
    RemediationPolicy(
        service="excel_core", min_severity="SEV-1",
        action=ActionType.RESTART_SERVICE, cooldown_sec=300,
    ),

    # ── ollama ────────────────────────────────────────────────────────────────
    # Ollama down → switch ocean-core to fallback model immediately
    RemediationPolicy(
        service="ollama", min_severity="SEV-1",
        action=ActionType.SWITCH_FALLBACK_MODEL, cooldown_sec=600,
        params={"model": OCEAN_FALLBACK_MODEL, "reason": "ollama SEV-1 — switching fallback"},
    ),

    # ── translation ───────────────────────────────────────────────────────────
    RemediationPolicy(
        service="translation", min_severity="SEV-1",
        action=ActionType.REROUTE_TRAFFIC, cooldown_sec=300,
        params={"target": "fallback_translation"},
    ),
    RemediationPolicy(
        service="translation", min_severity="SEV-1",
        action=ActionType.OPEN_CIRCUIT_BREAKER, cooldown_sec=300,
        params={"downstream": "translation", "reason": "SEV-1 — circuit open"},
    ),
]


# ═══════════════════════════════════════════════════════════════════════════════
# ACTION EXECUTORS  — one function per ActionType
# ═══════════════════════════════════════════════════════════════════════════════

def _http_post(
    url: str,
    payload: Dict[str, Any],
    token: str = "",
    timeout: int = HTTP_TIMEOUT,
) -> tuple[bool, str]:
    """
    POST a JSON payload to *url*.

    Returns (success: bool, detail: str).
    Never raises — all errors are caught and returned as detail.
    """
    body = json.dumps(payload).encode("utf-8")
    headers: Dict[str, str] = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["X-Admin-Token"] = token
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return (200 <= resp.status < 300), raw
    except urllib.error.HTTPError as exc:
        return False, f"HTTP {exc.code}: {exc.reason}"
    except Exception as exc:
        return False, str(exc)


def _execute_restart_service(service: str, params: Dict[str, Any]) -> tuple[bool, str]:
    """
    POST /admin/restart on the service's management API.

    Falls back to the backend-api brain restart endpoint for backend_api.
    """
    host = _HOSTS[service]
    port = _MGMT_PORTS[service]

    if service == "backend_api":
        url = f"http://{host}:{port}/brain/restart"
        return _http_post(url, {}, token=API_ADMIN_TOKEN)

    url = f"http://{host}:{port}/admin/restart"
    return _http_post(url, {"reason": "auto-remediation"}, token=OCEAN_ADMIN_TOKEN)


def _execute_flush_cache(service: str, params: Dict[str, Any]) -> tuple[bool, str]:
    """POST /admin/cache/flush — ocean-core & openmind."""
    host = _HOSTS[service]
    port = _MGMT_PORTS[service]
    url = f"http://{host}:{port}/admin/cache/flush"
    return _http_post(url, {}, token=OCEAN_ADMIN_TOKEN)


def _execute_switch_fallback_model(service: str, params: Dict[str, Any]) -> tuple[bool, str]:
    """
    POST /admin/model/switch on ocean-core with the configured fallback model.

    Works for both ocean_core and ollama breaches: both target the ocean-core
    admin endpoint since ocean-core is the consumer of the Ollama model.
    """
    host = _HOSTS.get("ocean_core", _HOSTS[service])
    port = _MGMT_PORTS.get("ocean_core", _MGMT_PORTS[service])
    url = f"http://{host}:{port}/admin/model/switch"
    payload = {
        "model": params.get("model", OCEAN_FALLBACK_MODEL),
        "reason": params.get("reason", "auto-remediation"),
    }
    return _http_post(url, payload, token=OCEAN_ADMIN_TOKEN)


def _execute_open_circuit_breaker(service: str, params: Dict[str, Any]) -> tuple[bool, str]:
    """POST /admin/circuit-breaker/open on ocean-core."""
    host = _HOSTS.get("ocean_core", _HOSTS[service])
    port = _MGMT_PORTS.get("ocean_core", _MGMT_PORTS[service])
    url = f"http://{host}:{port}/admin/circuit-breaker/open"
    payload = {
        "downstream": params.get("downstream", service),
        "reason": params.get("reason", "auto-remediation"),
    }
    return _http_post(url, payload, token=OCEAN_ADMIN_TOKEN)


def _execute_scale_up(service: str, params: Dict[str, Any]) -> tuple[bool, str]:
    """
    POST /admin/scale on the container management API.

    If the management port is not accessible, returns a graceful failure
    (the container management API must be exposed separately).
    """
    host = _HOSTS[service]
    mgmt_port = int(os.getenv("MGMT_API_PORT", "2375"))
    url = f"http://{host}:{mgmt_port}/admin/scale"
    payload = {
        "service": service,
        "replicas": params.get("replicas", 2),
        "reason": "auto-remediation",
    }
    return _http_post(url, payload)


def _execute_reroute_traffic(service: str, params: Dict[str, Any]) -> tuple[bool, str]:
    """
    POST /admin/routing/fallback on the backend API gateway.

    Tells the gateway to route away from the failing service.
    """
    host = _HOSTS.get("backend_api", _HOSTS[service])
    port = _MGMT_PORTS.get("backend_api", _MGMT_PORTS[service])
    url = f"http://{host}:{port}/admin/routing/fallback"
    payload = {
        "service": service,
        "target": params.get("target", f"{service}_fallback"),
        "reason": "auto-remediation",
    }
    return _http_post(url, payload, token=API_ADMIN_TOKEN)


def _execute_rotate_key(service: str, params: Dict[str, Any]) -> tuple[bool, str]:
    """
    POST /admin/api-keys/rotate on the backend API.

    Generates a new API key for the service if the current one may be
    compromised (e.g. high error rate caused by auth failures).
    """
    import secrets as _secrets
    host = _HOSTS.get("backend_api", _HOSTS[service])
    port = _MGMT_PORTS.get("backend_api", _MGMT_PORTS[service])
    url = f"http://{host}:{port}/admin/api-keys/rotate"
    payload = {
        "service": service,
        "new_key_hint": _secrets.token_hex(8),  # entropy hint, server decides final key
        "reason": "auto-remediation",
    }
    return _http_post(url, payload, token=API_ADMIN_TOKEN)


# Dispatch table: ActionType → executor function
_EXECUTORS = {
    ActionType.RESTART_SERVICE:       _execute_restart_service,
    ActionType.FLUSH_CACHE:           _execute_flush_cache,
    ActionType.SWITCH_FALLBACK_MODEL: _execute_switch_fallback_model,
    ActionType.OPEN_CIRCUIT_BREAKER:  _execute_open_circuit_breaker,
    ActionType.SCALE_UP:              _execute_scale_up,
    ActionType.REROUTE_TRAFFIC:       _execute_reroute_traffic,
    ActionType.ROTATE_KEY:            _execute_rotate_key,
}


# ═══════════════════════════════════════════════════════════════════════════════
# AUTO-REMEDIATOR
# ═══════════════════════════════════════════════════════════════════════════════

class AutoRemediator:
    """
    Executes corrective actions when SLO breaches are detected.

    For each breaching service, the remediator:
      1. Finds all matching policies (action's min_severity ≤ breach severity).
      2. Skips policies still within cooldown.
      3. Executes the action (real HTTP call, or dry-run log).
      4. Records a RemediationResult.

    Args:
        policies:   List of RemediationPolicy objects.
                    Defaults to DEFAULT_POLICIES.
        dry_run:    Override the REMEDIATION_DRY_RUN env var.
    """

    def __init__(
        self,
        policies: Optional[List[RemediationPolicy]] = None,
        dry_run: bool = DRY_RUN,
    ):
        self._policies = policies if policies is not None else DEFAULT_POLICIES
        self._dry_run = dry_run
        # (service, action) → last_executed_timestamp
        self._last_executed: Dict[tuple, float] = {}

    # ── public API ────────────────────────────────────────────────────────────

    def remediate(self, report: CollectorReport) -> List[RemediationResult]:
        """
        Evaluate *report* and execute remediation actions for any breach.

        Args:
            report: CollectorReport from slo_sli_collector.collect_all().

        Returns:
            List of RemediationResult — one entry per action attempted.
        """
        results: List[RemediationResult] = []
        for gate_result in report.gate_results:
            if gate_result.passed:
                continue
            service_results = self._remediate_service(gate_result)
            results.extend(service_results)
        return results

    # ── internal ─────────────────────────────────────────────────────────────

    def _remediate_service(self, gate: SLOGateResult) -> List[RemediationResult]:
        results: List[RemediationResult] = []
        breach_rank = _SEV_RANK.get(gate.severity, 0)

        for policy in self._policies:
            if policy.service != gate.service_name:
                continue
            if _SEV_RANK.get(policy.min_severity, 0) > breach_rank:
                continue  # breach not severe enough for this policy

            cooldown_key = (gate.service_name, policy.action)
            if self._in_cooldown(cooldown_key, policy.cooldown_sec):
                logger.debug(
                    "Cooldown active for %s.%s — skipping",
                    gate.service_name, policy.action.value,
                )
                continue

            result = self._execute(gate, policy)
            self._last_executed[cooldown_key] = time.monotonic()
            results.append(result)

        return results

    def _in_cooldown(self, key: tuple, cooldown_sec: int) -> bool:
        last = self._last_executed.get(key)
        if last is None:
            return False  # Never executed before — not in cooldown
        return (time.monotonic() - last) < cooldown_sec

    def _execute(
        self,
        gate: SLOGateResult,
        policy: RemediationPolicy,
    ) -> RemediationResult:
        """Run the action executor (or log it in dry-run mode)."""
        action_label = policy.action.value
        t0 = time.monotonic()

        if self._dry_run:
            duration_ms = (time.monotonic() - t0) * 1000
            logger.info(
                "[DRY RUN] Would execute %s on %s (severity: %s, cooldown: %ds)",
                action_label, gate.service_name, gate.severity, policy.cooldown_sec,
            )
            return RemediationResult(
                service=gate.service_name,
                action=policy.action,
                severity=gate.severity,
                success=True,
                dry_run=True,
                duration_ms=round(duration_ms, 2),
                detail=f"dry-run: would call {action_label}",
            )

        executor = _EXECUTORS.get(policy.action)
        if executor is None:
            return RemediationResult(
                service=gate.service_name,
                action=policy.action,
                severity=gate.severity,
                success=False,
                dry_run=False,
                duration_ms=0.0,
                detail=f"no executor registered for {action_label}",
            )

        try:
            success, detail = executor(gate.service_name, policy.params)
        except Exception as exc:
            success, detail = False, str(exc)

        duration_ms = (time.monotonic() - t0) * 1000

        if success:
            logger.info(
                "✅ Remediation OK: %s on %s (%.0f ms)",
                action_label, gate.service_name, duration_ms,
            )
        else:
            logger.warning(
                "⚠️  Remediation FAILED: %s on %s — %s",
                action_label, gate.service_name, detail,
            )

        return RemediationResult(
            service=gate.service_name,
            action=policy.action,
            severity=gate.severity,
            success=success,
            dry_run=False,
            duration_ms=round(duration_ms, 2),
            detail=detail,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    from slo_sli_collector import collect_all, PROBE_COUNT, PROBE_TIMEOUT

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Clisonix SLO/SLI Auto-Remediator"
    )
    parser.add_argument("--dry-run", action="store_true", help="Log actions without executing")
    parser.add_argument("--probe-count", type=int, default=PROBE_COUNT)
    parser.add_argument("--probe-timeout", type=int, default=PROBE_TIMEOUT)
    args = parser.parse_args()

    dry_run = args.dry_run or DRY_RUN
    mode = "DRY RUN" if dry_run else "LIVE"
    logger.info("Auto-Remediator starting — mode: %s", mode)

    report = collect_all(probe_count=args.probe_count, probe_timeout=args.probe_timeout)
    remediator = AutoRemediator(dry_run=dry_run)
    results = remediator.remediate(report)

    if results:
        print(f"\nRemediation actions executed ({len(results)}):")
        print(f"{'Service':<22} {'Action':<26} {'Sev':<8} {'OK':<6} {'ms':>6}")
        print("-" * 72)
        for r in results:
            ok = "✅" if r.success else "❌"
            print(f"{r.service:<22} {r.action.value:<26} {r.severity:<8} {ok:<6} {r.duration_ms:>6.0f}")
    else:
        print("\nNo remediation actions fired (all SLOs passing or in cooldown)")
