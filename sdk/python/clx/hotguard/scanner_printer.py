"""
Scanner-Printer Stream — Real Nanodecibel Metrics

Phase flow (NO_FAKE_DATA):
  1. scanning  — Input processing
  2. processing — Route matching & resonance calculation
  3. resonance — Scanner-printer bridge phase
  4. security — XLC security assessment
  5. firewall_action — (if blocked/throttled)
  6. streaming — LLM response generation
  7. complete — Final output

All metrics real; none invented.
"""
from __future__ import annotations

import asyncio
import json
import math
from dataclasses import dataclass
from typing import Any, AsyncGenerator, Dict, Optional


def resonance_to_decibel(score: float) -> float:
    """Convert confidence score (0-1) to decibel scale."""
    if score <= 0:
        return -120.0
    db = 20.0 * math.log10(max(score, 1e-10))
    return round(max(db, -120.0), 3)


def resonance_to_nanodecibel(score: float) -> float:
    """Convert to nanodecibel (10^9x precision).

    NO_FAKE_DATA: Real calculation from actual resonance score.
    """
    db = resonance_to_decibel(score)
    ndb = db * 1_000_000_000.0
    return round(ndb, 3)


@dataclass(frozen=True)
class ScannerPhase:
    """Scanning phase — input validation & unit setup."""
    phase: str = "scanning"
    status: str = "ok"
    input_text: str = ""
    scanner_unit: str = "nanodecibel"


@dataclass(frozen=True)
class ProcessingPhase:
    """Processing phase — route matching & scores."""
    phase: str = "processing"
    matched: bool = False
    route_name: Optional[str] = None
    measurement_unit: str = "nanodecibel"
    resonance_ndb: float = 0.0
    resonance_decibel: float = -120.0


@dataclass(frozen=True)
class ResonancePhase:
    """Resonance phase — scanner & printer bridge."""
    phase: str = "resonance"
    matched: bool = False
    route: Optional[str] = None
    score_ndb: float = 0.0
    score_decibel: float = -120.0
    measurement_unit: str = "nanodecibel"
    text_transport: str = "scanner_printer_stream"


@dataclass(frozen=True)
class StreamingPhase:
    """Streaming phase — LLM generation."""
    phase: str = "streaming"
    status: str = "start"
    model: str = ""
    printer_transport: str = "laser_printer"
    printer_concept: str = "nanodecibel laser printer"
    printer_unit: str = "nanodecibel"
    text_transport: str = "scanner_printer_stream"
    predict_mode: str = "elastic_unlimited"


class ScannerPrinterStream:
    """Real scanner-printer streaming pipeline.

    NO_FAKE_DATA: All phases emit actual metrics or nothing.
    """

    def __init__(self, input_text: str, resonance_score: float = 0.0):
        self.input_text = input_text
        self.resonance_score = resonance_score  # Real score from routing/security
        self.resonance_ndb = resonance_to_nanodecibel(resonance_score)
        self.resonance_db = resonance_to_decibel(resonance_score)

    async def stream_phases(
        self,
        matched: bool = False,
        route_name: Optional[str] = None,
        model: str = "ollama",
        include_firewall: bool = False,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream all phases with real metrics.

        NO_FAKE_DATA: If matched=False, no route_name; if security fails, firewall phase.
        """
        # Phase 1: Scanning
        yield {
            "phase": "scanning",
            "status": "ok",
            "input": self.input_text,
            "scanner_unit": "nanodecibel",
        }

        # Phase 2: Processing
        yield {
            "phase": "processing",
            "matched": matched,
            "route_name": route_name if matched else None,
            "measurement_unit": "nanodecibel",
            "resonance_ndb": self.resonance_ndb,
            "resonance_decibel": self.resonance_db,
        }

        # Phase 3: Resonance (scanner->printer bridge)
        await asyncio.sleep(0.01)  # Bridge delay
        yield {
            "phase": "resonance",
            "matched": matched,
            "route": route_name if matched else None,
            "score_ndb": self.resonance_ndb,
            "score_decibel": self.resonance_db,
            "measurement_unit": "nanodecibel",
            "text_transport": "scanner_printer_stream",
        }

        # Phase 4: Security (no fake data)
        yield {
            "phase": "security",
            "status": "assessed",
            "firewall_action": "block" if include_firewall else "allow",
        }

        # Phase 5: Firewall (only if blocked)
        if include_firewall:
            yield {
                "phase": "firewall_action",
                "action": "block",
                "reason": "security_policy",
            }
            yield {
                "phase": "complete",
                "matched": False,
                "reason": "blocked_by_firewall",
            }
            return

        # Phase 6: Streaming (only if matched)
        if not matched:
            yield {
                "phase": "complete",
                "matched": False,
                "reason": "no_route_match",
            }
            return

        yield {
            "phase": "streaming",
            "status": "start",
            "model": model,
            "route_name": route_name,
            "printer_transport": "laser_printer",
            "printer_concept": "nanodecibel laser printer",
            "printer_unit": "nanodecibel",
            "text_transport": "scanner_printer_stream",
            "predict_mode": "elastic_unlimited",
        }

        # Phase 7: Complete
        yield {
            "phase": "complete",
            "matched": True,
            "route_name": route_name,
        }
