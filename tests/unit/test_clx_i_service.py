import json
from pathlib import Path

from fastapi.testclient import TestClient

import clx_i_service as svc


def _min_base64() -> str:
    # Tiny valid-looking payload for request validation only.
    return "a" * 128


def test_health_contains_selflearning_flag(monkeypatch):
    class _Resp:
        status_code = 200

    class _Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, _url):
            return _Resp()

    monkeypatch.setattr(svc.httpx, "AsyncClient", lambda timeout: _Client())

    client = TestClient(svc.app)
    res = client.get("/health")

    assert res.status_code == 200
    body = res.json()
    assert "selflearning_enabled" in body


def test_analyze_icon_writes_mirror_and_selflearning(tmp_path, monkeypatch):
    mirror_file = tmp_path / "mirror.jsonl"
    selflearning_file = tmp_path / "selflearning.jsonl"

    monkeypatch.setattr(svc, "MIRROR_FILE_PATH", mirror_file)
    monkeypatch.setattr(svc, "SELFLEARNING_FILE_PATH", selflearning_file)
    monkeypatch.setattr(svc, "SELFLEARNING_ENABLED", True)

    async def _fake_call(image_base64: str, prompt: str, stigma_level: int) -> str:
        assert image_base64
        assert prompt
        assert stigma_level in {1, 2, 3}
        return "icon-analysis-ok"

    monkeypatch.setattr(svc, "_call_ollama_vision", _fake_call)

    client = TestClient(svc.app)
    payload = {
        "image_base64": _min_base64(),
        "prompt": "Analyze icon quickly",
        "stigma_level": 2,
        "mirror_level": 3,
    }
    res = client.post("/api/v1/icons/analyze", json=payload)

    assert res.status_code == 200
    body = res.json()
    assert body["output"] == "icon-analysis-ok"

    assert mirror_file.exists()
    assert selflearning_file.exists()

    mirror_lines = mirror_file.read_text(encoding="utf-8").splitlines()
    learn_lines = selflearning_file.read_text(encoding="utf-8").splitlines()
    assert mirror_lines
    assert learn_lines

    mirror_event = json.loads(mirror_lines[-1])
    learn_event = json.loads(learn_lines[-1])

    assert mirror_event["level"] == 3
    assert learn_event["learning_signal"] == "success"


def test_analyze_icon_no_selflearning_when_disabled(tmp_path, monkeypatch):
    mirror_file = tmp_path / "mirror.jsonl"
    selflearning_file = tmp_path / "selflearning.jsonl"

    monkeypatch.setattr(svc, "MIRROR_FILE_PATH", mirror_file)
    monkeypatch.setattr(svc, "SELFLEARNING_FILE_PATH", selflearning_file)
    monkeypatch.setattr(svc, "SELFLEARNING_ENABLED", False)

    async def _fake_call(image_base64: str, prompt: str, stigma_level: int) -> str:
        return "ok"

    monkeypatch.setattr(svc, "_call_ollama_vision", _fake_call)

    client = TestClient(svc.app)
    payload = {
        "image_base64": _min_base64(),
        "prompt": "Analyze icon",
        "stigma_level": 1,
        "mirror_level": 1,
    }
    res = client.post("/api/v1/icons/analyze", json=payload)

    assert res.status_code == 200
    assert mirror_file.exists()
    assert not selflearning_file.exists()
