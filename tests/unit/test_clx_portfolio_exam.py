from pathlib import Path

from fastapi.testclient import TestClient

import clx_i_service as clx_i
from clx_local_domain_wrapper import CLXDomainPromptWrapper


class StubBackend:
    def generate(self, prompt, generation_kwargs):
        assert "SYSTEM:" in prompt
        assert "CONTEXT:" in prompt
        assert generation_kwargs["temp"] <= 0.25
        return "exam-pass"


def _workspace_root() -> str:
    return str(Path(__file__).resolve().parents[2])


def test_clx_exam_question_returns_authoritative_metric_context():
    wrapper = CLXDomainPromptWrapper(workspace_root=_workspace_root(), backend=StubBackend())

    result = wrapper.answer(
        "Provim: shpjego resonance_to_nanodecibel dhe burimin autoritativ.",
        temperature=0.1,
        max_tokens=128,
    )

    assert result["response"] == "exam-pass"
    assert result["error"] is None
    assert "resonance" in result["mapped_terms"]
    assert "nanodecibel" in result["mapped_terms"]
    assert any("scanner_printer.py" in source for source in result["context_sources"])


def test_xcl_exam_question_detects_wwwmmm_and_xlc_terms():
    wrapper = CLXDomainPromptWrapper(workspace_root=_workspace_root(), backend=StubBackend())

    result = wrapper.answer(
        "Provim: cfare roli kane WWWMMM dhe XLC ne resonant reading?",
        temperature=0.1,
        max_tokens=128,
    )

    assert result["response"] == "exam-pass"
    assert result["error"] is None
    assert "wwwmmm" in result["mapped_terms"]
    assert "xlc" in result["mapped_terms"]
    assert result["context_sources"]


def test_clx_i_exam_question_applies_domain_context_to_icon_flow(monkeypatch):
    captured = {}

    async def _fake_call(image_base64: str, prompt: str, stigma_level: int) -> str:
        captured["prompt"] = prompt
        captured["stigma_level"] = stigma_level
        return "exam-icon-pass"

    monkeypatch.setattr(clx_i, "_call_ollama_vision", _fake_call)
    monkeypatch.setattr(clx_i, "_DOMAIN_WRAPPER", None)
    monkeypatch.setattr(clx_i, "_DOMAIN_WRAPPER_READY", False)
    monkeypatch.setattr(clx_i, "_DOMAIN_WRAPPER_ERROR", None)

    client = TestClient(clx_i.app)
    payload = {
        "image_base64": "a" * 128,
        "prompt": "Provim: analizo nje ikon hospitali me kontekst HVO dhe XLC.",
        "stigma_level": 2,
        "mirror_level": 1,
    }
    response = client.post("/api/v1/icons/analyze", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["output"] == "exam-icon-pass"
    assert body["domain_enrichment_applied"] is True
    assert body["domain_context_sources"]
    assert "CLX_DOMAIN_ENRICHMENT" in captured["prompt"]
    assert captured["stigma_level"] == 2
