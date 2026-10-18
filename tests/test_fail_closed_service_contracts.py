import importlib

from fastapi.testclient import TestClient


UNREACHABLE_URL = "http://127.0.0.1:1"


def test_alda_rejects_requests_without_capacity_configuration(monkeypatch):
    monkeypatch.delenv("ALDA_LABS_JSON", raising=False)
    import alda_server

    module = importlib.reload(alda_server)
    client = TestClient(module.app)

    assert client.get("/health").status_code == 503
    assert client.get("/api/v1/queue").status_code == 503


def test_blerina_health_requires_ollama(monkeypatch):
    from services.blerina import main

    monkeypatch.setattr(main, "OLLAMA_HOST", UNREACHABLE_URL)

    assert TestClient(main.app).get("/health").status_code == 503


def test_alba_idle_health_requires_ocean(monkeypatch):
    import alba_idle_chat

    monkeypatch.setattr(alba_idle_chat, "OCEAN_CORE_URL", UNREACHABLE_URL)

    assert TestClient(alba_idle_chat.app).get("/health").status_code == 503


def test_asi_health_requires_all_core_dependencies(monkeypatch):
    import asi_api_server

    for variable in ("ALBA_URL", "ALBI_URL", "JONA_URL"):
        monkeypatch.setenv(variable, UNREACHABLE_URL)

    assert TestClient(asi_api_server.app).get("/health").status_code == 503
