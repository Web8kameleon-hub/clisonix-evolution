# -*- coding: utf-8 -*-
"""
WWWMMM.thinker - Strict Thinking Guard
======================================
Rejects uncertain/noisy phrasing and keeps reasoning outputs deterministic.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ThinkResult:
	input_text: str
	output_text: str
	is_real: bool
	confidence: float
	blocked_hallucination: bool
	reason: str
	timestamp: float = field(default_factory=time.time)


class StrictThinker:
	"""Guardrail for stable, non-speculative response quality."""

	HALLUCINATION_MARKERS = [
		"as an ai",
		"as a language model",
		"i am not sure",
		"i don't know",
		"maybe",
		"perhaps",
		"possibly",
		"guess",
		"placeholder",
		"fabricated",
		"made up",
	]

	REAL_MARKERS = [
		"definition",
		"equation",
		"formula",
		"source",
		"document",
		"api",
		"runtime",
		"signal",
		"clisonix",
	]

	def __init__(self, hallucination_tolerance: float = 0.0):
		self.tolerance = max(0.0, float(hallucination_tolerance))
		self._history: List[ThinkResult] = []

	def verify(self, text: str) -> ThinkResult:
		source = text or ""
		lower = source.lower()
		h_hits = [m for m in self.HALLUCINATION_MARKERS if m in lower]
		r_hits = [m for m in self.REAL_MARKERS if m in lower]

		base = min(len(r_hits) * 0.18, 0.72)
		penalty = min(len(h_hits) * 0.25, 0.9)
		confidence = max(0.0, min(base - penalty + 0.3, 1.0))

		blocked = len(h_hits) > 0 and self.tolerance == 0.0
		is_real = (not blocked) and confidence >= 0.5
		reason = (
			"blocked_hallucination_markers"
			if blocked
			else "verified"
			if is_real
			else "insufficient_signal"
		)

		result = ThinkResult(
			input_text=source,
			output_text=source if is_real else "",
			is_real=is_real,
			confidence=round(confidence, 3),
			blocked_hallucination=blocked,
			reason=reason,
		)
		self._history.append(result)
		return result

	def filter_response(self, response: str) -> Tuple[str, bool]:
		result = self.verify(response)
		if result.blocked_hallucination:
			return "", False
		return response, result.is_real

	@property
	def stats(self) -> Dict[str, Any]:
		if not self._history:
			return {"total": 0, "real": 0, "blocked": 0}
		total = len(self._history)
		real = sum(1 for item in self._history if item.is_real)
		blocked = sum(1 for item in self._history if item.blocked_hallucination)
		avg = sum(item.confidence for item in self._history) / total
		return {
			"total": total,
			"real": real,
			"blocked": blocked,
			"avg_confidence": round(avg, 3),
		}


_thinker_instance: Optional[StrictThinker] = None


def get_thinker(tolerance: float = 0.0) -> StrictThinker:
	global _thinker_instance
	if _thinker_instance is None:
		_thinker_instance = StrictThinker(hallucination_tolerance=tolerance)
	return _thinker_instance

