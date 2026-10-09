# -*- coding: utf-8 -*-
"""WWWMMM memory engines: NanopresureMemory and StigmaFilmMemory."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class MemoryEntry:
	data: Any
	pressure: float
	created_at: float = field(default_factory=time.time)


class NanopresureMemory:
	def __init__(self, capacity: int = 10_000):
		self.capacity = max(1, int(capacity))
		self._entries: List[MemoryEntry] = []

	def store(self, data: Any, pressure: float = 0.5) -> MemoryEntry:
		entry = MemoryEntry(data=data, pressure=max(0.0, min(1.0, float(pressure))))
		self._entries.append(entry)
		if len(self._entries) > self.capacity:
			self._entries.sort(key=lambda e: e.pressure)
			self._entries.pop(0)
		return entry

	def retrieve(self, threshold: float = 0.3) -> List[Any]:
		limit = max(0.0, min(1.0, float(threshold)))
		return [entry.data for entry in self._entries if entry.pressure >= limit]

	@property
	def stats(self) -> Dict[str, Any]:
		if not self._entries:
			return {"count": 0, "avg_pressure": 0.0}
		return {
			"count": len(self._entries),
			"avg_pressure": round(sum(e.pressure for e in self._entries) / len(self._entries), 4),
		}


class StigmaFilmMemory:
	def __init__(self):
		self._films: Dict[str, Dict[str, Any]] = {}

	def write_film(self, film_id: str, content: Any, stigma: float = 0.5) -> None:
		self._films[film_id] = {
			"content": content,
			"stigma": max(0.0, min(1.0, float(stigma))),
			"updated_at": time.time(),
			"access_count": 0,
		}

	def read_film(self, film_id: str) -> Optional[Any]:
		film = self._films.get(film_id)
		if not film:
			return None
		film["access_count"] += 1
		film["updated_at"] = time.time()
		return film["content"]

	def stigmatize(self, film_id: str, delta: float) -> Optional[float]:
		film = self._films.get(film_id)
		if not film:
			return None
		film["stigma"] = max(0.0, min(1.0, film["stigma"] + float(delta)))
		film["updated_at"] = time.time()
		return film["stigma"]

	@property
	def stats(self) -> Dict[str, Any]:
		return {"films": len(self._films)}


_memory_instance: Optional[NanopresureMemory] = None
_film_memory_instance: Optional[StigmaFilmMemory] = None


def get_memory() -> NanopresureMemory:
	global _memory_instance
	if _memory_instance is None:
		_memory_instance = NanopresureMemory()
	return _memory_instance


def get_film_memory() -> StigmaFilmMemory:
	global _film_memory_instance
	if _film_memory_instance is None:
		_film_memory_instance = StigmaFilmMemory()
	return _film_memory_instance

