# -*- coding: utf-8 -*-
"""WWWMMM lighting engine for route intensity decisions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class LightingProfile:
	name: str
	intensity: float


class LightingEngine:
	def __init__(self):
		self._profiles = {
			"lightning": LightingProfile("lightning", 0.95),
			"normal": LightingProfile("normal", 0.65),
			"conservative": LightingProfile("conservative", 0.3),
		}

	def choose(self, nanovolt_level: int) -> LightingProfile:
		if nanovolt_level >= 700:
			return self._profiles["lightning"]
		if nanovolt_level >= 350:
			return self._profiles["normal"]
		return self._profiles["conservative"]

	@property
	def stats(self) -> Dict[str, int]:
		return {"profiles": len(self._profiles)}


_lighting_instance: LightingEngine | None = None


def get_lighting() -> LightingEngine:
	global _lighting_instance
	if _lighting_instance is None:
		_lighting_instance = LightingEngine()
	return _lighting_instance

