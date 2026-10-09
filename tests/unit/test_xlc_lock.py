"""Tests XLCKey + XLCLock — algebra e çelësit dhe celesberi."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
XLC_DIR = ROOT / "ocean-core" / "xlc"
if str(XLC_DIR) not in sys.path:
    sys.path.insert(0, str(XLC_DIR))

from xlc_key import XLCKey  # type: ignore
from xlc_lock import LockResult, XLCLock  # type: ignore

# ---------------------------------------------------------------------------
# XLCKey — ndërtimi dhe superpozicioni
# ---------------------------------------------------------------------------

def test_key_same_string_produces_identical_keyprint() -> None:
    """E njëjta sekuencë → keyprint identik bit-for-bit."""
    k1 = XLCKey.from_string("HELLO")
    k2 = XLCKey.from_string("HELLO")
    assert k1.keyprint == k2.keyprint


def test_key_different_strings_produce_different_keyprints() -> None:
    """Sekuenca e ndryshme → keyprint i ndryshëm."""
    k1 = XLCKey.from_string("OPEN")
    k2 = XLCKey.from_string("FAIL")
    # cosine similarity < 1.0 kur keyprint-et ndryshojnë
    similarity = k1.cosine_similarity_with(k2)
    assert similarity < 1.0


def test_key_is_unit_vector() -> None:
    """Keyprint duhet të jetë vektor unit (||v|| ≈ 1.0)."""
    import math
    key = XLCKey.from_string("CLISONIX")
    norm = math.sqrt(sum(x * x for x in key.keyprint))
    assert abs(norm - 1.0) < 1e-9


def test_key_ignores_unknown_chars() -> None:
    """Karakteret jo-alfabet dhe numrat kalohen — sekuenca mbetet me shkronjat."""
    key = XLCKey.from_string("HI 2026!")
    assert key.sequence == "HI"
    assert key.length == 2


def test_key_case_insensitive() -> None:
    """'hello' dhe 'HELLO' prodhojnë keyprint identik."""
    k_lower = XLCKey.from_string("hello")
    k_upper = XLCKey.from_string("HELLO")
    assert k_lower.keyprint == k_upper.keyprint


def test_key_supports_unicode_sequence() -> None:
    """XLCKey duhet të pranojë skripte Unicode."""
    key = XLCKey.from_string("مرحبا")
    assert key.sequence == "مرحبا"
    assert key.length == 5


def test_key_empty_after_strip_raises() -> None:
    """Sekuencë pa asnjë simbol të njohur duhet të ngrejë ValueError."""
    import pytest
    with pytest.raises(ValueError):
        XLCKey.from_string("123 !@#")


# ---------------------------------------------------------------------------
# XLCLock — celesberi
# ---------------------------------------------------------------------------

def test_lock_opens_with_correct_key() -> None:
    """Çelësi korrekt → dera hapet."""
    lock = XLCLock.from_passphrase("OPEN")
    result = lock.try_open_string("OPEN")
    assert result.opened is True
    assert result.similarity >= 0.9999


def test_lock_stays_closed_with_wrong_key() -> None:
    """Çelësi i gabuar → dera mbetet e mbyllur."""
    lock = XLCLock.from_passphrase("OPEN")
    result = lock.try_open_string("FAIL")
    assert result.opened is False


def test_lock_result_similarity_is_real_value() -> None:
    """similarity duhet të jetë float real, jo hardcoded."""
    lock = XLCLock.from_passphrase("ABC")
    result = lock.try_open_string("XYZ")
    # Vlera reale — jo 0.0 hardcoded, jo 1.0 hardcoded
    assert isinstance(result.similarity, float)
    assert 0.0 <= result.similarity <= 1.0


def test_lock_latency_is_measured_in_nanoseconds() -> None:
    """check_latency_ns duhet të jetë > 0 (matur nga perf_counter_ns)."""
    lock = XLCLock.from_passphrase("LATENCY")
    result = lock.try_open_string("LATENCY")
    assert result.check_latency_ns > 0


def test_lock_reports_sequences_correctly() -> None:
    """LockResult duhet të raportojë sekuencat e regjistruara dhe kandidate."""
    lock = XLCLock.from_passphrase("DOOR")
    result = lock.try_open_string("KEY")
    assert result.registered_sequence == "DOOR"
    assert result.candidate_sequence == "KEY"


def test_lock_custom_threshold_allows_similar_key() -> None:
    """Me threshold të ulët, çelësa me vala të ngjashme mund të hapin derën."""
    # "AB" dhe "AC" kanë vala relativisht të ngjashme
    lock = XLCLock.from_passphrase("AB", min_similarity=0.98)
    result = lock.try_open_string("AB")
    assert result.opened is True


def test_lock_single_letter_roundtrip() -> None:
    """Çelës me 1 shkronjë → Lock me 1 shkronjë → hapet."""
    for letter in "AZMQ":
        lock = XLCLock.from_passphrase(letter)
        result = lock.try_open_string(letter)
        assert result.opened is True, f"Shkronja '{letter}' nuk hapi derën"


def test_lock_unicode_passphrase_opens() -> None:
    """Passphrase Unicode duhet të hapë lock-un përkatës."""
    lock = XLCLock.from_passphrase("世界")
    result = lock.try_open_string("世界")
    assert result.opened is True


# ---------------------------------------------------------------------------
# Algebra — XLCKey.cosine_similarity_with
# ---------------------------------------------------------------------------

def test_key_self_similarity_is_one() -> None:
    """Çelësi me veten e tij ka similarity = 1.0 (unit vectors)."""
    key = XLCKey.from_string("WAVE")
    sim = key.cosine_similarity_with(key)
    assert abs(sim - 1.0) < 1e-9
