#!/usr/bin/env python3
"""CLX local domain wrapper for WWWMMM/XLC/nanodecibel questions.

This module adds:
- domain term mapping for CLX vocabulary
- lightweight local retrieval over authoritative repo files
- deterministic prompting defaults (low temperature)
- optional local backends (GPT4All and llama.cpp)
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

DEFAULT_SOURCE_FILES = [
    "docs/legal/WWWMMM_IP_MEMO.md",
    "docs/legal/de/dpma-handoff-2026-05-09/DE_EN_CLAIMS_WWWMMM_NDB_STIGMA_v1.md",
    "docs/legal/de/wipo-ready-2026-05-09/DE_EN_CLAIMS_WWWMMM_NDB_STIGMA_v1.md",
    "docs/architecture/XLC_RESONANT_READING_MODEL.md",
    "CLX_I_STIGMA_README.md",
    "CLISONIX_MODULE_MAP.md",
    "CLX_AI_INSTALLATION_GUIDE.md",
    "sdk/python/clx/hotguard/stigma_profiles.py",
    "sdk/python/clx/hotguard/scanner_printer.py",
]

DOMAIN_KEYWORDS: Dict[str, Sequence[str]] = {
    "wwwmmm": ("wwwmmm", "mmm", "wave matrix", "resonant reading"),
    "hvo": ("hvo", "horizontal", "vertical", "orbital", "resonance", "film", "stigma memory"),
    "xlc": ("xlc", "xcl", "codec", "x.l.c", "resonance codec"),
    "clx": ("clx", "clx-i", "clx-hybrid", "clx-agent"),
    "cli": ("cli", "command line", "terminal", "shell"),
    "stigma": ("stigma", "stigma fluid", "stigma fluid memory"),
    "nodedb": ("nodedb", "node db", "nodedb fluid", "fluid nodedb"),
    "resonance": ("resonance", "resonant", "resonance score", "resonance endpoint"),
    "nanodecibel": ("nanodecibel", "ndb", "nano decibel", "db"),
    "scanner_printer": ("scanner", "printer", "laser printer", "stream phases"),
    "no_fake_data": ("no fake", "no fallback", "real data", "placeholder"),
}


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z0-9_]+", (text or "").lower())


def _chunk_text(raw: str, max_chars: int = 800) -> List[str]:
    chunks: List[str] = []
    current: List[str] = []
    current_len = 0
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        if current_len + len(line) + 1 > max_chars and current:
            chunks.append("\n".join(current))
            current = [line]
            current_len = len(line)
        else:
            current.append(line)
            current_len += len(line) + 1
    if current:
        chunks.append("\n".join(current))
    return chunks


@dataclass
class RetrievedChunk:
    source: str
    text: str
    score: int


class _NoModelBackend:
    def generate(self, prompt: str, generation_kwargs: Dict[str, Any]) -> str:
        raise RuntimeError("No local model backend is available")


class GPT4AllBackend:
    def __init__(self, model_path: str):
        from gpt4all import GPT4All

        self._client = GPT4All(model_name=model_path)

    def generate(self, prompt: str, generation_kwargs: Dict[str, Any]) -> str:
        local_kwargs = {
            "temp": generation_kwargs.get("temp", 0.15),
            "max_tokens": generation_kwargs.get("max_tokens", 320),
            "top_p": generation_kwargs.get("top_p", 0.85),
        }
        with self._client.chat_session():
            return str(self._client.generate(prompt, **local_kwargs)).strip()


class LlamaCppBackend:
    def __init__(self, model_path: str):
        from llama_cpp import Llama

        self._llm = Llama(model_path=model_path, n_ctx=4096)

    def generate(self, prompt: str, generation_kwargs: Dict[str, Any]) -> str:
        local_kwargs = {
            "temperature": generation_kwargs.get("temp", 0.15),
            "max_tokens": generation_kwargs.get("max_tokens", 320),
            "top_p": generation_kwargs.get("top_p", 0.85),
        }
        response = self._llm.create_completion(prompt=prompt, **local_kwargs)
        if isinstance(response, dict):
            choices = response.get("choices") or []
            if choices:
                first = choices[0]
                if isinstance(first, dict):
                    return str(first.get("text", "")).strip()
            return ""

        # Streaming iterator: concatenate partial text chunks.
        chunks: List[str] = []
        for item in response:
            if isinstance(item, dict):
                choices = item.get("choices") or []
                if choices and isinstance(choices[0], dict):
                    part = choices[0].get("text")
                    if isinstance(part, str) and part:
                        chunks.append(part)
        return "".join(chunks).strip()


class CLXDomainPromptWrapper:
    def __init__(
        self,
        workspace_root: str,
        source_files: Optional[Sequence[str]] = None,
        backend: Optional[Any] = None,
    ) -> None:
        self.workspace_root = Path(workspace_root)
        self.source_files = list(source_files or DEFAULT_SOURCE_FILES)
        self.backend = backend or _NoModelBackend()
        self._indexed: List[RetrievedChunk] = []
        self._build_index()

    @classmethod
    def create_with_auto_backend(
        cls,
        workspace_root: str,
        model_path: Optional[str] = None,
        preferred_backend: str = "auto",
    ) -> "CLXDomainPromptWrapper":
        model_path = (model_path or os.getenv("CLX_LOCAL_MODEL_PATH") or "").strip()
        backend_name = (preferred_backend or os.getenv("CLX_LOCAL_BACKEND") or "auto").lower()
        backend: Any = _NoModelBackend()

        if model_path:
            if backend_name in ("auto", "gpt4all"):
                try:
                    backend = GPT4AllBackend(model_path=model_path)
                except Exception:
                    backend = _NoModelBackend()
            if isinstance(backend, _NoModelBackend) and backend_name in ("auto", "llama_cpp"):
                try:
                    backend = LlamaCppBackend(model_path=model_path)
                except Exception:
                    backend = _NoModelBackend()

        return cls(workspace_root=workspace_root, backend=backend)

    def map_domain_terms(self, query: str) -> Dict[str, List[str]]:
        normalized = query.lower()
        mapped: Dict[str, List[str]] = {}
        for concept, variants in DOMAIN_KEYWORDS.items():
            hits = [token for token in variants if token in normalized]
            if hits:
                mapped[concept] = hits
        return mapped

    def retrieve_context(self, query: str, max_chunks: int = 3) -> List[RetrievedChunk]:
        normalized_query = (query or "").lower()
        q_tokens = set(_tokenize(query))
        if not q_tokens:
            return []

        ranked: List[RetrievedChunk] = []
        for chunk in self._indexed:
            c_tokens = set(_tokenize(chunk.text))
            overlap = len(q_tokens & c_tokens)
            if overlap > 0:
                score = overlap
                source_lower = chunk.source.lower()
                if source_lower.endswith(".py") and any("_" in token for token in q_tokens):
                    score += 2
                if "scanner_printer.py" in source_lower and (
                    "resonance_to_nanodecibel" in normalized_query
                    or "scanner printer" in normalized_query
                    or "scanner-printer" in normalized_query
                ):
                    score += 5
                ranked.append(RetrievedChunk(source=chunk.source, text=chunk.text, score=score))

        ranked.sort(key=lambda item: item.score, reverse=True)
        return ranked[:max_chunks]

    def build_system_prompt(self, mapped_terms: Dict[str, List[str]]) -> str:
        concept_line = ", ".join(sorted(mapped_terms.keys())) if mapped_terms else "generic_clx"
        return (
            "You are CLX domain assistant for WWWMMM/XLC. "
            "Use only provided context and explicit CLX domain definitions. "
            "If context is missing, state that data is unavailable instead of inventing facts. "
            f"Focus concepts: {concept_line}."
        )

    def build_augmented_prompt(self, query: str) -> str:
        mapped = self.map_domain_terms(query)
        system_prompt = self.build_system_prompt(mapped)
        context = self.retrieve_context(query=query, max_chunks=3)

        context_lines: List[str] = []
        for idx, chunk in enumerate(context, start=1):
            context_lines.append(f"[source:{idx}:{chunk.source}]\n{chunk.text}")

        joined_context = "\n\n".join(context_lines) if context_lines else "[no_context]"
        return (
            f"SYSTEM:\n{system_prompt}\n\n"
            f"CONTEXT:\n{joined_context}\n\n"
            "INSTRUCTIONS:\n"
            "- answer in concise technical style\n"
            "- include formulas only if present in context\n"
            "- never fabricate missing definitions\n\n"
            f"USER_QUERY:\n{query}\n\n"
            "ANSWER:"
        )

    def answer(self, query: str, temperature: float = 0.15, max_tokens: int = 320) -> Dict[str, Any]:
        prompt = self.build_augmented_prompt(query)
        generation_kwargs = {
            "temp": max(0.0, min(temperature, 0.25)),
            "max_tokens": max_tokens,
            "top_p": 0.85,
        }

        if isinstance(self.backend, _NoModelBackend):
            return {
                "response": None,
                "error": "local_model_backend_unavailable",
                "mapped_terms": self.map_domain_terms(query),
                "context_sources": [chunk.source for chunk in self.retrieve_context(query)],
            }

        response = self.backend.generate(prompt=prompt, generation_kwargs=generation_kwargs)
        return {
            "response": response if response else None,
            "error": None if response else "empty_model_response",
            "mapped_terms": self.map_domain_terms(query),
            "context_sources": [chunk.source for chunk in self.retrieve_context(query)],
        }

    def _build_index(self) -> None:
        indexed: List[RetrievedChunk] = []
        for rel_path in self.source_files:
            abs_path = self.workspace_root / rel_path
            if not abs_path.exists() or not abs_path.is_file():
                continue
            raw = abs_path.read_text(encoding="utf-8", errors="replace")
            for chunk in _chunk_text(raw):
                indexed.append(RetrievedChunk(source=rel_path, text=chunk, score=0))
        self._indexed = indexed


def main() -> int:
    import argparse
    import json

    parser = argparse.ArgumentParser(description="CLX local domain wrapper")
    parser.add_argument("--query", required=True, type=str)
    parser.add_argument("--workspace-root", default=str(Path(__file__).resolve().parent))
    parser.add_argument("--model-path", default=None)
    parser.add_argument("--backend", default="auto", choices=["auto", "gpt4all", "llama_cpp"])
    parser.add_argument("--temperature", type=float, default=0.15)
    parser.add_argument("--max-tokens", type=int, default=320)
    args = parser.parse_args()

    wrapper = CLXDomainPromptWrapper.create_with_auto_backend(
        workspace_root=args.workspace_root,
        model_path=args.model_path,
        preferred_backend=args.backend,
    )
    result = wrapper.answer(query=args.query, temperature=args.temperature, max_tokens=args.max_tokens)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("response") else 1


if __name__ == "__main__":
    raise SystemExit(main())
