from fastapi.testclient import TestClient

from apps.api.master import app


client = TestClient(app)


def _valid_event() -> dict:
    return {
        "event_id": "7f7b5d2f-b2d1-4f96-9ac9-6d6f8e59bb31",
        "event_type": "clx.llm.request",
        "timestamp": "2026-05-27T10:00:00Z",
        "trace": {
            "trace_id": "trace-001",
            "span_id": "span-001",
            "correlation_id": "corr-001",
        },
        "delivery": {
            "retry_count": 0,
            "max_retries": 3,
            "ttl_ms": 10000,
            "delivery_mode": "at-least-once",
        },
        "payload_version": "v1",
        "payload_schema": "clx.llm.request.v1",
        "payload": {"query": "hello"},
        "metadata": {
            "source_service": "wwwmmm-gateway",
            "target_service": "ai-execution-core",
            "priority": "normal",
            "auth_context": {"token_type": "service", "scopes": ["events.write"]},
        },
    }


def test_ingest_rejects_invalid_event() -> None:
    bad = {"event_id": "x"}
    response = client.post("/v1/events/ingest", json=bad)
    assert response.status_code == 422
    assert response.json()["error"] == "invalid_clx_event"


def test_ingest_accepts_valid_event() -> None:
    response = client.post("/v1/events/ingest", json=_valid_event())
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["trace_id"] == "trace-001"
    assert body["correlation_id"] == "corr-001"
