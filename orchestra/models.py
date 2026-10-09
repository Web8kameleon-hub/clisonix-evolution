"""
orchestra.models
=================
Shared dataclasses / enums used across all Orchestra probes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class SignalStatus(str, Enum):
    OK      = "ok"
    WARNING = "warning"
    ERROR   = "error"
    UNKNOWN = "unknown"


@dataclass
class ProbeResult:
    """Single signal probe result."""
    domain: str                              # e.g. "repo", "hetzner", "cache"
    status: SignalStatus = SignalStatus.UNKNOWN
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    latency_ms: float = 0.0
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def ok(self) -> bool:
        return self.status == SignalStatus.OK

    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain":     self.domain,
            "status":     self.status.value,
            "message":    self.message,
            "details":    self.details,
            "latency_ms": round(self.latency_ms, 2),
            "timestamp":  self.timestamp,
        }


@dataclass
class DivisionReport:
    """Aggregated report from OrchestraDivision.run()."""
    probes:        List[ProbeResult] = field(default_factory=list)
    overall:       SignalStatus      = SignalStatus.UNKNOWN
    errors:        List[str]         = field(default_factory=list)
    warnings:      List[str]         = field(default_factory=list)
    generated_at:  str               = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    version:       str               = "1.0.0"

    # ── derived ────────────────────────────────────────────────────────────────

    @property
    def ok_count(self) -> int:
        return sum(1 for p in self.probes if p.status == SignalStatus.OK)

    @property
    def error_count(self) -> int:
        return sum(1 for p in self.probes if p.status == SignalStatus.ERROR)

    @property
    def warning_count(self) -> int:
        return sum(1 for p in self.probes if p.status == SignalStatus.WARNING)

    def compute_overall(self) -> SignalStatus:
        if any(p.status == SignalStatus.ERROR for p in self.probes):
            return SignalStatus.ERROR
        if any(p.status == SignalStatus.WARNING for p in self.probes):
            return SignalStatus.WARNING
        if all(p.status == SignalStatus.OK for p in self.probes):
            return SignalStatus.OK
        return SignalStatus.UNKNOWN

    def to_dict(self) -> Dict[str, Any]:
        self.overall = self.compute_overall()
        return {
            "overall":      self.overall.value,
            "ok_count":     self.ok_count,
            "warning_count": self.warning_count,
            "error_count":  self.error_count,
            "generated_at": self.generated_at,
            "version":      self.version,
            "errors":       self.errors,
            "warnings":     self.warnings,
            "probes":       [p.to_dict() for p in self.probes],
        }
