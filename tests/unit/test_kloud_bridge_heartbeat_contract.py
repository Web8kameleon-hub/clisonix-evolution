import importlib.util
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
KLOUD_BRIDGE_MAIN = ROOT / "services" / "kloud_bridge" / "main.py"
SPEC = importlib.util.spec_from_file_location("kloud_bridge_main", KLOUD_BRIDGE_MAIN)
assert SPEC and SPEC.loader
kloud_bridge_main = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(kloud_bridge_main)


def _mk_heartbeat(**kwargs):
    payload = {
        "node_id": "edge-node-01",
        "status": "online",
        "uptime_seconds": 42,
        "temperature_c": 33.5,
        "power_watts": 4.2,
        "latency_ms": 12.0,
        "telemetry": {"source": "hardware"},
        "forward_to_ocean": False,
    }
    payload.update(kwargs)
    return SimpleNamespace(**payload)


def test_validate_hardware_heartbeat_contract_accepts_valid_payload():
    request = _mk_heartbeat()

    reasons = kloud_bridge_main._validate_hardware_heartbeat_contract(request)

    assert reasons == []


def test_validate_hardware_heartbeat_contract_rejects_invalid_fields():
    request = _mk_heartbeat(
        status="unknown-status",
        uptime_seconds=-1,
        temperature_c=999,
        power_watts=-2,
        latency_ms=-5,
        telemetry={"source": "demo"},
    )

    reasons = kloud_bridge_main._validate_hardware_heartbeat_contract(request)

    assert any("status must be one of" in reason for reason in reasons)
    assert "uptime_seconds must be >= 0" in reasons
    assert "temperature_c must be between -80 and 180" in reasons
    assert "power_watts must be >= 0" in reasons
    assert "latency_ms must be >= 0" in reasons
    assert any("non-live data" in reason for reason in reasons)


def test_heartbeat_conformance_counters_track_pass_and_fail():
    kloud_bridge_main.HEARTBEAT_CONFORMANCE.clear()
    kloud_bridge_main.HEARTBEAT_CONFORMANCE.update(
        {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "last_pass_at": None,
            "last_failure_at": None,
            "last_failure_reasons": [],
            "by_node": {},
        }
    )

    kloud_bridge_main._record_heartbeat_conformance("edge-node-01", passed=True)
    kloud_bridge_main._record_heartbeat_conformance("edge-node-01", passed=False, reasons=["invalid status"])

    summary = kloud_bridge_main._heartbeat_conformance_summary(limit_nodes=5)

    assert summary["total"] == 2
    assert summary["passed"] == 1
    assert summary["failed"] == 1
    assert summary["pass_rate"] == 0.5
    assert summary["fail_rate"] == 0.5
    assert summary["last_failure_reasons"] == ["invalid status"]
    assert summary["top_nodes"][0]["node_id"] == "edge-node-01"
    assert summary["top_nodes"][0]["total"] == 2
