from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
SERVICE_DIR = ROOT / "services" / "curiosity_ocean"
if str(SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(SERVICE_DIR))

from api import AskRequest, CuriosityOceanAPI, create_app  # type: ignore  # noqa: E402


def test_fallback_ask_localizes_arabic_answer() -> None:
    api = CuriosityOceanAPI()
    request = AskRequest(query="مرحبا كيف حالك؟", language="ar", max_sources=2)
    response = asyncio.run(api._fallback_ask(request, "qid", api_datetime_now()))
    assert "يقوم Curiosity Ocean" in response.answer
    assert "مرحبا كيف حالك؟" in response.answer


def test_search_links_uses_public_data_source_api() -> None:
    api = CuriosityOceanAPI()
    response = asyncio.run(api.search_links(api_search_request()))
    assert response.total >= 0
    assert response.measurement_unit == "nanodecibel"
    assert any("Provo" in suggestion for suggestion in response.suggestions)


def test_open_data_resolves_region_string() -> None:
    api = CuriosityOceanAPI()
    response = asyncio.run(api.get_open_data(api_open_data_request()))
    assert response.region == "europe"
    assert "filter" in response.metadata


def test_ask_endpoint_returns_multilingual_rule_based_answers_with_threshold() -> None:
    client = TestClient(create_app())
    cases = [
        ("What is the capital of Germany?", "The capital of", 0.60),
        ("Cili është kryeqyteti i Gjermanisë?", "Kryeqyteti i", 0.60),
        ("ما هي عاصمة ألمانيا؟", "عاصمة", 0.60),
    ]

    for query, prefix, min_confidence in cases:
        response = client.post(
            "/ask",
            json={"query": query, "max_sources": 3, "include_reasoning": True},
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["answer"].startswith(prefix)
        assert payload["confidence"] >= min_confidence
        assert payload["measurement_unit"] == "nanodecibel"


def api_datetime_now():
    from datetime import datetime

    return datetime.now()


def api_search_request():
    from api import SearchRequest  # type: ignore

    return SearchRequest(query="university", api_only=False, limit=3, language="sq")


def api_open_data_request():
    from api import OpenDataRequest  # type: ignore

    return OpenDataRequest(region="europe", language="sq")


def test_ask_falls_back_fast_on_context_timeout(monkeypatch) -> None:
    api = CuriosityOceanAPI()

    class _RouteDecision:
        primary_sources = ["europe_sources"]
        secondary_sources = []

        def to_dict(self):
            return {"primary_sources": self.primary_sources, "secondary_sources": self.secondary_sources}

    class _Router:
        def route(self, query):
            return _RouteDecision()

        def parse_query(self, query):
            class _Intent:
                def to_dict(self):
                    return {"query": query}

            return _Intent()

    class _SlowContextBuilder:
        async def build_context(self, **kwargs):
            await asyncio.sleep(0.05)
            return None

    api.knowledge_router = _Router()
    api.context_builder = _SlowContextBuilder()

    monkeypatch.setattr("api.ASK_CONTEXT_TIMEOUT_SECONDS", 0.01)

    request = AskRequest(query="What is the capital of Germany?", language="en", max_sources=2)
    response = asyncio.run(api.ask(request))
    assert response.answer == "The capital of Germany is Berlin."
    assert response.processing_time_ms < 1000
