"""
STIGMA FLUID - Lightweight Stigma Data Generator (NodeDB-style)
================================================================
Creates minimal resonance/stigma metadata on-the-fly without heavy DB ops.
Complies with wwwmmm + nanodecibel + firewall semantics.

Features:
- Single-pass aggregation (no re-queries)
- Fluid JSON (grows on-demand)
- Deterministic from message hash
- NDB compliance
"""

import hashlib
import time
from typing import Any, Dict, Optional


class StigmaFluidGenerator:
    """Generate lightweight stigma metadata from request context."""

    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl_sec = 60

    def _hash_key(self, message: str, user_id: Optional[str] = None) -> str:
        """Generate cache key from message hash."""
        sig = hashlib.md5(f"{message}:{user_id}".encode()).hexdigest()
        return sig[:12]

    def _is_cached_fresh(self, key: str) -> bool:
        """Check if cache entry is still valid."""
        if key not in self.cache:
            return False
        cached = self.cache[key]
        age_sec = time.time() - cached.get("_ts", 0)
        return age_sec < self.cache_ttl_sec

    def generate(
        self,
        message: str,
        user_id: Optional[str] = None,
        language: Optional[str] = None,
        mode: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate minimal stigma profile.

        Returns:
        --------
        {
            "stigma_profile": "lightning" | "normal" | "conservative",
            "firewall_action": "allow" | "monitor" | "throttle",
            "resonance_ndb": <nanodecibel int>,
            "confidence": 0.0-1.0,
            "source": "fluid_node"
        }
        """
        key = self._hash_key(message, user_id)

        # Fast-path: cache hit
        if self._is_cached_fresh(key):
            return self.cache[key].copy()

        # Compute lightweight signals
        msg_len = len(message.strip())
        has_question = "?" in message

        # Determine profile from message length + language
        if msg_len < 15:
            profile = "conservative"
        elif msg_len < 50:
            profile = "normal"
        else:
            profile = "lightning"

        # Language-based resonance bias
        lang_bias = 0.0
        if language == "sq":
            lang_bias = 0.15  # Albanian conversational boost
        elif language in ["en", "de", "fr"]:
            lang_bias = 0.05

        # Mode-based resonance
        mode_bias = 0.0
        if mode == "creative":
            mode_bias = 0.2
        elif mode == "analytical":
            mode_bias = 0.1

        # Base resonance score (0-1 range)
        base_resonance = 0.5 + lang_bias + mode_bias
        base_resonance = min(1.0, max(0.0, base_resonance))

        # Convert to nanodecibel (10^9 scale, logarithmic)
        # Formula: resonance_ndb = round(log10(resonance + 1e-10) * 1_000_000_000)
        ndb_value = int(
            (10 * (base_resonance * 10)) * 1_000_000_000
        ) if base_resonance > 0 else -1_000_000_000

        # Firewall action (conservative on short, aggressive on long)
        if profile == "lightning":
            fw_action = "allow"
        elif profile == "normal":
            fw_action = "allow" if not has_question else "monitor"
        else:
            fw_action = "monitor"

        # Minimal confidence score
        confidence = 0.85 + (0.15 * (msg_len / 200.0))
        confidence = min(1.0, confidence)

        result = {
            "stigma_profile": profile,
            "firewall_action": fw_action,
            "resonance_ndb": ndb_value,
            "confidence": round(confidence, 2),
            "source": "fluid_node",
            "_ts": time.time(),
        }

        # Cache for TTL
        self.cache[key] = result

        return {k: v for k, v in result.items() if not k.startswith("_")}


# Singleton instance
_stigma_gen = StigmaFluidGenerator()


def get_stigma_profile(
    message: str,
    user_id: Optional[str] = None,
    language: Optional[str] = None,
    mode: Optional[str] = None,
) -> Dict[str, Any]:
    """Lightweight stigma metadata (fluid, no-DB)."""
    return _stigma_gen.generate(message, user_id, language, mode)


def stigma_sse_event(meta: Dict[str, Any]) -> str:
    """Format stigma metadata as SSE event."""
    import json
    return f"data: {json.dumps({'phase': 'security', **meta})}\n\n"
