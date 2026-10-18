"""
CLX Creative media helpers (isolated).

Outputs from this module are synthetic by design and MUST stay outside
NO_FAKE_DATA production endpoints.
"""

from __future__ import annotations

from typing import Any, Dict

from .policy import tagged_payload


def build_creative_brief(prompt: str, style: str = "experimental") -> Dict[str, Any]:
    """Create an isolated creative brief payload with mandatory synthetic tagging."""
    clean_prompt = (prompt or "").strip()
    if not clean_prompt:
        raise ValueError("prompt is required")

    payload = {
        "prompt": clean_prompt,
        "style": style,
        "pipeline": "clx_creative",
    }
    return tagged_payload(payload)
