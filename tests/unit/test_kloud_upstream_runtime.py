import importlib.util
import os
import uuid
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
RUNTIME_MAIN = ROOT / "services" / "kloud_upstream_runtime" / "main.py"


def load_runtime_module(state_path: Path):
    os.environ["KLOUD_RUNTIME_STATE_PATH"] = str(state_path)
    module_name = f"kloud_upstream_runtime_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(module_name, RUNTIME_MAIN)
    assert spec and spec.loader, f"Missing runtime module at {RUNTIME_MAIN}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_runtime_status_registers_real_nodes_and_submits(tmp_path):
    module = load_runtime_module(tmp_path / "runtime-state.json")
    client = TestClient(module.app)

    before = client.get("/status")
    assert before.status_code == 200
    before_payload = before.json()
    assert before_payload["status"] == "ok"
    assert before_payload["sync"] == "waiting"

    register = client.post(
        "/nodes/register",
        json={
            "node_id": "aiagi-node-01",
            "role": "coordinator",
            "region": "eu-central",
            "capabilities": ["reasoning", "mesh-routing"],
        },
    )
    assert register.status_code == 200
    assert register.json()["node"]["node_id"] == "aiagi-node-01"

    heartbeat = client.post(
        "/nodes/heartbeat",
        json={
            "node_id": "aiagi-node-01",
            "status": "online",
            "latency_ms": 12.5,
            "load": 0.21,
        },
    )
    assert heartbeat.status_code == 200
    assert heartbeat.json()["node"]["status"] == "online"

    submit = client.post(
        "/submit",
        json={
            "source": "kloud-bridge",
            "ops": ["sync", "route"],
            "payload": {"topic": "real-runtime-check"},
        },
    )
    assert submit.status_code == 200
    submit_payload = submit.json()
    assert submit_payload["accepted"] is True
    assert submit_payload["status"] == "queued"

    after = client.get("/status")
    assert after.status_code == 200
    after_payload = after.json()
    assert after_payload["sync"] == "ready"
    assert after_payload["received_submit_count"] == 1
    assert after_payload["registered_node_count"] >= 1


def test_runtime_peers_and_state_surface_real_registry(tmp_path):
    module = load_runtime_module(tmp_path / "runtime-state.json")
    client = TestClient(module.app)

    client.post(
        "/nodes/register",
        json={
            "node_id": "client-edge-01",
            "role": "edge",
            "region": "field-eu",
            "capabilities": ["capture", "pulse"],
        },
    )
    client.post(
        "/nodes/heartbeat",
        json={
            "node_id": "client-edge-01",
            "status": "online",
            "latency_ms": 18.0,
            "load": 0.34,
        },
    )

    peers = client.get("/peers")
    assert peers.status_code == 200
    peers_payload = peers.json()
    assert peers_payload["count"] >= 1
    assert any(peer["id"] == "client-edge-01" for peer in peers_payload["peers"])

    state = client.get("/state")
    assert state.status_code == 200
    state_payload = state.json()
    assert state_payload["registered_node_count"] >= 1
    assert state_payload["proof_of_life"] is True
