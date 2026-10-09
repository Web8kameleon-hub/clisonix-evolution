"""
CLX (Clisonix Lightweight eXtensions) - Official Python SDK

Real-time AI inference, streaming, observability.
"""

# Re-export hotguard public API
from .hotguard import (
    STIGMA_PROFILES,
    NoFakeDataValidator,
    ScannerPrinterStream,
    StigmaProfile,
    get_profile_for_resonance,
    resonance_to_decibel,
    resonance_to_nanodecibel,
    validate_no_fake_data,
)

__version__ = "2.1.0"

__all__ = [
    "resonance_to_nanodecibel",
    "resonance_to_decibel",
    "ScannerPrinterStream",
    "StigmaProfile",
    "STIGMA_PROFILES",
    "get_profile_for_resonance",
    "NoFakeDataValidator",
    "validate_no_fake_data",
]
