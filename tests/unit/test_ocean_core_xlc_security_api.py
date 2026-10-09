from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
OCEAN_CORE_DIR = ROOT / "ocean-core"
if str(OCEAN_CORE_DIR) not in sys.path:
    sys.path.insert(0, str(OCEAN_CORE_DIR))

import ocean_core_full as ocean_core_module  # type: ignore  # noqa: E402
from xlc_security_runtime import XLCSecurityMonitor  # type: ignore  # noqa: E402


def test_xlc_route_and_inspect_expose_security_payloads(monkeypatch) -> None:
    monitor = XLCSecurityMonitor(min_baseline_samples=3, max_baseline_samples=10)
    monkeypatch.setattr(ocean_core_module, "_xlc_security_monitor", monitor)

    async def _noop_ingest_signal(_request):
        return None

    monkeypatch.setattr(ocean_core_module, "_ingest_signal", _noop_ingest_signal)

    client = TestClient(ocean_core_module.app)

    route_response = client.post(
        "/xlc/route",
        json={"text": "ju lutem START tani", "commands": ["START", "RESET", "MODE"]},
    )
    assert route_response.status_code == 200
    route_payload = route_response.json()
    assert route_payload["measurement_unit"] == "nanodecibel"
    assert "resonance_profile" in route_payload
    assert "normal_behavior_baseline" in route_payload
    assert "attack_signature" in route_payload
    assert "firewall_action" in route_payload
    assert route_payload["resonance_profile"]["endpoint"] == "xlc.route"

    inspect_response = client.post(
        "/xlc/inspect",
        json={"candidate": "A je ti CLX sistemi?", "reference": "CLX", "scan": True},
    )
    assert inspect_response.status_code == 200
    inspect_payload = inspect_response.json()
    assert inspect_payload["measurement_unit"] == "nanodecibel"
    assert inspect_payload["resonance_profile"]["endpoint"] == "xlc.inspect"
    assert "normal_behavior_baseline" in inspect_payload
    assert "firewall_action" in inspect_payload

    profiles_response = client.get("/xlc/security/profiles")
    assert profiles_response.status_code == 200
    profiles_payload = profiles_response.json()
    endpoints = {item["endpoint"] for item in profiles_payload["profiles"]}
    assert {"xlc.route", "xlc.inspect"}.issubset(endpoints)

    route_profile_response = client.get("/xlc/security/profiles/xlc.route")
    assert route_profile_response.status_code == 200
    route_profile_payload = route_profile_response.json()["profile"]
    assert route_profile_payload["endpoint"] == "xlc.route"
    assert route_profile_payload["samples"] >= 1


def test_xlc_route_stream_emits_security_and_firewall_action(monkeypatch) -> None:
    async def _fake_assess_xlc_security(**_kwargs):
        return {
            "resonance_profile": {"endpoint": "xlc.route.stream", "samples": 2},
            "normal_behavior_baseline": {
                "endpoint": "xlc.route.stream",
                "armed": True,
                "sample_count": 2,
                "avg_ndb": 0.0,
                "min_ndb": -1.0,
                "max_ndb": 0.0,
                "stddev_ndb": 0.5,
            },
            "attack_signature": {
                "name": "unmatched_resonance_probe",
                "severity": "critical",
                "endpoint": "xlc.route.stream",
            },
            "firewall_action": {
                "action": "block",
                "reason": "unmatched_resonance_probe",
                "severity": "critical",
            },
        }

    monkeypatch.setattr(ocean_core_module, "_assess_xlc_security", _fake_assess_xlc_security)

    client = TestClient(ocean_core_module.app)

    with client.stream(
        "POST",
        "/xlc/route/stream",
        json={
            "text": "???????????????????????? probe",
            "commands": ["START", "RESET", "MODE"],
            "threshold": 0.9999999999999999,
            "max_tokens": 64,
        },
        headers={"Accept": "text/event-stream"},
    ) as response:
        assert response.status_code == 200
        stream_body = "".join(response.iter_text())
        normalized_stream = stream_body.replace("\\n\\n", "\n\n")
        events = []
        for payload in re.findall(r"data: (.+?)(?:\n\n|$)", normalized_stream, re.DOTALL):
            payload = payload.strip()
            if payload == "[DONE]":
                break
            events.append(json.loads(payload))

    phases = [event.get("phase") for event in events]
    assert "security" in phases
    assert "firewall_action" in phases

    security_event = next(event for event in events if event.get("phase") == "security")
    firewall_event = next(event for event in events if event.get("phase") == "firewall_action")
    complete_event = next(event for event in events if event.get("phase") == "complete")

    assert security_event["attack_signature"] is not None
    assert security_event["firewall_action"]["action"] == "block"
    assert firewall_event["action"] == "block"
    assert complete_event["reason"] == "blocked_by_xlc_firewall"
