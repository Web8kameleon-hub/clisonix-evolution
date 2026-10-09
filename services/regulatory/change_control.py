from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Optional


def _utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


@dataclass
class DriftThresholds:
    warning: float = 0.05
    critical: float = 0.10


class DriftMonitor:
    """Compares current metrics to a certified baseline and computes drift state."""

    def __init__(self, baseline_metrics: Dict[str, float], thresholds: Optional[DriftThresholds] = None) -> None:
        self.baseline_metrics = baseline_metrics
        self.thresholds = thresholds or DriftThresholds()

    def evaluate(self, current_metrics: Dict[str, float]) -> Dict[str, object]:
        drift_by_metric: Dict[str, float] = {}
        max_drift = 0.0

        for metric, baseline in self.baseline_metrics.items():
            current = current_metrics.get(metric, baseline)
            metric_lower = metric.lower()
            if "success" in metric_lower or "accuracy" in metric_lower:
                degradation = max(0.0, baseline - current)
            elif "retry" in metric_lower or "error" in metric_lower or "latency" in metric_lower:
                degradation = max(0.0, current - baseline)
            else:
                degradation = abs(current - baseline)

            if baseline == 0:
                drift = degradation
            else:
                drift = degradation / abs(baseline)

            drift_by_metric[metric] = drift
            max_drift = max(max_drift, drift)

        if max_drift >= self.thresholds.critical:
            state = "critical"
        elif max_drift >= self.thresholds.warning:
            state = "warning"
        else:
            state = "normal"

        return {
            "state": state,
            "max_drift": max_drift,
            "drift_by_metric": drift_by_metric,
            "timestamp": _utc_now_iso(),
        }


class ChangeControlManager:
    """Tracks approved versions and enforces rollback on critical drift."""

    def __init__(self, certified_version: str) -> None:
        self.certified_version = certified_version
        self.active_version = certified_version
        self.pending_version: Optional[str] = None
        self.change_log = []

    def propose_version(self, version_id: str, rationale: str) -> None:
        self.pending_version = version_id
        self.change_log.append(
            {
                "event": "proposal",
                "version_id": version_id,
                "rationale": rationale,
                "timestamp": _utc_now_iso(),
            }
        )

    def approve_pending(self, reviewer: str) -> bool:
        if not self.pending_version:
            return False
        self.active_version = self.pending_version
        self.change_log.append(
            {
                "event": "approval",
                "version_id": self.active_version,
                "reviewer": reviewer,
                "timestamp": _utc_now_iso(),
            }
        )
        self.pending_version = None
        return True

    def enforce_drift_decision(self, drift_state: str, reason: str) -> Dict[str, str]:
        if drift_state == "critical":
            previous = self.active_version
            self.active_version = self.certified_version
            self.change_log.append(
                {
                    "event": "auto_rollback",
                    "from": previous,
                    "to": self.certified_version,
                    "reason": reason,
                    "timestamp": _utc_now_iso(),
                }
            )
            return {"action": "rollback", "active_version": self.active_version}

        if drift_state == "warning":
            self.change_log.append(
                {
                    "event": "human_review_required",
                    "active_version": self.active_version,
                    "reason": reason,
                    "timestamp": _utc_now_iso(),
                }
            )
            return {"action": "review", "active_version": self.active_version}

        return {"action": "continue", "active_version": self.active_version}
