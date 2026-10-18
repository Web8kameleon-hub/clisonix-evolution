import asyncio
import io
import sys
from pathlib import Path
from zipfile import ZipFile

import httpx
import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps" / "api"))
import runtime_compat_routes as compat
from main import app

SERVER_ONLY_PATHS = {
    "/api", "/api/health", "/api/status", "/api/query", "/api/zurich",
    "/api/asi/alba/metrics", "/api/asi/albi/metrics", "/api/asi/jona/metrics",
    "/api/asi/status", "/api/asi/health", "/api/asi/{service_name}/health",
    "/api/system/health", "/api/system/cache/stats", "/api/system/cache/invalidate",
    "/api/system/errors", "/api/proxy/marketplace-health",
    "/api/proxy/reporting-dashboard", "/api/proxy/reporting-errors",
    "/api/proxy/reporting-error-summary", "/api/reporting/metrics",
    "/api/reporting/alerts", "/api/reporting/docker-stats", "/api/reporting/export",
    "/api/reporting/export-pdf", "/api/reporting/export-docx", "/neural-symphony",
}


def transport(monkeypatch, handler):
    original = httpx.AsyncClient
    backend = httpx.MockTransport(handler)
    monkeypatch.setattr(compat.httpx, "AsyncClient",
                        lambda **kwargs: original(transport=backend, **kwargs))


def test_preserves_every_observed_server_path():
    assert SERVER_ONLY_PATHS <= app.openapi()["paths"].keys()


def test_status_alias_reads_system_metrics():
    with TestClient(app) as client:
        response = client.get("/api/status")
    assert response.status_code == 200


def test_gateway_preserves_request_and_upstream_error(monkeypatch):
    seen = []
    def backend(request):
        seen.append(request)
        return httpx.Response(409, json={"error": "conflict"})
    transport(monkeypatch, backend)
    monkeypatch.setenv("OCEAN_INTERNAL_URL", "http://ocean.test")
    with TestClient(app) as client:
        response = client.post("/api/query?mode=deep", json={"query": "test"},
                               headers={"Authorization": "Bearer test-only"})
    assert response.status_code == 409
    assert response.json() == {"error": "conflict"}
    assert seen[0].url.path == "/api/v1/chat"
    assert seen[0].url.params["mode"] == "deep"
    assert seen[0].headers["authorization"] == "Bearer test-only"
    assert b'"query":"test"' in seen[0].content


def test_unreachable_dependency_is_not_reported_healthy(monkeypatch):
    def unavailable(request):
        raise httpx.ConnectError("offline", request=request)
    transport(monkeypatch, unavailable)
    monkeypatch.setenv("ALBA_SERVICE_URL", "http://alba.test")
    with TestClient(app) as client:
        response = client.get("/api/asi/health")
    assert response.status_code == 503
    assert response.json()["status"] == "degraded"
    assert all(not row["reachable"] for row in response.json()["services"].values())


def test_missing_alba_configuration_fails_closed(monkeypatch):
    monkeypatch.delenv("ALBA_SERVICE_URL", raising=False)
    monkeypatch.delenv("ALBA_URL", raising=False)
    with TestClient(app) as client:
        response = client.get("/api/asi/alba/metrics")
    assert response.status_code == 503


@pytest.mark.parametrize("format", ["pdf", "docx"])
def test_documents_use_live_upstream_payload(monkeypatch, format):
    def backend(request):
        assert request.url.path == "/api/reporting/dashboard"
        return httpx.Response(200, json={"observed_cpu_percent": 12.75})
    transport(monkeypatch, backend)
    with TestClient(app) as client:
        response = client.get(f"/api/reporting/export?format={format}")
    assert response.status_code == 200
    assert "no-store" in response.headers["cache-control"]
    if format == "pdf":
        assert response.content.startswith(b"%PDF-")
    else:
        with ZipFile(io.BytesIO(response.content)) as document:
            xml = document.read("word/document.xml")
        assert b"observed_cpu_percent" in xml and b"12.75" in xml


def test_document_export_does_not_invent_a_report_on_failure(monkeypatch):
    transport(monkeypatch, lambda request: httpx.Response(503, json={"error": "offline"}))
    with TestClient(app) as client:
        response = client.get("/api/reporting/export-pdf")
    assert response.status_code == 503
    assert response.json() == {"error": "offline"}


@pytest.mark.parametrize("path", ["/neural-symphony", "/neural/neural-symphony"])
def test_synthetic_eeg_is_retired(path):
    with TestClient(app) as client:
        assert client.get(path).status_code == 410
