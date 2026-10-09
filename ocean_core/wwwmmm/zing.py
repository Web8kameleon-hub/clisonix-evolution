# -*- coding: utf-8 -*-
"""WWWMMM zing engine for ultra-fast reaction paths."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class ZingReaction:
	action: str
	latency_ms: float
	timestamp: float = field(default_factory=time.time)


class ZingEngine:
	def __init__(self):
		self._last: Optional[ZingReaction] = None
		self._count = 0

	def react(self, action: str) -> ZingReaction:
		start = time.perf_counter()
		action_name = (action or "noop").strip() or "noop"
		latency_ms = (time.perf_counter() - start) * 1000.0
		reaction = ZingReaction(action=action_name, latency_ms=round(latency_ms, 6))
		self._last = reaction
		self._count += 1
		return reaction

	@property
	def stats(self) -> Dict[str, float]:
		return {
			"count": self._count,
			"last_latency_ms": self._last.latency_ms if self._last else 0.0,
		}


_zing_instance: ZingEngine | None = None


def get_zing() -> ZingEngine:
	global _zing_instance
	if _zing_instance is None:
		_zing_instance = ZingEngine()
	return _zing_instance

