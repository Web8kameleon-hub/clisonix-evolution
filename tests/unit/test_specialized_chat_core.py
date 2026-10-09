import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OCEAN_CORE_DIR = ROOT / "ocean-core"
if str(OCEAN_CORE_DIR) not in sys.path:
    sys.path.insert(0, str(OCEAN_CORE_DIR))

from specialized_chat_engine import SpecializedChatEngine
from specialized_expert_core import SpecializedExpertCore


def test_specialized_core_normalizes_domain_aliases():
    core = SpecializedExpertCore()
    known = SpecializedChatEngine.EXPERTISE_DOMAINS

    assert core.normalize_domain("ai", known) == "ai_ml"
    assert core.normalize_domain("neuro", known) == "neuroscience"
    assert core.normalize_domain("bio", known) == "biotech"
    assert core.normalize_domain("data", known) == "data_science"
    assert core.normalize_domain("unknown-domain", known) is None


def test_specialized_engine_returns_response_alias():
    engine = SpecializedChatEngine()

    result = asyncio.run(
        engine.generate_expert_response(
            "Explain neural network overfitting briefly.",
            domain="ai",
        )
    )

    assert result["domain"] == "ai_ml"
    assert isinstance(result.get("answer"), str) and result["answer"].strip()
    assert result.get("response") == result.get("answer")
