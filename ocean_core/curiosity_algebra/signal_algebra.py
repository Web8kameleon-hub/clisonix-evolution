# -*- coding: utf-8 -*-
"""
🧮 SIGNAL ALGEBRA ENGINE - Algjebra që kupton valët
====================================================
Motori matematikor që i jep kuptim sinjaleve.

Operacionet bazë:
- Superpozim: S = Σᵢ Sᵢ
- Filtrim: F(S, condition) → S'
- Devijim: D = Sreal - Sexpected
- Agregim: A(S, window) → metrics
- Korelacion: Corr(Sᵢ, Sⱼ)
"""

import math
import logging
import statistics
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Callable, Optional, Tuple, Union
from dataclasses import dataclass
from collections import defaultdict

from .event_bus import Event, EventType

logger = logging.getLogger(__name__)


@dataclass
class SignalVector:
    """Vektor sinjali - gjendje modulare"""
    values: List[float]
    labels: List[str] = None
    timestamp: datetime = None
    source: str = ""
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = [f"v{i}" for i in range(len(self.values))]
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)
    
    def __add__(self, other: 'SignalVector') -> 'SignalVector':
        return SignalVector(
            values=[a + b for a, b in zip(self.values, other.values)],
            labels=self.labels,
            source=f"{self.source}+{other.source}"
        )
    
    def __sub__(self, other: 'SignalVector') -> 'SignalVector':
        return SignalVector(
            values=[a - b for a, b in zip(self.values, other.values)],
            labels=self.labels,
            source=f"{self.source}-{other.source}"
        )
    
    def magnitude(self) -> float:
        return math.sqrt(sum(v**2 for v in self.values))
    
    def normalize(self) -> 'SignalVector':
        mag = self.magnitude()
        if mag == 0:
            return self
        return SignalVector(
            values=[v / mag for v in self.values],
            labels=self.labels,
            source=self.source
        )


class SignalAlgebra:
    """
    🧮 Motori Algjebrik i Sinjaleve
    
    Ky motor është "truri analitik" i detit.
    Kupton valët, gjen mospërputhjet, zbulon korelacionet.
    """
    
    def __init__(self):
        self.signal_cache: Dict[str, List[float]] = defaultdict(list)
        self.expectations: Dict[str, float] = {}
        logger.info("🧮 SignalAlgebra initialized - Truri analitik është gati")
    
    # ==================== SUPERPOZIM ====================
    def superpose(self, signals: List[Union[float, SignalVector]]) -> Union[float, SignalVector]:
        """
        Superpozim: S = Σᵢ Sᵢ
        Kombinon sinjale nga burime të ndryshme në një "valë" të vetme.
        """
        if not signals:
            return 0.0
        
        if isinstance(signals[0], SignalVector):
            result = signals[0]
            for s in signals[1:]:
                result = result + s
            return result
        
        return sum(signals)
    
    def weighted_superpose(self, signals: List[float], weights: List[float]) -> float:
        """Superpozim i peshuar"""
        if len(signals) != len(weights):
            raise ValueError("Signals and weights must have same length")
        return sum(s * w for s, w in zip(signals, weights))
    
    # ==================== FILTRIM ====================
    def filter(self, signals: List[Event], condition: Callable[[Event], bool]) -> List[Event]:
        """
        Filtrim: F(S, condition) → S'
        Nxjerr vetëm sinjalet që përmbushin kushte.
        """
        return [s for s in signals if condition(s)]
    
    def filter_by_confidence(self, signals: List[Event], min_confidence: float = 0.5) -> List[Event]:
        """Filtro sipas konfidencës"""
        return self.filter(signals, lambda e: e.confidence >= min_confidence)
    
    def filter_by_type(self, signals: List[Event], event_type: EventType) -> List[Event]:
        """Filtro sipas tipit"""
        return self.filter(signals, lambda e: e.type == event_type)
    
    def filter_by_source(self, signals: List[Event], source: str) -> List[Event]:
        """Filtro sipas burimit"""
        return self.filter(signals, lambda e: e.source == source)
    
    def filter_by_tags(self, signals: List[Event], tags: List[str]) -> List[Event]:
        """Filtro sipas tag-eve"""
        return self.filter(signals, lambda e: any(t in e.tags for t in tags))
    
    def filter_anomalies(self, signals: List[Event]) -> List[Event]:
        """Filtro vetëm anomalitë"""
        return self.filter(signals, lambda e: e.type == EventType.ANOMALY)
    
    # ==================== DEVIJIM ====================
    def deviation(self, real: float, expected: float) -> float:
        """
        Devijim: D = Sreal - Sexpected
        Baza e kuriozitetit: ku realiteti nuk përputhet me modelin.
        """
        return real - expected
    
    def deviation_percent(self, real: float, expected: float) -> float:
        """Devijimi në përqindje"""
        if expected == 0:
            return 0.0 if real == 0 else float('inf')
        return ((real - expected) / abs(expected)) * 100
    
    def deviation_vector(self, real: SignalVector, expected: SignalVector) -> SignalVector:
        """Devijimi i vektorëve"""
        return real - expected
    
    def set_expectation(self, key: str, value: float) -> None:
        """Vendos pritshmërinë për një sinjal"""
        self.expectations[key] = value
    
    def check_deviation(self, key: str, real: float, threshold: float = 0.1) -> Tuple[bool, float]:
        """
        Kontrollo nëse ka devijim të rëndësishëm.
        Returns: (is_deviation, deviation_value)
        """
        expected = self.expectations.get(key, real)
        dev = self.deviation_percent(real, expected) / 100
        return (abs(dev) > threshold, dev)
    
    # ==================== AGREGIM ====================
    def aggregate(self, signals: List[float], window: Optional[int] = None) -> Dict[str, float]:
        """
        Agregim: A(S, window) → metrics
        Mesatare, variançë, trend—për të parë ritmin e detit.
        """
        if window:
            signals = signals[-window:]
        
        if not signals:
            return {"count": 0}
        
        return {
            "count": len(signals),
            "sum": sum(signals),
            "mean": statistics.mean(signals),
            "median": statistics.median(signals),
            "min": min(signals),
            "max": max(signals),
            "range": max(signals) - min(signals),
            "stdev": statistics.stdev(signals) if len(signals) > 1 else 0,
            "variance": statistics.variance(signals) if len(signals) > 1 else 0
        }
    
    def aggregate_time_window(self, events: List[Event], 
                               minutes: int = 5, 
                               value_key: str = "value") -> Dict[str, float]:
        """Agregim sipas dritares kohore"""
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        values = [
            e.payload.get(value_key, 0) 
            for e in events 
            if e.timestamp >= cutoff
        ]
        return self.aggregate(values)
    
    def trend(self, signals: List[float]) -> str:
        """Përcakto trendin: rising, falling, stable"""
        if len(signals) < 2:
            return "stable"
        
        first_half = signals[:len(signals)//2]
        second_half = signals[len(signals)//2:]
        
        avg_first = statistics.mean(first_half) if first_half else 0
        avg_second = statistics.mean(second_half) if second_half else 0
        
        diff = avg_second - avg_first
        threshold = 0.05 * abs(avg_first) if avg_first != 0 else 0.1
        
        if diff > threshold:
            return "rising"
        elif diff < -threshold:
            return "falling"
        return "stable"
    
    # ==================== KORELACION ====================
    def correlate(self, s1: List[float], s2: List[float]) -> float:
        """
        Korelacion: Corr(Sᵢ, Sⱼ)
        Gjen marrëdhëniet ndërmjet sinjaleve.
        """
        if len(s1) != len(s2) or len(s1) < 2:
            return 0.0
        
        n = len(s1)
        mean1 = sum(s1) / n
        mean2 = sum(s2) / n
        
        numerator = sum((a - mean1) * (b - mean2) for a, b in zip(s1, s2))
        
        std1 = math.sqrt(sum((a - mean1) ** 2 for a in s1))
        std2 = math.sqrt(sum((b - mean2) ** 2 for b in s2))
        
        if std1 == 0 or std2 == 0:
            return 0.0
        
        return numerator / (std1 * std2)
    
    def find_correlations(self, signals_dict: Dict[str, List[float]], 
                          threshold: float = 0.7) -> List[Tuple[str, str, float]]:
        """Gjej të gjitha korelacionet e forta ndërmjet sinjaleve"""
        correlations = []
        keys = list(signals_dict.keys())
        
        for i, key1 in enumerate(keys):
            for key2 in keys[i+1:]:
                corr = self.correlate(signals_dict[key1], signals_dict[key2])
                if abs(corr) >= threshold:
                    correlations.append((key1, key2, corr))
        
        return sorted(correlations, key=lambda x: abs(x[2]), reverse=True)
    
    # ==================== CACHE & MEMORY ====================
    def record(self, key: str, value: float, max_history: int = 1000) -> None:
        """Regjistro një vlerë në cache"""
        self.signal_cache[key].append(value)
        if len(self.signal_cache[key]) > max_history:
            self.signal_cache[key] = self.signal_cache[key][-max_history:]
    
    def get_history(self, key: str) -> List[float]:
        """Merr historinë e një sinjali"""
        return self.signal_cache.get(key, [])
    
    def analyze(self, key: str) -> Dict[str, Any]:
        """Analizë e plotë e një sinjali"""
        history = self.get_history(key)
        if not history:
            return {"key": key, "status": "no_data"}
        
        metrics = self.aggregate(history)
        trend = self.trend(history)
        
        # Check deviation from expectation
        if key in self.expectations:
            current = history[-1]
            is_dev, dev_value = self.check_deviation(key, current)
            metrics["deviation"] = dev_value
            metrics["is_anomaly"] = is_dev
        
        return {
            "key": key,
            "current": history[-1],
            "metrics": metrics,
            "trend": trend,
            "samples": len(history)
        }


# Singleton
_algebra: Optional[SignalAlgebra] = None

def get_signal_algebra() -> SignalAlgebra:
    global _algebra
    if _algebra is None:
        _algebra = SignalAlgebra()
    return _algebra
