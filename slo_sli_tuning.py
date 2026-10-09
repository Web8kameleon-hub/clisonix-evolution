#!/usr/bin/env python3
"""
CLISONIX SLO/SLI AUTO-TUNING LAYER
=====================================

Reads the budget ledger produced by BudgetTracker and computes tuning
adjustments for the next cycle iteration. These adjustments are then
applied via real HTTP calls to service admin endpoints — no manual config
changes, no restarts.

Pipeline position (stage 5 — runs after remediation):
    collect_all()
      → SLOSLIAlerter.process()     [alert]
      → BudgetTracker.record()      [budget + MTTR]
      → AutoRemediator.remediate()  [act]
      → AutoTuner.tune()            [THIS — optimise for next run]

Tuning rules (deterministic, explainable — no ML):

  PROBE INTENSITY
  ───────────────
  avg_burn_rate > HIGH_BURN (14×)   → increase probe_count by +2 (max: MAX_PROBE_COUNT)
  avg_burn_rate > MED_BURN (5×)     → increase probe_count by +1
  sustained_ok for N iterations     → decrease probe_count by -1 (min: MIN_PROBE_COUNT)

  PROBE TIMEOUT
  ─────────────
  latency_p95 > 80% of SLO limit   → decrease probe_timeout by -1s (min: MIN_TIMEOUT)
  latency_p95 < 20% of SLO limit   → increase probe_timeout by +1s (max: MAX_TIMEOUT)

  CYCLE INTERVAL
  ──────────────
  any SEV-1 open incident           → decrease cycle_interval to FAST_INTERVAL (30s)
  all services ok for RELAX_ITERS   → reset cycle_interval to DEFAULT_INTERVAL (60s)

  OCEAN-CORE RATE LIMIT (pushed to POST /admin/tune)
  ──────────────────────────────────────────────────
  ocean_core error_rate > 5%        → halve chat_rate_limit_requests (min: 5)
  ocean_core error_rate < 1% AND    → restore chat_rate_limit_requests toward default
    no open incidents

  OCEAN-CORE STREAM TIMEOUT (pushed to POST /admin/tune)
  ───────────────────────────────────────────────────────
  ocean_core latency_p95 > 80%      → increase ollama_stream_timeout_base_s by +10s
  ocean_core latency_p95 < 20%      → decrease ollama_stream_timeout_base_s by -10s

Every adjustment is logged and recorded in a ``TuningHistory`` persisted
alongside the budget ledger.

Environment variables:
    TUNING_HISTORY_PATH         path to JSON history (default: slo_tuning_history.json)
    TUNING_WINDOW_RUNS          number of recent runs used for decisions (default: 5)
    TUNING_RELAX_ITERATIONS     consecutive ok runs before relaxing (default: 10)
    MIN_PROBE_COUNT             floor for probe_count (default: 3)
    MAX_PROBE_COUNT             ceiling for probe_count (default: 20)
    MIN_PROBE_TIMEOUT           floor for probe_timeout seconds (default: 1)
    MAX_PROBE_TIMEOUT           ceiling for probe_timeout seconds (default: 8)
    FAST_CYCLE_INTERVAL         interval during active incident (default: 30)
    DEFAULT_CYCLE_INTERVAL      normal interval (default: 60)
    DEFAULT_RATE_LIMIT          baseline chat_rate_limit_requests (default: 40)
    MIN_RATE_LIMIT              floor for rate limit (default: 5)
    DEFAULT_STREAM_TIMEOUT      baseline ollama timeout seconds (default: 90)
    OCEAN_ADMIN_API_TOKEN       token for ocean-core admin endpoints
    OCEAN_HOST                  ocean-core host (default: 127.0.0.1)
    OCEAN_PORT                  ocean-core port (default: 8030)

Author: Clisonix Engineering
"""

from __future__ import annotations

import json
import logging
import os
import time
import urllib.request
import urllib.error
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from slo_sli_budget import BudgetTracker, BUDGET_WINDOW_DAYS
from slo_sli_gate import SLO_TARGETS

logger = logging.getLogger("clisonix.slo_sli_tuning")

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

TUNING_HISTORY_PATH: str = os.getenv("TUNING_HISTORY_PATH", "slo_tuning_history.json")
TUNING_WINDOW_RUNS: int = int(os.getenv("TUNING_WINDOW_RUNS", "5"))
TUNING_RELAX_ITERATIONS: int = int(os.getenv("TUNING_RELAX_ITERATIONS", "10"))

MIN_PROBE_COUNT: int = int(os.getenv("MIN_PROBE_COUNT", "3"))
MAX_PROBE_COUNT: int = int(os.getenv("MAX_PROBE_COUNT", "20"))
MIN_PROBE_TIMEOUT: int = int(os.getenv("MIN_PROBE_TIMEOUT", "1"))
MAX_PROBE_TIMEOUT: int = int(os.getenv("MAX_PROBE_TIMEOUT", "8"))

FAST_CYCLE_INTERVAL: int = int(os.getenv("FAST_CYCLE_INTERVAL", "30"))
DEFAULT_CYCLE_INTERVAL: int = int(os.getenv("DEFAULT_CYCLE_INTERVAL", "60"))

DEFAULT_RATE_LIMIT: int = int(os.getenv("DEFAULT_RATE_LIMIT", "999999"))  # unlimited
MIN_RATE_LIMIT: int = int(os.getenv("MIN_RATE_LIMIT", "999999"))  # unlimited floor
DEFAULT_STREAM_TIMEOUT: float = float(os.getenv("DEFAULT_STREAM_TIMEOUT", "3600.0"))  # 1 hour elastic

OCEAN_ADMIN_TOKEN: str = os.getenv("OCEAN_ADMIN_API_TOKEN", "")
OCEAN_HOST: str = os.getenv("OCEAN_HOST", "127.0.0.1")
OCEAN_PORT: int = int(os.getenv("OCEAN_PORT", "8030"))
HTTP_TIMEOUT: int = int(os.getenv("REMEDIATION_HTTP_TIMEOUT", "10"))

# Burn-rate thresholds (from SLO_SLI_CRITICAL_SERVICES.md)
HIGH_BURN: float = 14.0   # SEV-1 fast-burn threshold
MED_BURN: float = 5.0    # SEV-2 slow-burn threshold
HIGH_LATENCY_RATIO: float = 0.80  # 80% of SLO target
LOW_LATENCY_RATIO: float = 0.20   # 20% of SLO target
HIGH_ERROR_RATE: float = 0.05     # 5%
LOW_ERROR_RATE: float = 0.01      # 1%


# ═══════════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TuningConfig:
    """
    The live tuning configuration applied by the AutonomousCycle.

    Each field can change after a ``AutoTuner.tune()`` call.
    The cycle reads ``tuner.current_config`` before running collect_all().

    Attributes:
        probe_count:            HTTP probes per service per iteration.
        probe_timeout:          Per-probe timeout in seconds.
        cycle_interval:         Seconds between cycle iterations.
        chat_rate_limit:        Max requests per IP per window (ocean-core).
        stream_timeout_base_s:  Ollama streaming timeout base (ocean-core).
    """
    probe_count: int = 10
    probe_timeout: int = 3
    cycle_interval: int = DEFAULT_CYCLE_INTERVAL
    chat_rate_limit: int = DEFAULT_RATE_LIMIT
    stream_timeout_base_s: float = DEFAULT_STREAM_TIMEOUT

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "TuningConfig":
        return TuningConfig(**{k: v for k, v in d.items() if k in TuningConfig.__dataclass_fields__})


@dataclass
class TuningAdjustment:
    """
    A single tuning change with its rationale.

    Attributes:
        parameter:  Name of the parameter changed.
        previous:   Value before the adjustment.
        current:    Value after the adjustment.
        reason:     Human-readable explanation.
        service:    Service that triggered the change (or "global").
    """
    parameter: str
    previous: Any
    current: Any
    reason: str
    service: str = "global"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TuningRecord:
    """
    Record of one AutoTuner.tune() call.

    Attributes:
        tuned_at:     ISO-8601 UTC timestamp.
        adjustments:  List of TuningAdjustment made in this pass.
        config_after: Snapshot of TuningConfig after adjustments applied.
    """
    tuned_at: str
    adjustments: List[TuningAdjustment]
    config_after: TuningConfig

    def to_dict(self) -> dict:
        return {
            "tuned_at": self.tuned_at,
            "adjustments": [a.to_dict() for a in self.adjustments],
            "config_after": self.config_after.to_dict(),
        }

    @staticmethod
    def from_dict(d: dict) -> "TuningRecord":
        return TuningRecord(
            tuned_at=d["tuned_at"],
            adjustments=[TuningAdjustment(**a) for a in d.get("adjustments", [])],
            config_after=TuningConfig.from_dict(d.get("config_after", {})),
        )


# ═══════════════════════════════════════════════════════════════════════════════
# TUNING HISTORY (persistence)
# ═══════════════════════════════════════════════════════════════════════════════

class TuningHistory:
    """Persists TuningRecord objects as a JSON list."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._records: List[TuningRecord] = []
        self._load()

    @property
    def records(self) -> List[TuningRecord]:
        return self._records

    def append(self, record: TuningRecord) -> None:
        self._records.append(record)

    def save(self) -> None:
        self.path.write_text(
            json.dumps([r.to_dict() for r in self._records], indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            self._records = [TuningRecord.from_dict(r) for r in raw]
        except Exception as exc:
            logger.warning("Could not load tuning history from %s: %s", self.path, exc)


# ═══════════════════════════════════════════════════════════════════════════════
# AUTO-TUNER
# ═══════════════════════════════════════════════════════════════════════════════

class AutoTuner:
    """
    Reads the budget ledger and adjusts the tuning config for the next run.

    Args:
        tracker:       BudgetTracker instance (already loaded from disk).
        history_path:  Path to the tuning history JSON file.
        dry_run:       If True, compute adjustments but do not POST to admin.
    """

    def __init__(
        self,
        tracker: BudgetTracker,
        history_path: str | Path | None = None,
        dry_run: bool = False,
    ):
        self._tracker = tracker
        self._history = TuningHistory(history_path or TUNING_HISTORY_PATH)
        self._dry_run = dry_run
        self._ok_streak: int = 0   # consecutive passing runs (for relaxation)

        # Start from last persisted config (if any), else defaults
        if self._history.records:
            self._config = TuningConfig.from_dict(
                self._history.records[-1].config_after.to_dict()
            )
        else:
            self._config = TuningConfig()

    # ── public ────────────────────────────────────────────────────────────────

    @property
    def current_config(self) -> TuningConfig:
        """The live TuningConfig to use for the next cycle iteration."""
        return self._config

    def tune(self, window_days: int = BUDGET_WINDOW_DAYS) -> TuningRecord:
        """
        Evaluate the budget report and apply tuning adjustments.

        Returns:
            TuningRecord with all adjustments made and the resulting config.
        """
        report = self._tracker.budget_report(window_days=window_days)
        adjustments: List[TuningAdjustment] = []

        # Track whether any breach is active
        has_open_incident = bool(report["open_incidents"])
        all_ok = not report["open_incidents"] and not report["incidents"]

        # ── per-service rules ─────────────────────────────────────────────────
        for svc_key, entry in report["services"].items():
            adjustments.extend(
                self._tune_probe_intensity(svc_key, entry)
            )
            adjustments.extend(
                self._tune_probe_timeout(svc_key, entry)
            )

        # ── ocean-core specific ───────────────────────────────────────────────
        ocean = report["services"].get("ocean_core", {})
        adjustments.extend(self._tune_ocean_rate_limit(ocean))
        adjustments.extend(self._tune_ocean_stream_timeout(ocean))

        # ── cycle interval ────────────────────────────────────────────────────
        adjustments.extend(
            self._tune_cycle_interval(has_open_incident, all_ok)
        )

        # ── push ocean-core tuning via HTTP ───────────────────────────────────
        if adjustments:
            self._push_ocean_tune()

        # ── persist ───────────────────────────────────────────────────────────
        record = TuningRecord(
            tuned_at=datetime.now(timezone.utc).isoformat(),
            adjustments=adjustments,
            config_after=TuningConfig.from_dict(self._config.to_dict()),
        )
        self._history.append(record)
        self._history.save()

        if adjustments:
            logger.info(
                "⚙️  Auto-tuning: %d adjustment(s) applied", len(adjustments)
            )
            for adj in adjustments:
                logger.info(
                    "   %s.%s: %s → %s (%s)",
                    adj.service, adj.parameter, adj.previous, adj.current, adj.reason,
                )
        else:
            logger.debug("Auto-tuning: no adjustments needed")

        return record

    # ── tuning rules ──────────────────────────────────────────────────────────

    def _tune_probe_intensity(
        self, svc_key: str, entry: dict
    ) -> List[TuningAdjustment]:
        """Adjust probe_count based on avg_burn_rate."""
        adjustments: List[TuningAdjustment] = []
        burn = entry.get("avg_burn_rate", 0.0)
        prev = self._config.probe_count

        if burn >= HIGH_BURN:
            new_count = min(MAX_PROBE_COUNT, self._config.probe_count + 2)
            reason = f"avg_burn_rate={burn:.1f}× ≥ {HIGH_BURN}× (SEV-1 range) — need more probe samples"
        elif burn >= MED_BURN:
            new_count = min(MAX_PROBE_COUNT, self._config.probe_count + 1)
            reason = f"avg_burn_rate={burn:.1f}× ≥ {MED_BURN}× (SEV-2 range) — extra samples"
        else:
            return adjustments  # no upward adjustment needed

        if new_count != prev:
            self._config.probe_count = new_count
            adjustments.append(TuningAdjustment(
                parameter="probe_count",
                previous=prev,
                current=new_count,
                reason=reason,
                service=svc_key,
            ))
        return adjustments

    def _tune_probe_timeout(
        self, svc_key: str, entry: dict
    ) -> List[TuningAdjustment]:
        """Adjust probe_timeout based on observed latency_p95 vs SLO target."""
        adjustments: List[TuningAdjustment] = []
        target = SLO_TARGETS.get(svc_key)
        if target is None:
            return adjustments

        observed_lat = entry.get("avg_availability", 1.0)  # proxy
        # Use latency from the last snapshot via the ledger runs
        last_runs = self._tracker._ledger.runs[-TUNING_WINDOW_RUNS:]
        lats = [
            r.services[svc_key].latency_p95_ms
            for r in last_runs
            if svc_key in r.services
        ]
        if not lats:
            return adjustments

        avg_lat = sum(lats) / len(lats)
        slo_lat = target.latency_p95_ms
        ratio = avg_lat / slo_lat if slo_lat > 0 else 0.0

        prev = self._config.probe_timeout

        if ratio > HIGH_LATENCY_RATIO:
            # Services are slow → tighten timeout to detect failures faster
            new_timeout = max(MIN_PROBE_TIMEOUT, self._config.probe_timeout - 1)
            reason = (
                f"avg latency {avg_lat:.0f}ms = {ratio:.0%} of SLO {slo_lat:.0f}ms — "
                "tightening probe timeout to detect failures faster"
            )
        elif ratio < LOW_LATENCY_RATIO and avg_lat > 0:
            # Services are very fast → relax timeout slightly
            new_timeout = min(MAX_PROBE_TIMEOUT, self._config.probe_timeout + 1)
            reason = (
                f"avg latency {avg_lat:.0f}ms = {ratio:.0%} of SLO {slo_lat:.0f}ms — "
                "relaxing probe timeout (services healthy)"
            )
        else:
            return adjustments

        if new_timeout != prev:
            self._config.probe_timeout = new_timeout
            adjustments.append(TuningAdjustment(
                parameter="probe_timeout",
                previous=prev,
                current=new_timeout,
                reason=reason,
                service=svc_key,
            ))
        return adjustments

    def _tune_ocean_rate_limit(self, ocean: dict) -> List[TuningAdjustment]:
        """
        Adjust chat_rate_limit_requests based on ocean_core error_rate.

        High error rate → tighten rate limit to shed load.
        Low error rate + no incidents → restore toward default.
        """
        adjustments: List[TuningAdjustment] = []
        last_runs = self._tracker._ledger.runs[-TUNING_WINDOW_RUNS:]
        rates = [
            r.services["ocean_core"].error_rate
            for r in last_runs
            if "ocean_core" in r.services
        ]
        if not rates:
            return adjustments

        avg_err = sum(rates) / len(rates)
        prev = self._config.chat_rate_limit

        if avg_err > HIGH_ERROR_RATE:
            new_limit = max(MIN_RATE_LIMIT, self._config.chat_rate_limit // 2)
            reason = (
                f"ocean_core avg_error_rate={avg_err:.1%} > {HIGH_ERROR_RATE:.0%} — "
                "halving rate limit to shed load"
            )
        elif avg_err < LOW_ERROR_RATE and self._config.chat_rate_limit < DEFAULT_RATE_LIMIT:
            # Recover toward default: +5 per tune pass
            new_limit = min(DEFAULT_RATE_LIMIT, self._config.chat_rate_limit + 5)
            reason = (
                f"ocean_core avg_error_rate={avg_err:.1%} < {LOW_ERROR_RATE:.0%} — "
                "restoring rate limit toward default"
            )
        else:
            return adjustments

        if new_limit != prev:
            self._config.chat_rate_limit = new_limit
            adjustments.append(TuningAdjustment(
                parameter="chat_rate_limit_requests",
                previous=prev,
                current=new_limit,
                reason=reason,
                service="ocean_core",
            ))
        return adjustments

    def _tune_ocean_stream_timeout(self, ocean: dict) -> List[TuningAdjustment]:
        """
        Adjust ollama_stream_timeout_base_s based on ocean_core latency trend.
        """
        adjustments: List[TuningAdjustment] = []
        target = SLO_TARGETS.get("ocean_core")
        if target is None:
            return adjustments

        last_runs = self._tracker._ledger.runs[-TUNING_WINDOW_RUNS:]
        lats = [
            r.services["ocean_core"].latency_p95_ms
            for r in last_runs
            if "ocean_core" in r.services
        ]
        if not lats:
            return adjustments

        avg_lat = sum(lats) / len(lats)
        slo_lat = target.latency_p95_ms
        ratio = avg_lat / slo_lat if slo_lat > 0 else 0.0
        prev = self._config.stream_timeout_base_s

        if ratio > HIGH_LATENCY_RATIO:
            new_t = prev + 10.0
            reason = (
                f"ocean_core latency {avg_lat:.0f}ms = {ratio:.0%} of SLO — "
                "increasing stream timeout to avoid premature cuts"
            )
        elif ratio < LOW_LATENCY_RATIO and prev > DEFAULT_STREAM_TIMEOUT:
            new_t = max(DEFAULT_STREAM_TIMEOUT, prev - 10.0)
            reason = (
                f"ocean_core latency {avg_lat:.0f}ms = {ratio:.0%} of SLO — "
                "restoring stream timeout toward default"
            )
        else:
            return adjustments

        if new_t != prev:
            self._config.stream_timeout_base_s = new_t
            adjustments.append(TuningAdjustment(
                parameter="ollama_stream_timeout_base_s",
                previous=prev,
                current=new_t,
                reason=reason,
                service="ocean_core",
            ))
        return adjustments

    def _tune_cycle_interval(
        self, has_open_incident: bool, all_ok: bool
    ) -> List[TuningAdjustment]:
        """Speed up cycle when incidents are open; relax when stable."""
        adjustments: List[TuningAdjustment] = []
        prev = self._config.cycle_interval

        if has_open_incident and prev != FAST_CYCLE_INTERVAL:
            self._config.cycle_interval = FAST_CYCLE_INTERVAL
            self._ok_streak = 0
            adjustments.append(TuningAdjustment(
                parameter="cycle_interval",
                previous=prev,
                current=FAST_CYCLE_INTERVAL,
                reason="open incident detected — accelerating cycle",
                service="global",
            ))
        elif all_ok:
            self._ok_streak += 1
            if self._ok_streak >= TUNING_RELAX_ITERATIONS and prev != DEFAULT_CYCLE_INTERVAL:
                self._config.cycle_interval = DEFAULT_CYCLE_INTERVAL
                adjustments.append(TuningAdjustment(
                    parameter="cycle_interval",
                    previous=prev,
                    current=DEFAULT_CYCLE_INTERVAL,
                    reason=f"all services ok for {self._ok_streak} iterations — relaxing cycle interval",
                    service="global",
                ))

        # Also relax probe_count after sustained ok streak
        if all_ok and self._ok_streak >= TUNING_RELAX_ITERATIONS:
            prev_pc = self._config.probe_count
            new_pc = max(MIN_PROBE_COUNT, prev_pc - 1)
            if new_pc != prev_pc:
                self._config.probe_count = new_pc
                adjustments.append(TuningAdjustment(
                    parameter="probe_count",
                    previous=prev_pc,
                    current=new_pc,
                    reason=f"all services ok for {self._ok_streak} iterations — reducing probe count",
                    service="global",
                ))

        return adjustments

    # ── HTTP push ──────────────────────────────────────────────────────────────

    def _push_ocean_tune(self) -> None:
        """
        POST the current chat_rate_limit + stream_timeout to ocean-core
        /admin/tune so changes take effect immediately in the running process.
        """
        if not OCEAN_ADMIN_TOKEN:
            logger.debug("OCEAN_ADMIN_API_TOKEN not set — skipping push to /admin/tune")
            return
        if self._dry_run:
            logger.info(
                "[DRY RUN] Would POST /admin/tune: rate_limit=%d timeout=%.1f",
                self._config.chat_rate_limit,
                self._config.stream_timeout_base_s,
            )
            return

        url = f"http://{OCEAN_HOST}:{OCEAN_PORT}/admin/tune"
        payload = {
            "chat_rate_limit_requests": self._config.chat_rate_limit,
            "ollama_stream_timeout_base_s": self._config.stream_timeout_base_s,
            "reason": "auto-tuning",
        }
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "X-Admin-Token": OCEAN_ADMIN_TOKEN,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
                logger.info(
                    "✅ /admin/tune pushed: rate_limit=%d timeout=%.1f (HTTP %d)",
                    self._config.chat_rate_limit,
                    self._config.stream_timeout_base_s,
                    resp.status,
                )
        except Exception as exc:
            logger.warning("⚠️  /admin/tune push failed: %s", exc)


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
        description="Clisonix SLO/SLI Auto-Tuner"
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--ledger",
        default=os.getenv("BUDGET_LEDGER_PATH", "slo_budget_ledger.json"),
    )
    parser.add_argument(
        "--history",
        default=TUNING_HISTORY_PATH,
    )
    args = parser.parse_args()

    tracker = BudgetTracker(ledger_path=args.ledger)
    tuner = AutoTuner(tracker=tracker, history_path=args.history, dry_run=args.dry_run)
    record = tuner.tune()

    print(f"\nTuning record — {record.tuned_at}")
    if record.adjustments:
        print(f"  {len(record.adjustments)} adjustment(s):")
        for adj in record.adjustments:
            print(f"    [{adj.service}] {adj.parameter}: {adj.previous} → {adj.current}")
            print(f"      reason: {adj.reason}")
    else:
        print("  No adjustments needed — all within bounds")

    cfg = record.config_after
    print(f"\nActive config:")
    print(f"  probe_count={cfg.probe_count}  probe_timeout={cfg.probe_timeout}s"
          f"  cycle_interval={cfg.cycle_interval}s")
    print(f"  chat_rate_limit={cfg.chat_rate_limit}  stream_timeout={cfg.stream_timeout_base_s}s")
