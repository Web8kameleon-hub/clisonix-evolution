"""
SELF DIAGNOSTICS - Self-Assessment & Learning
==============================================
Tracks errors, learns patterns, self-improves.

Ultra-light: ~70 lines | Error tracking | Pattern learning
"""

from dataclasses import dataclass
from typing import Dict, List
from datetime import datetime
import json


@dataclass
class DiagnosticReport:
    health_score: float  # 0.0 - 1.0
    total_requests: int
    error_count: int
    error_rate: float
    common_issues: List[str]
    recommendations: List[str]


@dataclass
class ErrorRecord:
    timestamp: str
    error_type: str
    query_hash: str
    resolved: bool = False


class SelfDiagnostics:
    """
    Self-monitoring and diagnostic system.
    """
    
    def __init__(self, max_history: int = 500):
        self._errors: List[ErrorRecord] = []
        self._request_count: int = 0
        self._success_count: int = 0
        self._error_patterns: Dict[str, int] = {}
        self._max_history = max_history
    
    def record_success(self) -> None:
        """Record successful request."""
        self._request_count += 1
        self._success_count += 1
    
    def record_error(self, error_type: str, query_hash: str = "") -> None:
        """Record error occurrence."""
        self._request_count += 1
        
        record = ErrorRecord(
            timestamp=datetime.now().isoformat(),
            error_type=error_type,
            query_hash=query_hash
        )
        self._errors.append(record)
        
        # Track patterns
        self._error_patterns[error_type] = self._error_patterns.get(error_type, 0) + 1
        
        # Trim history
        if len(self._errors) > self._max_history:
            self._errors = self._errors[-self._max_history:]
    
    def get_health(self) -> float:
        """Get current health score."""
        if self._request_count == 0:
            return 1.0
        return self._success_count / self._request_count
    
    def diagnose(self) -> DiagnosticReport:
        """Run full diagnostic."""
        health = self.get_health()
        error_count = len(self._errors)
        error_rate = 1.0 - health
        
        # Find common issues
        sorted_patterns = sorted(
            self._error_patterns.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        common_issues = [p[0] for p in sorted_patterns[:5]]
        
        # Generate recommendations
        recommendations = []
        if error_rate > 0.1:
            recommendations.append("Shkalla e gabimeve është e lartë, kontrollo loget.")
        if "timeout" in self._error_patterns:
            recommendations.append("Ka timeout të shumta, konsidero optimizimin.")
        if "memory" in str(common_issues).lower():
            recommendations.append("Probleme memorie të detektuara.")
        if health > 0.95:
            recommendations.append("✅ Sistemi është në gjendje të shkëlqyer!")
        
        return DiagnosticReport(
            health_score=health,
            total_requests=self._request_count,
            error_count=error_count,
            error_rate=error_rate,
            common_issues=common_issues,
            recommendations=recommendations
        )
    
    def export_report(self) -> str:
        """Export diagnostic report as JSON."""
        report = self.diagnose()
        return json.dumps({
            "health_score": report.health_score,
            "total_requests": report.total_requests,
            "error_rate": f"{report.error_rate*100:.2f}%",
            "common_issues": report.common_issues,
            "recommendations": report.recommendations,
        }, indent=2)


# Singleton
_diagnostics = None

def get_diagnostics() -> SelfDiagnostics:
    global _diagnostics
    if _diagnostics is None:
        _diagnostics = SelfDiagnostics()
    return _diagnostics
