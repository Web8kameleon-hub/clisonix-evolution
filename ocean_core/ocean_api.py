"""
OCEAN CORE 8030 API
===================
Standalone FastAPI application - completely isolated from main.py

Port: 8030
Features:
- Query endpoint (natural language → intelligent response)
- Data sources status
- Knowledge exploration
- Curiosity threads
- Document processing (Kitchen integration)
- Real-time spreadsheet generation (Excel Core)
- Voice conversation, reactions, multimedia
"""

import asyncio
import hashlib
import html
import importlib
import importlib.util
import io
import json
import logging
import os
import re
import shutil
import time
from datetime import datetime
from typing import Any
from urllib.parse import quote_plus, urlparse
from uuid import uuid4

# Kitchen + Excel integrations (2026 level)
try:
    from kitchen_integration import kitchen_convert_to_excel, kitchen_process_document
except ImportError:
    kitchen_process_document = None
    kitchen_convert_to_excel = None

try:
    from excel_core_integration import (
        excel_apply_formula,
        excel_create_workbook,
        excel_export,
        excel_get_data,
        excel_insert_rows,
    )
except ImportError:
    excel_create_workbook = None

import httpx
from fastapi import FastAPI, File, HTTPException, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse
from pydantic import BaseModel

# Binary protocol support (CBOR2, MessagePack)
try:
    cbor2 = importlib.import_module("cbor2")
    HAS_CBOR2 = True
except ImportError:
    HAS_CBOR2 = False

try:
    msgpack = importlib.import_module("msgpack")
    HAS_MSGPACK = True
except ImportError:
    HAS_MSGPACK = False

# Local imports - NANOGRID: Minimal
# DISABLED: from query_processor import get_query_processor, QueryIntent
# DISABLED: from knowledge_engine import get_knowledge_engine, KnowledgeResponse
# DISABLED: from persona_router import PersonaRouter
# DISABLED: from laboratories import get_laboratory_network
# DISABLED: from real_data_engine import get_real_data_engine
# DISABLED: from specialized_chat_engine import get_specialized_chat, initialize_specialized_chat
# ORCHESTRATOR - Ollama only
from laboratories import get_laboratory_network
from response_orchestrator_v5 import get_orchestrator_v5

# 72-language text-based detector (no external deps)
try:
    from lang72 import build_language_instruction as _lang72_instruction
    from lang72 import detect_language as _detect_lang72
except ImportError:
    def _detect_lang72(text: str, default: str = "en") -> str:  # type: ignore[misc]
        return default
    def _lang72_instruction(lang_code: str) -> str:  # type: ignore[misc]
        return f"Respond ONLY in the same language as the user's message. Language code: {lang_code}."

_data_sources_module = importlib.import_module("data_sources")


def _get_global_data_connector() -> Any:
    module = importlib.import_module("global_data_sources")
    factory = getattr(module, "get_global_data_connector", None)
    if not callable(factory):
        raise RuntimeError("global_data_sources missing get_global_data_connector")
    return factory()


def get_all_sources() -> Any:
    factory = getattr(_data_sources_module, "get_internal_data_sources", None)
    if callable(factory):
        return factory()

    cls = getattr(_data_sources_module, "InternalDataSources", None)
    if cls is None:
        raise RuntimeError("data_sources module missing InternalDataSources")
    return cls()

# DISABLED: from autolearning_engine import get_autolearning_engine, AutolearningEngine
# DISABLED: Curiosity Algebra - creates loops
# from curiosity_algebra.api import router as curiosity_router


async def get_knowledge_engine_hybrid(data_sources):
    """Create hybrid knowledge engine that only uses internal data"""
    # For now, use the standard knowledge engine but we'll filter external APIs
    # This is a wrapper that ensures no external data is used
    try:
        from knowledge_engine import KnowledgeEngine

        if data_sources is None:
            logger.error("❌ Cannot initialize knowledge engine: data_sources is None!")
            return None

        logger.info("🧠 Initializing KnowledgeEngine with internal data sources...")
        ke = KnowledgeEngine(data_sources, None)  # No external_apis_manager

        if ke is None:
            logger.error("❌ KnowledgeEngine() returned None!")
            return None

        logger.info("⏳ Initializing knowledge engine...")
        await ke.initialize()
        logger.info("✅ Knowledge engine initialized successfully!")
        return ke
    except Exception as e:
        logger.error(f"❌ Error initializing hybrid knowledge engine: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ocean_api")

# API Version prefix - SECURITY REQUIREMENT
API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"
IS_IN_DOCKER = os.path.exists("/.dockerenv") or os.getenv("DOCKER_ENV") == "1"
EXCEL_SERVICE_URL = os.getenv(
    "EXCEL_SERVICE_URL",
    "http://clisonix-excel:8002" if IS_IN_DOCKER else "http://localhost:8002",
)
INTELLIGENCE_LAB_SIGNAL_URLS = [
    url.strip()
    for url in (
        os.getenv("INTELLIGENCE_LAB_SIGNAL_URLS")
        or (
            "http://clisonix-intelligence-lab:8098/klajdi/signal"
            if IS_IN_DOCKER
            else "http://localhost:8098/klajdi/signal"
        )
    ).split(",")
    if url.strip()
]
INTELLIGENCE_SIGNAL_TIMEOUT = float(os.getenv("INTELLIGENCE_SIGNAL_TIMEOUT", "0.8"))
DOCUMENT_MAX_BYTES = int(os.getenv("DOCUMENT_MAX_BYTES", str(25 * 1024 * 1024)))

DOCUMENT_MIME_ALLOWLIST = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/json",
    "text/plain",
    "text/csv",
    "text/markdown",
}

# Initialize FastAPI app
app = FastAPI(
    title="Curiosity Ocean",
    description="Universal Knowledge Aggregation Engine with 14 Expert Personas - Internal + External Free Data Sources",
    version="4.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DISABLED: Curiosity Algebra - creates loops
# app.include_router(curiosity_router)
# logger.info("✅ Curiosity Algebra System integrated - /api/curiosity endpoints active")

# Global instances - NANOGRID: Minimal
internal_data_sources: Any = None
persona_router: Any = None
query_processor: Any = None
knowledge_engine: Any = None
laboratory_network: Any = None
real_data_engine: Any = None
specialized_chat: Any = None
orchestrator: Any = None
autolearning_engine: Any = None  # New: Autolearning Engine


def _get_orchestrator_runtime() -> dict[str, Any]:
    """Return the real runtime state of the active orchestrator."""
    runtime: dict[str, Any] = {
        "mode": "unavailable",
        "ollama_active": False,
        "specialized_chat_active": specialized_chat is not None,
        "knowledge_seeds_available": False,
        "knowledge_seeds_active": False,
        "mega_layers_available": False,
        "mega_layers_active": False,
        "universal_connector": False,
        "alphabet_layers": 0,
    }

    if not orchestrator:
        return runtime

    runtime["mode"] = "orchestrator_v5_minimal"
    runtime["ollama_active"] = getattr(orchestrator, "ollama_engine", None) is not None
    runtime["mega_layers_active"] = getattr(orchestrator, "mega_layer_engine", None) is not None
    runtime["universal_connector"] = getattr(orchestrator, "universal_connector", None) is not None

    alphabet_layers = getattr(orchestrator, "alphabet_layers", None)
    if alphabet_layers and hasattr(alphabet_layers, "alphabet"):
        runtime["alphabet_layers"] = alphabet_layers.alphabet.get("size", 0)
        runtime["mode"] = "orchestrator_full"

    try:
        orch_module = importlib.import_module("response_orchestrator_v5")
        runtime["knowledge_seeds_available"] = bool(getattr(orch_module, "KNOWLEDGE_SEEDS_AVAILABLE", False))
        runtime["mega_layers_available"] = bool(getattr(orch_module, "MEGA_LAYERS_AVAILABLE", False))
    except Exception:
        pass

    return runtime


def _get_mega_signal_status() -> dict[str, Any]:
    """Return read-safe Mega Signal Integrator status."""
    try:
        from mega_signal_integrator import get_mega_signal_integrator

        integrator = get_mega_signal_integrator()
        overview = integrator.get_system_overview()
        return {
            "status": "connected",
            "overview": overview,
        }
    except Exception as e:
        return {
            "status": "unavailable",
            "error": str(e),
        }


UNIFIED_LAYER_STAGES: list[dict[str, Any]] = [
    {
        "depth": 0.5,
        "name": "foundation_awareness",
        "focus": "input-grounding",
        "governance": "strict",
    },
    {
        "depth": 1.0,
        "name": "context_ingest",
        "focus": "facts-and-context",
        "governance": "strict",
    },
    {
        "depth": 2.0,
        "name": "signal_mapping",
        "focus": "saas-signal-routing",
        "governance": "strict",
    },
    {
        "depth": 3.0,
        "name": "pattern_alignment",
        "focus": "cross-source-alignment",
        "governance": "balanced",
    },
    {
        "depth": 4.0,
        "name": "reasoning_core",
        "focus": "structured-reasoning",
        "governance": "balanced",
    },
    {
        "depth": 5.0,
        "name": "persona_blending",
        "focus": "persona-aware-response",
        "governance": "balanced",
    },
    {
        "depth": 6.0,
        "name": "creative_planning",
        "focus": "md-table-figure-design",
        "governance": "balanced",
    },
    {
        "depth": 7.0,
        "name": "creator_orchestration",
        "focus": "painting-music-video-design",
        "governance": "balanced",
    },
    {
        "depth": 8.0,
        "name": "statistical_excel_core",
        "focus": "excel-doc-stats-pipelines",
        "governance": "balanced",
    },
    {
        "depth": 9.0,
        "name": "service_mesh_linking",
        "focus": "internal-external-api-composition",
        "governance": "guided",
    },
    {
        "depth": 10.0,
        "name": "agentic_feedback",
        "focus": "autolearning-feedback-loops",
        "governance": "guided",
    },
    {
        "depth": 11.0,
        "name": "hybrid_cognition",
        "focus": "feeling-thinking-synthesis",
        "governance": "guided",
    },
    {
        "depth": 12.0,
        "name": "executive_orchestrator",
        "focus": "full-system-execution",
        "governance": "policy-and-human-oversight",
    },
]


COGNITIVE_MODES: dict[str, dict[str, Any]] = {
    "feeling": {
        "temperature": 0.85,
        "style": "empathetic-creative",
        "response_bias": "human-centered",
    },
    "thinking": {
        "temperature": 0.45,
        "style": "analytical-structured",
        "response_bias": "evidence-first",
    },
    "hybrid": {
        "temperature": 0.65,
        "style": "empathetic-analytical",
        "response_bias": "balanced",
    },
}


CREATOR_CAPABILITIES: dict[str, str] = {
    "markdown_docs": "md_document_generator",
    "tables_and_figures": "structured_output_builder",
    "painting_creator": "prompt_to_visual_pipeline",
    "music_creator": "audio_generation_pipeline",
    "video_creator": "video_generation_pipeline",
    "design_architect": "design_system_orchestrator",
    "excel_core": "excel_document_stats_processor",
}


def _get_unified_layer_stage(requested_depth: float) -> dict[str, Any]:
    ordered = sorted(UNIFIED_LAYER_STAGES, key=lambda item: float(item["depth"]))
    selected = ordered[0]
    for stage in ordered:
        if float(stage["depth"]) <= requested_depth:
            selected = stage
        else:
            break
    return selected


def _compute_ocean_validation_summary() -> dict[str, Any]:
    orchestrator_runtime = _get_orchestrator_runtime()
    mega_signal = _get_mega_signal_status()

    checks = {
        "apps_api_main": {
            "path": "apps/api/main.py",
            "present": _repo_file_exists("apps/api/main.py"),
        },
        "services_api_main": {
            "path": "services/api/main.py",
            "present": _repo_file_exists("services/api/main.py"),
        },
        "saas_signal_api": {
            "path": "apps/api/saas_signal_api.py",
            "present": _repo_file_exists("apps/api/saas_signal_api.py"),
        },
        "unified_layers": {
            "min_depth": 0.5,
            "max_depth": 12.0,
            "count": len(UNIFIED_LAYER_STAGES),
            "present": len(UNIFIED_LAYER_STAGES) > 0,
        },
        "ocean_full_runtime": {
            "path": "ocean-core/ocean_core_full.py",
            "present": _repo_file_exists("ocean-core/ocean_core_full.py"),
        },
    }

    total = len(checks)
    passed = sum(1 for check in checks.values() if check.get("present", True))
    signal_paths = [path for route in app.routes for path in [getattr(route, "path", "")] if path.startswith(f"{API_PREFIX}/signals")]
    pulse_paths = [path for route in app.routes for path in [getattr(route, "path", "")] if path.startswith(f"{API_PREFIX}/pulse")]

    return {
        "status": "ok" if passed == total else "degraded",
        "score": round((passed / total) * 100, 2),
        "checks": checks,
        "routes": {
            "signals_count": len(signal_paths),
            "pulse_count": len(pulse_paths),
            "signals_sample": sorted(signal_paths)[:8],
            "pulse_sample": sorted(pulse_paths)[:8],
        },
        "runtime": {
            "orchestrator": orchestrator_runtime,
            "mega_signal": mega_signal,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


# Full 72-language name map shared by prompt builders
_LANG_NAMES: dict[str, str] = {
    "sq": "Albanian", "en": "English", "de": "German", "es": "Spanish",
    "fr": "French", "it": "Italian", "pt": "Portuguese", "nl": "Dutch",
    "sv": "Swedish", "no": "Norwegian", "da": "Danish", "fi": "Finnish",
    "pl": "Polish", "cs": "Czech", "sk": "Slovak", "sl": "Slovenian",
    "hr": "Croatian", "sr": "Serbian", "bg": "Bulgarian", "ro": "Romanian",
    "hu": "Hungarian", "ru": "Russian", "uk": "Ukrainian", "be": "Belarusian",
    "el": "Greek", "tr": "Turkish", "he": "Hebrew", "ar": "Arabic",
    "fa": "Persian", "ur": "Urdu", "hi": "Hindi", "bn": "Bengali",
    "ta": "Tamil", "te": "Telugu", "mr": "Marathi", "gu": "Gujarati",
    "pa": "Punjabi", "ml": "Malayalam", "kn": "Kannada", "or": "Odia",
    "as": "Assamese", "ne": "Nepali", "si": "Sinhala", "th": "Thai",
    "my": "Burmese", "km": "Khmer", "lo": "Lao", "vi": "Vietnamese",
    "id": "Indonesian", "ms": "Malay", "tl": "Filipino", "sw": "Swahili",
    "am": "Amharic", "ha": "Hausa", "yo": "Yoruba", "ig": "Igbo",
    "zu": "Zulu", "xh": "Xhosa", "af": "Afrikaans", "et": "Estonian",
    "lv": "Latvian", "lt": "Lithuanian", "mt": "Maltese", "ga": "Irish",
    "cy": "Welsh", "is": "Icelandic", "mk": "Macedonian", "bs": "Bosnian",
    "kk": "Kazakh", "uz": "Uzbek", "ky": "Kyrgyz", "mn": "Mongolian",
    "ka": "Georgian", "hy": "Armenian", "az": "Azerbaijani",
    "ps": "Pashto", "so": "Somali",
    "zh": "Chinese", "ja": "Japanese", "ko": "Korean",
}


OCEAN_DECLARED_OWNER = os.getenv("OCEAN_DECLARED_OWNER", "Ledjan Ahmati")
OCEAN_DECLARED_OWNER_TITLE = os.getenv("OCEAN_DECLARED_OWNER_TITLE", "CEO and Creator")
EXTERNAL_CONTEXT_TIMEOUT_SECONDS = float(os.getenv("OCEAN_EXTERNAL_CONTEXT_TIMEOUT", "8.0"))
EXTERNAL_CONTEXT_MAX_CHARS = int(os.getenv("OCEAN_EXTERNAL_CONTEXT_MAX_CHARS", "2500"))

# Typeahead pre-warm cache: stores pre-built prompts keyed by message prefix
# so when user hits Enter, generation starts with 0 context-fetch wait.
_WARM_CACHE: dict = {}
_WARM_CACHE_MAX = 64  # max entries before LRU eviction


def _build_owner_identity_instruction() -> str:
    return (
        "Identity: You are Curiosity Ocean, a proprietary Clisonix intelligence system. "
        f"The declared owner is {OCEAN_DECLARED_OWNER} ({OCEAN_DECLARED_OWNER_TITLE}). "
        "If ownership/creator is requested, state this identity clearly and consistently."
    )


def _is_medical_query(query: str) -> bool:
    q = (query or "").lower()
    markers = [
        "medical", "medicine", "clinical", "disease", "therapy", "drug", "pubmed",
        "biomedical", "patient", "diagnosis", "health", "neuro", "brain",
    ]
    return any(marker in q for marker in markers)


def _is_research_query(query: str) -> bool:
    q = (query or "").lower()
    markers = [
        "research", "paper", "study", "scientific", "arxiv", "publication", "journal",
        "evidence", "analysis", "experiment", "methodology",
    ]
    return any(marker in q for marker in markers)


def _build_external_context_block(source_payloads: dict[str, Any]) -> str:
    fragments: list[str] = []

    wikipedia = source_payloads.get("wikipedia")
    if isinstance(wikipedia, dict):
        for item in (wikipedia.get("results") or [])[:4]:
            title = str(item.get("title", "")).strip()
            snippet = str(item.get("snippet", "")).strip()
            url = str(item.get("url", "")).strip()
            if title or snippet:
                fragments.append(f"[Wikipedia] {title}: {snippet} ({url})")

    arxiv = source_payloads.get("arxiv")
    if isinstance(arxiv, dict):
        for item in (arxiv.get("papers") or [])[:3]:
            title = str(item.get("title", "")).strip()
            summary = str(item.get("summary", "")).strip()
            url = str(item.get("url", "")).strip()
            if title or summary:
                fragments.append(f"[ArXiv] {title}: {summary} ({url})")

    pubmed = source_payloads.get("pubmed")
    if isinstance(pubmed, dict):
        for item in (pubmed.get("articles") or [])[:3]:
            title = str(item.get("title", "")).strip()
            source = str(item.get("source", "")).strip()
            url = str(item.get("url", "")).strip()
            if title:
                fragments.append(f"[PubMed] {title} | {source} ({url})")

    context = "\n".join(fragment for fragment in fragments if fragment.strip())
    return context[:EXTERNAL_CONTEXT_MAX_CHARS]


async def _collect_external_context_for_query(query: str) -> dict[str, Any]:
    payloads: dict[str, Any] = {}

    async def _capture(name: str, coro: Any) -> None:
        try:
            payloads[name] = await asyncio.wait_for(coro, timeout=EXTERNAL_CONTEXT_TIMEOUT_SECONDS)
        except Exception as exc:
            payloads[name] = {"status": "error", "error": str(exc)}

    tasks = [_capture("wikipedia", research_wikipedia(query=query, limit=5))]
    if _is_research_query(query):
        tasks.append(_capture("arxiv", research_arxiv(query=query, max_results=4)))
    if _is_medical_query(query):
        tasks.append(_capture("pubmed", research_pubmed(query=query, max_results=4)))

    await asyncio.gather(*tasks)

    context_block = _build_external_context_block(payloads)
    used_sources = [name for name, payload in payloads.items() if isinstance(payload, dict) and payload.get("status") != "error"]

    return {
        "sources": used_sources,
        "payloads": payloads,
        "context_block": context_block,
    }


def _compose_enriched_query(
    message: str,
    external_context_block: str,
    conversation_context: list[str] | None = None,
) -> str:
    owner_instruction = _build_owner_identity_instruction()
    runtime_context = _build_runtime_context_block(conversation_context)
    if external_context_block:
        return (
            f"{owner_instruction}\n\n"
            f"{runtime_context}\n\n"
            "Use external factual context below when relevant. Prioritize factual accuracy and cite source names in prose.\n"
            f"\n[External Context]\n{external_context_block}\n\n"
            f"[User Message]\n{message}"
        )
    return f"{owner_instruction}\n\n{runtime_context}\n\n[User Message]\n{message}"


def _build_runtime_context_block(conversation_context: list[str] | None = None) -> str:
    now_local = datetime.now()
    now_utc = datetime.utcnow()
    history_lines = [
        str(line).strip()
        for line in (conversation_context or [])[-12:]
        if isinstance(line, str) and str(line).strip()
    ]
    history_block = "\n".join(f"- {line[:500]}" for line in history_lines)
    if not history_block:
        history_block = "- (no prior history provided in this request)"

    return (
        "[Session Context]\n"
        f"Local datetime: {now_local.isoformat()}\n"
        f"UTC datetime: {now_utc.isoformat()}Z\n"
        f"Conversation history items: {len(history_lines)}\n"
        "Recent history:\n"
        f"{history_block}"
    )


def _build_stream_system_prompt(language: str | None) -> str:
    """Create a streaming-safe language/system instruction for Ollama."""
    lang = (language or "").strip().lower()
    base_instruction = (
        "Give a complete, professional answer in full sentences. "
        "Do NOT switch to English or any other language mid-response. "
        "Do not stop mid-sentence. "
        "If the answer needs multiple paragraphs, continue until the explanation is complete. "
        f"{_build_owner_identity_instruction()}"
    )

    if not lang or lang == "und":
        return (
            "Detect the language of the user's message and respond ENTIRELY in that same language. "
            f"{base_instruction}"
        )

    lang_name = _LANG_NAMES.get(lang, lang.upper())
    return (
        f"CRITICAL INSTRUCTION: The user wrote in {lang_name}. "
        f"You MUST respond ONLY in {lang_name}. "
        f"Every single word in your response must be in {lang_name}. "
        f"Do NOT use English. Do NOT switch languages. "
        f"Language code: {lang}. "
        f"{base_instruction}"
    )


def _normalize_language_code(value: str | None) -> str:
    """Normalize client/header language hints into compact ISO-like codes."""
    raw = str(value or "").strip().lower()
    if not raw:
        return ""
    if raw in {"auto", "und", "undefined", "none", "null"}:
        return ""
    token = raw.split(",")[0].split(";")[0].strip()
    token = token.split("-")[0].split("_")[0].strip()
    if re.fullmatch(r"[a-z]{2,3}", token):
        return token
    return ""


def _extract_user_context_messages(conversation_context: list[str]) -> list[str]:
    messages: list[str] = []
    for line in (conversation_context or [])[-20:]:
        if not isinstance(line, str):
            continue
        cleaned = line.strip()
        if not cleaned:
            continue
        lowered = cleaned.lower()
        if lowered.startswith("user:"):
            messages.append(cleaned[5:].strip())
        elif lowered.startswith("assistant:") or lowered.startswith("system:"):
            continue
        else:
            messages.append(cleaned)
    return messages


def _detect_context_language(conversation_context: list[str]) -> str:
    """Weighted language inference from recent user turns."""
    votes: dict[str, float] = {}
    user_messages = _extract_user_context_messages(conversation_context)
    for idx, text in enumerate(user_messages[-8:]):
        detected = _normalize_language_code(_detect_lang72(text, default=""))
        if not detected:
            continue
        votes[detected] = votes.get(detected, 0.0) + float(idx + 1)

    if not votes:
        return ""
    return max(votes.items(), key=lambda item: item[1])[0]


def resolve_conversation_language(
    message: str,
    conversation_context: list[str] | None = None,
    request_language: str | None = None,
    accept_language: str | None = None,
) -> tuple[str, str]:
    """
    Resolve language from multiple signals for fluid conversation continuity.

    Returns:
        (language_code or "und", source)
    """
    query_lang = _normalize_language_code(_detect_lang72(message or "", default="")) if message else ""
    context_lang = _detect_context_language(conversation_context or [])
    req_lang = _normalize_language_code(request_language)
    header_lang = _normalize_language_code(accept_language)

    if query_lang and context_lang:
        return query_lang, "query_detect"

    if query_lang:
        return query_lang, "query_detect"
    if context_lang:
        return context_lang, "context_flow"
    if req_lang:
        return req_lang, "request_hint"
    if header_lang:
        return header_lang, "accept_language"
    return "und", "auto"


def _language_message(language: str, variants: dict[str, str], default: str) -> str:
    lang = _normalize_language_code(language)
    if lang and lang in variants:
        return variants[lang]
    base_lang = (lang or "").split("-")[0]
    if base_lang and base_lang in variants:
        return variants[base_lang]
    return variants.get("en", default)


async def _publish_ocean_signal(
    event: str,
    message: str,
    language: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    if not INTELLIGENCE_LAB_SIGNAL_URLS:
        return

    payload = {
        "source": "ocean",
        "channel": "http",
        "severity": "info",
        "payload": {
            "event": event,
            "message": (message or "")[:1200],
            "language": language or "und",
        },
        "meta": metadata or {},
    }

    for signal_url in INTELLIGENCE_LAB_SIGNAL_URLS:
        try:
            async with httpx.AsyncClient(timeout=INTELLIGENCE_SIGNAL_TIMEOUT) as client:
                response = await client.post(signal_url, json=payload)
            if 200 <= response.status_code < 300:
                return
        except Exception as exc:
            logger.debug(f"Ocean signal publish failed ({signal_url}): {exc}")


def _publish_ocean_signal_background(
    event: str,
    message: str,
    language: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    try:
        asyncio.create_task(_publish_ocean_signal(event, message, language, metadata))
    except RuntimeError:
        logger.debug("No running loop to publish ocean signal")


SYSTEM_ANATOMY = {
    "layers_layout_governance": {
        "label": "Layers • Layout • Governance",
        "activation_query": "layers layout governance mapping alignment policy",
        "description": "Semantic layers, routing layout, governance and alignment policies.",
    },
    "powernance_provenance": {
        "label": "Powernance • Provenance",
        "activation_query": "provenance powernance trace trust",
        "description": "Data trust, provenance lineage, activation traceability.",
    },
    "excel_core": {
        "label": "Excel Core",
        "activation_query": "excel spreadsheet csv data table process",
        "description": "Excel/data-table processing and analytics pathways.",
    },
    "openmind_core": {
        "label": "OpenMind Core",
        "activation_query": "openmind reasoning think orchestrator",
        "description": "OpenMind reasoning bridge and orchestration context.",
    },
    "agents_laboratories": {
        "label": "Agents • Laboratories",
        "activation_query": "agents laboratories specialized roles",
        "description": "Agent systems and laboratory capabilities.",
    },
    "pulse_publish_pillar": {
        "label": "Pulse • Publish • Pillar",
        "activation_query": "pulse publish pillar telemetry stream",
        "description": "Signal pulse, publish flows and core pillars.",
    },
    "asi_saas": {
        "label": "ASI SaaS",
        "activation_query": "asi saas superintelligence service mesh",
        "description": "ASI service domain and SaaS orchestration touchpoints.",
    },
    "internal_apis": {
        "label": "Internal APIs",
        "activation_query": "internal api service routing endpoint",
        "description": "Internal service APIs and cross-service routing.",
    },
    "open_data_sources": {
        "label": "Open Links • Free Data Sources",
        "activation_query": "open data sources free api public datasets",
        "description": "Open/public data sources and discovery graph.",
    },
    "i18n_translate_mapping": {
        "label": "i18n • Translate • Mapping",
        "activation_query": "i18n translate multilingual mapping",
        "description": "Translation and multilingual mapping pathways.",
    },
}


PULSE_ROUTE_ALIASES = {
    "overview": f"{API_PREFIX}/pulse",
    "routes": f"{API_PREFIX}/pulse/routes",
    "services": f"{API_PREFIX}/pulse/services",
    "personas": f"{API_PREFIX}/pulse/personas",
    "agents": f"{API_PREFIX}/pulse/agents",
    "labs": f"{API_PREFIX}/pulse/labs",
    "sources": f"{API_PREFIX}/pulse/sources",
    "signals": f"{API_PREFIX}/pulse/signals",
    "anatomy": f"{API_PREFIX}/pulse/anatomy",
    "autolearning": f"{API_PREFIX}/pulse/autolearning",
}


PULSE_SERVICE_CATALOG = {
    "personas": {
        "label": "Personas",
        "category": "routing",
        "kind": "runtime",
        "aliases": ["personas", "specialists"],
        "target_path": f"{API_PREFIX}/personas",
        "source_paths": ["ocean-core/ocean_api.py", "ocean-core/response_orchestrator_v5.py"],
    },
    "agents_registry": {
        "label": "Agents Registry",
        "category": "agents",
        "kind": "module",
        "aliases": ["agents", "agents.py", "registry"],
        "target_path": f"{API_PREFIX}/agents",
        "module_names": ["agents"],
        "source_paths": ["agents.py", "ocean-core/ocean_api.py"],
    },
    "liam": {
        "label": "LIAM",
        "category": "core-engine",
        "kind": "service",
        "aliases": ["labor-intelligence", "matrix"],
        "probe_urls": ["http://clisonix-liam:8062/health", "http://localhost:8062/health"],
        "source_paths": ["liam_core.py", "liam_server.py"],
        "compose_service": "liam",
    },
    "alda": {
        "label": "ALDA",
        "category": "core-engine",
        "kind": "service",
        "aliases": ["artificial-labor", "deterministic-array"],
        "probe_urls": ["http://clisonix-alda:8063/health", "http://localhost:8063/health"],
        "source_paths": ["alda_core.py", "alda_server.py"],
        "compose_service": "alda",
    },
    "blerina": {
        "label": "Blerina",
        "category": "signals",
        "kind": "service",
        "aliases": ["document-intelligence", "gap-detector"],
        "probe_urls": ["http://clisonix-blerina:8035/health", "http://localhost:8035/health"],
        "source_paths": ["blerina_core.py", "services/blerina/main.py"],
        "compose_service": "blerina",
    },
    "dr_albana": {
        "label": "Dr. Albana",
        "category": "content",
        "kind": "service",
        "aliases": ["albana", "medical"],
        "probe_urls": ["http://clisonix-dr-albana:8040/health", "http://localhost:8040/health"],
        "source_paths": ["services/dr_albana/main.py"],
        "compose_service": "dr_albana",
    },
    "publisher": {
        "label": "Blog Publisher",
        "category": "publish",
        "kind": "service",
        "aliases": ["blog_publisher", "clx_publisher", "publish"],
        "probe_urls": ["http://clisonix-blog-publisher:8041/health", "http://localhost:8041/health"],
        "source_paths": ["clx_publisher.py", "services/blog_publisher/main.py"],
        "compose_service": "blog_publisher",
    },
    "lagter": {
        "label": "Lagter",
        "category": "publish",
        "kind": "service",
        "aliases": ["publish-orchestrator", "lagter-pulse"],
        "probe_urls": ["http://clisonix-lagter:9500/health", "http://localhost:9500/health"],
        "source_paths": ["services/lagter/main.py", "excel-core/lagter_v1_api.py"],
        "compose_service": "lagter",
    },
    "saas_api": {
        "label": "SaaS API",
        "category": "saas",
        "kind": "module",
        "aliases": ["saas", "signal-api", "multi-tenant"],
        "module_names": ["apps.api.saas_signal_api"],
        "source_paths": ["apps/api/saas_signal_api.py"],
        "compose_service": "saas-api",
    },
    "saas_orchestrator": {
        "label": "SaaS Orchestrator",
        "category": "saas",
        "kind": "service",
        "aliases": ["saas-orchestrator", "marketplace-orchestrator"],
        "probe_urls": ["http://clisonix-saas-orchestrator:9999/health", "http://localhost:9999/health"],
        "source_paths": ["saas_services_orchestrator.py", "saas_services_orchestrator_v3.py"],
        "compose_service": "saas-orchestrator",
    },
    "klajdi": {
        "label": "KLAJDI",
        "category": "signals",
        "kind": "module",
        "aliases": ["detective-intelligence", "signal-lab"],
        "module_names": ["services.intelligence-lab.klajdi_lab"],
        "probe_urls": ["http://clisonix-intelligence-lab:8098/health", "http://localhost:8098/health"],
        "source_paths": ["services/intelligence-lab/klajdi_lab.py", "services/intelligence-lab/main.py"],
    },
    "mali": {
        "label": "MALI",
        "category": "signals",
        "kind": "module",
        "aliases": ["master-announced-labor-intelligence", "announcements"],
        "module_names": ["services.intelligence-lab.mali_core"],
        "probe_urls": ["http://clisonix-intelligence-lab:8098/status", "http://localhost:8098/status"],
        "source_paths": ["services/intelligence-lab/mali_core.py", "services/intelligence-lab/main.py"],
    },
    "autolearning": {
        "label": "Autolearning",
        "category": "learning",
        "kind": "runtime",
        "aliases": ["auto-learning", "learning"],
        "target_path": f"{API_PREFIX}/autolearning/stats",
        "source_paths": ["ocean-core/ocean_api.py", "ocean-core/ocean_core_full.py", "production_autolearning_connector.py"],
    },
    "selflearning": {
        "label": "Selflearning",
        "category": "learning",
        "kind": "module",
        "aliases": ["self-learning", "adaptive-learning"],
        "source_paths": ["ocean-core/ocean_core_full.py", "production_autolearning_connector.py"],
    },
    "internal_apis": {
        "label": "Internal APIs",
        "category": "data",
        "kind": "runtime",
        "aliases": ["internal", "central-api"],
        "target_path": f"{API_PREFIX}/sources",
        "source_paths": ["ocean-core/data_sources.py", "apps/api/main.py"],
    },
    "external_free_apis": {
        "label": "External Free APIs",
        "category": "data",
        "kind": "module",
        "aliases": ["open-data", "free-data", "public-apis"],
        "source_paths": ["ocean-core/config.py", "ocean-core/curiosity_algebra/signal_integrator.py", "ocean-core/external_apis.py"],
        "providers": ["Wikipedia", "ArXiv", "PubMed", "GitHub", "DBPedia"],
    },
    "clisonix_signals": {
        "label": "Clisonix Signals",
        "category": "signals",
        "kind": "runtime",
        "aliases": ["mega-signal", "pulse", "signals"],
        "target_path": f"{API_PREFIX}/signals/overview",
        "source_paths": ["ocean-core/mega_signal_integrator.py", "ocean-core/ocean_api.py"],
    },
}


def _repo_file_exists(relative_path: str) -> bool:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    normalized = relative_path.replace("/", os.sep)
    return os.path.exists(os.path.join(repo_root, normalized))


def _module_exists(module_name: str) -> bool:
    try:
        return importlib.util.find_spec(module_name) is not None
    except Exception:
        return False


async def _probe_service_urls(urls: list[str]) -> dict[str, Any]:
    last_error = None

    async with httpx.AsyncClient(timeout=2.5, follow_redirects=True) as client:
        for url in urls:
            try:
                response = await client.get(url)
                content_type = response.headers.get("content-type", "")
                payload: Any
                if "application/json" in content_type:
                    try:
                        payload = response.json()
                    except Exception:
                        payload = response.text[:300]
                else:
                    payload = response.text[:300]

                return {
                    "reachable": response.is_success,
                    "status_code": response.status_code,
                    "url": url,
                    "payload": payload,
                }
            except Exception as exc:
                last_error = str(exc)

    return {
        "reachable": False,
        "status_code": None,
        "url": urls[0] if urls else None,
        "error": last_error,
    }


async def _build_pulse_service_record(service_name: str, probe: bool = False) -> dict[str, Any]:
    spec = PULSE_SERVICE_CATALOG[service_name]
    source_paths = spec.get("source_paths", [])
    source_files_present = [path for path in source_paths if _repo_file_exists(path)]
    module_names = spec.get("module_names", [])
    module_available = any(_module_exists(name) for name in module_names)

    status = "declared"
    runtime = "catalogued"
    details: dict[str, Any] = {}

    if service_name == "personas":
        if persona_router:
            status = "active"
            runtime = "runtime_enabled"
            details["count"] = len(getattr(persona_router, "mapping", {}))
        else:
            status = "disabled"
            runtime = "runtime_disabled"
            details["reason"] = "persona_router is disabled in active Ocean startup"
    elif service_name == "agents_registry":
        internal_data = internal_data_sources.get_all_data() if internal_data_sources else {}
        agents = internal_data.get("agents") or internal_data.get("ai_agents_status") or {}
        details["count"] = len(agents) if hasattr(agents, "__len__") else 0
        status = "active" if details["count"] else "partial"
        runtime = "telemetry_snapshot"
    elif service_name == "autolearning":
        if autolearning_engine:
            status = "active"
            runtime = "runtime_enabled"
        else:
            status = "disabled"
            runtime = "runtime_disabled"
            details["reason"] = "autolearning is disabled in ocean_api.py startup"
    elif service_name == "internal_apis":
        connected = False
        if internal_data_sources:
            try:
                connected = bool(internal_data_sources.get_all_data().get("central_api_connected", False))
            except Exception:
                connected = False
        status = "active" if connected else "partial"
        runtime = "central_api_bridge"
        details["central_api_connected"] = connected
    elif service_name == "external_free_apis":
        status = "active"
        runtime = "runtime_enabled"
        details["routes"] = [
            f"{API_PREFIX}/wikipedia",
            f"{API_PREFIX}/wiki/{{query}}",
            f"{API_PREFIX}/arxiv/{{query}}",
            f"{API_PREFIX}/pubmed/{{query}}",
            f"{API_PREFIX}/archive",
        ]
    elif service_name == "clisonix_signals":
        mega_signal = _get_mega_signal_status()
        status = mega_signal.get("status", "unavailable")
        runtime = "mega_signal_integrator"
        details["overview"] = mega_signal.get("overview")
    elif service_name == "selflearning":
        status = "available_in_code" if source_files_present else "missing"
        runtime = "module_only"
        details["reason"] = "no dedicated selflearning route is wired in active Ocean runtime"
    else:
        status = "module_available" if (source_files_present or module_available) else "missing"
        runtime = "module_only"

    record = {
        "name": service_name,
        "label": spec["label"],
        "category": spec["category"],
        "kind": spec["kind"],
        "status": status,
        "runtime": runtime,
        "aliases": spec.get("aliases", []),
        "target_path": spec.get("target_path"),
        "compose_service": spec.get("compose_service"),
        "providers": spec.get("providers", []),
        "availability": {
            "source_files_present": source_files_present,
            "module_available": module_available,
        },
        "details": details,
    }

    if probe and spec.get("probe_urls"):
        record["probe"] = await _probe_service_urls(spec["probe_urls"])
        if record["probe"].get("reachable"):
            record["status"] = "reachable"
            record["runtime"] = "http_live"

    return record


class AnatomyActivateRequest(BaseModel):
    targets: list[str] | None = None
    include_overview: bool = True


class DocumentGenerateRequest(BaseModel):
    query: str
    format: str = "xlsx"
    contract_type: str = "cpi"
    language: str = "en"


def _extract_text_from_document(filename: str, content_type: str, data: bytes, max_chars: int = 200_000) -> dict[str, Any]:
    """Industrial multi-format text extraction with parser fallback chain."""
    lower_name = filename.lower()
    extracted_text = ""
    parser_used = "none"
    pages_or_rows = 0

    try:
        if lower_name.endswith((".txt", ".md", ".csv")) or content_type in {"text/plain", "text/markdown", "text/csv"}:
            extracted_text = data.decode("utf-8", errors="ignore")
            parser_used = "utf8_text"
            pages_or_rows = extracted_text.count("\n") + 1 if extracted_text else 0
        elif lower_name.endswith(".json") or content_type == "application/json":
            parsed = json.loads(data.decode("utf-8", errors="ignore"))
            extracted_text = json.dumps(parsed, ensure_ascii=False, indent=2)
            parser_used = "json"
            pages_or_rows = 1
        elif lower_name.endswith(".pdf") or content_type == "application/pdf":
            pypdf = None
            for mod_name in ("pypdf", "PyPDF2"):
                try:
                    pypdf = importlib.import_module(mod_name)
                    break
                except Exception:
                    continue

            if pypdf:
                stream = io.BytesIO(data)
                reader = pypdf.PdfReader(stream)
                pages_or_rows = len(reader.pages)
                texts: list[str] = []
                for page in reader.pages[:50]:
                    texts.append((page.extract_text() or "").strip())
                extracted_text = "\n\n".join(t for t in texts if t)
                parser_used = "pypdf"
            else:
                parser_used = "pdf_parser_unavailable"
        elif lower_name.endswith(".docx") or content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            try:
                docx = importlib.import_module("docx")
                doc = docx.Document(io.BytesIO(data))
                paragraphs = [p.text for p in doc.paragraphs if p.text and p.text.strip()]
                extracted_text = "\n".join(paragraphs)
                parser_used = "python-docx"
                pages_or_rows = len(paragraphs)
            except Exception:
                parser_used = "docx_parser_unavailable"
        elif lower_name.endswith((".xlsx", ".xls")) or content_type in {
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel",
        }:
            try:
                openpyxl = importlib.import_module("openpyxl")
                wb = openpyxl.load_workbook(io.BytesIO(data), read_only=True, data_only=True)
                fragments: list[str] = []
                row_counter = 0
                for ws in wb.worksheets[:5]:
                    fragments.append(f"# Sheet: {ws.title}")
                    for row in ws.iter_rows(min_row=1, max_row=200, values_only=True):
                        values = [str(v).strip() for v in row if v is not None and str(v).strip()]
                        if values:
                            fragments.append(" | ".join(values))
                            row_counter += 1
                extracted_text = "\n".join(fragments)
                parser_used = "openpyxl"
                pages_or_rows = row_counter
            except Exception:
                parser_used = "xlsx_parser_unavailable"
        else:
            parser_used = "unsupported_format"
    except Exception as ex:
        parser_used = f"parser_error:{type(ex).__name__}"
        extracted_text = ""

    extracted_text = (extracted_text or "")[:max_chars]
    return {
        "text": extracted_text,
        "parser": parser_used,
        "units": pages_or_rows,
        "text_length": len(extracted_text),
    }


@app.on_event("startup")
async def startup_event():
    """Initialize all managers on startup"""
    global internal_data_sources, persona_router, query_processor, knowledge_engine, laboratory_network, real_data_engine, specialized_chat, orchestrator, autolearning_engine

    logger.info("[OCEAN] Ocean Core 8030 starting up with 14 personas...")

    try:
        # Initialize all managers in parallel
        logger.info("→ Initializing internal data sources...")
        internal_data_sources = get_all_sources()

        if internal_data_sources is None:
            logger.error("❌ CRITICAL: get_all_sources() returned None!")
            raise RuntimeError("Failed to initialize data sources")

        logger.info("[OK] Data sources initialized")

        # NANOGRID: Minimal initialization - only what's needed
        persona_router = None  # DISABLED
        query_processor = None  # DISABLED - Ollama handles queries
        laboratory_network = None  # DISABLED
        real_data_engine = None  # DISABLED
        knowledge_engine = None  # DISABLED
        autolearning_engine = None  # DISABLED

        # Initialize specialized chat if available
        try:
            from specialized_chat_engine import get_specialized_chat, initialize_specialized_chat
            logger.info("→ Initializing Specialized Chat Engine...")
            specialized_chat = get_specialized_chat()
            if specialized_chat:
                await initialize_specialized_chat()
                logger.info("✅ Specialized Chat Engine initialized")
            else:
                specialized_chat = None
                logger.info("⏭️  Specialized Chat Engine not available")
        except Exception as e:
            logger.warning(f"⚠️  Specialized Chat Engine initialization failed: {e}")
            specialized_chat = None

        # Initialize orchestrator v5 - ONLY OLLAMA
        logger.info("→ Initializing Orchestrator (Ollama only)...")
        orchestrator = get_orchestrator_v5()
        logger.info("🦙 [OK] Orchestrator ready - Ollama ONLY!")

        logger.info("✅ Ocean Core 8030 initialized - NANOGRID mode")
        logger.info("   - Ollama: ✅ Ready")
    except Exception as e:
        logger.error(f"❌ Ocean Core 8030 initialization failed: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise


@app.get("/api/info")
@app.get(f"{API_PREFIX}/info")
async def api_info():
    """API info endpoint"""
    internal_data = internal_data_sources.get_all_data() if internal_data_sources else {}
    orchestrator_runtime = _get_orchestrator_runtime()

    return {
        "service": "Curiosity Ocean 8030",
        "version": "4.0.0",
        "status": "operational",
        "personas": len(persona_router.mapping) if persona_router else 0,
        "data_sources": len(internal_data) if internal_data else 0,
        "description": "Curiosity Ocean runtime with Ollama chat, signal routes, and internal Clisonix integrations",
        "runtime_mode": orchestrator_runtime["mode"],
        "features": [
            "Ollama chat orchestration",
            "Internal data sources only",
            "Mega signal routes",
            "Nanogrid and LoRa endpoints",
            "Knowledge exploration",
            "Curiosity threads"
        ],
        "endpoints": [
            "GET /api/personas - List all 14 specialists",
            "POST /api/query - Query with persona routing",
            "GET /api/v1/excel/status - Excel service status via Ocean",
            "GET /api/v1/excel/generate - Generate Excel via Ocean",
            "GET /api/status - Service status",
            "GET /api/labs - Location lab data",
            "GET /api/agents - Agent telemetry",
            "GET /health - Health check"
        ]
    }


@app.get("/favicon.ico")
async def favicon():
    """Serve favicon - Ocean blue icon"""
    # Return a simple 1x1 pixel transparent GIF to prevent 404
    import base64
    # Minimal valid ICO (1x1 blue pixel)
    favicon_bytes = base64.b64decode(
        "AAABAAEAEBAAAAEAIABoBAAAFgAAACgAAAAQAAAAIAAAAAEAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
        "AAD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//"
        "/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//"
        "/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//"
        "/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//"
        "/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//"
        "/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//"
        "/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//"
        "/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//"
        "/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//"
        "/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//"
        "/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//"
        "/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//"
        "/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//"
        "/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//"
        "/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AAAA"
        "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    )
    from fastapi.responses import Response
    return Response(content=favicon_bytes, media_type="image/x-icon")


@app.get("/")
async def root_chat_ui():
    """Serve the specialized chat interface at root"""
    import os
    file_path = os.path.join(os.path.dirname(__file__), "specialized_chat.html")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/html")
    return {"error": "Chat UI not found", "tip": "Try /api/info for API info"}


@app.get("/chat")
async def chat_ui():
    """Serve the specialized chat interface"""
    import os
    file_path = os.path.join(os.path.dirname(__file__), "specialized_chat.html")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/html")
    else:
        return {"error": "Chat UI not found"}


@app.get("/status")
@app.get(f"{API_PREFIX}/status")
async def get_status():
    """Get service status"""
    if not internal_data_sources:
        return {"status": "initializing"}

    try:
        internal_data = internal_data_sources.get_all_data()
        orchestrator_runtime = _get_orchestrator_runtime()
        mega_signal = _get_mega_signal_status()

        return {
            "service": "Curiosity Ocean 8030",
            "version": "4.0.0",
            "status": "operational",
            "initialized": True,
            "runtime_mode": orchestrator_runtime["mode"],
            "personas": len(persona_router.mapping) if persona_router else 0,
            "knowledge_engine": "operational" if knowledge_engine else "disabled",
            "timestamp": datetime.now().isoformat(),
            "data_sources": {
                "timestamp": internal_data.get("timestamp"),
                "source": internal_data.get("source"),
                "central_api_connected": internal_data.get("central_api_connected", False),
                "laboratories": len(internal_data.get("laboratories", {}).get("labs", [])),
                "system_metrics": len(internal_data.get("system_metrics", {})),
                "asi_status": bool(internal_data.get("asi_status")),
                "ocean_labs_list": len(internal_data.get("ocean_labs_list", {}).get("laboratories", [])),
                "ai_agents_status": len(internal_data.get("ai_agents_status", {})),
                "all_keys": list(internal_data.keys())
            },
            "orchestrator": orchestrator_runtime,
            "advanced_systems": {
                "specialized_chat": "operational" if specialized_chat else "disabled",
                "knowledge_seeds": "available" if orchestrator_runtime["knowledge_seeds_available"] else "unavailable",
                "knowledge_seeds_active": orchestrator_runtime["knowledge_seeds_active"],
                "mega_layers": "active" if orchestrator_runtime["mega_layers_active"] else (
                    "available_but_disabled" if orchestrator_runtime["mega_layers_available"] else "unavailable"
                ),
                "mega_signal_integrator": mega_signal["status"],
                "nanogrid_routes": "active",
                "lora_routes": "active",
            },
            "components": {
                "persona_router": "operational" if persona_router else "disabled",
                "internal_data_sources": "operational",
                "query_processor": "operational" if query_processor else "disabled",
                "knowledge_engine": "operational" if knowledge_engine else "disabled",
                "laboratory_network": "operational" if laboratory_network else "disabled",
                "real_data_engine": "operational" if real_data_engine else "disabled",
                "autolearning_engine": "operational" if autolearning_engine else "disabled"
            }
        }
    except Exception as e:
        logger.error(f"Status check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{API_PREFIX}/system-full")
async def get_full_system_status():
    """
    Get COMPLETE system status with ALL components:
    - 14 Personas
    - 23 Laboratories
    - 61 Alphabet Layers
    - 12 Backend Layers (0-12)
    - ASI Trinity (Alba/Albi/Jona)
    - Open Data Sources
    - Enforcement Manager
    - ML Manager
    - Cycle Engine
    """
    try:
        orchestrator_runtime = _get_orchestrator_runtime()
        mega_signal = _get_mega_signal_status()
        status = {
            "service": "Clisonix Ocean Core",
            "version": "4.0.0",
            "runtime_mode": orchestrator_runtime["mode"],
            "timestamp": datetime.now().isoformat(),
            "components": {}
        }

        # Personas
        status["components"]["personas"] = {
            "count": len(persona_router.mapping) if persona_router else 0,
            "status": "active" if persona_router else "unavailable",
            "list": list(persona_router.mapping.keys()) if persona_router else []
        }

        # Laboratories
        if laboratory_network:
            labs = laboratory_network.get_all_labs()
            status["components"]["laboratories"] = {
                "count": len(labs),
                "status": "active",
                "locations": [lab.location for lab in labs[:5]]
            }
        else:
            status["components"]["laboratories"] = {"count": 0, "status": "unavailable"}

        # Orchestrator with Alphabet Layers & Universal Connector
        if orchestrator:
            status["components"]["orchestrator"] = {
                "status": "active",
                "alphabet_layers": orchestrator_runtime["alphabet_layers"],
                "ollama_active": orchestrator_runtime["ollama_active"],
                "knowledge_seeds_available": orchestrator_runtime["knowledge_seeds_available"],
                "mega_layers": "active" if orchestrator_runtime["mega_layers_active"] else (
                    "available_but_disabled" if orchestrator_runtime["mega_layers_available"] else "unavailable"
                ),
                "universal_connector": "connected" if orchestrator_runtime["universal_connector"] else "not_connected"
            }

            # Get Universal Connector summary
            if hasattr(orchestrator, 'universal_connector') and orchestrator.universal_connector:
                status["components"]["universal_system"] = orchestrator.universal_connector.get_system_summary()

        # Real Data Engine
        status["components"]["real_data_engine"] = {
            "status": "active" if real_data_engine else "unavailable"
        }

        # Knowledge Engine
        status["components"]["knowledge_engine"] = {
            "status": "active" if knowledge_engine else "disabled"
        }

        status["components"]["mega_signal_integrator"] = {
            "status": mega_signal["status"],
            "managers": mega_signal.get("overview", {}).get("managers", {}),
        }

        # Summary
        active_count = sum(1 for c in status["components"].values() if c.get("status") == "active" or c.get("status") == "connected")
        status["summary"] = {
            "total_components": len(status["components"]),
            "active_components": active_count,
            "health": "healthy" if active_count > 4 else "degraded"
        }

        return status

    except Exception as e:
        logger.error(f"Full system status error: {e}")
        return {"error": str(e), "status": "error"}


@app.get(f"{API_PREFIX}/sources")
async def get_sources():
    """List available data sources (INTERNAL ONLY)"""
    if not internal_data_sources:
        raise HTTPException(status_code=503, detail="Service initializing")

    internal_data = internal_data_sources.get_all_data()

    # REAL SOURCES from actual data
    return {
        "timestamp": datetime.now().isoformat(),
        "internal_sources_operational": list(internal_data.keys()),
        "central_api": {
            "url": internal_data.get("central_api_url", "http://localhost:8000"),
            "connected": internal_data.get("central_api_connected", False),
            "health": internal_data.get("health", {}),
            "status_code": internal_data.get("status")
        },
        "laboratories_network": {
            "description": "23 Specialized Research Laboratories across EU",
            "total": internal_data.get("laboratories", {}).get("total_labs", 0),
            "list_count": len(internal_data.get("ocean_labs_list", {}).get("laboratories", [])),
            "status": "operational",
            "locations": [
                "Elbasan, Albania (AI)",
                "Tirana, Albania (Medical)",
                "Prishtina, Kosovo (Security)",
                "Vienna, Austria (Neuroscience)",
                "Zurich, Switzerland (Finance)",
                "Prague, Czech Republic (Robotics)",
                "Budapest, Hungary (Data)",
                "Ljubljana, Slovenia (Quantum)",
                "Zagreb, Croatia (Biotech)",
                "Sofia, Bulgaria (Chemistry)",
                "Beograd, Serbia (Industrial)",
                "Bucharest, Romania (Nanotechnology)",
                "Istanbul, Turkey (Trade)",
                "Cairo, Egypt (Archeology)",
                "Jerusalem, Palestine (Heritage)",
                "Rome, Italy (Architecture)",
                "Athens, Greece (Classical)",
                "Kostur, Greece (Energy)",
                "Durrës, Albania (IoT)",
                "Shkodër, Albania (Marine)",
                "Vlorë, Albania (Environmental)",
                "Korça, Albania (Agricultural)",
                "Sarandë, Albania (Underwater)"
            ]
        },
        "agi_agents": {
            "description": "ASI Trinity - 3 Superintelligences",
            "alba": {
                "role": "Network Monitor",
                "health": internal_data.get("asi_status", {}).get("trinity", {}).get("alba", {}).get("health", 0),
                "operational": internal_data.get("asi_status", {}).get("trinity", {}).get("alba", {}).get("operational", False)
            },
            "albi": {
                "role": "Neural Processor",
                "health": internal_data.get("asi_status", {}).get("trinity", {}).get("albi", {}).get("health", 0),
                "operational": internal_data.get("asi_status", {}).get("trinity", {}).get("albi", {}).get("operational", False)
            },
            "jona": {
                "role": "Data Coordinator",
                "health": internal_data.get("asi_status", {}).get("trinity", {}).get("jona", {}).get("health", 0),
                "operational": internal_data.get("asi_status", {}).get("trinity", {}).get("jona", {}).get("operational", False)
            },
            "count": len(internal_data.get("ai_agents_status", {})),
            "status": "operational"
        },
        "system_metrics": {
            "description": "Real-time system health monitoring",
            "cpu_percent": internal_data.get("system_metrics", {}).get("cpu_percent"),
            "memory_percent": internal_data.get("system_metrics", {}).get("memory_percent"),
            "disk_percent": internal_data.get("system_metrics", {}).get("disk_percent"),
            "status": "operational"
        },
        "data_quality": {
            "laboratories": len(internal_data.get("laboratories", {}).get("labs", [])),
            "ocean_labs_list": len(internal_data.get("ocean_labs_list", {}).get("laboratories", [])),
            "ai_agents": len(internal_data.get("ai_agents_status", {})),
            "total_data_records": sum([
                len(v) if isinstance(v, list) else (len(v) if isinstance(v, dict) else 1)
                for v in internal_data.values() if v
            ])
        },
        "external_free_sources": {
            "enabled": True,
            "routes": [
                f"{API_PREFIX}/wikipedia",
                f"{API_PREFIX}/wiki/{{query}}",
                f"{API_PREFIX}/arxiv/{{query}}",
                f"{API_PREFIX}/pubmed/{{query}}",
                f"{API_PREFIX}/archive",
            ],
        },
        "note": "✅ Internal Clisonix APIs + external free public data sources are active"
    }


async def _fetch_external_source(source_id: str, params: dict[str, Any]) -> dict[str, Any]:
    try:
        connector = _get_global_data_connector()
        result = await connector.fetch_from_source(source_id=source_id, params=params)
        if result.get("error"):
            detail = str(result.get("error"))
            if detail.startswith("Source") and "not found" in detail:
                raise HTTPException(status_code=404, detail=detail)
            raise HTTPException(status_code=502, detail=detail)
        result["timestamp"] = datetime.utcnow().isoformat()
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"External source fetch failed ({source_id}): {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch {source_id}")


@app.get(f"{API_PREFIX}/integrations/connectors")
async def get_connectors_status():
    """Runtime status for AIAGI/infra/toolchain connectors (backend only)."""
    aiagi_url = os.getenv("AIAGI_BASE_URL", "https://www.aiagi.io")
    cloudflare_api = os.getenv("CLOUDFLARE_API_BASE", "https://api.cloudflare.com/client/v4")
    hetzner_api = os.getenv("HETZNER_API_BASE", "https://api.hetzner.cloud/v1")
    mesh_url = os.getenv("MESH_MODULES_URL", "")

    return {
        "mode": "backend-data-only",
        "connectors": {
            "aiagi": {"configured": bool(aiagi_url), "base_url": aiagi_url},
            "cloudflare": {"configured": bool(os.getenv("CLOUDFLARE_API_TOKEN")), "api_base": cloudflare_api},
            "hetzner": {"configured": bool(os.getenv("HETZNER_API_TOKEN")), "api_base": hetzner_api},
            "mesh_modules": {"configured": bool(mesh_url), "url": mesh_url},
        },
        "signals": {
            "lora": f"{API_PREFIX}/signals/lora",
            "mesh": f"{API_PREFIX}/signals/data-sources",
        },
        "toolchain": {
            "git": shutil.which("git") is not None,
            "docker": shutil.which("docker") is not None,
            "node": shutil.which("node") is not None,
            "npm": shutil.which("npm") is not None,
            "yarn": shutil.which("yarn") is not None,
            "python": shutil.which("python") is not None,
            "pytorch": importlib.util.find_spec("torch") is not None,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/weather")
@app.get(f"{API_PREFIX}/weather")
async def weather_data(
    lat: float = Query(41.3275, description="Latitude"),
    lon: float = Query(19.8187, description="Longitude"),
    days: int = Query(2, ge=1, le=7, description="Forecast days"),
):
    """Dedicated weather endpoint via Open-Meteo (free)."""
    return await _fetch_external_source("open_meteo", {"lat": lat, "lon": lon, "days": days})


@app.get("/nasa")
@app.get(f"{API_PREFIX}/nasa")
async def nasa_data(api_key: str = Query("DEMO_KEY", description="NASA API key (optional)")):
    """Dedicated NASA endpoint via APOD (free with DEMO_KEY)."""
    return await _fetch_external_source("nasa", {"api_key": api_key})


@app.get("/coingecko")
@app.get(f"{API_PREFIX}/coingecko")
async def coingecko_data(
    coin: str = Query("bitcoin", description="Coin id, e.g. bitcoin"),
    fiat: str = Query("usd", description="Fiat currency, e.g. usd"),
):
    """Dedicated crypto endpoint via CoinGecko (free)."""
    return await _fetch_external_source("coingecko", {"coin": coin, "fiat": fiat})


@app.get("/wikipedia")
@app.get(f"{API_PREFIX}/wikipedia")
async def wikipedia_data(
    q: str = Query("artificial intelligence", description="Search query"),
    limit: int = Query(5, ge=1, le=25, description="Max results"),
):
    """Dedicated Wikipedia endpoint (data only)."""
    return await _fetch_external_source("wikipedia", {"q": q, "limit": limit})


@app.get("/archive")
@app.get(f"{API_PREFIX}/archive")
async def archive_data(
    q: str = Query("mediatype:texts", description="Archive query"),
    limit: int = Query(10, ge=1, le=50, description="Max results"),
):
    """Dedicated Internet Archive endpoint (data only)."""
    return await _fetch_external_source("internet_archive", {"q": q, "limit": limit})


@app.get(f"{API_PREFIX}/wiki/{{query}}")
async def research_wikipedia(query: str, limit: int = Query(10, ge=1, le=25)):
    """Search Wikipedia articles for Archive & Research module."""
    search_query = (query or "").strip()
    if not search_query:
        raise HTTPException(status_code=400, detail="query is required")

    params = {
        "action": "query",
        "list": "search",
        "srsearch": search_query,
        "srlimit": str(limit),
        "format": "json",
        "utf8": "1",
    }

    try:
        headers = {
            "User-Agent": "ClisonixOceanResearchBot/1.0 (+https://clisonix.com)",
            "Accept": "application/json",
        }
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get("https://en.wikipedia.org/w/api.php", params=params, headers=headers)
            response.raise_for_status()
            payload = response.json()

        results: list[dict[str, Any]] = []
        for item in payload.get("query", {}).get("search", []):
            title = str(item.get("title", "")).strip()
            if not title:
                continue
            results.append(
                {
                    "title": title,
                    "snippet": str(item.get("snippet", "")).replace("<span class=\"searchmatch\">", "").replace("</span>", ""),
                    "pageid": item.get("pageid"),
                    "wordcount": item.get("wordcount"),
                    "url": f"https://en.wikipedia.org/wiki/{quote_plus(title.replace(' ', '_'))}",
                }
            )

        return {
            "query": search_query,
            "total_results": len(results),
            "results": results,
            "source": "wikipedia.org",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"Wikipedia API returned {e.response.status_code}")
    except Exception as e:
        logger.error(f"Wikipedia search error: {e}")
        raise HTTPException(status_code=500, detail="Wikipedia search failed")


@app.get(f"{API_PREFIX}/arxiv/{{query}}")
async def research_arxiv(query: str, max_results: int = Query(10, ge=1, le=25)):
    """Search ArXiv papers for Archive & Research module."""
    search_query = (query or "").strip()
    if not search_query:
        raise HTTPException(status_code=400, detail="query is required")

    arxiv_url = "https://export.arxiv.org/api/query"
    params = {
        "search_query": f"all:{search_query}",
        "start": "0",
        "max_results": str(max_results),
    }

    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            response = await client.get(arxiv_url, params=params)
            response.raise_for_status()
            xml_body = response.text

        papers: list[dict[str, Any]] = []
        entry_pattern = re.compile(r"<entry>(.*?)</entry>", re.DOTALL)
        title_pattern = re.compile(r"<title>(.*?)</title>", re.DOTALL)
        summary_pattern = re.compile(r"<summary>(.*?)</summary>", re.DOTALL)
        id_pattern = re.compile(r"<id>(.*?)</id>", re.DOTALL)
        published_pattern = re.compile(r"<published>(.*?)</published>", re.DOTALL)
        author_pattern = re.compile(r"<author>\s*<name>(.*?)</name>\s*</author>", re.DOTALL)
        category_pattern = re.compile(r"<category[^>]*term=\"(.*?)\"", re.DOTALL)

        for entry in entry_pattern.findall(xml_body):
            title_match = title_pattern.search(entry)
            if not title_match:
                continue
            title = re.sub(r"\s+", " ", html.unescape(title_match.group(1))).strip()
            if title.lower() == "arxiv query":
                continue

            summary_match = summary_pattern.search(entry)
            paper_id_match = id_pattern.search(entry)
            published_match = published_pattern.search(entry)
            authors = [
                re.sub(r"\s+", " ", html.unescape(name)).strip()
                for name in author_pattern.findall(entry)
                if name.strip()
            ]
            categories = [c.strip() for c in category_pattern.findall(entry) if c.strip()]

            papers.append(
                {
                    "title": title,
                    "summary": re.sub(r"\s+", " ", html.unescape(summary_match.group(1))).strip() if summary_match else "",
                    "authors": authors,
                    "published": published_match.group(1).strip() if published_match else "",
                    "url": paper_id_match.group(1).strip() if paper_id_match else "",
                    "categories": categories,
                }
            )

        return {
            "query": search_query,
            "total_results": len(papers),
            "papers": papers,
            "source": "arxiv.org",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"ArXiv API returned {e.response.status_code}")
    except Exception as e:
        logger.error(f"ArXiv search error: {e}")
        raise HTTPException(status_code=500, detail="ArXiv search failed")


@app.get(f"{API_PREFIX}/pubmed/{{query}}")
async def research_pubmed(query: str, max_results: int = Query(10, ge=1, le=25)):
    """Search PubMed articles for Archive & Research module."""
    search_query = (query or "").strip()
    if not search_query:
        raise HTTPException(status_code=400, detail="query is required")

    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            search_response = await client.get(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
                params={
                    "db": "pubmed",
                    "term": search_query,
                    "retmode": "json",
                    "retmax": str(max_results),
                    "sort": "relevance",
                },
            )
            search_response.raise_for_status()
            search_payload = search_response.json()

            id_list = search_payload.get("esearchresult", {}).get("idlist", [])
            if not id_list:
                return {
                    "query": search_query,
                    "total_results": 0,
                    "articles": [],
                    "source": "pubmed.ncbi.nlm.nih.gov",
                    "timestamp": datetime.utcnow().isoformat(),
                }

            summary_response = await client.get(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
                params={
                    "db": "pubmed",
                    "id": ",".join(id_list),
                    "retmode": "json",
                },
            )
            summary_response.raise_for_status()
            summary_payload = summary_response.json()

        articles: list[dict[str, Any]] = []
        result_map = summary_payload.get("result", {})
        for pmid in id_list:
            item = result_map.get(pmid, {})
            if not item:
                continue
            authors = [a.get("name") for a in item.get("authors", []) if isinstance(a, dict) and a.get("name")]
            articles.append(
                {
                    "pmid": pmid,
                    "title": item.get("title", ""),
                    "authors": authors,
                    "source": item.get("source", ""),
                    "pubdate": item.get("pubdate", ""),
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                }
            )

        return {
            "query": search_query,
            "total_results": len(articles),
            "articles": articles,
            "source": "pubmed.ncbi.nlm.nih.gov",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"PubMed API returned {e.response.status_code}")
    except Exception as e:
        logger.error(f"PubMed search error: {e}")
        raise HTTPException(status_code=500, detail="PubMed search failed")


def generate_key_findings(question: str, response: str | None) -> list:
    """Generate key findings from response"""
    findings = []

    # Extract sentences that look like findings
    if response:
        sentences = response.split('. ')
        for i, sentence in enumerate(sentences[:5]):  # Top 5 findings
            if len(sentence.strip()) > 20:
                findings.append({
                    "finding": sentence.strip(),
                    "importance": 0.8 - (i * 0.1),
                    "source": "persona_analysis"
                })

    return findings


def generate_curiosity_threads(question: str, findings: list) -> list:
    """Generate curiosity threads for deeper exploration"""
    # Common curiosity thread patterns
    thread_templates = [
        {
            "title": "Deep Dive",
            "hook": f"Let's explore the underlying mechanisms behind: {question[:50]}...",
            "depth_level": "expert"
        },
        {
            "title": "Historical Context",
            "hook": "How did our understanding of this topic evolve?",
            "depth_level": "medium"
        },
        {
            "title": "Practical Applications",
            "hook": "How can we apply this knowledge in real-world scenarios?",
            "depth_level": "beginner"
        },
        {
            "title": "Related Concepts",
            "hook": "What other topics are connected to this?",
            "depth_level": "medium"
        }
    ]

    # Adjust depth based on number of findings
    if len(findings) > 5:
        for thread in thread_templates:
            thread["depth_level"] = "expert"

    return thread_templates[:3]  # Return top 3 threads


@app.get("/api/excel/status")
@app.get(f"{API_PREFIX}/excel/status")
async def excel_status_proxy():
    """Proxy Excel service status via Ocean Core."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{EXCEL_SERVICE_URL}/status")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Excel service returned an error")
    except Exception as e:
        logger.error(f"Excel status proxy error: {e}")
        raise HTTPException(status_code=502, detail="Excel service unavailable")


@app.get("/api/excel/templates")
@app.get(f"{API_PREFIX}/excel/templates")
async def excel_templates_proxy():
    """Proxy Excel templates endpoint via Ocean Core."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{EXCEL_SERVICE_URL}/api/excel/templates")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Excel templates endpoint returned an error")
    except Exception as e:
        logger.error(f"Excel templates proxy error: {e}")
        raise HTTPException(status_code=502, detail="Excel service unavailable")


@app.get("/api/excel/formulas")
@app.get(f"{API_PREFIX}/excel/formulas")
async def excel_formulas_proxy():
    """Proxy Excel formulas endpoint via Ocean Core."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{EXCEL_SERVICE_URL}/api/excel/formulas")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Excel formulas endpoint returned an error")
    except Exception as e:
        logger.error(f"Excel formulas proxy error: {e}")
        raise HTTPException(status_code=502, detail="Excel service unavailable")


@app.get("/api/excel/generate")
@app.get(f"{API_PREFIX}/excel/generate")
async def excel_generate_proxy(title: str = "Clisonix Data Export", include_metrics: bool = True):
    """Generate Excel file through Excel service and return binary content."""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(
                f"{EXCEL_SERVICE_URL}/api/excel/generate",
                params={"title": title, "include_metrics": include_metrics}
            )
            response.raise_for_status()
            content_disposition = response.headers.get("content-disposition", "attachment; filename=clisonix_export.xlsx")
            return Response(
                content=response.content,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": content_disposition}
            )
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Excel generate endpoint returned an error")
    except Exception as e:
        logger.error(f"Excel generate proxy error: {e}")
        raise HTTPException(status_code=502, detail="Excel service unavailable")


@app.post("/api/excel/validate")
@app.post(f"{API_PREFIX}/excel/validate")
async def excel_validate_proxy(file: UploadFile = File(...)):
    """Validate uploaded Excel file via Excel service."""
    try:
        file_bytes = await file.read()
        files = {
            "file": (
                file.filename or "upload.xlsx",
                file_bytes,
                file.content_type or "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(f"{EXCEL_SERVICE_URL}/api/excel/validate", files=files)
            return JSONResponse(status_code=response.status_code, content=response.json())
    except Exception as e:
        logger.error(f"Excel validate proxy error: {e}")
        raise HTTPException(status_code=502, detail="Excel service unavailable")


@app.post("/api/excel/parse")
@app.post(f"{API_PREFIX}/excel/parse")
async def excel_parse_proxy(file: UploadFile = File(...), sheet: str | None = None):
    """Parse uploaded Excel file via Excel service."""
    try:
        file_bytes = await file.read()
        files = {
            "file": (
                file.filename or "upload.xlsx",
                file_bytes,
                file.content_type or "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        }
        params = {"sheet": sheet} if sheet else None
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(f"{EXCEL_SERVICE_URL}/api/excel/parse", files=files, params=params)
            return JSONResponse(status_code=response.status_code, content=response.json())
    except Exception as e:
        logger.error(f"Excel parse proxy error: {e}")
        raise HTTPException(status_code=502, detail="Excel service unavailable")


@app.get(f"{API_PREFIX}/personas")
async def get_personas():
    """List all 14 specialist personas"""
    if not persona_router:
        raise HTTPException(status_code=503, detail="Service not initialized")

    personas_list = []
    for domain, keywords in persona_router.mapping.items():
        personas_list.append({
            "domain": domain,
            "keywords": keywords,
            "description": f"{domain} specialist analyst"
        })

    return {
        "total_personas": len(personas_list),
        "personas": personas_list,
        "timestamp": datetime.now().isoformat()
    }


@app.post(f"{API_PREFIX}/query")
async def query_ocean(request: Request):
    """
    Query Ocean with 14 Specialist Personas

    Accepts JSON body with:
    - query: Natural language question (required)
    - use_personas: Route through specialist personas (default: true)
    - limit_results: Limit results per source (default: 5)

    Routes to specialized analysts based on keywords:
    - Medical Science: brain, neuro, health, biology
    - LoRa IoT: lora, iot, sensor, gateway
    - Security: security, vulnerability, encrypted
    - Systems Architecture: api, infrastructure, system
    - Natural Science: physics, chemistry, energy, quantum
    - Industrial Process: cycle, production, factory
    - Business: kpi, revenue, growth, strategy
    - AGI Systems: agi, cognitive, autonomous
    - And 6 more specialized domains...
    """

    # Parse JSON body
    try:
        body = await request.json()
    except Exception as e:
        logger.error(f"JSON parse error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON body: {str(e)}")

    question = body.get("query") or body.get("question") or ""
    use_personas = body.get("use_personas", True)

    # Start timing from 0.1ms precision
    start_time = time.perf_counter()

    if not question or len(question.strip()) == 0:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    if not query_processor or not knowledge_engine or not persona_router or not internal_data_sources:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        logger.info(f"🧠 Received query: {question}")

        # 0. ORCHESTRATOR V5 (Brain with Ollama/Knowledge Seeds) - First Priority!
        orchestrator_result = None
        if orchestrator:
            try:
                logger.info("🧠 Using Orchestrator v5 (Ollama + Knowledge Seeds)...")
                orchestrator_result = await orchestrator.orchestrate(question)
                # OrchestratedResponse is a dataclass - use attributes, not .get()
                if orchestrator_result and hasattr(orchestrator_result, 'fused_answer') and orchestrator_result.fused_answer:
                    sources = orchestrator_result.sources_cited if hasattr(orchestrator_result, 'sources_cited') else []
                    source_str = sources[0] if sources else "orchestrator_v5"
                    logger.info(f"✅ Orchestrator v5 answered (source: {source_str})")
            except Exception as orch_err:
                logger.warning(f"Orchestrator v5 error: {orch_err}")

        # If orchestrator gave real answer, use it
        if orchestrator_result and hasattr(orchestrator_result, 'fused_answer') and orchestrator_result.fused_answer:
            sources = orchestrator_result.sources_cited if hasattr(orchestrator_result, 'sources_cited') else []
            response_source = sources[0] if sources else "orchestrator_v5"
            response_content = orchestrator_result.fused_answer
            confidence = orchestrator_result.confidence if hasattr(orchestrator_result, 'confidence') else 0.9

            # Check if this is from Ollama or Knowledge Seeds (not a fallback/template)
            is_real_answer = any(s.startswith(("ollama", "knowledge_seed")) for s in sources) if sources else False

            if is_real_answer or (response_content and len(response_content) > 50):
                # Calculate elapsed time from 0.1ms to full response
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                return {
                    "query": question,
                    "intent": str(orchestrator_result.query_category.value) if hasattr(orchestrator_result, 'query_category') else "general",
                    "response": response_content,
                    "persona_answer": response_content,
                    "key_findings": [{"finding": response_content[:500], "importance": 0.95, "source": response_source, "confidence": confidence}],
                    "sources": {"internal": sources, "external": []},
                    "confidence": confidence,
                    "processing_time_ms": round(elapsed_ms, 2),
                    "curiosity_threads": generate_curiosity_threads(question, []),
                    "data_sources_used": ["orchestrator_v5"] + sources,
                    "ollama_used": any(s.startswith("ollama") for s in sources),
                    "knowledge_seed_used": any(s.startswith("knowledge_seed") for s in sources),
                    "timestamp": datetime.now().isoformat()
                }

        # 1. FALLBACK: Real laboratories data
        lab_data = None
        if real_data_engine:
            logger.info("🔬 Fallback: Querying real laboratories for data...")
            try:
                lab_data = await real_data_engine.get_comprehensive_response(question)
                logger.info(f"✅ Real labs returned {lab_data.get('total_labs_queried', 0)} responses")
            except Exception as e:
                logger.warning(f"⚠️  Real data engine error: {e}")

        # 1. Get internal data
        internal_data = internal_data_sources.get_all_data()

        # 2. Route to specialist persona first (if enabled)
        persona_response = None
        if use_personas:
            persona = persona_router.route(question)
            persona_response = persona.answer(question, internal_data)
            logger.info(f"✅ Persona {persona.__class__.__name__} answered question")

        # 3. Process query with full knowledge engine
        processed = await query_processor.process(question)

        # 4. Generate comprehensive answer
        response = None
        if knowledge_engine:
            try:
                response = await knowledge_engine.answer_query(question, processed)
            except Exception as ke_error:
                logger.warning(f"Knowledge engine error: {ke_error}, using persona response")

        # If knowledge engine not available, create lightweight response
        if not response:
            # Generate enhanced findings - use real lab data if available!
            if lab_data and lab_data.get('lab_responses'):
                # Use REAL lab data instead of generic findings
                key_findings = [
                    {
                        "finding": lab['answer'][:200] + "...",
                        "importance": lab['quality_score'],
                        "source": lab['lab_name'],
                        "lab_domain": lab['domain'],
                        "confidence": lab['confidence']
                    }
                    for lab in lab_data.get('lab_responses', [])[:20]
                ]
            else:
                key_findings = generate_key_findings(question, persona_response)

            curiosity_threads = generate_curiosity_threads(question, key_findings)

            # Build ULTRA response with real lab data
            ultra_response = persona_response or "Analyzed based on internal data sources"
            if lab_data and lab_data.get('comprehensive_answer'):
                ultra_response = lab_data['comprehensive_answer']

            # Calculate elapsed time from 0.1ms to full response
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            response_dict = {
                "query": question,
                "intent": processed.intent.value if processed else "unknown",
                "response": ultra_response,
                "persona_answer": persona_response if use_personas else None,
                "key_findings": key_findings,
                "sources": {"internal": ["persona_analysis", "real_laboratories"] if lab_data else ["persona_analysis"], "external": []},
                "confidence": lab_data.get('average_confidence', 0.75) if lab_data else (0.75 if persona_response else 0.5),
                "processing_time_ms": round(elapsed_ms, 2),
                "curiosity_threads": curiosity_threads,
                "data_sources_used": ["internal_only", "real_labs"] if lab_data else ["internal_only"],
                "labs_queried": lab_data.get('total_labs_queried', 0) if lab_data else 0,
                "real_lab_data": lab_data if lab_data else None,
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Convert dataclass to dict
            response_dict = {
                "query": response.query,
                "intent": response.intent,
                "response": response.main_response,
                "persona_answer": persona_response if use_personas else None,
                "key_findings": response.key_findings,
                "sources": response.sources_cited,
                "confidence": response.confidence_score,
                "processing_time_ms": response.processing_time_ms,
                "curiosity_threads": [
                    {
                        "topic": thread.topic,
                        "question": thread.initial_question,
                        "related_topics": thread.related_topics,
                        "continue_with": thread.continue_suggestions,
                        "sources": thread.sources_used
                    }
                    for thread in response.curiosity_threads
                ],
                "data_sources_used": ["internal_only"],
                "timestamp": response.timestamp
            }

        return response_dict

    except ValueError as e:
        logger.warning(f"Query validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Query processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{API_PREFIX}/chat/specialized")
async def specialized_chat_endpoint(request: Request):
    """
    Specialized Expert Chat - Clean Interface

    Returns real, expert answers in your advanced domains:
    - Neuroscience & Brain Research
    - AI/ML & Deep Learning
    - Quantum Physics & Energy
    - IoT/LoRa & Sensor Networks
    - Cybersecurity & Encryption
    - Bioinformatics & Genetics
    - Data Science & Analytics
    - Marine Biology & Environmental Science

    NO system status - JUST expert answers.
    """
    if not specialized_chat:
        raise HTTPException(status_code=503, detail="Specialized Chat Engine not initialized")

    try:
        body = await request.json()
        query = body.get("query", body.get("message", "")).strip()
        requested_domain = (body.get("domain") or "").strip().lower()

        if not query:
            raise ValueError("Query cannot be empty")

        requested_domain = specialized_chat.normalize_domain(requested_domain)

        # Generate expert response
        response = await specialized_chat.generate_expert_response(query, domain=requested_domain)

        return {
            "type": "specialized_chat",
            "query": query,
            "domain": response["domain"],
            "domain_expertise": response["domain_expertise"],
            "answer": response["answer"],
            "response": response.get("response", response["answer"]),
            "sources": response["sources"],
            "confidence": response["confidence"],
            "follow_up_topics": response["follow_up_topics"],
            "timestamp": response["timestamp"]
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Chat processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{API_PREFIX}/chat/history")
async def get_chat_history(request: Request):
    """Get chat conversation history"""
    if not specialized_chat:
        raise HTTPException(status_code=503, detail="Specialized Chat Engine not initialized")

    try:
        body = await request.json()
        limit = body.get("limit", 20)

        history = specialized_chat.get_chat_history(limit)
        stats = specialized_chat.get_statistics()

        return {
            "messages": history,
            "statistics": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"History retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{API_PREFIX}/chat/clear")
async def clear_chat():
    """Clear chat history for new conversation"""
    if not specialized_chat:
        raise HTTPException(status_code=503, detail="Specialized Chat Engine not initialized")

    try:
        specialized_chat.clear_history()
        return {"status": "success", "message": "Chat history cleared", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Clear history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{API_PREFIX}/chat/spontaneous")
async def spontaneous_conversation(request: Request):
    """
    SPONTANEOUS CONVERSATION MODE
    ============================

    This is the NEW way to chat - with full context awareness!

    Features:
    - Understands references to previous discussion ("what we talked about")
    - Maintains conversation topic coherence
    - Adapts responses based on full conversation history
    - Can handle follow-ups and clarifications naturally
    - Natural multi-turn dialogue

    Returns:
    - context_aware: boolean (true if using previous context)
    - conversation_topic: the main topic being discussed
    - turn_number: which turn of conversation this is
    - follow_up_topics: context-aware suggestions

    Example flow:
    1. User: "Tell me about quantum computing"
    2. User: "How does error correction work?" → System remembers quantum context
    3. User: "And what about hardware?" → Continues quantum discussion
    """
    if not specialized_chat:
        raise HTTPException(status_code=503, detail="Specialized Chat Engine not initialized")

    try:
        body = await request.json()
        query = body.get("query", "").strip()
        use_context = body.get("use_context", True)  # Default: use conversation context
        requested_domain = (body.get("domain") or "").strip().lower()

        if not query:
            raise ValueError("Query cannot be empty")

        requested_domain = specialized_chat.normalize_domain(requested_domain)

        # Generate spontaneous response with context awareness
        response = await specialized_chat.generate_spontaneous_response(
            query,
            domain=requested_domain,
            use_context=use_context,
        )

        return {
            "type": "spontaneous_chat",
            "query": response["query"],
            "domain": response["domain"],
            "domain_expertise": response["domain_expertise"],
            "answer": response["answer"],
            "response": response.get("response", response["answer"]),
            "sources": response["sources"],
            "confidence": response["confidence"],
            "follow_up_topics": response["follow_up_topics"],
            "context_aware": response["context_aware"],
            "conversation_topic": response["conversation_topic"],
            "turn_number": response["turn_number"],
            "timestamp": response["timestamp"]
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Spontaneous chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{API_PREFIX}/chat")
async def chat_test(message: str = Query(default="Hello", description="Mesazhi për të testuar")):
    """
    GET CHAT ENDPOINT - Për testim në browser
    ==========================================

    Shembull: http://localhost:8030/api/chat?message=What%20is%20neuroplasticity
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    try:
        logger.info(f"💬 GET chat test: {message[:50]}...")
        result = await orchestrator.process_query_async(message)

        # Extract intent and complexity from understanding
        understanding = result.understanding or {}
        intent = understanding.get("intent", "exploratory")
        complexity = understanding.get("complexity_level", "simple")

        return {
            "response": result.fused_answer,
            "sources": result.sources_cited,
            "confidence": result.confidence,
            "query_category": result.query_category.value if hasattr(result.query_category, 'value') else str(result.query_category),
            "intent": intent,
            "complexity": complexity
        }
    except Exception as e:
        logger.error(f"GET chat error: {e}")
        return {"response": f"Gabim: {e}", "sources": [], "confidence": 0.0, "intent": "error", "complexity": "unknown"}


@app.get(f"{API_PREFIX}/signals/live")
async def get_live_signals(limit: int = Query(50, ge=1, le=500)):
    """Live signal feed for Curiosity Ocean dashboard."""
    try:
        try:
            from signal_fabric import get_signal_fabric  # type: ignore
            fabric = get_signal_fabric()
            events = fabric.recent(limit=limit)
        except Exception:
            events = []

        normalized_events = []
        for event in events:
            if isinstance(event, dict):
                normalized_events.append(event)
            elif hasattr(event, "__dict__"):
                normalized_events.append(dict(event.__dict__))

        levels = {}
        sources = {}
        for event in normalized_events:
            level = str(event.get("level", "info")).lower()
            src = str(event.get("source", "unknown"))
            levels[level] = levels.get(level, 0) + 1
            sources[src] = sources.get(src, 0) + 1

        return {
            "type": "live_signals",
            "status": "ok",
            "count": len(normalized_events),
            "signals": normalized_events,
            "levels": levels,
            "sources": sources,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Live signals error: {e}")
        return {
            "type": "live_signals",
            "status": "error",
            "count": 0,
            "signals": [],
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@app.get(f"{API_PREFIX}/signals/live/stream")
async def stream_live_signals(
    request: Request,
    limit: int = Query(40, ge=1, le=500),
    interval_ms: int = Query(2000, ge=500, le=10000),
):
    """SSE stream for live SignalFabric updates in Curiosity Ocean dashboard."""

    async def event_stream():
        while True:
            if await request.is_disconnected():
                break

            try:
                payload = await get_live_signals(limit=limit)
                stream_payload = {
                    "status": payload.get("status", "ok"),
                    "count": payload.get("count", 0),
                    "levels": payload.get("levels", {}),
                    "sources": payload.get("sources", {}),
                    "signals": payload.get("signals", [])[:10],
                    "timestamp": datetime.utcnow().isoformat(),
                }
                yield f"data: {json.dumps(stream_payload)}\n\n"
            except Exception as e:
                logger.warning(f"signals/live/stream iteration error: {e}")
                yield f"data: {json.dumps({'status': 'error', 'error': str(e), 'timestamp': datetime.utcnow().isoformat()})}\n\n"

            await asyncio.sleep(interval_ms / 1000.0)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get(f"{API_PREFIX}/system/health")
async def get_dashboard_system_health():
    """Dashboard-oriented consolidated system health."""
    full_status = await get_full_system_status()
    sources = await get_sources() if internal_data_sources else {}

    raw_summary = full_status.get("summary", {}) if isinstance(full_status, dict) else {}
    summary = raw_summary if isinstance(raw_summary, dict) else {}
    raw_metrics = sources.get("system_metrics", {}) if isinstance(sources, dict) else {}
    metrics = raw_metrics if isinstance(raw_metrics, dict) else {}
    raw_agi_agents = sources.get("agi_agents", {}) if isinstance(sources, dict) else {}
    agi_agents = raw_agi_agents if isinstance(raw_agi_agents, dict) else {}
    raw_jona = agi_agents.get("jona", {})
    jona = raw_jona if isinstance(raw_jona, dict) else {}

    return {
        "type": "system_health",
        "status": summary.get("health", "unknown"),
        "active_components": summary.get("active_components", 0),
        "total_components": summary.get("total_components", 0),
        "runtime_mode": full_status.get("runtime_mode", "unknown") if isinstance(full_status, dict) else "unknown",
        "metrics": {
            "cpu_percent": metrics.get("cpu_percent"),
            "memory_percent": metrics.get("memory_percent"),
            "disk_percent": metrics.get("disk_percent"),
        },
        "jona_health": jona.get("health", 0),
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get(f"{API_PREFIX}/agents/status")
async def get_dashboard_agents_status():
    """Dashboard snapshot for agent status and counts."""
    agents_payload = await get_agents()
    sources = await get_sources() if internal_data_sources else {}
    agi_agents = sources.get("agi_agents", {}) if isinstance(sources, dict) else {}

    return {
        "type": "agents_status",
        "status": "ok",
        "total": agents_payload.get("total", 0),
        "agents": agents_payload.get("agents", []),
        "trinity": {
            "alba": agi_agents.get("alba", {}),
            "albi": agi_agents.get("albi", {}),
            "jona": agi_agents.get("jona", {}),
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get(f"{API_PREFIX}/pipelines/status")
async def get_dashboard_pipelines_status():
    """Dashboard pipeline status derived from Mega Signal overview."""
    overview = await get_signals_overview()
    raw_overview = overview.get("overview", {}) if isinstance(overview, dict) else {}
    overview_data = raw_overview if isinstance(raw_overview, dict) else {}
    raw_managers = overview_data.get("managers", {})
    managers = raw_managers if isinstance(raw_managers, dict) else {}

    pipeline_entries = {
        key: value
        for key, value in managers.items()
        if "pipeline" in key.lower() or "flow" in key.lower()
    }

    return {
        "type": "pipelines_status",
        "status": overview.get("status", "unknown") if isinstance(overview, dict) else "unknown",
        "pipeline_managers": pipeline_entries,
        "manager_count": len(pipeline_entries),
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get(f"{API_PREFIX}/cycles/status")
async def get_dashboard_cycles_status():
    """Dashboard cycles status wrapper."""
    cycles_payload = await get_cycles()
    return {
        "type": "cycles_status",
        "status": "ok",
        "count": cycles_payload.get("count", 0),
        "cycles": cycles_payload.get("cycles", []),
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get(f"{API_PREFIX}/mali/insights")
async def get_dashboard_mali_insights():
    """MALI observability snapshot for dashboard."""
    try:
        mali_service = await _build_pulse_service_record("mali", probe=False)
    except Exception as e:
        mali_service = {
            "name": "mali",
            "status": "unknown",
            "error": str(e),
        }

    live_signals = await get_live_signals(limit=100)
    mali_signals = [
        sig for sig in live_signals.get("signals", [])
        if "mali" in str(sig.get("source", "")).lower() or "mali" in str(sig.get("kind", "")).lower()
    ]

    return {
        "type": "mali_insights",
        "status": mali_service.get("status", "unknown"),
        "service": mali_service,
        "signal_count": len(mali_signals),
        "recent_signals": mali_signals[:10],
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get(f"{API_PREFIX}/jona-real/harmony")
async def get_dashboard_jona_harmony():
    """JONA harmony score computed from trinity and system metrics."""
    sources = await get_sources() if internal_data_sources else {}
    jona_health = float(sources.get("agi_agents", {}).get("jona", {}).get("health", 0) or 0)
    metrics = sources.get("system_metrics", {}) if isinstance(sources, dict) else {}

    cpu = float(metrics.get("cpu_percent", 0) or 0)
    memory = float(metrics.get("memory_percent", 0) or 0)
    disk = float(metrics.get("disk_percent", 0) or 0)
    resource_health = max(0.0, 100.0 - ((cpu + memory + disk) / 3.0))
    harmony_score = round((jona_health + resource_health) / 2.0, 2)

    return {
        "type": "jona_harmony",
        "status": "ok",
        "jona_health": jona_health,
        "resource_health": round(resource_health, 2),
        "harmony_score": harmony_score,
        "metrics": {
            "cpu_percent": cpu,
            "memory_percent": memory,
            "disk_percent": disk,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


def _build_global_dashboard_presentation(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Convert technical snapshot into user-friendly, global-facing dashboard values."""
    signals = snapshot.get("signals", {}) if isinstance(snapshot, dict) else {}
    system = snapshot.get("system", {}) if isinstance(snapshot, dict) else {}
    agents = snapshot.get("agents", {}) if isinstance(snapshot, dict) else {}
    pipelines = snapshot.get("pipelines", {}) if isinstance(snapshot, dict) else {}
    cycles = snapshot.get("cycles", {}) if isinstance(snapshot, dict) else {}
    mali = snapshot.get("mali", {}) if isinstance(snapshot, dict) else {}
    jona = snapshot.get("jona", {}) if isinstance(snapshot, dict) else {}

    system_status = str(system.get("status", "unknown")).lower()
    if system_status in {"healthy", "ok", "active", "connected"}:
        platform_status = "Online"
    elif system_status in {"degraded", "partial"}:
        platform_status = "Partial"
    else:
        platform_status = "Checking"

    harmony = float(jona.get("harmony_score", 0) or 0)
    harmony_label = "Strong" if harmony >= 80 else ("Stable" if harmony >= 60 else "Needs attention")

    return {
        "audience": "global",
        "cards": {
            "signals": {
                "value": str(signals.get("count", 0)),
                "sub": f"{len(signals.get('sources', {}) or {})} active sources",
            },
            "system": {
                "value": platform_status,
                "sub": f"Platform health: {system.get('active_components', 0)}/{system.get('total_components', 0)} modules",
            },
            "agents": {
                "value": str(agents.get("total", 0)),
                "sub": "AI agents available",
            },
            "pipelines": {
                "value": str(pipelines.get("manager_count", 0)),
                "sub": "Automation flows active",
            },
            "cycles": {
                "value": str(cycles.get("count", 0)),
                "sub": "Continuous cycles running",
            },
            "mali": {
                "value": str(mali.get("signal_count", 0)),
                "sub": "Insights generated",
            },
            "jona": {
                "value": str(round(harmony, 2)),
                "sub": f"Harmony: {harmony_label}",
            },
        },
    }


async def _build_dashboard_snapshot(signals_limit: int = 40, audience: str = "global") -> dict[str, Any]:
    """Compose a unified dashboard payload for Curiosity Ocean live UI."""
    signals = await get_live_signals(limit=signals_limit)
    system = await get_dashboard_system_health()
    agents = await get_dashboard_agents_status()
    pipelines = await get_dashboard_pipelines_status()
    cycles = await get_dashboard_cycles_status()
    mali = await get_dashboard_mali_insights()
    jona = await get_dashboard_jona_harmony()

    snapshot = {
        "type": "dashboard_live",
        "status": "ok",
        "signals": signals,
        "system": system,
        "agents": agents,
        "pipelines": pipelines,
        "cycles": cycles,
        "mali": mali,
        "jona": jona,
        "audience": audience,
        "timestamp": datetime.utcnow().isoformat(),
    }

    if audience == "global":
        snapshot["presentation"] = _build_global_dashboard_presentation(snapshot)

    return snapshot


@app.get(f"{API_PREFIX}/dashboard/live")
async def get_dashboard_live(
    signals_limit: int = Query(40, ge=1, le=500),
    audience: str = Query("global", description="global or technical"),
):
    """Single-shot unified snapshot for all dashboard cards."""
    try:
        audience_mode = "technical" if str(audience).lower() == "technical" else "global"
        return await _build_dashboard_snapshot(signals_limit=signals_limit, audience=audience_mode)
    except Exception as e:
        logger.error(f"dashboard/live error: {e}")
        return {
            "type": "dashboard_live",
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@app.get(f"{API_PREFIX}/dashboard/live/stream")
async def stream_dashboard_live(
    request: Request,
    signals_limit: int = Query(40, ge=1, le=500),
    interval_ms: int = Query(2000, ge=500, le=10000),
    audience: str = Query("global", description="global or technical"),
):
    """SSE stream emitting unified dashboard payload for all cards."""

    async def event_stream():
        audience_mode = "technical" if str(audience).lower() == "technical" else "global"
        while True:
            if await request.is_disconnected():
                break

            try:
                payload = await _build_dashboard_snapshot(signals_limit=signals_limit, audience=audience_mode)
                yield f"data: {json.dumps(payload)}\n\n"
            except Exception as e:
                logger.warning(f"dashboard/live/stream iteration error: {e}")
                yield f"data: {json.dumps({'type': 'dashboard_live', 'status': 'error', 'error': str(e), 'timestamp': datetime.utcnow().isoformat()})}\n\n"

            await asyncio.sleep(interval_ms / 1000.0)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


def calculate_dynamic_timeout(
    message: str,
    conversation_context: list | None = None,
    base_timeout: float = 15.0,
    token_per_second: float = 20.0,
    max_timeout: float = 120.0,
    min_timeout: float = 15.0
) -> float:
    """
    Calculate elastic timeout based on content size and complexity.

    Factors:
    - Message length (tokens ~ 4 chars per token average)
    - Conversation history size
    - Response complexity markers (images, tables, figures, code, etc.)
    - Token estimation

    Returns:
    - Dynamic timeout in seconds, bounded between min_timeout and max_timeout
    """
    if conversation_context is None:
        conversation_context = []

    # Estimate tokens: ~1 token per 4 characters average
    message_tokens = len(message) / 4.0
    history_tokens = sum(len(msg) / 4.0 for msg in conversation_context[-10:])  # Last 10 messages
    total_input_tokens = message_tokens + history_tokens

    # Estimate output tokens (response typically 200-500 tokens)
    estimated_output_tokens = 300.0

    # Calculate generation time: output_tokens / token_per_second
    generation_time = estimated_output_tokens / token_per_second

    # Add overhead for orchestration, language detection, source attribution
    overhead = 3.0

    # Detect complexity markers that require longer processing
    complexity_multiplier = 1.0

    # Visual content indicators
    if any(marker in message.lower() for marker in ['image', 'chart', 'graph', 'diagram', 'table', 'figure', 'icon', 'visual', 'foto', 'fotografi', 'ikonë', 'tabela', 'grafik']):
        complexity_multiplier = 1.5  # 50% more time

    # Code/technical content indicators
    if any(marker in message.lower() for marker in ['code', 'program', 'function', 'algorithm', 'data structure', 'script', 'api', 'database']):
        complexity_multiplier = max(complexity_multiplier, 1.3)  # 30% more time

    # Long conversation context (more context = more processing)
    if len(conversation_context) > 15:
        complexity_multiplier *= 1.2  # Additional 20% for long context

    # Dynamic timeout calculation
    timeout = base_timeout + generation_time + overhead
    timeout = timeout * complexity_multiplier

    # Enforce bounds: min 15s (simple queries), max 120s (complex multi-document)
    timeout = max(min_timeout, min(timeout, max_timeout))

    logger.debug(f"⏱️ Dynamic timeout: {timeout:.1f}s (input:{total_input_tokens:.0f}t, output:{estimated_output_tokens:.0f}t, complexity:{complexity_multiplier:.1f}x, history_len:{len(conversation_context)})")

    return timeout


def _is_heartbeat_probe(message: str) -> bool:
    normalized = (message or "").strip().lower()
    return normalized in {
        "ping",
        "pong",
        "health",
        "health check",
        "healthcheck",
        "probe",
        "latency probe",
    }


@app.post(f"{API_PREFIX}/chat")
async def simple_chat(request: Request):
    """
    SIMPLE CHAT ENDPOINT - ORCHESTRATOR V5
    =======================================

    Fast path conversational - 100% lokal, pa API të jashtme.

    Body:
    {
        "message": "Përshëndetje! Si je?",
        "user_id": "user_xxx" (optional)
    }

    Returns:
    {
        "response": "Mirëdita! Jam mirë, faleminderit...",
        "sources": ["conversational_greeting"],
        "confidence": 0.98
    }
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    body: dict[str, Any] = {}
    try:
        body = await request.json()
        message = body.get("message", body.get("query", "")).strip()
        raw_messages_obj = body.get("messages")
        raw_messages: list[Any] = raw_messages_obj if isinstance(raw_messages_obj, list) else []
        conversation_context = []
        for item in raw_messages[-20:]:
            if not isinstance(item, dict):
                continue
            role = str(item.get("role", "user")).strip() or "user"
            content = str(item.get("content", "")).strip()
            if content:
                conversation_context.append(f"{role}: {content}")

        # Get user context from request
        user_id = (
            body.get("user_id")
            or body.get("clerk_user_id")
            or request.headers.get("X-User-ID")
            or request.headers.get("X-User-Id")
            or request.headers.get("X-Clerk-User-Id")
        )
        user_name = body.get("user_name")
        request_language = body.get("user_language") or body.get("language") or ""
        accept_language = request.headers.get("Accept-Language", "")
        user_language, language_source = resolve_conversation_language(
            message=message,
            conversation_context=conversation_context,
            request_language=request_language,
            accept_language=accept_language,
        )

        if not message:
            return {
                "response": _language_message(
                    user_language,
                    {
                        "sq": "Ju lutem shkruani diçka për të vazhduar bisedën.",
                        "de": "Bitte schreiben Sie etwas, um das Gespräch fortzusetzen.",
                        "fr": "Veuillez écrire quelque chose pour continuer la conversation.",
                        "it": "Scrivi qualcosa per continuare la conversazione.",
                        "es": "Escribe algo para continuar la conversación.",
                        "en": "Please write something to continue the conversation.",
                    },
                    "Please write something to continue the conversation.",
                ),
                "sources": [],
                "confidence": 1.0,
                "language": user_language,
            }

        if _is_heartbeat_probe(message):
            return {
                "response": "pong",
                "sources": ["heartbeat_probe"],
                "confidence": 1.0,
                "language": user_language,
                "query_category": "health",
                "fast_path": True,
            }

        # Log with user context
        user_info = f"[User: {user_name or user_id or 'anonymous'}]" if user_id else ""
        logger.info(
            f"💬 Chat v5 {user_info}: {message[:50]}... "
            f"(lang:{user_language}, source:{language_source})"
        )
        _publish_ocean_signal_background(
            event="chat_message",
            message=message,
            language=user_language,
            metadata={
                "endpoint": "chat",
                "language_source": language_source,
                "has_user": bool(user_id),
            },
        )

        external_context = await _collect_external_context_for_query(message)
        enriched_message = _compose_enriched_query(
            message,
            external_context.get("context_block", ""),
            conversation_context=conversation_context,
        )

        # Use Orchestrator v5 with conversational context for flow continuity
        # ELASTIC TIMEOUT: Dynamically scaled based on content size, complexity, and history
        adaptive_timeout = calculate_dynamic_timeout(
            message=message,
            conversation_context=conversation_context,
            base_timeout=float(os.getenv("OCEAN_TIMEOUT_BASE", "15.0")),
            token_per_second=float(os.getenv("OCEAN_TOKEN_RATE", "20.0")),
            max_timeout=float(os.getenv("OCEAN_TIMEOUT_MAX", "120.0")),
            min_timeout=float(os.getenv("OCEAN_TIMEOUT_MIN", "15.0"))
        )

        try:
            result = await asyncio.wait_for(
                orchestrator.orchestrate(
                    enriched_message,
                    conversation_context=conversation_context,
                    mode="conversational",
                    user_context={
                        "external_sources": external_context.get("sources", []),
                    },
                    user_language=user_language,
                ),
                timeout=adaptive_timeout,
            )
        except asyncio.TimeoutError:
            logger.warning(f"⏱️ Chat timeout guard triggered after {adaptive_timeout:.1f}s")
            raise HTTPException(status_code=504, detail="Processing timeout")
        return {
            "response": result.fused_answer,
            "sources": list(dict.fromkeys((result.sources_cited or []) + [f"external:{src}" for src in external_context.get("sources", [])])),
            "confidence": result.confidence,
            "language": result.language,
            "query_category": result.query_category.value if hasattr(result.query_category, 'value') else str(result.query_category),
            "user_identified": bool(user_id),
            "external_sources_used": external_context.get("sources", []),
        }

    except Exception as e:
        logger.error(f"Chat v5 error: {e}")
        fallback_language = "en"
        if isinstance(body, dict):
            request_language = body.get("user_language") or body.get("language") or ""
            accept_language = request.headers.get("Accept-Language", "")
            fallback_language, _ = resolve_conversation_language(
                message=body.get("message", body.get("query", "")) if isinstance(body.get("message", body.get("query", "")), str) else "",
                conversation_context=[],
                request_language=request_language,
                accept_language=accept_language,
            )
        return {
            "response": _language_message(
                fallback_language,
                {
                    "sq": f"Ndodhi një gabim: {str(e)}. Ju lutem provoni përsëri.",
                    "de": f"Es ist ein Fehler aufgetreten: {str(e)}. Bitte versuchen Sie es erneut.",
                    "fr": f"Une erreur s'est produite : {str(e)}. Veuillez réessayer.",
                    "it": f"Si è verificato un errore: {str(e)}. Riprova.",
                    "es": f"Se produjo un error: {str(e)}. Inténtalo de nuevo.",
                    "en": f"An error occurred: {str(e)}. Please try again.",
                },
                f"An error occurred: {str(e)}. Please try again.",
            ),
            "sources": [],
            "confidence": 0.0
        }


@app.post(f"{API_PREFIX}/chat/fast")
async def fast_chat(request: Request):
    """
    FAST CHAT ENDPOINT - <=2s target
    =================================

    Dedicated low-latency endpoint for frontend microservice routing.
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    body: dict[str, Any] = {}
    fast_language = "en"
    try:
        body = await request.json()
        message = body.get("message", body.get("query", "")).strip()
        raw_messages_obj = body.get("messages")
        raw_messages: list[Any] = raw_messages_obj if isinstance(raw_messages_obj, list) else []
        conversation_context = []
        for item in raw_messages[-20:]:
            if not isinstance(item, dict):
                continue
            role = str(item.get("role", "user")).strip() or "user"
            content = str(item.get("content", "")).strip()
            if content:
                conversation_context.append(f"{role}: {content}")
        if not message:
            return {
                "response": _language_message(
                    fast_language,
                    {
                        "sq": "Ju lutem shkruani një pyetje.",
                        "de": "Bitte schreiben Sie eine Frage.",
                        "fr": "Veuillez écrire une question.",
                        "it": "Scrivi una domanda.",
                        "es": "Escribe una pregunta.",
                        "en": "Please enter a question.",
                    },
                    "Please enter a question.",
                ),
                "sources": [],
                "confidence": 1.0,
                "fast_path": True,
            }

        # Extract language from request
        request_language = body.get("user_language") or body.get("language") or ""
        accept_language = request.headers.get("Accept-Language", "")
        fast_language, _ = resolve_conversation_language(
            message=message,
            conversation_context=conversation_context,
            request_language=request_language,
            accept_language=accept_language,
        )
        _publish_ocean_signal_background(
            event="chat_fast_message",
            message=message,
            language=fast_language,
            metadata={
                "endpoint": "chat/fast",
                "fast_path": True,
            },
        )

        external_context = await _collect_external_context_for_query(message)
        enriched_message = _compose_enriched_query(
            message,
            external_context.get("context_block", ""),
            conversation_context=conversation_context,
        )

        # ELASTIC TIMEOUT: Dynamically scaled based on content size, complexity, and history
        adaptive_timeout = calculate_dynamic_timeout(
            message=message,
            conversation_context=conversation_context,
            base_timeout=float(os.getenv("OCEAN_TIMEOUT_BASE", "15.0")),
            token_per_second=float(os.getenv("OCEAN_TOKEN_RATE", "20.0")),
            max_timeout=float(os.getenv("OCEAN_TIMEOUT_MAX", "120.0")),
            min_timeout=float(os.getenv("OCEAN_TIMEOUT_MIN", "15.0"))
        )
        result = await asyncio.wait_for(
            orchestrator.orchestrate(
                enriched_message,
                conversation_context=conversation_context,
                mode="conversational",
                user_context={
                    "external_sources": external_context.get("sources", []),
                },
                user_language=fast_language,
            ),
            timeout=adaptive_timeout,
        )

        return {
            "response": result.fused_answer,
            "sources": list(dict.fromkeys((result.sources_cited or []) + [f"external:{src}" for src in external_context.get("sources", [])])),
            "confidence": result.confidence,
            "query_category": result.query_category.value if hasattr(result.query_category, 'value') else str(result.query_category),
            "fast_path": True,
            "timeout_seconds": adaptive_timeout,
            "external_sources_used": external_context.get("sources", []),
        }
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Processing timeout")
    except Exception as e:
        logger.error(f"Fast chat error: {e}")
        return {
            "response": _language_message(
                fast_language,
                {
                    "sq": f"Ndodhi një gabim: {str(e)}",
                    "de": f"Es ist ein Fehler aufgetreten: {str(e)}",
                    "fr": f"Une erreur s'est produite : {str(e)}",
                    "it": f"Si è verificato un errore: {str(e)}",
                    "es": f"Se produjo un error: {str(e)}",
                    "en": f"An error occurred: {str(e)}",
                },
                f"An error occurred: {str(e)}",
            ),
            "sources": [],
            "confidence": 0.0,
            "fast_path": True,
        }


@app.post(f"{API_PREFIX}/chat/stream/warm")
async def warm_stream(request: Request):
    """
    TYPEAHEAD PRE-WARM ENDPOINT
    ===========================
    Call this while the user is still typing (e.g. on keypress or after
    500ms debounce). Ocean fetches external context and pre-builds the
    enriched prompt into _WARM_CACHE so that when /chat/stream is called
    the response starts in <0.3s instead of waiting 2-8s.

    Body: { "message": "partial or full user text" }
    Returns: { "status": "warmed", "context_ready": bool }
    """
    global _WARM_CACHE
    try:
        body = await request.json()
        message = str(body.get("message", body.get("query", ""))).strip()
        if not message or len(message) < 6:
            return {"status": "skipped", "reason": "too_short"}

        cache_key = f"warm:{message[:120]}"
        if cache_key in _WARM_CACHE:
            return {"status": "already_warmed", "context_ready": True}

        # Collect context with full timeout (non-blocking to caller)
        async def _warm_build():
            try:
                ext = await asyncio.wait_for(
                    _collect_external_context_for_query(message),
                    timeout=EXTERNAL_CONTEXT_TIMEOUT_SECONDS
                )
                context_block = ext.get("context_block", "")
            except Exception:
                context_block = ""

            enriched = _compose_enriched_query(message, context_block)
            _raw_lang = body.get("language") or ""
            lang, _ = resolve_conversation_language(
                message=message, conversation_context=[],
                request_language=_raw_lang, accept_language=""
            )
            lang_code = lang if lang and lang != "und" else _detect_lang72(message, default="en")
            lang_instr = _lang72_instruction(lang_code)
            prompt = f"{lang_instr}\n\nUser message:\n{enriched}"

            # LRU eviction
            if len(_WARM_CACHE) >= _WARM_CACHE_MAX:
                oldest = next(iter(_WARM_CACHE))
                del _WARM_CACHE[oldest]

            _WARM_CACHE[cache_key] = {
                "prompt": prompt,
                "context_ready": bool(context_block),
                "ts": time.time(),
            }
            logger.info(f"🔥 Warm cache built for: {message[:50]}... (context={'yes' if context_block else 'no'})")

        asyncio.ensure_future(_warm_build())
        return {"status": "warming", "context_ready": False}

    except Exception as e:
        logger.error(f"Warm endpoint error: {e}")
        return {"status": "error", "error": str(e)}


@app.post(f"{API_PREFIX}/chat/stream")
async def streaming_chat(request: Request):
    """
    STREAMING CHAT ENDPOINT - Real-time response (INSTANT START)
    ===========================================================

    ✅ INSTANT STREAMING:
    - Starts writing within 0.2 seconds
    - Streams response tokens as they generate
    - Parallel generation & transmission

    No waiting for full response - text appears immediately!

    Body:
    {
        "message": "Përshëndetje! Si je?"
    }

    Returns: SSE stream with chunks (starts immediately)
    """
    from ollama_fast_engine import get_fast_engine

    try:
        body = await request.json()
        message = body.get("message", body.get("query", "")).strip()
        raw_messages_obj = body.get("messages")
        raw_messages: list[Any] = raw_messages_obj if isinstance(raw_messages_obj, list) else []
        conversation_context = []
        for item in raw_messages[-20:]:
            if not isinstance(item, dict):
                continue
            role = str(item.get("role", "user")).strip() or "user"
            content = str(item.get("content", "")).strip()
            if content:
                conversation_context.append(f"{role}: {content}")
        _raw_lang = body.get("user_language") or body.get("language") or ""
        _accept_lang = request.headers.get("Accept-Language", "")
        language, lang_source = resolve_conversation_language(
            message=message,
            conversation_context=conversation_context,
            request_language=_raw_lang,
            accept_language=_accept_lang,
        )

        if not message:
            return StreamingResponse(
                iter(["data: {\"error\": \"Message required\"}\n\n"]),
                media_type="text/event-stream"
            )

        logger.info(
            f"🌊 Streaming chat: {message[:50]}... "
            f"(lang:{language}, source:{lang_source}, instant start)"
        )
        _publish_ocean_signal_background(
            event="chat_stream_message",
            message=message,
            language=language,
            metadata={
                "endpoint": "chat/stream",
                "language_source": lang_source,
                "streaming": True,
            },
        )

        # ─────────────────────────────────────────────────────────────────
        # HUMAN-THINKING MODEL: Ocean "listens" while the user types.
        #
        # WARM HIT  → Ocean was already reading this message (typeahead
        #             pre-warm called during typing). Prompt is ready, 0ms.
        #
        # COLD MISS → No pre-warm. Start generation INSTANTLY with the
        #             base context (no blocking). A background task
        #             collects external context and stores it in the warm
        #             cache — if the user sends the same message again or
        #             a follow-up, the next response is instant.
        # ─────────────────────────────────────────────────────────────────

        _warm_key = f"warm:{message[:120]}"
        _warm_cached = _WARM_CACHE.get(_warm_key)

        if not _warm_cached:
            # Cold miss: fire-and-forget context build for future warmth.
            # Generation will start below with no external context blocking.
            asyncio.ensure_future(_collect_external_context_for_query(message))

        async def generate_stream():
            """
            HUMAN-THINKING STREAMING:
            - Warm cache hit  → 0ms wait, Ocean already understood the message
            - Cold (no cache) → 0ms wait, start talking immediately; context
              will be ready for the next exchange.
            First token is always <0.3s.
            """
            engine = get_fast_engine()
            start_gen = time.time()
            system_prompt = _build_stream_system_prompt(language)
            lang_code = language if language and language != "und" else _detect_lang72(message, default="en")
            language_instruction = _lang72_instruction(lang_code)

            if _warm_cached and isinstance(_warm_cached, dict):
                # Ocean was already reading — use the pre-built enriched prompt.
                prompt_for_generation = _warm_cached.get("prompt", "")
                # Clean up warm entry so stale context is not reused.
                _WARM_CACHE.pop(_warm_key, None)
                logger.info(f"⚡ Human-thinking HIT: {message[:40]}... (was already reading)")
            else:
                # Cold path: build prompt with conversation context only.
                # External facts are NOT needed for most conversational replies.
                base_enriched = _compose_enriched_query(
                    message,
                    "",  # no external context — generation starts instantly
                    conversation_context=conversation_context,
                )
                prompt_for_generation = f"{language_instruction}\n\nUser message:\n{base_enriched}"
                logger.info(f"💬 Human-thinking COLD: {message[:40]}... (instant, no wait)")

            try:
                chunk_count = 0
                async for chunk in engine.generate_stream(prompt_for_generation, system=system_prompt):
                    chunk_count += 1
                    elapsed = time.time() - start_gen
                    yield f"data: {{\"chunk\": {json.dumps(chunk)}, \"sequence\": {chunk_count}, \"elapsed_ms\": {int(elapsed*1000)}}}\n\n"
                    if chunk_count % 100 == 0:
                        logger.debug(f"📡 Streaming: chunk {chunk_count}, {elapsed:.2f}s elapsed")

                total_time = time.time() - start_gen
                logger.info(f"✅ Stream complete: {chunk_count} chunks in {total_time:.2f}s")
                yield f"data: {{\"status\": \"complete\", \"chunks\": {chunk_count}, \"total_ms\": {int(total_time*1000)}}}\n\n"

            except Exception as e:
                yield f"data: {{\"error\": {json.dumps(str(e))}}}\n\n"
                logger.error(f"Stream generation error: {e}")

            yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
                "Transfer-Encoding": "chunked",
                "Content-Encoding": "none"
            }
        )

    except Exception as e:
        logger.error(f"Streaming chat error: {e}")
        return StreamingResponse(
            iter([f"data: {{\"error\": {json.dumps(str(e))}}}\n\n"]),
            media_type="text/event-stream"
        )


@app.post(f"{API_PREFIX}/chat/binary")
async def binary_chat(request: Request):
    """
    BINARY CHAT ENDPOINT - CBOR2 / MessagePack
    ==========================================

    Pranon dhe kthen të dhëna në format binary (CBOR2 ose MessagePack).

    Content-Type pranuar:
    - application/cbor (CBOR2 - preferuar)
    - application/msgpack (MessagePack)
    - application/json (fallback)

    Returns: Same format as input (binary response)
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    try:
        content_type = request.headers.get("content-type", "application/json")
        raw_body = await request.body()

        # Parse based on content type
        if "cbor" in content_type and HAS_CBOR2:
            body = cbor2.loads(raw_body)
            response_format = "cbor"
            logger.info("📦 CBOR2 request received")
        elif "msgpack" in content_type and HAS_MSGPACK:
            body = msgpack.loads(raw_body)
            response_format = "msgpack"
            logger.info("📦 MessagePack request received")
        else:
            import json
            body = json.loads(raw_body)
            response_format = "json"

        message = body.get("message", body.get("query", "")).strip()

        if not message:
            result_data = {
                "response": "Ju lutem shkruani diçka.",
                "sources": [],
                "confidence": 1.0,
                "format": response_format
            }
        else:
            logger.info(f"💬 Binary chat ({response_format}): {message[:50]}...")

            try:
                result = await orchestrator.process_query_async(message)
                result_data = {
                    "response": result.fused_answer,
                    "sources": result.sources_cited,
                    "confidence": result.confidence,
                    "query_category": result.query_category.value if hasattr(result.query_category, 'value') else str(result.query_category),
                    "format": response_format
                }
            except Exception as e:
                logger.warning(f"Async failed: {e}, using sync")
                result = orchestrator.process_query(message)
                result_data = {
                    "response": result.fused_answer,
                    "sources": result.sources_cited,
                    "confidence": result.confidence,
                    "format": response_format
                }

        # Return in same format
        if response_format == "cbor" and HAS_CBOR2:
            return Response(
                content=cbor2.dumps(result_data),
                media_type="application/cbor"
            )
        elif response_format == "msgpack" and HAS_MSGPACK:
            return Response(
                content=msgpack.dumps(result_data),
                media_type="application/msgpack"
            )
        else:
            return result_data

    except Exception as e:
        logger.error(f"Binary chat error: {e}")
        error_data = {
            "response": f"Gabim: {str(e)}",
            "sources": [],
            "confidence": 0.0
        }
        return error_data


@app.post(f"{API_PREFIX}/chat/orchestrated")
async def orchestrated_response(request: Request):
    """
    ORCHESTRATED RESPONSE - ORCHESTRATOR V5 (DEEP MODE)
    ====================================================

    Deep mode - përdor edhe ekspertë kur ka sens.
    100% LOKAL - pa API të jashtme me pagesë.

    Features:
    - RealAnswerEngine (fast path)
    - Minimal experts (1 persona + 1 lab + 1 module)
    - Multilingual support
    - Timeouts për ekspertët
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator v5 not initialized")

    try:
        body = await request.json()
        query = body.get("query", body.get("message", "")).strip()
        conversation_context = body.get("conversation_context", [])
        mode = body.get("mode", "deep")  # Default: deep mode për orchestrated

        if not query:
            raise ValueError("Query cannot be empty")

        logger.info(f"🧠 Orchestrator v5 ({mode}): {query[:60]}...")

        # Check Autolearning Engine for cached responses
        knowledge_id = None
        if autolearning_engine:
            learning_result = autolearning_engine.process_query(query)

            # Use cached if high-confidence
            if learning_result.get('cached_knowledge'):
                cached = learning_result['cached_knowledge']
                if cached.get('helpfulness', 0) > 0.7 and cached.get('confidence', 0) > 0.85:
                    logger.info("   ✅ Using learned response")
                    return {
                        "type": "learned_response",
                        "query": query,
                        "query_category": "learned",
                        "fused_answer": cached['response'],
                        "sources_cited": ["autolearning"],
                        "confidence": cached['confidence'],
                        "timestamp": datetime.utcnow().isoformat()
                    }

            # Use pattern response if available
            if learning_result.get('pattern_response'):
                return {
                    "type": "pattern_response",
                    "query": query,
                    "query_category": learning_result['pattern_type'],
                    "fused_answer": learning_result['pattern_response'],
                    "sources_cited": ["pattern_detector"],
                    "confidence": 0.95,
                    "timestamp": datetime.utcnow().isoformat()
                }

        # Use Orchestrator v5
        orchestrated = await orchestrator.orchestrate(query, conversation_context, mode=mode)

        # Learn from response
        if autolearning_engine:
            knowledge_id = autolearning_engine.learn_from_response(
                query=query,
                response=orchestrated.fused_answer,
                sources=orchestrated.sources_cited,
                confidence=orchestrated.confidence
            )

        return {
            "type": "orchestrated_v5",
            "query": orchestrated.query,
            "query_category": orchestrated.query_category.value,
            "language": orchestrated.language,
            "understanding": orchestrated.understanding,
            "consulted_experts": [
                {
                    "type": c.expert_type,
                    "name": c.expert_name,
                    "confidence": c.confidence,
                    "relevance": c.relevance_score,
                }
                for c in orchestrated.consulted_experts
            ],
            "fused_answer": orchestrated.fused_answer,
            "sources_cited": orchestrated.sources_cited,
            "confidence": orchestrated.confidence,
            "narrative_quality": orchestrated.narrative_quality,
            "learning_record": {"knowledge_id": knowledge_id} if knowledge_id else {},
            "timestamp": orchestrated.timestamp
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Orchestrator v5 error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{API_PREFIX}/orchestrator/learning")
async def get_orchestrator_learning():
    """Get the learning stats from orchestrator v5"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator v5 not initialized")

    try:
        stats = orchestrator.get_stats()
        return {
            "type": "orchestrator_v5_stats",
            "version": stats.get("version", "v5"),
            "engine_active": stats.get("engine_active", False),
            "learning_history_count": stats.get("learning_history_count", 0),
            "expert_timeout_ms": stats.get("expert_timeout_ms", 500),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Orchestrator stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{API_PREFIX}/autolearning/stats")
async def get_autolearning_stats():
    """
    Get Autolearning Engine statistics

    Shows:
    - Total knowledge entries learned
    - Top queries used
    - Pattern statistics
    - Session learning info
    """
    if not autolearning_engine:
        raise HTTPException(status_code=503, detail="Autolearning Engine not initialized")

    try:
        stats = autolearning_engine.get_learning_stats()
        return {
            "type": "autolearning_stats",
            "knowledge_base": stats["knowledge_base"],
            "patterns": stats["patterns"],
            "session": stats["session"],
            "independence": {
                "internal_sources": True,
                "external_api_dependency": False,
                "description": "Sistemi mëson dhe funksionon pa varësi nga API të jashtme"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Autolearning stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{API_PREFIX}/autolearning/feedback")
async def autolearning_feedback(request: Request):
    """
    Record user feedback for a response

    Body:
    - knowledge_id: ID of the knowledge entry
    - helpful: true/false
    """
    if not autolearning_engine:
        raise HTTPException(status_code=503, detail="Autolearning Engine not initialized")

    try:
        body = await request.json()
        knowledge_id = body.get("knowledge_id")
        helpful = body.get("helpful", True)

        if not knowledge_id:
            raise ValueError("knowledge_id is required")

        autolearning_engine.record_feedback(knowledge_id, helpful)

        return {
            "status": "recorded",
            "knowledge_id": knowledge_id,
            "feedback": "helpful" if helpful else "not_helpful",
            "message": "Faleminderit për feedback-un! Sistemi do të mësojë nga kjo."
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Feedback error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{API_PREFIX}/chat/domains")
async def get_domains():
    """Get available expertise domains"""
    if not specialized_chat:
        raise HTTPException(status_code=503, detail="Specialized Chat Engine not initialized")

    domains = {}
    for domain_name, domain_info in specialized_chat.EXPERTISE_DOMAINS.items():
        domains[domain_name] = {
            "focus": domain_info["focus"],
            "expertise_level": domain_info["expertise_level"],
            "keywords": domain_info["keywords"][:5],  # Show first 5 keywords
            "labs": domain_info["labs"]
        }

    return {
        "domains": domains,
        "total_domains": len(domains),
        "total_labs": len(set(lab for d in domains.values() for lab in d["labs"])),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get(f"{API_PREFIX}/labs")
async def get_labs():
    """Get all location labs data"""
    if not laboratory_network:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        labs_dicts = laboratory_network.get_all_labs()
        # labs_dicts is already a list of dicts from get_all_labs()
        return {
            "labs": labs_dicts,
            "total": len(labs_dicts),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Labs data error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{API_PREFIX}/agents")
async def get_agents():
    """Get all agent telemetry"""
    if not internal_data_sources:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        internal_data = internal_data_sources.get_all_data()
        return {
            "agents": internal_data.get("agents", []),
            "total": len(internal_data.get("agents", [])),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Agents data error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(API_PREFIX + "/threads/{topic}")
async def get_curiosity_thread(topic: str):
    """Get curiosity threads for exploration"""

    if not topic:
        raise HTTPException(status_code=400, detail="Topic required")

    # Map common topics to threads
    threads_map = {
        "laboratory": {
            "topic": "Geographic Laboratory Networks",
            "related": ["Elbasan", "Tirana", "Durrës", "Shkodër", "Vlorë", "Korça","Sarandë","Zürich","Roma"],
            "explore": [
                "What domains are most active?",
                "Which locations have highest quality data?",
                "What's the correlation between lab domains?",
                "How are labs interconnected across countries?"
            ]
        },
        "agents": {
            "topic": "Agent Intelligence & Decisions",
            "related": ["ALBA", "ALBI", "Blerina", "AGIEM", "ASI"],
            "explore": [
                "What are the top agent decisions?",
                "Which agent has highest confidence?",
                "What anomalies were detected?",
                "How do agents coordinate?"
            ]
        },
        "system": {
            "topic": "System Infrastructure & Performance",
            "related": ["CPU", "Memory", "Latency", "Uptime"],
            "explore": [
                "What are current metrics?",
                "Are there performance bottlenecks?",
                "How's resource utilization?",
                "What's the trend over time?"
            ]
        }
    }

    thread = threads_map.get(topic.lower())

    if not thread:
        raise HTTPException(status_code=404, detail=f"Topic '{topic}' not found")

    return {
        "topic": thread["topic"],
        "related_entities": thread["related"],
        "explore_further": thread["explore"],
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ocean-core-8030",
        "timestamp": datetime.now().isoformat()
    }


# =============================================================================
# AI PROCESSING ENDPOINTS
# =============================================================================

@app.post(f"{API_PREFIX}/ai/sentiment")
async def analyze_sentiment(request: Request):
    """
    Analyze sentiment and emotions in text

    Body: {"text": "Your text here", "use_llm": true}
    """
    try:
        from ai_processes import get_sentiment_analyzer

        data = await request.json()
        text = data.get("text", "")
        use_llm = data.get("use_llm", True)

        if not text:
            raise HTTPException(status_code=400, detail="Text is required")

        analyzer = get_sentiment_analyzer()
        await analyzer.initialize()
        result = await analyzer.analyze(text, use_llm=use_llm)

        return {
            "success": True,
            "result": result.to_dict(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{API_PREFIX}/ai/summarize")
async def summarize_text(request: Request):
    """
    Generate summary of text

    Body: {"text": "Long text...", "type": "hybrid", "target_ratio": 0.3}
    Types: extractive, abstractive, hybrid, bullet_points, tldr
    """
    try:
        from ai_processes import get_text_summarizer
        from ai_processes.text_summarizer import SummaryType

        data = await request.json()
        text = data.get("text", "")
        summary_type = data.get("type", "hybrid")
        target_ratio = data.get("target_ratio", 0.3)
        max_sentences = data.get("max_sentences", 5)

        if not text:
            raise HTTPException(status_code=400, detail="Text is required")

        # Map string to enum
        type_map = {
            "extractive": SummaryType.EXTRACTIVE,
            "abstractive": SummaryType.ABSTRACTIVE,
            "hybrid": SummaryType.HYBRID,
            "bullet_points": SummaryType.BULLET_POINTS,
            "tldr": SummaryType.TLDR
        }
        stype = type_map.get(summary_type, SummaryType.HYBRID)

        summarizer = get_text_summarizer()
        await summarizer.initialize()
        result = await summarizer.summarize(
            text,
            summary_type=stype,
            target_ratio=target_ratio,
            max_sentences=max_sentences
        )

        return {
            "success": True,
            "result": result.to_dict(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Summarization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{API_PREFIX}/ai/entities")
async def extract_entities(request: Request):
    """
    Extract named entities from text (NER)

    Body: {"text": "Text with names, places, dates...", "use_llm": true}
    """
    try:
        from ai_processes import get_entity_extractor

        data = await request.json()
        text = data.get("text", "")
        use_llm = data.get("use_llm", True)

        if not text:
            raise HTTPException(status_code=400, detail="Text is required")

        extractor = get_entity_extractor()
        await extractor.initialize()
        result = await extractor.extract(text, use_llm=use_llm)

        return {
            "success": True,
            "result": result.to_dict(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Entity extraction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{API_PREFIX}/ai/classify")
async def classify_text(request: Request):
    """
    Classify text into categories

    Body: {"text": "Text to classify...", "use_llm": true}
    """
    try:
        from ai_processes import get_text_classifier

        data = await request.json()
        text = data.get("text", "")
        use_llm = data.get("use_llm", True)

        if not text:
            raise HTTPException(status_code=400, detail="Text is required")

        classifier = get_text_classifier()
        await classifier.initialize()
        result = await classifier.classify(text, use_llm=use_llm)

        return {
            "success": True,
            "result": result.to_dict(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Classification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{API_PREFIX}/ai/analyze-code")
async def analyze_code(request: Request):
    """
    Analyze source code structure and quality

    Body: {"code": "def hello():\\n    pass", "language": "python"}
    """
    try:
        from ai_processes import get_code_analyzer

        data = await request.json()
        code = data.get("code", "")
        language = data.get("language")  # Optional, auto-detect if not provided

        if not code:
            raise HTTPException(status_code=400, detail="Code is required")

        analyzer = get_code_analyzer()
        await analyzer.initialize()
        result = await analyzer.analyze(code, language=language)

        return {
            "success": True,
            "result": result.to_dict(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Code analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{API_PREFIX}/ai/detect-language")
async def detect_language(request: Request):
    """
    Detect language of text

    Body: {"text": "Përshëndetje, si jeni?"}
    """
    try:
        from ai_processes import get_language_detector

        data = await request.json()
        text = data.get("text", "")

        if not text:
            raise HTTPException(status_code=400, detail="Text is required")

        detector = get_language_detector()
        await detector.initialize()
        result = await detector.detect(text)

        return {
            "success": True,
            "result": result.to_dict(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Language detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{API_PREFIX}/ai/intent")
async def classify_intent(request: Request):
    """
    Classify user intent from message

    Body: {"message": "I want to order a pizza", "use_llm": true}
    """
    try:
        from ai_processes import get_intent_classifier

        data = await request.json()
        message = data.get("message", "")
        use_llm = data.get("use_llm", True)

        if not message:
            raise HTTPException(status_code=400, detail="Message is required")

        classifier = get_intent_classifier()
        await classifier.initialize()
        result = await classifier.classify(message, use_llm=use_llm)

        return {
            "success": True,
            "result": result.to_dict(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Intent classification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{API_PREFIX}/ai/process")
async def unified_ai_process(request: Request):
    """
    Unified AI processing endpoint - run multiple analyses at once

    Body: {
        "text": "Text to analyze...",
        "processes": ["sentiment", "entities", "language", "classify"]
    }
    """
    try:
        from ai_processes import (
            get_entity_extractor,
            get_intent_classifier,
            get_language_detector,
            get_sentiment_analyzer,
            get_text_classifier,
            get_text_summarizer,
        )

        data = await request.json()
        text = data.get("text", "")
        processes = data.get("processes", ["sentiment", "language"])

        if not text:
            raise HTTPException(status_code=400, detail="Text is required")

        results = {}

        if "sentiment" in processes:
            analyzer = get_sentiment_analyzer()
            await analyzer.initialize()
            results["sentiment"] = (await analyzer.analyze(text)).to_dict()

        if "entities" in processes:
            extractor = get_entity_extractor()
            await extractor.initialize()
            results["entities"] = (await extractor.extract(text)).to_dict()

        if "language" in processes:
            detector = get_language_detector()
            await detector.initialize()
            results["language"] = (await detector.detect(text)).to_dict()

        if "classify" in processes:
            classifier = get_text_classifier()
            await classifier.initialize()
            results["classification"] = (await classifier.classify(text)).to_dict()

        if "summarize" in processes:
            summarizer = get_text_summarizer()
            await summarizer.initialize()
            results["summary"] = (await summarizer.summarize(text)).to_dict()

        if "intent" in processes:
            intent_clf = get_intent_classifier()
            await intent_clf.initialize()
            results["intent"] = (await intent_clf.classify(text)).to_dict()

        return {
            "success": True,
            "text_preview": text[:200] + "..." if len(text) > 200 else text,
            "processes_run": list(results.keys()),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Unified AI processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{API_PREFIX}/ai/capabilities")
async def ai_capabilities():
    """List all available AI processing capabilities"""
    return {
        "capabilities": [
            {
                "name": "sentiment",
                "endpoint": f"{API_PREFIX}/ai/sentiment",
                "method": "POST",
                "description": "Sentiment and emotion analysis"
            },
            {
                "name": "summarize",
                "endpoint": f"{API_PREFIX}/ai/summarize",
                "method": "POST",
                "description": "Text summarization"
            },
            {
                "name": "entities",
                "endpoint": f"{API_PREFIX}/ai/entities",
                "method": "POST",
                "description": "Named Entity Recognition"
            },
            {
                "name": "classify",
                "endpoint": f"{API_PREFIX}/ai/classify",
                "method": "POST",
                "description": "Text classification"
            },
            {
                "name": "analyze-code",
                "endpoint": f"{API_PREFIX}/ai/analyze-code",
                "method": "POST",
                "description": "Source code analysis"
            },
            {
                "name": "detect-language",
                "endpoint": f"{API_PREFIX}/ai/detect-language",
                "method": "POST",
                "description": "Language detection"
            },
            {
                "name": "intent",
                "endpoint": f"{API_PREFIX}/ai/intent",
                "method": "POST",
                "description": "User intent classification"
            },
            {
                "name": "process",
                "endpoint": f"{API_PREFIX}/ai/process",
                "method": "POST",
                "description": "Unified multi-process analysis"
            }
        ],
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


# =============================================================================
# END AI PROCESSING ENDPOINTS
# =============================================================================


@app.get(f"{API_PREFIX}/spec")
async def api_spec():
    """OpenAPI specification"""
    return app.openapi()


@app.get("/api/chat")
async def api_chat_redirect():
    """Redirect to chat UI"""
    return FileResponse("specialized_chat.html", media_type="text/html")


@app.get("/api/status")
async def api_status_short():
    """Short status endpoint without version"""
    return {
        "service": "Curiosity Ocean",
        "version": "4.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }


@app.get(f"{API_PREFIX}/laboratories")
async def get_all_laboratories():
    """Get all 23 specialized laboratories with their functions"""
    try:
        lab_network = get_laboratory_network()
        return {
            "total_laboratories": len(lab_network.labs),
            "laboratories": lab_network.get_all_labs(),
            "network_stats": lab_network.get_network_stats(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Laboratories data error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{API_PREFIX}/laboratories/summary")
async def get_laboratories_summary():
    """Get summary of all 23 laboratories"""
    try:
        lab_network = get_laboratory_network()
        return lab_network.get_all_labs_summary()
    except Exception as e:
        logger.error(f"Laboratories summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{API_PREFIX}/laboratories/types")
async def get_laboratory_types():
    """Get all unique laboratory types"""
    try:
        lab_network = get_laboratory_network()
        return {
            "types": lab_network.get_lab_types(),
            "count": len(lab_network.get_lab_types()),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Laboratory types error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(API_PREFIX + "/laboratories/{lab_id}")
async def get_laboratory(lab_id: str):
    """Get specific laboratory by ID"""
    try:
        lab_network = get_laboratory_network()
        lab = lab_network.get_lab_by_id(lab_id)

        if not lab:
            raise HTTPException(status_code=404, detail=f"Laboratory '{lab_id}' not found")

        return {
            "laboratory": lab.to_dict(),
            "status_summary": lab.get_status_summary(),
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Laboratory lookup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(API_PREFIX + "/laboratories/type/{lab_type}")
async def get_laboratories_by_type(lab_type: str):
    """Get laboratories by type"""
    try:
        lab_network = get_laboratory_network()
        labs = lab_network.get_labs_by_type(lab_type)

        if not labs:
            raise HTTPException(status_code=404, detail=f"No laboratories of type '{lab_type}' found")

        return {
            "type": lab_type,
            "count": len(labs),
            "laboratories": [lab.to_dict() for lab in labs],
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Laboratory type lookup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(API_PREFIX + "/laboratories/location/{location}")
async def get_laboratories_by_location(location: str):
    """Get laboratories by location"""
    try:
        lab_network = get_laboratory_network()
        labs = lab_network.get_labs_by_location(location)

        if not labs:
            raise HTTPException(status_code=404, detail=f"No laboratories in '{location}' found")

        return {
            "location": location,
            "count": len(labs),
            "laboratories": [lab.to_dict() for lab in labs],
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Laboratory location lookup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(API_PREFIX + "/laboratories/function/{keyword}")
async def get_laboratories_by_function(keyword: str):
    """Get laboratories by function keyword"""
    try:
        lab_network = get_laboratory_network()
        labs = lab_network.get_labs_by_function_keyword(keyword)

        if not labs:
            raise HTTPException(status_code=404, detail=f"No laboratories with function containing '{keyword}' found")

        return {
            "keyword": keyword,
            "count": len(labs),
            "laboratories": [lab.to_dict() for lab in labs],
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Laboratory function lookup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# MEGA SIGNAL INTEGRATOR ENDPOINTS
# =============================================================================

@app.get(f"{API_PREFIX}/signals/overview")
async def get_signals_overview():
    """
    🌊 MEGA SIGNAL SYSTEM OVERVIEW

    Returns status of all signal managers:
    - Cycles, Alignments, Proposals
    - Kubernetes, CI/CD
    - News, Data Sources (5000+ from 200+ countries)
    """
    try:
        from mega_signal_integrator import get_mega_signal_integrator
        integrator = get_mega_signal_integrator()
        overview = integrator.get_system_overview()

        return {
            "type": "mega_signal_overview",
            "status": "connected",
            "overview": overview,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Mega Signal overview error: {e}")
        return {
            "type": "mega_signal_overview",
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@app.get(f"{API_PREFIX}/signals/anatomy")
async def get_system_anatomy():
    """
    🫀 SYSTEM ANATOMY MAP

    Returns the unified Clisonix body-map domains and their activation intents.
    """
    return {
        "type": "system_anatomy",
        "status": "ready",
        "domains": SYSTEM_ANATOMY,
        "activate_endpoint": f"{API_PREFIX}/signals/activate",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post(f"{API_PREFIX}/signals/activate")
async def activate_system_domains(payload: AnatomyActivateRequest):
    """
    ⚡ ACTIVATE SYSTEM DOMAINS (SAFE MODE)

    Activates selected domains by running orchestrated intent queries through
    Mega Signal Integrator (read-safe, no destructive operations).
    """
    try:
        from mega_signal_integrator import get_mega_signal_integrator
        integrator = get_mega_signal_integrator()

        targets = payload.targets or list(SYSTEM_ANATOMY.keys())
        normalized_targets = [t for t in targets if t in SYSTEM_ANATOMY]

        if not normalized_targets:
            raise HTTPException(
                status_code=400,
                detail="No valid targets. Use keys from /signals/anatomy",
            )

        activated = []
        for target in normalized_targets:
            spec = SYSTEM_ANATOMY[target]
            result = await integrator.process_query(spec["activation_query"])
            activated.append(
                {
                    "target": target,
                    "label": spec["label"],
                    "query": spec["activation_query"],
                    "sources_checked": result.get("sources_checked", []),
                    "status": "active" if result.get("sources_checked") else "partial",
                }
            )

        response = {
            "type": "system_activation",
            "mode": "safe-read",
            "requested": targets,
            "activated": activated,
            "activated_count": len(activated),
            "timestamp": datetime.utcnow().isoformat(),
        }

        if payload.include_overview:
            response["overview"] = integrator.get_system_overview()

        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"System activation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{API_PREFIX}/pulse")
async def get_pulse_overview():
    """Unified pulse overview for routes, services, signals, and runtime state."""
    runtime = _get_orchestrator_runtime()
    mega_signal = _get_mega_signal_status()
    services = [await _build_pulse_service_record(name, probe=False) for name in PULSE_SERVICE_CATALOG]

    return {
        "type": "pulse_overview",
        "status": "ready",
        "runtime": runtime,
        "mega_signal": mega_signal.get("status"),
        "service_count": len(services),
        "active_or_reachable": sum(1 for item in services if item["status"] in {"active", "reachable", "connected"}),
        "disabled": [item["name"] for item in services if item["status"] == "disabled"],
        "aliases": PULSE_ROUTE_ALIASES,
        "anatomy_domains": list(SYSTEM_ANATOMY.keys()),
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get(f"{API_PREFIX}/pulse/routes")
async def get_pulse_routes():
    """Return all pulse alias routes and their target endpoints."""
    return {
        "type": "pulse_routes",
        "status": "ready",
        "aliases": {
            "overview": {"path": PULSE_ROUTE_ALIASES["overview"], "target": None},
            "routes": {"path": PULSE_ROUTE_ALIASES["routes"], "target": None},
            "services": {"path": PULSE_ROUTE_ALIASES["services"], "target": None},
            "personas": {"path": PULSE_ROUTE_ALIASES["personas"], "target": f"{API_PREFIX}/personas"},
            "agents": {"path": PULSE_ROUTE_ALIASES["agents"], "target": f"{API_PREFIX}/agents"},
            "labs": {"path": PULSE_ROUTE_ALIASES["labs"], "target": f"{API_PREFIX}/labs"},
            "sources": {"path": PULSE_ROUTE_ALIASES["sources"], "target": f"{API_PREFIX}/sources"},
            "signals": {"path": PULSE_ROUTE_ALIASES["signals"], "target": f"{API_PREFIX}/signals/overview"},
            "anatomy": {"path": PULSE_ROUTE_ALIASES["anatomy"], "target": f"{API_PREFIX}/signals/anatomy"},
            "autolearning": {"path": PULSE_ROUTE_ALIASES["autolearning"], "target": f"{API_PREFIX}/autolearning/stats"},
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get(f"{API_PREFIX}/pulse/services")
async def get_pulse_services(probe: bool = Query(False, description="Probe known HTTP services before returning results")):
    """Audit services and modules requested around Ocean integration, with optional live probing."""
    services = [await _build_pulse_service_record(name, probe=probe) for name in PULSE_SERVICE_CATALOG]
    return {
        "type": "pulse_services",
        "status": "ready",
        "probe_enabled": probe,
        "services": services,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get(f"{API_PREFIX}/pulse/services/{{service_name}}")
async def get_pulse_service(service_name: str, probe: bool = Query(True, description="Probe HTTP service when URLs are known")):
    """Detailed pulse audit for one named service or module."""
    normalized = service_name.strip().lower().replace("-", "_")
    if normalized not in PULSE_SERVICE_CATALOG:
        raise HTTPException(status_code=404, detail=f"Unknown pulse service '{service_name}'")

    return await _build_pulse_service_record(normalized, probe=probe)


@app.get(f"{API_PREFIX}/pulse/personas")
async def pulse_personas():
    """Pulse alias for personas with safe disabled-state response."""
    try:
        return await get_personas()
    except HTTPException as exc:
        return {
            "type": "pulse_personas",
            "status": "disabled",
            "detail": exc.detail,
            "timestamp": datetime.utcnow().isoformat(),
        }


@app.get(f"{API_PREFIX}/pulse/agents")
async def pulse_agents():
    """Pulse alias for agent telemetry and registry visibility."""
    try:
        payload = await get_agents()
    except HTTPException as exc:
        payload = {
            "agents": [],
            "total": 0,
            "status": "unavailable",
            "detail": exc.detail,
            "timestamp": datetime.utcnow().isoformat(),
        }

    payload["registry_module_present"] = _repo_file_exists("agents.py")
    payload["type"] = "pulse_agents"
    return payload


@app.get(f"{API_PREFIX}/pulse/labs")
async def pulse_labs():
    """Pulse alias for labs."""
    try:
        payload = await get_labs()
    except HTTPException as exc:
        payload = {
            "labs": [],
            "total": 0,
            "status": "unavailable",
            "detail": exc.detail,
            "timestamp": datetime.utcnow().isoformat(),
        }

    payload["type"] = "pulse_labs"
    return payload


@app.get(f"{API_PREFIX}/pulse/sources")
async def pulse_sources():
    """Pulse alias for internal/open data source visibility."""
    try:
        payload = await get_sources()
    except HTTPException as exc:
        payload = {
            "type": "pulse_sources",
            "status": "unavailable",
            "detail": exc.detail,
            "timestamp": datetime.utcnow().isoformat(),
        }
        return payload

    payload["type"] = "pulse_sources"
    payload["free_external_api_catalog"] = ["Wikipedia", "ArXiv", "PubMed", "GitHub", "DBPedia"]
    payload["free_external_api_runtime"] = "disabled_in_active_ocean_runtime"
    return payload


@app.get(f"{API_PREFIX}/pulse/signals")
async def pulse_signals():
    """Pulse alias for Mega Signal overview."""
    payload = await get_signals_overview()
    payload["type"] = "pulse_signals"
    return payload


@app.get(f"{API_PREFIX}/pulse/anatomy")
async def pulse_anatomy():
    """Pulse alias for anatomy domains."""
    payload = await get_system_anatomy()
    payload["type"] = "pulse_anatomy"
    return payload


@app.get(f"{API_PREFIX}/pulse/autolearning")
async def pulse_autolearning():
    """Pulse alias for autolearning status with disabled-state visibility."""
    try:
        payload = await get_autolearning_stats()
    except HTTPException as exc:
        payload = {
            "type": "pulse_autolearning",
            "status": "disabled",
            "detail": exc.detail,
            "active_runtime": "ocean_api.py",
            "full_runtime_candidate": "ocean_core_full.py",
            "timestamp": datetime.utcnow().isoformat(),
        }
        return payload

    payload["type"] = "pulse_autolearning"
    return payload


def _normalize_web_url(raw_url: str) -> str:
    candidate = (raw_url or "").strip()
    if not candidate:
        raise HTTPException(status_code=400, detail="url is required")

    if not candidate.startswith(("http://", "https://")):
        candidate = f"https://{candidate}"

    parsed = urlparse(candidate)
    host = (parsed.hostname or "").lower()
    if parsed.scheme not in {"http", "https"}:
        raise HTTPException(status_code=400, detail="Only http/https URLs are allowed")

    blocked_hosts = {
        "localhost",
        "127.0.0.1",
        "0.0.0.0",
        "::1",
        "clisonix-ocean-core",
        "ocean-core",
        "clisonix-api",
    }
    if host in blocked_hosts:
        raise HTTPException(status_code=400, detail="Local/internal hosts are not allowed")

    return candidate


def _html_to_plain_text(content: str, max_chars: int = 8000) -> str:
    stripped = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", content)
    stripped = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", stripped)
    stripped = re.sub(r"(?is)<[^>]+>", " ", stripped)
    stripped = html.unescape(stripped)
    stripped = re.sub(r"\s+", " ", stripped).strip()
    return stripped[:max_chars]


async def _browse_url_content(target_url: str, max_chars: int = 8000) -> dict[str, Any]:
    normalized_url = _normalize_web_url(target_url)
    headers = {
        "User-Agent": "ClisonixOceanWebReader/1.0 (+https://clisonix.com)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        response = await client.get(normalized_url, headers=headers)
        response.raise_for_status()
        body = response.text

    title_match = re.search(r"(?is)<title[^>]*>(.*?)</title>", body)
    title = html.unescape(title_match.group(1).strip()) if title_match else normalized_url
    text = _html_to_plain_text(body, max_chars=max_chars)

    return {
        "url": str(response.url) if 'response' in locals() else normalized_url,
        "title": title,
        "content": text,
        "char_count": len(text),
        "status": "ok",
    }


@app.get(f"{API_PREFIX}/search")
async def web_reader_search(q: str = Query(..., min_length=2), num: int = Query(5, ge=1, le=20)):
    """Free web search endpoint for Web Reader proxy."""
    query = q.strip()
    endpoint = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
    headers = {
        "User-Agent": "ClisonixOceanWebReader/1.0",
        "Accept": "text/html",
    }

    results: list[dict[str, str]] = []
    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            response = await client.get(endpoint, headers=headers)
            response.raise_for_status()
            html_body = response.text

        for match in re.finditer(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', html_body, flags=re.IGNORECASE | re.DOTALL):
            url = html.unescape(match.group(1))
            title = re.sub(r"<[^>]+>", "", match.group(2))
            title = html.unescape(title).strip()
            if not title or not url:
                continue
            results.append({"title": title, "url": url})
            if len(results) >= num:
                break
    except Exception as e:
        logger.warning(f"Web search failed: {e}")

    return {
        "query": query,
        "results": results,
        "total": len(results),
        "source": "duckduckgo_html",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get(f"{API_PREFIX}/browse")
async def web_reader_browse(url: str = Query(...), max_chars: int = Query(8000, ge=500, le=50000)):
    """Browse and extract text content from a public webpage."""
    try:
        payload = await _browse_url_content(url, max_chars=max_chars)
        payload["timestamp"] = datetime.utcnow().isoformat()
        return payload
    except HTTPException:
        raise
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"Upstream returned {e.response.status_code}")
    except Exception as e:
        logger.error(f"Web browse error: {e}")
        raise HTTPException(status_code=500, detail="Failed to browse URL")


@app.post(f"{API_PREFIX}/chat/browse")
async def web_reader_chat_browse(request: Request):
    """Answer user question based on webpage content."""
    body = await request.json()
    target_url = (body.get("url") or "").strip()
    message = (body.get("message") or body.get("query") or "").strip()

    if not target_url or not message:
        raise HTTPException(status_code=400, detail="url and message are required")

    page = await _browse_url_content(target_url, max_chars=10000)
    composed_query = (
        "Webpage analysis task. Use the page context to answer accurately.\n\n"
        f"URL: {page['url']}\n"
        f"Title: {page['title']}\n"
        f"Page content:\n{page['content']}\n\n"
        f"User question: {message}"
    )

    answer = ""
    sources: list[str] = [str(page["url"])]

    if orchestrator:
        try:
            result = await orchestrator.process_query_async(composed_query)
            answer = getattr(result, "fused_answer", "") or ""
            sources_cited = getattr(result, "sources_cited", None)
            if isinstance(sources_cited, list):
                sources.extend([str(item) for item in sources_cited])
        except Exception as e:
            logger.warning(f"chat/browse orchestrator async failed: {e}")

    if not answer and orchestrator:
        try:
            sync_result = orchestrator.process_query(composed_query)
            answer = getattr(sync_result, "fused_answer", "") or ""
        except Exception as e:
            logger.warning(f"chat/browse orchestrator sync failed: {e}")

    if not answer:
        answer = (
            f"I read '{page['title']}' but the advanced engine is currently unavailable. "
            "Please retry in a few seconds."
        )

    return {
        "status": "success",
        "url": page["url"],
        "title": page["title"],
        "response": answer,
        "answer": answer,
        "sources": list(dict.fromkeys(sources)),
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post(f"{API_PREFIX}/chat/browse/stream")
async def web_reader_chat_browse_stream(request: Request):
    """SSE wrapper for browse+chat used by Web Reader streaming UI."""
    body = await request.json()
    target_url = (body.get("url") or "").strip()
    message = (body.get("message") or body.get("query") or "").strip()

    if not target_url or not message:
        return StreamingResponse(
            iter(["data: {\"error\": \"url and message are required\"}\n\n"]),
            media_type="text/event-stream",
        )

    async def event_stream():
        try:
            yield f"data: {json.dumps({'status': 'browsing', 'title': target_url})}\n\n"
            response = await web_reader_chat_browse(request)
            answer = str(response.get("response", ""))
            yield f"data: {json.dumps({'status': 'thinking'})}\n\n"

            chunk_size = 120
            for idx in range(0, len(answer), chunk_size):
                chunk = answer[idx: idx + chunk_size]
                yield f"data: {json.dumps({'token': chunk, 'status': 'streaming'})}\n\n"

            yield f"data: {json.dumps({'status': 'complete', 'total_chars': len(answer)})}\n\n"
        except Exception as e:
            logger.error(f"chat/browse/stream error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get(f"{API_PREFIX}/layers/unified")
async def get_unified_layers_profile(
    depth: float = Query(5.0, ge=0.5, le=12.0, description="Unified layer depth from 0.5 to 12"),
    mode: str = Query("hybrid", description="Cognitive mode: feeling | thinking | hybrid"),
):
    """Return unified layer governance profile and creator capabilities."""
    normalized_mode = mode.strip().lower()
    if normalized_mode not in COGNITIVE_MODES:
        raise HTTPException(status_code=400, detail="Invalid mode. Use: feeling, thinking, hybrid")

    active_stage = _get_unified_layer_stage(depth)
    return {
        "type": "unified_layers_profile",
        "requested_depth": depth,
        "active_stage": active_stage,
        "mode": normalized_mode,
        "mode_profile": COGNITIVE_MODES[normalized_mode],
        "stages": UNIFIED_LAYER_STAGES,
        "creator_capabilities": CREATOR_CAPABILITIES,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get(f"{API_PREFIX}/ocean/validate")
async def validate_ocean_runtime():
    """Validate Ocean runtime coverage for main.py, SaaS signal, unified layers, and ocean full module."""
    summary = _compute_ocean_validation_summary()
    summary["type"] = "ocean_validation"
    return summary


@app.post(f"{API_PREFIX}/signals/query")
async def query_signals(request: Request):
    """
    🔍 QUERY MEGA SIGNAL SYSTEM

    Ask about cycles, alignments, proposals, kubernetes,
    data sources, and more!
    """
    try:
        from mega_signal_integrator import get_mega_signal_integrator
        integrator = get_mega_signal_integrator()

        body = await request.json()
        query = body.get("query", body.get("message", "")).strip()

        if not query:
            raise ValueError("Query cannot be empty")

        result = await integrator.process_query(query)

        return {
            "type": "mega_signal_query",
            "query": query,
            "response": result.get("response", ""),
            "sources_checked": result.get("sources_checked", []),
            "signals": result.get("signals", []),
            "timestamp": datetime.utcnow().isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Mega Signal query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{API_PREFIX}/signals/cycles")
async def get_cycles():
    """Get all active cycles"""
    try:
        from mega_signal_integrator import get_mega_signal_integrator
        integrator = get_mega_signal_integrator()
        cycles = integrator.cycle_manager.get_active_cycles()

        return {
            "type": "cycles",
            "count": len(cycles),
            "cycles": cycles,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Cycles error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{API_PREFIX}/signals/cycles")
async def create_cycle(request: Request):
    """Create a new cycle"""
    try:
        from mega_signal_integrator import get_mega_signal_integrator
        integrator = get_mega_signal_integrator()

        body = await request.json()
        domain = body.get("domain", "general")
        source = body.get("source", "api")
        interval = body.get("interval_seconds", 300)

        signal = integrator.cycle_manager.create_cycle(domain, source, interval)

        return {
            "type": "cycle_created",
            "signal": {
                "id": signal.signal_id,
                "message": signal.message,
                "data": signal.data
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Create cycle error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{API_PREFIX}/signals/proposals")
async def create_proposal(request: Request):
    """Create a new proposal"""
    try:
        from mega_signal_integrator import get_mega_signal_integrator
        integrator = get_mega_signal_integrator()

        body = await request.json()
        title = body.get("title", "New Proposal")
        domain = body.get("domain", "general")
        description = body.get("description", "")

        signal = integrator.proposal_manager.create_proposal(title, domain, description)

        return {
            "type": "proposal_created",
            "signal": {
                "id": signal.signal_id,
                "message": signal.message,
                "data": signal.data
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Create proposal error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{API_PREFIX}/signals/kubernetes")
async def get_kubernetes_status():
    """Get Kubernetes cluster status"""
    try:
        from mega_signal_integrator import get_mega_signal_integrator
        integrator = get_mega_signal_integrator()
        signal = integrator.devops_manager.get_kubernetes_status()

        return {
            "type": "kubernetes_status",
            "message": signal.message,
            "data": signal.data,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Kubernetes status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{API_PREFIX}/signals/data-sources")
async def get_data_sources_summary():
    """
    🌍 GET 5000+ DATA SOURCES FROM 200+ COUNTRIES

    Returns summary of all available data sources:
    - EEG/Neuro (OpenNeuro, PhysioNet)
    - Scientific (PubMed, ArXiv, NCBI)
    - Statistics EU (Eurostat, Destatis, INSEE)
    - Statistics Asia (China NBS, Japan, Korea)
    - Finance (ECB, IMF, World Bank, CoinGecko)
    - Environment (Copernicus, NASA, NOAA)
    - Health (WHO, CDC, ECDC)
    - News (NewsAPI, Guardian, NY Times)
    - IoT (FIWARE, Smart Data Models)
    - International (UN Data, WTO, ILO, FAO)
    """
    try:
        from mega_signal_integrator import get_mega_signal_integrator
        integrator = get_mega_signal_integrator()
        signal = integrator.news_data_manager.get_data_sources_summary()

        return {
            "type": "data_sources",
            "message": signal.message,
            "total_sources": signal.data.get("total", 0),
            "categories": signal.data.get("categories", {}),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Data sources error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{API_PREFIX}/signals/data-sources/search")
async def search_data_sources(query: str = Query(..., description="Search query for data sources")):
    """Search data sources by keyword"""
    try:
        from mega_signal_integrator import get_mega_signal_integrator
        integrator = get_mega_signal_integrator()
        results = integrator.news_data_manager.search_sources(query)

        return {
            "type": "data_sources_search",
            "query": query,
            "count": len(results),
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Data sources search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{API_PREFIX}/signals/lora")
async def get_lora_status():
    """
    📡 GET LORA/LORAWAN NETWORK STATUS

    Returns status of LoRa gateways and nodes.
    Low-power wide-area network for IoT.
    """
    try:
        from mega_signal_integrator import get_mega_signal_integrator
        integrator = get_mega_signal_integrator()
        signal = integrator.lora_manager.get_network_status()

        return {
            "type": "lora_status",
            "message": signal.message,
            "data": signal.data,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"LoRa status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{API_PREFIX}/signals/lora/nodes")
async def register_lora_node(request: Request):
    """Register a new LoRa node"""
    try:
        from mega_signal_integrator import get_mega_signal_integrator
        integrator = get_mega_signal_integrator()

        body = await request.json()
        node_id = body.get("node_id", f"node_{datetime.utcnow().timestamp()}")
        node_type = body.get("node_type", "sensor")
        metadata = body.get("metadata", {})

        signal = integrator.lora_manager.register_node(node_id, node_type, metadata)

        return {
            "type": "lora_node_registered",
            "signal": {"id": signal.signal_id, "message": signal.message, "data": signal.data},
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"LoRa node registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{API_PREFIX}/signals/nanogrid")
async def get_nanogrid_status():
    """
    🔌 GET NANOGRID GATEWAY STATUS

    Returns status of embedded devices:
    - ESP32 (WiFi, BLE, I2C)
    - STM32 (LoRa, UART, DMA)
    - ASIC (LoRa, UART)
    - Raspberry Pi
    """
    try:
        from mega_signal_integrator import get_mega_signal_integrator
        integrator = get_mega_signal_integrator()
        signal = integrator.nanogrid_manager.get_gateway_status()

        return {
            "type": "nanogrid_status",
            "message": signal.message,
            "data": signal.data,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Nanogrid status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{API_PREFIX}/signals/nanogrid/devices")
async def register_nanogrid_device(request: Request):
    """Register a new Nanogrid device"""
    try:
        from mega_signal_integrator import get_mega_signal_integrator
        integrator = get_mega_signal_integrator()

        body = await request.json()
        device_id = body.get("device_id", f"dev_{datetime.utcnow().timestamp()}")
        model = body.get("model", "CUSTOM_IOT")
        metadata = body.get("metadata", {})

        signal = integrator.nanogrid_manager.register_device(device_id, model, metadata)

        return {
            "type": "nanogrid_device_registered",
            "signal": {"id": signal.signal_id, "message": signal.message, "data": signal.data},
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Nanogrid device registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{API_PREFIX}/signals/nanogrid/telemetry")
async def receive_telemetry(request: Request):
    """Receive telemetry from Nanogrid device"""
    try:
        from mega_signal_integrator import get_mega_signal_integrator
        integrator = get_mega_signal_integrator()

        body = await request.json()
        device_id = body.get("device_id")
        payload = body.get("payload", {})

        if not device_id:
            raise ValueError("device_id is required")

        signal = integrator.nanogrid_manager.process_telemetry(device_id, payload)

        return {
            "type": "telemetry_received",
            "signal": {"id": signal.signal_id, "message": signal.message},
            "timestamp": datetime.utcnow().isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Telemetry error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{API_PREFIX}/signals/nodes")
async def get_nodes_status():
    """Get nodes, arrays, and buffers status"""
    try:
        from mega_signal_integrator import get_mega_signal_integrator
        integrator = get_mega_signal_integrator()
        status = integrator.node_array_manager.get_status()

        return {
            "type": "node_array_status",
            "data": status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Nodes status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{API_PREFIX}/signals/formats")
async def get_data_formats():
    """
    📦 GET SUPPORTED DATA FORMATS

    Returns info about supported formats:
    - CBOR (39% smaller than JSON)
    - JSON (human readable)
    - YAML (config files)
    - MsgPack (30% smaller than JSON)
    """
    try:
        from mega_signal_integrator import get_mega_signal_integrator
        integrator = get_mega_signal_integrator()
        signal = integrator.format_manager.get_all_formats()

        return {
            "type": "data_formats",
            "message": signal.message,
            "formats": signal.data,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Formats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents/capabilities")
@app.get(f"{API_PREFIX}/documents/capabilities")
async def documents_capabilities():
    """Industrial document pipeline capabilities and operational limits."""
    return {
        "service": "Curiosity Ocean Document Core",
        "status": "operational",
        "max_upload_bytes": DOCUMENT_MAX_BYTES,
        "supported_mime_types": sorted(list(DOCUMENT_MIME_ALLOWLIST)),
        "features": {
            "scan_read": True,
            "checksum_sha256": True,
            "parser_fallback_chain": True,
            "contract_generation": True,
            "provenance_tracking": True,
            "ocr_for_scanned_docs": False,
        },
        "endpoints": [
            f"{API_PREFIX}/documents/scan",
            f"{API_PREFIX}/documents/generate",
            f"{API_PREFIX}/documents/agents",
        ],
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/api/documents/agents")
@app.get(f"{API_PREFIX}/documents/agents")
async def documents_agents():
    """List available industrial document agents."""
    try:
        _document_agents_module = importlib.import_module("document_agents")
        list_agents = getattr(_document_agents_module, "list_agents", None)
        if callable(list_agents):
            return {
                "agents": list_agents(),
                "timestamp": datetime.utcnow().isoformat(),
            }
        else:
            raise HTTPException(status_code=503, detail="document_agents module found but list_agents function not available")
    except ImportError:
        logger.warning("document_agents module not found")
        raise HTTPException(status_code=503, detail="Document agents service not available")
    except Exception as e:
        logger.error(f"Document agents listing error: {e}")
        raise HTTPException(status_code=500, detail="Failed to list document agents")


@app.post("/api/documents/scan")
@app.post(f"{API_PREFIX}/documents/scan")
async def documents_scan(file: UploadFile = File(...), max_chars: int = Query(default=120000, ge=2000, le=500000)):
    """Industrial upload + scan/read endpoint with metadata and parser provenance."""
    started = time.perf_counter()
    ingestion_id = f"DOC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:10]}"

    try:
        raw = await file.read()
        size_bytes = len(raw)
        content_type = (file.content_type or "application/octet-stream").lower()
        filename = file.filename or "unknown"

        if size_bytes == 0:
            raise HTTPException(status_code=400, detail="Empty file")
        if size_bytes > DOCUMENT_MAX_BYTES:
            raise HTTPException(status_code=413, detail=f"File too large. Limit is {DOCUMENT_MAX_BYTES} bytes")

        lower_name = filename.lower()
        extension_allowed = lower_name.endswith((".pdf", ".doc", ".docx", ".xls", ".xlsx", ".txt", ".csv", ".json", ".md"))
        mime_allowed = content_type in DOCUMENT_MIME_ALLOWLIST
        if not (extension_allowed or mime_allowed):
            raise HTTPException(status_code=415, detail=f"Unsupported document type: {content_type}")

        sha256 = hashlib.sha256(raw).hexdigest()
        extraction = _extract_text_from_document(filename, content_type, raw, max_chars=max_chars)
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)

        return {
            "ingestion_id": ingestion_id,
            "filename": filename,
            "content_type": content_type,
            "size_bytes": size_bytes,
            "sha256": sha256,
            "extraction": {
                "parser": extraction["parser"],
                "text_length": extraction["text_length"],
                "units": extraction["units"],
                "text_preview": extraction["text"][:2000],
                "text": extraction["text"],
            },
            "provenance": {
                "source_type": "uploaded_document",
                "retrieved_at": datetime.utcnow().isoformat(),
                "agent": "ocean_document_scan",
            },
            "processing_time_ms": elapsed_ms,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document scan error [{ingestion_id}]: {e}")
        raise HTTPException(status_code=500, detail=f"Document scanning failed: {type(e).__name__}")


# ═══════════════════════════════════════════════════════════════════════════════
# MESSAGE REACTIONS — Real-time Emoji Interactions (2026 Level)
# ═══════════════════════════════════════════════════════════════════════════════

_REACTION_STORE: dict[str, dict[str, list[str]]] = {}  # {message_id: {emoji: [user_ids]}}

@app.post(f"{API_PREFIX}/message/reaction")
async def add_message_reaction(request: Request):
    """
    Add or toggle an emoji reaction to a message.

    Body:
    {
        "message_id": "msg_123",
        "emoji": "👍",
        "user_id": "clerk_user_id_or_anonymous"
    }

    Returns:
    {
        "message_id": "msg_123",
        "emoji": "👍",
        "count": 3,
        "users": ["user1", "user2", "user3"],
        "added": true
    }
    """
    try:
        body = await request.json()
        message_id = str(body.get("message_id", "")).strip()
        emoji = str(body.get("emoji", "")).strip()
        user_id = str(body.get("user_id", "anonymous")).strip()

        if not message_id or not emoji:
            return {"status": "error", "message": "message_id and emoji required"}

        if message_id not in _REACTION_STORE:
            _REACTION_STORE[message_id] = {}

        if emoji not in _REACTION_STORE[message_id]:
            _REACTION_STORE[message_id][emoji] = []

        users = _REACTION_STORE[message_id][emoji]

        # Toggle: remove if already reacted, add if not
        if user_id in users:
            users.remove(user_id)
            added = False
        else:
            users.append(user_id)
            added = True

        # Clean empty reactions
        if not users:
            del _REACTION_STORE[message_id][emoji]
        if not _REACTION_STORE[message_id]:
            del _REACTION_STORE[message_id]

        logger.info(f"💬 Message reaction: {message_id} + {emoji} by {user_id} ({'added' if added else 'removed'})")

        return {
            "status": "success",
            "message_id": message_id,
            "emoji": emoji if (emoji in _REACTION_STORE.get(message_id, {})) else None,
            "count": len(_REACTION_STORE.get(message_id, {}).get(emoji, [])),
            "users": _REACTION_STORE.get(message_id, {}).get(emoji, []),
            "added": added,
        }

    except Exception as e:
        logger.error(f"Reaction endpoint error: {e}")
        return {"status": "error", "message": str(e)}


@app.get(f"{API_PREFIX}/message/{'{message_id}'}/reactions")
async def get_message_reactions(message_id: str):
    """Get all reactions for a message."""
    if message_id not in _REACTION_STORE:
        return {"message_id": message_id, "reactions": {}, "total": 0}

    reactions = {}
    total = 0
    for emoji, users in _REACTION_STORE[message_id].items():
        if users:
            reactions[emoji] = {"count": len(users), "users": users}
            total += len(users)

    return {
        "message_id": message_id,
        "reactions": reactions,
        "total": total,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# DOCUMENT PROCESSING WITH KITCHEN + EXCEL (2026 Level)
# ═══════════════════════════════════════════════════════════════════════════════

@app.post(f"{API_PREFIX}/documents/process-with-excel")
async def process_document_and_create_excel(request: Request):
    """
    Process document via Kitchen, extract tables, generate Excel workbook.

    Full pipeline:
    1. Kitchen processes document (extracts tables, text, structure)
    2. Excel Core creates workbook with extracted data
    3. Returns workbook URL + analysis

    Body:
    {
        "filename": "data.pdf",
        "content_base64": "...",
        "doc_type": "pdf",
        "processing_mode": "full"   # or "extract", "convert", "structure"
    }
    """
    try:
        body = await request.json()
        filename = str(body.get("filename", "document")).strip()
        content_b64 = str(body.get("content_base64", "")).strip()
        doc_type = str(body.get("doc_type", "pdf")).strip().lower()
        proc_mode = str(body.get("processing_mode", "full")).strip()

        if not content_b64:
            return {"status": "error", "message": "content_base64 required"}

        # ─────────────────────────────────────────────────────────────────
        # Step 1: Kitchen processes document
        # ─────────────────────────────────────────────────────────────────
        if not kitchen_process_document:
            return {
                "status": "error",
                "message": "Kitchen integration not available (import failed)"
            }

        kitchen_result = await kitchen_process_document(
            filename=filename,
            content_base64=content_b64,
            doc_type=doc_type,
            processing_mode=proc_mode,
        )

        if kitchen_result.get("status") == "error":
            return kitchen_result

        extracted_text = kitchen_result.get("extracted_text", "")
        tables = kitchen_result.get("tables", [])
        metadata = kitchen_result.get("metadata", {})

        # ─────────────────────────────────────────────────────────────────
        # Step 2: Excel Core creates workbook if tables detected
        # ─────────────────────────────────────────────────────────────────
        excel_workbook = None
        if tables and excel_create_workbook:
            try:
                # Build data from first table
                first_table = tables[0] if isinstance(tables, list) else {}
                table_rows = first_table.get("rows", [])
                table_cols = first_table.get("columns", [])

                if table_rows:
                    excel_result = await excel_create_workbook(
                        title=f"Data from {filename}",
                        data=table_rows,
                        column_names=table_cols,
                    )
                    excel_workbook = excel_result.get("workbook_id")
                    logger.info(f"💾 Excel workbook created: {excel_workbook}")
            except Exception as e:
                logger.warning(f"Excel generation failed (non-blocking): {e}")

        # ─────────────────────────────────────────────────────────────────
        # Return integrated result
        # ─────────────────────────────────────────────────────────────────
        return {
            "status": "success",
            "filename": filename,
            "doc_type": doc_type,
            "extraction": {
                "text": extracted_text[:3000],  # First 3k chars
                "length": len(extracted_text),
                "tables_detected": len(tables),
            },
            "tables": tables[:3],  # First 3 tables
            "excel": {
                "workbook_id": excel_workbook,
                "status": "created" if excel_workbook else "no_tables",
            },
            "metadata": metadata,
            "processing_time_ms": int(time.time() * 1000) % 1000000,
        }

    except Exception as e:
        logger.error(f"Document + Excel processing error: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/api/documents/generate")
@app.post(f"{API_PREFIX}/documents/generate")
async def documents_generate(request: DocumentGenerateRequest):
    """Industrial contract-governed generation via specialized document agents."""
    try:
        try:
            document_agents_module = importlib.import_module("document_agents")
            document_contracts_module = importlib.import_module("document_contracts")
            get_agent = getattr(document_agents_module, "get_agent", None)
            create_cpi_report_contract = getattr(document_contracts_module, "create_cpi_report_contract", None)
            create_research_report_contract = getattr(document_contracts_module, "create_research_report_contract", None)
            VideoContract = getattr(document_contracts_module, "VideoContract", None)
            VoiceContract = getattr(document_contracts_module, "VoiceContract", None)

            if not get_agent:
                raise AttributeError("get_agent function not found")
        except (ImportError, AttributeError) as e:
            logger.warning(f"document_agents or document_contracts module not found: {e}")
            raise HTTPException(status_code=503, detail="Document generation service not available")

        format_map = {
            "xlsx": "excel",
            "csv": "excel",
            "pdf": "pdf",
            "report": "report",
            "mp4": "video",
            "video": "video",
            "wav": "voice",
            "voice": "voice",
            "audio": "voice",
        }

        contract_map = {
            "cpi": create_cpi_report_contract,
            "research": create_research_report_contract,
            "video": lambda: VideoContract() if VideoContract else None,
            "voice": lambda: VoiceContract() if VoiceContract else None,
        }

        agent_name = format_map.get(request.format.lower())
        if not agent_name:
            raise HTTPException(status_code=400, detail="Unsupported format. Use xlsx/csv/pdf/report/video/voice")

        contract_factory = contract_map.get(request.contract_type.lower())
        if not contract_factory:
            raise HTTPException(status_code=400, detail="Unsupported contract_type. Use cpi/research/video/voice")

        agent = get_agent(agent_name)
        if not agent:
            raise HTTPException(status_code=503, detail=f"Agent unavailable: {agent_name}")

        contract = contract_factory()
        if not contract:
            raise HTTPException(status_code=400, detail=f"Cannot create contract: {request.contract_type}")

        result = agent.generate_document(contract=contract, query=request.query, language=request.language)

        document_payload = result.get("document")
        if document_payload is not None and hasattr(document_payload, "to_dict"):
            document_payload = document_payload.to_dict()

        return {
            "success": bool(result.get("success")),
            "validation_status": result.get("validation_status"),
            "errors": result.get("errors", []),
            "document": document_payload,
            "provenance": result.get("provenance"),
            "meta": {
                "agent": agent_name,
                "contract_type": request.contract_type,
                "format": request.format,
                "timestamp": datetime.utcnow().isoformat(),
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Document generation failed: {type(e).__name__}")


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("OCEAN_PORT", 8030))
    logger.info(f"🌊 Starting Curiosity Ocean on port {port}...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
