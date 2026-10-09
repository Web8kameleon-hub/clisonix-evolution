#!/usr/bin/env python3
"""
Unit tests for slo_sli_collector.py

All network calls are mocked — no real services are required.
"""

from __future__ import annotations

import io
import json
import sys
import os
import unittest
from unittest.mock import MagicMock, patch
from typing import List

# Allow importing from the repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from slo_sli_collector import (
    ProbeResult,
    ServiceConfig,
    CollectorReport,
    SLO_TARGETS,
    SERVICE_CONFIG,
    _probe_once,
    _parse_dependency_health,
    _latency_p95,
    collect_snapshot,
    collect_all,
    _format_table,
)
from slo_sli_gate import SLISnapshot, evaluate_services


# ═══════════════════════════════════════════════════════════════════════════════
# _parse_dependency_health
# ═══════════════════════════════════════════════════════════════════════════════

class TestParseDependencyHealth(unittest.TestCase):

    def test_explicit_dependency_health_key(self):
        body = json.dumps({"dependency_health": 0.97}).encode()
        self.assertAlmostEqual(_parse_dependency_health(body), 0.97)

    def test_upstream_health_key(self):
        body = json.dumps({"upstream_health": 0.993}).encode()
        self.assertAlmostEqual(_parse_dependency_health(body), 0.993)

    def test_dependencies_dict(self):
        body = json.dumps({"dependencies": {"healthy": 9, "total": 10}}).encode()
        self.assertAlmostEqual(_parse_dependency_health(body), 0.9)

    def test_missing_key_returns_1(self):
        body = json.dumps({"status": "ok"}).encode()
        self.assertEqual(_parse_dependency_health(body), 1.0)

    def test_invalid_json_returns_1(self):
        self.assertEqual(_parse_dependency_health(b"not json"), 1.0)

    def test_empty_bytes_returns_1(self):
        self.assertEqual(_parse_dependency_health(b""), 1.0)

    def test_value_clamped_to_0_1(self):
        body = json.dumps({"dependency_health": 1.5}).encode()
        self.assertEqual(_parse_dependency_health(body), 1.0)

    def test_zero_total_in_dependencies(self):
        body = json.dumps({"dependencies": {"healthy": 0, "total": 0}}).encode()
        self.assertEqual(_parse_dependency_health(body), 1.0)


# ═══════════════════════════════════════════════════════════════════════════════
# _latency_p95
# ═══════════════════════════════════════════════════════════════════════════════

class TestLatencyP95(unittest.TestCase):

    def test_single_value(self):
        self.assertEqual(_latency_p95([42.0]), 42.0)

    def test_empty_list(self):
        self.assertEqual(_latency_p95([]), 0.0)

    def test_ten_values(self):
        latencies = list(range(1, 11))  # 1..10
        # idx = max(0, int(10 * 0.95) - 1) = max(0, 9-1) = 8  → sorted[8] = 9
        self.assertEqual(_latency_p95(latencies), 9.0)

    def test_sorted_order_irrelevant(self):
        unsorted = [10, 1, 5, 3, 8, 2, 7, 6, 4, 9]
        self.assertEqual(_latency_p95(unsorted), _latency_p95(sorted(unsorted)))


# ═══════════════════════════════════════════════════════════════════════════════
# _probe_once — mock urllib.request.urlopen
# ═══════════════════════════════════════════════════════════════════════════════

class TestProbeOnce(unittest.TestCase):

    def _make_response(self, status: int, body: bytes) -> MagicMock:
        resp = MagicMock()
        resp.status = status
        resp.read.return_value = body
        resp.__enter__ = lambda s: s
        resp.__exit__ = MagicMock(return_value=False)
        return resp

    def test_successful_2xx_probe(self):
        body = json.dumps({"status": "ok", "dependency_health": 0.99}).encode()
        resp = self._make_response(200, body)
        with patch("urllib.request.urlopen", return_value=resp):
            result = _probe_once("http://localhost:8000/health", timeout=3)
        self.assertTrue(result.success)
        self.assertEqual(result.status_code, 200)
        self.assertFalse(result.is_5xx)
        self.assertAlmostEqual(result.dependency_health, 0.99)
        self.assertGreaterEqual(result.latency_ms, 0)

    def test_5xx_probe_marks_is_5xx(self):
        import urllib.error
        exc = urllib.error.HTTPError(
            url="http://x", code=503, msg="Service Unavailable",
            hdrs=None, fp=None
        )
        with patch("urllib.request.urlopen", side_effect=exc):
            result = _probe_once("http://localhost:8000/health", timeout=3)
        self.assertFalse(result.success)
        self.assertTrue(result.is_5xx)
        self.assertEqual(result.status_code, 503)

    def test_connection_refused_gives_status_0(self):
        with patch("urllib.request.urlopen", side_effect=ConnectionRefusedError("refused")):
            result = _probe_once("http://localhost:1/health", timeout=1)
        self.assertFalse(result.success)
        self.assertEqual(result.status_code, 0)
        self.assertFalse(result.is_5xx)

    def test_4xx_is_not_5xx(self):
        import urllib.error
        exc = urllib.error.HTTPError(
            url="http://x", code=404, msg="Not Found",
            hdrs=None, fp=None
        )
        with patch("urllib.request.urlopen", side_effect=exc):
            result = _probe_once("http://localhost/health", timeout=1)
        self.assertFalse(result.success)
        self.assertFalse(result.is_5xx)
        self.assertEqual(result.status_code, 404)


# ═══════════════════════════════════════════════════════════════════════════════
# collect_snapshot — mock _probe_once
# ═══════════════════════════════════════════════════════════════════════════════

class TestCollectSnapshot(unittest.TestCase):

    def _make_probe(self, success: bool, latency_ms: float,
                    status_code: int = 200, is_5xx: bool = False,
                    dep_health: float = 1.0) -> ProbeResult:
        return ProbeResult(
            success=success,
            latency_ms=latency_ms,
            status_code=status_code,
            is_5xx=is_5xx,
            dependency_health=dep_health,
        )

    def test_all_successful_probes(self):
        probes = [self._make_probe(True, 50.0, dep_health=0.995) for _ in range(10)]
        cfg = SERVICE_CONFIG["backend_api"]
        with patch("slo_sli_collector._probe_once", side_effect=probes):
            snap = collect_snapshot(cfg, probe_count=10)
        self.assertEqual(snap.availability, 1.0)
        self.assertEqual(snap.error_rate, 0.0)
        self.assertAlmostEqual(snap.dependency_health, 0.995)
        self.assertGreater(snap.latency_p95_ms, 0)

    def test_half_probes_failed(self):
        probes = (
            [self._make_probe(True, 100.0)] * 5
            + [self._make_probe(False, 10.0, status_code=0)] * 5
        )
        cfg = SERVICE_CONFIG["ocean_core"]
        with patch("slo_sli_collector._probe_once", side_effect=probes):
            snap = collect_snapshot(cfg, probe_count=10)
        self.assertAlmostEqual(snap.availability, 0.5)
        self.assertEqual(snap.error_rate, 0.0)  # failures are connection errors, not 5xx

    def test_5xx_probes_counted_in_error_rate(self):
        probes = (
            [self._make_probe(False, 5.0, status_code=500, is_5xx=True)] * 3
            + [self._make_probe(True, 50.0)] * 7
        )
        cfg = SERVICE_CONFIG["openmind"]
        with patch("slo_sli_collector._probe_once", side_effect=probes):
            snap = collect_snapshot(cfg, probe_count=10)
        self.assertAlmostEqual(snap.error_rate, 0.3)

    def test_all_failed_gives_zero_dep_health(self):
        probes = [self._make_probe(False, 1.0, status_code=0)] * 5
        cfg = SERVICE_CONFIG["ollama"]
        with patch("slo_sli_collector._probe_once", side_effect=probes):
            snap = collect_snapshot(cfg, probe_count=5)
        self.assertEqual(snap.dependency_health, 0.0)

    def test_service_name_matches_config_key(self):
        probes = [self._make_probe(True, 80.0)] * 4
        cfg = SERVICE_CONFIG["excel_core"]
        with patch("slo_sli_collector._probe_once", side_effect=probes):
            snap = collect_snapshot(cfg, probe_count=4)
        self.assertEqual(snap.service_name, "excel_core")

    def test_window_minutes_positive(self):
        probes = [self._make_probe(True, 30.0)] * 3
        cfg = SERVICE_CONFIG["translation"]
        with patch("slo_sli_collector._probe_once", side_effect=probes):
            snap = collect_snapshot(cfg, probe_count=3)
        self.assertGreater(snap.window_minutes, 0)


# ═══════════════════════════════════════════════════════════════════════════════
# collect_all
# ═══════════════════════════════════════════════════════════════════════════════

class TestCollectAll(unittest.TestCase):

    def _healthy_snapshot(self, key: str) -> SLISnapshot:
        target = SLO_TARGETS[key]
        return SLISnapshot(
            service_name=key,
            availability=target.availability_slo + 0.0001,
            latency_p95_ms=target.latency_p95_ms * 0.5,
            error_rate=0.001,
            dependency_health=0.999,
            window_minutes=1.0,
        )

    def test_all_healthy_returns_passed_report(self):
        healthy_snaps = {k: self._healthy_snapshot(k) for k in SLO_TARGETS}

        def fake_collect(cfg: ServiceConfig, probe_count: int = 10, probe_timeout: int = 3) -> SLISnapshot:
            return healthy_snaps[cfg.key]

        with patch("slo_sli_collector.collect_snapshot", side_effect=fake_collect):
            report = collect_all(probe_count=2)

        self.assertTrue(report.all_passed)
        self.assertEqual(len(report.gate_results), 6)
        self.assertEqual(report.highest_severity, "OK")

    def test_one_failing_service_propagates(self):
        def fake_collect(cfg: ServiceConfig, probe_count: int = 10, probe_timeout: int = 3) -> SLISnapshot:
            if cfg.key == "openmind":
                return SLISnapshot(
                    service_name="openmind",
                    availability=0.0,
                    latency_p95_ms=1.0,
                    error_rate=0.0,
                    dependency_health=0.0,
                    window_minutes=1.0,
                )
            target = SLO_TARGETS[cfg.key]
            return SLISnapshot(
                service_name=cfg.key,
                availability=target.availability_slo + 0.0001,
                latency_p95_ms=10.0,
                error_rate=0.0,
                dependency_health=0.999,
                window_minutes=1.0,
            )

        with patch("slo_sli_collector.collect_snapshot", side_effect=fake_collect):
            report = collect_all(probe_count=2)

        self.assertFalse(report.all_passed)
        failing = [r.service_name for r in report.failing_services]
        self.assertIn("openmind", failing)

    def test_report_has_six_results(self):
        def fake_collect(cfg: ServiceConfig, probe_count: int = 10, probe_timeout: int = 3) -> SLISnapshot:
            return SLISnapshot(
                service_name=cfg.key,
                availability=0.5,
                latency_p95_ms=100.0,
                error_rate=0.0,
                dependency_health=0.5,
                window_minutes=0.1,
            )

        with patch("slo_sli_collector.collect_snapshot", side_effect=fake_collect):
            report = collect_all(probe_count=1)

        self.assertEqual(len(report.snapshots), 6)
        self.assertEqual(len(report.gate_results), 6)

    def test_collected_at_is_iso8601(self):
        def fake_collect(cfg: ServiceConfig, probe_count: int = 10, probe_timeout: int = 3) -> SLISnapshot:
            target = SLO_TARGETS[cfg.key]
            return SLISnapshot(
                service_name=cfg.key,
                availability=target.availability_slo + 0.0001,
                latency_p95_ms=10.0,
                error_rate=0.0,
                dependency_health=0.999,
                window_minutes=0.1,
            )

        with patch("slo_sli_collector.collect_snapshot", side_effect=fake_collect):
            report = collect_all(probe_count=1)

        from datetime import datetime
        dt = datetime.fromisoformat(report.collected_at.replace("Z", "+00:00"))
        self.assertIsNotNone(dt)


# ═══════════════════════════════════════════════════════════════════════════════
# CollectorReport helpers
# ═══════════════════════════════════════════════════════════════════════════════

class TestCollectorReport(unittest.TestCase):

    def _make_report(self, passing_keys, failing_keys) -> CollectorReport:
        snaps = []
        results = []
        for key in list(passing_keys) + list(failing_keys):
            target = SLO_TARGETS[key]
            is_passing = key in passing_keys
            snap = SLISnapshot(
                service_name=key,
                availability=target.availability_slo + (0.0001 if is_passing else -0.01),
                latency_p95_ms=50.0,
                error_rate=0.0,
                dependency_health=0.999 if is_passing else 0.0,
                window_minutes=1.0,
            )
            snaps.append(snap)
        results = evaluate_services(snaps)
        return CollectorReport(snapshots=snaps, gate_results=results)

    def test_all_passed_property(self):
        report = self._make_report(passing_keys=list(SLO_TARGETS.keys()), failing_keys=[])
        self.assertTrue(report.all_passed)

    def test_failing_services_subset(self):
        report = self._make_report(
            passing_keys=["ocean_core", "backend_api"],
            failing_keys=["openmind", "excel_core", "ollama", "translation"],
        )
        self.assertFalse(report.all_passed)
        failing_names = [r.service_name for r in report.failing_services]
        self.assertIn("openmind", failing_names)

    def test_highest_severity_ok_when_all_pass(self):
        report = self._make_report(passing_keys=list(SLO_TARGETS.keys()), failing_keys=[])
        self.assertEqual(report.highest_severity, "OK")

    def test_highest_severity_sev1_when_fully_down(self):
        # Put one service at 0% availability to trigger fast-burn SEV-1
        snaps = [
            SLISnapshot(
                service_name="backend_api",
                availability=0.0,
                latency_p95_ms=0.0,
                error_rate=0.0,
                dependency_health=0.0,
                window_minutes=60.0,
            )
        ]
        results = evaluate_services(snaps)
        report = CollectorReport(snapshots=snaps, gate_results=results)
        self.assertEqual(report.highest_severity, "SEV-1")


# ═══════════════════════════════════════════════════════════════════════════════
# _format_table
# ═══════════════════════════════════════════════════════════════════════════════

class TestFormatTable(unittest.TestCase):

    def _build_report(self) -> CollectorReport:
        snaps = [
            SLISnapshot(
                service_name=k,
                availability=0.9999,
                latency_p95_ms=50.0,
                error_rate=0.001,
                dependency_health=0.999,
                window_minutes=1.0,
            )
            for k in SLO_TARGETS
        ]
        results = evaluate_services(snaps)
        return CollectorReport(snapshots=snaps, gate_results=results)

    def test_table_contains_all_service_names(self):
        report = self._build_report()
        table = _format_table(report)
        for key in SLO_TARGETS:
            display = SLO_TARGETS[key].service_name
            self.assertIn(display, table, f"Missing: {display}")

    def test_table_shows_pass_for_healthy_services(self):
        report = self._build_report()
        table = _format_table(report)
        self.assertIn("PASS", table)

    def test_table_shows_overall_ok(self):
        report = self._build_report()
        table = _format_table(report)
        self.assertIn("ALL SERVICES PASSING", table)

    def test_table_shows_fail_for_broken_service(self):
        snaps = [
            SLISnapshot(
                service_name="translation",
                availability=0.0,
                latency_p95_ms=0.0,
                error_rate=0.0,
                dependency_health=0.0,
                window_minutes=60.0,
            )
        ]
        results = evaluate_services(snaps)
        report = CollectorReport(snapshots=snaps, gate_results=results)
        table = _format_table(report)
        self.assertIn("FAIL", table)
        self.assertIn("GATE OPEN", table)


# ═══════════════════════════════════════════════════════════════════════════════
# SERVICE_CONFIG
# ═══════════════════════════════════════════════════════════════════════════════

class TestServiceConfig(unittest.TestCase):

    def test_all_six_services_configured(self):
        self.assertEqual(set(SERVICE_CONFIG.keys()), set(SLO_TARGETS.keys()))

    def test_ports_match_slo_targets(self):
        for key, cfg in SERVICE_CONFIG.items():
            self.assertEqual(cfg.port, SLO_TARGETS[key].port, key)

    def test_url_format(self):
        cfg = SERVICE_CONFIG["backend_api"]
        self.assertTrue(cfg.url.startswith("http://"))
        self.assertIn(":8000", cfg.url)
        self.assertIn("/health", cfg.url)

    def test_env_var_override(self):
        # _build_service_config() reads env vars at call time, so patching the
        # env and calling it directly is the correct way to test this behaviour
        # (the module-level SERVICE_CONFIG is already built at import time).
        with patch.dict(os.environ, {"API_HOST": "my-docker-host"}):
            from slo_sli_collector import _build_service_config
            cfg_map = _build_service_config()
        self.assertEqual(cfg_map["backend_api"].host, "my-docker-host")
        # Other services should not be affected
        self.assertEqual(cfg_map["ocean_core"].host, os.getenv("OCEAN_HOST", "127.0.0.1"))


if __name__ == "__main__":
    unittest.main()
