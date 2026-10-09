"""
XLC Codec — eXtreme Latency Codec për WWWMMM.

Inovacioni kryesor ndaj ResonanceChannel:
  - Alfabeti parakompjutohet si matric (lista e listave) në __init__
  - Decode = 1 kalim: dot-product i vektorit incoming me ÇDDO rresht të matricës
  - Nuk ka loop for-symbol brenda decode_sample (ose ka por overhead i jashtëzakonshëm
    minimizohet pasi matrix është e ndërtuar me cache locality)
  - Latency e kthimit matet me time.perf_counter_ns()
  - Kthimi i plotë: simboli, confidence, deformation, latency_ns (integer)

Rregull NO_FAKE_DATA: nëse asnjë simbol nuk kalon min_confidence, kthehet
  symbol=None — asnjëherë mos invento rezultat.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
from xlc_alphabet import ALPHABET, WWWMMM, normalize_symbol, resolve_profile  # type: ignore

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class XLCPacket:
    """Paketa e enkoduar gati për transmetim ose ruajtje."""

    symbol: str
    profile: WWWMMM
    encode_latency_ns: int


@dataclass(frozen=True)
class XLCResult:
    """Rezultati i dekodimit — gjithmonë real, asnjëherë i shpikur."""

    symbol: Optional[str]          # None nëse confidence < threshold
    confidence: float              # [0.0, 1.0]
    deformation: float             # distanca euklidiane nga profili ideal
    decode_latency_ns: int         # nanosekonda


# ---------------------------------------------------------------------------
# Precomputed matrix for batch cosine similarity
# ---------------------------------------------------------------------------

class _AlphabetMatrix:
    """Matric numpy e parakompjutuar: shape (N, D) — vektorë të normalizuar.

    cosine_all = 1 matrix-vector multiply (dot) + norm scalar → O(N*D) SIMD.
    """

    def __init__(self, alphabet: Dict[str, WWWMMM]) -> None:
        self.symbols: List[str] = sorted(alphabet.keys())
        raw = np.array(
            [alphabet[s].to_vector() for s in self.symbols], dtype=np.float64
        )  # shape (N, 24)
        self._norms: np.ndarray = np.linalg.norm(raw, axis=1)  # (N,)
        self._matrix: np.ndarray = raw  # (N, 24)

    def cosine_all(self, incoming: List[float]) -> List[Tuple[str, float, float]]:
        """Kthen listën (symbol, cosine_similarity, euclidean_distance).

        1 matrix-vector dot + broadcasting — zero Python loop.
        """
        vec = np.asarray(incoming, dtype=np.float64)  # (24,)
        in_norm = float(np.linalg.norm(vec))
        dots = self._matrix @ vec  # (N,) — single BLAS call
        denoms = self._norms * in_norm
        sims = np.divide(dots, denoms, out=np.zeros_like(dots), where=denoms != 0.0)
        diffs = self._matrix - vec  # (N, 24) broadcast
        dists = np.linalg.norm(diffs, axis=1)  # (N,)
        return [
            (self.symbols[i], float(sims[i]), float(dists[i]))
            for i in range(len(self.symbols))
        ]


# ---------------------------------------------------------------------------
# XLC Codec — API kryesore
# ---------------------------------------------------------------------------

class XLCCodec:
    """WWWMMM encoder/decoder me shpejtësi absolute.

    Parametra:
        alphabet: Dict[str, WWWMMM] — zakonisht ALPHABET nga xlc_alphabet.py
        min_confidence: float — threshold poshtë të cilit decode kthen symbol=None
    """

    def __init__(
        self,
        alphabet: Dict[str, WWWMMM] | None = None,
        min_confidence: float = 0.82,
    ) -> None:
        if alphabet is None:
            alphabet = ALPHABET
        if not alphabet:
            raise ValueError("alphabet nuk mund të jetë bosh")
        if not (0.0 < min_confidence <= 1.0):
            raise ValueError("min_confidence duhet të jetë në (0.0, 1.0]")
        self._alphabet = alphabet
        self._min_confidence = min_confidence
        self._matrix = _AlphabetMatrix(alphabet)

    def _refresh_matrix(self) -> None:
        self._matrix = _AlphabetMatrix(self._alphabet)

    def _ensure_symbol(self, symbol: str) -> str:
        normalized = normalize_symbol(symbol)
        if not normalized or not normalized.isalpha():
            raise KeyError(f"simboli '{symbol}' nuk ekziston në alfabet")
        if normalized not in self._alphabet:
            resolve_profile(normalized, self._alphabet)
            self._refresh_matrix()
        return normalized

    # ------------------------------------------------------------------
    # Encode
    # ------------------------------------------------------------------

    def encode(self, symbol: str) -> XLCPacket:
        """Enkodon simbolin dhe kthen paketën me profilin WWWMMM + latency."""
        normalized = self._ensure_symbol(symbol)
        t0 = time.perf_counter_ns()
        profile = self._alphabet[normalized]
        t1 = time.perf_counter_ns()
        return XLCPacket(
            symbol=normalized,
            profile=profile,
            encode_latency_ns=t1 - t0,
        )

    # ------------------------------------------------------------------
    # Decode
    # ------------------------------------------------------------------

    def decode(self, profile: WWWMMM) -> XLCResult:
        """Dekodon profilin WWWMMM duke përdorur matrix projection.

        Nuk gjeneron asnjë vlerë false — nëse confidence < threshold
        kthen symbol=None me confidence reale.
        """
        t0 = time.perf_counter_ns()
        incoming = profile.to_vector()
        scores = self._matrix.cosine_all(incoming)

        best_symbol, best_sim, best_dist = max(scores, key=lambda x: x[1])
        t1 = time.perf_counter_ns()

        if best_sim < self._min_confidence:
            return XLCResult(
                symbol=None,
                confidence=best_sim,
                deformation=best_dist,
                decode_latency_ns=t1 - t0,
            )

        return XLCResult(
            symbol=best_symbol,
            confidence=best_sim,
            deformation=best_dist,
            decode_latency_ns=t1 - t0,
        )

    def decode_packet(self, packet: XLCPacket) -> XLCResult:
        """Shkurtore: dekodon direkt nga XLCPacket."""
        return self.decode(packet.profile)

    # ------------------------------------------------------------------
    # Batch decode (fjali / sekuencë)
    # ------------------------------------------------------------------

    def decode_string(self, text: str) -> List[XLCResult]:
        """Enkodon dhe dekodon çdo shkronjë të text (uppercase).

        Kthyer vetëm shkronjat që ekzistojnë në alfabet; karakteret e tjera
        kalohen pa gjeneruar vlerë false.
        """
        results: List[XLCResult] = []
        for char in text:
            normalized = normalize_symbol(char)
            if not normalized or not normalized.isalpha():
                continue
            packet = self.encode(normalized)
            results.append(self.decode_packet(packet))
        return results

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def alphabet_size(self) -> int:
        return len(self._alphabet)

    def min_confidence(self) -> float:
        return self._min_confidence
