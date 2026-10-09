"""
NO_FAKE_DATA Validator — Ensure all CLX outputs are real, not invented

Policy enforced:
  - No placeholder data (e.g., "mock_", "default_", "PLACEHOLDER")
  - No hardcoded fallback responses when data unavailable
  - Return null/error instead of fake data
  - All metrics must be calculated (not guessed)
"""
import re
from typing import Any, Dict, List


class NoFakeDataValidator:
    """Validates that outputs comply with NO_FAKE_DATA policy."""

    FORBIDDEN_PATTERNS = [
        r"mock_",
        r"fake_",
        r"placeholder",
        r"PLACEHOLDER",
        r"dummy_",
        r"sample_",
        r"default_",
        r"example_",
        r"test_",
        r"stub_",
    ]

    @staticmethod
    def is_fake_string(value: str) -> bool:
        """Check if string looks like fake/placeholder data."""
        if not isinstance(value, str):
            return False
        value_lower = value.lower()
        for pattern in NoFakeDataValidator.FORBIDDEN_PATTERNS:
            if re.search(pattern, value_lower):
                return True
        return False

    @staticmethod
    def validate_output(data: Dict[str, Any]) -> List[str]:
        """Scan output for fake data. Returns list of issues found."""
        issues = []

        for key, value in data.items():
            # Check for fake strings
            if isinstance(value, str) and NoFakeDataValidator.is_fake_string(value):
                issues.append(f"Field '{key}' contains fake data pattern: {value}")

            # Check for fake numeric ranges
            if isinstance(value, (int, float)):
                # Resonance metrics should be in valid dB range
                if "ndb" in key.lower() or "decibel" in key.lower():
                    if value > 1_000_000_000.0 or value < -200_000_000_000.0:
                        issues.append(f"Field '{key}' has unrealistic value: {value}")

            # Check for complete absence when required
            if key in ["phase", "status", "matched"] and value is None:
                issues.append(f"Required field '{key}' is None")

        return issues

    @staticmethod
    def validate_stream_phases(phases: List[Dict[str, Any]]) -> List[str]:
        """Validate that all stream phases are real (no skipped phases with fake data)."""
        issues = []

        required_phases = [
            "scanning",
            "processing",
            "resonance",
            "security",
        ]

        found_phases = {p.get("phase") for p in phases}

        for req_phase in required_phases:
            if req_phase not in found_phases:
                issues.append(f"Missing required phase: {req_phase}")

        # Validate each phase
        for phase_data in phases:
            phase_issues = NoFakeDataValidator.validate_output(phase_data)
            issues.extend(phase_issues)

        # Check for firewall phase consistency
        has_firewall = any(p.get("phase") == "firewall_action" for p in phases)
        is_blocked = any(p.get("firewall_action") == "block" for p in phases)
        if is_blocked and not has_firewall:
            issues.append("Firewall action 'block' without firewall_action phase")

        return issues


def validate_no_fake_data(data: Any) -> bool:
    """Quick check: is this data real (no fake patterns)?

    Returns True if data is valid (no fake data detected).
    """
    validator = NoFakeDataValidator()

    if isinstance(data, dict):
        issues = validator.validate_output(data)
        return len(issues) == 0
    elif isinstance(data, list):
        issues = validator.validate_stream_phases(data)
        return len(issues) == 0

    return True  # Primitive types assumed real
