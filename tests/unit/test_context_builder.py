from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SERVICE_DIR = ROOT / "services" / "internal_agi"
if str(SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(SERVICE_DIR))

from context_builder import ContextBuilder  # type: ignore  # noqa: E402


def test_context_builder_initializes_source_cache_from_public_data_sources() -> None:
    builder = ContextBuilder()
    assert builder.get_stats()["total_sources_cached"] > 0
    assert builder.get_stats()["unique_countries"] > 0
