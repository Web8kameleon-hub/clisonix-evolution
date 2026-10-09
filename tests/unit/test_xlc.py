"""Tests for XLC WWWMMM codec — roundtrip, speed, rejection, batch."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
XLC_DIR = ROOT / "ocean-core" / "xlc"
if str(XLC_DIR) not in sys.path:
    sys.path.insert(0, str(XLC_DIR))

from xlc_alphabet import ALPHABET, WWWMMM, build_alphabet  # type: ignore
from xlc_codec import XLCCodec, XLCResult  # type: ignore

# ---------------------------------------------------------------------------
# Roundtrip
# ---------------------------------------------------------------------------

def test_roundtrip_all_26_letters() -> None:
    """Çdo shkronjë e enkoduar duhet të dekodet saktë."""
    codec = XLCCodec()
    failures = []
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        packet = codec.encode(letter)
        result = codec.decode_packet(packet)
        if result.symbol != letter:
            failures.append(f"{letter} → {result.symbol} (conf={result.confidence:.4f})")
    assert not failures, f"Roundtrip dështoi për: {failures}"


# ---------------------------------------------------------------------------
# Speed — latency absolute
# ---------------------------------------------------------------------------

def test_decode_latency_under_500_microseconds() -> None:
    """Decode i çdo simboli duhet të zgjasë < 500 000 ns (0.5 ms) me pure Python."""
    codec = XLCCodec()
    MAX_NS = 500_000  # 0.5 ms — shpejtësi absolute pa numpy
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        packet = codec.encode(letter)
        result = codec.decode_packet(packet)
        assert result.decode_latency_ns < MAX_NS, (
            f"Shkronja '{letter}': {result.decode_latency_ns} ns > {MAX_NS} ns limit"
        )


# ---------------------------------------------------------------------------
# Rejection — profil i panjohur
# ---------------------------------------------------------------------------

def test_unknown_profile_is_rejected_with_high_threshold() -> None:
    """Profil plotësisht i huaj duhet të kthehet si symbol=None."""
    codec = XLCCodec(min_confidence=0.999)  # threshold jashtëzakonisht i lartë
    alien = WWWMMM(
        w1_amplitude=[0.01, 0.01, 0.01, 0.01],
        w2_phase=[0.99, 0.99, 0.99, 0.99],
        w3_coherence=[0.50, 0.50, 0.50, 0.50],
        m1_frequency=[0.01, 0.01, 0.01, 0.01],
        m2_harmonic=[0.99, 0.99, 0.99, 0.99],
        m3_jitter_ns=[200.0, 200.0, 200.0, 200.0],
    )
    result = codec.decode(alien)
    assert result.symbol is None
    assert result.confidence < 0.999


# ---------------------------------------------------------------------------
# Batch decode_string
# ---------------------------------------------------------------------------

def test_batch_decode_string_hello() -> None:
    """decode_string('HELLO') duhet të kthejë 5 rezultate me simbolet korrekte."""
    codec = XLCCodec()
    results = codec.decode_string("HELLO")
    assert len(results) == 5
    decoded = [r.symbol for r in results]
    assert decoded == ["H", "E", "L", "L", "O"], f"Mori: {decoded}"


def test_batch_decode_skips_non_alphabet_chars() -> None:
    """Karakteret jo-alfabetike (numra, hapësira) kalohen pa gabim."""
    codec = XLCCodec()
    results = codec.decode_string("AI 2026!")
    # Vetëm A dhe I janë në alfabet; hapësira, numrat dhe ! kalohen
    symbols = [r.symbol for r in results]
    assert symbols == ["A", "I"]


def test_unicode_symbol_roundtrip() -> None:
    """Një simbol Unicode duhet të enkodohet/dekodohet pa hardcoding latin."""
    codec = XLCCodec()
    packet = codec.encode("Ж")
    result = codec.decode_packet(packet)
    assert result.symbol == "Ж"


def test_unicode_batch_decode_string() -> None:
    """decode_string duhet të pranojë skripte jo-latine."""
    codec = XLCCodec()
    results = codec.decode_string("你好 2026")
    symbols = [r.symbol for r in results]
    assert symbols == ["你", "好"]


# ---------------------------------------------------------------------------
# Alphabet uniqueness
# ---------------------------------------------------------------------------

def test_all_profiles_have_distinct_vectors() -> None:
    """Asnjë dy shkronja nuk duhet të kenë vektorin identik."""
    alpha = build_alphabet()
    vectors = {s: tuple(p.to_vector()) for s, p in alpha.items()}
    unique_vectors = set(vectors.values())
    assert len(unique_vectors) == 26, "Dy ose më shumë shkronja kanë vektorin identik"


# ---------------------------------------------------------------------------
# Deformation is real
# ---------------------------------------------------------------------------

def test_deformation_is_positive_after_roundtrip() -> None:
    """Deformation duhet të jetë >= 0 (zero vetëm nëse profili është identik bit-per-bit)."""
    codec = XLCCodec()
    for letter in "AZ":
        packet = codec.encode(letter)
        result = codec.decode_packet(packet)
        assert result.deformation >= 0.0
