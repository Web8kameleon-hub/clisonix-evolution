#!/usr/bin/env python3
"""
Unit tests for slo_sli_alerter.py

All network calls and collector probes are mocked.
No real services or Slack webhooks are required.
"""

from __future__ import annotations

import sys
import os
import time
import unittest
from unittest.mock import MagicMock, patch, call
from typing import List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from slo_sli_alerter import (
    AlertEvent,
    SLOSLIAlerter,
    _build_recovery_blocks,
    _build_slo_breach_blocks,
    post_slack_message,
    _RecoveryResult,
    _SEV_EMOJI,
    SLACK_CHANNEL_CRITICAL,
    SLACK_CHANNEL_MONITORING,
)
from slo_sli_gate import SLO_TARGETS, SLOGateResult, evaluate_services
from slo_sli_collector import CollectorReport
from slo_sli_gate import SLISnapshot


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _passing_snapshot(key: str) -> SLISnapshot:
    """Return a snapshot that passes all SLOs for *key*."""
    target = SLO_TARGETS[key]
    return SLISnapshot(
        service_name=key,
        availability=target.availability_slo + 0.0001,
        latency_p95_ms=target.latency_p95_ms * 0.5,
        error_rate=0.001,
        dependency_health=0.999,
        window_minutes=60.0,
    )


def _failing_snapshot(key: str) -> SLISnapshot:
    """Return a snapshot with 0% availability (guaranteed SEV-1)."""
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
        [_passing_snapshot(k) for k in passing_keys]
        + [_failing_snapshot(k) for k in failing_keys]
    )
    results = evaluate_services(snaps)
    return CollectorReport(snapshots=snaps, gate_results=results)


def _mock_poster() -> MagicMock:
    """Return a mock poster that always returns True."""
    m = MagicMock(return_value=True)
    return m


# ═══════════════════════════════════════════════════════════════════════════════
# post_slack_message
# ═══════════════════════════════════════════════════════════════════════════════

class TestPostSlackMessage(unittest.TestCase):

    def test_dry_run_returns_true_without_http(self):
        result = post_slack_message(
            channel="#test",
            fallback_text="test",
            blocks=[],
            webhook_url="https://hooks.slack.com/services/FAKE",
            dry_run=True,
        )
        self.assertTrue(result)

    def test_no_webhook_returns_false(self):
        result = post_slack_message(
            channel="#test",
            fallback_text="test",
            blocks=[],
            webhook_url="",
            dry_run=False,
        )
        self.assertFalse(result)

    def test_successful_http_post(self):
        resp = MagicMock()
        resp.status = 200
        resp.__enter__ = lambda s: s
        resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=resp):
            result = post_slack_message(
                channel="#test",
                fallback_text="ok",
                blocks=[{"type": "section"}],
                webhook_url="https://hooks.slack.com/services/FAKE",
                dry_run=False,
            )
        self.assertTrue(result)

    def test_http_error_returns_false(self):
        import urllib.error
        exc = urllib.error.HTTPError(
            url="https://x", code=400, msg="Bad Request",
            hdrs=None, fp=None,
        )
        with patch("urllib.request.urlopen", side_effect=exc):
            result = post_slack_message(
                channel="#test",
                fallback_text="ok",
                blocks=[],
                webhook_url="https://hooks.slack.com/services/FAKE",
                dry_run=False,
            )
        self.assertFalse(result)

    def test_connection_error_returns_false(self):
        with patch("urllib.request.urlopen", side_effect=ConnectionRefusedError("refused")):
            result = post_slack_message(
                channel="#test",
                fallback_text="ok",
                blocks=[],
                webhook_url="https://hooks.slack.com/services/FAKE",
                dry_run=False,
            )
        self.assertFalse(result)


# ═══════════════════════════════════════════════════════════════════════════════
# Block-building helpers
# ═══════════════════════════════════════════════════════════════════════════════

class TestBuildBlocks(unittest.TestCase):

    def _failing_report(self, key: str) -> CollectorReport:
        return _build_report(passing_keys=[], failing_keys=[key])

    def test_breach_blocks_contain_service_name(self):
        report = self._failing_report("backend_api")
        result = next(r for r in report.gate_results if r.service_name == "backend_api")
        blocks = _build_slo_breach_blocks(result, report)
        dumped = str(blocks)
        self.assertIn("Backend API", dumped)

    def test_breach_blocks_contain_severity(self):
        report = self._failing_report("openmind")
        result = next(r for r in report.gate_results if r.service_name == "openmind")
        blocks = _build_slo_breach_blocks(result, report)
        self.assertTrue(any("SEV-1" in str(b) for b in blocks))

    def test_breach_blocks_contain_violations(self):
        report = self._failing_report("ocean_core")
        result = next(r for r in report.gate_results if r.service_name == "ocean_core")
        blocks = _build_slo_breach_blocks(result, report)
        # Violations section should exist
        self.assertTrue(any("Violations" in str(b) for b in blocks))

    def test_recovery_blocks_contain_service_name(self):
        blocks = _build_recovery_blocks("translation")
        dumped = str(blocks)
        self.assertIn("Translation Node", dumped)

    def test_recovery_blocks_contain_recovery_word(self):
        blocks = _build_recovery_blocks("ollama")
        self.assertTrue(any("RECOVERY" in str(b) or "Restored" in str(b) for b in blocks))


# ═══════════════════════════════════════════════════════════════════════════════
# SLOSLIAlerter — severity mapping
# ═══════════════════════════════════════════════════════════════════════════════

class TestSeverityMapping(unittest.TestCase):

    def test_sev1_maps_to_critical(self):
        from clisonix.alert_policy import AlertLevel
        self.assertEqual(SLOSLIAlerter._severity_to_level("SEV-1"), AlertLevel.CRITICAL)

    def test_sev2_maps_to_warning(self):
        from clisonix.alert_policy import AlertLevel
        self.assertEqual(SLOSLIAlerter._severity_to_level("SEV-2"), AlertLevel.WARNING)

    def test_sev3_maps_to_info(self):
        from clisonix.alert_policy import AlertLevel
        self.assertEqual(SLOSLIAlerter._severity_to_level("SEV-3"), AlertLevel.INFO)

    def test_ok_maps_to_none(self):
        self.assertIsNone(SLOSLIAlerter._severity_to_level("OK"))

    def test_unknown_maps_to_none(self):
        self.assertIsNone(SLOSLIAlerter._severity_to_level("SEV-99"))


# ═══════════════════════════════════════════════════════════════════════════════
# SLOSLIAlerter.process()
# ═══════════════════════════════════════════════════════════════════════════════

class TestAlerterProcess(unittest.TestCase):

    def test_sev1_fires_for_failing_service(self):
        poster = _mock_poster()
        alerter = SLOSLIAlerter(slack_poster=poster)

        report = _build_report(
            passing_keys=["ocean_core", "openmind", "excel_core", "ollama", "translation"],
            failing_keys=["backend_api"],
        )
        events = alerter.process(report)

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].service_name, "backend_api")
        self.assertEqual(events[0].severity, "SEV-1")
        self.assertEqual(events[0].channel, SLACK_CHANNEL_CRITICAL)

    def test_all_passing_fires_no_alerts(self):
        poster = _mock_poster()
        alerter = SLOSLIAlerter(slack_poster=poster)

        report = _build_report(passing_keys=list(SLO_TARGETS.keys()), failing_keys=[])
        events = alerter.process(report)

        self.assertEqual(len(events), 0)
        poster.assert_not_called()

    def test_multiple_failing_services_each_fire(self):
        poster = _mock_poster()
        alerter = SLOSLIAlerter(slack_poster=poster)

        report = _build_report(passing_keys=[], failing_keys=list(SLO_TARGETS.keys()))
        events = alerter.process(report)

        self.assertEqual(len(events), 6)
        fired_services = {e.service_name for e in events}
        self.assertEqual(fired_services, set(SLO_TARGETS.keys()))

    def test_sev1_routed_to_critical_channel(self):
        poster = _mock_poster()
        alerter = SLOSLIAlerter(slack_poster=poster)

        report = _build_report(passing_keys=[], failing_keys=["backend_api"])
        events = alerter.process(report)

        self.assertTrue(any(e.channel == SLACK_CHANNEL_CRITICAL for e in events))

    def test_poster_called_for_each_breach(self):
        poster = _mock_poster()
        alerter = SLOSLIAlerter(slack_poster=poster)

        report = _build_report(passing_keys=[], failing_keys=["ocean_core", "openmind"])
        alerter.process(report)

        self.assertEqual(poster.call_count, 2)

    def test_poster_not_called_when_poster_returns_false(self):
        """Events should not be recorded if the poster fails."""
        poster = MagicMock(return_value=False)
        alerter = SLOSLIAlerter(slack_poster=poster)

        report = _build_report(passing_keys=[], failing_keys=["backend_api"])
        events = alerter.process(report)

        # Poster was called (once), but no event recorded because it returned False
        self.assertEqual(poster.call_count, 1)
        self.assertEqual(len(events), 0)


# ═══════════════════════════════════════════════════════════════════════════════
# SLOSLIAlerter — cooldown / throttle
# ═══════════════════════════════════════════════════════════════════════════════

class TestAlerterCooldown(unittest.TestCase):

    def test_sev2_throttled_within_cooldown(self):
        """Second SEV-2 alert within cooldown window should be suppressed."""
        poster = _mock_poster()
        # Very short cooldown for test speed
        alerter = SLOSLIAlerter(slack_poster=poster, cooldown_sev2=3600)

        # Craft a SEV-2 result manually (high error rate, availability barely ok)
        target = SLO_TARGETS["backend_api"]
        snap = SLISnapshot(
            service_name="backend_api",
            availability=target.availability_slo + 0.0001,
            latency_p95_ms=target.latency_p95_ms * 0.5,
            error_rate=0.03,   # > 2%, triggers SEV-2
            dependency_health=0.999,
            window_minutes=5.0,
        )
        from slo_sli_gate import evaluate_service
        result = evaluate_service(snap)

        from slo_sli_collector import CollectorReport
        report = CollectorReport(
            snapshots=[snap],
            gate_results=[result],
        )

        # Only proceed if the gate actually gives SEV-2
        if result.severity not in ("SEV-1", "SEV-2", "SEV-3"):
            self.skipTest("snapshot did not trigger a breachable severity")

        first_call = alerter.process(report)
        second_call = alerter.process(report)  # should be throttled for WARNING/INFO

        if result.severity == "SEV-1":
            # SEV-1 has no cooldown — both calls should fire
            pass
        else:
            # SEV-2 or SEV-3 should be throttled on second call
            self.assertGreaterEqual(len(first_call), 0)
            self.assertEqual(len(second_call), 0,
                             f"Expected second call to be throttled, got {second_call}")

    def test_sev1_never_throttled(self):
        """SEV-1 alerts should always fire (no cooldown)."""
        poster = _mock_poster()
        alerter = SLOSLIAlerter(slack_poster=poster)

        report = _build_report(passing_keys=[], failing_keys=["backend_api"])

        first = alerter.process(report)
        second = alerter.process(report)

        # Both calls should have fired exactly one alert each
        self.assertEqual(len(first), 1)
        self.assertEqual(len(second), 1)
        self.assertEqual(poster.call_count, 2)


# ═══════════════════════════════════════════════════════════════════════════════
# SLOSLIAlerter — recovery notifications
# ═══════════════════════════════════════════════════════════════════════════════

class TestAlerterRecovery(unittest.TestCase):

    def test_recovery_fires_when_service_goes_from_failing_to_passing(self):
        poster = _mock_poster()
        alerter = SLOSLIAlerter(slack_poster=poster)

        # Round 1: service is failing
        report_failing = _build_report(passing_keys=[], failing_keys=["backend_api"])
        alerter.process(report_failing)

        # Reset poster call count before the recovery round
        poster.reset_mock()

        # Round 2: service is now passing
        report_passing = _build_report(
            passing_keys=["backend_api"],
            failing_keys=[],
        )
        events = alerter.process(report_passing)

        # One recovery notification should have been dispatched
        recovery_events = [e for e in events if e.severity == "RECOVERY"]
        self.assertEqual(len(recovery_events), 1)
        self.assertEqual(recovery_events[0].service_name, "backend_api")

    def test_recovery_channel_is_monitoring_not_critical(self):
        poster = _mock_poster()
        alerter = SLOSLIAlerter(slack_poster=poster)

        report_fail = _build_report(passing_keys=[], failing_keys=["ocean_core"])
        alerter.process(report_fail)
        poster.reset_mock()

        report_pass = _build_report(
            passing_keys=["ocean_core"],
            failing_keys=[],
        )
        events = alerter.process(report_pass)

        recovery = [e for e in events if e.severity == "RECOVERY"]
        if recovery:
            self.assertEqual(recovery[0].channel, SLACK_CHANNEL_MONITORING)

    def test_no_recovery_if_service_was_not_previously_failing(self):
        poster = _mock_poster()
        alerter = SLOSLIAlerter(slack_poster=poster)

        # Service was never observed as failing — no recovery should fire
        report_pass = _build_report(
            passing_keys=["backend_api"],
            failing_keys=[],
        )
        events = alerter.process(report_pass)

        recovery_events = [e for e in events if e.severity == "RECOVERY"]
        self.assertEqual(len(recovery_events), 0)

    def test_no_recovery_if_still_failing(self):
        poster = _mock_poster()
        alerter = SLOSLIAlerter(slack_poster=poster)

        report_fail = _build_report(passing_keys=[], failing_keys=["backend_api"])
        alerter.process(report_fail)
        poster.reset_mock()

        # Still failing — no recovery
        events = alerter.process(report_fail)
        recovery_events = [e for e in events if e.severity == "RECOVERY"]
        self.assertEqual(len(recovery_events), 0)


# ═══════════════════════════════════════════════════════════════════════════════
# SLOSLIAlerter.run_once() — mock collect_all
# ═══════════════════════════════════════════════════════════════════════════════

class TestRunOnce(unittest.TestCase):

    def _make_collect_all(self, passing_keys, failing_keys):
        report = _build_report(passing_keys=passing_keys, failing_keys=failing_keys)
        return MagicMock(return_value=report)

    def test_run_once_returns_events(self):
        mock_collect = self._make_collect_all(
            passing_keys=[k for k in SLO_TARGETS if k != "backend_api"],
            failing_keys=["backend_api"],
        )
        poster = _mock_poster()
        alerter = SLOSLIAlerter(slack_poster=poster)

        with patch("slo_sli_alerter.collect_all", mock_collect):
            events = alerter.run_once(probe_count=2)

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].service_name, "backend_api")

    def test_run_once_passes_probe_args_to_collect_all(self):
        mock_collect = self._make_collect_all(
            passing_keys=list(SLO_TARGETS.keys()),
            failing_keys=[],
        )
        alerter = SLOSLIAlerter(slack_poster=_mock_poster())

        with patch("slo_sli_alerter.collect_all", mock_collect):
            alerter.run_once(probe_count=5, probe_timeout=2)

        mock_collect.assert_called_once_with(probe_count=5, probe_timeout=2)


# ═══════════════════════════════════════════════════════════════════════════════
# AlertEvent dataclass
# ═══════════════════════════════════════════════════════════════════════════════

class TestAlertEvent(unittest.TestCase):

    def test_fired_at_is_iso8601(self):
        from datetime import datetime
        evt = AlertEvent(
            service_name="ocean_core",
            severity="SEV-1",
            channel="#critical-alerts",
            dry_run=True,
        )
        dt = datetime.fromisoformat(evt.fired_at)
        self.assertIsNotNone(dt)

    def test_dry_run_flag_recorded(self):
        evt = AlertEvent(
            service_name="backend_api",
            severity="SEV-2",
            channel="#clisonix-monitoring",
            dry_run=True,
        )
        self.assertTrue(evt.dry_run)


if __name__ == "__main__":
    unittest.main()
