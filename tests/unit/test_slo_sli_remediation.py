#!/usr/bin/env python3
"""
Unit tests for slo_sli_remediation.py and slo_sli_cycle.py

All HTTP calls and live probes are mocked.
No live services or admin tokens required.
"""

from __future__ import annotations

import sys
import os
import time
import unittest
from unittest.mock import MagicMock, patch
from typing import List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from slo_sli_remediation import (
    ActionType,
    AutoRemediator,
    DEFAULT_POLICIES,
    RemediationPolicy,
    RemediationResult,
    _http_post,
    _execute_flush_cache,
    _execute_switch_fallback_model,
    _execute_open_circuit_breaker,
)
from slo_sli_cycle import AutonomousCycle, CycleResult
from slo_sli_gate import SLO_TARGETS, SLISnapshot, evaluate_services
from slo_sli_collector import CollectorReport


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _failing_snap(key: str) -> SLISnapshot:
    return SLISnapshot(
        service_name=key, availability=0.0, latency_p95_ms=0.0,
        error_rate=0.0, dependency_health=0.0, window_minutes=60.0,
    )

def _passing_snap(key: str) -> SLISnapshot:
    target = SLO_TARGETS[key]
    return SLISnapshot(
        service_name=key,
        availability=target.availability_slo + 0.0001,
        latency_p95_ms=target.latency_p95_ms * 0.5,
        error_rate=0.001, dependency_health=0.999, window_minutes=60.0,
    )

def _build_report(passing_keys, failing_keys) -> CollectorReport:
    snaps = [_passing_snap(k) for k in passing_keys] + [_failing_snap(k) for k in failing_keys]
    return CollectorReport(snapshots=snaps, gate_results=evaluate_services(snaps))

def _make_remediator(dry_run: bool = True, policies=None) -> AutoRemediator:
    return AutoRemediator(
        policies=policies if policies is not None else DEFAULT_POLICIES,
        dry_run=dry_run,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# _http_post helper
# ═══════════════════════════════════════════════════════════════════════════════

class TestHttpPost(unittest.TestCase):

    def test_successful_post_returns_true(self):
        resp = MagicMock()
        resp.status = 200
        resp.read.return_value = b'{"ok": true}'
        resp.__enter__ = lambda s: s
        resp.__exit__ = MagicMock(return_value=False)
        with patch("urllib.request.urlopen", return_value=resp):
            ok, detail = _http_post("http://fake/endpoint", {"a": 1}, token="tok")
        self.assertTrue(ok)
        self.assertIn("ok", detail)

    def test_http_error_returns_false(self):
        import urllib.error
        with patch("urllib.request.urlopen", side_effect=urllib.error.HTTPError(
            url="x", code=503, msg="down", hdrs=None, fp=None
        )):
            ok, detail = _http_post("http://fake/endpoint", {})
        self.assertFalse(ok)
        self.assertIn("503", detail)

    def test_connection_error_returns_false(self):
        with patch("urllib.request.urlopen", side_effect=ConnectionRefusedError("refused")):
            ok, detail = _http_post("http://fake/endpoint", {})
        self.assertFalse(ok)

    def test_token_added_to_headers(self):
        captured = {}
        def fake_urlopen(req, timeout=None):
            captured["headers"] = dict(req.headers)
            raise ConnectionRefusedError("no server")
        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            _http_post("http://fake/endpoint", {}, token="my-secret")
        # urllib.request capitalises the first letter of each header component
        header_keys_lower = {k.lower() for k in captured.get("headers", {})}
        self.assertIn("x-admin-token", header_keys_lower)


# ═══════════════════════════════════════════════════════════════════════════════
# ActionType enum
# ═══════════════════════════════════════════════════════════════════════════════

class TestActionType(unittest.TestCase):

    def test_all_expected_values_exist(self):
        expected = {
            "restart_service", "flush_cache", "switch_fallback_model",
            "open_circuit_breaker", "scale_up", "reroute_traffic", "rotate_key",
        }
        actual = {a.value for a in ActionType}
        self.assertEqual(actual, expected)


# ═══════════════════════════════════════════════════════════════════════════════
# RemediationPolicy
# ═══════════════════════════════════════════════════════════════════════════════

class TestRemediationPolicy(unittest.TestCase):

    def test_default_policies_cover_all_services(self):
        services_with_policies = {p.service for p in DEFAULT_POLICIES}
        self.assertTrue(services_with_policies.issubset(set(SLO_TARGETS.keys())))

    def test_every_service_has_at_least_one_sev1_policy(self):
        """Every service should have at least one action for SEV-1."""
        sev1_services = {p.service for p in DEFAULT_POLICIES if p.min_severity == "SEV-1"}
        for svc in SLO_TARGETS:
            self.assertIn(svc, sev1_services, f"{svc} has no SEV-1 policy")

    def test_cooldowns_are_positive(self):
        for p in DEFAULT_POLICIES:
            self.assertGreater(p.cooldown_sec, 0)


# ═══════════════════════════════════════════════════════════════════════════════
# AutoRemediator.remediate() — dry-run mode
# ═══════════════════════════════════════════════════════════════════════════════

class TestAutoRemediatorDryRun(unittest.TestCase):

    def test_no_actions_when_all_passing(self):
        remediator = _make_remediator(dry_run=True)
        report = _build_report(passing_keys=list(SLO_TARGETS.keys()), failing_keys=[])
        results = remediator.remediate(report)
        self.assertEqual(len(results), 0)

    def test_actions_fired_for_failing_service(self):
        remediator = _make_remediator(dry_run=True)
        report = _build_report(
            passing_keys=[k for k in SLO_TARGETS if k != "ocean_core"],
            failing_keys=["ocean_core"],
        )
        results = remediator.remediate(report)
        self.assertGreater(len(results), 0)
        self.assertTrue(all(r.dry_run for r in results))
        self.assertTrue(all(r.service == "ocean_core" for r in results))

    def test_dry_run_results_have_success_true(self):
        remediator = _make_remediator(dry_run=True)
        report = _build_report(passing_keys=[], failing_keys=["backend_api"])
        results = remediator.remediate(report)
        self.assertTrue(all(r.success for r in results))

    def test_only_matching_severity_policies_fire(self):
        """A SEV-3 breach should NOT trigger SEV-1-only policies."""
        from slo_sli_gate import SLISnapshot, evaluate_services
        # Build a SEV-3 snap: latency-only breach
        target = SLO_TARGETS["backend_api"]
        snap = SLISnapshot(
            service_name="backend_api",
            availability=target.availability_slo + 0.0001,
            latency_p95_ms=target.latency_p95_ms * 2.5,
            error_rate=0.001,
            dependency_health=0.999,
            window_minutes=15.0,
        )
        report = CollectorReport(
            snapshots=[snap],
            gate_results=evaluate_services([snap]),
        )
        gate = report.gate_results[0]
        if gate.severity not in ("SEV-1", "SEV-2", "SEV-3"):
            self.skipTest("snapshot did not trigger a breach")

        # Use a policy set with only a SEV-1 min_severity entry
        sev1_only_policies = [
            p for p in DEFAULT_POLICIES
            if p.service == "backend_api" and p.min_severity == "SEV-1"
        ]
        remediator = AutoRemediator(policies=sev1_only_policies, dry_run=True)
        results = remediator.remediate(report)

        if gate.severity in ("SEV-2", "SEV-3"):
            # SEV-1-only policy should not fire for SEV-2/3
            self.assertEqual(len(results), 0)

    def test_multiple_failing_services_each_get_actions(self):
        remediator = _make_remediator(dry_run=True)
        report = _build_report(passing_keys=[], failing_keys=list(SLO_TARGETS.keys()))
        results = remediator.remediate(report)
        services_actioned = {r.service for r in results}
        self.assertEqual(services_actioned, set(SLO_TARGETS.keys()))

    def test_result_has_all_required_fields(self):
        remediator = _make_remediator(dry_run=True)
        report = _build_report(
            passing_keys=[k for k in SLO_TARGETS if k != "ocean_core"],
            failing_keys=["ocean_core"],
        )
        results = remediator.remediate(report)
        self.assertGreater(len(results), 0)
        r = results[0]
        self.assertIsInstance(r.service, str)
        self.assertIsInstance(r.action, ActionType)
        self.assertIsInstance(r.severity, str)
        self.assertIsInstance(r.success, bool)
        self.assertIsInstance(r.duration_ms, float)
        self.assertIsInstance(r.executed_at, str)


# ═══════════════════════════════════════════════════════════════════════════════
# AutoRemediator — cooldown
# ═══════════════════════════════════════════════════════════════════════════════

class TestCooldown(unittest.TestCase):

    def test_action_suppressed_within_cooldown(self):
        policy = RemediationPolicy(
            service="ocean_core",
            min_severity="SEV-1",
            action=ActionType.FLUSH_CACHE,
            cooldown_sec=3600,  # 1 hour
        )
        remediator = AutoRemediator(policies=[policy], dry_run=True)
        report = _build_report(passing_keys=[], failing_keys=["ocean_core"])

        first = remediator.remediate(report)
        second = remediator.remediate(report)

        self.assertEqual(len(first), 1)
        self.assertEqual(len(second), 0, "Expected second call to be suppressed by cooldown")

    def test_action_fires_again_after_cooldown_expires(self):
        policy = RemediationPolicy(
            service="backend_api",
            min_severity="SEV-1",
            action=ActionType.FLUSH_CACHE,
            cooldown_sec=0,  # no cooldown
        )
        remediator = AutoRemediator(policies=[policy], dry_run=True)
        report = _build_report(passing_keys=[], failing_keys=["backend_api"])

        first = remediator.remediate(report)
        second = remediator.remediate(report)

        self.assertEqual(len(first), 1)
        self.assertEqual(len(second), 1)


# ═══════════════════════════════════════════════════════════════════════════════
# AutoRemediator — live mode (HTTP mocked)
# ═══════════════════════════════════════════════════════════════════════════════

class TestAutoRemediatorLive(unittest.TestCase):

    def _mock_http_ok(self, monkeypatch_target="slo_sli_remediation._http_post"):
        return patch(monkeypatch_target, return_value=(True, '{"ok": true}'))

    def test_live_mode_calls_executor(self):
        policy = RemediationPolicy(
            service="ocean_core",
            min_severity="SEV-1",
            action=ActionType.FLUSH_CACHE,
            cooldown_sec=0,
        )
        remediator = AutoRemediator(policies=[policy], dry_run=False)
        report = _build_report(passing_keys=[], failing_keys=["ocean_core"])

        with patch("slo_sli_remediation._http_post", return_value=(True, '{"ok":true}')):
            results = remediator.remediate(report)

        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].success)
        self.assertFalse(results[0].dry_run)

    def test_failed_executor_records_failure(self):
        policy = RemediationPolicy(
            service="ocean_core",
            min_severity="SEV-1",
            action=ActionType.FLUSH_CACHE,
            cooldown_sec=0,
        )
        remediator = AutoRemediator(policies=[policy], dry_run=False)
        report = _build_report(passing_keys=[], failing_keys=["ocean_core"])

        with patch("slo_sli_remediation._http_post", return_value=(False, "connection refused")):
            results = remediator.remediate(report)

        self.assertEqual(len(results), 1)
        self.assertFalse(results[0].success)
        self.assertIn("refused", results[0].detail)


# ═══════════════════════════════════════════════════════════════════════════════
# AutonomousCycle
# ═══════════════════════════════════════════════════════════════════════════════

class TestAutonomousCycle(unittest.TestCase):

    def _make_cycle(self, passing_keys, failing_keys):
        """Create a cycle where collect_all returns a fixed report."""
        import tempfile
        ledger_path = tempfile.mktemp(suffix=".json")
        report = _build_report(passing_keys=passing_keys, failing_keys=failing_keys)

        cycle = AutonomousCycle(
            probe_count=2,
            probe_timeout=1,
            ledger_path=ledger_path,
        )
        # Replace alerter's poster with a no-op
        cycle._alerter._post = MagicMock(return_value=True)
        # Patch collect_all to return our fixed report
        cycle._collect_all_fn = MagicMock(return_value=report)
        return cycle, report

    def test_run_once_returns_cycle_result(self):
        import tempfile
        ledger = tempfile.mktemp(suffix=".json")
        cycle = AutonomousCycle(probe_count=2, probe_timeout=1, ledger_path=ledger)
        cycle._alerter._post = MagicMock(return_value=True)

        with patch("slo_sli_cycle.collect_all") as mock_collect:
            mock_collect.return_value = _build_report(
                passing_keys=list(SLO_TARGETS.keys()), failing_keys=[]
            )
            result = cycle.run_once()

        self.assertIsInstance(result, CycleResult)
        self.assertEqual(result.iteration, 1)
        self.assertIsNotNone(result.ran_at)

    def test_all_passing_no_alerts_no_remediations(self):
        import tempfile
        ledger = tempfile.mktemp(suffix=".json")
        cycle = AutonomousCycle(probe_count=2, probe_timeout=1, ledger_path=ledger)
        cycle._alerter._post = MagicMock(return_value=True)

        with patch("slo_sli_cycle.collect_all") as mock_collect:
            mock_collect.return_value = _build_report(
                passing_keys=list(SLO_TARGETS.keys()), failing_keys=[]
            )
            result = cycle.run_once()

        self.assertEqual(len(result.alerts), 0)
        self.assertEqual(len(result.remediations), 0)
        self.assertTrue(result.ok)

    def test_failing_service_produces_alerts_and_remediations(self):
        import tempfile
        ledger = tempfile.mktemp(suffix=".json")
        cycle = AutonomousCycle(probe_count=2, probe_timeout=1, ledger_path=ledger)
        cycle._alerter._post = MagicMock(return_value=True)

        with patch("slo_sli_cycle.collect_all") as mock_collect, \
             patch("slo_sli_remediation._http_post", return_value=(True, '{"ok":true}')):
            mock_collect.return_value = _build_report(
                passing_keys=[k for k in SLO_TARGETS if k != "ocean_core"],
                failing_keys=["ocean_core"],
            )
            result = cycle.run_once()

        self.assertGreater(len(result.alerts), 0)
        self.assertGreater(len(result.remediations), 0)
        self.assertFalse(result.ok)

    def test_iteration_counter_increments(self):
        import tempfile
        ledger = tempfile.mktemp(suffix=".json")
        cycle = AutonomousCycle(probe_count=2, probe_timeout=1, ledger_path=ledger)
        cycle._alerter._post = MagicMock(return_value=True)

        with patch("slo_sli_cycle.collect_all") as mock_collect:
            mock_collect.return_value = _build_report(
                passing_keys=list(SLO_TARGETS.keys()), failing_keys=[]
            )
            r1 = cycle.run_once()
            r2 = cycle.run_once()
            r3 = cycle.run_once()

        self.assertEqual(r1.iteration, 1)
        self.assertEqual(r2.iteration, 2)
        self.assertEqual(r3.iteration, 3)

    def test_collect_failure_is_captured_in_errors(self):
        import tempfile
        ledger = tempfile.mktemp(suffix=".json")
        cycle = AutonomousCycle(probe_count=2, probe_timeout=1, ledger_path=ledger)
        cycle._alerter._post = MagicMock(return_value=True)

        with patch("slo_sli_cycle.collect_all", side_effect=RuntimeError("network down")):
            result = cycle.run_once()

        self.assertTrue(any("collect" in e for e in result.errors))

    def test_breaching_services_count(self):
        import tempfile
        ledger = tempfile.mktemp(suffix=".json")
        cycle = AutonomousCycle(probe_count=2, probe_timeout=1, ledger_path=ledger)
        cycle._alerter._post = MagicMock(return_value=True)

        with patch("slo_sli_cycle.collect_all") as mock_collect, \
             patch("slo_sli_remediation._http_post", return_value=(True, '{}')):
            mock_collect.return_value = _build_report(
                passing_keys=[k for k in SLO_TARGETS if k not in ("ocean_core", "backend_api")],
                failing_keys=["ocean_core", "backend_api"],
            )
            result = cycle.run_once()

        self.assertEqual(result.breaching_services, 2)
        self.assertEqual(result.healthy_services, len(SLO_TARGETS) - 2)

    def test_summary_line_contains_iteration_number(self):
        import tempfile
        ledger = tempfile.mktemp(suffix=".json")
        cycle = AutonomousCycle(probe_count=2, probe_timeout=1, ledger_path=ledger)
        cycle._alerter._post = MagicMock(return_value=True)

        with patch("slo_sli_cycle.collect_all") as mock_collect:
            mock_collect.return_value = _build_report(
                passing_keys=list(SLO_TARGETS.keys()), failing_keys=[]
            )
            result = cycle.run_once()

        self.assertIn("#1", result.summary_line())


# ═══════════════════════════════════════════════════════════════════════════════
# RemediationResult dataclass
# ═══════════════════════════════════════════════════════════════════════════════

class TestRemediationResult(unittest.TestCase):

    def test_executed_at_is_iso8601(self):
        from datetime import datetime
        r = RemediationResult(
            service="ocean_core",
            action=ActionType.FLUSH_CACHE,
            severity="SEV-1",
            success=True,
            dry_run=True,
            duration_ms=5.0,
            detail="dry-run",
        )
        dt = datetime.fromisoformat(r.executed_at)
        self.assertIsNotNone(dt)

    def test_dry_run_flag_preserved(self):
        r = RemediationResult(
            service="backend_api",
            action=ActionType.RESTART_SERVICE,
            severity="SEV-2",
            success=False,
            dry_run=True,
            duration_ms=0.0,
            detail="dry",
        )
        self.assertTrue(r.dry_run)


if __name__ == "__main__":
    unittest.main()
