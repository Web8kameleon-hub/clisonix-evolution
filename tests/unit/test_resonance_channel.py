from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OCEAN_CORE_DIR = ROOT / "ocean-core"
if str(OCEAN_CORE_DIR) not in sys.path:
    sys.path.insert(0, str(OCEAN_CORE_DIR))

from resonance_channel import ResonanceChannel, ResonanceSample  # type: ignore


def test_resonance_roundtrip_for_symbol_a() -> None:
    channel = ResonanceChannel(ResonanceChannel.default_alphabet())
    packet = channel.encode_symbol("A", observed_latency_seconds=0.0000001, nano_shift_ns=0.2)

    result = channel.decode_packet(packet)

    assert result.symbol == "A"
    assert result.confidence >= 0.82


def test_w_m_are_not_identical_deformation_stays_positive() -> None:
    channel = ResonanceChannel(ResonanceChannel.default_alphabet())
    packet = channel.encode_symbol("X", observed_latency_seconds=0.0000001)
    shifted = packet.w_sample.with_nano_shift(0.35)

    result = channel.decode_sample(shifted, observed_latency_seconds=packet.observed_latency_seconds)

    assert result.symbol == "X"
    assert result.deformation > 0.0


def test_low_confidence_profile_is_rejected() -> None:
    channel = ResonanceChannel(ResonanceChannel.default_alphabet(), min_confidence=0.95)
    unknown_profile = ResonanceSample(
        amplitude=[0.05, 0.04, 0.03, 0.02],
        phase=[0.95, 0.92, 0.91, 0.89],
        frequency=[0.10, 0.12, 0.09, 0.08],
        jitter_ns=[90.0, 110.0, 105.0, 115.0],
    )

    result = channel.decode_sample(unknown_profile, observed_latency_seconds=0.0003)

    assert result.symbol is None
    assert result.confidence < 0.95
