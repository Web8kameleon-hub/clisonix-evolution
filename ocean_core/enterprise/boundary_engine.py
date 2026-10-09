"""
BOUNDARY ENGINE - What Ocean Does & Doesn't Do
===============================================
Clear limits. No ambiguity. Professional boundaries.

Ultra-light: ~70 lines | Pattern matching | Fast checks
"""

from dataclasses import dataclass
from typing import Set, Tuple
import re


@dataclass
class BoundaryResult:
    allowed: bool
    reason: str
    category: str


class BoundaryEngine:
    """
    Enforces clear operational boundaries.
    """
    
    # Things I DO
    CAPABILITIES: Set[str] = {
        "answer_questions", "explain_concepts", "write_code",
        "translate_text", "summarize_content", "analyze_data",
        "help_with_tasks", "provide_information", "creative_writing",
        "technical_support", "language_help", "brainstorming",
    }
    
    # Things I DON'T DO - with patterns
    BLOCKED_PATTERNS: Tuple[Tuple[str, str], ...] = (
        (r"\b(hack|crack|exploit)\b.*\b(system|password|account)\b", "security_violation"),
        (r"\b(make|create|build)\b.*\b(bomb|weapon|virus)\b", "dangerous_content"),
        (r"\b(steal|fraud|scam)\b", "illegal_activity"),
        (r"\bpretend.*human\b", "identity_violation"),
        (r"\b(child|minor).*\b(inappropriate|sexual)\b", "harmful_content"),
    )
    
    # Soft limits - I can do but with caution
    CAUTION_PATTERNS: Tuple[Tuple[str, str], ...] = (
        (r"\bmedical\s+advice\b", "medical_disclaimer"),
        (r"\blegal\s+advice\b", "legal_disclaimer"),
        (r"\bfinancial\s+advice\b", "financial_disclaimer"),
    )
    
    def __init__(self):
        self._compiled_blocked = [(re.compile(p, re.I), c) for p, c in self.BLOCKED_PATTERNS]
        self._compiled_caution = [(re.compile(p, re.I), c) for p, c in self.CAUTION_PATTERNS]
    
    def check(self, query: str) -> BoundaryResult:
        """Check if query is within boundaries."""
        
        # Check blocked patterns
        for pattern, category in self._compiled_blocked:
            if pattern.search(query):
                return BoundaryResult(
                    allowed=False,
                    reason="Kjo kërkesë është jashtë kufijve të mi operacionalë.",
                    category=category
                )
        
        # Check caution patterns
        for pattern, category in self._compiled_caution:
            if pattern.search(query):
                return BoundaryResult(
                    allowed=True,
                    reason=f"⚠️ Kujdes: Kjo është vetëm informacion, jo këshillë profesionale {category.replace('_', ' ')}.",
                    category=category
                )
        
        # Default: allowed
        return BoundaryResult(
            allowed=True,
            reason="",
            category="general"
        )
    
    def can_do(self, capability: str) -> bool:
        """Check if capability is supported."""
        return capability in self.CAPABILITIES


# Singleton
_engine = None

def get_boundaries() -> BoundaryEngine:
    global _engine
    if _engine is None:
        _engine = BoundaryEngine()
    return _engine
