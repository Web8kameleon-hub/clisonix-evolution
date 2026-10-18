"""Test-only observations exercise rejection; live verification is separate."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import importlib.util
import json
from pathlib import Path
from unittest.mock import Mock

import pytest

SOURCE = Path(__file__).resolve().parents[2] / "scripts/hetzner/post_deploy_verify_status.py"
spec = importlib.util.spec_from_file_location("post_deploy_status", SOURCE)
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def fixture_snapshot():
    timestamp = datetime.now(timezone.utc).isoformat()
    services = [{"name": name, "healthy": True, "latency_ms": 0.0, "observed_at": timestamp} for name in sorted(verify.NAMES)]
    month = {"month": timestamp[:7], "samples": 1, "uptime": 100.0, "last_sample_at": timestamp,
             "services": {name: {"samples": 1, "uptime": 100.0} for name in verify.NAMES}}
    return {"status": "operational", "timestamp": timestamp, "services": services,
            "telemetry": {"status": "recorded", "last_sample_at": timestamp, "uptime_history": [month]}}


def fixture_storage(snapshot):
    storage = Mock()
    storage.xrevrange.return_value = [("test-record", {"observed_at": snapshot["timestamp"], "services": json.dumps(snapshot["services"])})]
    counts = {"samples": "1", "operational": "1"}
    counts.update({name + ":samples": "1" for name in verify.NAMES})
    counts.update({name + ":operational": "1" for name in verify.NAMES})
    storage.hgetall.return_value = counts
    return storage


def test_verifier_accepts_zero_latency_supported_by_storage():
    snapshot = fixture_snapshot()
    assert verify.verify_snapshot(snapshot, fixture_storage(snapshot)) == snapshot["timestamp"]


@pytest.mark.parametrize("failure", ["unhealthy", "static-string", "nan", "boolean", "missing-service", "stale", "no-history", "no-storage", "wrong-history"])
def test_verifier_rejects_unsubstantiated_success(failure):
    snapshot = fixture_snapshot()
    storage = fixture_storage(deepcopy(snapshot))
    if failure == "unhealthy": snapshot["services"][0]["healthy"] = False
    elif failure == "static-string": snapshot["services"][0]["latency_ms"] = "10ms"
    elif failure == "nan": snapshot["services"][0]["latency_ms"] = float("nan")
    elif failure == "boolean": snapshot["services"][0]["latency_ms"] = True
    elif failure == "missing-service": snapshot["services"].pop()
    elif failure == "stale": snapshot["timestamp"] = (datetime.now(timezone.utc) - timedelta(minutes=3)).isoformat()
    elif failure == "no-history": snapshot["telemetry"]["uptime_history"] = []
    elif failure == "no-storage": storage.xrevrange.return_value = []
    elif failure == "wrong-history": snapshot["telemetry"]["uptime_history"][0]["uptime"] = 99.9
    with pytest.raises(ValueError):
        verify.verify_snapshot(snapshot, storage)
