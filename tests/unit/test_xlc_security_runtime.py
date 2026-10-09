from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OCEAN_CORE_DIR = ROOT / "ocean-core"
if str(OCEAN_CORE_DIR) not in sys.path:
    sys.path.insert(0, str(OCEAN_CORE_DIR))

from xlc_security_runtime import XLCSecurityMonitor  # type: ignore  # noqa: E402


def test_security_monitor_builds_endpoint_resonance_profile_and_baseline() -> None:
    monitor = XLCSecurityMonitor(min_baseline_samples=3, max_baseline_samples=10)

    for value in (-10.0, -11.0, -9.5):
        result = monitor.evaluate(
            endpoint="xlc.route",
            resonance_ndb=value,
            matched=True,
            route_name="START",
            input_text="ju lutem START tani",
        )

    profile = result["resonance_profile"]
    baseline = result["normal_behavior_baseline"]

    assert profile["endpoint"] == "xlc.route"
    assert profile["samples"] == 3
    assert profile["dominant_route"] == "START"
    assert baseline["armed"] is True
    assert baseline["sample_count"] == 3
    assert baseline["avg_ndb"] is not None


def test_security_monitor_emits_signature_and_firewall_action_on_ndb_spike() -> None:
    monitor = XLCSecurityMonitor(
        min_baseline_samples=3,
        max_baseline_samples=10,
        alert_deviation_ndb=50.0,
        block_deviation_ndb=100.0,
    )

    for value in (-10.0, -11.0, -9.0):
        monitor.evaluate(
            endpoint="xlc.route.stream",
            resonance_ndb=value,
            matched=True,
            route_name="START",
            input_text="ju lutem START tani",
        )

    result = monitor.evaluate(
        endpoint="xlc.route.stream",
        resonance_ndb=-250.0,
        matched=False,
        route_name=None,
        input_text="probe",
    )

    signature = result["attack_signature"]
    firewall_action = result["firewall_action"]

    assert signature is not None
    assert signature["deviation_ndb"] >= 100.0
    assert signature["name"] in {"unmatched_resonance_probe", "ndb_deviation_spike"}
    assert firewall_action["action"] == "block"
    assert firewall_action["severity"] == "critical"
