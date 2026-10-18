"""
CLX Creative isolation policy.

This package is intentionally isolated from NO_FAKE_DATA production flows.
Creative outputs are allowed only when explicitly enabled and must be tagged.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class CreativePolicy:
    enabled: bool
    synthetic_tag: str


def load_policy() -> CreativePolicy:
    enabled = os.getenv("CLX_CREATIVE_ENABLED", "false").strip().lower() in {"1", "true", "yes", "on"}
    synthetic_tag = os.getenv("CLX_CREATIVE_SYNTHETIC_TAG", "creative_synthetic")
    return CreativePolicy(enabled=enabled, synthetic_tag=synthetic_tag)


def enforce_creative_enabled() -> CreativePolicy:
    policy = load_policy()
    if not policy.enabled:
        raise RuntimeError(
            "clx.creative is disabled. Set CLX_CREATIVE_ENABLED=true only in isolated creative environments."
        )
    return policy


def tagged_payload(content: Dict[str, Any]) -> Dict[str, Any]:
    """Attach synthetic metadata to prevent accidental reuse in NO_FAKE_DATA flows."""
    policy = enforce_creative_enabled()
    return {
        "metadata": {
            "classification": policy.synthetic_tag,
            "is_synthetic": True,
            "no_fake_compatible": False,
        },
        "content": content,
    }
