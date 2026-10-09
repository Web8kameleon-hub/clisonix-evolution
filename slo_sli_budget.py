#!/usr/bin/env python3
"""
CLISONIX SLO/SLI ERROR BUDGET TRACKER
=======================================

Persists every CollectorReport run to a JSON ledger and answers the
questions defined in docs/enterprise/SLO_SLI_CRITICAL_SERVICES.md:

    Error Budget
    - 99.95% => 21m 54s/month downtime budget
    - 99.90% => 43m 49s/month downtime budget

    Weekly Review
    - Burn-rate review
    - Top 3 incidents and MTTR
    - Proposed reliability tasks for next sprint

Pipeline position:
    collect_all()  →  SLOSLIAlerter.process()  →  BudgetTracker.record()
                                                         ↓
                                                  budget_report()
                                                  (weekly / on-demand)

Ledger format (``slo_budget_ledger.json``):
    {
      "runs":      [ RunRecord, ... ],
      "incidents": [ IncidentRecord, ... ]
    }

    RunRecord   – one entry per ``record()`` call
    IncidentRecord – opens when a service first breaches, closes on recovery

Usage (CLI):
    # Record a live check and print the current budget table
    python slo_sli_budget.py

    # Print budget report only (no live probe)
    python slo_sli_budget.py --report

    # Use a custom ledger path
    python slo_sli_budget.py --ledger /var/lib/clisonix/slo_budget.json

Usage (programmatic):
    from slo_sli_budget import BudgetTracker
    from slo_sli_collector import collect_all

    tracker = BudgetTracker()            # reads ledger from disk
    report  = collect_all()
    tracker.record(report)               # persists run, opens/closes incidents
    summary = tracker.budget_report()    # full weekly-review dict
    print(summary["markdown"])

Environment variables:
    BUDGET_LEDGER_PATH   path to JSON ledger (default: slo_budget_ledger.json)
    BUDGET_WINDOW_DAYS   look-back window for the weekly report (default: 7)

Author: Clisonix Engineering
"""

from __future__ import annotations

import json
import logging
import os
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from slo_sli_collector import CollectorReport, collect_all, PROBE_COUNT, PROBE_TIMEOUT
from slo_sli_gate import SLO_TARGETS

logger = logging.getLogger("clisonix.slo_sli_budget")

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

BUDGET_LEDGER_PATH: str = os.getenv(
    "BUDGET_LEDGER_PATH", "slo_budget_ledger.json"
)
BUDGET_WINDOW_DAYS: int = int(os.getenv("BUDGET_WINDOW_DAYS", "7"))

# Minutes of allowed downtime per calendar month from SLO_SLI_CRITICAL_SERVICES.md
# 99.95% SLO → 21m 54s  = 21.9 min/month
# 99.90% SLO → 43m 49s  = 43.8 min/month
_MONTHLY_BUDGET_MINUTES: Dict[str, float] = {
    "ocean_core":  21.9,
    "backend_api": 21.9,
    "openmind":    21.9,
    "excel_core":  21.9,
    "ollama":      43.8,
    "translation": 43.8,
}

# Severity labels used for incident records
_BREACH_SEVERITIES = {"SEV-1", "SEV-2", "SEV-3"}


# ═══════════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class RunRecord:
    """
    Snapshot of one collector run — one entry per ``BudgetTracker.record()`` call.

    Attributes:
        run_id:     ISO-8601 UTC timestamp used as a unique key.
        services:   Per-service gate results for this run.
    """
    run_id: str  # ISO-8601 UTC
    services: Dict[str, "ServiceRunResult"]

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "services": {k: asdict(v) for k, v in self.services.items()},
        }

    @staticmethod
    def from_dict(d: dict) -> "RunRecord":
        return RunRecord(
            run_id=d["run_id"],
            services={
                k: ServiceRunResult(**v)
                for k, v in d.get("services", {}).items()
            },
        )


@dataclass
class ServiceRunResult:
    """Per-service result stored inside a RunRecord."""
    passed: bool
    severity: str          # OK / SEV-1 / SEV-2 / SEV-3
    availability: float    # 0–1
    latency_p95_ms: float
    error_rate: float      # 0–1
    dependency_health: float  # 0–1
    burn_rate: float


@dataclass
class IncidentRecord:
    """
    Tracks a single reliability incident.

    An incident opens when a service first reports a non-OK severity and
    closes when the next run shows ``severity == "OK"`` (passed).
    MTTR = closed_at − opened_at.

    Attributes:
        incident_id:  ISO-8601 UTC of the opening run.
        service:      Service key (e.g. "ocean_core").
        severity:     Highest severity seen during the incident.
        opened_at:    ISO-8601 UTC when the breach was first detected.
        closed_at:    ISO-8601 UTC when the service recovered (None if open).
        mttr_minutes: Float minutes from open to close (None if still open).
    """
    incident_id: str
    service: str
    severity: str
    opened_at: str
    closed_at: Optional[str] = None
    mttr_minutes: Optional[float] = None

    @property
    def is_open(self) -> bool:
        return self.closed_at is None

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "IncidentRecord":
        return IncidentRecord(**d)


# ═══════════════════════════════════════════════════════════════════════════════
# LEDGER (persistence)
# ═══════════════════════════════════════════════════════════════════════════════

class Ledger:
    """
    Thin JSON persistence layer for RunRecord and IncidentRecord objects.

    Thread-safety: not guaranteed — designed for single-process use.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._runs: List[RunRecord] = []
        self._incidents: List[IncidentRecord] = []
        self._load()

    # ── public collections ────────────────────────────────────────────────────

    @property
    def runs(self) -> List[RunRecord]:
        return self._runs

    @property
    def incidents(self) -> List[IncidentRecord]:
        return self._incidents

    # ── persistence ──────────────────────────────────────────────────────────

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            self._runs = [RunRecord.from_dict(r) for r in raw.get("runs", [])]
            self._incidents = [
                IncidentRecord.from_dict(i) for i in raw.get("incidents", [])
            ]
            logger.debug(
                "Ledger loaded: %d runs, %d incidents from %s",
                len(self._runs),
                len(self._incidents),
                self.path,
            )
        except Exception as exc:
            logger.warning("Could not load ledger from %s: %s", self.path, exc)

    def save(self) -> None:
        data = {
            "runs": [r.to_dict() for r in self._runs],
            "incidents": [i.to_dict() for i in self._incidents],
        }
        self.path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        logger.debug("Ledger saved: %d runs, %d incidents", len(self._runs), len(self._incidents))

    # ── mutation helpers ──────────────────────────────────────────────────────

    def append_run(self, run: RunRecord) -> None:
        self._runs.append(run)

    def append_incident(self, inc: IncidentRecord) -> None:
        self._incidents.append(inc)

    def open_incidents_for(self, service: str) -> List[IncidentRecord]:
        return [i for i in self._incidents if i.service == service and i.is_open]

    def runs_in_window(self, since: datetime) -> List[RunRecord]:
        since_iso = since.isoformat()
        return [r for r in self._runs if r.run_id >= since_iso]


# ═══════════════════════════════════════════════════════════════════════════════
# BUDGET TRACKER
# ═══════════════════════════════════════════════════════════════════════════════

class BudgetTracker:
    """
    Records CollectorReport runs, manages incident lifecycle, and computes
    error budget consumption for the weekly SLO review.

    Args:
        ledger_path:    Path to the JSON ledger file.
                        Defaults to ``BUDGET_LEDGER_PATH`` env var.
        window_days:    Look-back window for budget calculations.
                        Defaults to ``BUDGET_WINDOW_DAYS`` env var.
    """

    def __init__(
        self,
        ledger_path: str | Path | None = None,
        window_days: int = BUDGET_WINDOW_DAYS,
    ):
        self._ledger = Ledger(ledger_path or BUDGET_LEDGER_PATH)
        self._window_days = window_days

    # ── public API ────────────────────────────────────────────────────────────

    def record(self, report: CollectorReport) -> None:
        """
        Persist a CollectorReport run and update incident records.

        Opens a new IncidentRecord when a service first breaches its SLO.
        Closes the record (computing MTTR) when the service recovers.

        Args:
            report: CollectorReport from slo_sli_collector.collect_all().
        """
        now = datetime.now(timezone.utc).isoformat()
        service_results: Dict[str, ServiceRunResult] = {}

        for result in report.gate_results:
            snap = next(
                (s for s in report.snapshots if s.service_name == result.service_name),
                None,
            )
            srr = ServiceRunResult(
                passed=result.passed,
                severity=result.severity if not result.passed else "OK",
                availability=snap.availability if snap else 0.0,
                latency_p95_ms=snap.latency_p95_ms if snap else 0.0,
                error_rate=snap.error_rate if snap else 0.0,
                dependency_health=snap.dependency_health if snap else 0.0,
                burn_rate=result.burn_rate,
            )
            service_results[result.service_name] = srr

            # ── incident lifecycle ─────────────────────────────────────────
            if not result.passed and result.severity in _BREACH_SEVERITIES:
                open_incs = self._ledger.open_incidents_for(result.service_name)
                if not open_incs:
                    inc = IncidentRecord(
                        incident_id=now,
                        service=result.service_name,
                        severity=result.severity,
                        opened_at=now,
                    )
                    self._ledger.append_incident(inc)
                    logger.info(
                        "Incident opened: %s %s @ %s",
                        result.service_name,
                        result.severity,
                        now,
                    )
                else:
                    # Update severity to the highest seen
                    inc = open_incs[0]
                    _sev_rank = {"SEV-1": 3, "SEV-2": 2, "SEV-3": 1}
                    if _sev_rank.get(result.severity, 0) > _sev_rank.get(inc.severity, 0):
                        inc.severity = result.severity

            elif result.passed:
                for open_inc in self._ledger.open_incidents_for(result.service_name):
                    opened_dt = datetime.fromisoformat(open_inc.opened_at)
                    closed_dt = datetime.fromisoformat(now)
                    mttr = (closed_dt - opened_dt).total_seconds() / 60.0
                    open_inc.closed_at = now
                    open_inc.mttr_minutes = round(mttr, 2)
                    logger.info(
                        "Incident closed: %s MTTR=%.1f min",
                        open_inc.service,
                        mttr,
                    )

        run = RunRecord(run_id=now, services=service_results)
        self._ledger.append_run(run)
        self._ledger.save()

    def budget_report(self, window_days: int | None = None) -> dict:
        """
        Compute the SLO error budget report for the look-back window.

        Returns a dict with keys:
            generated_at:    ISO-8601 UTC timestamp
            window_days:     int
            services:        {service: BudgetEntry}
            incidents:       list of closed IncidentRecord dicts (window only)
            open_incidents:  list of currently open IncidentRecord dicts
            top3_incidents:  top-3 incidents by MTTR (for weekly review)
            markdown:        pre-formatted markdown weekly review
        """
        wdays = window_days or self._window_days
        since = datetime.now(timezone.utc) - timedelta(days=wdays)
        runs = self._ledger.runs_in_window(since)

        service_entries: Dict[str, dict] = {}
        for key in SLO_TARGETS:
            entry = self._compute_budget_entry(key, runs, since)
            service_entries[key] = entry

        # Closed incidents within window
        closed = [
            i for i in self._ledger.incidents
            if not i.is_open and i.closed_at and i.closed_at >= since.isoformat()
        ]
        # Open incidents (any age)
        open_incs = [i for i in self._ledger.incidents if i.is_open]
        # Top-3 by MTTR
        top3 = sorted(
            [i for i in closed if i.mttr_minutes is not None],
            key=lambda i: i.mttr_minutes or 0.0,
            reverse=True,
        )[:3]

        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "window_days": wdays,
            "services": service_entries,
            "incidents": [i.to_dict() for i in closed],
            "open_incidents": [i.to_dict() for i in open_incs],
            "top3_incidents": [i.to_dict() for i in top3],
            "markdown": self._render_markdown(
                wdays, service_entries, closed, open_incs, top3
            ),
        }
        return report

    # ── private helpers ───────────────────────────────────────────────────────

    def _compute_budget_entry(
        self,
        service: str,
        runs: List[RunRecord],
        since: datetime,
    ) -> dict:
        """
        For a given service and list of runs, compute:
        - total checks
        - failed checks (availability = 0 OR SEV-1)
        - downtime minutes consumed
        - remaining budget minutes
        - budget consumed % (0–100)
        - average availability
        - average burn rate
        """
        if not runs:
            return _empty_budget_entry(service)

        service_runs = [
            r.services[service] for r in runs if service in r.services
        ]
        if not service_runs:
            return _empty_budget_entry(service)

        total = len(service_runs)
        failed = sum(1 for s in service_runs if not s.passed)

        # Estimate downtime: assume each run covers the time since the previous
        # run (or window start for the first run).  We compute this from
        # actual run timestamps for accuracy.
        downtime_min = _estimate_downtime_minutes(service, runs, since)

        monthly_budget = _MONTHLY_BUDGET_MINUTES.get(service, 21.9)
        # Scale monthly budget to the look-back window
        window_budget = monthly_budget * (self._window_days / 30.0)
        remaining = max(0.0, window_budget - downtime_min)
        consumed_pct = min(100.0, (downtime_min / window_budget) * 100.0) if window_budget else 0.0

        avg_avail = sum(s.availability for s in service_runs) / total
        avg_burn = sum(s.burn_rate for s in service_runs) / total

        target = SLO_TARGETS.get(service)
        return {
            "service": service,
            "display_name": target.service_name if target else service,
            "availability_slo": target.availability_slo if target else 0.9995,
            "total_checks": total,
            "failed_checks": failed,
            "avg_availability": round(avg_avail, 6),
            "avg_burn_rate": round(avg_burn, 2),
            "downtime_minutes": round(downtime_min, 2),
            "window_budget_minutes": round(window_budget, 2),
            "remaining_budget_minutes": round(remaining, 2),
            "budget_consumed_pct": round(consumed_pct, 1),
            "status": (
                "critical" if consumed_pct >= 100
                else "warning" if consumed_pct >= 50
                else "ok"
            ),
        }

    @staticmethod
    def _render_markdown(
        window_days: int,
        service_entries: Dict[str, dict],
        closed: List[IncidentRecord],
        open_incs: List[IncidentRecord],
        top3: List[IncidentRecord],
    ) -> str:
        """Render the weekly SLO review markdown matching the doc spec."""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        lines = [
            f"# 📊 Clisonix SLO Weekly Review — {now}",
            f"_Window: last {window_days} days_",
            "",
            "## Error Budget Consumption",
            "",
            "| Service | SLO | Avg Avail | Downtime | Budget Used | Remaining | Status |",
            "|---|---|---|---|---|---|---|",
        ]
        status_emoji = {"ok": "✅", "warning": "⚠️", "critical": "🔴"}
        for entry in service_entries.values():
            icon = status_emoji.get(entry["status"], "⚪")
            slo_pct = f"{entry['availability_slo']:.4%}"
            avail_pct = f"{entry['avg_availability']:.4%}"
            lines.append(
                f"| **{entry['display_name']}** "
                f"| {slo_pct} "
                f"| {avail_pct} "
                f"| {entry['downtime_minutes']:.1f} min "
                f"| {entry['budget_consumed_pct']:.1f}% "
                f"| {entry['remaining_budget_minutes']:.1f} min "
                f"| {icon} {entry['status'].upper()} |"
            )

        lines += [
            "",
            "## Burn Rate Summary",
            "",
            "| Service | Avg Burn Rate | SLO Checks | Failed |",
            "|---|---|---|---|",
        ]
        for entry in service_entries.values():
            lines.append(
                f"| {entry['display_name']} "
                f"| {entry['avg_burn_rate']:.1f}× "
                f"| {entry['total_checks']} "
                f"| {entry['failed_checks']} |"
            )

        lines += ["", "## Top 3 Incidents by MTTR", ""]
        if top3:
            lines += [
                "| # | Service | Severity | Opened | Closed | MTTR |",
                "|---|---|---|---|---|---|",
            ]
            for i, inc in enumerate(top3, 1):
                opened = inc.opened_at[:19].replace("T", " ")
                closed_str = inc.closed_at[:19].replace("T", " ") if inc.closed_at else "open"
                mttr = f"{inc.mttr_minutes:.1f} min" if inc.mttr_minutes else "n/a"
                lines.append(
                    f"| {i} | {inc.service} | {inc.severity} "
                    f"| {opened} | {closed_str} | {mttr} |"
                )
        else:
            lines.append("_No closed incidents in this window._")

        if open_incs:
            lines += [
                "",
                f"## ⚠️ Open Incidents ({len(open_incs)})",
                "",
                "| Service | Severity | Opened | Duration |",
                "|---|---|---|---|",
            ]
            now_dt = datetime.now(timezone.utc)
            for inc in open_incs:
                opened_dt = datetime.fromisoformat(inc.opened_at)
                dur_min = (now_dt - opened_dt).total_seconds() / 60
                opened_str = inc.opened_at[:19].replace("T", " ")
                lines.append(
                    f"| {inc.service} | {inc.severity} "
                    f"| {opened_str} | {dur_min:.1f} min |"
                )

        lines += [
            "",
            "## Proposed Reliability Tasks for Next Sprint",
            "",
        ]
        # Auto-generate tasks based on which services are in warning/critical
        tasks_added = False
        for entry in service_entries.values():
            if entry["status"] == "critical":
                lines.append(
                    f"- [ ] **{entry['display_name']}**: budget exhausted "
                    f"({entry['budget_consumed_pct']:.0f}% used) — "
                    "investigate root cause and add circuit-breaker"
                )
                tasks_added = True
            elif entry["status"] == "warning":
                lines.append(
                    f"- [ ] **{entry['display_name']}**: budget at "
                    f"{entry['budget_consumed_pct']:.0f}% — review error logs"
                )
                tasks_added = True
        if not tasks_added:
            lines.append("_All services within SLO. No remediation tasks required._")

        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _empty_budget_entry(service: str) -> dict:
    target = SLO_TARGETS.get(service)
    return {
        "service": service,
        "display_name": target.service_name if target else service,
        "availability_slo": target.availability_slo if target else 0.9995,
        "total_checks": 0,
        "failed_checks": 0,
        "avg_availability": 1.0,
        "avg_burn_rate": 0.0,
        "downtime_minutes": 0.0,
        "window_budget_minutes": 0.0,
        "remaining_budget_minutes": 0.0,
        "budget_consumed_pct": 0.0,
        "status": "ok",
    }


def _estimate_downtime_minutes(
    service: str,
    runs: List[RunRecord],
    since: datetime,
) -> float:
    """
    Estimate downtime minutes for a service across a list of ordered runs.

    Strategy: each failed run contributes the time gap to the *next* run
    (or to now, if it is the last run) as downtime, capped to 5 minutes
    (the expected check interval) to avoid inflating downtime during gaps.
    """
    MAX_INTERVAL_MIN = 5.0  # maximum downtime credited per failed run
    total = 0.0
    sorted_runs = sorted(runs, key=lambda r: r.run_id)

    for idx, run in enumerate(sorted_runs):
        if service not in run.services:
            continue
        srr = run.services[service]
        if srr.passed:
            continue

        # Time gap to next run
        if idx + 1 < len(sorted_runs):
            next_dt = datetime.fromisoformat(sorted_runs[idx + 1].run_id)
            this_dt = datetime.fromisoformat(run.run_id)
            gap_min = (next_dt - this_dt).total_seconds() / 60.0
        else:
            # Last run — credit until now, capped
            this_dt = datetime.fromisoformat(run.run_id)
            gap_min = (datetime.now(timezone.utc) - this_dt).total_seconds() / 60.0

        total += min(gap_min, MAX_INTERVAL_MIN)

    return total


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
        description="Clisonix SLO/SLI Error Budget Tracker"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Print the weekly budget report without running a live probe",
    )
    parser.add_argument(
        "--ledger",
        default=BUDGET_LEDGER_PATH,
        help=f"Path to JSON ledger (default: {BUDGET_LEDGER_PATH})",
    )
    parser.add_argument(
        "--window",
        type=int,
        default=BUDGET_WINDOW_DAYS,
        help=f"Look-back window in days (default: {BUDGET_WINDOW_DAYS})",
    )
    parser.add_argument(
        "--probe-count",
        type=int,
        default=PROBE_COUNT,
    )
    parser.add_argument(
        "--probe-timeout",
        type=int,
        default=PROBE_TIMEOUT,
    )
    args = parser.parse_args()

    tracker = BudgetTracker(ledger_path=args.ledger, window_days=args.window)

    if not args.report:
        print("🔬 Running live probe …")
        live_report = collect_all(
            probe_count=args.probe_count,
            probe_timeout=args.probe_timeout,
        )
        tracker.record(live_report)
        print("✅ Run recorded to ledger")

    summary = tracker.budget_report(window_days=args.window)

    # Print markdown weekly review to stdout
    print("\n" + summary["markdown"])

    # Print open incidents
    if summary["open_incidents"]:
        print(f"\n⚠️  Open incidents: {len(summary['open_incidents'])}")
        for inc in summary["open_incidents"]:
            print(f"   {inc['service']:20s} {inc['severity']} opened {inc['opened_at'][:19]}")
    else:
        print("\n✅ No open incidents")
