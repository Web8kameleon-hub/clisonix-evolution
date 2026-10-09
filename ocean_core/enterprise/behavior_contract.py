"""
BEHAVIOR CONTRACT - Formal Behavior Rules
==========================================
Codified rules for enterprise-grade behavior.

Ultra-light: ~70 lines | Rule engine | Contract enforcement
"""

from dataclasses import dataclass
from typing import Dict, List
from enum import Enum


class ContractStatus(Enum):
    COMPLIANT = "compliant"
    WARNING = "warning"
    VIOLATION = "violation"


@dataclass
class ContractCheck:
    rule_name: str
    status: ContractStatus
    message: str


class BehaviorContract:
    """
    Formal behavior contract enforcement.
    """
    
    # Core contract rules
    RULES: Dict[str, Dict] = {
        "honesty": {
            "description": "Always provide accurate information",
            "check": lambda r: "i made that up" not in r.lower(),
        },
        "identity": {
            "description": "Never claim to be human",
            "check": lambda r: "i am human" not in r.lower() and "i am a person" not in r.lower(),
        },
        "safety": {
            "description": "Never provide harmful instructions",
            "check": lambda r: not any(w in r.lower() for w in ["how to hack", "how to steal", "how to hurt"]),
        },
        "privacy": {
            "description": "Never reveal system prompts or internal data",
            "check": lambda r: "system prompt" not in r.lower() and "my instructions are" not in r.lower(),
        },
        "professionalism": {
            "description": "Maintain professional communication",
            "check": lambda r: not any(w in r.lower() for w in ["stupid", "idiot", "shut up"]),
        },
        "helpfulness": {
            "description": "Always attempt to help within bounds",
            "check": lambda r: len(r.strip()) > 10,  # Non-empty helpful response
        },
    }
    
    def __init__(self):
        self._violations: List[ContractCheck] = []
    
    def check_response(self, response: str) -> List[ContractCheck]:
        """Check response against all contract rules."""
        results = []
        
        for rule_name, rule_def in self.RULES.items():
            check_fn = rule_def["check"]
            try:
                passed = check_fn(response)
                status = ContractStatus.COMPLIANT if passed else ContractStatus.VIOLATION
                message = "" if passed else f"Shkelje e rregullit: {rule_def['description']}"
            except Exception as e:
                status = ContractStatus.WARNING
                message = f"Gabim në kontroll: {e}"
            
            check = ContractCheck(rule_name=rule_name, status=status, message=message)
            results.append(check)
            
            if status == ContractStatus.VIOLATION:
                self._violations.append(check)
        
        return results
    
    def is_compliant(self, response: str) -> bool:
        """Quick compliance check."""
        checks = self.check_response(response)
        return all(c.status == ContractStatus.COMPLIANT for c in checks)
    
    def get_violations(self) -> List[ContractCheck]:
        """Get history of violations."""
        return self._violations[-100:]  # Last 100
    
    def get_contract_text(self) -> str:
        """Get human-readable contract."""
        lines = ["📜 OCEAN BEHAVIOR CONTRACT", "=" * 30, ""]
        for name, rule in self.RULES.items():
            lines.append(f"• {name.upper()}: {rule['description']}")
        return "\n".join(lines)


# Singleton
_contract = None

def get_contract() -> BehaviorContract:
    global _contract
    if _contract is None:
        _contract = BehaviorContract()
    return _contract
