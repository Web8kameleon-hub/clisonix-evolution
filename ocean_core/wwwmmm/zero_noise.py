# -*- coding: utf-8 -*-
"""WWWMMM zero-noise cleaner."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict


@dataclass
class NoiseFilter:
	noise_ratio: float
	cleaned_length: int


class ZeroNoise:
	def denoise(self, text: str) -> tuple[str, NoiseFilter]:
		source = text or ""
		cleaned = re.sub(r"\s+", " ", source).strip()
		src_len = max(1, len(source))
		noise_ratio = max(0.0, min(1.0, (len(source) - len(cleaned)) / src_len))
		return cleaned, NoiseFilter(noise_ratio=round(noise_ratio, 4), cleaned_length=len(cleaned))


_zero_noise_instance: ZeroNoise | None = None


def get_zero_noise() -> ZeroNoise:
	global _zero_noise_instance
	if _zero_noise_instance is None:
		_zero_noise_instance = ZeroNoise()
	return _zero_noise_instance

