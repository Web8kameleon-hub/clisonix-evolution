"""Status probes and persistence; fixtures are test-only, never runtime data."""
import asyncio
import importlib.util
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


SOURCE = Path(__file__).resolve().parents[2] / "apps/api/unified_status_layer.py"
spec = importlib.util.spec_from_file_location("status_telemetry_under_test", SOURCE)
status = importlib.util.module_from_spec(spec)
spec.loader.exec_module(status)


def test_registry_uses_live_core_and_balancer_contracts():
    urls = []

    async def fetch(url):
        urls.append(url)
        return httpx.Response(200)

    with patch.object(status.os.path, "exists", return_value=True), patch("httpx.AsyncClient") as client:
        client.return_value.__aenter__.return_value.get = fetch
        rows = asyncio.run(status._check_all_services())
    assert urls[2] == "http://clisonix-ocean-core:8030/health"
    assert urls[5] == "http://balancer:8091/health"
    assert {row["name"] for row in rows} == {"api", "web", "core", "excel", "marketplace", "balancer"}
    assert all(row["healthy"] and row["latency_ms"] >= 0 and row["observed_at"] for row in rows)


def test_failed_probe_is_not_classified_as_operational():
    async def fetch(url):
        if "balancer" in url:
            raise httpx.ConnectError("DNS failed")
        return httpx.Response(200)

    with patch.object(status.os.path, "exists", return_value=True), patch("httpx.AsyncClient") as client:
        client.return_value.__aenter__.return_value.get = fetch
        rows = asyncio.run(status._check_all_services())
    balancer = next(row for row in rows if row["name"] == "balancer")
    assert balancer["healthy"] is False
    assert "latency_ms" not in balancer
    assert len([row for row in rows if row["healthy"]]) == 5


def test_missing_storage_does_not_invent_history(monkeypatch):
    monkeypatch.delenv("REDIS_URL", raising=False)
    result = asyncio.run(status._record_status_telemetry([], datetime.now(timezone.utc).isoformat()))
    assert result["status"] == "unavailable"
    assert result["uptime_history"] == []
    assert result["last_sample_at"] is None


def test_storage_outage_does_not_invent_history(monkeypatch):
    monkeypatch.setenv("REDIS_URL", "redis://127.0.0.1:1/0")
    result = asyncio.run(status._record_status_telemetry(
        [{"name": "core", "healthy": True}], datetime.now(timezone.utc).isoformat()))
    assert result["status"] == "unavailable"
    assert result["reason"] in {"ConnectionError", "TimeoutError"}
    assert result["uptime_history"] == []
    assert result["last_sample_at"] is None


def test_http_error_keeps_measured_latency_without_success():
    async def fetch(url):
        return httpx.Response(503 if "balancer" in url else 200)

    with patch.object(status.os.path, "exists", return_value=True), patch("httpx.AsyncClient") as client:
        client.return_value.__aenter__.return_value.get = fetch
        rows = asyncio.run(status._check_all_services())
    balancer = next(row for row in rows if row["name"] == "balancer")
    assert balancer["healthy"] is False
    assert balancer["status_code"] == 503
    assert balancer["latency_ms"] >= 0


@pytest.mark.parametrize("offset", [-121, 6])
def test_out_of_window_samples_are_rejected(monkeypatch, offset):
    monkeypatch.setenv("REDIS_URL", "redis://127.0.0.1:1/0")
    timestamp = (datetime.now(timezone.utc) + timedelta(seconds=offset)).isoformat()
    result = asyncio.run(status._record_status_telemetry([{"name": "core", "healthy": True}], timestamp))
    assert result["status"] == "unavailable"
    assert result["reason"] == "ValueError"
    assert result["uptime_history"] == []


def test_cache_hits_do_not_create_telemetry_samples(monkeypatch):
    status.status_cache.invalidate()
    record = AsyncMock(return_value={"status": "unavailable", "uptime_history": []})
    monkeypatch.setattr(status, "_record_status_telemetry", record)
    monkeypatch.setattr(status, "_check_all_services", AsyncMock(return_value=[{"name": "core", "healthy": True}]))
    app = FastAPI()
    app.include_router(status.unified_router)
    with TestClient(app) as client:
        assert client.get("/api/system/health").status_code == 200
        assert client.get("/api/system/health").headers["x-cache"] == "HIT"
    record.assert_awaited_once()
    status.status_cache.invalidate()


@pytest.mark.skipif(os.environ.get("STATUS_TELEMETRY_INTEGRATION") != "1", reason="requires real service probes and isolated Redis")
def test_real_probes_are_persisted_and_returned_through_status_api():
    import redis

    store = redis.Redis.from_url(os.environ["REDIS_URL"], decode_responses=True)
    before = store.xlen("clisonix:system:health:samples")
    status.status_cache.invalidate()
    app = FastAPI()
    app.include_router(status.unified_router)
    # Include production's outer cache so both cache layers are exercised.
    app.add_middleware(status.CachingMiddleware)
    with TestClient(app) as client:
        response = client.get("/api/system/health")
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "operational", payload["services"]
        assert len(payload["services"]) == 6
        assert all(row["healthy"] and isinstance(row["latency_ms"], (float, int)) for row in payload["services"])
        telemetry = payload["telemetry"]
        assert telemetry["status"] == "recorded", telemetry
        assert telemetry["last_sample_at"] == payload["timestamp"]
        assert telemetry["uptime_history"]
        assert all(month["samples"] > 0 for month in telemetry["uptime_history"])
        assert client.get("/api/system/health").json()["timestamp"] == payload["timestamp"]
    assert store.xlen("clisonix:system:health:samples") == before + 1
    record = store.xrevrange("clisonix:system:health:samples", count=1)[0][1]
    assert json.loads(record["services"]) == payload["services"]
    # Recreate the API owner: history survives its in-memory cache lifecycle.
    reloaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reloaded)
    app = FastAPI()
    app.include_router(reloaded.unified_router)
    with TestClient(app) as client:
        next_payload = client.get("/api/system/health").json()
    assert next_payload["telemetry"]["uptime_history"][-1]["samples"] == telemetry["uptime_history"][-1]["samples"] + 1
    print("LIVE_STATUS_EVIDENCE=" + json.dumps(payload))
    store.close()
    status.status_cache.invalidate()
