from __future__ import annotations

import importlib
import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable

_SUPPORTED_LANGS = ("sq", "en", "de", "fr")


@dataclass(frozen=True)
class GreetingMatch:
    language: str
    response: str


def _normalize_text(text: str) -> str:
    lower = (text or "").strip().lower()
    lower = lower.replace("’", "'")
    lower = re.sub(r"[!?.,;:]+", "", lower)
    lower = re.sub(r"\s+", " ", lower)
    return lower


def _candidate_forms(text: str) -> Iterable[str]:
    normalized = _normalize_text(text)
    if not normalized:
        return []

    forms = {normalized}
    forms.add(normalized.replace("ë", "e"))
    forms.add(normalized.replace("ç", "c"))
    forms.add(normalized.replace("ë", "e").replace("ç", "c"))
    forms.add(normalized.replace("ë", "").replace("ç", "c"))
    return [f for f in forms if f]


@lru_cache(maxsize=8)
def _load_language_pack(lang: str) -> tuple[set[str], str] | None:
    if lang not in _SUPPORTED_LANGS:
        return None

    module = importlib.import_module(f"dictionaries.languages.{lang}")
    greetings = getattr(module, "GREETINGS", None)
    response = getattr(module, "RESPONSE", None)

    if not isinstance(greetings, set) or not isinstance(response, str):
        return None

    return greetings, response


def match_greeting(message: str, language_hint: str | None = None) -> GreetingMatch | None:
    forms = _candidate_forms(message)
    if not forms:
        return None

    language_order = []
    if language_hint and language_hint in _SUPPORTED_LANGS:
        language_order.append(language_hint)
    for lang in _SUPPORTED_LANGS:
        if lang not in language_order:
            language_order.append(lang)

    for lang in language_order:
        pack = _load_language_pack(lang)
        if not pack:
            continue
        greetings, response = pack

        for form in forms:
            if form in greetings:
                return GreetingMatch(language=lang, response=response)

    return None
