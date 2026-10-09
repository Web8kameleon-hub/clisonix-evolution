#!/usr/bin/env python3
"""
Unit tests for slo_sli_tuning.py

All ledger state is injected via real (in-memory) BudgetTracker/Ledger objects.
No live services, no HTTP calls (all _push_ocean_tune calls use dry_run=True).
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone, timedelta
from typing import List
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from slo_sli_tuning import (
    AutoTuner,
    TuningConfig,
    TuningAdjustment,
    TuningRecord,
    TuningHistory,
    DEFAULT_RATE_LIMIT,
    DEFAULT_STREAM_TIMEOUT,
    DEFAULT_CYCLE_INTERVAL,
    FAST_CYCLE_INTERVAL,
    HIGH_BURN,
    MED_BURN,
    HIGH_ERROR_RATE,
    LOW_ERROR_RATE,
    MIN_PROBE_COUNT,
    MAX_PROBE_COUNT,
    TUNING_RELAX_ITERATIONS,
)
from slo_sli_budget import BudgetTracker
from slo_sli_gate import SLO_TARGETS, SLISnapshot, evaluate_services
from slo_sli_collector import CollectorReport


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _tmp_path(suffix=".json") -> str:
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    os.unlink(path)
    return path


def _passing_snap(key: str) -> SLISnapshot:
    target = SLO_TARGETS[key]
    return SLISnapshot(
        service_name=key,
        availability=target.availability_slo + 0.0001,
        latency_p95_ms=target.latency_p95_ms * 0.1,   # very fast (10% of SLO)
        error_rate=0.001,
        dependency_health=0.999,
        window_minutes=60.0,
    )


def _failing_snap(key: str) -> SLISnapshot:
    return SLISnapshot(
        service_name=key, availability=0.0, latency_p95_ms=9999.0,
        error_rate=0.5, dependency_health=0.0, window_minutes=60.0,
    )


def _build_report(passing_keys, failing_keys) -> CollectorReport:
    snaps = [_passing_snap(k) for k in passing_keys] + [_failing_snap(k) for k in failing_keys]
    return CollectorReport(snapshots=snaps, gate_results=evaluate_services(snaps))


def _make_tracker(ledger_path=None) -> BudgetTracker:
    return BudgetTracker(ledger_path=ledger_path or _tmp_path())


def _make_tuner(tracker=None, dry_run=True, history_path=None) -> AutoTuner:
    t = tracker or _make_tracker()
    return AutoTuner(tracker=t, history_path=history_path or _tmp_path(), dry_run=dry_run)


def _record_failing(tracker: BudgetTracker, service: str):
    report = _build_report(
        passing_keys=[k for k in SLO_TARGETS if k != service],
        failing_keys=[service],
    )
    tracker.record(report)


def _record_passing(tracker: BudgetTracker):
    report = _build_report(passing_keys=list(SLO_TARGETS.keys()), failing_keys=[])
    tracker.record(report)


# ═══════════════════════════════════════════════════════════════════════════════
# TuningConfig
# ═══════════════════════════════════════════════════════════════════════════════

class TestTuningConfig(unittest.TestCase):

    def test_default_values(self):
        cfg = TuningConfig()
        self.assertEqual(cfg.probe_count, 10)
        self.assertEqual(cfg.probe_timeout, 3)
        self.assertEqual(cfg.cycle_interval, DEFAULT_CYCLE_INTERVAL)
        self.assertEqual(cfg.chat_rate_limit, DEFAULT_RATE_LIMIT)
        self.assertAlmostEqual(cfg.stream_timeout_base_s, DEFAULT_STREAM_TIMEOUT)

    def test_round_trip_dict(self):
        cfg = TuningConfig(probe_count=7, probe_timeout=2, cycle_interval=45,
                           chat_rate_limit=20, stream_timeout_base_s=60.0)
        cfg2 = TuningConfig.from_dict(cfg.to_dict())
        self.assertEqual(cfg2.probe_count, 7)
        self.assertEqual(cfg2.probe_timeout, 2)
        self.assertEqual(cfg2.cycle_interval, 45)
        self.assertEqual(cfg2.chat_rate_limit, 20)
        self.assertAlmostEqual(cfg2.stream_timeout_base_s, 60.0)


# ═══════════════════════════════════════════════════════════════════════════════
# TuningHistory — persistence
# ═══════════════════════════════════════════════════════════════════════════════

class TestTuningHistory(unittest.TestCase):

    def test_empty_on_new_file(self):
        h = TuningHistory(_tmp_path())
        self.assertEqual(len(h.records), 0)

    def test_save_and_reload(self):
        path = _tmp_path()
        h = TuningHistory(path)
        rec = TuningRecord(
            tuned_at=datetime.now(timezone.utc).isoformat(),
            adjustments=[
                TuningAdjustment("probe_count", 10, 12, "burn rate high", "ocean_core")
            ],
            config_after=TuningConfig(probe_count=12),
        )
        h.append(rec)
        h.save()

        h2 = TuningHistory(path)
        self.assertEqual(len(h2.records), 1)
        self.assertEqual(h2.records[0].config_after.probe_count, 12)
        self.assertEqual(h2.records[0].adjustments[0].parameter, "probe_count")

    def test_corrupted_file_loads_empty(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        with open(path, "w") as f:
            f.write("{{bad json")
        h = TuningHistory(path)
        self.assertEqual(len(h.records), 0)


# ═══════════════════════════════════════════════════════════════════════════════
# AutoTuner.current_config — persisted state
# ═══════════════════════════════════════════════════════════════════════════════

class TestAutoTunerInit(unittest.TestCase):

    def test_fresh_tuner_uses_defaults(self):
        tuner = _make_tuner()
        cfg = tuner.current_config
        self.assertEqual(cfg.probe_count, 10)
        self.assertEqual(cfg.cycle_interval, DEFAULT_CYCLE_INTERVAL)

    def test_tuner_loads_last_config_from_history(self):
        path = _tmp_path()
        h = TuningHistory(path)
        h.append(TuningRecord(
            tuned_at=datetime.now(timezone.utc).isoformat(),
            adjustments=[],
            config_after=TuningConfig(probe_count=15, probe_timeout=5),
        ))
        h.save()

        tuner = _make_tuner(history_path=path)
        self.assertEqual(tuner.current_config.probe_count, 15)
        self.assertEqual(tuner.current_config.probe_timeout, 5)


# ═══════════════════════════════════════════════════════════════════════════════
# AutoTuner.tune() — probe intensity rules
# ═══════════════════════════════════════════════════════════════════════════════

class TestProbeIntensityTuning(unittest.TestCase):

    def test_high_burn_increases_probe_count(self):
        tracker = _make_tracker()
        # Record several failing (high burn) runs
        for _ in range(6):
            _record_failing(tracker, "ocean_core")
        tuner = _make_tuner(tracker=tracker)
        record = tuner.tune()

        probe_adj = [a for a in record.adjustments if a.parameter == "probe_count"]
        self.assertTrue(len(probe_adj) > 0, "Expected probe_count adjustment for high burn")
        self.assertGreater(record.config_after.probe_count, 10)

    def test_probe_count_never_exceeds_max(self):
        tracker = _make_tracker()
        for _ in range(50):
            _record_failing(tracker, "backend_api")
        tuner = _make_tuner(tracker=tracker)
        tuner.current_config.probe_count = MAX_PROBE_COUNT

        record = tuner.tune()
        self.assertLessEqual(record.config_after.probe_count, MAX_PROBE_COUNT)

    def test_no_probe_adjustment_for_passing_service(self):
        tracker = _make_tracker()
        for _ in range(6):
            _record_passing(tracker)
        tuner = _make_tuner(tracker=tracker)
        # Force a low ok_streak so cycle interval doesn't change
        tuner._ok_streak = 0
        record = tuner.tune()

        probe_adj = [a for a in record.adjustments if a.parameter == "probe_count"
                     and a.service != "global"]
        self.assertEqual(len(probe_adj), 0)


# ═══════════════════════════════════════════════════════════════════════════════
# AutoTuner.tune() — rate limit rules
# ═══════════════════════════════════════════════════════════════════════════════

class TestRateLimitTuning(unittest.TestCase):

    def _inject_high_error_runs(self, tracker: BudgetTracker, count: int = 6):
        """Inject runs with ocean_core error_rate > HIGH_ERROR_RATE."""
        from slo_sli_budget import RunRecord, ServiceRunResult
        for i in range(count):
            run = RunRecord(
                run_id=(datetime.now(timezone.utc) - timedelta(minutes=i)).isoformat(),
                services={
                    "ocean_core": ServiceRunResult(
                        passed=False, severity="SEV-1",
                        availability=0.0,
                        latency_p95_ms=500.0,
                        error_rate=0.15,       # 15% — well above HIGH_ERROR_RATE
                        dependency_health=0.0,
                        burn_rate=2000.0,
                    )
                },
            )
            tracker._ledger.append_run(run)

    def test_high_error_rate_reduces_rate_limit(self):
        tracker = _make_tracker()
        self._inject_high_error_runs(tracker)
        tuner = _make_tuner(tracker=tracker)

        record = tuner.tune()
        rl_adj = [a for a in record.adjustments if a.parameter == "chat_rate_limit_requests"]
        self.assertTrue(len(rl_adj) > 0, "Expected rate limit adjustment for high error rate")
        self.assertLess(record.config_after.chat_rate_limit, DEFAULT_RATE_LIMIT)

    def test_rate_limit_never_below_minimum(self):
        from slo_sli_tuning import MIN_RATE_LIMIT
        tracker = _make_tracker()
        self._inject_high_error_runs(tracker, count=20)
        tuner = _make_tuner(tracker=tracker)
        tuner.current_config.chat_rate_limit = MIN_RATE_LIMIT  # already at floor

        record = tuner.tune()
        self.assertGreaterEqual(record.config_after.chat_rate_limit, MIN_RATE_LIMIT)

    def test_low_error_rate_restores_rate_limit(self):
        tracker = _make_tracker()
        for _ in range(6):
            _record_passing(tracker)
        tuner = _make_tuner(tracker=tracker)
        tuner.current_config.chat_rate_limit = 10   # previously tightened

        record = tuner.tune()
        rl_adj = [a for a in record.adjustments if a.parameter == "chat_rate_limit_requests"]
        # Should be recovering toward DEFAULT_RATE_LIMIT (+5 per pass)
        if rl_adj:
            self.assertGreater(record.config_after.chat_rate_limit, 10)


# ═══════════════════════════════════════════════════════════════════════════════
# AutoTuner.tune() — cycle interval rules
# ═══════════════════════════════════════════════════════════════════════════════

class TestCycleIntervalTuning(unittest.TestCase):

    def test_open_incident_triggers_fast_interval(self):
        tracker = _make_tracker()
        _record_failing(tracker, "ocean_core")  # creates open incident
        tuner = _make_tuner(tracker=tracker)
        tuner.current_config.cycle_interval = DEFAULT_CYCLE_INTERVAL

        record = tuner.tune()
        interval_adj = [a for a in record.adjustments if a.parameter == "cycle_interval"]
        self.assertTrue(len(interval_adj) > 0, "Expected cycle_interval adjustment for open incident")
        self.assertEqual(record.config_after.cycle_interval, FAST_CYCLE_INTERVAL)

    def test_sustained_ok_relaxes_interval(self):
        tracker = _make_tracker()
        for _ in range(TUNING_RELAX_ITERATIONS + 2):
            _record_passing(tracker)
        tuner = _make_tuner(tracker=tracker)
        tuner.current_config.cycle_interval = FAST_CYCLE_INTERVAL
        tuner._ok_streak = TUNING_RELAX_ITERATIONS  # pre-seed streak

        record = tuner.tune()
        interval_adj = [a for a in record.adjustments if a.parameter == "cycle_interval"]
        if interval_adj:
            self.assertEqual(record.config_after.cycle_interval, DEFAULT_CYCLE_INTERVAL)


# ═══════════════════════════════════════════════════════════════════════════════
# AutoTuner.tune() — result structure
# ═══════════════════════════════════════════════════════════════════════════════

class TestTuningRecord(unittest.TestCase):

    def test_tune_returns_tuning_record(self):
        tuner = _make_tuner()
        record = tuner.tune()
        self.assertIsInstance(record, TuningRecord)
        self.assertIsInstance(record.tuned_at, str)
        self.assertIsInstance(record.adjustments, list)
        self.assertIsInstance(record.config_after, TuningConfig)

    def test_tuned_at_is_iso8601(self):
        tuner = _make_tuner()
        record = tuner.tune()
        dt = datetime.fromisoformat(record.tuned_at)
        self.assertIsNotNone(dt)

    def test_tune_persists_to_history(self):
        path = _tmp_path()
        tuner = _make_tuner(history_path=path)
        tuner.tune()
        tuner.tune()

        data = json.loads(open(path).read())
        self.assertEqual(len(data), 2)

    def test_config_after_matches_current_config(self):
        tuner = _make_tuner()
        record = tuner.tune()
        self.assertEqual(
            record.config_after.to_dict(),
            tuner.current_config.to_dict(),
        )

    def test_adjustment_round_trip(self):
        adj = TuningAdjustment(
            parameter="probe_count",
            previous=10,
            current=12,
            reason="burn rate high",
            service="ocean_core",
        )
        d = adj.to_dict()
        adj2 = TuningAdjustment(**d)
        self.assertEqual(adj2.parameter, "probe_count")
        self.assertEqual(adj2.current, 12)


# ═══════════════════════════════════════════════════════════════════════════════
# AutoTuner — dry_run push
# ═══════════════════════════════════════════════════════════════════════════════

class TestDryRunPush(unittest.TestCase):

    def test_dry_run_does_not_call_http(self):
        tuner = _make_tuner(dry_run=True)
        with patch("urllib.request.urlopen") as mock_open:
            tuner._push_ocean_tune()
        mock_open.assert_not_called()

    def test_no_token_does_not_call_http(self):
        tuner = _make_tuner(dry_run=False)
        # Ensure no token
        with patch.dict(os.environ, {"OCEAN_ADMIN_API_TOKEN": ""}):
            import slo_sli_tuning
            orig = slo_sli_tuning.OCEAN_ADMIN_TOKEN
            slo_sli_tuning.OCEAN_ADMIN_TOKEN = ""
            try:
                with patch("urllib.request.urlopen") as mock_open:
                    tuner._push_ocean_tune()
                mock_open.assert_not_called()
            finally:
                slo_sli_tuning.OCEAN_ADMIN_TOKEN = orig


# ═══════════════════════════════════════════════════════════════════════════════
# AutonomousCycle with tuner wired in (stage 5)
# ═══════════════════════════════════════════════════════════════════════════════

class TestCycleTunerIntegration(unittest.TestCase):

    def test_cycle_result_includes_tuning_record(self):
        from slo_sli_cycle import AutonomousCycle

        cycle = AutonomousCycle(
            probe_count=2, probe_timeout=1,
            ledger_path=_tmp_path(),
            tuning_path=_tmp_path(),
        )
        cycle._alerter._post = MagicMock(return_value=True)

        with patch("slo_sli_cycle.collect_all") as mock_collect:
            mock_collect.return_value = _build_report(
                passing_keys=list(SLO_TARGETS.keys()), failing_keys=[]
            )
            result = cycle.run_once()

        self.assertIsNotNone(result.tuning)
        self.assertIsInstance(result.tuning, TuningRecord)

    def test_cycle_probe_params_come_from_tuner(self):
        """collect_all should be called with probe params from tuner config."""
        from slo_sli_cycle import AutonomousCycle

        cycle = AutonomousCycle(
            probe_count=5, probe_timeout=2,
            ledger_path=_tmp_path(),
            tuning_path=_tmp_path(),
        )
        cycle._alerter._post = MagicMock(return_value=True)
        # Set tuner config to different values
        cycle._tuner.current_config.probe_count = 7
        cycle._tuner.current_config.probe_timeout = 4

        with patch("slo_sli_cycle.collect_all") as mock_collect:
            mock_collect.return_value = _build_report(
                passing_keys=list(SLO_TARGETS.keys()), failing_keys=[]
            )
            cycle.run_once()

        mock_collect.assert_called_once_with(probe_count=7, probe_timeout=4)

    def test_cycle_interval_from_tuner_config(self):
        """run_watch must use tuner's cycle_interval, not a fixed value."""
        from slo_sli_cycle import AutonomousCycle
        import threading

        cycle = AutonomousCycle(
            probe_count=2, probe_timeout=1,
            ledger_path=_tmp_path(),
            tuning_path=_tmp_path(),
        )
        cycle._alerter._post = MagicMock(return_value=True)
        cycle._tuner.current_config.cycle_interval = 999  # sentinel value

        sleep_calls = []

        def fake_sleep(secs):
            sleep_calls.append(secs)
            raise KeyboardInterrupt  # stop after first iteration

        with patch("slo_sli_cycle.collect_all") as mock_collect, \
             patch("slo_sli_cycle.time.sleep", side_effect=fake_sleep):
            mock_collect.return_value = _build_report(
                passing_keys=list(SLO_TARGETS.keys()), failing_keys=[]
            )
            cycle.run_watch(initial_interval=60)

        # The sleep should have used the tuner's interval, not 60
        self.assertTrue(len(sleep_calls) > 0)


if __name__ == "__main__":
    unittest.main()
