#!/usr/bin/env python3
"""
CLISONIX SLO/SLI GATE
======================

Evaluates the 6 critical services against their Service Level Objectives.

Services monitored:
  1. Ocean Core     (port 8030)
  2. Backend API    (port 8000)
  3. OpenMind       (port 9999)
  4. Excel Core     (port 8002)
  5. Ollama         (port 11434)
  6. Translation    (port 8036)

SLO targets sourced from: docs/enterprise/SLO_SLI_CRITICAL_SERVICES.md

Author: Clisonix Engineering
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS — monthly error budgets derived from SLO targets
# ═══════════════════════════════════════════════════════════════════════════════

# Minutes in a 30-day month
MINUTES_PER_MONTH: float = 30 * 24 * 60  # 43 200

# Error budget per SLO tier (minutes of allowed downtime per month)
ERROR_BUDGET_MINUTES: Dict[str, float] = {
    "99.95%": MINUTES_PER_MONTH * (1 - 0.9995),  # ≈ 21.6 min
    "99.9%": MINUTES_PER_MONTH * (1 - 0.999),    # ≈ 43.2 min
}

# Fast-burn multiplier threshold for SEV-1 (14× normal burn rate)
FAST_BURN_MULTIPLIER = 14.0

# Slow-burn multiplier threshold for SEV-2
SLOW_BURN_MULTIPLIER = 2.0


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SLOTarget:
    """
    SLO targets for a single service.

    Attributes:
        service_name:              Human-readable service name.
        port:                      TCP port the service listens on.
        availability_slo:          Required availability fraction (0–1), e.g. 0.9995.
        latency_p95_ms:            Maximum allowed p95 latency in milliseconds.
        error_rate_threshold:      Maximum allowed 5xx ratio (0–1), e.g. 0.005 = 0.5%.
        dependency_health_slo:     Minimum required upstream dependency health ratio (0–1).
    """
    service_name: str
    port: int
    availability_slo: float
    latency_p95_ms: float
    error_rate_threshold: float
    dependency_health_slo: float


@dataclass
class SLISnapshot:
    """
    Current SLI measurements for a single service.

    Attributes:
        service_name:       Must match the corresponding SLOTarget.
        availability:       Observed availability fraction (0–1).
        latency_p95_ms:     Observed p95 latency in milliseconds.
        error_rate:         Observed 5xx ratio (0–1).
        dependency_health:  Observed upstream dependency health ratio (0–1).
        window_minutes:     Length of the measurement window in minutes.
    """
    service_name: str
    availability: float
    latency_p95_ms: float
    error_rate: float
    dependency_health: float
    window_minutes: float = 60.0


@dataclass
class SLOGateResult:
    """
    Gate evaluation result for a single service.

    Attributes:
        service_name:               Evaluated service.
        passed:                     True only when ALL SLIs are within SLO.
        availability_ok:            Availability SLI within SLO.
        latency_ok:                 Latency p95 SLI within SLO.
        error_rate_ok:              Error-rate SLI within SLO.
        dependency_health_ok:       Dependency-health SLI within SLO.
        error_budget_remaining_pct: Percentage of monthly error budget still available.
        burn_rate:                  Current burn-rate (1.0 = consuming budget at nominal pace).
        severity:                   "OK", "SEV-3", "SEV-2", or "SEV-1".
        issues:                     Descriptive messages for each SLI violation.
        evaluated_at:               ISO-8601 UTC timestamp of the evaluation.
    """
    service_name: str
    passed: bool
    availability_ok: bool
    latency_ok: bool
    error_rate_ok: bool
    dependency_health_ok: bool
    error_budget_remaining_pct: float
    burn_rate: float
    severity: str
    issues: List[str]
    evaluated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SLO TARGETS — sourced from docs/enterprise/SLO_SLI_CRITICAL_SERVICES.md
# ═══════════════════════════════════════════════════════════════════════════════

SLO_TARGETS: Dict[str, SLOTarget] = {
    "ocean_core": SLOTarget(
        service_name="Ocean Core",
        port=8030,
        availability_slo=0.9995,
        latency_p95_ms=1200.0,
        error_rate_threshold=0.005,
        dependency_health_slo=0.99,
    ),
    "backend_api": SLOTarget(
        service_name="Backend API",
        port=8000,
        availability_slo=0.9995,
        latency_p95_ms=300.0,
        error_rate_threshold=0.005,
        dependency_health_slo=0.99,
    ),
    "openmind": SLOTarget(
        service_name="OpenMind",
        port=9999,
        availability_slo=0.9995,
        latency_p95_ms=200.0,
        error_rate_threshold=0.005,
        dependency_health_slo=0.99,
    ),
    "excel_core": SLOTarget(
        service_name="Excel Core",
        port=8002,
        availability_slo=0.9995,
        latency_p95_ms=300.0,
        error_rate_threshold=0.005,
        dependency_health_slo=0.99,
    ),
    "ollama": SLOTarget(
        service_name="Ollama",
        port=11434,
        availability_slo=0.999,
        latency_p95_ms=300.0,
        error_rate_threshold=0.005,
        dependency_health_slo=0.99,
    ),
    "translation": SLOTarget(
        service_name="Translation Node",
        port=8036,
        availability_slo=0.999,
        latency_p95_ms=300.0,
        error_rate_threshold=0.005,
        dependency_health_slo=0.99,
    ),
}


# ═══════════════════════════════════════════════════════════════════════════════
# GATE
# ═══════════════════════════════════════════════════════════════════════════════

class SLOSLIGate:
    """
    Evaluates live SLI snapshots against the defined SLO targets and
    computes error budgets and burn rates for each critical service.
    """

    def evaluate(self, snapshot: SLISnapshot, target: Optional[SLOTarget] = None) -> SLOGateResult:
        """
        Evaluate one SLI snapshot against its SLO target.

        Args:
            snapshot: Live measurements for a single service.
            target:   SLO target to evaluate against.  If omitted the target
                      is looked up from SLO_TARGETS by service key derived
                      from the snapshot's service_name.

        Returns:
            SLOGateResult with pass/fail status, burn rate and severity.

        Raises:
            ValueError: When no SLO target can be found for the service.
        """
        if target is None:
            key = snapshot.service_name.lower().replace(" ", "_")
            target = SLO_TARGETS.get(key)
            if target is None:
                raise ValueError(
                    f"No SLO target registered for service '{snapshot.service_name}'. "
                    f"Known keys: {list(SLO_TARGETS.keys())}"
                )

        issues: List[str] = []

        # ── 1. Availability SLI ───────────────────────────────────────────────
        availability_ok = snapshot.availability >= target.availability_slo
        if not availability_ok:
            issues.append(
                f"Availability {snapshot.availability:.4%} below SLO "
                f"{target.availability_slo:.4%}"
            )

        # ── 2. Latency p95 SLI ───────────────────────────────────────────────
        latency_ok = snapshot.latency_p95_ms <= target.latency_p95_ms
        if not latency_ok:
            issues.append(
                f"Latency p95 {snapshot.latency_p95_ms:.1f}ms exceeds SLO "
                f"{target.latency_p95_ms:.0f}ms"
            )

        # ── 3. Error-rate SLI ────────────────────────────────────────────────
        error_rate_ok = snapshot.error_rate <= target.error_rate_threshold
        if not error_rate_ok:
            issues.append(
                f"Error rate {snapshot.error_rate:.3%} exceeds SLO "
                f"{target.error_rate_threshold:.3%}"
            )

        # ── 4. Dependency-health SLI ──────────────────────────────────────────
        dependency_health_ok = snapshot.dependency_health >= target.dependency_health_slo
        if not dependency_health_ok:
            issues.append(
                f"Dependency health {snapshot.dependency_health:.4%} below SLO "
                f"{target.dependency_health_slo:.4%}"
            )

        # ── 5. Error budget & burn rate ───────────────────────────────────────
        tier_key = "99.95%" if target.availability_slo >= 0.9995 else "99.9%"
        monthly_budget_minutes = ERROR_BUDGET_MINUTES[tier_key]

        # Downtime minutes observed in the measurement window
        observed_downtime_minutes = (1.0 - snapshot.availability) * snapshot.window_minutes

        # Nominal downtime pace to exactly exhaust the budget over a 30-day month
        nominal_rate = monthly_budget_minutes / MINUTES_PER_MONTH  # fraction of budget per minute

        # Burn rate: how fast we are consuming the budget vs. nominal pace
        if nominal_rate > 0:
            burn_rate = (observed_downtime_minutes / snapshot.window_minutes) / nominal_rate
        else:
            burn_rate = 0.0

        # Remaining error budget (percentage of monthly budget)
        budget_consumed_pct = min(
            100.0,
            (observed_downtime_minutes / monthly_budget_minutes) * 100.0
            * (MINUTES_PER_MONTH / snapshot.window_minutes),
        )
        error_budget_remaining_pct = max(0.0, 100.0 - budget_consumed_pct)

        # ── 6. Severity classification (from alerting thresholds) ─────────────
        severity = self._classify_severity(
            availability_ok=availability_ok,
            latency_ok=latency_ok,
            error_rate_ok=error_rate_ok,
            burn_rate=burn_rate,
            error_rate=snapshot.error_rate,
            latency_p95_ms=snapshot.latency_p95_ms,
            latency_target=target.latency_p95_ms,
            window_minutes=snapshot.window_minutes,
        )

        passed = availability_ok and latency_ok and error_rate_ok and dependency_health_ok

        return SLOGateResult(
            service_name=snapshot.service_name,
            passed=passed,
            availability_ok=availability_ok,
            latency_ok=latency_ok,
            error_rate_ok=error_rate_ok,
            dependency_health_ok=dependency_health_ok,
            error_budget_remaining_pct=round(error_budget_remaining_pct, 2),
            burn_rate=round(burn_rate, 2),
            severity=severity,
            issues=issues,
        )

    # ── helpers ───────────────────────────────────────────────────────────────

    def _classify_severity(
        self,
        availability_ok: bool,
        latency_ok: bool,
        error_rate_ok: bool,
        burn_rate: float,
        error_rate: float,
        latency_p95_ms: float,
        latency_target: float,
        window_minutes: float,
    ) -> str:
        """
        Map SLI violations to severity levels as defined in
        docs/enterprise/SLO_SLI_CRITICAL_SERVICES.md:

            SEV-1: fast burn-rate ≥ 14×
            SEV-2: error rate > 2% for ≥ 5 min window
            SEV-3: latency p95 > 2× target for ≥ 10 min window
        """
        # SEV-1: fast burn
        if burn_rate >= FAST_BURN_MULTIPLIER:
            return "SEV-1"

        # SEV-2: error rate > 2% with sufficient window
        if not error_rate_ok and error_rate > 0.02 and window_minutes >= 5:
            return "SEV-2"

        # SEV-3: latency p95 > 2× target with sufficient window
        if not latency_ok and latency_p95_ms > 2 * latency_target and window_minutes >= 10:
            return "SEV-3"

        if not availability_ok or not latency_ok or not error_rate_ok:
            return "SEV-3"

        return "OK"


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def evaluate_service(snapshot: SLISnapshot) -> SLOGateResult:
    """Evaluate a single service snapshot against its registered SLO target."""
    gate = SLOSLIGate()
    return gate.evaluate(snapshot)


def evaluate_services(snapshots: List[SLISnapshot]) -> List[SLOGateResult]:
    """Evaluate multiple service snapshots and return one result per service."""
    gate = SLOSLIGate()
    results: List[SLOGateResult] = []
    for snapshot in snapshots:
        try:
            results.append(gate.evaluate(snapshot))
        except ValueError as exc:
            results.append(
                SLOGateResult(
                    service_name=snapshot.service_name,
                    passed=False,
                    availability_ok=False,
                    latency_ok=False,
                    error_rate_ok=False,
                    dependency_health_ok=False,
                    error_budget_remaining_pct=0.0,
                    burn_rate=0.0,
                    severity="SEV-1",
                    issues=[f"SLO target not found: {exc}"],
                )
            )
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# CLI ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("SLO/SLI Gate — Clisonix Critical Services")
    print("=" * 55)

    # Example snapshots (replace with live metric collection in production)
    demo_snapshots = [
        SLISnapshot(
            service_name="ocean_core",
            availability=0.9998,
            latency_p95_ms=950.0,
            error_rate=0.002,
            dependency_health=0.995,
            window_minutes=60.0,
        ),
        SLISnapshot(
            service_name="backend_api",
            availability=0.9997,
            latency_p95_ms=220.0,
            error_rate=0.001,
            dependency_health=0.998,
            window_minutes=60.0,
        ),
        SLISnapshot(
            service_name="openmind",
            availability=0.9994,       # breaches 99.95% SLO
            latency_p95_ms=185.0,
            error_rate=0.003,
            dependency_health=0.995,
            window_minutes=60.0,
        ),
        SLISnapshot(
            service_name="excel_core",
            availability=0.9996,
            latency_p95_ms=270.0,
            error_rate=0.0015,
            dependency_health=0.997,
            window_minutes=60.0,
        ),
        SLISnapshot(
            service_name="ollama",
            availability=0.9992,
            latency_p95_ms=290.0,
            error_rate=0.004,
            dependency_health=0.993,
            window_minutes=60.0,
        ),
        SLISnapshot(
            service_name="translation",
            availability=0.9988,       # breaches 99.9% SLO
            latency_p95_ms=310.0,      # breaches 300ms target
            error_rate=0.025,          # SEV-2: > 2%
            dependency_health=0.985,
            window_minutes=60.0,
        ),
    ]

    results = evaluate_services(demo_snapshots)

    for result in results:
        service_key = result.service_name.lower().replace(" ", "_")
        target = SLO_TARGETS.get(service_key)
        display_name = target.service_name if target else result.service_name
        status = "✅ PASS" if result.passed else "❌ FAIL"
        print(
            f"\n{display_name:<20} {status}  "
            f"[{result.severity}]  "
            f"burn={result.burn_rate:.1f}×  "
            f"budget_left={result.error_budget_remaining_pct:.1f}%"
        )
        for issue in result.issues:
            print(f"  ⚠ {issue}")

    all_passed = all(r.passed for r in results)
    print("\n" + "=" * 55)
    print(f"Gate result: {'✅ ALL SERVICES PASSING' if all_passed else '❌ ONE OR MORE SERVICES FAILING'}")
