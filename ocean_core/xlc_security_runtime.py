from __future__ import annotations

import statistics
import time
from collections import Counter, deque
from typing import Any, Deque, Dict, List, Optional


class XLCSecurityMonitor:
    """Tracks endpoint resonance profiles and derives simple ndB-based security decisions."""

    def __init__(
        self,
        *,
        min_baseline_samples: int = 5,
        max_baseline_samples: int = 120,
        alert_deviation_ndb: float = 500_000_000.0,
        block_deviation_ndb: float = 2_000_000_000.0,
    ) -> None:
        self.min_baseline_samples = max(3, int(min_baseline_samples))
        self.max_baseline_samples = max(self.min_baseline_samples, int(max_baseline_samples))
        self.alert_deviation_ndb = float(alert_deviation_ndb)
        self.block_deviation_ndb = float(block_deviation_ndb)
        self._profiles: Dict[str, Dict[str, Any]] = {}

    def evaluate(
        self,
        *,
        endpoint: str,
        resonance_ndb: float,
        matched: bool,
        route_name: Optional[str],
        input_text: str,
    ) -> Dict[str, Any]:
        profile = self._profiles.setdefault(
            endpoint,
            {
                "history": deque(maxlen=self.max_baseline_samples),
                "matched_history": deque(maxlen=self.max_baseline_samples),
                "route_counts": Counter(),
                "total_requests": 0,
                "last_seen": None,
            },
        )

        baseline = self._build_baseline(endpoint, profile)
        signature = self._detect_signature(
            endpoint=endpoint,
            profile=profile,
            baseline=baseline,
            resonance_ndb=float(resonance_ndb),
            matched=matched,
            route_name=route_name,
            input_text=input_text,
        )
        firewall_action = self._decide_firewall_action(signature)

        profile["history"].append(float(resonance_ndb))
        profile["matched_history"].append(bool(matched))
        profile["route_counts"].update([route_name or "__unmatched__"])
        profile["total_requests"] += 1
        profile["last_seen"] = time.time()

        return {
            "resonance_profile": self._profile_snapshot(endpoint, profile),
            "normal_behavior_baseline": self._build_baseline(endpoint, profile),
            "attack_signature": signature,
            "firewall_action": firewall_action,
        }

    def get_profiles(self) -> List[Dict[str, Any]]:
        return [self._profile_snapshot(endpoint, profile) for endpoint, profile in sorted(self._profiles.items())]

    def get_profile(self, endpoint: str) -> Optional[Dict[str, Any]]:
        profile = self._profiles.get(endpoint)
        if profile is None:
            return None
        return self._profile_snapshot(endpoint, profile)

    def _build_baseline(self, endpoint: str, profile: Dict[str, Any]) -> Dict[str, Any]:
        history = list(profile["history"])
        sample_count = len(history)
        if not history:
            return {
                "endpoint": endpoint,
                "armed": False,
                "sample_count": 0,
                "avg_ndb": None,
                "min_ndb": None,
                "max_ndb": None,
                "stddev_ndb": None,
            }

        stddev = statistics.pstdev(history) if sample_count > 1 else 0.0
        return {
            "endpoint": endpoint,
            "armed": sample_count >= self.min_baseline_samples,
            "sample_count": sample_count,
            "avg_ndb": round(statistics.fmean(history), 3),
            "min_ndb": round(min(history), 3),
            "max_ndb": round(max(history), 3),
            "stddev_ndb": round(stddev, 3),
        }

    def _profile_snapshot(self, endpoint: str, profile: Dict[str, Any]) -> Dict[str, Any]:
        history = list(profile["history"])
        matched_history = list(profile["matched_history"])
        matched_rate = (
            round(sum(1 for item in matched_history if item) / len(matched_history), 4)
            if matched_history
            else 0.0
        )
        route_counts = profile["route_counts"]
        dominant_route = route_counts.most_common(1)[0][0] if route_counts else None
        return {
            "endpoint": endpoint,
            "samples": len(history),
            "total_requests": int(profile["total_requests"]),
            "matched_rate": matched_rate,
            "dominant_route": dominant_route,
            "routes": dict(route_counts.most_common(5)),
            "avg_ndb": round(statistics.fmean(history), 3) if history else None,
            "min_ndb": round(min(history), 3) if history else None,
            "max_ndb": round(max(history), 3) if history else None,
            "last_seen_epoch": profile["last_seen"],
        }

    def _detect_signature(
        self,
        *,
        endpoint: str,
        profile: Dict[str, Any],
        baseline: Dict[str, Any],
        resonance_ndb: float,
        matched: bool,
        route_name: Optional[str],
        input_text: str,
    ) -> Optional[Dict[str, Any]]:
        if not baseline["armed"]:
            return None

        avg_ndb = float(baseline["avg_ndb"])
        deviation_ndb = abs(float(resonance_ndb) - avg_ndb)
        dominant_route = self._profile_snapshot(endpoint, profile).get("dominant_route")

        signature_name: Optional[str] = None
        severity = "low"
        if not matched and deviation_ndb >= self.block_deviation_ndb:
            signature_name = "unmatched_resonance_probe"
            severity = "critical"
        elif deviation_ndb >= self.block_deviation_ndb:
            signature_name = "ndb_deviation_spike"
            severity = "critical"
        elif dominant_route and route_name and dominant_route not in {route_name, "__unmatched__"} and deviation_ndb >= self.alert_deviation_ndb:
            signature_name = "route_flip_deviation"
            severity = "high"
        elif not matched and deviation_ndb >= self.alert_deviation_ndb:
            signature_name = "unmatched_resonance_probe"
            severity = "high"
        elif deviation_ndb >= self.alert_deviation_ndb:
            signature_name = "ndb_deviation_drift"
            severity = "medium"

        if signature_name is None:
            return None

        return {
            "name": signature_name,
            "severity": severity,
            "endpoint": endpoint,
            "route_name": route_name,
            "matched": matched,
            "deviation_ndb": round(deviation_ndb, 3),
            "baseline_avg_ndb": baseline["avg_ndb"],
            "dominant_route": dominant_route,
            "input_chars": len(input_text or ""),
        }

    def _decide_firewall_action(self, signature: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if signature is None:
            return {"action": "allow", "reason": "baseline_ok", "severity": "none"}
        severity = signature["severity"]
        if severity == "critical":
            return {"action": "block", "reason": signature["name"], "severity": severity}
        if severity == "high":
            return {"action": "throttle", "reason": signature["name"], "severity": severity}
        return {"action": "monitor", "reason": signature["name"], "severity": severity}
