from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Dict, Iterable, List, Optional


def _dot(left: Iterable[float], right: Iterable[float]) -> float:
    return sum(a * b for a, b in zip(left, right))


def _norm(values: Iterable[float]) -> float:
    return sqrt(sum(v * v for v in values))


def _cosine_similarity(left: List[float], right: List[float]) -> float:
    denominator = _norm(left) * _norm(right)
    if denominator == 0.0:
        return 0.0
    return _dot(left, right) / denominator


def _euclidean_distance(left: List[float], right: List[float]) -> float:
    return sqrt(sum((a - b) ** 2 for a, b in zip(left, right)))


@dataclass(frozen=True)
class ResonanceSample:
    """Physical profile of a symbol in amplitude/phase/frequency/jitter dimensions."""

    amplitude: List[float]
    phase: List[float]
    frequency: List[float]
    jitter_ns: List[float]

    def to_feature_vector(self) -> List[float]:
        # Jitter is scaled to keep all dimensions in comparable ranges.
        jitter_scaled = [value / 1000.0 for value in self.jitter_ns]
        return [*self.amplitude, *self.phase, *self.frequency, *jitter_scaled]

    def with_nano_shift(self, shift_ns: float) -> "ResonanceSample":
        return ResonanceSample(
            amplitude=list(self.amplitude),
            phase=list(self.phase),
            frequency=list(self.frequency),
            jitter_ns=[value + shift_ns for value in self.jitter_ns],
        )


@dataclass(frozen=True)
class ResonancePacket:
    symbol_hint: str
    w_sample: ResonanceSample
    observed_latency_seconds: float


@dataclass(frozen=True)
class DecodeResult:
    symbol: Optional[str]
    confidence: float
    deformation: float
    latency_seconds: float


class ResonanceChannel:
    """Prototype WWWMMM channel where symbols are decoded from physical resonance profiles."""

    def __init__(
        self,
        alphabet: Dict[str, ResonanceSample],
        min_confidence: float = 0.82,
    ) -> None:
        if not alphabet:
            raise ValueError("alphabet must contain at least one symbol profile")
        if not (0.0 < min_confidence <= 1.0):
            raise ValueError("min_confidence must be in range (0.0, 1.0]")
        self._alphabet = alphabet
        self._min_confidence = min_confidence

    @staticmethod
    def default_alphabet() -> Dict[str, ResonanceSample]:
        return {
            "A": ResonanceSample(
                amplitude=[0.91, 0.86, 0.80, 0.73],
                phase=[0.10, 0.22, 0.33, 0.49],
                frequency=[0.62, 0.78, 0.55, 0.31],
                jitter_ns=[14.0, 18.0, 13.0, 16.0],
            ),
            "X": ResonanceSample(
                amplitude=[0.64, 0.82, 0.67, 0.90],
                phase=[0.55, 0.37, 0.24, 0.12],
                frequency=[0.28, 0.61, 0.84, 0.70],
                jitter_ns=[22.0, 26.0, 24.0, 28.0],
            ),
        }

    def encode_symbol(
        self,
        symbol: str,
        observed_latency_seconds: float,
        nano_shift_ns: float = 0.0,
    ) -> ResonancePacket:
        if symbol not in self._alphabet:
            raise KeyError(f"symbol '{symbol}' is not registered")
        if observed_latency_seconds < 0.0:
            raise ValueError("observed_latency_seconds must be >= 0")
        sample = self._alphabet[symbol].with_nano_shift(nano_shift_ns)
        return ResonancePacket(
            symbol_hint=symbol,
            w_sample=sample,
            observed_latency_seconds=observed_latency_seconds,
        )

    def decode_packet(self, packet: ResonancePacket) -> DecodeResult:
        return self.decode_sample(packet.w_sample, packet.observed_latency_seconds)

    def decode_sample(
        self,
        w_sample: ResonanceSample,
        observed_latency_seconds: float,
    ) -> DecodeResult:
        incoming_vector = w_sample.to_feature_vector()
        best_symbol: Optional[str] = None
        best_confidence = -1.0
        best_deformation = 0.0

        for symbol, profile in self._alphabet.items():
            profile_vector = profile.to_feature_vector()
            confidence = _cosine_similarity(incoming_vector, profile_vector)
            deformation = _euclidean_distance(incoming_vector, profile_vector)
            if confidence > best_confidence:
                best_symbol = symbol
                best_confidence = confidence
                best_deformation = deformation

        if best_symbol is None:
            return DecodeResult(
                symbol=None,
                confidence=0.0,
                deformation=0.0,
                latency_seconds=observed_latency_seconds,
            )

        if best_confidence < self._min_confidence:
            return DecodeResult(
                symbol=None,
                confidence=best_confidence,
                deformation=best_deformation,
                latency_seconds=observed_latency_seconds,
            )

        return DecodeResult(
            symbol=best_symbol,
            confidence=best_confidence,
            deformation=best_deformation,
            latency_seconds=observed_latency_seconds,
        )
