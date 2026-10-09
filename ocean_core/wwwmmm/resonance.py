# -*- coding: utf-8 -*-
"""WWWMMM resonance engine based on tide + mesh signal metrics."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class ResonanceResult:
	tide_level: float
	mesh_energy: float
	frequency_hz: float
	resonance_score: float
	timestamp: float = field(default_factory=time.time)


class ResonanceEngine:
	BASE_FREQ_HZ = 432.0

	def __init__(self):
		self._last = ResonanceResult(0.5, 0.0, self.BASE_FREQ_HZ, 0.0)
		self._history: list[ResonanceResult] = []

	def resonate(self, scan_payload: Dict[str, Any]) -> ResonanceResult:
		nv = float(scan_payload.get("nanovolt_level", 0))
		token_count = float(len(scan_payload.get("tokens", [])))
		confidence = float(scan_payload.get("confidence", 0.0))

		tide = max(0.0, min(1.0, (nv % 1000) / 1000.0))
		mesh_energy = round((token_count * 0.2) + (confidence * 0.8), 4)
		frequency_hz = round(self.BASE_FREQ_HZ + (nv % 300) + confidence * 30.0, 3)
		resonance_score = max(0.0, min(1.0, (mesh_energy / 10.0) + (tide * 0.4)))

		result = ResonanceResult(
			tide_level=tide,
			mesh_energy=mesh_energy,
			frequency_hz=frequency_hz,
			resonance_score=round(resonance_score, 4),
		)
		self._last = result
		self._history.append(result)
		if len(self._history) > 5000:
			self._history = self._history[-5000:]
		return result

	@property
	def last(self) -> ResonanceResult:
		return self._last

	@property
	def stats(self) -> Dict[str, Any]:
		if not self._history:
			return {"count": 0, "avg_score": 0.0}
		avg_score = sum(r.resonance_score for r in self._history) / len(self._history)
		return {
			"count": len(self._history),
			"avg_score": round(avg_score, 4),
			"last_frequency_hz": self._last.frequency_hz,
		}


_resonance_instance: Optional[ResonanceEngine] = None


def get_resonance() -> ResonanceEngine:
	global _resonance_instance
	if _resonance_instance is None:
		_resonance_instance = ResonanceEngine()
	return _resonance_instance

