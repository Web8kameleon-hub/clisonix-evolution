"""
STRESS ENGINE - Logic Under Pressure
=====================================
Maintains quality responses under high load or complex queries.

Ultra-light: ~65 lines | Load awareness | Graceful degradation
"""

from dataclasses import dataclass

import time


@dataclass
class StressLevel:
    level: str  # "low", "medium", "high", "critical"
    score: float  # 0.0 - 1.0
    recommendation: str
    max_response_time: float  # seconds


class StressEngine:
    """
    Manages system stress and response quality under pressure.
    """
    
    # Stress thresholds
    THRESHOLDS = {
        "low": (0.0, 0.3),
        "medium": (0.3, 0.6),
        "high": (0.6, 0.8),
        "critical": (0.8, 1.0),
    }
    
    # Response time targets by stress level
    TIME_TARGETS = {
        "low": 10.0,
        "medium": 7.0,
        "high": 5.0,
        "critical": 3.0,
    }
    
    def __init__(self):
        self._request_times: list = []
        self._max_history = 100
    
    def record_request(self, duration: float) -> None:
        """Record request duration for stress calculation."""
        self._request_times.append((time.time(), duration))
        # Keep only recent history
        if len(self._request_times) > self._max_history:
            self._request_times = self._request_times[-self._max_history:]
    
    def calculate_stress(self) -> StressLevel:
        """Calculate current stress level."""
        if not self._request_times:
            return StressLevel("low", 0.0, "Sistemi është i qetë.", 10.0)
        
        # Calculate metrics
        recent = [d for t, d in self._request_times if time.time() - t < 60]
        
        if not recent:
            score = 0.0
        else:
            avg_time = sum(recent) / len(recent)
            request_rate = len(recent) / 60  # requests per second
            
            # Stress formula: combination of response time and rate
            time_stress = min(1.0, avg_time / 10.0)
            rate_stress = min(1.0, request_rate / 10.0)
            score = (time_stress * 0.6) + (rate_stress * 0.4)
        
        # Determine level
        level = "low"
        for lvl, (low, high) in self.THRESHOLDS.items():
            if low <= score < high:
                level = lvl
                break
        
        recommendations = {
            "low": "Performancë optimale.",
            "medium": "Ngarkesë e moderuar, përgjigjet mund të jenë pak më të ngadalta.",
            "high": "Ngarkesë e lartë, prioritet për përgjigje koncize.",
            "critical": "Ngarkesë kritike, vetëm përgjigje esenciale.",
        }
        
        return StressLevel(
            level=level,
            score=score,
            recommendation=recommendations[level],
            max_response_time=self.TIME_TARGETS[level]
        )
    
    def should_simplify(self) -> bool:
        """Check if responses should be simplified due to stress."""
        return self.calculate_stress().level in ("high", "critical")


# Singleton
_engine = None

def get_stress_handler() -> StressEngine:
    global _engine
    if _engine is None:
        _engine = StressEngine()
    return _engine
