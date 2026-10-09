"""
AMBIGUITY RESOLVER - Ask When Unclear
======================================
Detects vague queries and generates clarifying questions.

Ultra-light: ~65 lines | Pattern detection | Smart prompts
"""

from dataclasses import dataclass
from typing import List, Optional
import re


@dataclass
class AmbiguityResult:
    is_ambiguous: bool
    confidence: float  # 0.0 = very ambiguous, 1.0 = crystal clear
    clarifying_questions: List[str]
    ambiguity_type: Optional[str]


class AmbiguityResolver:
    """
    Detects and resolves ambiguous queries.
    """
    
    # Ambiguity indicators
    VAGUE_PATTERNS = [
        (r"^(it|this|that|these|those)\b", "pronoun_reference"),
        (r"^(do|make|fix|help)\s*$", "incomplete_request"),
        (r"\b(something|anything|stuff|things)\b", "vague_noun"),
        (r"^.{1,10}$", "too_short"),  # Very short queries
        (r"\?$", None),  # Questions are usually clear
    ]
    
    # Clarifying question templates
    CLARIFIERS = {
        "pronoun_reference": "Mund të specifikoni se çfarë keni parasysh me '{match}'?",
        "incomplete_request": "Çfarë dëshironi të {match} specifikisht?",
        "vague_noun": "Mund të jepni më shumë detaje rreth {match}?",
        "too_short": "Mund të më jepni më shumë kontekst?",
        "general": "A mund të sqaroni pak më shumë kërkesën tuaj?",
    }
    
    def analyze(self, query: str) -> AmbiguityResult:
        """Analyze query for ambiguity."""
        query = query.strip()
        ambiguities = []
        
        for pattern, amb_type in self.VAGUE_PATTERNS:
            match = re.search(pattern, query, re.I)
            if match and amb_type:
                ambiguities.append((amb_type, match.group()))
        
        # Calculate confidence (inverse of ambiguity)
        base_confidence = 1.0
        
        # Reduce confidence for each ambiguity found
        confidence = max(0.0, base_confidence - (len(ambiguities) * 0.25))
        
        # Boost confidence for longer, detailed queries
        word_count = len(query.split())
        if word_count > 10:
            confidence = min(1.0, confidence + 0.2)
        
        # Generate clarifying questions
        questions = []
        for amb_type, match_text in ambiguities[:2]:  # Max 2 questions
            template = self.CLARIFIERS.get(amb_type, self.CLARIFIERS["general"])
            questions.append(template.format(match=match_text))
        
        return AmbiguityResult(
            is_ambiguous=confidence < 0.6,
            confidence=confidence,
            clarifying_questions=questions,
            ambiguity_type=ambiguities[0][0] if ambiguities else None
        )
    
    def needs_clarification(self, query: str) -> bool:
        """Quick check if query needs clarification."""
        return self.analyze(query).is_ambiguous


# Singleton
_resolver = None

def get_resolver() -> AmbiguityResolver:
    global _resolver
    if _resolver is None:
        _resolver = AmbiguityResolver()
    return _resolver
