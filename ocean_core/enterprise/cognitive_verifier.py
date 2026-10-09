"""
COGNITIVE VERIFIER - Double-Check Before Responding
====================================================
Verification layer for response quality and accuracy.

Ultra-light: ~70 lines | Rule-based checks | Fast validation
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class VerificationResult:
    passed: bool
    score: float  # 0.0 - 1.0
    issues: List[str]
    suggestion: Optional[str]


class CognitiveVerifier:
    """
    Verifies response quality before delivery.
    """
    
    # Quality checks
    CHECKS = {
        "length": lambda r: 10 < len(r) < 10000,
        "not_empty": lambda r: bool(r.strip()),
        "no_forbidden": lambda r: not any(w in r.lower() for w in ["as an ai", "i cannot", "i'm sorry but"]),
        "has_content": lambda r: len(r.split()) > 3,
        "not_repetitive": lambda r: len(set(r.split())) / max(len(r.split()), 1) > 0.3,
    }
    
    # Red flags in responses
    RED_FLAGS = [
        "i don't know",
        "i cannot help",
        "error occurred",
        "undefined",
        "null",
    ]
    
    def verify(self, response: str, query: str = "") -> VerificationResult:
        """Verify response quality."""
        issues = []
        passed_checks = 0
        total_checks = len(self.CHECKS)
        
        # Run all checks
        for name, check in self.CHECKS.items():
            try:
                if check(response):
                    passed_checks += 1
                else:
                    issues.append(f"Failed: {name}")
            except Exception:
                issues.append(f"Error in: {name}")
        
        # Check for red flags
        response_lower = response.lower()
        for flag in self.RED_FLAGS:
            if flag in response_lower:
                issues.append(f"Red flag: '{flag}'")
        
        # Calculate score
        score = passed_checks / total_checks if total_checks > 0 else 0.0
        
        # Determine if passed (80% threshold)
        passed = score >= 0.8 and len([i for i in issues if "Red flag" in i]) == 0
        
        # Generate suggestion
        suggestion = None
        if not passed:
            if "length" in str(issues):
                suggestion = "Përgjigja duhet të jetë më e gjatë ose më e shkurtër."
            elif "not_repetitive" in str(issues):
                suggestion = "Përgjigja është shumë repetitive."
            elif issues:
                suggestion = "Përgjigja ka nevojë për përmirësim."
        
        return VerificationResult(
            passed=passed,
            score=score,
            issues=issues,
            suggestion=suggestion
        )
    
    def quick_check(self, response: str) -> bool:
        """Fast pass/fail check."""
        return self.verify(response).passed


# Singleton
_verifier = None

def get_verifier() -> CognitiveVerifier:
    global _verifier
    if _verifier is None:
        _verifier = CognitiveVerifier()
    return _verifier
