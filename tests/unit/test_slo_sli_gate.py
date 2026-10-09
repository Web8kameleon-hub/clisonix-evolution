#!/usr/bin/env python3
"""
Unit tests for slo_sli_gate.py
"""

import pytest
import sys
import os

# Allow importing from the repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from slo_sli_gate import (
    SLISnapshot,
    SLOGateResult,
    SLOSLIGate,
    SLO_TARGETS,
    evaluate_service,
    evaluate_services,
    ERROR_BUDGET_MINUTES,
    FAST_BURN_MULTIPLIER,
)


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _healthy_snapshot(service_name: str, window_minutes: float = 60.0) -> SLISnapshot:
    """Return a snapshot that should pass all SLIs for the given service."""
    target = SLO_TARGETS[service_name]
    return SLISnapshot(
        service_name=service_name,
        availability=target.availability_slo + 0.0001,
        latency_p95_ms=target.latency_p95_ms * 0.5,
        error_rate=target.error_rate_threshold * 0.5,
        dependency_health=target.dependency_health_slo + 0.001,
        window_minutes=window_minutes,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SLO_TARGETS sanity checks
# ═══════════════════════════════════════════════════════════════════════════════

class TestSLOTargets:
    def test_all_six_services_registered(self):
        expected = {
            "ocean_core", "backend_api", "openmind",
            "excel_core", "ollama", "translation",
        }
        assert set(SLO_TARGETS.keys()) == expected

    def test_high_tier_availability(self):
        high_tier = ["ocean_core", "backend_api", "openmind", "excel_core"]
        for key in high_tier:
            assert SLO_TARGETS[key].availability_slo == 0.9995, key

    def test_standard_tier_availability(self):
        for key in ["ollama", "translation"]:
            assert SLO_TARGETS[key].availability_slo == 0.999, key

    def test_error_rate_threshold_half_percent(self):
        for key, target in SLO_TARGETS.items():
            assert target.error_rate_threshold == 0.005, key

    def test_ocean_latency_target(self):
        assert SLO_TARGETS["ocean_core"].latency_p95_ms == 1200.0

    def test_openmind_latency_target(self):
        assert SLO_TARGETS["openmind"].latency_p95_ms == 200.0

    def test_error_budget_minutes_sanity(self):
        # 99.95% → ≈ 21.6 min
        assert 20 < ERROR_BUDGET_MINUTES["99.95%"] < 23
        # 99.9% → ≈ 43.2 min
        assert 42 < ERROR_BUDGET_MINUTES["99.9%"] < 45


# ═══════════════════════════════════════════════════════════════════════════════
# Healthy services pass
# ═══════════════════════════════════════════════════════════════════════════════

class TestHealthyServicesPass:
    @pytest.mark.parametrize("service_key", list(SLO_TARGETS.keys()))
    def test_healthy_snapshot_passes(self, service_key):
        snapshot = _healthy_snapshot(service_key)
        result = evaluate_service(snapshot)
        assert result.passed is True, f"{service_key}: {result.issues}"
        assert result.severity == "OK"
        assert result.issues == []

    def test_result_has_positive_budget(self):
        snapshot = _healthy_snapshot("backend_api")
        result = evaluate_service(snapshot)
        assert result.error_budget_remaining_pct > 0

    def test_healthy_burn_rate_below_one(self):
        snapshot = _healthy_snapshot("ocean_core")
        result = evaluate_service(snapshot)
        assert result.burn_rate < 1.0


# ═══════════════════════════════════════════════════════════════════════════════
# Availability SLI violation
# ═══════════════════════════════════════════════════════════════════════════════

class TestAvailabilityViolation:
    def test_availability_below_slo_fails(self):
        target = SLO_TARGETS["openmind"]
        snapshot = SLISnapshot(
            service_name="openmind",
            availability=target.availability_slo - 0.0002,  # just below
            latency_p95_ms=target.latency_p95_ms * 0.5,
            error_rate=0.001,
            dependency_health=0.999,
            window_minutes=60.0,
        )
        result = evaluate_service(snapshot)
        assert result.passed is False
        assert result.availability_ok is False
        assert result.latency_ok is True
        assert result.error_rate_ok is True
        assert any("Availability" in issue for issue in result.issues)

    def test_fast_burn_triggers_sev1(self):
        target = SLO_TARGETS["backend_api"]
        # Simulate 100% downtime (availability=0) for 60-min window
        snapshot = SLISnapshot(
            service_name="backend_api",
            availability=0.0,
            latency_p95_ms=50.0,
            error_rate=0.001,
            dependency_health=0.999,
            window_minutes=60.0,
        )
        result = evaluate_service(snapshot)
        assert result.severity == "SEV-1"
        assert result.burn_rate >= FAST_BURN_MULTIPLIER


# ═══════════════════════════════════════════════════════════════════════════════
# Latency SLI violation
# ═══════════════════════════════════════════════════════════════════════════════

class TestLatencyViolation:
    def test_latency_exceeds_target_fails(self):
        target = SLO_TARGETS["backend_api"]
        snapshot = SLISnapshot(
            service_name="backend_api",
            availability=1.0,
            latency_p95_ms=target.latency_p95_ms + 50,  # 50ms over
            error_rate=0.001,
            dependency_health=0.999,
            window_minutes=60.0,
        )
        result = evaluate_service(snapshot)
        assert result.passed is False
        assert result.latency_ok is False
        assert any("Latency" in issue for issue in result.issues)

    def test_latency_2x_target_with_10min_window_is_sev3(self):
        target = SLO_TARGETS["openmind"]
        snapshot = SLISnapshot(
            service_name="openmind",
            availability=1.0,
            latency_p95_ms=target.latency_p95_ms * 2.5,  # > 2× target
            error_rate=0.001,
            dependency_health=0.999,
            window_minutes=15.0,  # ≥ 10 min
        )
        result = evaluate_service(snapshot)
        assert result.severity == "SEV-3"

    def test_latency_2x_target_short_window_still_sev3(self):
        """5-min window (< 10 min) still classified SEV-3 (generic SLI failure)."""
        target = SLO_TARGETS["openmind"]
        snapshot = SLISnapshot(
            service_name="openmind",
            availability=1.0,
            latency_p95_ms=target.latency_p95_ms * 2.5,
            error_rate=0.001,
            dependency_health=0.999,
            window_minutes=5.0,  # < 10 min
        )
        result = evaluate_service(snapshot)
        assert result.severity == "SEV-3"


# ═══════════════════════════════════════════════════════════════════════════════
# Error-rate SLI violation
# ═══════════════════════════════════════════════════════════════════════════════

class TestErrorRateViolation:
    def test_error_rate_above_threshold_fails(self):
        target = SLO_TARGETS["ocean_core"]
        snapshot = SLISnapshot(
            service_name="ocean_core",
            availability=1.0,
            latency_p95_ms=500.0,
            error_rate=target.error_rate_threshold + 0.002,  # just over
            dependency_health=0.999,
            window_minutes=60.0,
        )
        result = evaluate_service(snapshot)
        assert result.passed is False
        assert result.error_rate_ok is False
        assert any("Error rate" in issue for issue in result.issues)

    def test_error_rate_over_2pct_5min_window_is_sev2(self):
        snapshot = SLISnapshot(
            service_name="translation",
            availability=1.0,
            latency_p95_ms=100.0,
            error_rate=0.03,   # 3% → > 2% threshold
            dependency_health=0.999,
            window_minutes=10.0,  # ≥ 5 min
        )
        result = evaluate_service(snapshot)
        assert result.severity == "SEV-2"

    def test_error_rate_over_2pct_short_window_is_sev3(self):
        snapshot = SLISnapshot(
            service_name="translation",
            availability=1.0,
            latency_p95_ms=100.0,
            error_rate=0.03,
            dependency_health=0.999,
            window_minutes=3.0,  # < 5 min
        )
        result = evaluate_service(snapshot)
        # Not enough window for SEV-2 promotion; falls back to SEV-3
        assert result.severity == "SEV-3"


# ═══════════════════════════════════════════════════════════════════════════════
# Dependency-health SLI violation
# ═══════════════════════════════════════════════════════════════════════════════

class TestDependencyHealthViolation:
    def test_dependency_health_below_slo_fails(self):
        target = SLO_TARGETS["excel_core"]
        snapshot = SLISnapshot(
            service_name="excel_core",
            availability=1.0,
            latency_p95_ms=100.0,
            error_rate=0.001,
            dependency_health=target.dependency_health_slo - 0.005,
            window_minutes=60.0,
        )
        result = evaluate_service(snapshot)
        assert result.passed is False
        assert result.dependency_health_ok is False
        assert any("Dependency" in issue for issue in result.issues)


# ═══════════════════════════════════════════════════════════════════════════════
# evaluate_services batch helper
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvaluateServices:
    def test_all_healthy_batch(self):
        snapshots = [_healthy_snapshot(k) for k in SLO_TARGETS]
        results = evaluate_services(snapshots)
        assert len(results) == len(SLO_TARGETS)
        assert all(r.passed for r in results)

    def test_unknown_service_name_returns_fail_result(self):
        snapshot = SLISnapshot(
            service_name="unknown_service",
            availability=1.0,
            latency_p95_ms=50.0,
            error_rate=0.001,
            dependency_health=0.999,
            window_minutes=60.0,
        )
        results = evaluate_services([snapshot])
        assert len(results) == 1
        assert results[0].passed is False
        assert results[0].severity == "SEV-1"
        assert any("SLO target not found" in issue for issue in results[0].issues)

    def test_mixed_results(self):
        snapshots = [
            _healthy_snapshot("ocean_core"),
            SLISnapshot(
                service_name="translation",
                availability=0.990,  # below 99.9%
                latency_p95_ms=100.0,
                error_rate=0.001,
                dependency_health=0.999,
                window_minutes=60.0,
            ),
        ]
        results = evaluate_services(snapshots)
        assert results[0].passed is True
        assert results[1].passed is False


# ═══════════════════════════════════════════════════════════════════════════════
# SLOGateResult fields
# ═══════════════════════════════════════════════════════════════════════════════

class TestSLOGateResultFields:
    def test_evaluated_at_is_iso8601(self):
        snapshot = _healthy_snapshot("ollama")
        result = evaluate_service(snapshot)
        # Must parse without error
        from datetime import datetime, timezone
        dt = datetime.fromisoformat(result.evaluated_at.replace("Z", "+00:00"))
        assert dt is not None

    def test_error_budget_remaining_between_0_and_100(self):
        for key in SLO_TARGETS:
            snapshot = _healthy_snapshot(key)
            result = evaluate_service(snapshot)
            assert 0.0 <= result.error_budget_remaining_pct <= 100.0, key

    def test_burn_rate_non_negative(self):
        snapshot = _healthy_snapshot("backend_api")
        result = evaluate_service(snapshot)
        assert result.burn_rate >= 0.0
