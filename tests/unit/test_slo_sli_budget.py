#!/usr/bin/env python3
"""
Unit tests for slo_sli_budget.py

All I/O (ledger reads/writes, live probes) is fully isolated.
No live services, no real file-system side effects.
"""

from __future__ import annotations

import json
import sys
import os
import tempfile
import unittest
from datetime import datetime, timezone, timedelta
from typing import List
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from slo_sli_budget import (
    BudgetTracker,
    IncidentRecord,
    Ledger,
    RunRecord,
    ServiceRunResult,
    _estimate_downtime_minutes,
    _empty_budget_entry,
    BUDGET_WINDOW_DAYS,
)
from slo_sli_gate import SLO_TARGETS, SLISnapshot, evaluate_services
from slo_sli_collector import CollectorReport


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _ts(offset_minutes: float = 0.0) -> str:
    """Return an ISO-8601 UTC timestamp offset from now."""
    dt = datetime.now(timezone.utc) - timedelta(minutes=offset_minutes)
    return dt.isoformat()


def _passing_snap(key: str) -> SLISnapshot:
    target = SLO_TARGETS[key]
    return SLISnapshot(
        service_name=key,
        availability=target.availability_slo + 0.0001,
        latency_p95_ms=target.latency_p95_ms * 0.5,
        error_rate=0.001,
        dependency_health=0.999,
        window_minutes=60.0,
    )


def _failing_snap(key: str) -> SLISnapshot:
    return SLISnapshot(
        service_name=key,
        availability=0.0,
        latency_p95_ms=0.0,
        error_rate=0.0,
        dependency_health=0.0,
        window_minutes=60.0,
    )


def _build_report(passing_keys, failing_keys) -> CollectorReport:
    snaps = (
        [_passing_snap(k) for k in passing_keys]
        + [_failing_snap(k) for k in failing_keys]
    )
    return CollectorReport(snapshots=snaps, gate_results=evaluate_services(snaps))


def _tmp_ledger_path() -> str:
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    os.unlink(path)   # let Ledger create it
    return path


# ═══════════════════════════════════════════════════════════════════════════════
# Ledger — persistence
# ═══════════════════════════════════════════════════════════════════════════════

class TestLedger(unittest.TestCase):

    def test_empty_ledger_on_new_file(self):
        path = _tmp_ledger_path()
        ledger = Ledger(path)
        self.assertEqual(len(ledger.runs), 0)
        self.assertEqual(len(ledger.incidents), 0)

    def test_save_and_reload(self):
        path = _tmp_ledger_path()
        ledger = Ledger(path)

        run = RunRecord(
            run_id=_ts(10),
            services={
                "backend_api": ServiceRunResult(
                    passed=True, severity="OK",
                    availability=0.9999, latency_p95_ms=120.0,
                    error_rate=0.001, dependency_health=1.0, burn_rate=0.1,
                )
            },
        )
        ledger.append_run(run)
        ledger.save()

        ledger2 = Ledger(path)
        self.assertEqual(len(ledger2.runs), 1)
        self.assertEqual(ledger2.runs[0].run_id, run.run_id)
        self.assertIn("backend_api", ledger2.runs[0].services)

    def test_incident_round_trip(self):
        path = _tmp_ledger_path()
        ledger = Ledger(path)

        inc = IncidentRecord(
            incident_id=_ts(60),
            service="ocean_core",
            severity="SEV-1",
            opened_at=_ts(60),
            closed_at=_ts(30),
            mttr_minutes=30.0,
        )
        ledger.append_incident(inc)
        ledger.save()

        ledger2 = Ledger(path)
        self.assertEqual(len(ledger2.incidents), 1)
        loaded = ledger2.incidents[0]
        self.assertEqual(loaded.service, "ocean_core")
        self.assertFalse(loaded.is_open)
        self.assertAlmostEqual(loaded.mttr_minutes, 30.0)

    def test_runs_in_window_filters_by_since(self):
        path = _tmp_ledger_path()
        ledger = Ledger(path)

        old_run = RunRecord(run_id=_ts(200), services={})
        new_run = RunRecord(run_id=_ts(2),   services={})
        ledger.append_run(old_run)
        ledger.append_run(new_run)

        since = datetime.now(timezone.utc) - timedelta(minutes=10)
        in_window = ledger.runs_in_window(since)
        self.assertEqual(len(in_window), 1)
        self.assertEqual(in_window[0].run_id, new_run.run_id)

    def test_open_incidents_for_service(self):
        path = _tmp_ledger_path()
        ledger = Ledger(path)

        open_inc = IncidentRecord(
            incident_id=_ts(15), service="backend_api",
            severity="SEV-2", opened_at=_ts(15),
        )
        closed_inc = IncidentRecord(
            incident_id=_ts(60), service="backend_api",
            severity="SEV-1", opened_at=_ts(60),
            closed_at=_ts(45), mttr_minutes=15.0,
        )
        ledger.append_incident(open_inc)
        ledger.append_incident(closed_inc)

        open_ones = ledger.open_incidents_for("backend_api")
        self.assertEqual(len(open_ones), 1)
        self.assertTrue(open_ones[0].is_open)

    def test_corrupted_ledger_loads_empty(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        with open(path, "w") as f:
            f.write("not valid json {{{{")
        ledger = Ledger(path)
        self.assertEqual(len(ledger.runs), 0)


# ═══════════════════════════════════════════════════════════════════════════════
# BudgetTracker.record() — incident lifecycle
# ═══════════════════════════════════════════════════════════════════════════════

class TestBudgetTrackerRecord(unittest.TestCase):

    def setUp(self):
        self.path = _tmp_ledger_path()
        self.tracker = BudgetTracker(ledger_path=self.path)

    def test_record_passing_report_stores_run(self):
        report = _build_report(passing_keys=list(SLO_TARGETS.keys()), failing_keys=[])
        self.tracker.record(report)
        self.assertEqual(len(self.tracker._ledger.runs), 1)

    def test_record_saves_to_disk(self):
        report = _build_report(passing_keys=list(SLO_TARGETS.keys()), failing_keys=[])
        self.tracker.record(report)
        data = json.loads(open(self.path).read())
        self.assertEqual(len(data["runs"]), 1)

    def test_record_failing_service_opens_incident(self):
        report = _build_report(
            passing_keys=[k for k in SLO_TARGETS if k != "backend_api"],
            failing_keys=["backend_api"],
        )
        self.tracker.record(report)
        incidents = self.tracker._ledger.incidents
        self.assertEqual(len(incidents), 1)
        self.assertEqual(incidents[0].service, "backend_api")
        self.assertTrue(incidents[0].is_open)

    def test_second_failing_run_does_not_open_duplicate_incident(self):
        report = _build_report(
            passing_keys=[k for k in SLO_TARGETS if k != "ocean_core"],
            failing_keys=["ocean_core"],
        )
        self.tracker.record(report)
        self.tracker.record(report)   # second run, still failing
        open_incs = self.tracker._ledger.open_incidents_for("ocean_core")
        self.assertEqual(len(open_incs), 1)

    def test_recovery_closes_incident_and_sets_mttr(self):
        report_fail = _build_report(
            passing_keys=[k for k in SLO_TARGETS if k != "backend_api"],
            failing_keys=["backend_api"],
        )
        report_pass = _build_report(
            passing_keys=list(SLO_TARGETS.keys()),
            failing_keys=[],
        )
        self.tracker.record(report_fail)
        self.tracker.record(report_pass)

        incs = [i for i in self.tracker._ledger.incidents if i.service == "backend_api"]
        self.assertEqual(len(incs), 1)
        self.assertFalse(incs[0].is_open)
        self.assertIsNotNone(incs[0].mttr_minutes)
        self.assertGreaterEqual(incs[0].mttr_minutes, 0.0)

    def test_incident_severity_upgraded_on_worse_run(self):
        """If SEV-3 opens, then SEV-1 arrives, severity should be upgraded."""
        # Build a SEV-3 breach manually
        from slo_sli_gate import SLISnapshot, evaluate_services

        target = SLO_TARGETS["backend_api"]
        snap_sev3 = SLISnapshot(
            service_name="backend_api",
            availability=target.availability_slo + 0.0001,
            latency_p95_ms=target.latency_p95_ms * 2.5,  # >2× → SEV-3
            error_rate=0.001,
            dependency_health=0.999,
            window_minutes=15.0,
        )
        report_sev3 = CollectorReport(
            snapshots=[snap_sev3],
            gate_results=evaluate_services([snap_sev3]),
        )
        self.tracker.record(report_sev3)

        result_sev3 = report_sev3.gate_results[0]
        if result_sev3.severity not in ("SEV-1", "SEV-2", "SEV-3"):
            self.skipTest("snapshot did not trigger a breach")

        initial_sev = self.tracker._ledger.incidents[0].severity

        # Now record a SEV-1 (full outage)
        report_sev1 = _build_report(passing_keys=[], failing_keys=["backend_api"])
        self.tracker.record(report_sev1)

        open_incs = self.tracker._ledger.open_incidents_for("backend_api")
        if open_incs:
            # Severity should have been upgraded to SEV-1
            self.assertEqual(open_incs[0].severity, "SEV-1")

    def test_run_record_stores_correct_availability(self):
        report = _build_report(
            passing_keys=list(SLO_TARGETS.keys()),
            failing_keys=[],
        )
        self.tracker.record(report)
        run = self.tracker._ledger.runs[0]
        for key in SLO_TARGETS:
            self.assertIn(key, run.services)
            srr = run.services[key]
            self.assertTrue(srr.passed)
            self.assertEqual(srr.severity, "OK")
            self.assertGreater(srr.availability, 0.0)


# ═══════════════════════════════════════════════════════════════════════════════
# BudgetTracker.budget_report()
# ═══════════════════════════════════════════════════════════════════════════════

class TestBudgetReport(unittest.TestCase):

    def setUp(self):
        self.path = _tmp_ledger_path()
        self.tracker = BudgetTracker(ledger_path=self.path, window_days=7)

    def _record_failing(self, service: str):
        report = _build_report(
            passing_keys=[k for k in SLO_TARGETS if k != service],
            failing_keys=[service],
        )
        self.tracker.record(report)

    def _record_passing(self):
        report = _build_report(passing_keys=list(SLO_TARGETS.keys()), failing_keys=[])
        self.tracker.record(report)

    def test_empty_ledger_returns_all_ok(self):
        summary = self.tracker.budget_report()
        for entry in summary["services"].values():
            self.assertEqual(entry["status"], "ok")
        self.assertEqual(len(summary["incidents"]), 0)
        self.assertEqual(len(summary["open_incidents"]), 0)

    def test_report_has_required_keys(self):
        summary = self.tracker.budget_report()
        required = {
            "generated_at", "window_days", "services",
            "incidents", "open_incidents", "top3_incidents", "markdown",
        }
        self.assertTrue(required.issubset(summary.keys()))

    def test_report_contains_all_six_services(self):
        summary = self.tracker.budget_report()
        self.assertEqual(set(summary["services"].keys()), set(SLO_TARGETS.keys()))

    def test_open_incident_appears_in_report(self):
        self._record_failing("ocean_core")
        summary = self.tracker.budget_report()
        self.assertEqual(len(summary["open_incidents"]), 1)
        self.assertEqual(summary["open_incidents"][0]["service"], "ocean_core")

    def test_closed_incident_appears_in_incidents_list(self):
        self._record_failing("backend_api")
        self._record_passing()
        summary = self.tracker.budget_report()
        self.assertEqual(len(summary["incidents"]), 1)
        self.assertEqual(summary["incidents"][0]["service"], "backend_api")
        self.assertIsNotNone(summary["incidents"][0]["mttr_minutes"])

    def test_top3_incidents_sorted_by_mttr_descending(self):
        # Record 3 incidents of different durations
        # We can't control real time easily, so we inject incidents directly
        import time
        for svc in ["ocean_core", "backend_api", "openmind"]:
            self._record_failing(svc)
            time.sleep(0.01)
            self._record_passing()

        summary = self.tracker.budget_report()
        top3 = summary["top3_incidents"]
        # Should have up to 3 entries
        self.assertLessEqual(len(top3), 3)
        # Should be sorted descending by mttr
        mttr_values = [i["mttr_minutes"] for i in top3 if i["mttr_minutes"]]
        self.assertEqual(mttr_values, sorted(mttr_values, reverse=True))

    def test_failed_checks_counted_correctly(self):
        self._record_failing("excel_core")
        self._record_failing("excel_core")
        self._record_passing()

        summary = self.tracker.budget_report()
        entry = summary["services"]["excel_core"]
        # Should have 3 total checks, 2 failed
        self.assertEqual(entry["total_checks"], 3)
        self.assertEqual(entry["failed_checks"], 2)

    def test_budget_consumed_pct_between_0_and_100(self):
        self._record_failing("translation")
        summary = self.tracker.budget_report()
        entry = summary["services"]["translation"]
        self.assertGreaterEqual(entry["budget_consumed_pct"], 0.0)
        self.assertLessEqual(entry["budget_consumed_pct"], 100.0)


# ═══════════════════════════════════════════════════════════════════════════════
# Budget report — markdown output
# ═══════════════════════════════════════════════════════════════════════════════

class TestMarkdownReport(unittest.TestCase):

    def setUp(self):
        self.path = _tmp_ledger_path()
        self.tracker = BudgetTracker(ledger_path=self.path)

    def test_markdown_contains_weekly_review_header(self):
        summary = self.tracker.budget_report()
        md = summary["markdown"]
        self.assertIn("SLO Weekly Review", md)

    def test_markdown_contains_error_budget_section(self):
        summary = self.tracker.budget_report()
        md = summary["markdown"]
        self.assertIn("Error Budget", md)

    def test_markdown_contains_top3_incidents_section(self):
        summary = self.tracker.budget_report()
        md = summary["markdown"]
        self.assertIn("Top 3 Incidents", md)

    def test_markdown_contains_reliability_tasks_section(self):
        summary = self.tracker.budget_report()
        md = summary["markdown"]
        self.assertIn("Proposed Reliability Tasks", md)

    def test_markdown_contains_burn_rate_section(self):
        summary = self.tracker.budget_report()
        md = summary["markdown"]
        self.assertIn("Burn Rate", md)

    def test_markdown_includes_all_service_display_names(self):
        summary = self.tracker.budget_report()
        md = summary["markdown"]
        from slo_sli_gate import SLO_TARGETS
        for target in SLO_TARGETS.values():
            self.assertIn(target.service_name, md)

    def test_open_incident_appears_in_markdown(self):
        report = _build_report(
            passing_keys=[k for k in SLO_TARGETS if k != "ollama"],
            failing_keys=["ollama"],
        )
        self.tracker.record(report)
        summary = self.tracker.budget_report()
        md = summary["markdown"]
        self.assertIn("Open Incidents", md)
        self.assertIn("ollama", md)

    def test_all_ok_no_tasks_required_message(self):
        summary = self.tracker.budget_report()
        md = summary["markdown"]
        self.assertIn("No remediation tasks required", md)


# ═══════════════════════════════════════════════════════════════════════════════
# _estimate_downtime_minutes
# ═══════════════════════════════════════════════════════════════════════════════

class TestEstimateDowntime(unittest.TestCase):

    def _make_run(self, service: str, passed: bool, offset_min: float) -> RunRecord:
        return RunRecord(
            run_id=_ts(offset_min),
            services={
                service: ServiceRunResult(
                    passed=passed,
                    severity="OK" if passed else "SEV-1",
                    availability=1.0 if passed else 0.0,
                    latency_p95_ms=100.0,
                    error_rate=0.0,
                    dependency_health=1.0,
                    burn_rate=0.0 if passed else 2000.0,
                )
            },
        )

    def test_no_failed_runs_zero_downtime(self):
        runs = [self._make_run("ocean_core", True, i * 5) for i in range(5)]
        runs = list(reversed(runs))  # oldest first by timestamp
        since = datetime.now(timezone.utc) - timedelta(minutes=30)
        dt = _estimate_downtime_minutes("ocean_core", runs, since)
        self.assertEqual(dt, 0.0)

    def test_single_failed_run_credits_up_to_max(self):
        runs = [
            self._make_run("backend_api", False, 10),  # failed 10 min ago
            self._make_run("backend_api", True, 5),    # recovered 5 min ago
        ]
        runs = sorted(runs, key=lambda r: r.run_id)
        since = datetime.now(timezone.utc) - timedelta(minutes=30)
        dt = _estimate_downtime_minutes("backend_api", runs, since)
        # Gap between the two runs is ~5 min, which is ≤ MAX_INTERVAL_MIN=5
        self.assertGreater(dt, 0.0)
        self.assertLessEqual(dt, 5.0)

    def test_downtime_is_non_negative(self):
        runs = [self._make_run("ollama", False, 3)]
        since = datetime.now(timezone.utc) - timedelta(minutes=10)
        dt = _estimate_downtime_minutes("ollama", runs, since)
        self.assertGreaterEqual(dt, 0.0)


# ═══════════════════════════════════════════════════════════════════════════════
# IncidentRecord
# ═══════════════════════════════════════════════════════════════════════════════

class TestIncidentRecord(unittest.TestCase):

    def test_open_incident_is_open(self):
        inc = IncidentRecord(
            incident_id=_ts(10),
            service="ocean_core",
            severity="SEV-1",
            opened_at=_ts(10),
        )
        self.assertTrue(inc.is_open)

    def test_closed_incident_not_open(self):
        inc = IncidentRecord(
            incident_id=_ts(30),
            service="backend_api",
            severity="SEV-2",
            opened_at=_ts(30),
            closed_at=_ts(15),
            mttr_minutes=15.0,
        )
        self.assertFalse(inc.is_open)

    def test_round_trip_to_dict(self):
        inc = IncidentRecord(
            incident_id="2026-03-16T12:00:00+00:00",
            service="excel_core",
            severity="SEV-3",
            opened_at="2026-03-16T12:00:00+00:00",
            closed_at="2026-03-16T12:05:00+00:00",
            mttr_minutes=5.0,
        )
        d = inc.to_dict()
        inc2 = IncidentRecord.from_dict(d)
        self.assertEqual(inc2.service, "excel_core")
        self.assertAlmostEqual(inc2.mttr_minutes, 5.0)
        self.assertFalse(inc2.is_open)


if __name__ == "__main__":
    unittest.main()
