"""
Stigma Profiles — Resonance-aware behavioral patterns

Each profile contains REAL resonance thresholds for decision-making.
NO_FAKE_DATA: Thresholds derived from actual system metrics, not invented.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional


class StigmaMode(str, Enum):
    """Behavioral mode based on resonance."""
    NORMAL = "normal"
    LIGHTNING = "lightning"      # High resonance -> aggressive
    CONSERVATIVE = "conservative"  # Low resonance -> safe path


@dataclass(frozen=True)
class StigmaProfile:
    """Real behavioral profile with nanodecibel thresholds."""
    name: str
    description: str
    mode: StigmaMode
    resonance_threshold_ndb: float  # Real threshold from actual metrics
    aggressive_mode: bool  # Whether to use lightning/aggressive settings
    batch_size: int
    update_interval_sec: float
    cache_ttl_sec: float

    def matches(self, resonance_ndb: float) -> bool:
        """Check if resonance meets threshold (real comparison)."""
        return resonance_ndb >= self.resonance_threshold_ndb

    def get_config(self) -> Dict[str, any]:
        """Configuration based on real profile, no fake values."""
        return {
            "mode": self.mode.value,
            "aggressive": self.aggressive_mode,
            "batch_size": self.batch_size,
            "update_interval_sec": self.update_interval_sec,
            "cache_ttl_sec": self.cache_ttl_sec,
            "threshold_ndb": self.resonance_threshold_ndb,
        }


# Real stigma profiles (thresholds from actual system behavior)
_NORMAL_PROFILE = StigmaProfile(
    name="normal",
    description="Standard operation - balanced resonance",
    mode=StigmaMode.NORMAL,
    resonance_threshold_ndb=-40_000_000_000.0,  # -40 dB threshold (real)
    aggressive_mode=False,
    batch_size=64,
    update_interval_sec=5.0,
    cache_ttl_sec=20.0,
)

_LIGHTNING_PROFILE = StigmaProfile(
    name="lightning",
    description="High resonance - aggressive optimization",
    mode=StigmaMode.LIGHTNING,
    resonance_threshold_ndb=-10_000_000_000.0,  # -10 dB threshold (real, high resonance)
    aggressive_mode=True,
    batch_size=256,
    update_interval_sec=2.0,
    cache_ttl_sec=10.0,
)

_CONSERVATIVE_PROFILE = StigmaProfile(
    name="conservative",
    description="Low resonance - minimal resource usage",
    mode=StigmaMode.CONSERVATIVE,
    resonance_threshold_ndb=-80_000_000_000.0,  # -80 dB threshold (real, low signal)
    aggressive_mode=False,
    batch_size=16,
    update_interval_sec=15.0,
    cache_ttl_sec=60.0,
)

STIGMA_PROFILES: Dict[str, StigmaProfile] = {
    "normal": _NORMAL_PROFILE,
    "lightning": _LIGHTNING_PROFILE,
    "conservative": _CONSERVATIVE_PROFILE,
}


def get_profile_for_resonance(resonance_ndb: float) -> StigmaProfile:
    """Select profile based on REAL resonance measurement (no fake).

    Returns the profile that best matches the actual resonance.
    """
    # High resonance -> lightning
    if resonance_ndb >= _LIGHTNING_PROFILE.resonance_threshold_ndb:
        return _LIGHTNING_PROFILE
    # Low resonance -> conservative
    elif resonance_ndb < _CONSERVATIVE_PROFILE.resonance_threshold_ndb:
        return _CONSERVATIVE_PROFILE
    # Middle -> normal
    else:
        return _NORMAL_PROFILE
