import gzip
import json
import math

from fastapi.testclient import TestClient

import albi_user_api


def _start_session(client: TestClient) -> str:
    response = client.post("/session/start?session_name=ingest-test")
    assert response.status_code == 200
    return response.json()["session_id"]


def _alpha_frames(count: int = 256, sample_rate: int = 128):
    return [
        {
            "timestamp": 1_700_000_000 + index / sample_rate,
            "sample_rate": sample_rate,
            "channels": {
                "Fp1": 20 * math.sin(2 * math.pi * 10 * index / sample_rate),
                "Fp2": 18 * math.sin(2 * math.pi * 10 * index / sample_rate),
            },
        }
        for index in range(count)
    ]


def _reset_state(tmp_path, monkeypatch):
    albi_user_api.sessions.clear()
    albi_user_api.session_locks.clear()
    albi_user_api.active_websockets.clear()
    albi_user_api.ingest_jobs.clear()
    monkeypatch.setattr(albi_user_api, "ALBI_INGEST_DIR", tmp_path)


def test_json_dump_produces_real_alpha_metrics(tmp_path, monkeypatch):
    _reset_state(tmp_path, monkeypatch)
    client = TestClient(albi_user_api.app)
    session_id = _start_session(client)

    upload = client.post(
        f"/session/{session_id}/bulk?format=json",
        content=json.dumps(_alpha_frames()),
        headers={"content-type": "application/json"},
    )

    assert upload.status_code == 202
    job_id = upload.json()["job_id"]
    result = client.get(f"/session/{session_id}/ingest/{job_id}/result")
    metrics = client.get(f"/session/{session_id}/metrics")

    assert result.status_code == 200
    assert result.json()["accepted_frames"] == 256
    assert metrics.status_code == 200
    assert metrics.json()["dominant_band"] == "alpha"
    assert metrics.json()["samples_received"] == 256


def test_gzip_ndjson_supports_nested_device_fields_and_channel_arrays(tmp_path, monkeypatch):
    _reset_state(tmp_path, monkeypatch)
    client = TestClient(albi_user_api.app)
    session_id = _start_session(client)
    rows = [
        {
            "device": {"captured_at": frame["timestamp"], "values": list(frame["channels"].values())}
        }
        for frame in _alpha_frames(64)
    ]
    body = gzip.compress("\n".join(json.dumps(row) for row in rows).encode())
    query = (
        "format=ndjson&timestamp_field=device.captured_at&channels_field=device.values"
        "&sample_rate=128&channel_names=Fp1,Fp2"
    )

    upload = client.post(
        f"/session/{session_id}/bulk?{query}",
        content=body,
        headers={"content-type": "application/x-ndjson", "content-encoding": "gzip"},
    )
    job = client.get(
        f"/session/{session_id}/ingest/{upload.json()['job_id']}"
    ).json()

    assert upload.status_code == 202
    assert job["status"] == "completed"
    assert job["accepted_frames"] == 64
    assert job["rejected_frames"] == 0


def test_wrapped_json_reports_observed_artifact_quality_loss(tmp_path, monkeypatch):
    _reset_state(tmp_path, monkeypatch)
    client = TestClient(albi_user_api.app)
    session_id = _start_session(client)
    frames = _alpha_frames(64)
    frames[12]["channels"]["Fp1"] = albi_user_api.ALBI_ARTIFACT_UV_THRESHOLD + 1

    upload = client.post(
        f"/session/{session_id}/bulk?format=json",
        content=json.dumps({"frames": frames}),
        headers={"content-type": "application/json"},
    )
    metrics = client.get(f"/session/{session_id}/metrics")

    assert upload.status_code == 202
    assert metrics.status_code == 200
    assert metrics.json()["anomalies_detected"] == 1
    assert metrics.json()["quality_score"] < 100


def test_bulk_endpoint_rejects_payload_above_configured_limit(tmp_path, monkeypatch):
    _reset_state(tmp_path, monkeypatch)
    monkeypatch.setattr(albi_user_api, "ALBI_MAX_INGEST_BYTES", 10)
    client = TestClient(albi_user_api.app)
    session_id = _start_session(client)

    response = client.post(
        f"/session/{session_id}/bulk",
        content=b'[{"timestamp":1}]',
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 413
    assert not list(tmp_path.iterdir())
