#!/usr/bin/env python3
"""
CLISONIX SLO/SLI ALERTER
==========================

Bridges the SLO/SLI evaluation pipeline to Slack notifications.

Pipeline:
    slo_sli_collector.collect_all()
        → CollectorReport
        → SLOSLIAlerter.process(report)
            → maps SEV-1/2/3 → AlertLevel (CRITICAL/WARNING/WARNING)
            → throttled by AlertManager (clisonix/alert_policy.py)
            → POST formatted Block Kit message to Slack webhook

Channel routing (override via env vars):
    SEV-1   → SLACK_CHANNEL_CRITICAL    default: #critical-alerts
    SEV-2/3 → SLACK_CHANNEL_MONITORING  default: #clisonix-monitoring
    Recovery→ SLACK_CHANNEL_MONITORING

Cooldowns (override via env vars):
    SEV-1  : no cooldown (fast-burn — always fire)
    SEV-2  : COOLDOWN_SEV2_SEC   default: 300   (5 min)
    SEV-3  : COOLDOWN_SEV3_SEC   default: 600   (10 min)

Environment variables:
    SLACK_WEBHOOK_URL          Slack incoming-webhook URL (required for real posts)
    SLACK_DRY_RUN              "true" → print to stdout, never POST (default: false)
    SLACK_CHANNEL_CRITICAL     default: #critical-alerts
    SLACK_CHANNEL_MONITORING   default: #clisonix-monitoring
    COOLDOWN_SEV2_SEC          default: 300
    COOLDOWN_SEV3_SEC          default: 600
    ALERT_INTERVAL             seconds between watchdog loop iterations (default: 60)
    PROBE_COUNT                passed through to collect_all (default: 10)
    PROBE_TIMEOUT              passed through to collect_all (default: 3)

Usage (CLI):
    # Single check
    python slo_sli_alerter.py

    # Watch loop (every 60 s by default)
    python slo_sli_alerter.py --watch

    # Dry-run (no Slack posts)
    SLACK_DRY_RUN=true python slo_sli_alerter.py --watch

Usage (programmatic):
    from slo_sli_alerter import SLOSLIAlerter

    alerter = SLOSLIAlerter()
    fired = alerter.run_once()   # returns list of fired AlertEvent

Author: Clisonix Engineering
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set

# Internal imports
sys.path.insert(0, os.path.dirname(__file__))

from clisonix.alert_policy import (
    Alert,
    AlertCategory,
    AlertLevel,
    AlertManager,
    AlertPolicy,
)
from slo_sli_collector import (
    CollectorReport,
    collect_all,
    PROBE_COUNT,
    PROBE_TIMEOUT,
)
from slo_sli_gate import SLO_TARGETS, SLOGateResult

logger = logging.getLogger("clisonix.slo_sli_alerter")


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

SLACK_WEBHOOK_URL: str = os.getenv("SLACK_WEBHOOK_URL", "")
SLACK_DRY_RUN: bool = os.getenv("SLACK_DRY_RUN", "false").lower() == "true"
SLACK_CHANNEL_CRITICAL: str = os.getenv("SLACK_CHANNEL_CRITICAL", "#critical-alerts")
SLACK_CHANNEL_MONITORING: str = os.getenv("SLACK_CHANNEL_MONITORING", "#clisonix-monitoring")

COOLDOWN_SEV2_SEC: int = int(os.getenv("COOLDOWN_SEV2_SEC", "300"))   # 5 min
COOLDOWN_SEV3_SEC: int = int(os.getenv("COOLDOWN_SEV3_SEC", "600"))   # 10 min

ALERT_INTERVAL: int = int(os.getenv("ALERT_INTERVAL", "60"))

# Emoji decorators for Slack messages
_SEV_EMOJI: Dict[str, str] = {
    "SEV-1": "🔴",
    "SEV-2": "🟠",
    "SEV-3": "🟡",
    "OK": "✅",
}


# ═══════════════════════════════════════════════════════════════════════════════
# ALERT EVENTS (thin record of what was fired)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class AlertEvent:
    """
    Record of a single alert that was dispatched.

    Attributes:
        service_name:  Gate key (e.g. "backend_api").
        severity:      SEV-1 / SEV-2 / SEV-3 / RECOVERY.
        channel:       Slack channel the message was posted to.
        dry_run:       True if the message was only logged, not actually sent.
        fired_at:      ISO-8601 UTC timestamp.
    """
    service_name: str
    severity: str
    channel: str
    dry_run: bool
    fired_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SLACK BLOCK KIT HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _build_slo_breach_blocks(
    result: SLOGateResult,
    report: CollectorReport,
) -> List[Dict]:
    """Build Slack Block Kit blocks for an SLO breach alert."""
    emoji = _SEV_EMOJI.get(result.severity, "⚠️")
    target = SLO_TARGETS.get(result.service_name)
    display_name = target.service_name if target else result.service_name

    # Find matching snapshot for metrics
    snap = next((s for s in report.snapshots if s.service_name == result.service_name), None)

    header = f"{emoji} {result.severity} — {display_name} SLO Breach"

    fields: List[Dict] = [
        {"type": "mrkdwn", "text": f"*Service:*\n{display_name}"},
        {"type": "mrkdwn", "text": f"*Severity:*\n{result.severity}"},
        {"type": "mrkdwn", "text": f"*Burn Rate:*\n{result.burn_rate:.1f}×"},
        {"type": "mrkdwn", "text": f"*Evaluated:*\n{result.evaluated_at}"},
    ]

    if snap:
        fields += [
            {"type": "mrkdwn", "text": f"*Availability:*\n{snap.availability:.4%}"},
            {"type": "mrkdwn", "text": f"*Latency p95:*\n{snap.latency_p95_ms:.0f}ms"},
        ]

    violation_text = "\n".join(f"• {issue}" for issue in result.issues) or "—"

    blocks: List[Dict] = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": header, "emoji": True},
        },
        {"type": "section", "fields": fields},
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Violations:*\n{violation_text}"},
        },
        {"type": "divider"},
    ]
    return blocks


def _build_recovery_blocks(service_name: str) -> List[Dict]:
    """Build Slack Block Kit blocks for a service recovery notification."""
    target = SLO_TARGETS.get(service_name)
    display_name = target.service_name if target else service_name

    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"✅ RECOVERY — {display_name} SLO Restored",
                "emoji": True,
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"*{display_name}* is now back within its SLO targets.\n"
                    f"_Recovered at {datetime.now(timezone.utc).isoformat()}_"
                ),
            },
        },
        {"type": "divider"},
    ]


# ═══════════════════════════════════════════════════════════════════════════════
# SLACK HTTP SENDER
# ═══════════════════════════════════════════════════════════════════════════════

def post_slack_message(
    channel: str,
    fallback_text: str,
    blocks: List[Dict],
    webhook_url: str = SLACK_WEBHOOK_URL,
    dry_run: bool = SLACK_DRY_RUN,
    timeout: int = 5,
) -> bool:
    """
    POST a Slack Block Kit message to *webhook_url*.

    In dry-run mode the payload is printed to stdout and the function
    returns True without making any network call.

    Args:
        channel:       Slack channel hint (informational; actual channel is
                       determined by the webhook's app configuration).
        fallback_text: Plain-text fallback shown in notifications.
        blocks:        Slack Block Kit payload.
        webhook_url:   Slack incoming-webhook URL.
        dry_run:       When True, log only — do not POST.
        timeout:       HTTP request timeout in seconds.

    Returns:
        True on success, False on failure.
    """
    payload = {
        "channel": channel,
        "text": fallback_text,
        "blocks": blocks,
    }

    if dry_run:
        logger.info(
            "[DRY RUN] Slack → %s | %s\n%s",
            channel,
            fallback_text,
            json.dumps(blocks, indent=2),
        )
        return True

    if not webhook_url:
        logger.warning("SLACK_WEBHOOK_URL not set — skipping Slack post")
        return False

    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return 200 <= resp.status < 300
    except urllib.error.HTTPError as exc:
        logger.error("Slack HTTP error: %s %s", exc.code, exc.reason)
        return False
    except Exception as exc:
        logger.error("Slack post failed: %s", exc)
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# ALERTER
# ═══════════════════════════════════════════════════════════════════════════════

class SLOSLIAlerter:
    """
    Processes a CollectorReport and fires Slack alerts for SLO breaches.

    Per-service cooldowns are enforced via AlertManager:
        - SEV-1 : always fires (no cooldown)
        - SEV-2 : fires at most once per COOLDOWN_SEV2_SEC seconds
        - SEV-3 : fires at most once per COOLDOWN_SEV3_SEC seconds

    Recovery notifications fire once when a service transitions from
    failing to passing (also subject to the monitoring-channel cooldown).

    Args:
        slack_poster:  Callable with the same signature as
                       `post_slack_message`.  Defaults to the real sender.
                       Pass a mock in tests.
    """

    def __init__(
        self,
        slack_poster=None,
        cooldown_sev2: int = COOLDOWN_SEV2_SEC,
        cooldown_sev3: int = COOLDOWN_SEV3_SEC,
    ):
        self._post = slack_poster or post_slack_message

        # Build a dedicated AlertManager with SLO-specific cooldowns
        policies = {
            AlertLevel.CRITICAL: AlertPolicy(
                level=AlertLevel.CRITICAL,
                send=True,
                cooldown_sec=0,  # SEV-1: always fire
            ),
            AlertLevel.WARNING: AlertPolicy(
                level=AlertLevel.WARNING,
                send=True,
                cooldown_sec=cooldown_sev2,  # SEV-2 default: 5 min
            ),
            AlertLevel.INFO: AlertPolicy(
                level=AlertLevel.INFO,
                send=True,
                cooldown_sec=cooldown_sev3,  # SEV-3 mapped to INFO
            ),
        }
        self._manager = AlertManager(policies=policies)
        self._manager.on_send(self._dispatch)

        # Track previously-failing services for recovery detection
        self._previously_failing: Set[str] = set()

        # Staging slot used by the dispatch handler so it knows the
        # current report without an extra method parameter.
        self._current_report: Optional[CollectorReport] = None
        self._fired_events: List[AlertEvent] = []

    # ─── internal dispatch ────────────────────────────────────────────────────

    def _dispatch(self, alert: Alert) -> bool:
        """
        Called by AlertManager when an alert passes the cooldown gate.
        Formats the Slack message and posts it.
        """
        result = (alert.details or {}).get("gate_result")
        if result is None:
            return False

        severity = result.severity
        is_recovery = severity == "RECOVERY"

        if is_recovery:
            channel = SLACK_CHANNEL_MONITORING
            fallback = f"✅ RECOVERY — {result.service_name} SLO Restored"
            blocks = _build_recovery_blocks(result.service_name)
        else:
            channel = (
                SLACK_CHANNEL_CRITICAL if severity == "SEV-1"
                else SLACK_CHANNEL_MONITORING
            )
            fallback = (
                f"{_SEV_EMOJI.get(severity, '⚠️')} {severity} — "
                f"{result.service_name} SLO Breach"
            )
            if self._current_report is None:
                logger.warning("current_report is None; skipping breach blocks")
                blocks = []
            else:
                blocks = _build_slo_breach_blocks(result, self._current_report)

        ok = self._post(
            channel=channel,
            fallback_text=fallback,
            blocks=blocks,
        )
        if ok:
            self._fired_events.append(AlertEvent(
                service_name=result.service_name,
                severity=severity,
                channel=channel,
                dry_run=SLACK_DRY_RUN,
            ))
        return ok

    # ─── severity → alert level mapping ──────────────────────────────────────

    @staticmethod
    def _severity_to_level(severity: str) -> Optional[AlertLevel]:
        """
        Map SLO gate severity string to AlertLevel.

        SEV-1 → CRITICAL  (fast burn, always fire)
        SEV-2 → WARNING   (5-min cooldown)
        SEV-3 → INFO      (10-min cooldown, reusing INFO bucket)
        OK    → None      (no alert)
        """
        return {
            "SEV-1": AlertLevel.CRITICAL,
            "SEV-2": AlertLevel.WARNING,
            "SEV-3": AlertLevel.INFO,
        }.get(severity)

    # ─── public API ──────────────────────────────────────────────────────────

    def process(self, report: CollectorReport) -> List[AlertEvent]:
        """
        Evaluate *report* and fire Slack alerts for any breaches.

        Also fires recovery notifications for services that were previously
        failing and are now passing.

        Args:
            report: CollectorReport from slo_sli_collector.collect_all().

        Returns:
            List of AlertEvent for every alert that was dispatched in this
            call (after cooldown filtering).
        """
        self._current_report = report
        self._fired_events = []

        currently_failing: Set[str] = set()

        for result in report.gate_results:
            service = result.service_name

            if not result.passed:
                currently_failing.add(service)
                level = self._severity_to_level(result.severity)
                if level is None:
                    continue

                alert = Alert(
                    level=level,
                    category=AlertCategory.SERVICE_DOWN,
                    title=f"{result.severity} — {service} SLO Breach",
                    message="; ".join(result.issues) or f"SLO breach ({result.severity})",
                    service=service,
                    details={"gate_result": result},
                )
                self._manager.process(alert)

            else:
                # Recovery: was failing, now passing
                if service in self._previously_failing:
                    recovery_result = _RecoveryResult(service_name=service)
                    recovery_alert = Alert(
                        level=AlertLevel.WARNING,
                        category=AlertCategory.SERVICE_DOWN,
                        title=f"RECOVERY — {service}",
                        message=f"{service} SLO restored",
                        service=service,
                        details={"gate_result": recovery_result},
                    )
                    # Use a one-shot copy of the manager to bypass cooldown for
                    # recoveries (a recovery after a long outage should always fire)
                    _recovery_manager = AlertManager(policies={
                        AlertLevel.WARNING: AlertPolicy(
                            level=AlertLevel.WARNING,
                            send=True,
                            cooldown_sec=0,
                        ),
                    })
                    _recovery_manager.on_send(self._dispatch)
                    _recovery_manager.process(recovery_alert)

        self._previously_failing = currently_failing
        return list(self._fired_events)

    def run_once(
        self,
        probe_count: int = PROBE_COUNT,
        probe_timeout: int = PROBE_TIMEOUT,
    ) -> List[AlertEvent]:
        """
        Probe all services, evaluate SLOs, and fire alerts.

        Returns:
            List of AlertEvent for every alert dispatched.
        """
        report = collect_all(probe_count=probe_count, probe_timeout=probe_timeout)
        return self.process(report)

    def run_watch(
        self,
        interval: int = ALERT_INTERVAL,
        probe_count: int = PROBE_COUNT,
        probe_timeout: int = PROBE_TIMEOUT,
    ) -> None:
        """
        Continuous watchdog loop.  Blocks until interrupted with Ctrl-C.

        Args:
            interval:      Seconds between evaluation rounds.
            probe_count:   HTTP probes per service per round.
            probe_timeout: Per-probe timeout in seconds.
        """
        logger.info(
            "Starting SLO/SLI watch loop — interval=%ds probe_count=%d",
            interval,
            probe_count,
        )
        try:
            while True:
                try:
                    fired = self.run_once(
                        probe_count=probe_count,
                        probe_timeout=probe_timeout,
                    )
                    if fired:
                        logger.info(
                            "Alerts fired: %d (%s)",
                            len(fired),
                            ", ".join(e.severity for e in fired),
                        )
                    else:
                        logger.debug("All SLOs passing — no alerts fired")
                except Exception as exc:
                    logger.error("run_once error: %s", exc)
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("Watch loop stopped")


# ═══════════════════════════════════════════════════════════════════════════════
# INTERNAL — recovery pseudo-result
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class _RecoveryResult:
    """Minimal stand-in for SLOGateResult used by recovery alerts."""
    service_name: str
    severity: str = "RECOVERY"
    passed: bool = True
    burn_rate: float = 0.0
    issues: List[str] = field(default_factory=list)
    evaluated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CLI ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Clisonix SLO/SLI Alerter — probe services and fire Slack alerts",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Run in continuous watch loop (interval: ALERT_INTERVAL env var)",
    )
    parser.add_argument(
        "--probe-count",
        type=int,
        default=PROBE_COUNT,
        help=f"HTTP probes per service (default: {PROBE_COUNT})",
    )
    parser.add_argument(
        "--probe-timeout",
        type=int,
        default=PROBE_TIMEOUT,
        help=f"Per-probe timeout seconds (default: {PROBE_TIMEOUT})",
    )
    args = parser.parse_args()

    mode = "DRY RUN" if SLACK_DRY_RUN else ("webhook configured" if SLACK_WEBHOOK_URL else "NO WEBHOOK")
    logger.info("SLO/SLI Alerter starting — mode: %s", mode)

    alerter = SLOSLIAlerter()

    if args.watch:
        alerter.run_watch(
            interval=ALERT_INTERVAL,
            probe_count=args.probe_count,
            probe_timeout=args.probe_timeout,
        )
    else:
        fired = alerter.run_once(
            probe_count=args.probe_count,
            probe_timeout=args.probe_timeout,
        )
        if fired:
            print(f"\nAlerts fired ({len(fired)}):")
            for evt in fired:
                print(f"  {evt.severity:<8} {evt.service_name:<20} → {evt.channel}")
        else:
            print("\nNo alerts fired (all SLOs passing or throttled by cooldown)")
