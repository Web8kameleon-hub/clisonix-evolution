# -*- coding: utf-8 -*-
"""
WWWMMM.printer - Raw SSE/Text Renderer
======================================
Renders WWWMMM outputs without json.dumps.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Iterator, Optional


class PrintFormat(str, Enum):
	SSE = "sse"
	PLAIN = "plain"
	MARKDOWN = "markdown"


class StructuredPrinter:
	"""Deterministic renderer used by WWWMMM pipelines."""

	def __init__(self, default_format: PrintFormat = PrintFormat.SSE):
		self.default_format = default_format

	def render_plain(self, payload: Dict[str, Any]) -> str:
		content = str(payload.get("response") or payload.get("content") or "")
		return content.strip()

	def render_markdown(self, payload: Dict[str, Any]) -> str:
		content = self.render_plain(payload)
		meta = payload.get("meta")
		if not isinstance(meta, dict):
			return content
		lines = [content, "", "## meta"]
		for key, value in meta.items():
			lines.append(f"- {key}: {value}")
		return "\n".join(lines).strip()

	def render_sse_events(self, payload: Dict[str, Any], chunk_size: int = 20) -> Iterator[str]:
		"""Yield raw SSE lines without JSON encoding."""
		text = self.render_plain(payload)
		if not text:
			yield "data: [NO_DATA]\n\n"
			yield "data: [DONE]\n\n"
			return
		for i in range(0, len(text), max(1, chunk_size)):
			chunk = text[i : i + max(1, chunk_size)]
			yield f"data: {chunk}\n\n"
		yield "data: [DONE]\n\n"

	def render(self, payload: Dict[str, Any], fmt: Optional[PrintFormat] = None) -> str:
		target = fmt or self.default_format
		if target == PrintFormat.SSE:
			return "".join(self.render_sse_events(payload))
		if target == PrintFormat.MARKDOWN:
			return self.render_markdown(payload)
		return self.render_plain(payload)


_printer_instance: Optional[StructuredPrinter] = None


def get_printer() -> StructuredPrinter:
	global _printer_instance
	if _printer_instance is None:
		_printer_instance = StructuredPrinter()
	return _printer_instance

