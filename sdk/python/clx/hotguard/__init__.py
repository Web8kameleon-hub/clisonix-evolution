"""
Hotguard: Scanner-Printer Stream + Stigma Profiles + NO_FAKE_DATA Validator

Core modules for CLX AI 2-minute hotguard package.
"""

from .no_fake_data_validator import NoFakeDataValidator, validate_no_fake_data
from .scanner_printer import ScannerPrinterStream, resonance_to_decibel, resonance_to_nanodecibel
from .stigma_profiles import STIGMA_PROFILES, StigmaProfile, get_profile_for_resonance

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
