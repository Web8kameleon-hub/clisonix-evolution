from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OCEAN_CORE_DIR = ROOT / "ocean-core"
if str(OCEAN_CORE_DIR) not in sys.path:
    sys.path.insert(0, str(OCEAN_CORE_DIR))

from chat_latency_policy import (  # type: ignore
    clamp_specialized_tokens,
    resolve_specialized_timeout_seconds,
)


def test_specialized_tokens_default_to_brief_budget() -> None:
    assert clamp_specialized_tokens(None, long_response=False) == 384
    assert clamp_specialized_tokens(4096, long_response=False) <= 768


def test_specialized_long_response_budget_is_bounded() -> None:
    assert clamp_specialized_tokens(None, long_response=True) == 768
    assert clamp_specialized_tokens(5000, long_response=True) <= 1536


def test_specialized_timeout_stays_interactive() -> None:
    short_timeout = resolve_specialized_timeout_seconds(120, long_response=False)
    long_timeout = resolve_specialized_timeout_seconds(6000, long_response=True)

    assert short_timeout <= 12.0
    assert long_timeout <= 30.0
    assert long_timeout > short_timeout
