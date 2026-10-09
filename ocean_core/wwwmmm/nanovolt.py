# -*- coding: utf-8 -*-
"""
WWWMMM.nanovolt - Voltage/Energy Signal Metrics
================================================
Provides deterministic, low-overhead signal energy measurements.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class VoltSignal:
	"""A measured energy snapshot for one signal event."""

	magnitude: float
	frequency_hz: float
	phase_deg: float
	source: str
	timestamp: float = field(default_factory=time.time)


class NanoVolt:
	"""Tracks recent signal measurements and computes stable aggregates."""

	def __init__(self, max_history: int = 2048):
		self._max_history = max(1, int(max_history))
		self._signals: List[VoltSignal] = []

	def measure(
		self,
		*,
		magnitude: float,
		frequency_hz: float = 50.0,
		phase_deg: float = 0.0,
		source: str = "runtime",
	) -> VoltSignal:
		signal = VoltSignal(
			magnitude=float(magnitude),
			frequency_hz=float(frequency_hz),
			phase_deg=float(phase_deg),
			source=source.strip() or "runtime",
		)
		self._signals.append(signal)
		if len(self._signals) > self._max_history:
			self._signals = self._signals[-self._max_history :]
		return signal

	def latest(self) -> Optional[VoltSignal]:
		if not self._signals:
			return None
		return self._signals[-1]

	@property
	def stats(self) -> Dict[str, Any]:
		if not self._signals:
			return {
				"count": 0,
				"avg_magnitude": 0.0,
				"avg_frequency_hz": 0.0,
			}

		count = len(self._signals)
		sum_mag = sum(s.magnitude for s in self._signals)
		sum_freq = sum(s.frequency_hz for s in self._signals)
		return {
			"count": count,
			"avg_magnitude": round(sum_mag / count, 6),
			"avg_frequency_hz": round(sum_freq / count, 6),
			"latest_source": self._signals[-1].source,
		}


_nanovolt_instance: Optional[NanoVolt] = None


def get_nanovolt() -> NanoVolt:
	global _nanovolt_instance
	if _nanovolt_instance is None:
		_nanovolt_instance = NanoVolt()
	return _nanovolt_instance

