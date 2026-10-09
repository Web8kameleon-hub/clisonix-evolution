# -*- coding: utf-8 -*-
"""WWWMMM fluid state layer."""

from __future__ import annotations

import time
from typing import Any, Dict


class FluidLayer:
	def __init__(self):
		self._state: Dict[str, Dict[str, Any]] = {}

	def set(self, session_id: str, key: str, value: Any) -> None:
		slot = self._state.setdefault(session_id, {"updated_at": time.time()})
		slot[key] = value
		slot["updated_at"] = time.time()

	def get(self, session_id: str, key: str, default: Any = None) -> Any:
		return self._state.get(session_id, {}).get(key, default)

	def snapshot(self, session_id: str) -> Dict[str, Any]:
		return dict(self._state.get(session_id, {}))


_fluid_instance: FluidLayer | None = None


def get_fluid() -> FluidLayer:
	global _fluid_instance
	if _fluid_instance is None:
		_fluid_instance = FluidLayer()
	return _fluid_instance

