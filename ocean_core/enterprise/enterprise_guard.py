"""
ENTERPRISE GUARD - Unified Enterprise Layer
=============================================
Single entry point for all enterprise modules.

Usage:
    from enterprise import EnterpriseGuard
    guard = EnterpriseGuard()
    result = guard.process("user query", "ai response")
"""

from typing import Dict, Optional, Any
from dataclasses import dataclass

from .identity_kernel import get_identity
from .boundary_engine import get_boundaries
from .consistency_matrix import get_consistency
from .cognitive_verifier import get_verifier
from .ambiguity_resolver import get_resolver
from .integrity_firewall import get_firewall
from .tone_governor import get_tone
from .stress_engine import get_stress_handler
from .self_diagnostics import get_diagnostics
from .behavior_contract import get_contract


@dataclass
class GuardResult:
    """Result of enterprise guard processing."""
    approved: bool
    query_safe: bool
    response_valid: bool
    warnings: list
    metadata: Dict[str, Any]


class EnterpriseGuard:
    """
    Unified enterprise intelligence layer.
    
    Processes both input (queries) and output (responses)
    through all enterprise modules in one call.
    """
    
    def __init__(self):
        # Initialize all modules (singletons)
        self.identity = get_identity()
        self.boundaries = get_boundaries()
        self.consistency = get_consistency()
        self.verifier = get_verifier()
        self.resolver = get_resolver()
        self.firewall = get_firewall()
        self.tone = get_tone()
        self.stress = get_stress_handler()
        self.diagnostics = get_diagnostics()
        self.contract = get_contract()
    
    def check_input(self, query: str) -> Dict[str, Any]:
        """
        Pre-process check on user input.
        Call BEFORE generating response.
        """
        result = {
            "safe": True,
            "proceed": True,
            "warnings": [],
            "clarify": None,
            "sanitized": query,
        }
        
        # 1. Security check
        firewall = self.firewall.scan(query)
        if not firewall.safe:
            result["safe"] = False
            result["proceed"] = False
            result["warnings"].append(f"🛡️ {firewall.threat_level}: {firewall.threats_detected}")
            result["sanitized"] = firewall.sanitized_input
            return result
        
        # 2. Boundary check
        boundary = self.boundaries.check(query)
        if not boundary.allowed:
            result["proceed"] = False
            result["warnings"].append(f"🚫 {boundary.reason}")
            return result
        
        # 3. Ambiguity check
        ambiguity = self.resolver.analyze(query)
        if ambiguity.is_ambiguous and ambiguity.clarifying_questions:
            result["clarify"] = ambiguity.clarifying_questions[0]
        
        # 4. Consistency pattern
        pattern, cached_style = self.consistency.get_pattern(query)
        result["pattern"] = pattern
        result["suggested_style"] = cached_style
        
        return result
    
    def check_output(self, response: str, query: str = "") -> Dict[str, Any]:
        """
        Post-process check on AI response.
        Call AFTER generating response, BEFORE sending to user.
        """
        result = {
            "valid": True,
            "send": True,
            "warnings": [],
            "issues": [],
        }
        
        # 1. Contract compliance
        if not self.contract.is_compliant(response):
            checks = self.contract.check_response(response)
            violations = [c for c in checks if c.status.value == "violation"]
            result["valid"] = False
            result["issues"].extend([v.message for v in violations])
        
        # 2. Cognitive verification
        verification = self.verifier.verify(response, query)
        if not verification.passed:
            result["warnings"].extend(verification.issues)
            if verification.suggestion:
                result["warnings"].append(verification.suggestion)
        
        # 3. Record for diagnostics
        if result["valid"]:
            self.diagnostics.record_success()
        else:
            self.diagnostics.record_error("response_invalid", query[:50])
        
        return result
    
    def process(self, query: str, response: str) -> GuardResult:
        """
        Full pipeline: check both input and output.
        Returns unified result.
        """
        input_check = self.check_input(query)
        output_check = self.check_output(response, query)
        
        warnings = input_check.get("warnings", []) + output_check.get("warnings", [])
        
        return GuardResult(
            approved=input_check["proceed"] and output_check["send"],
            query_safe=input_check["safe"],
            response_valid=output_check["valid"],
            warnings=warnings,
            metadata={
                "pattern": input_check.get("pattern"),
                "clarify": input_check.get("clarify"),
                "stress_level": self.stress.calculate_stress().level,
                "health": self.diagnostics.get_health(),
            }
        )
    
    def get_identity_response(self) -> str:
        """Get standard identity response."""
        return self.identity.who_am_i()
    
    def get_status(self) -> Dict[str, Any]:
        """Get full enterprise status."""
        stress = self.stress.calculate_stress()
        diagnostic = self.diagnostics.diagnose()
        
        return {
            "identity": self.identity.identity.name,
            "signature": self.identity.signature,
            "stress_level": stress.level,
            "health_score": f"{diagnostic.health_score*100:.1f}%",
            "total_requests": diagnostic.total_requests,
            "tone_preset": self.tone.current.style.value,
            "modules_active": 10,
        }


# Singleton
_guard: Optional[EnterpriseGuard] = None

def get_enterprise_guard() -> EnterpriseGuard:
    """Get singleton enterprise guard instance."""
    global _guard
    if _guard is None:
        _guard = EnterpriseGuard()
    return _guard
