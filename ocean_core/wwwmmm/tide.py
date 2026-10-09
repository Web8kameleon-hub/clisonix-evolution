# -*- coding: utf-8 -*-
"""WWWMMM tide engine for cadence and temporal flow."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class TideState:
	level: float = 0.5
	cycle: int = 0
	timestamp: float = field(default_factory=time.time)


class TideEngine:
	def __init__(self):
		self._state = TideState()

	def step(self, delta: float = 0.1) -> TideState:
		self._state.level = (self._state.level + float(delta)) % 1.0
		self._state.cycle += 1
		self._state.timestamp = time.time()
		return self._state

	@property
	def state(self) -> TideState:
		return self._state

	@property
	def stats(self) -> Dict[str, float]:
		return {"level": round(self._state.level, 4), "cycle": self._state.cycle}


_tide_instance: TideEngine | None = None


def get_tide() -> TideEngine:
	global _tide_instance
	if _tide_instance is None:
		_tide_instance = TideEngine()
	return _tide_instance

