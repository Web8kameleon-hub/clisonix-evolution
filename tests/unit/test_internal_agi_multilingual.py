from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INTERNAL_AGI_DIR = ROOT / "services" / "internal_agi"
if str(INTERNAL_AGI_DIR) not in sys.path:
    sys.path.insert(0, str(INTERNAL_AGI_DIR))

from knowledge_router import KnowledgeRouter, QueryIntent  # type: ignore  # noqa: E402
from reasoning_engine import (  # type: ignore  # noqa: E402
    ReasoningContext,
    ReasoningEngine,
)


def test_router_detects_multilingual_explain_intent() -> None:
    router = KnowledgeRouter()

    sq_intent = router.parse_query("Cili është kryeqyteti i Gjermanisë?")
    ar_intent = router.parse_query("ما هي عاصمة ألمانيا؟")

    assert sq_intent.intent_type == QueryIntent.EXPLAIN
    assert ar_intent.intent_type == QueryIntent.EXPLAIN
    assert "germany" in sq_intent.countries
    assert "germany" in ar_intent.countries


def test_reasoning_engine_formats_multilingual_capital_answers() -> None:
    engine = ReasoningEngine()

    sq_context = ReasoningContext(
        query="Cili është kryeqyteti i Gjermanisë?",
        intent=None,
        sources=["global_data_sources"],
        data={},
    )
    sq_result = asyncio.run(engine.reason(sq_context))

    ar_context = ReasoningContext(
        query="ما هي عاصمة ألمانيا؟",
        intent=None,
        sources=["global_data_sources"],
        data={},
    )
    ar_result = asyncio.run(engine.reason(ar_context))

    assert sq_result.answer.startswith("Kryeqyteti i")
    assert "gjerman" in sq_result.answer.lower()
    assert ar_result.answer.startswith("عاصمة")
    assert "ألمانيا" in ar_result.answer


def test_reasoning_engine_formats_multilingual_government_and_statistics_answers() -> None:
    engine = ReasoningEngine()

    president_result = asyncio.run(
        engine.reason(
            ReasoningContext(
                query="Cili është presidenti i Gjermanisë?",
                intent=None,
                sources=["global_data_sources"],
                data={},
            )
        )
    )
    population_result = asyncio.run(
        engine.reason(
            ReasoningContext(
                query="ما هو عدد سكان ألمانيا؟",
                intent=None,
                sources=["global_data_sources"],
                data={},
            )
        )
    )
    gdp_result = asyncio.run(
        engine.reason(
            ReasoningContext(
                query="What is the GDP of Germany?",
                intent=None,
                sources=["global_data_sources"],
                data={},
            )
        )
    )

    assert president_result.answer.startswith("Presidenti aktual i")
    assert "gjerman" in president_result.answer.lower()
    assert population_result.answer.startswith("عدد سكان")
    assert "ألمانيا" in population_result.answer
    assert gdp_result.answer.startswith("The GDP of")
    assert "germany" in gdp_result.answer.lower()
