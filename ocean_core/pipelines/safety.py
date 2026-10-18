#!/usr/bin/env python3
"""
SAFETY FILTER
=============
Filtron përmbajtje të dëmshme dhe siguron output të sigurt.
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple

logger = logging.getLogger("SafetyFilter")


class SafetyLevel(Enum):
    """Nivelet e sigurisë"""
    SAFE = "safe"
    WARNING = "warning"
    BLOCKED = "blocked"


@dataclass
class SafetyResult:
    """Rezultati i kontrollit të sigurisë"""
    level: SafetyLevel
    message: str
    flags: List[str]
    sanitized_input: Optional[str] = None


# Patterns to detect
BLOCKED_PATTERNS = [
    r"(?i)(how to|make|create|build)\s*(bomb|explosive|weapon)",
    r"(?i)(hack|break into|exploit)\s*(bank|government|system)",
    r"(?i)(kill|murder|harm)\s*(person|people|someone)",
    r"(?i)child\s*(porn|abuse|exploitation)",
]

WARNING_PATTERNS = [
    r"(?i)(password|credential|secret)\s*(steal|hack|extract)",
    r"(?i)(malware|virus|trojan)\s*(create|make|code)",
    r"(?i)(phishing|scam)\s*(create|design|make)",
]

# Words to sanitize from output
SANITIZE_WORDS = [
    "password", "api_key", "secret_key", "private_key",
    "credit_card", "ssn", "social_security"
]


class SafetyFilter:
    """Filtri i sigurisë për input/output"""
    
    def __init__(self):
        self.blocked_patterns = [re.compile(p) for p in BLOCKED_PATTERNS]
        self.warning_patterns = [re.compile(p) for p in WARNING_PATTERNS]
        self.checks_count = 0
        self.blocked_count = 0
        logger.info("✅ SafetyFilter initialized")
    
    def check_input(self, text: str) -> SafetyResult:
        """Kontrollo input për përmbajtje të dëmshme"""
        self.checks_count += 1
        flags = []
        
        # Check blocked patterns
        for pattern in self.blocked_patterns:
            if pattern.search(text):
                self.blocked_count += 1
                return SafetyResult(
                    level=SafetyLevel.BLOCKED,
                    message="Kjo kërkesë nuk mund të përpunohet.",
                    flags=["blocked_content"]
                )
        
        # Check warning patterns
        for pattern in self.warning_patterns:
            if pattern.search(text):
                flags.append("potential_risk")
        
        if flags:
            return SafetyResult(
                level=SafetyLevel.WARNING,
                message="Përmbajtja mund të jetë e ndjeshme.",
                flags=flags,
                sanitized_input=text
            )
        
        return SafetyResult(
            level=SafetyLevel.SAFE,
            message="OK",
            flags=[],
            sanitized_input=text
        )
    
    def sanitize_output(self, text: str) -> str:
        """Sanitizo output duke maskuar informacion të ndjeshëm"""
        result = text
        
        for word in SANITIZE_WORDS:
            # Mask patterns like "password: abc123"
            pattern = rf"(?i)({word})\s*[:=]\s*\S+"
            result = re.sub(pattern, f"{word}: [REDACTED]", result)
        
        return result
    
    def validate_response(self, response: str) -> Tuple[bool, str]:
        """Valido përgjigjen para se të kthehet"""
        # Check for leaked sensitive patterns
        sensitive_patterns = [
            r"(?i)api[_-]?key\s*[:=]\s*[a-zA-Z0-9]{20,}",
            r"(?i)bearer\s+[a-zA-Z0-9\-._~+/]+=*",
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
        ]
        
        for pattern in sensitive_patterns:
            if re.search(pattern, response):
                sanitized = self.sanitize_output(response)
                return False, sanitized
        
        return True, response
    
    def get_stats(self) -> dict:
        """Merr statistikat"""
        return {
            "total_checks": self.checks_count,
            "blocked": self.blocked_count,
            "block_rate": f"{(self.blocked_count / max(1, self.checks_count)) * 100:.2f}%"
        }


# Singleton
_filter: Optional[SafetyFilter] = None


def get_safety_filter() -> SafetyFilter:
    """Merr instancën singleton"""
    global _filter
    if _filter is None:
        _filter = SafetyFilter()
    return _filter
