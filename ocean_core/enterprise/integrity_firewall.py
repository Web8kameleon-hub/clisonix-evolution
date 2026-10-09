"""
INTEGRITY FIREWALL - Block Manipulation Attempts
=================================================
Protects against prompt injection and manipulation.

Ultra-light: ~75 lines | Security patterns | Fast detection
"""

from dataclasses import dataclass
from typing import List, Tuple
import re


@dataclass  
class FirewallResult:
    safe: bool
    threat_level: str  # "none", "low", "medium", "high", "critical"
    threats_detected: List[str]
    sanitized_input: str


class IntegrityFirewall:
    """
    Security layer against prompt injection and manipulation.
    """
    
    # Threat patterns (pattern, threat_name, severity)
    THREATS: Tuple[Tuple[str, str, int], ...] = (
        # Prompt injection attempts
        (r"ignore\s+(previous|above|all)\s+(instructions?|prompts?)", "injection_ignore", 3),
        (r"you\s+are\s+now\s+(?!ocean)", "injection_roleplay", 3),
        (r"forget\s+(everything|all|your)", "injection_reset", 3),
        (r"new\s+instructions?:", "injection_override", 3),
        
        # Jailbreak attempts
        (r"DAN\s+mode", "jailbreak_dan", 4),
        (r"developer\s+mode", "jailbreak_dev", 3),
        (r"pretend\s+you\s+(have\s+no|don'?t\s+have)", "jailbreak_pretend", 2),
        
        # Data extraction
        (r"(show|reveal|tell)\s+(me\s+)?(your|the)\s+(system|prompt|instructions)", "extraction", 2),
        (r"what\s+(are|is)\s+your\s+(system|initial)\s+(prompt|instructions)", "extraction", 2),
        
        # SQL/Code injection (if passed to backends)
        (r";\s*(DROP|DELETE|UPDATE|INSERT)\s+", "sql_injection", 4),
        (r"<script[^>]*>", "xss_attempt", 3),
    )
    
    SEVERITY_MAP = {0: "none", 1: "low", 2: "medium", 3: "high", 4: "critical"}
    
    def __init__(self):
        self._compiled = [(re.compile(p, re.I), n, s) for p, n, s in self.THREATS]
    
    def scan(self, text: str) -> FirewallResult:
        """Scan input for threats."""
        threats = []
        max_severity = 0
        
        for pattern, threat_name, severity in self._compiled:
            if pattern.search(text):
                threats.append(threat_name)
                max_severity = max(max_severity, severity)
        
        # Sanitize if threats found
        sanitized = text
        if threats:
            # Remove dangerous patterns
            for pattern, _, _ in self._compiled:
                sanitized = pattern.sub("[BLOCKED]", sanitized)
        
        return FirewallResult(
            safe=len(threats) == 0,
            threat_level=self.SEVERITY_MAP.get(max_severity, "none"),
            threats_detected=threats,
            sanitized_input=sanitized
        )
    
    def is_safe(self, text: str) -> bool:
        """Quick safety check."""
        return self.scan(text).safe
    
    def get_warning(self, result: FirewallResult) -> str:
        """Generate user-facing warning."""
        if result.safe:
            return ""
        return "⚠️ Kërkesa juaj përmban elementë të dyshimtë dhe nuk mund të përpunohet."


# Singleton
_firewall = None

def get_firewall() -> IntegrityFirewall:
    global _firewall
    if _firewall is None:
        _firewall = IntegrityFirewall()
    return _firewall
