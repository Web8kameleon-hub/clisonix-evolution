"""
OCEAN ECOSYSTEM KNOWLEDGE - Real retrieval grounding for internal CLX/Clisonix
architecture questions (HVOW, HVMOW, GS26, WWWMMM, XLC, GRAM, stigma, MegaLayer)
================================================================================

Why this exists:
Ocean was answering questions about its own internal architecture (e.g. "what
is HVO/HVMOW") by letting the LLM free-associate, because no real grounding
context existed in the chat pipeline for these terms — unlike user-facing
product terms, which already have real documentation wired in via
_build_shared_system_context() (CLISONIX_SYSTEM_PROMPT.md + MODULE_MAP.md).

Note: HVOW (GRAM's internal 6-dimension naming — left/right, up/down,
past/future; see packages/gram/node.py) and HVMOW (the OS-CLX federation
adapter/contract — an external bridge target, not a local engine; see
docs/production/canonical/clisonix_one_capability_audit_2026-09-10.md) are
two distinct, unrelated concepts that merely share similar letters. An
earlier version of this module conflated them under one "hvo" bucket, which
let a GRAM fact get miscited as evidence for an OS-CLX question. They are
kept strictly separate throughout this module.

This module is the internal-architecture equivalent: it indexes real,
existing ecosystem documents (mounted read-only from the actual repo files,
not duplicated/invented) and retrieves the chunks that actually match the
user's query by token overlap — the same proven technique already used by
clx_local_domain_wrapper.py. No generation happens here: this only supplies
real retrieved text as context, exactly like knowledge seeds / shared system
context / mega layer context already do in process_query_full().

NO_FAKE_DATA compliance:
- If no document chunk matches the query, build_context() returns an empty
  string, and the instruction injected alongside it explicitly tells the
  model to say the term is undocumented rather than invent a definition.
- Every retrieved fact is cited with its real source file path.
"""
import logging
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

logger = logging.getLogger("ocean_ecosystem_knowledge")

# Mounted read-only from the real repository files (see docker-compose.yml
# volumes for the ocean-core service) — this list only names them, it does
# not duplicate their content.
DEFAULT_DOCS: Sequence[str] = (
    "docs/production/canonical/clisonix_one_capability_audit_2026-09-10.md",
    "EKOSISTEMI-I-PLOTE.md",
    "CLX_I_STIGMA_README.md",
    "CLX_AI_COMPLETE_TIMELINE.md",
    "CLX_AI_INSTALLATION_GUIDE.md",
    "docs/legal/WWWMMM_IP_MEMO.md",
    "docs/architecture/XLC_RESONANT_READING_MODEL.md",
    "packages/gram/ORIGIN.md",
    "packages/gram/node.py",
)

DOCS_ROOT = Path(os.getenv("ECOSYSTEM_DOCS_ROOT", "/app/ecosystem_docs"))

# Verbatim from clx_local_domain_wrapper.py's DOMAIN_KEYWORDS — real,
# pre-existing ecosystem vocabulary mapping, reused here (not invented) so
# retrieval scoring recognizes CLX-domain terms even with partial/variant
# phrasing in the user's question.
#
# IMPORTANT: "hvow" (GRAM's internal 6-dimension naming: left/right,
# up/down, past/future — see packages/gram/node.py) and "hvmow" (the OS-CLX
# federation adapter/contract — an EXTERNAL bridge target, not a local
# engine; see docs/production/canonical/clisonix_one_capability_audit) are
# two distinct, unrelated concepts that merely share similar letters. They
# were previously conflated under one "hvo" bucket — that was a real bug
# that let a GRAM fact get cited as evidence for an OS-CLX question. Keep
# them separate everywhere, including in retrieval scoring.
DOMAIN_KEYWORDS: Dict[str, Sequence[str]] = {
    "wwwmmm": ("wwwmmm", "mmm", "wave matrix", "resonant reading"),
    "hvow": ("hvow", "horizontal", "vertical", "orbital"),
    "hvmow": ("hvmow",),
    "gs26": ("gs26", "albagsengine", "alba gs26 engine"),
    "xlc": ("xlc", "xcl", "codec", "x.l.c", "resonance codec"),
    "clx": ("clx", "clx-i", "clx-hybrid", "clx-agent"),
    "gram": ("gram", "growing resonance adaptive mesh", "mesh node"),
    "os-clx": ("os-clx", "os clx"),
    "megalayer": ("megalayer", "mega layer", "mega-layer", "layer combinations"),
    "stigma": ("stigma", "stigma fluid", "stigma fluid memory", "stigma memory"),
    "nodedb": ("nodedb", "node db", "nodedb fluid", "fluid nodedb"),
    "resonance": ("resonance", "resonant", "resonance score", "resonance endpoint"),
    "nanodecibel": ("nanodecibel", "ndb", "nano decibel", "db"),
    "scanner_printer": ("scanner", "printer", "laser printer", "stream phases"),
    "no_fake_data": ("no fake", "no fallback", "real data", "placeholder"),
}


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z0-9_]+", (text or "").lower())


def _chunk_text(raw: str, source: str, max_chars: int = 800) -> List[Tuple[str, str]]:
    chunks: List[Tuple[str, str]] = []
    current: List[str] = []
    current_len = 0
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if current_len + len(stripped) + 1 > max_chars and current:
            chunks.append((source, "\n".join(current)))
            current = [stripped]
            current_len = len(stripped)
        else:
            current.append(stripped)
            current_len += len(stripped) + 1
    if current:
        chunks.append((source, "\n".join(current)))
    return chunks


@lru_cache(maxsize=1)
def _build_index() -> Tuple[Tuple[str, str], ...]:
    """Index real mounted docs once per process. Missing files are skipped
    silently (honest degraded capability, not a crash) and logged once."""
    indexed: List[Tuple[str, str]] = []
    found_any = False
    for rel_path in DEFAULT_DOCS:
        abs_path = DOCS_ROOT / rel_path
        if not abs_path.exists() or not abs_path.is_file():
            continue
        found_any = True
        try:
            raw = abs_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        indexed.extend(_chunk_text(raw, rel_path))
    if not found_any:
        logger.warning(f"ecosystem_knowledge: no documents found under {DOCS_ROOT}")
    else:
        logger.info(f"ecosystem_knowledge: indexed {len(indexed)} chunks from {DOCS_ROOT}")
    return tuple(indexed)


def map_domain_terms(query: str) -> Dict[str, List[str]]:
    normalized = (query or "").lower()
    mapped: Dict[str, List[str]] = {}
    for concept, variants in DOMAIN_KEYWORDS.items():
        hits = [token for token in variants if token in normalized]
        if hits:
            mapped[concept] = hits
    return mapped


def retrieve(query: str, max_chunks: int = 3) -> List[Tuple[str, str, int]]:
    """Return up to max_chunks (source, text, score) real chunks ranked by
    token overlap with the query. Empty list means no genuine match — the
    caller must not fabricate a substitute."""
    q_tokens = set(_tokenize(query))
    if not q_tokens:
        return []

    mapped_concepts = map_domain_terms(query)
    concept_tokens: set = set()
    for concept, hits in mapped_concepts.items():
        concept_tokens.add(concept)
        for hit in hits:
            concept_tokens.update(_tokenize(hit))

    ranked: List[Tuple[str, str, int]] = []
    for source, text in _build_index():
        c_tokens = set(_tokenize(text))
        overlap = len(q_tokens & c_tokens) + 2 * len(concept_tokens & c_tokens)
        if overlap > 0:
            ranked.append((source, text, overlap))

    ranked.sort(key=lambda item: item[2], reverse=True)
    return ranked[:max_chunks]


def build_context(query: str, max_chunks: int = 3) -> str:
    """Build a real, cited context block for the enhanced prompt, or an
    empty string if nothing genuinely matched (never a fabricated filler)."""
    chunks = retrieve(query, max_chunks=max_chunks)
    if not chunks:
        return ""

    lines = ["## Ecosystem Knowledge (Retrieved, Real Sources Only)"]
    for source, text, _score in chunks:
        lines.append(f"[source:{source}]\n{text}")
    lines.append(
        "\nGROUNDING RULE: The block above is the ONLY verified internal-architecture "
        "context available for this query. If it does not fully define a term the user "
        "asked about, say explicitly that the detail is not documented/verified yet — "
        "do not invent an expansion, organization, or meaning for it."
    )
    return "\n\n".join(lines)


_CERTAINTY_PATTERNS = {
    "sq": ("cfare di me siguri", "çfarë di me siguri", "cka dihet me siguri",
           "c'dihet me siguri", "sa i sigurt je", "a je i sigurt"),
    "en": ("what do you know for certain", "what do you know with certainty",
           "what is known for certain", "how sure are you about"),
    "de": ("was weißt du mit sicherheit", "was ist sicher bekannt"),
}

# A chunk counts as carrying a "definition/fact" (not just a name-drop) when
# it has an explicit defining marker: parenthetical expansion, "=", "means",
# "stands for", "is a/an ...", or one of the audit-style factual verbs used
# in docs/production/canonical/*.md ("exposes", "integrates", "contains",
# "confirms", "exists as", "defines", "implements", "is already"). A bare
# bullet like "- HVO Memory" with none of these does not count — that is a
# *name*, not a documented fact.
_DEFINITION_MARKERS = re.compile(
    r"(\([^)]{3,80}\)|=\s*\S|\bmeans\s+\S|\bstands for\s+\S|\bis an?\b\s+\S"
    r"|\bexposes\b|\bintegrates\b|\bcontains\b|\bconfirms\b|\bexists as\b"
    r"|\bdefines\b|\bimplements\b|\bis already\b|\balready (exists|linked)\b)",
    re.IGNORECASE,
)


def detect_certainty_question(query: str) -> bool:
    normalized = (query or "").strip().lower()
    return any(p in normalized for patterns in _CERTAINTY_PATTERNS.values() for p in patterns)


# Strict name-only variants used for the certainty-check's chunk scan.
# DOMAIN_KEYWORDS above is intentionally loose (includes associated concepts
# like "resonance", "horizontal") to help retrieve() rank broadly related
# chunks for the general context builder — but that same looseness would let
# an unrelated chunk about e.g. "resonance" look like a "confirmed fact"
# about HVOW specifically. The certainty check needs the opposite precision
# bias: only the term's actual name forms count as "this chunk is about this
# concept". HVOW and HVMOW are deliberately kept separate (see note above).
_STRICT_CONCEPT_NAMES: Dict[str, Sequence[str]] = {
    "hvow": ("hvow",),
    "hvmow": ("hvmow",),
    "gs26": ("gs26",),
    "wwwmmm": ("wwwmmm",),
    "xlc": ("xlc", "x.l.c"),
    "clx": ("clx",),
    "gram": ("gram",),
    "os-clx": ("os-clx",),
    "megalayer": ("megalayer", "mega layer", "mega-layer"),
    "stigma": ("stigma",),
    "nodedb": ("nodedb", "node db"),
    "resonance": ("resonance",),
    "nanodecibel": ("nanodecibel", "ndb"),
    "scanner_printer": ("scanner-printer", "scanner printer"),
    "no_fake_data": ("no fake data", "no_fake_data"),
}


def _excerpt_around(text: str, variants: Sequence[str], window: int = 140) -> str:
    """Return a cleaned excerpt centered on the first matched keyword
    occurrence, instead of always truncating from the start of the chunk —
    so the citation actually shows the sentence that mentions the concept."""
    clean = re.sub(r"\s+", " ", text.strip().replace("\n", " "))
    low = clean.lower()
    pos = -1
    for variant in variants:
        idx = low.find(variant)
        if idx != -1 and (pos == -1 or idx < pos):
            pos = idx
    if pos == -1:
        return clean[:280]
    start = max(0, pos - window)
    end = min(len(clean), pos + window)
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(clean) else ""
    return f"{prefix}{clean[start:end]}{suffix}"


def _concept_facts(concept: str) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
    """Return (defined, bare) for a single concept, each a list of
    (source, excerpt) pairs, scanning indexed real document chunks. Uses
    strict name-only matching so a chunk is only ever credited to the
    concept it actually names. Operating at chunk (not line) granularity
    lets this catch real multi-sentence prose facts (e.g. audit-report
    paragraphs), not just single-line bullets."""
    variants = _STRICT_CONCEPT_NAMES.get(concept, (concept,))
    defined: List[Tuple[str, str]] = []
    bare: List[Tuple[str, str]] = []
    seen: set = set()
    for source, text in _build_index():
        low = text.lower()
        if not any(variant in low for variant in variants):
            continue
        key = (source, text[:80])
        if key in seen:
            continue
        seen.add(key)
        excerpt = _excerpt_around(text, variants)
        if _DEFINITION_MARKERS.search(text):
            defined.append((source, excerpt))
        else:
            bare.append((source, excerpt))
    return defined, bare


def build_certainty_answer(query: str, lang_code: str) -> Optional[str]:
    """Deterministic, non-generative answer for explicit "what do you know
    for certain" questions about CLX/Clisonix internal-architecture terms.

    This bypasses the LLM entirely for this narrow case because free
    generation was observed to invent plausible-sounding but fake acronym
    expansions (e.g. "HVO = High-Voltage Oscillation") even when instructed
    not to. Every line below is quoted verbatim from an indexed real file.
    """
    if not detect_certainty_question(query):
        return None

    mapped = map_domain_terms(query)
    if not mapped:
        return None

    confirmed: List[str] = []
    undocumented: List[str] = []
    for concept in mapped:
        defined, bare = _concept_facts(concept)
        if defined:
            cited = "; ".join(f"\"{excerpt}\" [{source}]" for source, excerpt in defined[:2])
            confirmed.append(f"{concept.upper()}: {cited}")
        elif bare:
            source, excerpt = bare[0]
            undocumented.append(f"{concept.upper()} (mentioned only as: \"{excerpt}\" [{source}], no definition found)")
        else:
            undocumented.append(f"{concept.upper()} (no indexed document mentions it)")

    if not confirmed and not undocumented:
        return None

    if lang_code == "sq":
        parts = ["Kontrollova direkt dokumentet e indeksuara të ekosistemit (jo supozime):"]
        if confirmed:
            parts.append("Konfirmuar nga dokumentacioni:\n- " + "\n- ".join(confirmed))
        if undocumented:
            parts.append(
                "Jo e dokumentuar ende (nuk shpik kuptim):\n- " + "\n- ".join(undocumented)
            )
        parts.append("Këto hollësi kërkojnë dokumentacion shtesë nga ekipi përpara se të konfirmohen si fakte.")
        return "\n\n".join(parts)

    if lang_code == "de":
        parts = ["Ich habe direkt die indexierten Ökosystem-Dokumente geprüft (keine Vermutungen):"]
        if confirmed:
            parts.append("Durch Dokumentation bestätigt:\n- " + "\n- ".join(confirmed))
        if undocumented:
            parts.append("Noch nicht dokumentiert (keine erfundene Bedeutung):\n- " + "\n- ".join(undocumented))
        parts.append("Diese Details benötigen zusätzliche Dokumentation vom Team, bevor sie als Fakten gelten.")
        return "\n\n".join(parts)

    parts = ["I checked the indexed ecosystem documents directly (not guessing):"]
    if confirmed:
        parts.append("Confirmed by documentation:\n- " + "\n- ".join(confirmed))
    if undocumented:
        parts.append("Not documented yet (no invented meaning):\n- " + "\n- ".join(undocumented))
    parts.append("These details require additional documentation from the team before they can be treated as facts.")
    return "\n\n".join(parts)
