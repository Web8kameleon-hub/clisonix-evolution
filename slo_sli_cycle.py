#!/usr/bin/env python3
"""
CLISONIX SLO/SLI AUTONOMOUS CYCLE
====================================

Closes the loop — no human in the middle.

Every iteration:
    1. collect_all()              — probe all 6 services
    2. SLOSLIAlerter.process()    — fire Slack alerts for breaches
    3. BudgetTracker.record()     — persist run, open/close incidents, compute MTTR
    4. AutoRemediator.remediate() — execute corrective actions (restart, flush, switch model …)
    5. AutoTuner.tune()           — adjust probe_count/timeout/interval/rate-limits for next run

The cycle repeats at an interval that is itself auto-tuned:
    • Open incident  → 30s (FAST_CYCLE_INTERVAL)
    • All ok x10     → 60s (DEFAULT_CYCLE_INTERVAL)

A single iteration can also be run with --once for CI/CD pipelines.

Environment variables:
    CYCLE_INTERVAL      Initial seconds between iterations (default: 60)
    PROBE_COUNT         Initial HTTP probes per service (default: 10)
    PROBE_TIMEOUT       Initial per-probe timeout seconds (default: 3)
    SLACK_WEBHOOK_URL   Slack incoming-webhook URL
    SLACK_DRY_RUN       "true" → Slack dry-run
    REMEDIATION_DRY_RUN "true" → remediation dry-run
    BUDGET_LEDGER_PATH  Path to JSON ledger (default: slo_budget_ledger.json)
    TUNING_HISTORY_PATH Path to tuning history (default: slo_tuning_history.json)

Usage:
    # One shot — run once and exit (exit code 1 on SEV-1)
    python slo_sli_cycle.py --once

    # Continuous autonomous loop (interval self-adjusts)
    python slo_sli_cycle.py

    # Full dry-run (no Slack, no HTTP remediation/tuning)
    SLACK_DRY_RUN=true REMEDIATION_DRY_RUN=true python slo_sli_cycle.py

Author: Clisonix Engineering
"""

from __future__ import annotations

import logging
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from slo_sli_alerter import SLOSLIAlerter, AlertEvent
from slo_sli_budget import BudgetTracker
from slo_sli_collector import CollectorReport, collect_all, PROBE_COUNT, PROBE_TIMEOUT
from slo_sli_remediation import AutoRemediator, RemediationResult
from slo_sli_tuning import AutoTuner, TuningRecord

logger = logging.getLogger("clisonix.slo_sli_cycle")

CYCLE_INTERVAL: int = int(os.getenv("CYCLE_INTERVAL", "60"))


# ═══════════════════════════════════════════════════════════════════════════════
# CYCLE RESULT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CycleResult:
    """
    Summary of one autonomous cycle iteration.

    Attributes:
        iteration:    Counter starting at 1.
        ran_at:       ISO-8601 UTC timestamp of the start.
        duration_ms:  Wall-clock time for the full iteration.
        report:       The CollectorReport produced by collect_all().
        alerts:       Slack alerts fired by SLOSLIAlerter.
        remediations: Actions executed by AutoRemediator.
        tuning:       TuningRecord from AutoTuner (None if tuning was skipped).
        errors:       Any exceptions caught during the iteration.
    """
    iteration: int
    ran_at: str
    duration_ms: float
    report: CollectorReport
    alerts: List[AlertEvent]
    remediations: List[RemediationResult]
    tuning: Optional[TuningRecord] = None
    errors: List[str] = field(default_factory=list)

    @property
    def healthy_services(self) -> int:
        return sum(1 for r in self.report.gate_results if r.passed)

    @property
    def breaching_services(self) -> int:
        return sum(1 for r in self.report.gate_results if not r.passed)

    @property
    def ok(self) -> bool:
        return not self.errors and self.breaching_services == 0

    def summary_line(self) -> str:
        tuning_adj = len(self.tuning.adjustments) if self.tuning else 0
        status = "✅ ALL OK" if self.ok else f"⚠️  {self.breaching_services} BREACH(ES)"
        return (
            f"[#{self.iteration}] {self.ran_at[:19]} | {status} | "
            f"alerts={len(self.alerts)} remediations={len(self.remediations)} "
            f"tuning={tuning_adj} duration={self.duration_ms:.0f}ms"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# AUTONOMOUS CYCLE RUNNER
# ═══════════════════════════════════════════════════════════════════════════════

class AutonomousCycle:
    """
    Orchestrates the full collect → alert → budget → remediate → tune pipeline.

    Args:
        probe_count:    Initial HTTP probes per service per iteration.
        probe_timeout:  Initial per-probe timeout in seconds.
        ledger_path:    Path to the budget ledger JSON file.
        tuning_path:    Path to the tuning history JSON file.
    """

    def __init__(
        self,
        probe_count: int = PROBE_COUNT,
        probe_timeout: int = PROBE_TIMEOUT,
        ledger_path: str | None = None,
        tuning_path: str | None = None,
    ):
        self._alerter = SLOSLIAlerter()
        self._budget = BudgetTracker(ledger_path=ledger_path)
        self._remediator = AutoRemediator()
        self._tuner = AutoTuner(
            tracker=self._budget,
            history_path=tuning_path,
        )
        self._iteration = 0

        # Seed tuning config from persisted state (or CLI overrides)
        if probe_count != PROBE_COUNT:
            self._tuner.current_config.probe_count = probe_count
        if probe_timeout != PROBE_TIMEOUT:
            self._tuner.current_config.probe_timeout = probe_timeout

    # ── public API ────────────────────────────────────────────────────────────

    def run_once(self) -> CycleResult:
        """
        Execute one full cycle iteration: collect → alert → budget → remediate → tune.

        Probe parameters come from the tuner's live config so each run
        automatically uses the parameters computed by the previous iteration.

        Returns:
            CycleResult with all pipeline outputs.
        """
        self._iteration += 1
        ran_at = datetime.now(timezone.utc).isoformat()
        t0 = time.monotonic()
        errors: List[str] = []
        report: CollectorReport
        alerts: List[AlertEvent] = []
        remediations: List[RemediationResult] = []
        tuning_record: Optional[TuningRecord] = None

        # Read probe params from tuner (self-adjusting between runs)
        cfg = self._tuner.current_config

        # 1 ── COLLECT ─────────────────────────────────────────────────────────
        try:
            report = collect_all(
                probe_count=cfg.probe_count,
                probe_timeout=cfg.probe_timeout,
            )
        except Exception as exc:
            errors.append(f"collect: {exc}")
            logger.error("collect_all failed: %s", exc)
            report = CollectorReport(snapshots=[], gate_results=[])

        # 2 ── ALERT ───────────────────────────────────────────────────────────
        try:
            alerts = self._alerter.process(report)
        except Exception as exc:
            errors.append(f"alert: {exc}")
            logger.error("alerter.process failed: %s", exc)

        # 3 ── BUDGET ──────────────────────────────────────────────────────────
        try:
            self._budget.record(report)
        except Exception as exc:
            errors.append(f"budget: {exc}")
            logger.error("budget.record failed: %s", exc)

        # 4 ── REMEDIATE ───────────────────────────────────────────────────────
        try:
            remediations = self._remediator.remediate(report)
        except Exception as exc:
            errors.append(f"remediate: {exc}")
            logger.error("remediator.remediate failed: %s", exc)

        # 5 ── TUNE (feedback loop — adjusts config for next iteration) ─────────
        try:
            tuning_record = self._tuner.tune()
        except Exception as exc:
            errors.append(f"tune: {exc}")
            logger.error("tuner.tune failed: %s", exc)

        duration_ms = (time.monotonic() - t0) * 1000

        result = CycleResult(
            iteration=self._iteration,
            ran_at=ran_at,
            duration_ms=round(duration_ms, 2),
            report=report,
            alerts=alerts,
            remediations=remediations,
            tuning=tuning_record,
            errors=errors,
        )
        logger.info(result.summary_line())
        return result

    def run_watch(self, initial_interval: int = CYCLE_INTERVAL) -> None:
        """
        Run the autonomous cycle indefinitely.

        The sleep interval between iterations comes from the tuner's live
        config (self-adjusting: 30s during incidents, 60s when stable).

        Args:
            initial_interval: Fallback interval before the first tuning pass.
        """
        logger.info(
            "🔄 Autonomous cycle starting — initial_interval=%ds "
            "probe_count=%d probe_timeout=%ds",
            initial_interval,
            self._tuner.current_config.probe_count,
            self._tuner.current_config.probe_timeout,
        )
        try:
            while True:
                result = self.run_once()
                self._print_iteration_summary(result)
                # Use the interval from tuner (may have changed this iteration)
                interval = self._tuner.current_config.cycle_interval
                logger.debug("Next iteration in %ds", interval)
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("Autonomous cycle stopped")

    # ── helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _print_iteration_summary(result: CycleResult) -> None:
        if result.breaching_services == 0 and not result.errors and (
            not result.tuning or not result.tuning.adjustments
        ):
            return  # quiet — nothing to report
        print(f"\n{result.summary_line()}")
        for gate in result.report.gate_results:
            if not gate.passed:
                print(f"  ❌ {gate.service_name:<20} {gate.severity} burn={gate.burn_rate:.1f}×")
        if result.alerts:
            for evt in result.alerts:
                print(f"  📣 alert  {evt.service_name:<20} → {evt.channel}")
        if result.remediations:
            for rem in result.remediations:
                icon = "✅" if rem.success else "❌"
                print(f"  {icon} action {rem.action.value:<26} on {rem.service:<20}")
        if result.tuning and result.tuning.adjustments:
            for adj in result.tuning.adjustments:
                print(f"  ⚙️  tune  [{adj.service}] {adj.parameter}: {adj.previous} → {adj.current}")
        if result.errors:
            for err in result.errors:
                print(f"  ⚠️  error: {err}")


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    parser = argparse.ArgumentParser(
        description=(
            "Clisonix Autonomous SLO/SLI Cycle — "
            "collect → alert → budget → remediate → tune"
        )
    )
    parser.add_argument(
        "--once", action="store_true",
        help="Run a single iteration and exit (exit code 1 if any SEV-1)",
    )
    parser.add_argument("--probe-count", type=int, default=PROBE_COUNT)
    parser.add_argument("--probe-timeout", type=int, default=PROBE_TIMEOUT)
    parser.add_argument(
        "--interval", type=int, default=CYCLE_INTERVAL,
        help=f"Initial seconds between iterations (default: {CYCLE_INTERVAL})",
    )
    parser.add_argument("--ledger", default=None)
    parser.add_argument("--tuning-history", default=None)
    args = parser.parse_args()

    dry_slack = os.getenv("SLACK_DRY_RUN", "false").lower() == "true"
    dry_rem   = os.getenv("REMEDIATION_DRY_RUN", "false").lower() == "true"
    logger.info(
        "Cycle mode: %s | Slack: %s | Remediation: %s",
        "once" if args.once else "watch",
        "DRY" if dry_slack else "LIVE",
        "DRY" if dry_rem else "LIVE",
    )

    cycle = AutonomousCycle(
        probe_count=args.probe_count,
        probe_timeout=args.probe_timeout,
        ledger_path=args.ledger,
        tuning_path=args.tuning_history,
    )

    if args.once:
        result = cycle.run_once()
        cycle._print_iteration_summary(result)
        sev1 = any(
            g.severity == "SEV-1" and not g.passed
            for g in result.report.gate_results
        )
        sys.exit(1 if sev1 else 0)
    else:
        cycle.run_watch(initial_interval=args.interval)

