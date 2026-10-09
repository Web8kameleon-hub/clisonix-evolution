"""
XLC Lock — celesberi (key-bearer / door guard).

Koncepti:
  XLCLock ruan keyprint-in e regjistruar.
  Kur vjen një çelës i ri (XLCKey), Lock llogarit ngjashmërinë cosine
  ndërmjet dy keyprint-eve. Nëse similarity >= min_similarity,
  dera hapet (LockResult.opened = True).

Algebra e verifikimit:
  similarity = dot(keyprint_registered, keyprint_incoming)
             (të dy janë unit vectors → cosine = dot)

  Dera: hapet  ←→  similarity >= min_similarity
        mbyllet ←→  similarity < min_similarity

Rregull NO_FAKE_DATA:
  - LockResult.opened = False nëse similarity nuk plotëson pragun — asnjëherë True i rremë
  - similarity është vlera reale llogaritje, jo hardcoded
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

from xlc_key import XLCKey  # type: ignore


@dataclass(frozen=True)
class LockResult:
    """Rezultati i provës së çelësit."""

    opened: bool           # True vetëm nëse similarity >= min_similarity
    similarity: float      # cosine similarity reale [−1.0, 1.0]
    check_latency_ns: int  # koha e verifikimit në nanosekonda
    registered_sequence: str   # sekuenca e regjistruar (read-only info)
    candidate_sequence: str    # sekuenca kandidate


class XLCLock:
    """Celesberi — ruan çelësin e regjistruar dhe kontrollon kandidatët.

    Parametra:
        registered_key: XLCKey — çelësi që "hap" derën
        min_similarity:  float — pragu cosine, default 0.9999 (identik praktikisht)

    Shembull:
        lock = XLCLock.from_passphrase("OPEN")
        result = lock.try_open(XLCKey.from_string("OPEN"))
        # result.opened == True

        result2 = lock.try_open(XLCKey.from_string("FAIL"))
        # result2.opened == False
    """

    # Pragu i parazgjedhur: shumë i lartë — vetëm sekuenca identike hap
    DEFAULT_MIN_SIMILARITY = 0.9999

    def __init__(
        self,
        registered_key: XLCKey,
        min_similarity: float = DEFAULT_MIN_SIMILARITY,
    ) -> None:
        if not (0.0 < min_similarity <= 1.0):
            raise ValueError("min_similarity duhet të jetë në (0.0, 1.0]")
        self._registered = registered_key
        self._min_similarity = min_similarity

    @staticmethod
    def from_passphrase(
        passphrase: str,
        min_similarity: float = DEFAULT_MIN_SIMILARITY,
    ) -> "XLCLock":
        """Shkurtore: krijon Lock direkt nga një string passphrase."""
        key = XLCKey.from_string(passphrase)
        return XLCLock(key, min_similarity=min_similarity)

    @property
    def registered_sequence(self) -> str:
        return self._registered.sequence

    def try_open(self, candidate: XLCKey) -> LockResult:
        """Provo çelësin kandidat kundrejt çelësit të regjistruar.

        Kthon LockResult me opened=True vetëm nëse valët përputhen.
        Asnjëherë nuk kthehet opened=True kur similarity < min_similarity.
        """
        t0 = time.perf_counter_ns()
        similarity = self._registered.cosine_similarity_with(candidate)
        t1 = time.perf_counter_ns()

        opened = similarity >= self._min_similarity

        return LockResult(
            opened=opened,
            similarity=similarity,
            check_latency_ns=t1 - t0,
            registered_sequence=self._registered.sequence,
            candidate_sequence=candidate.sequence,
        )

    def try_open_string(self, text: str) -> LockResult:
        """Shkurtore: provo direkt nga string, pa krijuar XLCKey manualisht."""
        candidate = XLCKey.from_string(text)
        return self.try_open(candidate)
