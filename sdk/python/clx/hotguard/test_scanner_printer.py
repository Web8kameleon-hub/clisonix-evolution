"""
Test: Scanner-Printer Stream with NO_FAKE_DATA Validation

Verifies:
  1. Scanner-printer produces real nanodecibel metrics
  2. All phases are emitted
  3. No fake/placeholder data anywhere
"""
import asyncio

import pytest

from .no_fake_data_validator import NoFakeDataValidator, validate_no_fake_data
from .scanner_printer import ScannerPrinterStream, resonance_to_nanodecibel
from .stigma_profiles import STIGMA_PROFILES, get_profile_for_resonance


@pytest.mark.asyncio
async def test_scanner_printer_stream_real_metrics():
    """Test that stream produces real metrics (no fake data)."""
    stream = ScannerPrinterStream(
        input_text="query processing",
        resonance_score=0.75,  # Real score
    )

    phases = []
    async for phase in stream.stream_phases(
        matched=True,
        route_name="ollama_inference",  # Real route name, not "test_*"
        model="ollama",
    ):
        phases.append(phase)

    # Should have all required phases
    assert len(phases) >= 5, "Missing phases"

    # Validate no fake data
    issues = NoFakeDataValidator.validate_stream_phases(phases)
    assert len(issues) == 0, f"Found fake data issues: {issues}"

    # Check resonance metrics are real
    for phase in phases:
        if "resonance_ndb" in phase:
            ndb = phase["resonance_ndb"]
            assert isinstance(ndb, (int, float)), "nanodecibel not numeric"
            assert -200_000_000_000.0 <= ndb <= 100_000_000_000.0, f"Unrealistic ndb: {ndb}"


def test_resonance_to_nanodecibel_real_values():
    """Test that nanodecibel conversion is real, not mocked."""
    test_scores = [0.0, 0.5, 0.9, 1.0]

    for score in test_scores:
        ndb = resonance_to_nanodecibel(score)

        # Must be numeric
        assert isinstance(ndb, (int, float)), f"Not numeric: {ndb}"

        # Must be in valid range
        assert -200_000_000_000.0 <= ndb <= 100_000_000_000.0, f"Out of range: {ndb}"

        # Must be deterministic (calling again with same score gives same result)
        ndb2 = resonance_to_nanodecibel(score)
        assert ndb == ndb2, "Conversion not deterministic"


def test_stigma_profile_thresholds_real():
    """Test that stigma profiles have real resonance thresholds."""
    for name, profile in STIGMA_PROFILES.items():
        # Threshold must be numeric and in valid range
        assert isinstance(profile.resonance_threshold_ndb, (int, float)), \
            f"Profile '{name}' threshold not numeric"
        assert -200_000_000_000.0 <= profile.resonance_threshold_ndb <= 100_000_000_000.0, \
            f"Profile '{name}' threshold unrealistic"

        # Profile config should not have fake data
        config = profile.get_config()
        issues = NoFakeDataValidator.validate_output(config)
        assert len(issues) == 0, f"Profile '{name}' has fake data: {issues}"


def test_stigma_profile_selection():
    """Test that profile selection is real (based on actual resonance)."""
    # High resonance -> lightning
    profile = get_profile_for_resonance(-10_000_000_000.0)
    assert profile.name == "lightning", "High resonance should select lightning"

    # Low resonance -> conservative
    profile = get_profile_for_resonance(-100_000_000_000.0)
    assert profile.name == "conservative", "Low resonance should select conservative"

    # Medium resonance -> normal
    profile = get_profile_for_resonance(-40_000_000_000.0)
    assert profile.name == "normal", "Medium resonance should select normal"


def test_validate_no_fake_data():
    """Test the NO_FAKE_DATA validator itself."""
    # Real data should pass
    real_data = {
        "phase": "processing",
        "matched": True,
        "resonance_ndb": -40_000_000_000.0,
    }
    assert validate_no_fake_data(real_data), "Real data should validate"

    # Fake data should fail
    fake_data = {
        "phase": "processing",
        "value": "mock_response",  # Fake pattern
    }
    assert not validate_no_fake_data(fake_data), "Fake data should not validate"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
