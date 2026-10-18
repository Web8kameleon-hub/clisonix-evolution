from pathlib import Path

from clx_local_domain_wrapper import CLXDomainPromptWrapper


class StubBackend:
    def generate(self, prompt, generation_kwargs):
        assert "SYSTEM:" in prompt
        assert "CONTEXT:" in prompt
        return "stubbed-response"


def _workspace_root() -> str:
    return str(Path(__file__).resolve().parents[2])


def test_map_domain_terms_detects_wwwmmm_xlc_ndb():
    wrapper = CLXDomainPromptWrapper(workspace_root=_workspace_root(), backend=StubBackend())
    mapped = wrapper.map_domain_terms("Explain WWWMMM and XLC nanodecibel conversion")
    assert "wwwmmm" in mapped
    assert "xlc" in mapped
    assert "nanodecibel" in mapped


def test_retrieve_context_returns_authoritative_sources():
    wrapper = CLXDomainPromptWrapper(workspace_root=_workspace_root(), backend=StubBackend())
    chunks = wrapper.retrieve_context("How is resonance_to_nanodecibel calculated?", max_chunks=2)
    assert chunks
    assert any("scanner_printer.py" in chunk.source for chunk in chunks)


def test_answer_uses_backend_and_returns_metadata():
    wrapper = CLXDomainPromptWrapper(workspace_root=_workspace_root(), backend=StubBackend())
    result = wrapper.answer("What is XLC scanner-printer stream?", temperature=0.1, max_tokens=128)
    assert result["response"] == "stubbed-response"
    assert result["error"] is None
    assert isinstance(result["mapped_terms"], dict)
    assert isinstance(result["context_sources"], list)
