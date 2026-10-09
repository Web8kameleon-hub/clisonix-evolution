"""
XLC Key — çelësi i bazuar në valë WWWMMM.

Koncepti:
  Çdo sekuencë simbolesh (p.sh. "HELLO") transformohet në një "keyprint" —
  një vektor i vetëm 24-dimensional që përfaqëson superpozicionin e valëve
  të të gjithë simboleve. Dy sekuenca identike prodhojnë keyprint identik.
  Sekuencë e ndryshme → keyprint i ndryshëm → dera nuk hapet.

Algebra e kombinimit:
  keyprint[i] = mean(v[i] for v in symbol_vectors)

  Kjo është analogia fizike me superpozicionin e valëve:
  kur N vale mbivendosen, rezultante është mesatarja e tyre amplitudinale.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import numpy as np
from xlc_alphabet import ALPHABET, WWWMMM, normalize_symbol, resolve_profile  # type: ignore


def _vector_mean(vectors: List[List[float]]) -> List[float]:
    """Mean element-wise me numpy."""
    if not vectors:
        raise ValueError("nuk mund të ndërtosh keyprint nga sekuencë bosh")
    arr = np.array(vectors, dtype=np.float64)  # (N, D)
    return arr.mean(axis=0).tolist()


def _normalize(v: List[float]) -> List[float]:
    """Normalizon vektorin në njësi (unit vector) me numpy."""
    arr = np.asarray(v, dtype=np.float64)
    n = float(np.linalg.norm(arr))
    return (arr / n).tolist() if n > 0.0 else arr.tolist()


@dataclass(frozen=True)
class XLCKey:
    """Çelësi i valëve — keyprint i normalizuar 24-dimensional.

    Atribute:
        sequence:  sekuenca origjinale e simboleve (uppercase)
        keyprint:  vektor unit 24-d (superpozicion i normalizuar)
        length:    numri i simboleve të njohur që ndërtuan keyprint-in
    """

    sequence: str
    keyprint: List[float]
    length: int

    @staticmethod
    def from_string(
        text: str,
        alphabet: Dict[str, WWWMMM] | None = None,
    ) -> "XLCKey":
        """Ndërton XLCKey nga teksti.

        Parametra:
            text:     sekuenca e simboleve (rasti i madh ose i vogël)
            alphabet: alfabeti WWWMMM (parazgjedhja = ALPHABET global)

        Raises:
            ValueError: nëse asnjë karakter i tekstit nuk ekziston në alfabet
        """
        if alphabet is None:
            alphabet = ALPHABET

        vectors: List[List[float]] = []
        known_chars: List[str] = []

        for ch in text:
            symbol = normalize_symbol(ch)
            if not symbol or not symbol.isalpha():
                continue
            vectors.append(resolve_profile(symbol, alphabet).to_vector())
            known_chars.append(symbol)

        if not vectors:
            raise ValueError(
                f"sekuenca '{text}' nuk përmban asnjë simbol të njohur në alfabet"
            )

        raw_keyprint = _vector_mean(vectors)
        unit_keyprint = _normalize(raw_keyprint)

        return XLCKey(
            sequence="".join(known_chars),
            keyprint=unit_keyprint,
            length=len(known_chars),
        )

    def cosine_similarity_with(self, other: "XLCKey") -> float:
        """Cosine similarity = dot product (unit vectors) me numpy."""
        a = np.asarray(self.keyprint, dtype=np.float64)
        b = np.asarray(other.keyprint, dtype=np.float64)
        return float(a @ b)
