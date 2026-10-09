# -*- coding: utf-8 -*-
"""WWWMMM stigma profile engine (lightning, normal, conservative)."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class StigmaProfile(str, Enum):
	LIGHTNING = "lightning"
	NORMAL = "normal"
	CONSERVATIVE = "conservative"


@dataclass
class StigmaState:
	profile: StigmaProfile
	speed: float
	depth: float
	tolerance: float
	timestamp: float = field(default_factory=time.time)


class StigmaEngine:
	_PROFILES: Dict[StigmaProfile, Dict[str, float]] = {
		StigmaProfile.LIGHTNING: {"speed": 0.95, "depth": 0.35, "tolerance": 0.85},
		StigmaProfile.NORMAL: {"speed": 0.65, "depth": 0.65, "tolerance": 0.6},
		StigmaProfile.CONSERVATIVE: {"speed": 0.3, "depth": 0.9, "tolerance": 0.35},
	}

	def __init__(self, default_profile: StigmaProfile = StigmaProfile.NORMAL):
		self._state = self._state_for(default_profile)
		self._film_stigma: Dict[str, float] = {}

	def _state_for(self, profile: StigmaProfile) -> StigmaState:
		cfg = self._PROFILES[profile]
		return StigmaState(profile=profile, speed=cfg["speed"], depth=cfg["depth"], tolerance=cfg["tolerance"])

	def set_profile(self, profile: str) -> StigmaState:
		try:
			target = StigmaProfile(profile.lower().strip())
		except Exception:
			target = StigmaProfile.NORMAL
		self._state = self._state_for(target)
		return self._state

	def choose_profile(self, nanovolt_level: int) -> StigmaState:
		if nanovolt_level >= 700:
			return self.set_profile(StigmaProfile.LIGHTNING.value)
		if nanovolt_level >= 350:
			return self.set_profile(StigmaProfile.NORMAL.value)
		return self.set_profile(StigmaProfile.CONSERVATIVE.value)

	def analyze(self, scan_payload: Dict[str, Any]) -> Dict[str, Any]:
		level = int(scan_payload.get("nanovolt_level", 0))
		state = self.choose_profile(level)
		return {
			"profile": state.profile.value,
			"speed": state.speed,
			"depth": state.depth,
			"tolerance": state.tolerance,
			"nanovolt_level": level,
			"timestamp": state.timestamp,
		}

	def stigmatize_film(self, film_id: str, delta: float) -> float:
		current = self._film_stigma.get(film_id, 0.5)
		updated = max(0.0, min(1.0, current + float(delta)))
		self._film_stigma[film_id] = updated
		return updated

	def film_stigma(self, film_id: str) -> Optional[float]:
		return self._film_stigma.get(film_id)

	@property
	def state(self) -> StigmaState:
		return self._state


_stigma_instance: Optional[StigmaEngine] = None


def get_stigma() -> StigmaEngine:
	global _stigma_instance
	if _stigma_instance is None:
		_stigma_instance = StigmaEngine()
	return _stigma_instance

