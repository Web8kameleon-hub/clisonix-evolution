# -*- coding: utf-8 -*-
"""
WWWMMM.scanner - Input Scan and Pattern Detection
=================================================
Extracts deterministic lexical patterns for downstream routing.
"""

from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import re
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class ScanResult:
	fingerprint: str
	nanovolt_level: int
	tokens: List[str]
	keywords: List[str]
	has_url: bool
	has_code_fence: bool
	has_question: bool
	confidence: float
	timestamp: float = field(default_factory=time.time)


class SignalScanner:
	"""Low-latency lexical scanner for text-based signals."""

	_KEYWORDS = {
		"routing",
		"signal",
		"mesh",
		"latency",
		"stability",
		"ocean",
		"albi",
		"alba",
		"kloud",
		"clisonix",
		"wwwmmm",
		"nanovolt",
		"scanner",
		"thinker",
		"printer",
	}

	def __init__(self):
		self._history: List[ScanResult] = []
		self._external_scan: Optional[Callable[[str], Any]] = self._load_external_scanner()

	def _load_external_scanner(self) -> Optional[Callable[[str], Any]]:
		"""
		Try to reuse sdk/python/clx/hotguard/scanner_printer.py when present.
		If unavailable, scanner keeps local deterministic path.
		"""
		candidate = (
			Path(__file__).resolve().parents[2]
			/ "sdk"
			/ "python"
			/ "clx"
			/ "hotguard"
			/ "scanner_printer.py"
		)
		if not candidate.exists():
			return None
		spec = importlib.util.spec_from_file_location("clx_scanner_printer", str(candidate))
		if not spec or not spec.loader:
			return None
		module = importlib.util.module_from_spec(spec)
		spec.loader.exec_module(module)
		fn = getattr(module, "scan", None)
		return fn if callable(fn) else None

	def scan(self, text: str) -> ScanResult:
		source = (text or "").strip()
		fingerprint = hashlib.sha256(source.encode("utf-8")).hexdigest()[:16]
		tokens = [t for t in re.findall(r"[A-Za-z0-9_:-]+", source.lower()) if t]
		uniq_tokens = list(dict.fromkeys(tokens))
		keywords = [k for k in uniq_tokens if k in self._KEYWORDS]
		has_url = bool(re.search(r"https?://", source, flags=re.IGNORECASE))
		has_code_fence = "```" in source
		has_question = "?" in source
		nanovolt_level = int(hashlib.md5(source.encode("utf-8")).hexdigest()[:8], 16) % 1000

		confidence_base = min(len(uniq_tokens) / 20.0, 0.6)
		confidence_boost = min(len(keywords) / 10.0, 0.3)
		external_boost = 0.0
		if self._external_scan:
			try:
				ext_result = self._external_scan(source)
				if ext_result:
					external_boost = 0.05
			except Exception:
				external_boost = 0.0
		confidence = min(confidence_base + confidence_boost + external_boost + (0.1 if has_question else 0.0), 1.0)

		result = ScanResult(
			fingerprint=fingerprint,
			nanovolt_level=nanovolt_level,
			tokens=uniq_tokens,
			keywords=keywords,
			has_url=has_url,
			has_code_fence=has_code_fence,
			has_question=has_question,
			confidence=round(confidence, 3),
		)
		self._history.append(result)
		return result

	@property
	def stats(self) -> Dict[str, Any]:
		if not self._history:
			return {"total_scans": 0}
		return {
			"total_scans": len(self._history),
			"avg_confidence": round(
				sum(item.confidence for item in self._history) / len(self._history),
				3,
			),
			"last_nanovolt_level": self._history[-1].nanovolt_level,
			"last_keywords": self._history[-1].keywords,
		}


_scanner_instance: Optional[SignalScanner] = None


def get_scanner() -> SignalScanner:
	global _scanner_instance
	if _scanner_instance is None:
		_scanner_instance = SignalScanner()
	return _scanner_instance

