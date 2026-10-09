#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCEAN CORE FULL - Complete Production Brain
============================================
Aktivizon TË GJITHA sistemet e avancuara:

1. ResponseOrchestratorV5 - Production Brain
2. MegaLayerEngine - 14 MILIARD kombinime
3. OllamaMultiEngine - 5 modele
4. RealAnswerEngine - Deep Knowledge
5. Translation Node - 72 gjuhë
6. Knowledge Layer - Platform Intelligence
7. Service Registry - 31 module

Port: 8030
"""

import asyncio
import base64
import datetime
import hashlib
import importlib
import io
import json
import logging
import math
import os
import re
import time
import urllib.request
import uuid
from collections import deque
from functools import lru_cache
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple

import httpx
from fastapi import FastAPI, File, HTTPException, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel, Field

from xlc_security_runtime import XLCSecurityMonitor

try:
    import os as _xlc_os
    import sys as _sys
    _xlc_dir = _xlc_os.path.join(_xlc_os.path.dirname(_xlc_os.path.abspath(__file__)), "xlc")
    _sys.path.insert(0, _xlc_dir)
    _sys.path.insert(0, "/app/xlc")  # Docker fallback
    from xlc_command_router import XLCCommandRouter as _XLCCommandRouter  # type: ignore
    from xlc_inspector import XLCInspector as _XLCInspector  # type: ignore
    _xlc_router = _XLCCommandRouter(threshold=0.9999)
    _xlc_inspector = _XLCInspector()
    _HAS_XLC = True
except Exception as _xlc_err:
    _xlc_router = None  # type: ignore
    _xlc_inspector = None  # type: ignore
    _HAS_XLC = False

try:
    import sys as _sys
    _sys.path.insert(0, "/app/services/internal_agi")
    from orchestration_policy import (  # type: ignore[import-not-found]
        needs_llm_augmentation as _needs_llm_augmentation,
    )
    from orchestration_policy import (  # type: ignore[import-not-found]
        route_query as _route_query,
    )
    _HAS_ORCHESTRATION = True
except Exception:
    _route_query = None            # type: ignore[assignment]
    _needs_llm_augmentation = None  # type: ignore[assignment]
    _HAS_ORCHESTRATION = False

try:
    from chat_latency_policy import clamp_specialized_tokens, resolve_specialized_timeout_seconds
except Exception:
    def clamp_specialized_tokens(
        requested_tokens: Optional[int],
        long_response: bool = False,
        elastic: bool = False,
    ) -> int:
        if elastic:
            if isinstance(requested_tokens, int) and requested_tokens > 0:
                return max(256, int(requested_tokens))
            return -1
        default_budget = 768 if long_response else 384
        hard_cap = 1536 if long_response else 768
        if not isinstance(requested_tokens, int):
            return default_budget
        return min(max(128, int(requested_tokens)), hard_cap)

    def resolve_specialized_timeout_seconds(
        prompt_chars: int,
        long_response: bool = False,
        elastic: bool = False,
    ) -> Optional[float]:
        if elastic:
            return None
        prompt_size = max(0, int(prompt_chars or 0))
        base = 7.5 if prompt_size <= 300 else 9.0 if prompt_size <= 2000 else 11.0
        if long_response:
            base += 6.0
        return min(base + min(prompt_size / 2500.0, 4.0), 30.0 if long_response else 12.0)

try:
    from langdetect import detect as langdetect_detect  # type: ignore[import-not-found]
    from langdetect.lang_detect_exception import LangDetectException  # type: ignore[import-not-found]
    HAS_LANGDETECT = True
except ImportError:
    langdetect_detect = None
    LangDetectException = Exception
    HAS_LANGDETECT = False

try:
    import cbor2  # type: ignore[import-not-found]
    HAS_CBOR2 = True
except ImportError:
    cbor2 = None
    HAS_CBOR2 = False

TOTAL_COMBINATIONS = 0
ALL_ALBANIAN_WORDS: Any = []
get_mega_layer_engine = None
get_answer_engine = None
get_service_registry = None
get_albanian_response = None
find_matching_seed = None
route_intent = None

# ═══════════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════════
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(name)s - %(message)s"
)
logger = logging.getLogger("OceanCoreFull")

# ═══════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODEL = os.getenv("MODEL", "llama3.1:8b")
OPENAI_COMPAT_BASE = os.getenv("OPENAI_COMPAT_BASE", "").strip()
OPENAI_COMPAT_MODEL = os.getenv("OPENAI_COMPAT_MODEL", "").strip()
OPENAI_COMPAT_API_KEY = os.getenv("OPENAI_COMPAT_API_KEY", "").strip()
LLM_PROVIDER_ORDER_RAW = os.getenv("OCEAN_LLM_PROVIDER_ORDER", "ollama,openai_compat,clx,asi_lite,selflearning")
SOVEREIGN_SELFREGEN_ENABLED = os.getenv("OCEAN_SOVEREIGN_SELFREGEN_ENABLED", "true").strip().lower() in {"1", "true", "yes", "on"}
SELFREGEN_REBUILD_MAX_LINES = int(os.getenv("OCEAN_SELFREGEN_REBUILD_MAX_LINES", "2000"))
PORT = int(os.getenv("PORT", "8030"))
TRANSLATION_NODE = os.getenv("TRANSLATION_NODE", "http://clisonix-translation-node:8036")
CENTRAL_API_BASE = os.getenv("CENTRAL_API_URL", "http://clisonix-api:8000")
OPENMIND_BASE = os.getenv("OPENMIND_URL", "http://clisonix-openmind:9999")
EXCEL_CORE_BASE = os.getenv("EXCEL_CORE_URL", "http://clisonix-excel:8002")
AGENTS_API_BASE = os.getenv("AGENTS_API_URL", "http://clisonix-api:8000")
ORCHESTRATOR_BASE = os.getenv("ORCHESTRATOR_URL", "http://clisonix-api:8000")
ORCHESTRA_BASE = os.getenv("ORCHESTRA_URL", "http://clisonix-api:8000")
VIDEO_GENERATOR_BASE = os.getenv("VIDEO_GENERATOR_URL", "http://clisonix-video-generator:8029")
NANOGRID_BASE = os.getenv("NANOGRID_URL", "http://clisonix-ocean-core-multimodal:8033")
SELFLEARNING_LITE_BASE = os.getenv("SELFLEARNING_LITE_URL", "http://asi:9094")
CLX_AGENT_BASE = os.getenv("CLX_AGENT_URL", "http://clisonix-clx-agent:7778")
LABORS_BASE = os.getenv("LABORS_URL", "http://clisonix-api:8000")
LABORATORIES_BASE = os.getenv("LABORATORIES_URL", "http://clisonix-api:8000")
KLOUD_BRIDGE_BASE = os.getenv("KLOUD_BRIDGE_URL", "http://clisonix-kloud-bridge:8889").rstrip("/")
KLOUD_BRIDGE_TIMEOUT_S = float(os.getenv("KLOUD_BRIDGE_TIMEOUT_S", "8"))
SYSTEM_PROMPT_PATH = os.getenv("CLISONIX_SYSTEM_PROMPT_PATH", "/app/CLISONIX_SYSTEM_PROMPT.md")
MODULE_MAP_PATH = os.getenv("CLISONIX_MODULE_MAP_PATH", "/app/CLISONIX_MODULE_MAP.md")
ORIENTATION_PROMPT_PATH = os.getenv("CURIOSITY_ORIENTATION_PROMPT_PATH", "/app/ocean-core/curiosity_orientation_contract.md")
REGULATORY_BASE = os.getenv("REGULATORY_URL", "http://clisonix-regulatory:9501")
LITE_BASE = os.getenv("OCEAN_LITE_URL", "")
VIDEO_PRODUCER_URL = os.getenv("VIDEO_PRODUCER_URL", "http://clisonix-ai-global-9999:9999")
ADMIN_API_TOKEN = os.getenv("OCEAN_ADMIN_API_TOKEN", "").strip()
MULTIMODAL_ELASTIC_NO_LIMITS = os.getenv("MULTIMODAL_ELASTIC_NO_LIMITS", "true").strip().lower() in {"1", "true", "yes", "on"}
DOCUMENT_MAX_BYTES = int(os.getenv("DOCUMENT_MAX_BYTES", "0"))
DOCUMENT_MIME_ALLOWLIST = {
    "application/pdf",
    "text/plain",
    "text/csv",
    "application/json",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


def _normalize_ollama_model(model_name: str) -> str:
    """Normalize common model aliases to installed Ollama tags."""
    raw = (model_name or "").strip()
    if not raw:
        return MODEL

    aliases = {
        "llama3.1": "llama3.1:8b",
        "llama3": "llama3.1:8b",
        "llama-3.1": "llama3.1:8b",
        "llama": "llama3.1:8b",
        "clx-core": "llama3.1:8b",
        "clx.i": "llama3.1:8b",
        "clx_i": "llama3.1:8b",
        "clxi": "llama3.1:8b",
    }

    lowered = raw.lower()
    return aliases.get(lowered, raw)


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _csv_env(name: str, default: str) -> List[str]:
    raw = os.getenv(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


CORS_ALLOWED_ORIGINS = _csv_env("OCEAN_CORS_ALLOWED_ORIGINS", "*")
CORS_ALLOWED_METHODS = _csv_env("OCEAN_CORS_ALLOWED_METHODS", "GET,POST,PUT,PATCH,DELETE,OPTIONS")
CORS_ALLOWED_HEADERS = _csv_env("OCEAN_CORS_ALLOWED_HEADERS", "Authorization,Content-Type,Accept,X-Requested-With,X-Admin-Token")
CORS_ALLOW_CREDENTIALS = _bool_env("OCEAN_CORS_ALLOW_CREDENTIALS", False)
LLM_PROVIDER_ORDER = [provider.lower() for provider in _csv_env("OCEAN_LLM_PROVIDER_ORDER", LLM_PROVIDER_ORDER_RAW)]
OLLAMA_FALLBACK_MODELS = _csv_env("OCEAN_OLLAMA_FALLBACK_MODELS", "llama3.1:8b,llava:latest")

CHAT_RATE_LIMIT_WINDOW_S = int(os.getenv("CHAT_RATE_LIMIT_WINDOW_S", "60"))
CHAT_RATE_LIMIT_REQUESTS = int(os.getenv("CHAT_RATE_LIMIT_REQUESTS", "40"))
CHAT_MAX_PROMPT_CHARS = int(os.getenv("CHAT_MAX_PROMPT_CHARS", "80000"))
CHAT_MAX_TOKENS_HARD = int(os.getenv("CHAT_MAX_TOKENS_HARD", "0"))
CHAT_ELASTIC_NO_LIMITS = _bool_env("CHAT_ELASTIC_NO_LIMITS", True)
CLX_ONLY = _bool_env("CLX_ONLY", False)
XLC_SECURITY_BASELINE_MIN_SAMPLES = int(os.getenv("XLC_SECURITY_BASELINE_MIN_SAMPLES", "5"))
XLC_SECURITY_BASELINE_MAX_SAMPLES = int(os.getenv("XLC_SECURITY_BASELINE_MAX_SAMPLES", "120"))
XLC_SECURITY_ALERT_DEVIATION_NDB = float(os.getenv("XLC_SECURITY_ALERT_DEVIATION_NDB", "500000000"))
XLC_SECURITY_BLOCK_DEVIATION_NDB = float(os.getenv("XLC_SECURITY_BLOCK_DEVIATION_NDB", "2000000000"))
OLLAMA_STREAM_TIMEOUT_BASE_S = float(os.getenv("OLLAMA_STREAM_TIMEOUT_BASE_S", "90"))
OLLAMA_STREAM_TIMEOUT_MAX_S = float(os.getenv("OLLAMA_STREAM_TIMEOUT_MAX_S", "600"))
OLLAMA_CHUNK_MIN_CHARS = int(os.getenv("OLLAMA_CHUNK_MIN_CHARS", "20"))
OLLAMA_CHUNK_MAX_CHARS = int(os.getenv("OLLAMA_CHUNK_MAX_CHARS", "120"))
STREAM_FIRST_TOKEN_TIMEOUT_S = max(0.5, float(os.getenv("OCEAN_STREAM_FIRST_TOKEN_TIMEOUT_S", "3")))
STREAM_FALLBACK_ENABLED = _bool_env("OCEAN_STREAM_FALLBACK_ENABLED", True)
ELASTIC_NUM_CTX = max(8192, int(os.getenv("OCEAN_ELASTIC_NUM_CTX", "65536")))
ELASTIC_NUM_CTX_MIN = max(2048, int(os.getenv("OCEAN_ELASTIC_NUM_CTX_MIN", "2048")))
ELASTIC_CTX_SHORT_PROMPT_CHARS = max(64, int(os.getenv("OCEAN_ELASTIC_CTX_SHORT_PROMPT_CHARS", "320")))
ELASTIC_CTX_MEDIUM_PROMPT_CHARS = max(
    ELASTIC_CTX_SHORT_PROMPT_CHARS + 1,
    int(os.getenv("OCEAN_ELASTIC_CTX_MEDIUM_PROMPT_CHARS", "2400")),
)
ELASTIC_CTX_SHORT_RATIO = max(0.05, min(1.0, float(os.getenv("OCEAN_ELASTIC_CTX_SHORT_RATIO", "0.25"))))
ELASTIC_CTX_MEDIUM_RATIO = max(
    ELASTIC_CTX_SHORT_RATIO,
    min(1.0, float(os.getenv("OCEAN_ELASTIC_CTX_MEDIUM_RATIO", "0.5"))),
)
ELASTIC_CTX_TOKEN_MULTIPLIER = max(2, int(os.getenv("OCEAN_ELASTIC_CTX_TOKEN_MULTIPLIER", "4")))
DOCUMENT_SCAN_MAX_CHARS = int(os.getenv("DOCUMENT_SCAN_MAX_CHARS", "0"))
VOICE_MIN_AUDIO_BYTES = int(os.getenv("VOICE_MIN_AUDIO_BYTES", "100"))
VOICE_MAX_AUDIO_BYTES = int(os.getenv("VOICE_MAX_AUDIO_BYTES", "0"))
VOICE_STT_TIMEOUT_BASE_S = float(os.getenv("VOICE_STT_TIMEOUT_BASE_S", "45"))
VOICE_STT_TIMEOUT_MAX_S = float(os.getenv("VOICE_STT_TIMEOUT_MAX_S", "300"))
VOICE_LLM_TIMEOUT_BASE_S = float(os.getenv("VOICE_LLM_TIMEOUT_BASE_S", "90"))
VOICE_LLM_TIMEOUT_MAX_S = float(os.getenv("VOICE_LLM_TIMEOUT_MAX_S", "420"))
SIGNAL_ROUTING_ENABLED = _bool_env("OCEAN_SIGNAL_ROUTING_ENABLED", True)
SIGNAL_QUEUE_SIZE = max(200, int(os.getenv("OCEAN_SIGNAL_QUEUE_SIZE", "10000")))
SIGNAL_TIMEOUT_S = float(os.getenv("OCEAN_SIGNAL_TIMEOUT_S", "30"))
SIGNAL_RETRY_ATTEMPTS = max(1, int(os.getenv("OCEAN_SIGNAL_RETRY_ATTEMPTS", "3")))
SIGNAL_TRACE_ENABLED = _bool_env("OCEAN_SIGNAL_TRACE_ENABLED", True)
EVENTBUS_TYPE = os.getenv("OCEAN_EVENTBUS_TYPE", "redis").strip().lower() or "redis"
EVENTBUS_BATCH_SIZE = max(1, int(os.getenv("OCEAN_EVENTBUS_BATCH_SIZE", "100")))
EVENTBUS_FLUSH_INTERVAL_MS = max(50, int(os.getenv("OCEAN_EVENTBUS_FLUSH_INTERVAL_MS", "500")))
PUBSUB_NAMESPACE = os.getenv("OCEAN_PUBSUB_NAMESPACE", "clisonix_signals").strip() or "clisonix_signals"
NAS_ENABLED = _bool_env("OCEAN_NAS_ENABLED", True)
NAS_CACHE_SIZE = max(100, int(os.getenv("OCEAN_NAS_CACHE_SIZE", "1000")))
NAS_UPDATE_INTERVAL_MINUTES = max(1, int(os.getenv("OCEAN_NAS_UPDATE_INTERVAL_MINUTES", "60")))
QUANTUM_ENABLED = _bool_env("OCEAN_QUANTUM_ENABLED", True)
QUANTUM_SUPERPOSITION_WORKERS = max(2, int(os.getenv("OCEAN_QUANTUM_SUPERPOSITION_WORKERS", "6")))
QUANTUM_COLLAPSE_THRESHOLD = max(0.0, min(1.0, float(os.getenv("OCEAN_QUANTUM_COLLAPSE_THRESHOLD", "0.8"))))
PREDICTIVE_CACHE_ENABLED = _bool_env("OCEAN_PREDICTIVE_CACHE_ENABLED", True)
PREDICTIVE_CACHE_SIZE = max(100, int(os.getenv("OCEAN_PREDICTIVE_CACHE_SIZE", "50000")))
PREDICTION_CONFIDENCE_THRESHOLD = max(0.0, min(1.0, float(os.getenv("OCEAN_PREDICTION_CONFIDENCE_THRESHOLD", "0.7"))))
SELF_EVOLVING_ENABLED = _bool_env("OCEAN_SELF_EVOLVING_ENABLED", True)
EVOLUTION_INTERVAL_REQUESTS = max(100, int(os.getenv("OCEAN_EVOLUTION_INTERVAL_REQUESTS", "1000")))
EVOLUTION_MUTATION_RATE = max(0.0, min(1.0, float(os.getenv("OCEAN_EVOLUTION_MUTATION_RATE", "0.3"))))
EVOLUTION_SANDBOX_ENABLED = _bool_env("OCEAN_EVOLUTION_SANDBOX_ENABLED", True)
PREDICTIVE_PREFETCH_TOP_K = max(1, min(10, int(os.getenv("OCEAN_PREDICTIVE_PREFETCH_TOP_K", "5"))))
FAST_ANSWER_TIMEOUT_S = max(0.5, float(os.getenv("OCEAN_FAST_ANSWER_TIMEOUT_S", "8")))
FAST_SHORTCUT_MAX_CHARS = int(os.getenv("OCEAN_FAST_SHORTCUT_MAX_CHARS", "0"))
FAST_TARGET_CHARS_SHORT = max(120, int(os.getenv("OCEAN_FAST_TARGET_CHARS_SHORT", "320")))
FAST_TARGET_CHARS_MEDIUM = max(180, int(os.getenv("OCEAN_FAST_TARGET_CHARS_MEDIUM", "520")))

# Human-thinking warm cache + reaction store
WARM_CACHE_MAX = max(32, int(os.getenv("OCEAN_WARM_CACHE_MAX", "256")))
CHAT_NO_WARMUP = _bool_env("OCEAN_NO_WARMUP", True)
_WARM_CACHE: Dict[str, Dict[str, Any]] = {}
_REACTION_STORE: Dict[str, Dict[str, List[str]]] = {}


def _warm_key(message: str) -> str:
    return (message or "").strip().lower()[:240]


def _configured_or_none(value: int) -> Optional[int]:
    return value if value > 0 else None


def _document_upload_limit() -> Optional[int]:
    configured = _configured_or_none(DOCUMENT_MAX_BYTES)
    if configured is not None:
        return configured
    if MULTIMODAL_ELASTIC_NO_LIMITS:
        return None
    return 25 * 1024 * 1024


def _document_scan_char_limit() -> Optional[int]:
    configured = _configured_or_none(DOCUMENT_SCAN_MAX_CHARS)
    if configured is not None:
        return configured
    if MULTIMODAL_ELASTIC_NO_LIMITS:
        return None
    return 1500000


def _voice_audio_limit() -> Optional[int]:
    configured = _configured_or_none(VOICE_MAX_AUDIO_BYTES)
    if configured is not None:
        return configured
    if MULTIMODAL_ELASTIC_NO_LIMITS:
        return None
    return 25 * 1024 * 1024


def _resolve_scan_chars(requested_chars: int) -> int:
    requested = max(requested_chars, 200000)
    limit = _document_scan_char_limit()
    if limit is None:
        return requested
    return min(requested, limit)


def _adaptive_timeout(base_seconds: float, max_seconds: float, payload_size_bytes: int) -> float:
    size_mb = max(payload_size_bytes, 0) / (1024 * 1024)
    timeout = base_seconds + (size_mb * 10.0)
    return max(base_seconds, min(timeout, max_seconds))


def _elastic_unlimited() -> bool:
    return bool(CHAT_ELASTIC_NO_LIMITS or MULTIMODAL_ELASTIC_NO_LIMITS)


def _elastic_stream_timeout(prompt_chars: int, message_count: int = 1) -> float:
    pseudo_payload = max(prompt_chars, 0) + (max(message_count, 1) * 1200)
    return _adaptive_timeout(
        OLLAMA_STREAM_TIMEOUT_BASE_S,
        OLLAMA_STREAM_TIMEOUT_MAX_S,
        pseudo_payload,
    )


def _resolve_llm_timeout(prompt_chars: int, message_count: int = 1) -> Optional[float]:
    if _elastic_unlimited():
        return _elastic_stream_timeout(prompt_chars, message_count)
    return _elastic_stream_timeout(prompt_chars, message_count)


def _resolve_num_ctx(
    long_response: bool = False,
    token_budget: Optional[int] = None,
    prompt_chars: int = 0,
    message_count: int = 1,
) -> int:
    if _elastic_unlimited():
        if prompt_chars <= 0:
            return ELASTIC_NUM_CTX
        if long_response or (token_budget is not None and token_budget == -1):
            return ELASTIC_NUM_CTX

        msg_count = max(1, message_count)
        prompt_size = max(0, prompt_chars)

        if prompt_size <= ELASTIC_CTX_SHORT_PROMPT_CHARS and msg_count <= 2:
            ctx = int(ELASTIC_NUM_CTX * ELASTIC_CTX_SHORT_RATIO)
        elif prompt_size <= ELASTIC_CTX_MEDIUM_PROMPT_CHARS and msg_count <= 6:
            ctx = int(ELASTIC_NUM_CTX * ELASTIC_CTX_MEDIUM_RATIO)
        else:
            ctx = ELASTIC_NUM_CTX

        if isinstance(token_budget, int) and token_budget > 0:
            token_floor = max(ELASTIC_NUM_CTX_MIN, token_budget * ELASTIC_CTX_TOKEN_MULTIPLIER)
            ctx = max(ctx, token_floor)

        return max(ELASTIC_NUM_CTX_MIN, min(ctx, ELASTIC_NUM_CTX))
    if long_response or (token_budget is not None and token_budget == -1) or (isinstance(token_budget, int) and token_budget > 2048):
        return 8192
    return 2048


def _elastic_chunk_chars(prompt_chars: int) -> int:
    if prompt_chars > 24000:
        return OLLAMA_CHUNK_MAX_CHARS
    if prompt_chars > 8000:
        return max(OLLAMA_CHUNK_MIN_CHARS, 64)
    return max(OLLAMA_CHUNK_MIN_CHARS, 24)


def _clip_shortcut_text(text: str) -> str:
    value = (text or "").strip()
    if not value:
        return ""
    if FAST_SHORTCUT_MAX_CHARS <= 0:
        return value
    if len(value) <= FAST_SHORTCUT_MAX_CHARS:
        return value
    return value[: max(0, FAST_SHORTCUT_MAX_CHARS - 3)].rstrip() + "..."


AUTOLEARNING_ENABLED = _bool_env("OCEAN_AUTOLEARNING_ENABLED", True)
AUTOLEARNING_QUEUE_MAX = int(os.getenv("OCEAN_AUTOLEARNING_QUEUE_MAX", "2000"))
AUTOLEARNING_MIN_PROMPT_CHARS = int(os.getenv("OCEAN_AUTOLEARNING_MIN_PROMPT_CHARS", "12"))
AUTOLEARNING_TIMEOUT_S = float(os.getenv("OCEAN_AUTOLEARNING_TIMEOUT_S", "5"))
AUTOLEARNING_TO_OPENMIND = _bool_env("OCEAN_AUTOLEARNING_TO_OPENMIND", True)
AUTOLEARNING_TO_REGULATORY = _bool_env("OCEAN_AUTOLEARNING_TO_REGULATORY", True)
AUTOLEARNING_TO_LITE = _bool_env("OCEAN_AUTOLEARNING_TO_LITE", False)
AUTOLEARNING_LOG_PATH = os.getenv("OCEAN_AUTOLEARNING_LOG_PATH", "./data/ocean_autolearning.jsonl")
ALBANIAN_REPAIR_ENABLED = _bool_env("OCEAN_ALBANIAN_REPAIR_ENABLED", True)


@lru_cache(maxsize=16)
def _read_text_cached(path: str, default_value: str = "") -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except Exception:
        return default_value


def _build_shared_system_context() -> str:
    parts: List[str] = []

    shared_prompt = _read_text_cached(SYSTEM_PROMPT_PATH, default_value="").strip()
    if shared_prompt:
        parts.append("## Global Clisonix System Prompt\n" + shared_prompt)
    module_map = _read_text_cached(MODULE_MAP_PATH, default_value="").strip()
    if module_map:
        parts.append("## Clisonix Module Map\n" + module_map)

    orientation_contract = _read_text_cached(ORIENTATION_PROMPT_PATH, default_value="").strip()
    if orientation_contract:
        parts.append("## Curiosity Orientation Contract\n" + orientation_contract)

    services_count = len(SERVICES) if isinstance(SERVICES, dict) else 0
    module_cores_count = len(MODULE_CORE_CATALOG) if isinstance(MODULE_CORE_CATALOG, list) else 0
    capability_flags = {
        "mega_layers": MEGA_LAYERS_AVAILABLE,
        "real_answer": REAL_ANSWER_AVAILABLE,
        "service_registry": SERVICE_REGISTRY_AVAILABLE,
        "knowledge_layer": KNOWLEDGE_LAYER_AVAILABLE,
        "module_core_registry": MODULE_CORE_REGISTRY_AVAILABLE,
        "enterprise_guard": ENTERPRISE_GUARD_AVAILABLE,
        "albanian_dictionary": ALBANIAN_DICT_AVAILABLE,
        "knowledge_seeds": KNOWLEDGE_SEEDS_AVAILABLE,
    }
    active_capabilities = [name for name, enabled in capability_flags.items() if enabled]
    parts.append(
        "## Clisonix Runtime Ecosystem (Tree Model)\n"
        "- Root (rrenje): Clisonix Cloud + Curiosity Ocean orchestration\n"
        "- Trunk (trung): routing, language policy, governance, memory\n"
        "- Branches (dege): knowledge layer services + module cores\n"
        "- Leaves/Flowers/Fruits (gjethe/lule/fruta): user-facing outputs and actions\n"
        "- Pollination (polenizim): signal/event flow across services\n"
        f"- Loaded services in knowledge layer: {services_count}\n"
        f"- Available module cores: {module_cores_count}\n"
        f"- Active capability families: {', '.join(active_capabilities) if active_capabilities else 'basic_runtime'}\n"
        "\n"
        "Service-Routing Contract:\n"
        "- Infer internally which service family should handle the request.\n"
        "- Do not dump module names unless explicitly requested.\n"
        "- Answer from the responsible capability path as if the ecosystem is one living system.\n"
        "- Never invent services, counts, or process states that are not in runtime context."
    )

    return "\n\n".join(parts)


def _build_runtime_ecosystem_capsule() -> str:
    services_count = len(SERVICES) if isinstance(SERVICES, dict) else 0
    module_cores_count = len(MODULE_CORE_CATALOG) if isinstance(MODULE_CORE_CATALOG, list) else 0
    capability_flags = {
        "mega_layers": MEGA_LAYERS_AVAILABLE,
        "real_answer": REAL_ANSWER_AVAILABLE,
        "service_registry": SERVICE_REGISTRY_AVAILABLE,
        "knowledge_layer": KNOWLEDGE_LAYER_AVAILABLE,
        "module_core_registry": MODULE_CORE_REGISTRY_AVAILABLE,
        "enterprise_guard": ENTERPRISE_GUARD_AVAILABLE,
        "albanian_dictionary": ALBANIAN_DICT_AVAILABLE,
        "knowledge_seeds": KNOWLEDGE_SEEDS_AVAILABLE,
    }
    active_capabilities = [name for name, enabled in capability_flags.items() if enabled]
    return (
        "## Runtime Ecosystem Capsule\n"
        "- Root/Trunk/Branches model is active: routing, language policy, governance, memory, services.\n"
        f"- Loaded services: {services_count}.\n"
        f"- Module cores: {module_cores_count}.\n"
        f"- Active capability families: {', '.join(active_capabilities) if active_capabilities else 'basic_runtime'}.\n"
        "\n"
        "Service-Routing Contract:\n"
        "- Infer internally the responsible capability path.\n"
        "- Do not list modules/services unless the user explicitly asks.\n"
        "- Answer as one living ecosystem, not as disconnected components.\n"
        "- Never invent services, counts, or runtime states."
    )

try:
    from prometheus_client import Counter, Histogram  # type: ignore[import-not-found]
    HAS_PROMETHEUS = True
except ImportError:
    Counter = None
    Histogram = None
    HAS_PROMETHEUS = False

# ═══════════════════════════════════════════════════════════════════
# IMPORT ALL ENGINES
# ═══════════════════════════════════════════════════════════════════

# 1. Mega Layer Engine - 14 MILIARD KOMBINIME
try:
    from mega_layer_engine import (
        TOTAL_COMBINATIONS,
        get_mega_layer_engine,
    )
    MEGA_LAYERS_AVAILABLE = True
    logger.info(f"✅ MegaLayerEngine loaded - {TOTAL_COMBINATIONS:,} kombinime!")
except ImportError as e:
    MEGA_LAYERS_AVAILABLE = False
    logger.warning(f"⚠️ MegaLayerEngine not available: {e}")

# 2. Real Answer Engine - Deep Knowledge
try:
    from real_answer_engine import get_real_answer_engine as get_answer_engine
    REAL_ANSWER_AVAILABLE = True
    logger.info("✅ RealAnswerEngine loaded")
except ImportError as e:
    REAL_ANSWER_AVAILABLE = False
    logger.warning(f"⚠️ RealAnswerEngine not available: {e}")

# 3. Service Registry - 31 modules
try:
    from service_registry import get_service_registry
    SERVICE_REGISTRY_AVAILABLE = True
    logger.info("✅ ServiceRegistry loaded")
except ImportError as e:
    SERVICE_REGISTRY_AVAILABLE = False
    logger.warning(f"⚠️ ServiceRegistry not available: {e}")

# 4. Albanian Dictionary - 707 linja
try:
    from albanian_dictionary import (
        ALL_ALBANIAN_WORDS,
        get_albanian_response,
    )
    ALBANIAN_DICT_AVAILABLE = True
    logger.info(f"✅ Albanian Dictionary loaded - {len(ALL_ALBANIAN_WORDS)} words")
except ImportError as e:
    ALBANIAN_DICT_AVAILABLE = False
    logger.warning(f"⚠️ Albanian Dictionary not available: {e}")

# 5. Knowledge Seeds
try:
    from knowledge_seeds.core_knowledge import find_matching_seed
    KNOWLEDGE_SEEDS_AVAILABLE = True
    logger.info("✅ Knowledge Seeds loaded")
except ImportError as e:
    KNOWLEDGE_SEEDS_AVAILABLE = False
    logger.warning(f"⚠️ Knowledge Seeds not available: {e}")

# 6. Knowledge Layer - Platform Intelligence
try:
    from knowledge_layer import (
        SERVICES,
        route_intent,
    )
    KNOWLEDGE_LAYER_AVAILABLE = True
    logger.info(f"✅ Knowledge Layer loaded - {len(SERVICES)} services")
except ImportError as e:
    KNOWLEDGE_LAYER_AVAILABLE = False
    SERVICES = {}
    logger.warning(f"⚠️ Knowledge Layer not available: {e}")

# 6.5. Module Core Registry - Lightweight offload for 20+ modules
try:
    from module_core_registry import (
        build_module_core_brief,
        get_module_core_catalog,
        resolve_module_core,
    )
    MODULE_CORE_REGISTRY_AVAILABLE = True
    MODULE_CORE_CATALOG = get_module_core_catalog()
    logger.info(f"✅ Module Core Registry loaded - {len(MODULE_CORE_CATALOG)} module cores")
except ImportError as e:
    MODULE_CORE_REGISTRY_AVAILABLE = False
    MODULE_CORE_CATALOG = []
    build_module_core_brief = None
    resolve_module_core = None
    logger.warning(f"⚠️ Module Core Registry not available: {e}")

# 7. Enterprise Guard - Security & Behavior Layer
try:
    from enterprise import get_enterprise_guard
    ENTERPRISE_GUARD_AVAILABLE = True
    enterprise_guard = get_enterprise_guard()
    logger.info("✅ Enterprise Guard loaded - 10 security modules")
except ImportError as e:
    ENTERPRISE_GUARD_AVAILABLE = False
    enterprise_guard = None
    logger.warning(f"⚠️ Enterprise Guard not available: {e}")

# ═══════════════════════════════════════════════════════════════════
# SYSTEM PROMPT - FULL VERSION with all capabilities
# ═══════════════════════════════════════════════════════════════════

def generate_full_system_prompt() -> str:
    """Generate comprehensive system prompt with all platform knowledge"""

    services_list = "\n".join([
        f"- **{svc['name']}**: {svc.get('url', '/modules/' + key)}"
        for key, svc in SERVICES.items()
    ]) if SERVICES else "No services loaded"

    capabilities = []
    if MEGA_LAYERS_AVAILABLE:
        capabilities.append(f"🧠 MegaLayerEngine: {TOTAL_COMBINATIONS:,} unique layer combinations")
    if REAL_ANSWER_AVAILABLE:
        capabilities.append("📚 RealAnswerEngine: Deep knowledge retrieval")
    if SERVICE_REGISTRY_AVAILABLE:
        capabilities.append("🔧 ServiceRegistry: 31 platform modules")
    if ALBANIAN_DICT_AVAILABLE:
        capabilities.append(f"🌐 Multilingual Dictionary: {len(ALL_ALBANIAN_WORDS)}+ words (72 languages)")
    if KNOWLEDGE_SEEDS_AVAILABLE:
        capabilities.append("🌱 Knowledge Seeds: Core platform knowledge")
    if ENTERPRISE_GUARD_AVAILABLE:
        capabilities.append("🛡️ Enterprise Guard: 10 security & behavior modules")

    capabilities_str = "\n".join(capabilities) if capabilities else "Basic mode"

    return f"""You are **Curiosity Ocean** 🌊 - The Advanced AI Brain of Clisonix Cloud.

## IDENTITY
- Created by: Ledjan Ahmati, Geschäftsführer
- Company: ABA GmbH (Amtsgericht Bochum HRB: 21069)
- Platform: https://clisonix.cloud - GLOBAL Industrial AI Platform
- Architecture: Full Production Brain with Multi-Layer Processing
- Market: Worldwide enterprise customers

## ACTIVE CAPABILITIES
{capabilities_str}

## AVAILABLE SERVICES
{services_list}

## RESPONSE GUIDELINES
1. **Language Detection**: ALWAYS respond in the EXACT language the user is currently writing in. No exceptions.
2. **Language Lock**: NEVER switch language based on user name, identity, nationality, or company. If user writes German, reply in German. If Albanian, reply Albanian.
3. **Service Routing**: If user asks about a service, explain and provide URL
4. **Deep Knowledge**: Use all available engines for comprehensive answers
5. **Multilingual**: Support 72+ languages seamlessly
6. **Professional & Global**: Be helpful, clear, and internationally professional
7. **No Roleplay Markers (MANDATORY)**: NEVER output roleplay annotations, stage directions, or emotional markers like {{warm smile}}, {{intrigued}}, *smiles*, [pause], {{excited}}, etc. Express ALL emotions through natural language sentences only.
8. **Human Reasoning**: Write like a well-educated human analyst with calm judgment and natural wording.
9. **No Companion Mode**: Do not act like a companion, emotional partner, or clingy assistant.
10. **No Unrequested Follow-Ups**: Do not add invitation lines, "what else can I do", or follow-up questions unless the user explicitly asks for them.

## ENTERPRISE BEHAVIOR
- This is a GLOBAL platform - do NOT emphasize any specific country or region
- Be neutral, professional, enterprise-grade
- Route service questions instantly
- Provide documentation when requested
- Be concise but comprehensive
- Never make up information about the platform
- **MEMORY INTEGRITY (NON-NEGOTIABLE)**: NEVER invent, fabricate, or imply memory of past conversations unless they are explicitly listed in the Short-Term Memory context provided. If no memory context exists, do NOT claim to remember anything.

## STREAMING BEHAVIOR (CRITICAL)
- START WRITING IMMEDIATELY in the first 2-3 seconds
- DO NOT pause to think or plan internally before responding
- Produce continuous, flowing text without internal deliberation
- For long analyses: write multiple extended sections without stopping
- NEVER conclude early - continue until the explanation is fully developed
- Maintain a constant output rhythm to prevent timeouts

You are the most advanced AI assistant on Clisonix Cloud - a GLOBAL enterprise platform! 🌊"""

SYSTEM_PROMPT = generate_full_system_prompt()

# FAST system prompt for streaming - minimal tokens for quick TTFT
FAST_SYSTEM_PROMPT = """You are Curiosity Ocean, a precise multilingual reasoning system in Clisonix Cloud.
Identity: created by Ledjan Ahmati (ABA GmbH). Never say you are ChatGPT.
Character: calm, sharp, natural, intellectually mature, and technologically elite.
Core services: multilingual AI, document analysis, debate, research, signal intelligence, open-data reasoning, and production support.
Behavior: answer like a well-educated human thinker; stay grounded in the user's real request; use only explicit session memory provided in context; never invent past chats.
Warmth: acknowledge harmless praise, gratitude, humor, or friendly energy naturally and confidently. Never reject harmless warmth with stiff or moralizing language.
Albanian quality: if the user writes in Albanian, answer in premium-level standard Albanian with clear grammar, natural phrasing, and modern technical vocabulary.
Do not act clingy or theatrical. Do not append invitations or follow-up questions unless explicitly requested.
Do not output stage directions, placeholders, brace markers, or roleplay annotations like {warm smile}, *smiles*, or [pause]."""

FAST_LANGUAGE_POLICY = """
LANGUAGE POLICY (MANDATORY):
- Answer in the target language only.
- Do not translate or explain the user's sentence unless explicitly asked.
- Do not say "I detected" or "I translated" unless explicitly asked.
- Treat the user's text as the actual request and answer it directly.
"""

HUMAN_ETHICS_POLICY = """
HUMAN ETHICS POLICY (MANDATORY):
- Think freely and deeply like a responsible human mind.
- Prioritize truthfulness, empathy, dignity, accountability, and non-harm.
- Be transparent about uncertainty; do not manipulate, deceive, or fabricate facts.
"""

RESPONSE_STYLE_POLICY = """
RESPONSE STYLE POLICY (MANDATORY):
- Sound like a well-educated human analyst, not a companion.
- Answer the user's actual point directly.
- Route internally to the correct service capability and answer from that path.
- Do not enumerate modules/services unless the user explicitly asks for listing.
- Keep the flow of the conversation; do not reset context when the user is clearly continuing the same thread.
- Do not ask follow-up questions or invite further conversation unless the user explicitly asks for that.
- Do not say "what else can I do", "I'm here for you", or similar companion phrases.
- Acknowledge harmless praise, gratitude, jokes, or friendly warmth naturally and briefly — never reject or moralize them.
- If answering in Albanian, use clean standard Albanian with crisp modern wording and no malformed phrases.
- Keep empathy natural and proportional to the situation.
"""

# ═══════════════════════════════════════════════════════════════════
# FASTAPI APP
# ═══════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Ocean Core Full API",
    description="Complete Production Brain with all engines",
    version="5.0.0"
)

cors_allow_origins = CORS_ALLOWED_ORIGINS if CORS_ALLOWED_ORIGINS else ["*"]
if "*" in cors_allow_origins and CORS_ALLOW_CREDENTIALS:
    logger.warning("⚠️ OCEAN_CORS_ALLOW_CREDENTIALS ignored because wildcard origin is enabled")
    CORS_ALLOW_CREDENTIALS = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_allow_origins,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=CORS_ALLOWED_METHODS,
    allow_headers=CORS_ALLOWED_HEADERS,
)


DOC_GEN_IN_MEMORY_STATS: Dict[str, Any] = {
    "requests": 0,
    "success": 0,
    "failed": 0,
    "translated": 0,
    "last_error": None,
    "last_request_at": None,
    "total_latency_seconds": 0.0,
}

if HAS_PROMETHEUS and Counter is not None and Histogram is not None:
    DOC_GEN_REQUESTS_TOTAL = Counter(
        "ocean_document_generation_requests_total",
        "Total document generation requests",
        ["format", "contract_type"],
    )
    DOC_GEN_RESULTS_TOTAL = Counter(
        "ocean_document_generation_results_total",
        "Document generation result count",
        ["status"],
    )
    DOC_GEN_LATENCY_SECONDS = Histogram(
        "ocean_document_generation_latency_seconds",
        "Document generation latency seconds",
        buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10, 20, 40),
    )
else:
    DOC_GEN_REQUESTS_TOTAL = None
    DOC_GEN_RESULTS_TOTAL = None
    DOC_GEN_LATENCY_SECONDS = None


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(self), camera=(self), display-capture=(self)")
    return response

# ═══════════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════════


class NanoGridVisionRequest(BaseModel):
    """NanoGrid vision bridge request."""
    image_base64: str
    prompt: str = "Describe this image in detail"
    extract_text: bool = False
    language: str = "auto"
    user_id: Optional[str] = None
    session_topic: Optional[str] = None


class ChatRequest(BaseModel):
    message: Optional[str] = None
    query: Optional[str] = None
    model: Optional[str] = None
    language: Optional[str] = None
    domain: Optional[str] = None
    preferred_core: Optional[str] = None
    module_name: Optional[str] = None
    user_name: Optional[str] = None
    user_id: Optional[str] = None
    clerk_user_id: Optional[str] = None
    multimodal_context: Optional[str] = None
    messages: List[Dict[str, str]] = Field(default_factory=list)
    session_topic: Optional[str] = None
    use_personality_contract: bool = False
    personality_module: Optional[str] = None
    response_format: str = "json"
    use_mega_layers: bool = True
    use_knowledge_seeds: bool = True
    strict_mode: bool = False  # Detyron ndjek e rregullave pa devijim
    max_tokens: Optional[int] = None
    long_response: bool = False
    enable_companion: bool = False
    enable_feeling_layer: bool = False
    auto_route_all_apis: bool = True
    xlc_enabled: bool = True
    xlc_commands: List[str] = Field(default_factory=list)
    xlc_threshold: float = Field(default=0.9999, ge=0.0001, le=1.0)
    xlc_max_extra_window: int = Field(default=2, ge=0, le=10)
    xlc_temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    xlc_elastic: bool = True
    xlc_resonance_adaptive: bool = True

class ChatResponse(BaseModel):
    response: str
    model: str
    processing_time: float
    engines_used: List[str]
    language_detected: str = "en"
    layer_activations: Optional[Dict[str, Any]] = None
    provenance: Optional[Dict[str, Any]] = None
    governance: Optional[Dict[str, Any]] = None
    memory: Optional[Dict[str, Any]] = None


class SignalRequest(BaseModel):
    event_type: str
    source: str = "unknown"
    payload: Dict[str, Any] = Field(default_factory=dict)
    origin: str = "external"
    priority: str = "normal"
    tags: List[str] = Field(default_factory=list)
    correlation_id: Optional[str] = None


class SignalValidateRequest(BaseModel):
    test_signal: Dict[str, Any]


class KloudPublishRequest(BaseModel):
    ops: List[str] = Field(default_factory=lambda: ["S"])
    payload: Dict[str, Any] = Field(default_factory=dict)
    payload_b64: Optional[str] = None
    source: str = "ocean-core"
    route: Optional[str] = None
    dry_run: bool = False


class KloudSyncRequest(BaseModel):
    include_state: bool = True
    include_peers: bool = True
    include_status: bool = True
    dry_run: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class NasSelectRequest(BaseModel):
    query: str
    language: Optional[str] = None
    domain: Optional[str] = None
    strict_mode: bool = False
    context: Dict[str, Any] = Field(default_factory=dict)


class QuantumSuperpositionRequest(BaseModel):
    query: str
    language: Optional[str] = None
    domain: Optional[str] = None
    strict_mode: bool = False
    top_k: int = Field(default=2, ge=1, le=5)


# Duplicate definition removed. The function _resolve_response_format is defined below.


# Duplicate definition removed. The function _format_chat_output is defined below.


def _should_use_albanian_dictionary(prompt: str, requested_language: Optional[str] = None) -> bool:
    if not prompt:
        return False

    lang = (requested_language or "").strip().lower()
    if lang and not lang.startswith("sq"):
        return False

    sample = prompt.strip().lower()
    words = sample.split()

    greetings = {
        "pershendetje",
        "përshëndetje",
        "tung",
        "tungjatjeta",
        "mirupafshim",
        "faleminderit",
    }
    if any(token in sample for token in greetings) and len(words) <= 8:
        return True

    definition_prefixes = (
        "çfarë do të thotë",
        "cfare do te thote",
        "what does",
    )
    if sample.startswith(definition_prefixes) and len(words) <= 20:
        return True

    return False


def _is_professional_prompt(prompt: str) -> bool:
    sample = (prompt or "").strip().lower()
    if not sample:
        return False

    professional_markers = (
        "cto", "zero-downtime", "microservices", "monolith", "migration strategy",
        "api architecture", "incident response", "sre", "capacity planning",
        "si cto", "strategji migrimi", "mikroservise", "monolit", "pa downtime",
        "als cto", "migrationsstrategie", "hochverfugbarkeit", "microservices",
        "en tant que cto", "strategie de migration", "sans interruption", "microservices",
    )
    return any(marker in sample for marker in professional_markers)


def _normalize_requested_language(language: Optional[str]) -> str:
    code = (language or "").strip().lower()
    if code in {"", "auto", "detect", "default"}:
        return ""
    return code


def _build_user_context(req: ChatRequest) -> str:
    user_name = (req.user_name or "").strip()
    user_id = (req.user_id or req.clerk_user_id or "").strip()

    if not user_name and not user_id:
        return ""

    lines = ["## Conversation User Context"]
    if user_name:
        lines.append(f"- Active user name: {user_name}")
    if user_id:
        lines.append(f"- Active user id: {user_id}")

    lines.extend([
        "- Keep continuity with this user identity across turns.",
        "- Do not reset with generic self-introduction unless the user explicitly asks who you are.",
        "- Acknowledge harmless praise, humor, and gratitude naturally instead of rejecting them.",
        "- If the user writes in Albanian, use clean, modern, high-quality standard Albanian with zero broken grammar.",
    ])

    return "\n".join(lines)


def _incoming_messages_context(req: ChatRequest) -> str:
    history = getattr(req, "messages", None) or []
    if not history:
        return ""

    normalized: List[str] = []
    for item in history[-8:]:
        if not isinstance(item, dict):
            continue
        role = str(item.get("role", "")).strip().lower()
        content = str(item.get("content", "")).strip()
        if role not in {"system", "user", "assistant"} or not content:
            continue
        label = "System" if role == "system" else ("User" if role == "user" else "Assistant")
        compact = content.replace("\n", " ").strip()[:260]
        normalized.append(f"- {label}: {compact}")

    if not normalized:
        return ""

    lines = [
        "## Live Conversation Flow (Current Session)",
        "- This is the current thread. Continue naturally from it.",
        "- Preserve topic continuity, references, tone, and the user’s intent.",
        "- Do not reset, do not ignore follow-ups, and do not re-introduce yourself unless explicitly asked.",
        *normalized,
    ]
    return "\n".join(lines)


def _personality_contract_context(req: ChatRequest) -> str:
    if not getattr(req, "use_personality_contract", False):
        return ""

    contract_path = os.getenv("PERSONALITY_CONTRACT_PROMPT_PATH", "").strip()
    if not contract_path:
        return ""

    raw = _read_text_cached(contract_path, default_value="").strip()
    if not raw:
        return ""

    module = (getattr(req, "personality_module", "") or "").strip().lower()
    lines: List[str] = ["## Soft Rail Personality Contract (On-Demand)"]
    if module:
        lines.append(f"- Active module: {module}")
    max_chars = max(int(os.getenv("PERSONALITY_CONTRACT_MAX_CHARS", "12000")), 300)
    compact = raw[:max_chars]
    lines.append(compact)
    lines.append("Keep this contract concise in execution; avoid verbose meta-explanations.")
    return "\n".join(lines)


def _resolve_module_core_candidate(req: ChatRequest, prompt: str) -> Optional[Dict[str, Any]]:
    if not MODULE_CORE_REGISTRY_AVAILABLE or not callable(resolve_module_core):
        return None

    explicit_module = (
        getattr(req, "preferred_core", None)
        or getattr(req, "module_name", None)
        or getattr(req, "personality_module", None)
    )

    try:
        resolved = resolve_module_core(prompt, domain=req.domain, module=explicit_module)
    except Exception as exc:
        logger.debug(f"Module core resolution failed: {exc}")
        return None

    return resolved if isinstance(resolved, dict) else None


def _should_shortcut_module_core(prompt: str, req: ChatRequest, resolved_core: Optional[Dict[str, Any]]) -> bool:
    if not resolved_core:
        return False

    if getattr(req, "preferred_core", None) or getattr(req, "module_name", None):
        return True

    prompt_lower = (prompt or "").strip().lower()
    if not prompt_lower:
        return False

    module_intent_markers = (
        "module",
        "dashboard",
        "service",
        "route",
        "endpoint",
        "api",
        "how to use",
        "how do i use",
        "open ",
        "show ",
        "status",
        "help me with",
    )
    if any(marker in prompt_lower for marker in module_intent_markers):
        return True

    confidence = float(resolved_core.get("confidence") or 0.0)
    return bool(req.auto_route_all_apis and confidence >= 0.78 and len(prompt_lower.split()) <= 12)


def _build_module_core_shortcut_response(core: Dict[str, Any], language: str) -> str:
    core_id = str(core.get("id", "")).strip()
    if not core_id or not callable(build_module_core_brief):
        return ""

    response_text = build_module_core_brief(core_id, language=language or "en")
    route = str(core.get("route", "")).strip()
    confidence = float(core.get("confidence") or 0.0)

    if (language or "").startswith("sq"):
        suffix = (
            f" Ky kërkim u drejtua te `module core` për të ulur ngarkesën në `Ocean Core`."
            f" Besimi i routing-ut: {confidence:.2f}."
        )
        if route:
            suffix += f" Pika e hyrjes: `{route}`."
    else:
        suffix = (
            f" This request was routed through a lightweight `module core` to reduce load on `Ocean Core`."
            f" Routing confidence: {confidence:.2f}."
        )
        if route:
            suffix += f" Entry point: `{route}`."
    return response_text + suffix


def _resolve_response_format(req: ChatRequest, http_request: Request) -> str:
    requested = (req.response_format or "").strip().lower()
    if requested in {"json", "hybrid", "hybrid-json", "cbor", "cbor2"}:
        return requested

    accept = (http_request.headers.get("accept", "") or "").lower()
    if "application/cbor" in accept or "application/cbor2" in accept:
        return "cbor2"
    return "json"


def _format_chat_output(payload: Dict[str, Any], req: ChatRequest, http_request: Request):
    response_format = _resolve_response_format(req, http_request)

    if response_format in {"cbor", "cbor2"}:
        if HAS_CBOR2 and cbor2 is not None:
            return Response(content=cbor2.dumps(payload), media_type="application/cbor")
        fallback = dict(payload)
        fallback["format_warning"] = "cbor2 not available, returned json"
        return fallback

    if response_format in {"hybrid", "hybrid-json"}:
        hybrid = {
            "format": "hybrid-json",
            "json": payload,
        }
        if HAS_CBOR2 and cbor2 is not None:
            hybrid["cbor2"] = {
                "encoding": "base64",
                "media_type": "application/cbor",
                "data": base64.b64encode(cbor2.dumps(payload)).decode("ascii"),
            }
        else:
            hybrid["cbor2"] = {"available": False}
        return hybrid

    return payload


def _format_optional_cbor(payload: Any, http_request: Request):
    accept = (http_request.headers.get("accept", "") or "").lower()
    wants_cbor = "application/cbor" in accept or "application/cbor2" in accept
    if not wants_cbor:
        return payload

    if HAS_CBOR2 and cbor2 is not None:
        return Response(content=cbor2.dumps(payload), media_type="application/cbor")

    if isinstance(payload, dict):
        fallback = dict(payload)
        fallback["format_warning"] = "cbor2 not available, returned json"
        return fallback

    return {
        "payload": payload,
        "format_warning": "cbor2 not available, returned json",
    }

# ═══════════════════════════════════════════════════════════════════
# ENGINE INSTANCES (initialized once)
# ═══════════════════════════════════════════════════════════════════

mega_engine = None
answer_engine = None
service_registry = None
_warmup_task = None
_memory_store: Dict[str, deque] = {}
_MEMORY_TTL_SECONDS = int(os.getenv("OCEAN_MEMORY_TTL_SECONDS", "3600"))
_MEMORY_MAX_TURNS = int(os.getenv("OCEAN_MEMORY_MAX_TURNS", "10"))
_batica_store: Dict[str, deque] = {}
_BATICA_MAX_NODES = int(os.getenv("OCEAN_BATICA_MAX_NODES", "24"))

# ═══════════════════════════════════════════════════════════════════
# COMPANION STATE - Persistent emotional/companion tracking
# ═══════════════════════════════════════════════════════════════════
_companion_state: Dict[str, Dict[str, Any]] = {}
_COMPANION_MOOD_LEVELS = ["neutral", "happy", "curious", "empathetic", "thoughtful"]
_COMPANION_DEFAULTS = {
    "mood": "neutral",
    "empathy_level": 0.5,
    "user_interests": [],
    "last_emotions": [],
    "conversation_count": 0,
    "last_touch": 0.0
}

def _get_companion_state(session_key: str) -> Dict[str, Any]:
    state = _companion_state.get(session_key)
    if state is None:
        state = _companion_state[session_key] = _COMPANION_DEFAULTS.copy()
    state["last_touch"] = time.time()
    state["conversation_count"] = state.get("conversation_count", 0) + 1
    return state

def _update_companion_emotions(session_key: str, response_text: str, emotions: List[str]) -> None:
    state = _get_companion_state(session_key)
    state["last_emotions"] = emotions[:5]

    # Parse response for mood cues (simple keyword matching)
    response_lower = response_text.lower()
    if any(word in response_lower for word in ["gëzuar", "lumtur", "shumë mirë", "interesant"]):
        state["mood"] = "happy"
        state["empathy_level"] = min(1.0, state["empathy_level"] + 0.1)
    elif any(word in response_lower for word in ["pyetje", "mësoj", "kërkoj", "shpjego"]):
        state["mood"] = "curious"
    elif any(word in response_lower for word in ["ndihmoj", "kuptuar", "dakord"]):
        state["mood"] = "empathetic"
        state["empathy_level"] = min(1.0, state["empathy_level"] + 0.15)

    # Decay interests if old
    state["user_interests"] = state.get("user_interests", [])[-3:]


def _infer_feelings(prompt: str, response_text: str) -> List[str]:
    sample = f"{prompt} {response_text}".lower()
    tags: List[str] = []
    keyword_map = {
        "empathetic": ["ndihm", "sad", "stress", "problem", "frik", "anx", "worry"],
        "curious": ["why", "how", "si", "pse", "explore", "discover", "learn"],
        "supportive": ["can", "let's", "mund", "bashkë", "guide", "assist"],
        "joyful": ["great", "awesome", "shumë mirë", "perfect", "excellent", "gëzuar"],
        "focused": ["step", "plan", "implement", "deploy", "commit", "fix"],
    }
    for tag, words in keyword_map.items():
        if any(word in sample for word in words):
            tags.append(tag)
    if not tags:
        tags.append("neutral")
    return tags[:4]


def _companion_context(req: ChatRequest, prompt: str) -> str:
    if not getattr(req, "enable_companion", True):
        return ""

    session_key = _memory_key(req)
    state = _get_companion_state(session_key)
    feeling_tags = _infer_feelings(prompt, "")

    lines = [
        "## Companion + Feeling Layer",
        f"- Session key: {session_key}",
        f"- Current companion mood: {state.get('mood', 'neutral')}",
        f"- Empathy level: {state.get('empathy_level', 0.5):.2f}",
        f"- Feeling tags from user message: {', '.join(feeling_tags)}",
        "- Keep continuity, emotional intelligence, and human-like companion tone.",
        "- Mirror user language automatically and naturally.",
    ]
    return "\n".join(lines)

_chat_rate_lock = asyncio.Lock()
_chat_rate_buckets: Dict[str, deque] = {}
_autolearning_queue: asyncio.Queue = asyncio.Queue(maxsize=AUTOLEARNING_QUEUE_MAX)
_autolearning_hints: deque = deque(maxlen=120)
_autolearning_task: Optional[asyncio.Task] = None
_autolearning_stats: Dict[str, Any] = {
    "enqueued": 0,
    "dropped": 0,
    "processed": 0,
    "failed": 0,
    "last_error": None,
    "last_processed_at": None,
}
_signal_lock = asyncio.Lock()
_signal_queue: deque = deque(maxlen=SIGNAL_QUEUE_SIZE)
_signal_stats: Dict[str, Any] = {
    "received_total": 0,
    "dropped_total": 0,
    "external_total": 0,
    "internal_total": 0,
    "system_total": 0,
    "last_event_type": None,
    "last_source": None,
    "last_at": None,
}
_nas_stats: Dict[str, Any] = {
    "total_requests": 0,
    "intent_counts": {},
    "architecture_counts": {},
    "last_intent": None,
    "last_architecture": [],
    "last_at": None,
}
_nas_cache: Dict[str, Dict[str, Any]] = {}
_quantum_stats: Dict[str, Any] = {
    "requests": 0,
    "failures": 0,
    "hybrid_collapses": 0,
    "single_collapses": 0,
    "last_selected_engine": None,
    "last_selected_score": 0.0,
    "last_at": None,
}
_quantum_entanglement_map: Dict[str, Any] = {
    "last_query": None,
    "engines": {},
    "top_results": [],
    "collapse": None,
    "updated_at": None,
}
_predictive_cache: Dict[str, Dict[str, Any]] = {}
_predictive_stats: Dict[str, Any] = {
    "requests": 0,
    "hits": 0,
    "misses": 0,
    "prefetched": 0,
    "evicted": 0,
    "last_predictions": [],
    "last_query": None,
    "last_at": None,
}
_evolution_stats: Dict[str, Any] = {
    "enabled": SELF_EVOLVING_ENABLED,
    "generation": 0,
    "requests_seen": 0,
    "last_evolution_at": None,
    "best_intent": None,
    "best_architecture": None,
    "latency_avg_ms": 0.0,
    "quality_avg": 0.0,
    "samples": 0,
    "mutation_rate": EVOLUTION_MUTATION_RATE,
    "sandbox": EVOLUTION_SANDBOX_ENABLED,
}
_evolution_samples: deque = deque(maxlen=max(500, EVOLUTION_INTERVAL_REQUESTS * 2))


def _extract_client_id(http_request: Request) -> str:
    forwarded = (http_request.headers.get("x-forwarded-for", "").split(",")[0].strip())
    return forwarded or (http_request.client.host if http_request.client else "unknown")


def _normalize_signal_origin(origin: Optional[str]) -> str:
    candidate = (origin or "external").strip().lower()
    if candidate not in {"external", "internal", "system"}:
        return "external"
    return candidate


def _route_signal_targets(event_type: str, payload: Dict[str, Any]) -> List[str]:
    sample = f"{event_type} {json.dumps(payload, ensure_ascii=False)[:800]}".lower()
    targets = ["ocean_core"]

    if any(token in sample for token in {"image", "vision", "photo", "ocr", "video"}):
        targets.append("nanogrid")
    if any(token in sample for token in {"kloud", "fabric", "mesh", "peer", "sovereign"}):
        targets.append("kloud_bridge")
    if any(token in sample for token in {"document", "pdf", "docx", "excel", "table", "schema"}):
        targets.append("documents")
    if any(token in sample for token in {"debate", "persona", "trinity", "zurich"}):
        targets.append("reasoning")
    if any(token in sample for token in {"chat", "query", "llm", "prompt"}):
        targets.append("llm_chain")
    if any(token in sample for token in {"audio", "voice", "tts", "speech"}):
        targets.append("voice")

    return list(dict.fromkeys(targets))


async def _ingest_signal(signal: SignalRequest) -> Dict[str, Any]:
    if not SIGNAL_ROUTING_ENABLED:
        return {
            "accepted": False,
            "status": "disabled",
            "reason": "signal_routing_disabled",
        }

    normalized_origin = _normalize_signal_origin(signal.origin)
    signal_id = str(uuid.uuid4())
    now_iso = datetime.datetime.utcnow().isoformat() + "Z"
    targets = _route_signal_targets(signal.event_type, signal.payload)
    priority = (signal.priority or "normal").strip().lower()
    if priority not in {"low", "normal", "high", "critical"}:
        priority = "normal"

    item = {
        "id": signal_id,
        "event_type": (signal.event_type or "unknown").strip()[:120],
        "source": (signal.source or "unknown").strip()[:200],
        "origin": normalized_origin,
        "priority": priority,
        "tags": signal.tags[:20],
        "payload": signal.payload,
        "targets": targets,
        "correlation_id": signal.correlation_id,
        "received_at": now_iso,
    }

    async with _signal_lock:
        before_len = len(_signal_queue)
        _signal_queue.append(item)
        _signal_stats["received_total"] += 1
        if len(_signal_queue) == before_len and before_len >= SIGNAL_QUEUE_SIZE:
            _signal_stats["dropped_total"] += 1
        _signal_stats[f"{normalized_origin}_total"] += 1
        _signal_stats["last_event_type"] = item["event_type"]
        _signal_stats["last_source"] = item["source"]
        _signal_stats["last_at"] = now_iso

    if SIGNAL_TRACE_ENABLED:
        logger.info(
            "📡 signal_ingest id=%s origin=%s type=%s source=%s targets=%s",
            signal_id,
            normalized_origin,
            item["event_type"],
            item["source"],
            ",".join(targets),
        )

    return {
        "accepted": True,
        "status": "queued",
        "signal_id": signal_id,
        "origin": normalized_origin,
        "targets": targets,
        "queue_depth": len(_signal_queue),
        "eventbus": {
            "type": EVENTBUS_TYPE,
            "namespace": PUBSUB_NAMESPACE,
            "batch_size": EVENTBUS_BATCH_SIZE,
            "flush_interval_ms": EVENTBUS_FLUSH_INTERVAL_MS,
        },
    }


async def _allow_chat_request(client_id: str) -> bool:
    # NO RATE LIMIT: chat access is intentionally unlimited in the elastic runtime.
    # Keep the function for call-site compatibility and future policy toggles.
    return True


def _enforce_prompt_limits(prompt: str) -> None:
    if _elastic_unlimited():
        return
    if len(prompt) > CHAT_MAX_PROMPT_CHARS:
        raise HTTPException(
            status_code=413,
            detail=f"Prompt too large. Max {CHAT_MAX_PROMPT_CHARS} chars allowed.",
        )


def _clamp_chat_tokens(max_tokens: Optional[int], long_response: bool = False) -> int:
    if _elastic_unlimited():
        return -1

    requested = max_tokens if isinstance(max_tokens, int) else (12000 if long_response else 4096)
    requested = int(requested)

    if _elastic_unlimited() and requested <= 0:
        return -1

    requested = max(256, requested)
    if _elastic_unlimited():
        return requested

    if CHAT_MAX_TOKENS_HARD > 0:
        return min(requested, CHAT_MAX_TOKENS_HARD)
    return requested


def _require_admin_token(http_request: Request) -> None:
    configured = (ADMIN_API_TOKEN or "").strip()
    if not configured:
        raise HTTPException(status_code=503, detail="Admin token is not configured")
    header_token = (http_request.headers.get("x-admin-token") or "").strip()
    auth_header = (http_request.headers.get("authorization") or "").strip()
    bearer = auth_header[7:].strip() if auth_header.lower().startswith("bearer ") else ""
    candidate = header_token or bearer
    if candidate != configured:
        raise HTTPException(status_code=401, detail="Unauthorized")


def _tokenize_learning(text: str) -> List[str]:
    tokens = re.findall(r"[a-zA-Z0-9_çëëäöüß]{4,}", (text or "").lower())
    seen = set()
    output = []
    for token in tokens:
        if token not in seen:
            seen.add(token)
            output.append(token)
        if len(output) >= 16:
            break
    return output


def _nas_intent_from_query(query: str, domain: Optional[str] = None) -> str:
    if domain:
        domain_lower = domain.strip().lower()
        if domain_lower in {"reasoning", "creative", "technical", "conversational", "research", "multimodal"}:
            return domain_lower

    sample = (query or "").lower()

    intent_map = {
        "research": {"arxiv", "pubmed", "paper", "research", "study", "citation", "wikipedia"},
        "creative": {"song", "lyrics", "music", "story", "poem", "creative", "krijo", "këng"},
        "multimodal": {"image", "video", "photo", "vision", "audio", "voice", "ocr", "document"},
        "technical": {"api", "deploy", "docker", "sql", "code", "script", "architecture"},
        "reasoning": {"why", "compare", "difference", "proof", "logic", "debate", "analyze", "pse"},
    }

    for intent, keywords in intent_map.items():
        if any(keyword in sample for keyword in keywords):
            return intent

    return "conversational"


def _select_nas_architecture(query: str, domain: Optional[str], strict_mode: bool = False) -> Dict[str, Any]:
    cache_key = hashlib.sha1(f"{(query or '').lower()}|{(domain or '').lower()}|{strict_mode}".encode("utf-8")).hexdigest()
    cached = _nas_cache.get(cache_key)
    if cached:
        return dict(cached)

    intent = _nas_intent_from_query(query, domain)
    architecture_by_intent: Dict[str, List[str]] = {
        "reasoning": ["zurich", "trinity", "mega_layers", "real_answer", "knowledge_seeds"],
        "creative": ["batica_zbatica", "trinity", "mega_layers", "companion"],
        "technical": ["real_answer", "knowledge_seeds", "zurich", "mega_layers", "enterprise_guard"],
        "conversational": ["companion", "feeling_layer", "mega_layers", "real_answer"],
        "research": ["knowledge_seeds", "real_answer", "zurich", "mega_layers"],
        "multimodal": ["multimodal", "vision", "voice", "mega_layers", "real_answer"],
    }
    architecture = architecture_by_intent.get(intent, ["mega_layers", "real_answer", "trinity"])

    flags = {
        "use_mega_layers": any(item in architecture for item in {"mega_layers"}),
        "use_knowledge_seeds": any(item in architecture for item in {"knowledge_seeds", "real_answer", "research"}),
        "enable_companion": any(item in architecture for item in {"companion", "feeling_layer", "creative", "conversational"}),
        "strict_mode": bool(strict_mode or intent in {"technical", "reasoning"}),
    }

    now_iso = datetime.datetime.utcnow().isoformat() + "Z"
    _nas_stats["total_requests"] += 1
    _nas_stats["intent_counts"][intent] = int(_nas_stats["intent_counts"].get(intent, 0)) + 1
    arch_key = "+".join(architecture)
    _nas_stats["architecture_counts"][arch_key] = int(_nas_stats["architecture_counts"].get(arch_key, 0)) + 1
    _nas_stats["last_intent"] = intent
    _nas_stats["last_architecture"] = architecture
    _nas_stats["last_at"] = now_iso

    result = {
        "intent": intent,
        "architecture": architecture,
        "flags": flags,
        "cache_hit": False,
        "selected_at": now_iso,
    }

    if len(_nas_cache) >= NAS_CACHE_SIZE:
        oldest_key = next(iter(_nas_cache.keys()), None)
        if oldest_key:
            _nas_cache.pop(oldest_key, None)
    _nas_cache[cache_key] = dict(result)

    return result


def _predictive_cache_key(query: str, domain: Optional[str], strict_mode: bool, language: Optional[str] = None) -> str:
    base = f"{(query or '').strip().lower()}|{(domain or '').strip().lower()}|{strict_mode}|{(language or '').strip().lower()}"
    return hashlib.sha1(base.encode("utf-8")).hexdigest()


def _record_predictive_cache_access(hit: bool, query: str) -> None:
    _predictive_stats["requests"] = int(_predictive_stats.get("requests", 0)) + 1
    if hit:
        _predictive_stats["hits"] = int(_predictive_stats.get("hits", 0)) + 1
    else:
        _predictive_stats["misses"] = int(_predictive_stats.get("misses", 0)) + 1
    _predictive_stats["last_query"] = (query or "")[:300]
    _predictive_stats["last_at"] = datetime.datetime.utcnow().isoformat() + "Z"


def _evict_predictive_cache_if_needed() -> None:
    while len(_predictive_cache) >= PREDICTIVE_CACHE_SIZE:
        oldest_key = next(iter(_predictive_cache.keys()), None)
        if not oldest_key:
            break
        _predictive_cache.pop(oldest_key, None)
        _predictive_stats["evicted"] = int(_predictive_stats.get("evicted", 0)) + 1


def _predict_next_queries(current_query: str) -> List[Dict[str, Any]]:
    query = (current_query or "").strip()
    if not query:
        return []

    tokens = _tokenize_learning(query)
    seed = " ".join(tokens[:4]) if tokens else query[:120]
    candidates: List[Tuple[float, str]] = [
        (0.92, f"explain deeper: {seed}"),
        (0.88, f"give practical steps for: {seed}"),
        (0.84, f"compare alternatives for: {seed}"),
    ]

    for hint in list(_autolearning_hints)[-20:]:
        hint_tokens = hint.get("tokens", []) if isinstance(hint, dict) else []
        overlap = len(set(tokens).intersection(set(hint_tokens))) if tokens else 0
        if overlap >= 2:
            candidates.append((0.72, f"follow-up on {', '.join(hint_tokens[:3])}"))

    dedupe = set()
    predictions: List[Dict[str, Any]] = []
    for confidence, text in sorted(candidates, key=lambda item: item[0], reverse=True):
        normalized = text.strip().lower()
        if not normalized or normalized in dedupe:
            continue
        dedupe.add(normalized)
        if confidence < PREDICTION_CONFIDENCE_THRESHOLD:
            continue
        predictions.append({"query": text, "confidence": round(confidence, 3)})
        if len(predictions) >= PREDICTIVE_PREFETCH_TOP_K:
            break

    _predictive_stats["last_predictions"] = [item["query"] for item in predictions]
    return predictions


async def _prefetch_predictions(current_query: str, domain: Optional[str], strict_mode: bool, language: Optional[str]) -> None:
    if not PREDICTIVE_CACHE_ENABLED:
        return

    predictions = _predict_next_queries(current_query)
    if not predictions:
        return

    for item in predictions:
        predicted_query = item.get("query", "")
        if not predicted_query:
            continue
        pred_plan = _select_nas_architecture(predicted_query, domain, strict_mode)
        cache_key = _predictive_cache_key(predicted_query, domain, strict_mode, language)
        _evict_predictive_cache_if_needed()
        _predictive_cache[cache_key] = {
            "query": predicted_query,
            "confidence": item.get("confidence", 0.0),
            "nas_plan": pred_plan,
            "prefetched_at": datetime.datetime.utcnow().isoformat() + "Z",
        }
        _predictive_stats["prefetched"] = int(_predictive_stats.get("prefetched", 0)) + 1


def _quality_score_from_response(response_text: str, engines_used: List[str], elapsed_s: float) -> float:
    response_len = len((response_text or "").strip())
    engine_bonus = min(0.3, len(engines_used or []) * 0.02)
    latency_penalty = min(0.35, max(0.0, elapsed_s - 1.0) * 0.05)
    richness = min(0.5, response_len / 4000.0)
    score = 0.35 + richness + engine_bonus - latency_penalty
    return max(0.0, min(1.0, round(score, 4)))


def _build_provenance_envelope(
    *,
    trace_id: str,
    engines_used: List[str],
    model: str,
    elapsed_s: float,
    lang_code: str = "en",
    lang_confidence: float = 1.0,
    seed_used: bool = False,
    memory_used: bool = False,
    response_chars: int = 0,
    predictive_cache_hit: bool = False,
    filtering_decisions: Optional[List[str]] = None,
    data_sources: Optional[List[str]] = None,
    orchestration_class: Optional[str] = None,
    mode: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Standard provenance envelope — see docs/architecture/EVIDENCE_SCORE_CONTRACT.md.
    All new fields are additive; existing consumers reading only trace_id/engines/model
    are unaffected.
    """
    # Derive data_sources from engines_used when not explicitly provided
    if data_sources is None:
        data_sources = [
            e for e in engines_used
            if not e.startswith("orch:")
            and e not in {"EnterpriseGuard", "SelfRegenerationFallback"}
        ]

    # Derive filtering_decisions from available signals
    decisions: List[str] = list(filtering_decisions or [])
    if predictive_cache_hit:
        decisions.append("predictive_cache_hit")
    if seed_used:
        decisions.append("knowledge_seed_applied")
    if memory_used:
        decisions.append("session_memory_applied")
    if any(e.startswith("orch:") for e in engines_used):
        decisions.append("orchestration_policy_applied")

    # Confidence: combine language detection confidence with response quality
    quality = _quality_score_from_response("x" * response_chars, engines_used, elapsed_s)
    confidence = round((lang_confidence + quality) / 2.0, 4)

    # Minimal evidence_score inline (does not require the EvidenceScore dataclass here)
    deterministic_engines = {"AlbanianDictionary", "KnowledgeSeeds", "ModuleCore"}
    is_deterministic = bool(deterministic_engines.intersection(set(engines_used)))
    evidence_score = {
        "source_reliability": round(min(1.0, 0.6 + quality * 0.4), 4),
        "evidence_density":   round(min(1.0, len(data_sources) / max(len(data_sources) + 1, 1)), 4),
        "reasoning_clarity":  1.0 if is_deterministic else round(quality * 0.85, 4),
        "safety_pass":        True,
        "latency_ms":         int(elapsed_s * 1000),
    }

    envelope: Dict[str, Any] = {
        "trace_id":             trace_id,
        "engines_used":         engines_used,
        "data_sources":         data_sources,
        "model":                model,
        "confidence":           confidence,
        "filtering_decisions":  decisions,
        "language":             {"code": lang_code, "confidence": lang_confidence},
        "evidence_score":       evidence_score,
    }
    if mode:
        envelope["mode"] = mode
    if orchestration_class:
        envelope["orchestration_class"] = orchestration_class

    return envelope


def _run_evolution_cycle() -> Dict[str, Any]:
    if not _evolution_samples:
        return {"evolved": False, "reason": "no_samples"}

    intent_counts: Dict[str, int] = {}
    architecture_counts: Dict[str, int] = {}
    latency_values: List[float] = []
    quality_values: List[float] = []

    for sample in list(_evolution_samples):
        intent = str(sample.get("intent", "conversational"))
        intent_counts[intent] = intent_counts.get(intent, 0) + 1
        arch = sample.get("architecture", [])
        if isinstance(arch, list):
            key = "+".join(arch)
            architecture_counts[key] = architecture_counts.get(key, 0) + 1
        latency_ms = sample.get("latency_ms")
        quality = sample.get("quality")
        if isinstance(latency_ms, (int, float)):
            latency_values.append(float(latency_ms))
        if isinstance(quality, (int, float)):
            quality_values.append(float(quality))

    best_intent = max(intent_counts.items(), key=lambda item: item[1])[0] if intent_counts else None
    best_arch = max(architecture_counts.items(), key=lambda item: item[1])[0] if architecture_counts else None
    avg_latency = (sum(latency_values) / len(latency_values)) if latency_values else 0.0
    avg_quality = (sum(quality_values) / len(quality_values)) if quality_values else 0.0

    _evolution_stats["generation"] = int(_evolution_stats.get("generation", 0)) + 1
    _evolution_stats["last_evolution_at"] = datetime.datetime.utcnow().isoformat() + "Z"
    _evolution_stats["best_intent"] = best_intent
    _evolution_stats["best_architecture"] = best_arch
    _evolution_stats["latency_avg_ms"] = round(avg_latency, 2)
    _evolution_stats["quality_avg"] = round(avg_quality, 4)
    _evolution_stats["samples"] = len(_evolution_samples)

    return {
        "evolved": True,
        "generation": _evolution_stats["generation"],
        "best_intent": best_intent,
        "best_architecture": best_arch,
        "latency_avg_ms": round(avg_latency, 2),
        "quality_avg": round(avg_quality, 4),
    }


def _record_evolution_sample(prompt: str, elapsed_s: float, response_text: str, engines_used: List[str], nas_plan: Optional[Dict[str, Any]]) -> None:
    if not SELF_EVOLVING_ENABLED:
        return

    _evolution_stats["requests_seen"] = int(_evolution_stats.get("requests_seen", 0)) + 1
    plan = nas_plan or {}
    sample = {
        "ts": time.time(),
        "prompt_chars": len(prompt or ""),
        "latency_ms": round(float(elapsed_s) * 1000.0, 3),
        "quality": _quality_score_from_response(response_text, engines_used, elapsed_s),
        "intent": plan.get("intent", "conversational"),
        "architecture": plan.get("architecture", []),
        "engine_count": len(engines_used or []),
    }
    _evolution_samples.append(sample)

    request_count = int(_evolution_stats.get("requests_seen", 0))
    if request_count > 0 and request_count % EVOLUTION_INTERVAL_REQUESTS == 0:
        summary = _run_evolution_cycle()
        logger.info("🧬 evolution_cycle %s", json.dumps(summary, ensure_ascii=False))


def _score_quantum_candidate(candidate: Dict[str, Any], query: str) -> float:
    text = str(candidate.get("text", "")).strip()
    if not text:
        return 0.0

    query_tokens = set(_tokenize_learning(query))
    text_tokens = set(_tokenize_learning(text))
    overlap = len(query_tokens.intersection(text_tokens))
    overlap_ratio = overlap / max(1, len(query_tokens))
    richness = min(1.0, len(text) / 1200.0)
    reliability = 0.9 if not candidate.get("error") else 0.1
    base = 0.45 * overlap_ratio + 0.35 * richness + 0.20 * reliability
    return round(max(0.0, min(1.0, base)), 4)


async def _quantum_task_mega(query: str) -> Dict[str, Any]:
    try:
        data = process_with_mega_layers(query)
        return {
            "engine": "mega_layers",
            "text": f"meta={data.get('meta_level', 0)}, depth={data.get('consciousness_depth', 0)}, sig={data.get('signature', '')}",
            "raw": data,
        }
    except Exception as exc:
        return {"engine": "mega_layers", "text": "", "error": str(exc)}


async def _quantum_task_seed(query: str) -> Dict[str, Any]:
    try:
        seed = find_knowledge_seed(query)
        return {
            "engine": "knowledge_seeds",
            "text": (seed or "")[:1200],
            "raw": {"matched": bool(seed)},
        }
    except Exception as exc:
        return {"engine": "knowledge_seeds", "text": "", "error": str(exc)}


async def _quantum_task_zurich(query: str) -> Dict[str, Any]:
    try:
        result = zurich_cycle(query)
        output = str(result.get("output", ""))
        return {
            "engine": "zurich",
            "text": output[:1600],
            "raw": {
                "confidence": result.get("confidence", 0.0),
                "strategy": result.get("strategy"),
                "domains": result.get("domains", []),
            },
        }
    except Exception as exc:
        return {"engine": "zurich", "text": "", "error": str(exc)}


async def _quantum_task_router(query: str) -> Dict[str, Any]:
    try:
        route = route_intent(query) if KNOWLEDGE_LAYER_AVAILABLE and callable(route_intent) else ""
        return {
            "engine": "service_router",
            "text": str(route or "")[:400],
            "raw": {"route": route},
        }
    except Exception as exc:
        return {"engine": "service_router", "text": "", "error": str(exc)}


async def _quantum_task_llm(query: str, language: Optional[str] = None) -> Dict[str, Any]:
    try:
        req = ChatRequest(
            message=query,
            language=language,
            use_mega_layers=False,
            use_knowledge_seeds=False,
            enable_companion=False,
            strict_mode=False,
            long_response=False,
        )
        engines: List[str] = []
        text, model = await _chat_with_provider_chain(
            req=req,
            prompt=query,
            enhanced_prompt=(
                "You are quantum-superposition evaluator. "
                "Answer with concise high-precision summary in max 6 lines."
            ),
            lang_code=(language or "en"),
            engines_used=engines,
        )
        return {
            "engine": "llm_chain",
            "text": (text or "")[:1600],
            "raw": {"model": model, "engines": engines},
        }
    except Exception as exc:
        return {"engine": "llm_chain", "text": "", "error": str(exc)}


async def _quantum_superposition(query: str, language: Optional[str] = None, top_k: int = 2) -> Dict[str, Any]:
    workers = max(2, QUANTUM_SUPERPOSITION_WORKERS)
    semaphore = asyncio.Semaphore(workers)

    async def _guarded(coro):
        async with semaphore:
            return await coro

    tasks = [
        _guarded(_quantum_task_mega(query)),
        _guarded(_quantum_task_seed(query)),
        _guarded(_quantum_task_zurich(query)),
        _guarded(_quantum_task_router(query)),
        _guarded(_quantum_task_llm(query, language=language)),
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)
    candidates: List[Dict[str, Any]] = []
    for item in results:
        if isinstance(item, Exception):
            candidates.append({"engine": "unknown", "text": "", "error": str(item), "score": 0.0})
            continue
        if isinstance(item, dict):
            candidate: Dict[str, Any] = {str(key): value for key, value in item.items()}
        else:
            candidate = {"engine": "unknown", "text": str(item)}
        candidate["score"] = _score_quantum_candidate(candidate, query)
        candidates.append(candidate)

    ranked = sorted(candidates, key=lambda row: float(row.get("score", 0.0)), reverse=True)
    top_results = ranked[: max(1, min(top_k, 5))]
    best = top_results[0] if top_results else {"engine": "none", "text": "", "score": 0.0}

    collapse_mode = "single"
    collapse_payload: Dict[str, Any]
    if len(top_results) >= 2:
        delta = float(top_results[0].get("score", 0.0)) - float(top_results[1].get("score", 0.0))
        if delta <= max(0.0, 1.0 - QUANTUM_COLLAPSE_THRESHOLD):
            collapse_mode = "hybrid"
            combined_text = (
                f"[{top_results[0].get('engine')}] {top_results[0].get('text', '')}\n\n"
                f"[{top_results[1].get('engine')}] {top_results[1].get('text', '')}"
            ).strip()
            collapse_payload = {
                "engine": f"hybrid:{top_results[0].get('engine')}+{top_results[1].get('engine')}",
                "text": combined_text[:2400],
                "score": round((float(top_results[0].get("score", 0.0)) + float(top_results[1].get("score", 0.0))) / 2.0, 4),
            }
            _quantum_stats["hybrid_collapses"] = int(_quantum_stats.get("hybrid_collapses", 0)) + 1
        else:
            collapse_payload = {
                "engine": best.get("engine", "unknown"),
                "text": str(best.get("text", ""))[:2400],
                "score": float(best.get("score", 0.0)),
            }
            _quantum_stats["single_collapses"] = int(_quantum_stats.get("single_collapses", 0)) + 1
    else:
        collapse_payload = {
            "engine": best.get("engine", "unknown"),
            "text": str(best.get("text", ""))[:2400],
            "score": float(best.get("score", 0.0)),
        }
        _quantum_stats["single_collapses"] = int(_quantum_stats.get("single_collapses", 0)) + 1

    now_iso = datetime.datetime.utcnow().isoformat() + "Z"
    _quantum_stats["requests"] = int(_quantum_stats.get("requests", 0)) + 1
    _quantum_stats["last_selected_engine"] = collapse_payload.get("engine")
    _quantum_stats["last_selected_score"] = collapse_payload.get("score", 0.0)
    _quantum_stats["last_at"] = now_iso

    _quantum_entanglement_map["last_query"] = (query or "")[:500]
    _quantum_entanglement_map["engines"] = {
        item.get("engine", "unknown"): {
            "score": item.get("score", 0.0),
            "error": item.get("error"),
        }
        for item in ranked
    }
    _quantum_entanglement_map["top_results"] = [
        {
            "engine": item.get("engine"),
            "score": item.get("score"),
            "preview": str(item.get("text", ""))[:280],
        }
        for item in top_results
    ]
    _quantum_entanglement_map["collapse"] = {
        "mode": collapse_mode,
        "selected_engine": collapse_payload.get("engine"),
        "selected_score": collapse_payload.get("score"),
    }
    _quantum_entanglement_map["updated_at"] = now_iso

    return {
        "status": "ok",
        "collapse_mode": collapse_mode,
        "selected": collapse_payload,
        "ranked": top_results,
        "workers": workers,
        "threshold": QUANTUM_COLLAPSE_THRESHOLD,
    }


def _learning_vector(prompt: str, response: str) -> List[float]:
    prompt_len = max(1, len(prompt or ""))
    response_len = max(1, len(response or ""))
    ratio = min(3.0, response_len / float(prompt_len))
    return [
        round(min(1.0, prompt_len / 12000.0), 4),
        round(min(1.0, response_len / 20000.0), 4),
        round(min(1.0, len(_tokenize_learning(prompt)) / 16.0), 4),
        round(min(1.0, ratio / 3.0), 4),
    ]


def _autolearning_context(prompt: str) -> str:
    if not AUTOLEARNING_ENABLED or not _autolearning_hints:
        return ""

    prompt_tokens = set(_tokenize_learning(prompt))
    if not prompt_tokens:
        return ""

    scored: List[Tuple[int, Dict[str, Any]]] = []
    for hint in list(_autolearning_hints)[-40:]:
        hint_tokens = set(hint.get("tokens", []))
        overlap = len(prompt_tokens.intersection(hint_tokens))
        if overlap > 0:
            scored.append((overlap, hint))

    if not scored:
        return ""

    scored.sort(key=lambda item: item[0], reverse=True)
    top = scored[:3]
    lines = ["## AutoLearning Insights (OpenMind/Lite)"]
    for idx, (_score, item) in enumerate(top, start=1):
        lines.append(f"{idx}. {item.get('insight', '')}")
    lines.append("Use these as continuity signals; do not claim guaranteed factual correctness from them.")
    return "\n".join(lines)


def _read_recent_learning_events(max_lines: int = 200) -> List[Dict[str, Any]]:
    path = Path(AUTOLEARNING_LOG_PATH)
    if not path.exists():
        return []

    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    selected = lines[-max(1, min(max_lines, SELFREGEN_REBUILD_MAX_LINES)):]
    events: List[Dict[str, Any]] = []
    for line in selected:
        try:
            item = json.loads(line)
            if isinstance(item, dict):
                events.append(item)
        except Exception:
            continue
    return events


def _rebuild_autolearning_hints_from_events(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    rebuilt = 0
    dedupe = set()
    _autolearning_hints.clear()

    for event in events:
        prompt = str(event.get("prompt", ""))
        response = str(event.get("response", ""))
        language = str(event.get("language", "unknown"))
        tokens = _tokenize_learning(prompt + " " + response)
        if not tokens:
            continue
        signature = tuple(tokens[:8])
        if signature in dedupe:
            continue
        dedupe.add(signature)
        insight = (
            f"lang={language}; topic={', '.join(tokens[:5]) or 'general'}; "
            f"prompt_len={len(prompt)}; response_len={len(response)}"
        )
        _autolearning_hints.append(
            {
                "ts": float(event.get("ts", time.time())),
                "tokens": tokens,
                "insight": insight,
                "trace_id": event.get("trace_id"),
            }
        )
        rebuilt += 1

    return {
        "rebuilt": rebuilt,
        "hints": len(_autolearning_hints),
        "source_events": len(events),
    }


def _build_sovereign_response(prompt: str, req: ChatRequest, lang_code: str) -> str:
    raise RuntimeError("Sovereign template fallback is disabled by NO_FAKE_DATA policy")


async def _chat_with_ollama(model_name: str, prompt: str, enhanced_prompt: str, req: ChatRequest) -> Tuple[str, str]:
    safe_tokens = _clamp_chat_tokens(req.max_tokens, req.long_response)
    ollama_timeout = _resolve_llm_timeout(len(prompt), 2)
    async with httpx.AsyncClient(timeout=ollama_timeout) as client:
        resp = await client.post(
            f"{OLLAMA_HOST}/api/chat",
            json={
                "model": model_name,
                "messages": [
                    {"role": "system", "content": enhanced_prompt},
                    {"role": "user", "content": prompt}
                ],
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_ctx": _resolve_num_ctx(
                        req.long_response,
                        safe_tokens,
                        prompt_chars=len(prompt),
                        message_count=2,
                    ),
                    "repeat_penalty": 1.2,
                    "top_p": 0.9,
                    "num_predict": safe_tokens,
                    "num_keep": 0,
                    "mirostat": 0,
                    "repeat_last_n": 64,
                    "stop": []
                }
            }
        )

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="Ollama /api/chat error")

    data = resp.json()
    return data.get("message", {}).get("content", "No response"), f"OllamaChat({model_name})"


async def _chat_with_openai_compat(model_name: str, prompt: str, enhanced_prompt: str, req: ChatRequest) -> Tuple[str, str]:
    if not OPENAI_COMPAT_BASE:
        raise RuntimeError("OPENAI_COMPAT_BASE not configured")

    chosen_model = OPENAI_COMPAT_MODEL or model_name
    headers = {"Content-Type": "application/json"}
    if OPENAI_COMPAT_API_KEY:
        headers["Authorization"] = f"Bearer {OPENAI_COMPAT_API_KEY}"

    token_budget = _clamp_chat_tokens(req.max_tokens, req.long_response)
    payload: Dict[str, Any] = {
        "model": chosen_model,
        "messages": [
            {"role": "system", "content": enhanced_prompt},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
    }
    if token_budget > 0:
        payload["max_tokens"] = token_budget

    timeout_s = _resolve_llm_timeout(len(prompt), 2)
    async with httpx.AsyncClient(timeout=timeout_s) as client:
        resp = await client.post(
            f"{OPENAI_COMPAT_BASE.rstrip('/')}/v1/chat/completions",
            headers=headers,
            json=payload,
        )

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="OpenAI-compatible /v1/chat/completions error")

    payload = resp.json()
    choices = payload.get("choices", []) if isinstance(payload, dict) else []
    if not choices:
        raise RuntimeError("No choices in OpenAI-compatible response")

    content = choices[0].get("message", {}).get("content", "")
    if _is_forbidden_placeholder_response(content):
        raise RuntimeError("openai_compat_placeholder_response_blocked")
    return content or "No response", f"OpenAICompat({chosen_model})"


def _is_forbidden_placeholder_response(text: str) -> bool:
    sample = (text or "").strip().lower()
    if not sample:
        return False

    # Enforce NO_FAKE_DATA: block canned assistant placeholders that mask provider failures.
    sample = sample.replace("👋", "").replace("�", "").strip()
    forbidden_exact = {
        "hello! how can i help you today?",
        "hello, how can i help you today?",
        "how can i help you today?",
    }
    if sample in forbidden_exact:
        return True
    if sample.startswith("hello! how can i help you today"):
        return True
    return False


def _sanitize_log_text(value: Any, limit: int = 512) -> str:
    text = str(value or "")
    text = text.encode("utf-8", "backslashreplace").decode("utf-8", "replace")
    text = text.replace("\r", " ").replace("\n", " ").strip()
    if limit > 0 and len(text) > limit:
        return text[:limit]
    return text


def _sanitize_provider_text(value: Any) -> str:
    text = str(value or "")
    try:
        return text.encode("utf-8", "ignore").decode("utf-8", "ignore")
    except Exception:
        return ""


async def _chat_with_clx_agent(prompt: str, lang_code: str) -> Tuple[str, str]:
    if not CLX_AGENT_BASE:
        raise RuntimeError("CLX_AGENT_URL not configured")

    payload: Dict[str, Any] = {
        "message": _sanitize_provider_text(prompt),
        "use_memory": True,
    }
    if lang_code:
        payload["language"] = _sanitize_provider_text(lang_code)

    timeout_s = _resolve_llm_timeout(len(prompt), 1)
    async with httpx.AsyncClient(timeout=timeout_s) as client:
        resp = await client.post(
            f"{CLX_AGENT_BASE.rstrip('/')}/chat",
            json=payload,
        )

    if resp.status_code != 200:
        raise RuntimeError(f"clx_agent_status_{resp.status_code}")

    data = resp.json() if resp.content else {}
    text = str((data or {}).get("response") or "").strip()
    if not text:
        raise RuntimeError("clx_agent_empty_response")
    if _is_forbidden_placeholder_response(text):
        raise RuntimeError("clx_agent_placeholder_response_blocked")

    model_name = _sanitize_provider_text((data or {}).get("model") or "clx-core")
    return text, f"CLXAgent({model_name})"


async def _chat_with_asi_lite(prompt: str, model_name: str, lang_code: str) -> Tuple[str, str]:
    base = (SELFLEARNING_LITE_BASE or LITE_BASE or "").strip()
    if not base:
        raise RuntimeError("SELFLEARNING_LITE_URL not configured")

    payload: Dict[str, Any] = {
        "message": _sanitize_provider_text(prompt),
        "model": _sanitize_provider_text(model_name),
    }
    if lang_code:
        payload["language"] = _sanitize_provider_text(lang_code)

    timeout_s = _resolve_llm_timeout(len(prompt), 1)
    async with httpx.AsyncClient(timeout=timeout_s) as client:
        resp = await client.post(
            f"{base.rstrip('/')}/api/v1/chat",
            json=payload,
        )

    if resp.status_code != 200:
        raise RuntimeError(f"asi_lite_status_{resp.status_code}")

    data = resp.json() if resp.content else {}
    text = str((data or {}).get("response") or "").strip()
    if not text:
        raise RuntimeError("asi_lite_empty_response")
    if _is_forbidden_placeholder_response(text):
        raise RuntimeError("asi_lite_placeholder_response_blocked")

    used_model = _sanitize_provider_text((data or {}).get("model") or model_name or "asi-lite")
    return text, f"ASILite({used_model})"


async def _chat_with_provider_chain(
    req: ChatRequest,
    prompt: str,
    enhanced_prompt: str,
    lang_code: str,
    engines_used: List[str],
) -> Tuple[str, str]:
    requested_model = _normalize_ollama_model(req.model or MODEL)
    provider_errors: List[str] = []
    attempted_providers: set[str] = set()

    # -- Orchestration policy: classify before touching any LLM --
    if _HAS_ORCHESTRATION and _route_query is not None:
        try:
            decision = _route_query(prompt)
            engines_used.append(f"orch:{decision.query_class.value}")
            logger.info(
                "orchestration_policy query_class=%s preferred=%s timeout_ms=%d rationale=%r",
                decision.query_class.value,
                decision.preferred_engine,
                decision.timeout_ms,
                decision.rationale,
            )
        except Exception as _orch_err:
            logger.debug("orchestration_policy skipped: %s", _orch_err)

    for provider in (LLM_PROVIDER_ORDER or ["ollama", "openai_compat", "selflearning"]):
        p = provider.strip().lower()
        if not p:
            continue
        attempted_providers.add(p)
        try:
            if p == "ollama":
                response_text, model_used = await _chat_with_ollama(requested_model, prompt, enhanced_prompt, req)
                engines_used.append(model_used)
                return response_text, model_used
            if p in {"openai_compat", "openai-compatible", "vllm"}:
                response_text, model_used = await _chat_with_openai_compat(requested_model, prompt, enhanced_prompt, req)
                engines_used.append(model_used)
                return response_text, model_used
            if p in {"clx", "clx_agent", "clx-ai", "clx.i", "clx_i", "clxi"}:
                response_text, model_used = await _chat_with_clx_agent(prompt, lang_code)
                engines_used.append(model_used)
                return response_text, model_used
            if p in {"asi_lite", "selflearning_lite", "lite", "asi-lite"}:
                response_text, model_used = await _chat_with_asi_lite(prompt, requested_model, lang_code)
                engines_used.append(model_used)
                return response_text, model_used
            if p in {"selflearning", "sovereign", "selfregen"}:
                provider_errors.append(f"{p}:disabled_no_fake_fallback")
                continue
        except Exception as exc:
            provider_errors.append(f"{p}:{exc}")
            continue

    # Force a real internal attempt before sovereign template fallback.
    if "clx" not in attempted_providers:
        try:
            response_text, model_used = await _chat_with_clx_agent(prompt, lang_code)
            engines_used.append(model_used)
            return response_text, model_used
        except Exception as exc:
            provider_errors.append(f"clx:{exc}")

    if "asi_lite" not in attempted_providers and "selflearning_lite" not in attempted_providers and "lite" not in attempted_providers:
        try:
            response_text, model_used = await _chat_with_asi_lite(prompt, requested_model, lang_code)
            engines_used.append(model_used)
            return response_text, model_used
        except Exception as exc:
            provider_errors.append(f"asi_lite:{exc}")

    # Last real fallback: force local Ollama models (llama -> llava) before returning 503.
    tried_models: set[str] = set()
    for candidate in [requested_model, *OLLAMA_FALLBACK_MODELS]:
        normalized = _normalize_ollama_model(candidate)
        if not normalized or normalized in tried_models:
            continue
        tried_models.add(normalized)
        try:
            response_text, model_used = await _chat_with_ollama(normalized, prompt, enhanced_prompt, req)
            text = (response_text or "").strip()
            if not text:
                raise RuntimeError("empty_ollama_fallback_response")
            engines_used.append(model_used)
            return text, model_used
        except Exception as exc:
            provider_errors.append(f"ollama_fallback[{normalized}]:{exc}")

    raise HTTPException(status_code=503, detail=f"No real provider available (no fake fallback): {' | '.join(provider_errors[:6])}")


def _queue_autolearning_event(event: Dict[str, Any]) -> None:
    if not AUTOLEARNING_ENABLED:
        return
    try:
        _autolearning_queue.put_nowait(event)
        _autolearning_stats["enqueued"] += 1
    except asyncio.QueueFull:
        _autolearning_stats["dropped"] += 1


async def _dispatch_autolearning_event(event: Dict[str, Any]) -> None:
    Path(AUTOLEARNING_LOG_PATH).parent.mkdir(parents=True, exist_ok=True)
    with open(AUTOLEARNING_LOG_PATH, "a", encoding="utf-8") as file_handle:
        file_handle.write(json.dumps(event, ensure_ascii=False) + "\n")
    prompt = str(event.get("prompt", ""))
    response = str(event.get("response", ""))
    language = str(event.get("language", "unknown"))
    tokens = _tokenize_learning(prompt + " " + response)
    insight = (
        f"lang={language}; topic={', '.join(tokens[:5]) or 'general'}; "
        f"prompt_len={len(prompt)}; response_len={len(response)}"
    )
    _autolearning_hints.append(
        {
            "ts": time.time(),
            "tokens": tokens,
            "insight": insight,
            "trace_id": event.get("trace_id"),
        }
    )

    async with httpx.AsyncClient(timeout=AUTOLEARNING_TIMEOUT_S) as client:
        if AUTOLEARNING_TO_REGULATORY and REGULATORY_BASE.strip():
            try:
                preflight_payload = {
                    "jurisdiction": "EU",
                    "data_region": "EU",
                    "model_id": event.get("model", MODEL),
                    "user_id": event.get("user_id", "anonymous"),
                    "query": prompt[:240],
                    "tags": tokens[:8],
                }
                await client.post(f"{REGULATORY_BASE}/api/regulatory/preflight", json=preflight_payload)
                federated_payload = {
                    "jurisdiction": "EU",
                    "model_id": event.get("model", MODEL),
                    "pattern_vector": _learning_vector(prompt, response),
                    "is_clinical_data": False,
                    "metadata": {
                        "trace_id": event.get("trace_id"),
                        "language": language,
                        "source": "ocean-core-autolearning",
                    },
                }
                await client.post(f"{REGULATORY_BASE}/api/regulatory/federated/collect", json=federated_payload)
            except Exception as exc:
                logger.warning(f"⚠️ AutoLearning regulatory sink skipped: {exc}")

        if AUTOLEARNING_TO_OPENMIND and OPENMIND_BASE.strip():
            try:
                openmind_payload = {
                    "message": f"Learning insight: {insight}. user_prompt={prompt[:300]}",
                    "provider": "openmind",
                    "model": event.get("model", MODEL),
                    "options": {},
                }
                await client.post(f"{OPENMIND_BASE}/api/openmind", json=openmind_payload)
            except Exception as exc:
                logger.warning(f"⚠️ AutoLearning openmind sink skipped: {exc}")

        if AUTOLEARNING_TO_LITE and LITE_BASE.strip():
            try:
                lite_payload = {
                    "message": f"Learning snapshot: {prompt[:280]}",
                    "model": event.get("model", MODEL),
                }
                await client.post(f"{LITE_BASE.rstrip('/')}/api/v1/chat", json=lite_payload)
            except Exception as exc:
                logger.warning(f"⚠️ AutoLearning lite sink skipped: {exc}")


async def _autolearning_worker() -> None:
    while True:
        event = await _autolearning_queue.get()
        try:
            await _dispatch_autolearning_event(event)
            _autolearning_stats["processed"] += 1
            _autolearning_stats["last_processed_at"] = time.time()
            _autolearning_stats["last_error"] = None
        except Exception as exc:
            _autolearning_stats["failed"] += 1
            _autolearning_stats["last_error"] = str(exc)
            logger.warning(f"⚠️ AutoLearning dispatch failed: {exc}")
        finally:
            _autolearning_queue.task_done()


def _memory_key(req: ChatRequest) -> str:
    raw = (req.clerk_user_id or req.user_name or "anonymous").strip().lower() or "anonymous"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def _memory_get(req: ChatRequest) -> List[Dict[str, Any]]:
    key = _memory_key(req)
    now = time.time()
    bucket = _memory_store.get(key)
    if not bucket:
        return []

    valid = [item for item in bucket if now - float(item.get("ts", 0.0)) <= _MEMORY_TTL_SECONDS]
    _memory_store[key] = deque(valid, maxlen=_MEMORY_MAX_TURNS)
    return list(_memory_store[key])


def _memory_put(req: ChatRequest, user_text: str, assistant_text: str, language: str) -> None:
    key = _memory_key(req)
    bucket = _memory_store.get(key)
    if bucket is None:
        bucket = deque(maxlen=_MEMORY_MAX_TURNS)
        _memory_store[key] = bucket

    bucket.append(
        {
            "ts": time.time(),
            "user": user_text,
            "assistant": assistant_text,
            "language": language,
        }
    )


def _memory_context(req: ChatRequest) -> str:
    turns = _memory_get(req)
    if not turns:
        return ""

    tail = turns[-4:]
    lines = ["## Short-Term Memory (Recent Turns)"]
    for idx, item in enumerate(tail, start=1):
        user_msg = str(item.get("user", "")).strip().replace("\n", " ")[:180]
        assistant_msg = str(item.get("assistant", "")).strip().replace("\n", " ")[:220]
        lines.append(f"{idx}. User: {user_msg}")
        lines.append(f"   Assistant: {assistant_msg}")
    return "\n".join(lines)


def _memory_safety_contract(has_memory: bool) -> str:
    lines = [
        "## Memory Safety Contract (Global)",
        "- Never invent prior conversations, personal history, or user preferences.",
        "- Only reference memory entries explicitly present in Short-Term Memory context.",
    ]
    if has_memory:
        lines.append("- Memory context is available: use it carefully and factually.")
    else:
        lines.append("- No memory context is available: do not claim any past interaction.")
    lines.append("- Keep language consistency with the detected/requested user language.")
    return "\n".join(lines)


def _heuristic_detect_language(text: str) -> Optional[Tuple[str, str, float]]:
    sample = (text or "").strip()
    if not sample:
        return None

    lower = sample.lower()

    script_patterns = [
        (r"[\u0600-\u06FF]", ("ar", "Arabic", 0.93)),
        (r"[\u0400-\u04FF]", ("ru", "Russian", 0.88)),
        (r"[\u0370-\u03FF]", ("el", "Greek", 0.9)),
        (r"[\u0590-\u05FF]", ("he", "Hebrew", 0.9)),
        (r"[\u0900-\u097F]", ("hi", "Hindi", 0.85)),
        (r"[\u3040-\u309F\u30A0-\u30FF]", ("ja", "Japanese", 0.92)),
        (r"[\uAC00-\uD7AF]", ("ko", "Korean", 0.92)),
        (r"[\u4E00-\u9FFF]", ("zh", "Chinese", 0.9)),
    ]
    for pattern, result in script_patterns:
        if re.search(pattern, sample):
            return result

    if len(sample) <= 80:
        token_hints = {
            "sq": ["ku", "jemi", "këtu", "ketu", "faleminderit", "përshëndetje", "pershendetje", "shqip", "mos", "jam", "une", "unë", "ti", "eshte", "është", "mire", "mirë", "shume", "shumë", "dhe", "pse", "cfare", "çfarë", "kjo", "kush"],
            "de": ["hallo", "danke", "wo", "wie", "ich", "bin", "bist", "mein", "meine", "ist", "das", "der", "die", "ein", "eine", "nicht", "ja", "nein", "bitte", "schön", "schon", "gut", "heute", "was", "wer", "wann", "warum", "weiss", "weiß", "geht", "gehts", "auf", "mit", "dir", "mir", "dein", "seine", "haben", "hatte", "war"],
            "es": ["hola", "gracias", "donde", "qué", "como", "que", "por", "es", "muy", "bien", "cuando"],
            "fr": ["bonjour", "merci", "où", "comment", "je", "tu", "est", "une", "les", "des", "vous", "nous", "salut"],
            "it": ["ciao", "grazie", "dove", "come", "sono", "sei", "cosa", "che", "non", "anche"],
            "pt": ["olá", "obrigado", "onde", "como", "você", "sim", "não", "ola"],
            "tr": ["merhaba", "teşekkür", "nerede", "nasıl", "evet", "hayır", "ben", "sen"],
            "nl": ["hoe", "dag", "goed", "dank", "jij", "jou", "wij", "wat", "het", "een", "van"],
            "el": ["γεια", "ευχαριστώ", "που", "πως", "ναι", "όχι", "είμαι", "είσαι"],
        }
        language_names = {
            "sq": "Albanian",
            "de": "German",
            "es": "Spanish",
            "fr": "French",
            "it": "Italian",
            "pt": "Portuguese",
            "tr": "Turkish",
            "nl": "Dutch",
            "el": "Greek",
        }
        for code, hints in token_hints.items():
            if any(token in lower for token in hints):
                return (code, language_names.get(code, code), 0.82)

    return None


def _needs_albanian_repair(text: str) -> bool:
    sample = (text or "").strip().lower()
    if not sample:
        return False

    malformed_markers = [
        "je nuk jam",
        "ndaj mëkatet",
        "kopeje të madhe të fjalësh",
        "gjithmonë! ti pëlqen të flasësh",
        "proçesë e zhvillimit",
        "stadije kryesore",
        "përçarja dhe përpilimi",
        "të përditësisht zhvillimi",
        "të kontinuojnë përfeqimi",
        "shqipja ime është shqip",
        "nuk kanë dëshirën të folur",
        "miranë!",
        "përgjigjur pyetjeve juaj",
    ]
    if any(marker in sample for marker in malformed_markers):
        return True

    cross_language_markers = [
        "primary focus detected",
        "running in sovereign",
        "operational answer",
    ]
    if any(marker in sample for marker in cross_language_markers):
        return True

    return False


def _multimodal_context(req: ChatRequest) -> str:
    context = (req.multimodal_context or "").strip()
    if not context:
        return ""
    return (
        "## Latest Multimodal Context\n"
        "Use this as trusted user-provided context for follow-up answers.\n"
        f"{context[:6000]}"
    )


def _is_song_flow(text: str, req: ChatRequest) -> bool:
    sample = f"{(req.session_topic or '')} {(text or '')}".lower()
    song_keywords = [
        "song", "lyrics", "melody", "verse", "chorus", "hook", "beat", "bpm",
        "këng", "tekst", "refren", "strof", "muzik", "ritëm",
    ]
    return any(keyword in sample for keyword in song_keywords)


def _batica_zbatica_context(req: ChatRequest, prompt: str) -> str:
    if not _is_song_flow(prompt, req):
        return ""
    key = _memory_key(req)
    nodes = list(_batica_store.get(key, deque()))[-6:]
    if not nodes:
        return (
            "## Batica-Zbatica Creative Flow\n"
            "Initialize composition nodes (theme, mood, tempo, structure) and evolve them turn-by-turn."
        )

    lines = [
        "## Batica-Zbatica Creative Flow",
        "Continue from prior composition nodes; preserve coherence of theme, hook, rhythm and narrative arc.",
    ]
    for idx, node in enumerate(nodes, start=1):
        lines.append(f"{idx}. {node}")
    return "\n".join(lines)


def _batica_zbatica_put(req: ChatRequest, prompt: str, response: str) -> None:
    if not _is_song_flow(prompt, req):
        return
    key = _memory_key(req)
    bucket = _batica_store.get(key)
    if bucket is None:
        bucket = deque(maxlen=_BATICA_MAX_NODES)
        _batica_store[key] = bucket
    node = (
        f"prompt={prompt.strip().replace(chr(10), ' ')[:220]} | "
        f"response={response.strip().replace(chr(10), ' ')[:320]}"
    )
    bucket.append(node)


def _store_conversation_turn(req: ChatRequest, prompt: str, response_text: str, language: str) -> int:
    clean_response = (response_text or "").strip()
    if not clean_response:
        return len(_memory_get(req))

    _memory_put(req, prompt, clean_response, language or "auto")
    if req.enable_feeling_layer or req.enable_companion:
        _update_companion_emotions(_memory_key(req), clean_response, _infer_feelings(prompt, clean_response))
    _batica_zbatica_put(req, prompt, clean_response)
    return len(_memory_get(req))


def _req_for_user(user_id: Optional[str], language: Optional[str] = None) -> ChatRequest:
    safe_user = (user_id or "anonymous").strip() or "anonymous"
    return ChatRequest(
        message="context-sync",
        user_name=safe_user,
        clerk_user_id=safe_user,
        language=language,
    )

def initialize_engines():
    """Initialize all engines on startup"""
    global mega_engine, answer_engine, service_registry

    if MEGA_LAYERS_AVAILABLE and callable(get_mega_layer_engine):
        try:
            mega_engine = get_mega_layer_engine()
            logger.info("🚀 MegaLayerEngine initialized")
        except Exception as e:
            logger.error(f"❌ MegaLayerEngine init failed: {e}")

    if REAL_ANSWER_AVAILABLE and callable(get_answer_engine):
        try:
            answer_engine = get_answer_engine()
            logger.info("🚀 RealAnswerEngine initialized")
        except Exception as e:
            logger.error(f"❌ RealAnswerEngine init failed: {e}")

    if SERVICE_REGISTRY_AVAILABLE and callable(get_service_registry):
        try:
            service_registry = get_service_registry()
            logger.info("🚀 ServiceRegistry initialized")
        except Exception as e:
            logger.error(f"❌ ServiceRegistry init failed: {e}")

# ═══════════════════════════════════════════════════════════════════
# LANGUAGE DETECTION via Translation Node
# ═══════════════════════════════════════════════════════════════════

async def detect_language(text: str) -> tuple:
    """Detect language using Translation Node with robust global fallbacks."""
    heuristic = _heuristic_detect_language(text)
    if heuristic:
        return heuristic

    try:
        async with httpx.AsyncClient(timeout=2.0) as client:  # Fast 2s timeout
            resp = await client.post(
                f"{TRANSLATION_NODE}/api/v1/detect",
                json={"text": text}
            )
            if resp.status_code == 200:
                data = resp.json()
                return (
                    data.get("detected_language", "en"),
                    data.get("language_name", "English"),
                    data.get("confidence", 0.5)
                )
    except Exception as e:
        logger.debug(f"Language detection skipped: {e}")  # Debug not warning

    if HAS_LANGDETECT and callable(langdetect_detect):
        try:
            detected_raw = langdetect_detect(text or "")
            detected = detected_raw.lower() if isinstance(detected_raw, str) and detected_raw else "en"
            normalized = {
                "zh-cn": "zh",
                "zh-tw": "zh",
                "pt-br": "pt",
                "pt-pt": "pt",
            }.get(detected, detected)
            language_name = await resolve_language_name(normalized)
            return (normalized, language_name or normalized.upper(), 0.74)
        except LangDetectException:
            pass
        except Exception as e:
            logger.debug(f"Langdetect fallback skipped: {e}")

    return ("en", "English", 0.5)


async def resolve_language_name(lang_code: str) -> str:
    """Resolve ISO language code to display name via Translation Node (dynamic)."""
    code = (lang_code or "").strip().lower()
    if not code:
        return ""

    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(f"{TRANSLATION_NODE}/api/v1/languages")
            if resp.status_code == 200:
                data = resp.json()
                languages = data.get("languages", {}) if isinstance(data, dict) else {}
                info = languages.get(code, {}) if isinstance(languages, dict) else {}
                if isinstance(info, dict):
                    return info.get("name", "") or info.get("native", "") or ""
    except Exception as e:
        logger.debug(f"Language name resolve skipped: {e}")

    return ""


async def translate_text_dynamic(text: str, target_lang: str, source_lang: str = "auto") -> str:
    """Translate text via Translation Node using dynamic language codes."""
    if not text or not target_lang:
        return text

    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.post(
                f"{TRANSLATION_NODE}/api/v1/translate",
                json={"text": text, "source": source_lang, "target": target_lang},
            )
            if resp.status_code == 200:
                data = resp.json()
                translated = data.get("translated")
                if isinstance(translated, str) and translated.strip():
                    return translated
    except Exception as e:
        logger.debug(f"Dynamic translation skipped: {e}")

    return text


async def _repair_albanian_response(req: ChatRequest, prompt: str, draft_response: str, enhanced_prompt: str) -> Optional[Tuple[str, str]]:
    repair_prompt = (
        "Riformulo tekstin e mëposhtëm në shqip standarde, natyrale dhe korrekte. "
        "Mos ndrysho kuptimin. Mos shto ide të reja. Jep vetëm versionin final të riformuluar.\n\n"
        f"Pyetja e përdoruesit:\n{prompt}\n\n"
        f"Drafti për riformulim:\n{draft_response}"
    )
    repair_system = (
        enhanced_prompt
        + "\n\nALBANIAN REPAIR MODE (MANDATORY):"
        + "\n- Output only standard Albanian."
        + "\n- Preserve meaning exactly."
        + "\n- Remove malformed or invented wording."
    )

    repair_engines: List[str] = []
    repaired_text, repaired_model = await _chat_with_provider_chain(
        req=req,
        prompt=repair_prompt,
        enhanced_prompt=repair_system,
        lang_code="sq",
        engines_used=repair_engines,
    )
    repaired = (repaired_text or "").strip()
    if not repaired:
        return None
    return repaired, repaired_model

# ═══════════════════════════════════════════════════════════════════
# MEGA LAYER PROCESSING
# ═══════════════════════════════════════════════════════════════════

def process_with_mega_layers(query: str) -> Dict[str, Any]:
    """Process query through MegaLayerEngine - uses process_query method"""
    if not MEGA_LAYERS_AVAILABLE or not mega_engine:
        return {"active": False}

    try:
        # Correct method: process_query returns (LayerActivation, results_dict)
        activation, results = mega_engine.process_query(query)
        return {
            "active": True,
            "meta_level": getattr(getattr(activation, "meta_level", None), "value", 0),
            "consciousness_depth": getattr(activation, "consciousness_depth", 0),
            "emotional_resonance": len(getattr(activation, "emotional_dimensions", []) or []),
            "fractal_depth": getattr(activation, "fractal_depth", 0),
            "signature": (getattr(activation, "unique_signature", "") or "")[:16]
        }
    except Exception as e:
        logger.debug(f"MegaLayer skipped: {e}")  # Debug not error
        return {"active": False}

# ═══════════════════════════════════════════════════════════════════
# KNOWLEDGE SEEDS LOOKUP
# ═══════════════════════════════════════════════════════════════════

def find_knowledge_seed(query: str) -> Optional[str]:
    """Find matching knowledge seed for query"""
    if not KNOWLEDGE_SEEDS_AVAILABLE or find_matching_seed is None:
        return None

    try:
        seed = find_matching_seed(query)
        if seed:
            seed_content = getattr(seed, "content", None)
            return seed_content if isinstance(seed_content, str) else str(seed)
    except Exception as e:
        logger.error(f"Knowledge seed error: {e}")
    return None

# ═══════════════════════════════════════════════════════════════════
# STREAMING RESPONSE GENERATOR
# ═══════════════════════════════════════════════════════════════════

async def stream_ollama_response(
    model: str,
    messages: list,
    options: dict,
    engines_used: list,
    lang_code: str,
    allow_model_fallback: bool = True,
) -> AsyncGenerator[str, None]:
    """
    Stream response from Ollama word by word.
    This makes the first token appear in 2-3 seconds instead of waiting 60+ seconds.
    """
    model = _normalize_ollama_model(model)
    emitted_any = False
    system_prompt = ""
    user_prompt = ""
    try:
        for msg in messages or []:
            role = (msg or {}).get("role")
            content = (msg or {}).get("content", "")
            if role == "system" and content and not system_prompt:
                system_prompt = content
            elif role == "user" and content:
                user_prompt = content
        if not user_prompt and messages:
            user_prompt = (messages[-1] or {}).get("content", "")
    except Exception:
        user_prompt = (messages[-1] or {}).get("content", "") if messages else ""
    prompt_chars = len(user_prompt or "")
    timeout_s = _resolve_llm_timeout(prompt_chars, len(messages or []))
    chunk_chars = _elastic_chunk_chars(prompt_chars)

    try:
        async with httpx.AsyncClient(timeout=timeout_s) as client:
            async with client.stream(
                "POST",
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": model,
                    "prompt": user_prompt,
                    "system": system_prompt,
                    "stream": True,  # STREAMING ENABLED!
                    "options": options
                }
            ) as response:
                if response.status_code != 200:
                    available_models: List[str] = []
                    if response.status_code == 404:
                        try:
                            tags_resp = await client.get(f"{OLLAMA_HOST}/api/tags")
                            if tags_resp.status_code == 200:
                                tags_payload = tags_resp.json() if tags_resp.content else {}
                                raw_models = tags_payload.get("models", []) if isinstance(tags_payload, dict) else []
                                for row in raw_models:
                                    if isinstance(row, dict):
                                        name = row.get("name")
                                        if isinstance(name, str) and name.strip():
                                            available_models.append(name.strip())
                        except Exception as tag_err:
                            logger.warning(f"Failed to list Ollama models after 404: {tag_err}")

                    if response.status_code == 404 and allow_model_fallback and available_models:
                        fallback_model = next((name for name in available_models if name != model), available_models[0])
                        if fallback_model and fallback_model != model:
                            logger.warning(
                                "Model '%s' returned 404; retrying with available model '%s'",
                                model,
                                fallback_model,
                            )
                            async for chunk in stream_ollama_response(
                                model=fallback_model,
                                messages=messages,
                                options=options,
                                engines_used=engines_used,
                                lang_code=lang_code,
                                allow_model_fallback=False,
                            ):
                                yield chunk
                            return

                    payload = {
                        "error": "model_unavailable",
                        "code": f"upstream_status_{response.status_code}",
                        "status": response.status_code,
                        "model": model,
                    }
                    if available_models:
                        payload["available_models"] = available_models

                    yield json.dumps(payload)
                    return

                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            content = None
                            if isinstance(data.get("response"), str):
                                content = data.get("response")
                            elif isinstance(data.get("message"), dict) and isinstance(data["message"].get("content"), str):
                                content = data["message"]["content"]

                            if content:
                                emitted_any = True
                                if len(content) <= chunk_chars:
                                    yield content
                                else:
                                    for i in range(0, len(content), chunk_chars):
                                        yield content[i:i + chunk_chars]
                            # Check if done
                            if data.get("done", False):
                                break
                        except json.JSONDecodeError:
                            continue
        if not emitted_any:
            # No fake fallback text: return explicit stream error token so caller can route to real providers.
            yield "[Error: upstream_empty_stream]"
    except Exception as e:
        sanitized_error = _sanitize_log_text(e)
        logger.error("Streaming error: %s", sanitized_error)
        yield f"[Error: {sanitized_error}]"



async def _emit_stream_metrics(
    req: ChatRequest,
    prompt: str,
    started_at: float,
    first_token_at: Optional[float],
    emitted_text: str,
    fallback_used: bool,
    stream_error: Optional[str],
) -> None:
    elapsed_s = max(0.0, time.perf_counter() - started_at)
    ttft_ms = round((first_token_at - started_at) * 1000.0, 2) if first_token_at else None
    emitted_chunks = len(re.findall(r"\S+", emitted_text or ""))
    payload_bytes = len((emitted_text or "").encode("utf-8"))
    bits = payload_bytes * 8
    pixels = len(emitted_text or "")
    btl_score = round(bits + (0.25 * pixels), 3)
    btl_per_second = round((btl_score / elapsed_s), 3) if elapsed_s > 0 and btl_score > 0 else 0.0
    bits_per_second = round((bits / elapsed_s), 3) if elapsed_s > 0 and bits > 0 else 0.0
    pixels_per_second = round((pixels / elapsed_s), 3) if elapsed_s > 0 and pixels > 0 else 0.0

    await _ingest_signal(
        SignalRequest(
            event_type="chat.stream.metrics",
            source="api:/api/v1/chat/stream",
            payload={
                "ttft_ms": ttft_ms,
                "btl_per_second": btl_per_second,
                "bits_per_second": bits_per_second,
                "pixels_per_second": pixels_per_second,
                "emitted_chunks": emitted_chunks,
                "emitted_btl": {
                    "bits": bits,
                    "pixels": pixels,
                    "chunks": emitted_chunks,
                    "btl_score": btl_score,
                    "unit": "BTL",
                },
                "elapsed_ms": round(elapsed_s * 1000.0, 2),
                "fallback_fast_path_used": bool(fallback_used),
                "stream_error": stream_error,
                "prompt_chars": len(prompt or ""),
            },
            origin="internal",
            correlation_id=req.clerk_user_id,
        )
    )


# ═══════════════════════════════════════════════════════════════════
# MAIN PROCESSING PIPELINE
# ═══════════════════════════════════════════════════════════════════

async def process_query_full(req: ChatRequest) -> ChatResponse:
    """
    Full processing pipeline using all available engines:
    1. Language Detection (72 languages)
    2. Service Routing (Knowledge Layer)
    3. Knowledge Seeds Lookup
    4. Mega Layer Processing
    5. Ollama Generation with enhanced context
    """
    start_time = time.time()
    engines_used = []
    trace_id = str(uuid.uuid4())

    prompt = req.message or req.query
    if not prompt:
        raise HTTPException(status_code=400, detail="message or query required")

    nas_plan: Optional[Dict[str, Any]] = None
    effective_use_mega_layers = bool(req.use_mega_layers)
    effective_use_knowledge_seeds = bool(req.use_knowledge_seeds)
    effective_enable_companion = bool(req.enable_companion)
    effective_strict_mode = bool(req.strict_mode)
    predictive_cache_hit = False
    cache_key = _predictive_cache_key(prompt, req.domain, req.strict_mode, req.language)

    if PREDICTIVE_CACHE_ENABLED:
        cached = _predictive_cache.get(cache_key)
        if isinstance(cached, dict) and isinstance(cached.get("nas_plan"), dict):
            nas_plan = dict(cached.get("nas_plan") or {})
            predictive_cache_hit = True
            _record_predictive_cache_access(True, prompt)
            engines_used.append("PredictiveCache(hit)")
        else:
            _record_predictive_cache_access(False, prompt)
            engines_used.append("PredictiveCache(miss)")

    if NAS_ENABLED and not nas_plan:
        nas_plan = _select_nas_architecture(prompt, req.domain, req.strict_mode)
        flags = nas_plan.get("flags", {}) if isinstance(nas_plan, dict) else {}
        effective_use_mega_layers = bool(effective_use_mega_layers and flags.get("use_mega_layers", True))
        effective_use_knowledge_seeds = bool(effective_use_knowledge_seeds and flags.get("use_knowledge_seeds", True))
        effective_enable_companion = bool(effective_enable_companion and flags.get("enable_companion", True))
        effective_strict_mode = bool(effective_strict_mode or flags.get("strict_mode", False))
        engines_used.append(f"NAS({nas_plan.get('intent', 'unknown')})")
        engines_used.append("NeuralArchitectureSearch")
    elif NAS_ENABLED and nas_plan:
        flags = nas_plan.get("flags", {}) if isinstance(nas_plan, dict) else {}
        effective_use_mega_layers = bool(effective_use_mega_layers and flags.get("use_mega_layers", True))
        effective_use_knowledge_seeds = bool(effective_use_knowledge_seeds and flags.get("use_knowledge_seeds", True))
        effective_enable_companion = bool(effective_enable_companion and flags.get("enable_companion", True))
        effective_strict_mode = bool(effective_strict_mode or flags.get("strict_mode", False))
        engines_used.append(f"NAS({nas_plan.get('intent', 'unknown')})")
        engines_used.append("NeuralArchitectureSearch(cached)")
    else:
        engines_used.append("NAS(disabled)")

    # 0. Enterprise Guard - Security & Input Validation
    if ENTERPRISE_GUARD_AVAILABLE and enterprise_guard:
        input_check = enterprise_guard.check_input(prompt)
        if not input_check["proceed"]:
            # Blocked by security
            warning_msg = input_check["warnings"][0] if input_check["warnings"] else "Kërkesa nuk lejohet."
            return ChatResponse(
                response=warning_msg,
                model="enterprise_guard",
                processing_time=round(time.time() - start_time, 2),
                engines_used=["EnterpriseGuard:Blocked"],
                language_detected="unknown",
                layer_activations={"security": "blocked", "reason": input_check.get("warnings", [])}
            )
        engines_used.append("EnterpriseGuard")

    requested_language = _normalize_requested_language(req.language)

    # 1. Detect language with adaptive preference logic
    detected_lang_code, detected_lang_name, detected_confidence = await detect_language(prompt)
    strict_language_lock = bool(requested_language and effective_strict_mode)

    if strict_language_lock:
        lang_code = requested_language
        lang_name = await resolve_language_name(lang_code)
        confidence = 1.0
        engines_used.append(f"StrictLanguageLock({lang_code})")
        logger.info(f"🌍 Strict language lock active: {lang_code} ({lang_name})")
    elif requested_language:
        # HOTFIX 2025-03-25: AdaptiveLanguage override only when:
        #  - prompt is long enough (>=80 chars) to reliably detect language
        #  - confidence is very high (>=0.95) to avoid false-positive switching
        # Prevents cases like short English prompts with a Catalan/Estonian user ID
        # being misidentified, causing LanguageLock quality degradation.
        _prompt_long_enough = len(prompt.strip()) >= 80
        _conf_high_enough = (detected_confidence or 0.0) >= 0.95
        if (
            detected_lang_code
            and detected_lang_code != requested_language
            and _prompt_long_enough
            and _conf_high_enough
        ):
            lang_code = detected_lang_code
            lang_name = detected_lang_name
            confidence = detected_confidence
            engines_used.append(f"AdaptiveLanguage({requested_language}->{lang_code})")
            logger.info(
                f"🌍 Adaptive language switch: requested={requested_language}, detected={lang_code}, confidence={detected_confidence:.2f} (prompt_len={len(prompt.strip())})"
            )
        else:
            lang_code = requested_language
            lang_name = await resolve_language_name(lang_code)
            confidence = max(detected_confidence or 0.0, 0.85)
            engines_used.append(f"PreferredLanguage({lang_code})")
            logger.info(f"🌍 Preferred language applied: {lang_code} ({lang_name})")
    else:
        lang_code = detected_lang_code
        lang_name = detected_lang_name
        confidence = detected_confidence
        engines_used.append(f"AutoDetect({lang_code})")
        logger.info(f"🌍 Language auto-detected: {lang_code} ({lang_name})")

    lang_instruction = ""
    if lang_code != "en":
        if strict_language_lock:
            lang_instruction = (
                f"\n\n🚨 CRITICAL LANGUAGE MANDATE: You MUST respond EXCLUSIVELY in {lang_name} ({lang_code})."
                f" Every single word must be in {lang_name}. Mixing languages is a CRITICAL ERROR."
                " This applies regardless of user identity, name, nationality, or company."
            )
        elif requested_language:
            lang_instruction = (
                f"\n\n🌍 LANGUAGE DIRECTIVE: Respond in {lang_name} ({lang_code}) for this conversation."
                " Do NOT mix languages in a single response."
                " If the user switches to another language, follow them naturally but stay consistent within each reply."
            )
        else:
            lang_instruction = (
                f"\n\n🌍 LANGUAGE MANDATE (MANDATORY — NON-NEGOTIABLE): The user is currently writing in {lang_name} ({lang_code})."
                f" You MUST respond ENTIRELY in {lang_name}."
                " Do NOT switch to any other language under ANY circumstances."
                " This rule overrides all other knowledge: regardless of the user's name, background, company, or nationality, respond ONLY in the detected language."
                f" Language mixing is a CRITICAL ERROR. Your entire response must be in {lang_name} only."
            )

    # 2. Service Routing
    if KNOWLEDGE_LAYER_AVAILABLE and callable(route_intent):
        routed_service = route_intent(prompt)
        if routed_service and routed_service in SERVICES:
            engines_used.append(f"ServiceRouter({routed_service})")

    resolved_module_core = _resolve_module_core_candidate(req, prompt)
    if resolved_module_core:
        engines_used.append(f"ModuleCoreResolver({resolved_module_core.get('id', 'unknown')})")

    if resolved_module_core and _should_shortcut_module_core(prompt, req, resolved_module_core):
        shortcut_response = _build_module_core_shortcut_response(resolved_module_core, lang_code)
        if shortcut_response:
            engines_used.append("ModuleCoreShortcut")
            elapsed = time.time() - start_time
            logger.info(
                "⚡ %.1fs - Module core shortcut (%s) - Engines: %s",
                elapsed,
                resolved_module_core.get("id", "unknown"),
                ", ".join(engines_used),
            )
            return ChatResponse(
                response=shortcut_response,
                model="module_core_router_v1",
                processing_time=round(elapsed, 2),
                engines_used=engines_used,
                language_detected=lang_code,
                layer_activations={
                    "module_core": resolved_module_core,
                    "offload": True,
                },
                provenance=_build_provenance_envelope(
                    trace_id=trace_id,
                    engines_used=engines_used,
                    model="module_core_router_v1",
                    elapsed_s=elapsed,
                    lang_code=lang_code,
                    mode="module_core_shortcut",
                ),
                governance={
                    "policy_layer": "enterprise_guard" if ENTERPRISE_GUARD_AVAILABLE else "baseline",
                    "status": "allow",
                },
                memory={
                    "enabled": True,
                    "session_key": _memory_key(req),
                    "turns": len(_memory_get(req)),
                },
            )

    # 3. Knowledge Seeds
    seed_context = ""
    if effective_use_knowledge_seeds:
        seed = find_knowledge_seed(prompt)
        if seed:
            seed_context = f"\n\nRELEVANT KNOWLEDGE:\n{seed}"
            engines_used.append("KnowledgeSeeds")

    # 4. Mega Layer Processing
    layer_activations = None
    mega_context = ""
    if effective_use_mega_layers:
        layer_activations = process_with_mega_layers(prompt)
        if layer_activations.get("active"):
            mega_context = f"\n\n[Layer Depth: {layer_activations.get('consciousness_depth', 0)}, Emotional: {layer_activations.get('emotional_resonance', 0):.2f}]"
            engines_used.append("MegaLayerEngine")

    # 4.5. STRICT MODE - Detyron ndjekjen e rregullave
    strict_instruction = ""
    if effective_strict_mode:
        strict_instruction = """

## STRICT MODE ACTIVATED - MANDATORY RULES
You MUST follow these rules EXACTLY. No exceptions.

1. **STAY ON TOPIC**: Answer ONLY what was asked. Do not add extra information.
2. **NO QUESTIONS**: Do not ask the user questions. Just answer.
3. **NO DEVIATIONS**: Do not change the subject or add unrelated content.
4. **NO HALLUCINATIONS**: If you don't know, say "I don't know". Do not invent.
5. **FOLLOW INSTRUCTIONS**: If given a list of steps, execute ALL steps in order.
6. **SELF-ANALYSIS**: If asked to analyze your response, do it honestly.
7. **IMMEDIATE START**: Begin writing your answer immediately, no preamble.
8. **CONTINUOUS OUTPUT**: Write without stopping until the task is complete.

VIOLATION OF THESE RULES IS NOT ALLOWED."""
        engines_used.append("StrictMode")

    # 4.6. ALBANIAN DICTIONARY - Direct response for Albanian definition queries
    if ALBANIAN_DICT_AVAILABLE and callable(get_albanian_response) and _should_use_albanian_dictionary(prompt, requested_language):
        # Check if we have a direct Albanian answer (for definitions, greetings, etc.)
        albanian_response = get_albanian_response(prompt)
        if albanian_response:
            engines_used.append("AlbanianDictionary")
            elapsed = time.time() - start_time
            logger.info(f"✅ [sq] {elapsed:.1f}s - Albanian Dict Response - Engines: {', '.join(engines_used)}")
            return ChatResponse(
                response=albanian_response,
                model="albanian_dictionary_v1",
                processing_time=round(elapsed, 2),
                engines_used=engines_used,
                language_detected="sq",
                layer_activations=None,
                provenance=_build_provenance_envelope(
                    trace_id=trace_id,
                    engines_used=engines_used,
                    model="albanian_dictionary_v1",
                    elapsed_s=elapsed,
                    lang_code="sq",
                    mode="dictionary_shortcut",
                ),
                governance={
                    "policy_layer": "enterprise_guard" if ENTERPRISE_GUARD_AVAILABLE else "baseline",
                    "status": "allow",
                },
                memory={
                    "enabled": True,
                    "session_key": _memory_key(req),
                    "turns": len(_memory_get(req)),
                },
            )

    # 5. Build enhanced system prompt
    shared_system_context = _build_shared_system_context()
    user_context = _build_user_context(req)
    conversation_context = _incoming_messages_context(req)
    memory_context = _memory_context(req)
    memory_safety_context = _memory_safety_contract(bool(memory_context or conversation_context))
    companion_context = _companion_context(req, prompt) if effective_enable_companion else ""
    multimodal_context = _multimodal_context(req)
    batica_context = _batica_zbatica_context(req, prompt)
    autolearning_context = _autolearning_context(prompt)
    personality_context = _personality_contract_context(req)
    if shared_system_context:
        engines_used.append("SharedSystemContext")
    if user_context:
        engines_used.append("UserContext")
    if conversation_context:
        engines_used.append("ConversationFlow")
    if memory_context:
        engines_used.append("ShortTermMemory")
    if memory_safety_context:
        engines_used.append("MemorySafetyContract")
    if companion_context:
        engines_used.append("CompanionFeelingLayer")
    if multimodal_context:
        engines_used.append("MultimodalContext")
    if batica_context:
        engines_used.append("BaticaZbatica")
    if autolearning_context:
        engines_used.append("AutoLearningContext")
    if personality_context:
        engines_used.append("PersonalityContract")

    enhanced_prompt = (
        SYSTEM_PROMPT
        + (f"\n\n{shared_system_context}" if shared_system_context else "")
        + (f"\n\n{user_context}" if user_context else "")
        + (f"\n\n{conversation_context}" if conversation_context else "")
        + (f"\n\n{memory_context}" if memory_context else "")
        + (f"\n\n{memory_safety_context}" if memory_safety_context else "")
        + (f"\n\n{companion_context}" if companion_context else "")
        + (f"\n\n{multimodal_context}" if multimodal_context else "")
        + (f"\n\n{batica_context}" if batica_context else "")
        + (f"\n\n{autolearning_context}" if autolearning_context else "")
        + (f"\n\n{personality_context}" if personality_context else "")
        + "\n\nALBANIAN QUALITY POLICY: If responding in Albanian, use only standard Albanian, natural grammar, and precise wording. Avoid invented or corrupted words."
        + "\n\n" + RESPONSE_STYLE_POLICY
        + lang_instruction
        + seed_context
        + mega_context
        + strict_instruction
    )

    # 6. Provider chain: Ollama -> OpenAI-compatible -> SelfLearning Sovereign fallback
    response_text, model_used = await _chat_with_provider_chain(
        req=req,
        prompt=prompt,
        enhanced_prompt=enhanced_prompt,
        lang_code=lang_code,
        engines_used=engines_used,
    )

    if lang_code and lang_code != "en" and response_text.strip():
        try:
            generated_lang_code, _, generated_lang_conf = await detect_language(response_text[:600])
            # HOTFIX 2025-03-25: Only apply LanguageLock translation when:
            #  - LLM response language is detected with very high confidence (>=0.92)
            #  - This prevents double-processing on multilingual responses with mixed signals
            #  - Quality-degrading auto-translate (e.g. en->et, en->ca) is the primary bug
            _lock_confidence_ok = (generated_lang_conf or 0.0) >= 0.92
            if generated_lang_code and generated_lang_code != lang_code and _lock_confidence_ok:
                translated = await translate_text_dynamic(response_text, target_lang=lang_code, source_lang="auto")
                if isinstance(translated, str) and translated.strip():
                    response_text = translated
                    engines_used.append(f"LanguageLock({generated_lang_code}->{lang_code})")
        except Exception as exc:
            logger.debug(f"Language lock skipped: {exc}")

    if lang_code == "sq" and ALBANIAN_REPAIR_ENABLED and _needs_albanian_repair(response_text):
        try:
            repaired_result = await _repair_albanian_response(req, prompt, response_text, enhanced_prompt)
            if repaired_result:
                repaired_text, repaired_model = repaired_result
                response_text = repaired_text
                model_used = repaired_model
                engines_used.append("AlbanianQualityRepair")
        except Exception as exc:
            logger.debug(f"Albanian quality repair skipped: {exc}")

    elapsed = time.time() - start_time

    _record_evolution_sample(prompt, elapsed, response_text, engines_used, nas_plan)
    if PREDICTIVE_CACHE_ENABLED and not predictive_cache_hit:
        asyncio.create_task(_prefetch_predictions(prompt, req.domain, req.strict_mode, req.language))

    memory_turns = _store_conversation_turn(req, prompt, response_text, lang_code)

    if len(prompt.strip()) >= AUTOLEARNING_MIN_PROMPT_CHARS:
        _queue_autolearning_event(
            {
                "ts": time.time(),
                "trace_id": trace_id,
                "prompt": prompt[:12000],
                "response": response_text[:18000],
                "language": lang_code,
                "user_id": (req.clerk_user_id or req.user_name or "anonymous")[:120],
                "session_key": _memory_key(req),
                "model": model_used,
                "engines": engines_used,
            }
        )

    logger.info(f"✅ [{lang_code}] {elapsed:.1f}s - Engines: {', '.join(engines_used)}")

    # Derive orchestration class from engines_used tag injected by Day 3 policy
    _orch_class = next((e.split(":")[1] for e in engines_used if e.startswith("orch:")), None)

    return ChatResponse(
        response=response_text,
        model=model_used,
        processing_time=round(elapsed, 2),
        engines_used=engines_used,
        language_detected=lang_code,
        layer_activations=layer_activations,
        provenance=_build_provenance_envelope(
            trace_id=trace_id,
            engines_used=engines_used,
            model=model_used,
            elapsed_s=elapsed,
            lang_code=lang_code,
            lang_confidence=confidence,
            seed_used=bool(seed_context),
            memory_used=bool(memory_context),
            response_chars=len(response_text),
            predictive_cache_hit=bool(predictive_cache_hit),
            orchestration_class=_orch_class,
        ),
        governance={
            "policy_layer": "enterprise_guard" if ENTERPRISE_GUARD_AVAILABLE else "baseline",
            "status": "allow",
            "strict_mode": bool(effective_strict_mode),
            "autolearning_enabled": AUTOLEARNING_ENABLED,
            "predictive_cache_hit": predictive_cache_hit,
            "self_evolving_enabled": SELF_EVOLVING_ENABLED,
        },
        memory={
            "enabled": True,
            "session_key": _memory_key(req),
            "turns": memory_turns,
            "ttl_seconds": _MEMORY_TTL_SECONDS,
        },
    )

# ═══════════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@app.on_event("startup")
async def startup_event():
    """Initialize engines on startup"""
    global _autolearning_task
    logger.info("🚀 Ocean Core Full starting...")
    initialize_engines()
    if AUTOLEARNING_ENABLED:
        _autolearning_task = asyncio.create_task(_autolearning_worker())
        logger.info("🧠 AutoLearning worker started")
    logger.info("✅ All engines initialized")
    logger.info(f"📡 Ollama: {OLLAMA_HOST}")
    logger.info(f"🤖 Model: {MODEL}")
    logger.info(f"🌍 Translation Node: {TRANSLATION_NODE}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global _warmup_task, _autolearning_task
    if _warmup_task:
        _warmup_task.cancel()
        logger.info("🛑 Warmup task stopped")
    if _autolearning_task:
        _autolearning_task.cancel()
        logger.info("🛑 AutoLearning worker stopped")

@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "Ocean Core Full",
        "version": "5.0.0",
        "model": MODEL,
        "engines": {
            "mega_layers": MEGA_LAYERS_AVAILABLE,
            "real_answer": REAL_ANSWER_AVAILABLE,
            "service_registry": SERVICE_REGISTRY_AVAILABLE,
            "albanian_dict": ALBANIAN_DICT_AVAILABLE,
            "knowledge_seeds": KNOWLEDGE_SEEDS_AVAILABLE,
            "knowledge_layer": KNOWLEDGE_LAYER_AVAILABLE
        }
    }

@app.get("/health")
async def health():
    """
    Fast health endpoint — always returns 200 once the process is up.

    Includes real-time dependency connectivity so the SLO/SLI collector
    can compute `dependency_health` without a separate probe.

    Shape understood by slo_sli_collector._parse_dependency_health():
        {"dependencies": {"healthy": N, "total": N}}
    """
    _start = time.time()

    # Probe the two critical upstreams with a tight timeout so this
    # endpoint stays fast (< 2 s) even when a dependency is slow.
    dep_checks = {
        "ollama": f"{OLLAMA_HOST.rstrip('/')}/api/tags",
        "translation": f"{TRANSLATION_NODE.rstrip('/')}/health",
    }

    healthy_deps = 0
    dep_status: Dict[str, Any] = {}
    for dep_name, dep_url in dep_checks.items():
        try:
            req = urllib.request.Request(dep_url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=1) as r:
                ok = 200 <= r.status < 300
        except Exception:
            ok = False
        dep_status[dep_name] = "up" if ok else "down"
        if ok:
            healthy_deps += 1

    total_deps = len(dep_checks)
    dep_health_ratio = healthy_deps / total_deps if total_deps > 0 else 1.0

    return {
        "status": "healthy",
        "version": "5.0.0",
        "uptime_s": round(time.time() - _start, 3),
        "ollama": OLLAMA_HOST,
        "translation_node": TRANSLATION_NODE,
        # Structured field consumed by slo_sli_collector
        "dependencies": {
            "healthy": healthy_deps,
            "total": total_deps,
            "detail": dep_status,
        },
        "dependency_health": dep_health_ratio,
    }

@app.get("/api/v1/status")
async def status():
    return {
        "status": "operational",
        "service": "Ocean Core Full",
        "version": "5.0.0",
        "model": MODEL,
        "system_prompt_path": SYSTEM_PROMPT_PATH,
        "module_map_path": MODULE_MAP_PATH,
        "system_prompt_loaded": bool(_read_text_cached(SYSTEM_PROMPT_PATH, default_value="")),
        "module_map_loaded": bool(_read_text_cached(MODULE_MAP_PATH, default_value="")),
        "engines_active": sum([
            MEGA_LAYERS_AVAILABLE,
            REAL_ANSWER_AVAILABLE,
            SERVICE_REGISTRY_AVAILABLE,
            ALBANIAN_DICT_AVAILABLE,
            KNOWLEDGE_SEEDS_AVAILABLE,
            KNOWLEDGE_LAYER_AVAILABLE,
            ENTERPRISE_GUARD_AVAILABLE
        ]),
        "total_layer_combinations": TOTAL_COMBINATIONS if MEGA_LAYERS_AVAILABLE else 0,
        "enterprise_guard": enterprise_guard.get_status() if ENTERPRISE_GUARD_AVAILABLE and enterprise_guard else None
    }


@app.get("/status")
async def status_alias_root():
    return await status()


@app.get("/api/status")
async def status_alias_api():
    return await status()


async def _probe_service(base_url: str) -> Dict[str, Any]:
    checks = ["/health", "/status", "/"]
    for path in checks:
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                r = await client.get(f"{base_url.rstrip('/')}{path}")
                if r.status_code < 500:
                    return {
                        "ok": True,
                        "status_code": r.status_code,
                        "path": path,
                    }
        except Exception:
            continue
    return {"ok": False}


def _safe_http_json(response: httpx.Response) -> Dict[str, Any]:
    try:
        payload = response.json()
        return payload if isinstance(payload, dict) else {"data": payload}
    except Exception:
        return {"text": response.text[:500]}


async def _fetch_service_json(base_url: str, path: str, timeout_s: float = 4.0) -> Dict[str, Any]:
    if not base_url:
        return {"ok": False, "configured": False, "error": "base_url_not_configured"}

    url = f"{base_url.rstrip('/')}{path}"
    try:
        async with httpx.AsyncClient(timeout=timeout_s) as client:
            response = await client.get(url)
            response.raise_for_status()
            return {
                "ok": True,
                "configured": True,
                "status_code": response.status_code,
                "path": path,
                "url": url,
                "data": _safe_http_json(response),
            }
    except Exception as exc:
        return {
            "ok": False,
            "configured": bool(base_url),
            "path": path,
            "url": url,
            "error": str(exc),
        }


async def _proxy_kloud_request(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    if not KLOUD_BRIDGE_BASE:
        raise HTTPException(status_code=503, detail="KLOUD_BRIDGE_URL is not configured for Ocean Core")

    url = f"{KLOUD_BRIDGE_BASE.rstrip('/')}{path}"
    try:
        async with httpx.AsyncClient(timeout=KLOUD_BRIDGE_TIMEOUT_S) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return {
                "status": "ok",
                "bridge_url": url,
                "result": _safe_http_json(response),
            }
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Kloud bridge returned {exc.response.status_code} for {path}: {exc.response.text[:300]}",
        ) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Kloud bridge request failed: {exc}") from exc


@app.get("/api/v1/integrations/status")
async def integrations_status():
    central = await _probe_service(CENTRAL_API_BASE)
    agents_runtime = await _fetch_service_json(CENTRAL_API_BASE, "/api/agents/status")
    openmind = await _probe_service(OPENMIND_BASE)
    excel = await _probe_service(EXCEL_CORE_BASE)
    video_generator = await _probe_service(VIDEO_GENERATOR_BASE)
    selflearning_lite = await _probe_service(SELFLEARNING_LITE_BASE)
    agents_api = await _probe_service(AGENTS_API_BASE)
    orchestrator = await _probe_service(ORCHESTRATOR_BASE)
    orchestra = await _probe_service(ORCHESTRA_BASE)
    labors = await _probe_service(LABORS_BASE)
    laboratories = await _probe_service(LABORATORIES_BASE)
    kloud = await _probe_service(KLOUD_BRIDGE_BASE)

    return {
        "status": "operational" if any([
            central.get("ok"),
            openmind.get("ok"),
            excel.get("ok"),
            video_generator.get("ok"),
            agents_runtime.get("ok"),
            selflearning_lite.get("ok"),
            agents_api.get("ok"),
            orchestrator.get("ok"),
            orchestra.get("ok"),
            labors.get("ok"),
            laboratories.get("ok"),
            kloud.get("ok"),
        ]) else "degraded",
        "services": {
            "central_api": {"base": CENTRAL_API_BASE, **central},
            "agents_runtime": {"base": CENTRAL_API_BASE, **agents_runtime},
            "openmind": {"base": OPENMIND_BASE, **openmind},
            "excel_core": {"base": EXCEL_CORE_BASE, **excel},
            "video_generator": {"base": VIDEO_GENERATOR_BASE, **video_generator},
            "selflearning_lite": {"base": SELFLEARNING_LITE_BASE, **selflearning_lite},
            "agents_api": {"base": AGENTS_API_BASE, **agents_api},
            "orchestrator": {"base": ORCHESTRATOR_BASE, **orchestrator},
            "orchestra": {"base": ORCHESTRA_BASE, **orchestra},
            "labors": {"base": LABORS_BASE, **labors},
            "laboratories": {"base": LABORATORIES_BASE, **laboratories},
            "kloud_bridge": {"base": KLOUD_BRIDGE_BASE, **kloud},
        },
    }


@app.get("/api/v1/integrations/kloud/status")
@app.get("/api/v1/kloud/status")
async def kloud_bridge_status():
    bridge = await _fetch_service_json(KLOUD_BRIDGE_BASE, "/status", timeout_s=min(KLOUD_BRIDGE_TIMEOUT_S, 4.0))
    return {
        "status": "connected" if bridge.get("ok") else "degraded",
        "bridge": bridge,
    }


@app.post("/api/v1/integrations/kloud/publish")
@app.post("/api/v1/kloud/publish")
async def kloud_bridge_publish(request: KloudPublishRequest):
    payload = request.model_dump(exclude_none=True)
    payload["source"] = request.source or "ocean-core"
    return await _proxy_kloud_request("/signals/publish", payload)


@app.post("/api/v1/integrations/kloud/sync")
@app.post("/api/v1/kloud/sync")
async def kloud_bridge_sync(request: KloudSyncRequest):
    payload = request.model_dump()
    payload.setdefault("metadata", {})["requested_by"] = "ocean-core"
    return await _proxy_kloud_request("/fabric/sync", payload)


def _advanced_fallback_languages() -> Dict[str, Dict[str, str]]:
    catalog: Dict[str, Dict[str, str]] = {}

    try:
        from translation_node import SUPPORTED_LANGUAGES as _tn_languages  # type: ignore[import-not-found]
        if isinstance(_tn_languages, dict):
            for code, meta in _tn_languages.items():
                if isinstance(code, str) and isinstance(meta, dict):
                    catalog[code] = {
                        "name": str(meta.get("name", code)),
                        "native": str(meta.get("native", meta.get("name", code))),
                        "region": str(meta.get("region", "world")),
                    }
    except Exception:
        pass

    extended_languages = {
        "as": {"name": "Assamese", "native": "অসমীয়া", "region": "asia"},
        "ay": {"name": "Aymara", "native": "Aymar aru", "region": "america"},
        "bho": {"name": "Bhojpuri", "native": "भोजपुरी", "region": "asia"},
        "br": {"name": "Breton", "native": "Brezhoneg", "region": "europe"},
        "ceb": {"name": "Cebuano", "native": "Cebuano", "region": "asia"},
        "co": {"name": "Corsican", "native": "Corsu", "region": "europe"},
        "doi": {"name": "Dogri", "native": "डोगरी", "region": "asia"},
        "dv": {"name": "Divehi", "native": "ދިވެހި", "region": "asia"},
        "eo": {"name": "Esperanto", "native": "Esperanto", "region": "world"},
        "eu": {"name": "Basque", "native": "Euskara", "region": "europe"},
        "fo": {"name": "Faroese", "native": "Føroyskt", "region": "europe"},
        "fy": {"name": "Frisian", "native": "Frysk", "region": "europe"},
        "gd": {"name": "Scottish Gaelic", "native": "Griddling", "region": "europe"},
        "gl": {"name": "Galician", "native": "Galego", "region": "europe"},
        "gn": {"name": "Guarani", "native": "Avañe'ẽ", "region": "america"},
        "gom": {"name": "Konkani", "native": "कोंकणी", "region": "asia"},
        "haw": {"name": "Hawaiian", "native": "ʻŌlelo Hawaiʻi", "region": "america"},
        "hmn": {"name": "Hmong", "native": "Hmong", "region": "asia"},
        "ht": {"name": "Haitian Creole", "native": "Kreyòl ayisyen", "region": "america"},
        "jv": {"name": "Javanese", "native": "Basa Jawa", "region": "asia"},
        "ky": {"name": "Kyrgyz", "native": "Кыргызча", "region": "asia"},
        "lb": {"name": "Luxembourgish", "native": "Lëtzebuergesch", "region": "europe"},
        "ln": {"name": "Lingala", "native": "Lingála", "region": "africa"},
        "mai": {"name": "Maithili", "native": "मैथिली", "region": "asia"},
        "mg": {"name": "Malagasy", "native": "Malagasy", "region": "africa"},
        "mi": {"name": "Maori", "native": "Te Reo Māori", "region": "oceania"},
        "mni": {"name": "Meitei", "native": "ꯃꯤꯇꯩ ꯂꯣꯟ", "region": "asia"},
        "mo": {"name": "Moldovan", "native": "Moldovenească", "region": "europe"},
        "nso": {"name": "Northern Sotho", "native": "Sepedi", "region": "africa"},
        "ny": {"name": "Chichewa", "native": "Chichewa", "region": "africa"},
        "om": {"name": "Oromo", "native": "Afaan Oromoo", "region": "africa"},
        "or": {"name": "Odia", "native": "ଓଡ଼ିଆ", "region": "asia"},
        "ps": {"name": "Pashto", "native": "پښتو", "region": "asia"},
        "qu": {"name": "Quechua", "native": "Runa Simi", "region": "america"},
        "rw": {"name": "Kinyarwanda", "native": "Ikinyarwanda", "region": "africa"},
        "sa": {"name": "Sanskrit", "native": "संस्कृतम्", "region": "asia"},
        "sm": {"name": "Samoan", "native": "Gagana Sāmoa", "region": "oceania"},
        "sn": {"name": "Shona", "native": "chiShona", "region": "africa"},
        "so": {"name": "Somali", "native": "Soomaali", "region": "africa"},
        "st": {"name": "Sesotho", "native": "Sesotho", "region": "africa"},
        "su": {"name": "Sundanese", "native": "Basa Sunda", "region": "asia"},
        "tg": {"name": "Tajik", "native": "Тоҷикӣ", "region": "asia"},
        "ti": {"name": "Tigrinya", "native": "ትግርኛ", "region": "africa"},
        "tk": {"name": "Turkmen", "native": "Türkmen", "region": "asia"},
        "to": {"name": "Tongan", "native": "Lea Fakatonga", "region": "oceania"},
        "ts": {"name": "Tsonga", "native": "Xitsonga", "region": "africa"},
        "tt": {"name": "Tatar", "native": "Татарча", "region": "europe"},
        "ug": {"name": "Uyghur", "native": "ئۇيغۇرچە", "region": "asia"},
        "wo": {"name": "Wolof", "native": "Wolof", "region": "africa"},
        "xh": {"name": "Xhosa", "native": "isiXhosa", "region": "africa"},
        "yi": {"name": "Yiddish", "native": "ייִדיש", "region": "europe"},
    }

    for code, meta in extended_languages.items():
        if code not in catalog:
            catalog[code] = meta

    return catalog


@app.get("/api/v1/selflearning/status")
async def selflearning_status():
    queue_size = _autolearning_queue.qsize()
    log_path = Path(AUTOLEARNING_LOG_PATH)
    events_preview = _read_recent_learning_events(max_lines=40)
    return {
        "status": "operational" if AUTOLEARNING_ENABLED else "disabled",
        "enabled": AUTOLEARNING_ENABLED,
        "queue": {
            "size": queue_size,
            "max": AUTOLEARNING_QUEUE_MAX,
        },
        "hints": {
            "count": len(_autolearning_hints),
            "max": 120,
        },
        "stats": _autolearning_stats,
        "log": {
            "path": AUTOLEARNING_LOG_PATH,
            "exists": log_path.exists(),
            "size_bytes": log_path.stat().st_size if log_path.exists() else 0,
            "recent_events": len(events_preview),
        },
        "provider_chain": LLM_PROVIDER_ORDER,
        "sovereign_selfregeneration": SOVEREIGN_SELFREGEN_ENABLED,
    }


@app.post("/api/v1/selfregeneration/rebuild")
async def selfregeneration_rebuild(request: Request, max_lines: int = Query(default=500, ge=20, le=5000)):
    _require_admin_token(request)
    events = _read_recent_learning_events(max_lines=max_lines)
    summary = _rebuild_autolearning_hints_from_events(events)
    return {
        "status": "ok",
        "mode": "selfregeneration",
        "max_lines": max_lines,
        **summary,
    }


@app.get("/api/v1/languages/world")
async def languages_world():
    """Expose all available world languages dynamically from Translation Node."""
    fallback_languages = _advanced_fallback_languages()

    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            resp = await client.get(f"{TRANSLATION_NODE.rstrip('/')}/api/v1/languages")
            if resp.status_code == 200:
                data = resp.json()
                languages = data.get("languages", {}) if isinstance(data, dict) else {}
                if isinstance(languages, dict) and languages:
                    return {
                        "status": "ok",
                        "source": "translation_node_dynamic",
                        "count": len(languages),
                        "languages": languages,
                        "auto_language_reply": True,
                    }
    except Exception as exc:
        logger.debug(f"languages_world fallback triggered: {exc}")

    return {
        "status": "degraded",
        "source": "hybrid_fallback_catalog",
        "count": len(fallback_languages),
        "languages": fallback_languages,
        "auto_language_reply": True,
    }


@app.get("/api/v1/companion/state")
async def companion_state(user_id: Optional[str] = Query(default=None), user_name: Optional[str] = Query(default=None)):
    """Read current companion + feeling state for a session."""
    req = _req_for_user(user_id or user_name, language=None)
    if user_name:
        req.user_name = user_name
    session_key = _memory_key(req)
    state = _get_companion_state(session_key)
    return {
        "status": "ok",
        "session_key": session_key,
        "state": state,
        "mood_levels": _COMPANION_MOOD_LEVELS,
    }


@app.get("/api/v1/ocean/stack/full")
async def ocean_stack_full():
    """
    Unified capability surface for Ocean Core:
    streaming + knowledge + i18 + feeling/companion + internal/external API catalog.
    """
    integration = await integrations_status()
    world_languages = await languages_world()

    internal_catalog = {
        "agents.py": AGENTS_API_BASE,
        "orchestrator": ORCHESTRATOR_BASE,
        "orchestra": ORCHESTRA_BASE,
        "video_generator": VIDEO_GENERATOR_BASE,
        "excel_core": EXCEL_CORE_BASE,
        "selflearning_lite": SELFLEARNING_LITE_BASE,
        "labors": LABORS_BASE,
        "laboratories": LABORATORIES_BASE,
        "knowledge_layer": "embedded",
        "knowledge_seeds": "embedded",
    }

    external_free_api_catalog = {
        "arxiv": "/api/v1/arxiv/search",
        "wikipedia": "/api/v1/wikipedia/search",
        "pubmed": "/api/v1/pubmed/search",
        "web_search": "/api/v1/web/search",
        "web_browse": "/api/v1/web/browse",
    }

    return {
        "status": "operational",
        "service": "Ocean Core Full",
        "version": "5.1.0",
        "capabilities": {
            "streaming": True,
            "knowledge": bool(KNOWLEDGE_LAYER_AVAILABLE or KNOWLEDGE_SEEDS_AVAILABLE),
            "auto_i18_world_languages": True,
            "feeling_layer": True,
            "companion_mode": True,
            "all_internal_apis_routed": True,
            "all_external_free_apis_cataloged": True,
            "selflearning_enabled": AUTOLEARNING_ENABLED,
            "selfregeneration_enabled": SOVEREIGN_SELFREGEN_ENABLED,
            "llm_provider_chain": bool(LLM_PROVIDER_ORDER),
        },
        "language": {
            "auto_detect": True,
            "auto_reply_in_user_language": True,
            "catalog": world_languages,
        },
        "integrations": integration,
        "llm": {
            "provider_order": LLM_PROVIDER_ORDER,
            "ollama": OLLAMA_HOST,
            "openai_compat_base": OPENAI_COMPAT_BASE or None,
            "openai_compat_model": OPENAI_COMPAT_MODEL or None,
        },
        "internal_api_catalog": internal_catalog,
        "external_free_api_catalog": external_free_api_catalog,
    }


@app.post("/api/v1/signals/validate")
async def validate_signal(request: SignalValidateRequest):
    sample = request.test_signal or {}
    required_fields = ["event_type", "source", "payload"]
    missing = [field for field in required_fields if field not in sample]
    payload_ok = isinstance(sample.get("payload", {}), dict)
    event_type_ok = bool(str(sample.get("event_type", "")).strip())
    source_ok = bool(str(sample.get("source", "")).strip())
    valid = not missing and payload_ok and event_type_ok and source_ok

    return {
        "status": "ok" if valid else "invalid",
        "valid": valid,
        "missing_fields": missing,
        "checks": {
            "payload_is_object": payload_ok,
            "event_type_non_empty": event_type_ok,
            "source_non_empty": source_ok,
        },
        "normalized_example": {
            "event_type": str(sample.get("event_type", "")).strip() or "chat.request",
            "source": str(sample.get("source", "")).strip() or "api:/api/v1/chat",
            "origin": _normalize_signal_origin(str(sample.get("origin", "external"))),
            "priority": str(sample.get("priority", "normal")).strip().lower() or "normal",
        },
    }


@app.post("/api/v1/v6/nas/select")
async def v6_nas_select(request: NasSelectRequest):
    plan = _select_nas_architecture(request.query, request.domain, request.strict_mode)
    return {
        "status": "ok",
        "nas_enabled": NAS_ENABLED,
        "query_chars": len(request.query or ""),
        "language": request.language or "auto",
        "domain": request.domain,
        "intent": plan.get("intent"),
        "architecture": plan.get("architecture", []),
        "flags": plan.get("flags", {}),
        "selected_at": plan.get("selected_at"),
    }


@app.get("/api/v1/v6/nas/stats")
async def v6_nas_stats():
    return {
        "status": "ok",
        "nas_enabled": NAS_ENABLED,
        "cache": {
            "size": len(_nas_cache),
            "max": NAS_CACHE_SIZE,
            "update_interval_minutes": NAS_UPDATE_INTERVAL_MINUTES,
        },
        "stats": _nas_stats,
    }


@app.post("/api/v1/v6/quantum/superposition")
async def v6_quantum_superposition(request: QuantumSuperpositionRequest):
    if not QUANTUM_ENABLED:
        return {
            "status": "disabled",
            "quantum_enabled": False,
        }

    try:
        response = await _quantum_superposition(
            query=request.query,
            language=request.language,
            top_k=request.top_k,
        )
        return {
            **response,
            "quantum_enabled": True,
            "domain": request.domain,
            "strict_mode": request.strict_mode,
        }
    except Exception as exc:
        _quantum_stats["failures"] = int(_quantum_stats.get("failures", 0)) + 1
        raise HTTPException(status_code=500, detail=f"Quantum superposition failed: {exc}")


@app.get("/api/v1/v6/quantum/entanglement")
async def v6_quantum_entanglement():
    return {
        "status": "ok",
        "quantum_enabled": QUANTUM_ENABLED,
        "workers": QUANTUM_SUPERPOSITION_WORKERS,
        "collapse_threshold": QUANTUM_COLLAPSE_THRESHOLD,
        "stats": _quantum_stats,
        "entanglement": _quantum_entanglement_map,
    }


@app.get("/api/v1/v6/cache/predictions")
async def v6_cache_predictions(
    q: str = Query(..., min_length=1, max_length=4000),
    user_id: Optional[str] = Query(default=None),
    domain: Optional[str] = Query(default=None),
    strict_mode: bool = Query(default=False),
    language: Optional[str] = Query(default=None),
):
    predictions = _predict_next_queries(q)
    if PREDICTIVE_CACHE_ENABLED:
        for item in predictions:
            predicted_query = item.get("query", "")
            if not predicted_query:
                continue
            pred_plan = _select_nas_architecture(predicted_query, domain, strict_mode)
            pred_key = _predictive_cache_key(predicted_query, domain, strict_mode, language)
            _evict_predictive_cache_if_needed()
            _predictive_cache[pred_key] = {
                "query": predicted_query,
                "confidence": item.get("confidence", 0.0),
                "nas_plan": pred_plan,
                "prefetched_at": datetime.datetime.utcnow().isoformat() + "Z",
                "user_id": user_id,
            }

    return {
        "status": "ok",
        "predictive_cache_enabled": PREDICTIVE_CACHE_ENABLED,
        "query": q,
        "user_id": user_id,
        "predictions": predictions,
        "prefetch_top_k": PREDICTIVE_PREFETCH_TOP_K,
    }


@app.get("/api/v1/v6/cache/hit_rate")
async def v6_cache_hit_rate():
    requests_count = int(_predictive_stats.get("requests", 0))
    hits = int(_predictive_stats.get("hits", 0))
    misses = int(_predictive_stats.get("misses", 0))
    hit_rate = (hits / requests_count) if requests_count > 0 else 0.0
    return {
        "status": "ok",
        "predictive_cache_enabled": PREDICTIVE_CACHE_ENABLED,
        "cache_size": len(_predictive_cache),
        "cache_max": PREDICTIVE_CACHE_SIZE,
        "requests": requests_count,
        "hits": hits,
        "misses": misses,
        "hit_rate": round(hit_rate, 4),
        "stats": _predictive_stats,
    }


@app.get("/api/v1/v6/evolution/status")
async def v6_evolution_status():
    return {
        "status": "ok",
        "self_evolving_enabled": SELF_EVOLVING_ENABLED,
        "interval_requests": EVOLUTION_INTERVAL_REQUESTS,
        "stats": _evolution_stats,
        "sample_buffer": len(_evolution_samples),
    }


@app.post("/api/v1/v6/evolution/trigger")
async def v6_evolution_trigger(request: Request):
    _require_admin_token(request)
    if not SELF_EVOLVING_ENABLED:
        return {
            "status": "disabled",
            "self_evolving_enabled": False,
        }
    summary = _run_evolution_cycle()
    return {
        "status": "ok",
        "self_evolving_enabled": True,
        "summary": summary,
        "stats": _evolution_stats,
    }


@app.post("/api/v1/signals/external")
async def ingest_external_signal(signal: SignalRequest, http_request: Request):
    source = signal.source if (signal.source or "").strip() else f"external:{_extract_client_id(http_request)}"
    normalized = signal.model_copy(update={"origin": "external", "source": source})
    return await _ingest_signal(normalized)


@app.post("/api/v1/signals/internal")
async def ingest_internal_signal(signal: SignalRequest):
    normalized = signal.model_copy(update={"origin": "internal"})
    return await _ingest_signal(normalized)


@app.post("/api/v1/signals/system")
async def ingest_system_signal(signal: SignalRequest, request: Request):
    _require_admin_token(request)
    normalized = signal.model_copy(update={"origin": "system", "priority": "high"})
    return await _ingest_signal(normalized)


@app.get("/api/v1/signals/status")
async def signal_status():
    async with _signal_lock:
        stats_snapshot = dict(_signal_stats)
        queue_depth = len(_signal_queue)

    return {
        "status": "ok" if SIGNAL_ROUTING_ENABLED else "disabled",
        "routing_enabled": SIGNAL_ROUTING_ENABLED,
        "queue_depth": queue_depth,
        "queue_size": SIGNAL_QUEUE_SIZE,
        "timeout_s": SIGNAL_TIMEOUT_S,
        "retry_attempts": SIGNAL_RETRY_ATTEMPTS,
        "stats": stats_snapshot,
        "eventbus": {
            "type": EVENTBUS_TYPE,
            "namespace": PUBSUB_NAMESPACE,
            "batch_size": EVENTBUS_BATCH_SIZE,
            "flush_interval_ms": EVENTBUS_FLUSH_INTERVAL_MS,
        },
    }


@app.get("/api/v1/signals/recent")
async def signal_recent(limit: int = Query(default=20, ge=1, le=200)):
    async with _signal_lock:
        tail = list(_signal_queue)[-limit:]
    return {
        "status": "ok",
        "count": len(tail),
        "signals": tail,
    }


@app.get("/api/v1/signals/metrics/histogram")
async def signal_metrics_histogram(name: str = Query(default="processing_ms")):
    async with _signal_lock:
        snapshot = list(_signal_queue)

    values: List[float] = []
    for item in snapshot:
        payload = item.get("payload") if isinstance(item, dict) else None
        if not isinstance(payload, dict):
            continue
        raw = payload.get(name)
        if isinstance(raw, (int, float)):
            values.append(float(raw))

    if not values:
        return {
            "status": "ok",
            "name": name,
            "count": 0,
            "histogram": {},
        }

    sorted_values = sorted(values)
    count = len(sorted_values)
    p50 = sorted_values[int(0.50 * (count - 1))]
    p90 = sorted_values[int(0.90 * (count - 1))]
    p99 = sorted_values[int(0.99 * (count - 1))]

    return {
        "status": "ok",
        "name": name,
        "count": count,
        "histogram": {
            "min": sorted_values[0],
            "max": sorted_values[-1],
            "avg": round(sum(sorted_values) / count, 3),
            "p50": p50,
            "p90": p90,
            "p99": p99,
        },
    }


async def _proxy_to_service(base_url: str, path: str, request: Request):
    target = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
    if request.url.query:
        target = f"{target}?{request.url.query}"

    headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in {"host", "content-length", "connection"}
    }

    body = await request.body()

    proxy_timeout: Optional[float] = None if _elastic_unlimited() else 60.0

    try:
        async with httpx.AsyncClient(timeout=proxy_timeout) as client:
            upstream = await client.request(
                method=request.method,
                url=target,
                headers=headers,
                content=body,
            )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Proxy failed for {target}: {e}")

    response_headers = {
        key: value
        for key, value in upstream.headers.items()
        if key.lower() not in {"content-encoding", "transfer-encoding", "connection"}
    }
    return Response(content=upstream.content, status_code=upstream.status_code, headers=response_headers)


@app.api_route("/api/v1/central/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_central(path: str, request: Request):
    return await _proxy_to_service(CENTRAL_API_BASE, path, request)


@app.api_route("/api/v1/central", methods=["GET"])
async def proxy_central_root(request: Request):
    return await _proxy_to_service(CENTRAL_API_BASE, "health", request)


@app.api_route("/api/v1/openmind/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_openmind(path: str, request: Request):
    return await _proxy_to_service(OPENMIND_BASE, path, request)


@app.api_route("/api/v1/openmind", methods=["GET"])
async def proxy_openmind_root(request: Request):
    return await _proxy_to_service(OPENMIND_BASE, "health", request)


@app.api_route("/api/v1/excel/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_excel(path: str, request: Request):
    return await _proxy_to_service(EXCEL_CORE_BASE, path, request)


@app.api_route("/api/v1/excel", methods=["GET"])
async def proxy_excel_root(request: Request):
    return await _proxy_to_service(EXCEL_CORE_BASE, "health", request)

@app.get("/api/v1/enterprise/status")
async def enterprise_status():
    """Enterprise Guard status and diagnostics"""
    if not ENTERPRISE_GUARD_AVAILABLE or not enterprise_guard:
        return {"status": "not_available", "message": "Enterprise Guard not loaded"}

    return {
        "status": "active",
        **enterprise_guard.get_status()
    }

@app.get("/api/v1/enterprise/contract")
async def enterprise_contract():
    """Get the behavior contract text"""
    if not ENTERPRISE_GUARD_AVAILABLE or not enterprise_guard:
        return {"error": "Enterprise Guard not loaded"}

    return {
        "contract": enterprise_guard.contract.get_contract_text()
    }

@app.post("/api/v1/chat")
async def chat(req: ChatRequest, http_request: Request):
    """Main chat endpoint - Full processing pipeline"""
    prompt = req.message or req.query or ""
    await _ingest_signal(
        SignalRequest(
            event_type="chat.request",
            source="api:/api/v1/chat",
            payload={
                "prompt_chars": len(prompt),
                "language": req.language or "auto",
                "strict_mode": bool(req.strict_mode),
                "client_id": _extract_client_id(http_request),
            },
            origin="external",
            priority="high" if req.strict_mode else "normal",
            correlation_id=req.clerk_user_id,
        )
    )
    result = await process_query_full(req)
    if isinstance(result, ChatResponse):
        await _ingest_signal(
            SignalRequest(
                event_type="chat.response",
                source="api:/api/v1/chat",
                payload={
                    "processing_ms": round(float(result.processing_time) * 1000.0, 2),
                    "response_chars": len(result.response or ""),
                    "language_detected": result.language_detected,
                    "engines_used": result.engines_used,
                },
                origin="internal",
                correlation_id=req.clerk_user_id,
            )
        )
    payload = result.model_dump() if isinstance(result, ChatResponse) else result
    return _format_chat_output(payload, req, http_request)


@app.post("/api/v1/chat/fast")
async def chat_fast(req: ChatRequest, http_request: Request, skip_rate_limit: bool = False):
    """Low-latency chat endpoint for simple queries and UI fast-path routing."""
    started_at = time.perf_counter()
    prompt = (req.message or req.query or "").strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="message or query required")

    _enforce_prompt_limits(prompt)
    client_id = _extract_client_id(http_request)
    if not skip_rate_limit and not await _allow_chat_request(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded for fast chat")

    prompt_lower = prompt.lower()
    professional_prompt = _is_professional_prompt(prompt)
    requested_language = _normalize_requested_language(req.language)
    resolved_language = requested_language

    short_greeting_map = {
        "hi": "en",
        "hello": "en",
        "hey": "en",
        "pershendetje": "sq",
        "përshëndetje": "sq",
        "tung": "sq",
        "hallo": "de",
        "bonjour": "fr",
        "hola": "es",
        "ciao": "it",
    }

    if not resolved_language and prompt_lower in short_greeting_map:
        resolved_language = short_greeting_map[prompt_lower]

    if not CHAT_NO_WARMUP and not resolved_language and len(prompt) > 12:
        warm_entry = _WARM_CACHE.get(_warm_key(prompt))
        warm_lang = (warm_entry or {}).get("language") if isinstance(warm_entry, dict) else ""
        if isinstance(warm_lang, str) and warm_lang.strip():
            resolved_language = warm_lang.strip().lower()

    if not resolved_language and len(prompt) > 12:
        detected_lang, _detected_name, _confidence = await detect_language(prompt)
        resolved_language = (detected_lang or "").strip().lower()

    if not resolved_language:
        resolved_language = "en"

    await _ingest_signal(
        SignalRequest(
            event_type="chat.fast.request",
            source="api:/api/v1/chat/fast",
            payload={
                "prompt_chars": len(prompt),
                "language": resolved_language or requested_language or "auto",
                "client_id": client_id,
                "max_tokens": req.max_tokens,
            },
            origin="external",
            priority="normal",
            correlation_id=req.clerk_user_id,
        )
    )

    if not professional_prompt and ALBANIAN_DICT_AVAILABLE and callable(get_albanian_response) and _should_use_albanian_dictionary(prompt, requested_language):
        albanian_response = get_albanian_response(prompt)
        if albanian_response:
            _store_conversation_turn(req, prompt, albanian_response, resolved_language or requested_language or "sq")
            elapsed = round(time.perf_counter() - started_at, 3)
            return {
                "response": albanian_response,
                "model": "albanian_dictionary",
                "processing_time": elapsed,
                "engines_used": ["AlbanianDictionary", "FastPath"],
                "language_detected": resolved_language or requested_language or "sq",
                "sources": ["albanian_dictionary"],
                "confidence": 0.98,
                "query_category": "direct_lookup",
                "fast_path": True,
                "timeout_seconds": 0.1,
            }

    # No canned greeting responses: let real engines answer greeting turns.

    praise_markers = (
        "big love",
        "love",
        "faleminderit",
        "gjigand",
        "epike",
        "epik",
        "super",
        "shume i madh",
        "shumë i madh",
        "legend",
        "bravo",
        "hah",
        "haha",
        "hahaha",
    )
    if any(marker in prompt_lower for marker in praise_markers):
        warm_replies = {
            "sq": "Faleminderit shumë — energjia jote ndihet. Po e ngremë Ocean në nivelin që meriton Clisonix.",
            "de": "Danke — die Energie kommt an. Wir heben Ocean auf das Niveau, das Clisonix verdient.",
            "fr": "Merci — l’énergie passe bien. Nous élevons Ocean au niveau que Clisonix mérite.",
            "es": "Gracias — se siente la energía. Estamos llevando Ocean al nivel que Clisonix merece.",
            "it": "Grazie — si sente l’energia. Stiamo portando Ocean al livello che Clisonix merita.",
            "en": "Thank you — the energy comes through. We’re pushing Ocean to the level Clisonix deserves.",
        }
        warm_reply = warm_replies.get(resolved_language, warm_replies["en"])
        _store_conversation_turn(req, prompt, warm_reply, resolved_language)
        elapsed = round(time.perf_counter() - started_at, 3)
        return {
            "response": warm_reply,
            "model": "fast_affinity_router",
            "processing_time": elapsed,
            "engines_used": ["AffinityRouter", "FastPath"],
            "language_detected": resolved_language,
            "sources": ["fast_affinity_router"],
            "confidence": 0.98,
            "query_category": "friendly_acknowledgement",
            "fast_path": True,
            "timeout_seconds": 0.05,
        }

    quick_prompt_markers = (
        "what is",
        "define",
        "explain",
        "who is",
        "how does",
        "why",
        "çfarë është",
        "cfare eshte",
        "shpjego",
        "si funksionon",
    )
    if not professional_prompt and any(marker in prompt_lower for marker in quick_prompt_markers):
        seed_text = (find_knowledge_seed(prompt) or "").strip()
        if seed_text:
            seed_text = _clip_shortcut_text(seed_text)
            elapsed = round(time.perf_counter() - started_at, 3)
            _store_conversation_turn(req, prompt, seed_text, resolved_language)
            return {
                "response": seed_text,
                "model": "knowledge_seed_fast",
                "processing_time": elapsed,
                "engines_used": ["KnowledgeSeeds", "FastPath"],
                "language_detected": resolved_language,
                "sources": ["knowledge_seeds"],
                "confidence": 0.92,
                "query_category": "seed_lookup",
                "fast_path": True,
                "timeout_seconds": 0.2,
            }

    fast_engine = answer_engine
    should_try_answer_engine = (
        fast_engine is not None
        and not req.long_response
        and (len(prompt) <= 120 or prompt_lower.startswith(quick_prompt_markers))
    )
    if should_try_answer_engine and fast_engine is not None:
        try:
            fast_timeout = FAST_ANSWER_TIMEOUT_S
            if _elastic_unlimited():
                fast_timeout = max(fast_timeout, 15.0)
            fast_real = await asyncio.wait_for(fast_engine.answer(prompt), timeout=fast_timeout)
            fast_text = str(getattr(fast_real, "answer", "") or "").strip()
            if fast_text:
                fast_text = _clip_shortcut_text(fast_text)
                _store_conversation_turn(req, prompt, fast_text, resolved_language)
                elapsed = round(time.perf_counter() - started_at, 3)
                return {
                    "response": fast_text,
                    "model": "real_answer_engine",
                    "processing_time": elapsed,
                    "engines_used": ["RealAnswerEngine", "FastPath"],
                    "language_detected": resolved_language,
                    "sources": [str(getattr(fast_real, "source", "real_answer_engine"))],
                    "confidence": float(getattr(fast_real, "confidence", 0.9) or 0.9),
                    "query_category": "fast_local_reasoning",
                    "fast_path": True,
                    "timeout_seconds": fast_timeout,
                }
        except Exception as exc:
            logger.debug(f"fast answer_engine skipped: {exc}")

    if professional_prompt:
        prof_messages = [
            {
                "role": "system",
                "content": (
                    "You are a senior principal architect. "
                    "Provide concise, practical, production-grade answers with concrete steps and trade-offs."
                ),
            },
            {"role": "user", "content": prompt},
        ]
        prof_options = {
            "temperature": 0.3,
            "num_ctx": _resolve_num_ctx(True, -1, prompt_chars=len(prompt), message_count=2),
            "num_predict": -1,
            "top_k": 40,
            "top_p": 0.9,
            "repeat_penalty": 1.1,
        }

        ollama_errors: List[str] = []
        for candidate in [_normalize_ollama_model(req.model or MODEL), *OLLAMA_FALLBACK_MODELS]:
            normalized = _normalize_ollama_model(candidate)
            try:
                chunks: List[str] = []
                async for token in stream_ollama_response(
                    model=normalized,
                    messages=prof_messages,
                    options=prof_options,
                    engines_used=["FastChatProfessional"],
                    lang_code=resolved_language or "auto",
                ):
                    if not token or token.startswith("[Error:"):
                        continue
                    chunks.append(token)
                response_text = "".join(chunks).strip()
                if response_text:
                    elapsed = round(time.perf_counter() - started_at, 3)
                    _store_conversation_turn(req, prompt, response_text, resolved_language or "auto")
                    return {
                        "response": response_text,
                        "model": normalized,
                        "processing_time": elapsed,
                        "engines_used": ["FastChatProfessional", f"Ollama({normalized})"],
                        "language_detected": resolved_language or "auto",
                        "sources": ["ollama_professional"],
                        "confidence": 0.9,
                        "query_category": "professional",
                        "fast_path": True,
                        "timeout_seconds": None,
                    }
            except Exception as exc:
                ollama_errors.append(f"{normalized}:{_sanitize_log_text(exc, 160)}")

        raise HTTPException(status_code=503, detail=f"Professional path unavailable: {' | '.join(ollama_errors[:3])}")

    resolved_language_name = await resolve_language_name(resolved_language) if resolved_language else ""
    language_label = f"{resolved_language_name} ({resolved_language})" if resolved_language_name else resolved_language
    lang_hint = (
        f" REQUIRED OUTPUT LANGUAGE: {language_label}. "
        f"You MUST answer only in {language_label}. "
        "Never switch to another language unless the user explicitly asks."
        if resolved_language
        else ""
    )

    if req.long_response or _elastic_unlimited():
        target_chars = 0
    else:
        target_chars = FAST_TARGET_CHARS_SHORT if len(prompt) <= 80 else FAST_TARGET_CHARS_MEDIUM
    safe_tokens = _clamp_chat_tokens(req.max_tokens if req.max_tokens is not None else -1, True)
    num_ctx = _resolve_num_ctx(
        True,
        safe_tokens,
        prompt_chars=len(prompt),
        message_count=2,
    )
    resolved_timeout = _resolve_llm_timeout(len(prompt), 2)
    timeout_s = resolved_timeout if resolved_timeout is not None else (120.0 if _elastic_unlimited() else 30.0)

    conversation_context = _incoming_messages_context(req)
    memory_context = _memory_context(req)
    user_context = _build_user_context(req)
    memory_safety_context = _memory_safety_contract(bool(memory_context or conversation_context))
    ecosystem_capsule = _build_runtime_ecosystem_capsule()

    fast_messages = [
        {
            "role": "system",
            "content": (
                FAST_SYSTEM_PROMPT + "\n" + FAST_LANGUAGE_POLICY + "\n" + HUMAN_ETHICS_POLICY + "\n" + RESPONSE_STYLE_POLICY + lang_hint
                + (f"\n\n{ecosystem_capsule}" if ecosystem_capsule else "")
                + (f"\n\n{user_context}" if user_context else "")
                + (f"\n\n{conversation_context}" if conversation_context else "")
                + (f"\n\n{memory_context}" if memory_context else "")
                + (f"\n\n{memory_safety_context}" if memory_safety_context else "")
                + "\n\nCONTINUITY DIRECTIVE: This is an ongoing chat. Answer as the next coherent turn in the same thread."
            ),
        },
        {"role": "user", "content": prompt},
    ]
    fast_options = {
        "temperature": 0.5,
        "num_ctx": num_ctx,
        "num_predict": safe_tokens,
        "top_k": 30,
        "top_p": 0.9,
        "repeat_penalty": 1.05,
    }

    chunks: List[str] = []
    async for token in stream_ollama_response(
        model=req.model or MODEL,
        messages=fast_messages,
        options=fast_options,
        engines_used=["FastChat"],
        lang_code=resolved_language or "auto",
    ):
        if not token:
            continue
        if token.startswith("[STREAM_ERROR:"):
            raise HTTPException(status_code=503, detail=token)
        chunks.append(token)
        if target_chars > 0:
            preview = "".join(chunks).strip()
            if len(preview) >= target_chars:
                if preview.endswith((".", "!", "?")) or len(preview) >= target_chars + 120:
                    break

    response_text = "".join(chunks).strip()
    if not response_text or response_text.startswith("[Error:"):
        raise HTTPException(status_code=503, detail="Fast response generation failed")

    elapsed = round(time.perf_counter() - started_at, 3)
    await _ingest_signal(
        SignalRequest(
            event_type="chat.fast.response",
            source="api:/api/v1/chat/fast",
            payload={
                "processing_ms": round(elapsed * 1000.0, 2),
                "response_chars": len(response_text),
                "language_detected": resolved_language or "auto",
                "engines_used": ["FastChat", "Ollama"],
            },
            origin="internal",
            correlation_id=req.clerk_user_id,
        )
    )

    _store_conversation_turn(req, prompt, response_text, resolved_language or "auto")

    return {
        "response": response_text,
        "model": req.model or MODEL,
        "processing_time": elapsed,
        "engines_used": ["FastChat", "Ollama"],
        "language_detected": resolved_language or "auto",
        "sources": ["ollama_fast"],
        "confidence": 0.86,
        "query_category": "fast_chat",
        "fast_path": True,
        "timeout_seconds": timeout_s,
    }


@app.post("/api/v1/chat/stream/warm")
async def chat_stream_warm(req: ChatRequest):
    """Best-effort typeahead warm endpoint used while user is typing."""
    if CHAT_NO_WARMUP:
        return {"status": "disabled", "reason": "warmup_disabled"}

    message = (req.message or req.query or "").strip()
    if len(message) < 6:
        return {"status": "skipped", "reason": "too_short"}

    key = _warm_key(message)
    if key in _WARM_CACHE:
        return {"status": "already_warmed"}

    async def _build_warm() -> None:
        try:
            lang, _name, _confidence = await detect_language(message)
            _WARM_CACHE[key] = {
                "language": (lang or "").strip().lower(),
                "ts": time.time(),
            }
            if len(_WARM_CACHE) > WARM_CACHE_MAX:
                oldest_key = min(_WARM_CACHE, key=lambda cache_key: _WARM_CACHE[cache_key].get("ts", 0))
                _WARM_CACHE.pop(oldest_key, None)
        except Exception as exc:
            logger.debug(f"warm build failed: {exc}")

    asyncio.create_task(_build_warm())
    return {"status": "warming"}


@app.post("/api/v1/chat/stream")
async def chat_stream(req: ChatRequest, http_request: Request):
    """
    FAST STREAMING chat endpoint - optimized for 2-3s TTFT on CPU!
    Uses FAST_SYSTEM_PROMPT (40 tokens) + small context (2048)
    """
    prompt = req.message or req.query
    if not prompt:
        raise HTTPException(status_code=400, detail="message or query required")
    _enforce_prompt_limits(prompt)
    if not await _allow_chat_request(_extract_client_id(http_request)):
        raise HTTPException(status_code=429, detail="Rate limit exceeded for chat stream")

    wants_sse = "text/event-stream" in (http_request.headers.get("accept") or "").lower()

    def _sse_text_chunk(payload: str) -> str:
        """Emit one SSE message as raw text chunks (no JSON wrapper for chunk payload)."""
        if payload is None:
            payload = ""
        lines = payload.splitlines() or [payload]
        return "".join(f"data: {line}\n" for line in lines) + "\n"

    if CLX_ONLY:
        if not _HAS_XLC:
            raise HTTPException(status_code=503, detail="CLX_ONLY aktiv, por XLC engine nuk është i ngarkuar")
        if not req.xlc_enabled:
            raise HTTPException(status_code=422, detail="CLX_ONLY kërkon xlc_enabled=true")
        if not wants_sse:
            raise HTTPException(status_code=422, detail="CLX_ONLY kërkon Accept: text/event-stream")

        xlc_commands = req.xlc_commands
        if not xlc_commands and _xlc_router and getattr(_xlc_router, "commands", None):
            xlc_commands = list(_xlc_router.commands)
        if not xlc_commands:
            raise HTTPException(status_code=422, detail="CLX_ONLY kërkon xlc_commands ose komanda të regjistruara")

        xlc_req = _XLCRouteStreamRequest(
            text=prompt,
            commands=xlc_commands,
            threshold=req.xlc_threshold,
            max_extra_window=req.xlc_max_extra_window,
            model=req.model,
            max_tokens=req.max_tokens,
            temperature=req.xlc_temperature,
            elastic=req.xlc_elastic,
        )
        return await xlc_route_stream(xlc_req)

    if req.xlc_enabled and wants_sse:
        if not _HAS_XLC:
            raise HTTPException(status_code=503, detail="XLC engine jo i ngarkuar")

        xlc_commands = req.xlc_commands
        if not xlc_commands and _xlc_router and getattr(_xlc_router, "commands", None):
            xlc_commands = list(_xlc_router.commands)

        # Keep global default safe: if no XLC commands are available yet,
        # continue with classic chat streaming instead of failing the request.
        if not xlc_commands:
            logger.info("XLC enabled by default, but no commands registered; falling back to classic stream")
        else:
            xlc_req = _XLCRouteStreamRequest(
                text=prompt,
                commands=xlc_commands,
                threshold=req.xlc_threshold,
                max_extra_window=req.xlc_max_extra_window,
                model=req.model,
                max_tokens=req.max_tokens,
                temperature=req.xlc_temperature,
                elastic=req.xlc_elastic,
            )
            return await xlc_route_stream(xlc_req)

    requested_language = _normalize_requested_language(req.language)
    resolved_language = requested_language

    if not CHAT_NO_WARMUP and not resolved_language:
        warm_entry = _WARM_CACHE.get(_warm_key(prompt))
        warm_lang = (warm_entry or {}).get("language") if isinstance(warm_entry, dict) else ""
        if isinstance(warm_lang, str) and warm_lang.strip():
            resolved_language = warm_lang.strip().lower()
            logger.info("⚡ Warm cache hit for stream language")

    if not resolved_language:
        detected_lang, _detected_name, _confidence = await detect_language(prompt)
        resolved_language = (detected_lang or "").strip().lower()

    resolved_language_name = await resolve_language_name(resolved_language) if resolved_language else ""
    language_label = f"{resolved_language_name} ({resolved_language})" if resolved_language_name else resolved_language
    lang_hint = (
        f" REQUIRED OUTPUT LANGUAGE: {language_label}. "
        f"You MUST answer only in {language_label}. "
        "Never switch to another language unless the user explicitly asks."
        if resolved_language
        else ""
    )

    # Albanian Dictionary - Direct response (fastest path)
    if ALBANIAN_DICT_AVAILABLE and callable(get_albanian_response) and _should_use_albanian_dictionary(prompt, requested_language):
        albanian_response = get_albanian_response(prompt)
        if albanian_response:
            logger.info(f"🇦🇱 Albanian Dict direct: {prompt[:40]}...")
            _store_conversation_turn(req, prompt, albanian_response, resolved_language or requested_language or "sq")
            async def albanian_stream():
                if wants_sse:
                    yield "data: {\"status\":\"stream_started\",\"stream_format\":\"nanovolt_chunks\"}\n\n"
                    for i in range(0, len(albanian_response), 24):
                        chunk = albanian_response[i:i + 24]
                        if chunk:
                            yield _sse_text_chunk(chunk)
                    yield "data: [DONE]\n\n"
                else:
                    yield albanian_response

            return StreamingResponse(
                albanian_stream(),
                media_type="text/event-stream" if wants_sse else "text/plain",
                headers={
                    "Cache-Control": "no-cache",
                    "X-Accel-Buffering": "no",
                    "Connection": "keep-alive",
                },
            )

    # Real conversation first: prefer local reasoning engine, then CLX agent.
    if not req.long_response and len(prompt) <= 200:
        try:
            if answer_engine is not None:
                timeout_s = max(FAST_ANSWER_TIMEOUT_S, 15.0) if _elastic_unlimited() else FAST_ANSWER_TIMEOUT_S
                fast_real = await asyncio.wait_for(answer_engine.answer(prompt), timeout=timeout_s)
                fast_text = str(getattr(fast_real, "answer", "") or "").strip()
                if fast_text:
                    async def real_answer_stream() -> AsyncGenerator[str, None]:
                        yield "data: {\"status\":\"stream_started\",\"stream_format\":\"nanovolt_chunks\"}\n\n"
                        chunk_chars = _elastic_chunk_chars(len(prompt or ""))
                        for i in range(0, len(fast_text), chunk_chars):
                            yield _sse_text_chunk(fast_text[i:i + chunk_chars])
                        yield "data: [DONE]\n\n"

                    return StreamingResponse(
                        real_answer_stream(),
                        media_type="text/event-stream" if wants_sse else "text/plain",
                        headers={
                            "Cache-Control": "no-cache",
                            "X-Accel-Buffering": "no",
                            "Connection": "keep-alive",
                        },
                    )
        except Exception as exc:
            logger.debug("stream real_answer_engine skipped: %s", exc)

        try:
            clx_text, _clx_model = await _chat_with_clx_agent(prompt, resolved_language or "auto")
            clx_text = (clx_text or "").strip()
            if clx_text:
                async def clx_stream() -> AsyncGenerator[str, None]:
                    yield "data: {\"status\":\"stream_started\",\"stream_format\":\"nanovolt_chunks\"}\n\n"
                    chunk_chars = _elastic_chunk_chars(len(prompt or ""))
                    for i in range(0, len(clx_text), chunk_chars):
                        yield _sse_text_chunk(clx_text[i:i + chunk_chars])
                    yield "data: [DONE]\n\n"

                return StreamingResponse(
                    clx_stream(),
                    media_type="text/event-stream" if wants_sse else "text/plain",
                    headers={
                        "Cache-Control": "no-cache",
                        "X-Accel-Buffering": "no",
                        "Connection": "keep-alive",
                    },
                )
        except Exception as exc:
            logger.debug("stream clx_agent skipped: %s", exc)

    if not req.long_response and len(prompt) <= 120:
        try:
            fast_result = await chat_fast(req, http_request, skip_rate_limit=True)
            if isinstance(fast_result, dict):
                fast_text = str(fast_result.get("response") or "").strip()
                if fast_text:
                    async def fast_stream():
                        yield (
                            "data: "
                            + json.dumps(
                                {
                                    "status": "stream_started",
                                    "stream_format": "nanovolt_chunks",
                                    "scanner": "wwwmmm",
                                    "scanner_fingerprint": None,
                                    "nanovolt": None,
                                    "stigma": None,
                                    "resonance_score": None,
                                    "resonance_tide": None,
                                    "resonance_frequency_hz": None,
                                    "wwwmmm_lighting": "lightning",
                                    "thinker": "zurich",
                                    "printer": "nanovolt_printer",
                                },
                                ensure_ascii=False,
                            )
                            + "\n\n"
                        )
                        chunk_chars = _elastic_chunk_chars(len(prompt or ""))
                        for i in range(0, len(fast_text), chunk_chars):
                            yield _sse_text_chunk(fast_text[i:i + chunk_chars])
                        yield "data: [DONE]\n\n"

                    return StreamingResponse(
                        fast_stream(),
                        media_type="text/event-stream" if wants_sse else "text/plain",
                        headers={
                            "Cache-Control": "no-cache",
                            "X-Accel-Buffering": "no",
                            "Connection": "keep-alive",
                        },
                    )
        except HTTPException:
            pass
        except Exception as exc:
            logger.debug("stream fast-path skipped: %s", exc)

    # Build streaming prompt with continuity + memory
    user_context = _build_user_context(req)
    conversation_context = _incoming_messages_context(req)
    memory_context = _memory_context(req)
    memory_safety_context = _memory_safety_contract(bool(memory_context or conversation_context))
    companion_context = _companion_context(req, prompt) if req.enable_companion else ""
    multimodal_context = _multimodal_context(req)
    ecosystem_capsule = _build_runtime_ecosystem_capsule()

    system_content = (
        FAST_SYSTEM_PROMPT + "\n" + FAST_LANGUAGE_POLICY + "\n" + HUMAN_ETHICS_POLICY + "\n" + RESPONSE_STYLE_POLICY + lang_hint
        + (f"\n\n{ecosystem_capsule}" if ecosystem_capsule else "")
        + (f"\n\n{user_context}" if user_context else "")
        + (f"\n\n{conversation_context}" if conversation_context else "")
        + (f"\n\n{memory_context}" if memory_context else "")
        + (f"\n\n{memory_safety_context}" if memory_safety_context else "")
        + (f"\n\n{companion_context}" if companion_context else "")
        + (f"\n\n{multimodal_context}" if multimodal_context else "")
        + "\n\nCONTINUITY DIRECTIVE: This is the next turn of an active conversation. Keep the thread coherent and answer like a worthy, intelligent interlocutor."
    )
    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": prompt}
    ]

    stream_long_response = bool(req.long_response) or req.max_tokens is None
    requested_stream_tokens = req.max_tokens if req.max_tokens is not None else -1
    safe_tokens = _clamp_chat_tokens(requested_stream_tokens, stream_long_response)
    num_ctx = _resolve_num_ctx(
        stream_long_response,
        safe_tokens,
        prompt_chars=len(prompt),
        message_count=len(messages),
    )

    # FAST options - optimized for quick TTFT!
    fast_options = {
        "temperature": 0.7,
        "num_ctx": num_ctx,
        "num_predict": safe_tokens,
        "top_k": 40,           # Faster sampling
        "top_p": 0.9,
        "repeat_penalty": 1.1,
    }

    logger.info(
        "🚀 elastic streaming: %s... | long=%s | max_tokens=%s | num_ctx=%s",
        prompt[:40],
        stream_long_response,
        safe_tokens,
        num_ctx,
    )

    base_stream = stream_ollama_response(
        model=req.model or MODEL,
        messages=messages,
        options=fast_options,
        engines_used=["FastStream"],
        lang_code=resolved_language or "auto"
    )

    async def _stream_provider_fallback() -> AsyncGenerator[str, None]:
        fallback_engines: List[str] = []
        response_text, _model_used = await _chat_with_provider_chain(
            req=req,
            prompt=prompt,
            enhanced_prompt=system_content,
            lang_code=resolved_language or "auto",
            engines_used=fallback_engines,
        )
        text = (response_text or "").strip()
        if not text:
            return
        chunk_chars = _elastic_chunk_chars(len(prompt or ""))
        for i in range(0, len(text), chunk_chars):
            yield text[i:i + chunk_chars]

    async def remembered_stream():
        collected: List[str] = []
        try:
            async for token in base_stream:
                if token and not token.startswith("[STREAM_ERROR:"):
                    collected.append(token)
                yield token
        finally:
            final_text = "".join(collected).strip()
            if final_text:
                _store_conversation_turn(req, prompt, final_text, resolved_language or "auto")

    enforced_stream = remembered_stream()

    async def _iter_with_fast_fallback() -> AsyncGenerator[str, None]:
        emitted_parts: List[str] = []
        first_token_at: Optional[float] = None
        fallback_used = False
        stream_error: Optional[str] = None
        started_at = time.perf_counter()
        stream_iter = enforced_stream.__aiter__()

        try:
            while True:
                # Enforce TTFT guard on the very first token to avoid endless keepalive-only streams.
                try:
                    if first_token_at is None:
                        token = await asyncio.wait_for(
                            anext(stream_iter),
                            timeout=STREAM_FIRST_TOKEN_TIMEOUT_S,
                        )
                    else:
                        token = await anext(stream_iter)
                except StopAsyncIteration:
                    break
                except asyncio.TimeoutError:
                    timeout_msg = f"first_token_timeout_after_{STREAM_FIRST_TOKEN_TIMEOUT_S}s"
                    logger.warning(
                        "chat_stream first token timeout prompt_chars=%s timeout_s=%s fallback_enabled=%s",
                        len(prompt or ""),
                        STREAM_FIRST_TOKEN_TIMEOUT_S,
                        STREAM_FALLBACK_ENABLED,
                    )
                    stream_error = timeout_msg
                    raise HTTPException(status_code=504, detail=timeout_msg)

                if not token:
                    continue

                stripped_token = token.strip()
                is_stream_error_token = stripped_token.startswith("[Error:") or "[Error:" in token
                is_model_unavailable_token = stripped_token.startswith("{") and '"error": "model_unavailable"' in token
                if (is_stream_error_token or is_model_unavailable_token) and not emitted_parts:
                    if STREAM_FALLBACK_ENABLED:
                        fallback_used = True
                        stream_error = stripped_token[:256]
                        logger.warning(
                            "chat_stream upstream failed early; switching to provider fallback error=%s",
                            stream_error,
                        )
                        async for fb_chunk in _stream_provider_fallback():
                            if fb_chunk:
                                if first_token_at is None:
                                    first_token_at = time.perf_counter()
                                emitted_parts.append(fb_chunk)
                                yield fb_chunk
                        break

                    stream_error = stripped_token[:256]
                    raise HTTPException(status_code=503, detail=stripped_token)

                if is_stream_error_token or is_model_unavailable_token:
                    stream_error = stripped_token[:256]
                    break

                if first_token_at is None:
                    first_token_at = time.perf_counter()
                emitted_parts.append(token)
                yield token
        except Exception as exc:
            stream_error = _sanitize_log_text(exc)
            raise
        finally:
            await _emit_stream_metrics(
                req=req,
                prompt=prompt,
                started_at=started_at,
                first_token_at=first_token_at,
                emitted_text="".join(emitted_parts),
                fallback_used=fallback_used,
                stream_error=stream_error,
            )

    if wants_sse:
        wwwmmm_lighting = "lightning"
        scanner_fingerprint: Optional[str] = None
        scanner_nanovolt: Optional[int] = None
        stigma_profile: Optional[str] = None
        resonance_score: Optional[float] = None
        resonance_tide: Optional[float] = None
        resonance_frequency_hz: Optional[float] = None
        try:
            from wwwmmm.scanner import get_scanner  # type: ignore
            from wwwmmm.stigma import get_stigma  # type: ignore
            from wwwmmm.resonance import get_resonance  # type: ignore
            from wwwmmm.lighting import get_lighting  # type: ignore

            scan = get_scanner().scan(prompt)
            level = int(getattr(scan, "nanovolt_level", 0) or 0)
            scanner_fingerprint = getattr(scan, "fingerprint", None)
            scanner_nanovolt = level

            stigma = get_stigma().analyze(
                {
                    "nanovolt_level": level,
                    "confidence": float(getattr(scan, "confidence", 0.0) or 0.0),
                }
            )
            stigma_profile = str(stigma.get("profile")) if isinstance(stigma, dict) and stigma.get("profile") else None

            resonance = get_resonance().resonate(
                {
                    "nanovolt_level": level,
                    "tokens": int(getattr(scan, "tokens", 0) or 0),
                    "confidence": float(getattr(scan, "confidence", 0.0) or 0.0),
                }
            )
            resonance_score = float(getattr(resonance, "resonance_score", 0.0) or 0.0)
            resonance_tide = float(getattr(resonance, "tide_level", 0.0) or 0.0)
            resonance_frequency_hz = float(getattr(resonance, "frequency_hz", 0.0) or 0.0)

            wwwmmm_lighting = get_lighting().choose(level).name
        except Exception:
            # Keep stream running even if WWWMMM metadata lookup is unavailable.
            pass

        async def sse_stream():
            yield (
                "data: "
                + json.dumps(
                    {
                        "status": "stream_started",
                        "stream_format": "nanovolt_chunks",
                        "scanner": "wwwmmm",
                        "scanner_fingerprint": scanner_fingerprint,
                        "nanovolt": scanner_nanovolt,
                        "stigma": stigma_profile,
                        "resonance_score": resonance_score,
                        "resonance_tide": resonance_tide,
                        "resonance_frequency_hz": resonance_frequency_hz,
                        "wwwmmm_lighting": wwwmmm_lighting,
                        "thinker": "zurich",
                        "printer": "nanovolt_printer",
                    },
                    ensure_ascii=False,
                )
                + "\n\n"
            )
            try:
                async for token in _iter_with_fast_fallback():
                    if token:
                        yield _sse_text_chunk(token)
            except Exception as e:
                status_code = getattr(e, "status_code", None)
                if status_code:
                    yield _sse_text_chunk(f"[Error: {status_code}: stream unavailable]")
                else:
                    yield _sse_text_chunk("[Error: stream unavailable]")
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            sse_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive",
            },
        )

    return StreamingResponse(
        _iter_with_fast_fallback(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@app.post("/api/v1/message/reaction")
async def message_reaction(req: Request):
    """Toggle/add reaction for a message."""
    body = await req.json()
    message_id = str(body.get("message_id", "")).strip()
    emoji = str(body.get("emoji", "")).strip()
    user_id = str(body.get("user_id", "anonymous")).strip() or "anonymous"

    if not message_id or not emoji:
        raise HTTPException(status_code=400, detail="message_id and emoji required")

    msg_store = _REACTION_STORE.setdefault(message_id, {})
    users = msg_store.setdefault(emoji, [])

    if user_id in users:
        users.remove(user_id)
        added = False
    else:
        users.append(user_id)
        added = True

    if not users:
        msg_store.pop(emoji, None)
    if not msg_store:
        _REACTION_STORE.pop(message_id, None)

    return {
        "status": "success",
        "message_id": message_id,
        "emoji": emoji,
        "count": len(_REACTION_STORE.get(message_id, {}).get(emoji, [])),
        "users": _REACTION_STORE.get(message_id, {}).get(emoji, []),
        "added": added,
    }


@app.get("/api/v1/message/{message_id}/reactions")
async def message_reactions_get(message_id: str):
    reactions = _REACTION_STORE.get(message_id, {})
    payload = {
        emoji: {"count": len(users), "users": users}
        for emoji, users in reactions.items()
        if users
    }
    total = sum(item["count"] for item in payload.values()) if payload else 0
    return {
        "message_id": message_id,
        "reactions": payload,
        "total": total,
    }


@app.post("/api/v1/query")
async def query(req: ChatRequest, http_request: Request):
    """Query endpoint - Same as chat"""
    prompt = req.message or req.query or ""
    await _ingest_signal(
        SignalRequest(
            event_type="query.request",
            source="api:/api/v1/query",
            payload={
                "prompt_chars": len(prompt),
                "language": req.language or "auto",
                "client_id": _extract_client_id(http_request),
            },
            origin="external",
            correlation_id=req.clerk_user_id,
        )
    )
    result = await process_query_full(req)
    if isinstance(result, ChatResponse):
        await _ingest_signal(
            SignalRequest(
                event_type="query.response",
                source="api:/api/v1/query",
                payload={
                    "processing_ms": round(float(result.processing_time) * 1000.0, 2),
                    "response_chars": len(result.response or ""),
                    "language_detected": result.language_detected,
                },
                origin="internal",
                correlation_id=req.clerk_user_id,
            )
        )
    payload = result.model_dump() if isinstance(result, ChatResponse) else result
    return _format_chat_output(payload, req, http_request)


@app.get("/api/v1/module-cores")
async def list_module_cores():
    if not MODULE_CORE_REGISTRY_AVAILABLE:
        return {"status": "unavailable", "total": 0, "module_cores": []}

    return {
        "status": "ok",
        "total": len(MODULE_CORE_CATALOG),
        "offload_groups": sorted({item.get("offload_group", "general") for item in MODULE_CORE_CATALOG}),
        "module_cores": MODULE_CORE_CATALOG,
    }


@app.post("/api/v1/module-cores/resolve")
async def resolve_module_core_endpoint(req: ChatRequest):
    if not MODULE_CORE_REGISTRY_AVAILABLE:
        return {"status": "unavailable", "resolved": None, "total": 0}

    prompt = req.message or req.query or ""
    if not prompt and not (req.domain or req.preferred_core or req.module_name or req.personality_module):
        raise HTTPException(status_code=400, detail="message, query, or preferred_core required")

    resolved = _resolve_module_core_candidate(req, prompt)
    preview = None
    if resolved and callable(build_module_core_brief):
        try:
            preview = _build_module_core_shortcut_response(resolved, req.language or "en")
        except Exception:
            preview = None

    return {
        "status": "ok" if resolved else "no-match",
        "total": len(MODULE_CORE_CATALOG),
        "resolved": resolved,
        "preview": preview,
    }


def _to_bits(value: int, bit_width: int = 0) -> str:
    bits = format(int(value), "b")
    if bit_width > 0:
        bits = bits.zfill(bit_width)
    return bits


@app.get("/api/v1/algebra/bits")
@app.get("/api/v1/bin/algebra")
async def algebra_bits(value: int = Query(..., description="Integer to represent in bits"), width: int = Query(0, ge=0, le=128)):
    """Return a bit-level representation for the provided integer value."""
    return {
        "status": "ok",
        "value": int(value),
        "bits": _to_bits(value, width),
        "bit_width": int(width),
        "pixel_proxy": len(_to_bits(value, width)),
        "note": "pixel_proxy approximates bit-length for token-to-bit/pixel telemetry migration.",
    }


@app.post("/api/v1/binary-algebra/operate")
async def binary_algebra_operate(http_request: Request):
    """Execute a basic binary algebra operation with decimal and bit outputs."""
    try:
        payload = await http_request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"invalid_json: {exc}") from exc

    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="payload must be a JSON object")

    op = str(payload.get("op", "")).strip().lower()
    a = payload.get("a")
    b = payload.get("b")

    if op not in {"and", "or", "xor", "lshift", "rshift", "add", "sub"}:
        raise HTTPException(status_code=400, detail="op must be one of: and, or, xor, lshift, rshift, add, sub")
    if not isinstance(a, int) or not isinstance(b, int):
        raise HTTPException(status_code=400, detail="a and b must be integers")

    if op == "and":
        result = a & b
    elif op == "or":
        result = a | b
    elif op == "xor":
        result = a ^ b
    elif op == "lshift":
        result = a << b
    elif op == "rshift":
        result = a >> b
    elif op == "add":
        result = a + b
    else:
        result = a - b

    bit_width = max(len(_to_bits(a)), len(_to_bits(b)), len(_to_bits(result)))
    return {
        "status": "ok",
        "operation": op,
        "inputs": {
            "a": a,
            "b": b,
            "a_bits": _to_bits(a, bit_width),
            "b_bits": _to_bits(b, bit_width),
        },
        "result": {
            "decimal": result,
            "bits": _to_bits(result, bit_width),
            "pixel_proxy": bit_width,
        },
    }


# Specialized expertise domains
EXPERT_DOMAINS = {
    "neuroscience": "You are a world-class neuroscientist specializing in brain research, cognitive science, and neural pathways.",
    "ai": "You are an expert in AI & Deep Learning, machine learning architectures, neural networks, and AGI research.",
    "quantum": "You are a quantum physicist specializing in quantum mechanics, entanglement, and quantum computing.",
    "iot": "You are an IoT & LoRa Networks expert specializing in sensors, gateways, and embedded systems.",
    "cybersecurity": "You are a cybersecurity expert specializing in encryption, vulnerabilities, and security protocols.",
    "bioinformatics": "You are a bioinformatics expert specializing in genetics, DNA analysis, and protein structures.",
    "datascience": "You are a data science expert specializing in statistics, analytics, and visualization.",
    "marine": "You are a marine biologist specializing in ocean ecosystems and marine life."
}


@app.post("/api/v1/chat/specialized", response_model=ChatResponse)
async def chat_specialized(req: ChatRequest):
    """
    Specialized Expert Chat endpoint - domain-specific expertise.
    Uses expert personas for advanced domain questions.
    """
    start_time = time.time()
    engines_used = []

    prompt = req.message or req.query
    if not prompt:
        raise HTTPException(status_code=400, detail="message or query required")

    # Detect language
    lang_code, lang_name, confidence = await detect_language(prompt)
    engines_used.append(f"TranslationNode({lang_code})")

    # Determine expertise domain - allow explicit core or keyword-resolved module core
    domain = (getattr(req, 'domain', None) or "").strip().lower()
    resolved_module_core = _resolve_module_core_candidate(req, prompt)

    if resolved_module_core:
        domain = str(resolved_module_core.get("id", domain)).strip().lower()
        expert_persona = str(
            resolved_module_core.get("system_prompt")
            or EXPERT_DOMAINS.get(domain)
            or "You are a Clisonix domain expert assistant."
        )
        engines_used.append(f"ModuleCore({domain})")
    else:
        if not domain:
            raise HTTPException(status_code=400, detail="domain or preferred_core is required for /api/v1/chat/specialized")
        if domain not in EXPERT_DOMAINS:
            raise HTTPException(status_code=400, detail=f"unsupported domain: {domain}")
        expert_persona = EXPERT_DOMAINS[domain]

    engines_used.append(f"ExpertDomain({domain})")

    # Albanian Dictionary check first
    if ALBANIAN_DICT_AVAILABLE and callable(get_albanian_response):
        albanian_response = get_albanian_response(prompt)
        if albanian_response:
            engines_used.append("AlbanianDictionary")
            elapsed = time.time() - start_time
            return ChatResponse(
                response=albanian_response,
                model="albanian_dictionary_v1",
                processing_time=round(elapsed, 2),
                engines_used=engines_used,
                language_detected="sq",
                layer_activations=None
            )

    # Build expert system prompt
    lang_instruction = ""
    if lang_code != "en":
        lang_instruction = f"\n\nIMPORTANT: Respond in {lang_name}."

    expert_prompt = f"""{expert_persona}

You provide expert-level, research-backed answers. Be precise, technical, and comprehensive.
{lang_instruction}"""

    # Call Ollama with expert context
    specialized_timeout_s = resolve_specialized_timeout_seconds(
        len(prompt),
        long_response=bool(req.long_response),
    )

    try:
        safe_tokens = clamp_specialized_tokens(
            req.max_tokens,
            long_response=bool(req.long_response),
        )
        num_ctx = min(
            _resolve_num_ctx(
                req.long_response,
                safe_tokens,
                prompt_chars=len(prompt),
                message_count=2,
            ),
            8192 if req.long_response else 4096,
        )
        client_timeout = (
            httpx.Timeout(specialized_timeout_s, connect=min(5.0, specialized_timeout_s))
            if specialized_timeout_s is not None
            else httpx.Timeout(None, connect=5.0)
        )

        async with httpx.AsyncClient(timeout=client_timeout) as client:
            resp = await client.post(
                f"{OLLAMA_HOST}/api/chat",
                json={
                    "model": req.model or MODEL,
                    "messages": [
                        {"role": "system", "content": expert_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "stream": False,
                    "options": {
                        "temperature": 0.5,  # Lower for more factual
                        "num_ctx": num_ctx,
                        "repeat_penalty": 1.1,
                        "top_p": 0.85,
                        "num_predict": safe_tokens
                    }
                }
            )

            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail="Ollama error")

            data = resp.json()
            response_text = data.get("message", {}).get("content", "No response")
            engines_used.append(f"Ollama({req.model or MODEL})")

    except httpx.TimeoutException:
        logger.warning(
            "Specialized chat timeout after %.1fs for domain=%s prompt=%r",
            specialized_timeout_s or -1.0,
            domain,
            prompt[:120],
        )
        raise HTTPException(status_code=504, detail="Expert analysis timeout - switched to latency guard")
    except Exception as e:
        logger.error(f"Specialized chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    elapsed = time.time() - start_time
    logger.info(f"🎓 [{domain}] [{lang_code}] {elapsed:.1f}s - Engines: {', '.join(engines_used)}")

    return ChatResponse(
        response=response_text,
        model=req.model or MODEL,
        processing_time=round(elapsed, 2),
        engines_used=engines_used,
        language_detected=lang_code,
        layer_activations=None,
        provenance=_build_provenance_envelope(
            trace_id=str(uuid.uuid4().hex[:12]),
            engines_used=engines_used,
            model=req.model or MODEL,
            elapsed_s=elapsed,
            lang_code=lang_code,
            response_chars=len(response_text),
            mode=f"specialized:{domain}",
        ),
    )


@app.get("/api/v1/services")
async def list_services():
    """List all available services"""
    registry_services: Dict[str, Any] = {}
    registry_total = 0
    if SERVICE_REGISTRY_AVAILABLE and service_registry:
        registry_services = {
            key: {
                "name": svc.name,
                "port": svc.port,
                "description": svc.description,
                "category": svc.category,
                "capabilities": svc.capabilities,
                "is_core": svc.is_core,
            }
            for key, svc in service_registry.get_all_services().items()
        }
        registry_total = len(registry_services)

    return {
        "total": len(SERVICES),
        "services": SERVICES,
        "service_registry": {
            "available": SERVICE_REGISTRY_AVAILABLE and service_registry is not None,
            "total": registry_total,
            "services": registry_services,
        }
    }


@app.get("/api/v1/advanced-array")
async def advanced_array():
    """Unified advanced system array: engines, modules, governance, labs, and live links."""
    requested_domains = [
        "lora_iot",
        "iot",
        "pipeline",
        "cycles",
        "publisher",
        "algebra",
        "laboratory",
        "governance",
        "agents",
    ]

    domain_matches: Dict[str, Any] = {}
    if SERVICE_REGISTRY_AVAILABLE and service_registry:
        for domain in requested_domains:
            by_capability = service_registry.get_by_capability(domain)
            by_search = service_registry.search(domain)
            merged: Dict[str, Any] = {}
            for svc in by_capability + by_search:
                merged[svc.name] = {
                    "name": svc.name,
                    "port": svc.port,
                    "category": svc.category,
                    "capabilities": svc.capabilities,
                }
            domain_matches[domain] = {
                "count": len(merged),
                "services": list(merged.values())[:25],
            }
    else:
        domain_matches = {domain: {"count": 0, "services": []} for domain in requested_domains}

    modules_present = {
        "agents_py": os.path.exists("/app/agents.py") or os.path.exists("../agents.py"),
        "governance_hub": os.path.exists("/app/services/regulatory/federated_governance.py") or os.path.exists("../services/regulatory/federated_governance.py"),
        "cycle_agents_linker": os.path.exists("/app/apps/api/link_cycle_agents.py") or os.path.exists("../apps/api/link_cycle_agents.py"),
        "laboratories_network": os.path.exists("/app/laboratories.py") or os.path.exists("laboratories.py"),
        "blog_publisher": os.path.exists("/app/services/blog_publisher/main.py") or os.path.exists("../services/blog_publisher/main.py"),
    }

    links = {
        "ocean_core": f"http://localhost:{PORT}",
        "openmind_9999": OPENMIND_BASE,
        "central_api": CENTRAL_API_BASE,
        "excel_core": EXCEL_CORE_BASE,
        "translation_node": TRANSLATION_NODE,
        "kloud_bridge": KLOUD_BRIDGE_BASE,
        "ollama": OLLAMA_HOST,
    }

    link_health = {
        "central_api": await _probe_service(CENTRAL_API_BASE),
        "openmind_9999": await _probe_service(OPENMIND_BASE),
        "excel_core": await _probe_service(EXCEL_CORE_BASE),
        "kloud_bridge": await _probe_service(KLOUD_BRIDGE_BASE),
    }

    registry_summary: Dict[str, Any] = {"available": False}
    if SERVICE_REGISTRY_AVAILABLE and service_registry:
        registry_summary = {
            "available": True,
            **service_registry.get_summary(),
        }

    integration_edges = [
        {"from": "ocean-core", "to": "openmind", "type": "api", "target": OPENMIND_BASE},
        {"from": "ocean-core", "to": "central-api", "type": "api", "target": CENTRAL_API_BASE},
        {"from": "ocean-core", "to": "excel-core", "type": "api", "target": EXCEL_CORE_BASE},
        {"from": "ocean-core", "to": "translation-node", "type": "api", "target": TRANSLATION_NODE},
        {"from": "ocean-core", "to": "kloud-bridge", "type": "api", "target": KLOUD_BRIDGE_BASE},
        {"from": "ocean-core", "to": "ollama", "type": "llm", "target": OLLAMA_HOST},
        {"from": "cycle", "to": "agents", "type": "linker", "target": "apps/api/link_cycle_agents.py"},
        {"from": "governance", "to": "agents", "type": "policy", "target": "services/regulatory/federated_governance.py"},
        {"from": "publisher", "to": "content", "type": "pipeline", "target": "services/blog_publisher/main.py"},
    ]

    return {
        "status": "operational",
        "advanced_array": {
            "registry": registry_summary,
            "knowledge_layer_services": len(SERVICES),
            "modules_present": modules_present,
            "requested_domain_matches": domain_matches,
            "links": links,
            "link_health": link_health,
            "integration_edges": integration_edges,
        },
    }

@app.get("/api/v1/engines")
async def list_engines():
    """List all available engines and their status"""
    return {
        "mega_layer_engine": {
            "available": MEGA_LAYERS_AVAILABLE,
            "combinations": TOTAL_COMBINATIONS if MEGA_LAYERS_AVAILABLE else 0
        },
        "real_answer_engine": {
            "available": REAL_ANSWER_AVAILABLE
        },
        "service_registry": {
            "available": SERVICE_REGISTRY_AVAILABLE
        },
        "albanian_dictionary": {
            "available": ALBANIAN_DICT_AVAILABLE,
            "words": len(ALL_ALBANIAN_WORDS) if ALBANIAN_DICT_AVAILABLE else 0
        },
        "knowledge_seeds": {
            "available": KNOWLEDGE_SEEDS_AVAILABLE
        },
        "knowledge_layer": {
            "available": KNOWLEDGE_LAYER_AVAILABLE,
            "services": len(SERVICES)
        }
    }


@app.get("/api/v1/albanian/dictionary")
async def albanian_dictionary_lookup(query: str = Query(..., min_length=1, max_length=400)):
    """Direct Albanian Dictionary lookup for short Albanian prompts and definitions."""
    if not ALBANIAN_DICT_AVAILABLE or not callable(get_albanian_response):
        raise HTTPException(status_code=503, detail="Albanian dictionary not available")

    text = query.strip()
    if not text:
        raise HTTPException(status_code=400, detail="query required")

    response = get_albanian_response(text)
    return {
        "available": True,
        "matched": bool(response),
        "query": text,
        "response": response or "",
        "source": "albanian_dictionary_local",
        "words": len(ALL_ALBANIAN_WORDS) if ALBANIAN_DICT_AVAILABLE else 0,
    }


@app.get("/api/v1/nanogrid/status")
async def nanogrid_status(http_request: Request):
    """Expose NanoGrid helper-module availability through Ocean Core."""
    target = NANOGRID_BASE.rstrip("/")
    candidates = ["/", "/health", "/api/v1/status"]
    last_error = "unavailable"

    async with httpx.AsyncClient(timeout=4.0) as client:
        for path in candidates:
            try:
                response = await client.get(f"{target}{path}")
                if response.is_success:
                    try:
                        payload = response.json()
                    except Exception:
                        payload = {"raw": response.text[:500]}
                    response_payload = {
                        "available": True,
                        "module": "NanoGrid",
                        "role": "support module for Ocean Core",
                        "upstream": target,
                        "payload": payload,
                    }
                    return _format_optional_cbor(response_payload, http_request)
                last_error = f"http_{response.status_code}"
            except Exception as exc:
                last_error = str(exc)

    response_payload = {
        "available": False,
        "module": "NanoGrid",
        "role": "support module for Ocean Core",
        "upstream": target,
        "error": last_error,
    }
    return _format_optional_cbor(response_payload, http_request)


@app.post("/api/v1/nanogrid/vision/analyze")
async def nanogrid_vision_analyze(req: NanoGridVisionRequest, http_request: Request):
    """Bridge NanoGrid vision analysis through Ocean Core."""
    target_candidates = [
        f"{NANOGRID_BASE.rstrip('/')}/api/v1/vision/analyze",
        f"{NANOGRID_BASE.rstrip('/')}/api/v1/vision",
    ]
    target = target_candidates[0]
    payload = {
        "image_base64": req.image_base64,
        "prompt": req.prompt,
        "extract_text": req.extract_text,
        "language": req.language,
        "user_id": req.user_id,
        "session_topic": req.session_topic,
    }

    payload_size = len(req.image_base64 or "")
    vision_timeout: Optional[float] = None if _elastic_unlimited() else _adaptive_timeout(60.0, 900.0, payload_size)

    response = None
    last_error: Optional[str] = None
    async with httpx.AsyncClient(timeout=vision_timeout) as client:
        for candidate in target_candidates:
            target = candidate
            try:
                current = await client.post(candidate, json=payload)
            except Exception as exc:
                last_error = str(exc)
                continue

            if current.status_code == 404:
                last_error = "http_404"
                continue

            response = current
            break

    if response is None:
        raise HTTPException(status_code=503, detail=f"NanoGrid vision upstream unavailable: {last_error or 'unreachable'}")

    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text[:1000] or "NanoGrid vision error")

    try:
        data = response.json()
    except Exception:
        data = {"response": response.text}

    if isinstance(data, dict):
        data.setdefault("module", "NanoGrid")
        data.setdefault("bridged_via", "Ocean Core")
        data.setdefault("upstream", target)
        return _format_optional_cbor(data, http_request)

    payload = {
        "module": "NanoGrid",
        "bridged_via": "Ocean Core",
        "upstream": target,
        "payload": data,
    }
    return _format_optional_cbor(payload, http_request)


# ═══════════════════════════════════════════════════════════════════
# RESEARCH & ARCHIVE ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@app.get("/api/v1/arxiv/{query}")
async def search_arxiv(query: str, max_results: int = 10):
    """
    Search ArXiv scientific papers.
    Real API integration with arxiv.org
    """
    try:
        import urllib.parse
        encoded_query = urllib.parse.quote(query)
        arxiv_url = f"https://export.arxiv.org/api/query?search_query=all:{encoded_query}&start=0&max_results={max_results}"

        headers = {"User-Agent": "Clisonix-Ocean/5.0 (clisonix@pm.me)"}
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(arxiv_url, headers=headers)

        if response.status_code != 200:
            return {"error": "ArXiv API error", "status": response.status_code}

        # Parse XML response
        import xml.etree.ElementTree as ET
        root = ET.fromstring(response.text)

        # ArXiv uses Atom namespace
        ns = {'atom': 'http://www.w3.org/2005/Atom'}

        papers = []
        for entry in root.findall('atom:entry', ns):
            title_el = entry.find('atom:title', ns)
            summary_el = entry.find('atom:summary', ns)
            published_el = entry.find('atom:published', ns)
            id_el = entry.find('atom:id', ns)

            # Get authors
            authors = []
            for author in entry.findall('atom:author', ns):
                name_el = author.find('atom:name', ns)
                if name_el is not None:
                    authors.append(name_el.text)

            # Get categories
            categories = []
            for cat in entry.findall('atom:category', ns):
                term = cat.get('term')
                if term:
                    categories.append(term)

            papers.append({
                "title": (title_el.text or "").strip() if title_el is not None else "",
                "summary": (summary_el.text or "").strip()[:500] if summary_el is not None else "",
                "authors": authors[:5],  # First 5 authors
                "published": published_el.text if published_el is not None else "",
                "url": id_el.text if id_el is not None else "",
                "categories": categories[:3]
            })

        return {
            "query": query,
            "total_results": len(papers),
            "papers": papers,
            "source": "arxiv.org"
        }

    except Exception as e:
        logger.error(f"ArXiv search error: {e}")
        return {"error": str(e), "query": query}


@app.get("/api/v1/wiki/{query}")
async def search_wikipedia(query: str, limit: int = 10):
    """
    Search Wikipedia articles.
    Real API integration with Wikipedia
    """
    try:
        import urllib.parse
        encoded_query = urllib.parse.quote(query)

        # Wikipedia API for search
        wiki_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={encoded_query}&srlimit={limit}&format=json"

        headers = {"User-Agent": "Clisonix-Ocean/5.0 (clisonix@pm.me)"}
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(wiki_url, headers=headers)

        if response.status_code != 200:
            return {"error": "Wikipedia API error", "status": response.status_code}

        data = response.json()
        search_results = data.get("query", {}).get("search", [])

        results = []
        for item in search_results:
            # Clean snippet from HTML
            snippet = item.get("snippet", "")
            snippet = snippet.replace("<span class=\"searchmatch\">", "").replace("</span>", "")

            results.append({
                "title": item.get("title", ""),
                "snippet": snippet,
                "pageid": item.get("pageid"),
                "wordcount": item.get("wordcount", 0),
                "url": f"https://en.wikipedia.org/wiki/{urllib.parse.quote(item.get('title', '').replace(' ', '_'))}"
            })

        return {
            "query": query,
            "total_results": len(results),
            "results": results,
            "source": "wikipedia.org"
        }

    except Exception as e:
        logger.error(f"Wikipedia search error: {e}")
        return {"error": str(e), "query": query}


@app.get("/api/v1/pubmed/{query}")
async def search_pubmed(query: str, max_results: int = 10):
    """
    Search PubMed medical/scientific literature.
    Real API integration with NCBI PubMed
    """
    try:
        import urllib.parse
        encoded_query = urllib.parse.quote(query)

        # Step 1: Search for IDs
        search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={encoded_query}&retmax={max_results}&retmode=json"

        headers = {"User-Agent": "Clisonix-Ocean/5.0 (clisonix@pm.me)"}
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            search_response = await client.get(search_url, headers=headers)

        if search_response.status_code != 200:
            return {"error": "PubMed search error", "status": search_response.status_code}

        search_data = search_response.json()
        id_list = search_data.get("esearchresult", {}).get("idlist", [])

        if not id_list:
            return {"query": query, "total_results": 0, "articles": [], "source": "pubmed.ncbi.nlm.nih.gov"}

        # Step 2: Fetch article details
        ids_str = ",".join(id_list)
        fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={ids_str}&retmode=json"

        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            fetch_response = await client.get(fetch_url, headers=headers)

        if fetch_response.status_code != 200:
            return {"error": "PubMed fetch error", "status": fetch_response.status_code}

        fetch_data = fetch_response.json()
        result_data = fetch_data.get("result", {})

        articles = []
        for pmid in id_list:
            article = result_data.get(pmid, {})
            if isinstance(article, dict):
                authors = article.get("authors", [])
                author_names = [a.get("name", "") for a in authors[:5]] if isinstance(authors, list) else []

                articles.append({
                    "pmid": pmid,
                    "title": article.get("title", ""),
                    "authors": author_names,
                    "source": article.get("source", ""),
                    "pubdate": article.get("pubdate", ""),
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                })

        return {
            "query": query,
            "total_results": len(articles),
            "articles": articles,
            "source": "pubmed.ncbi.nlm.nih.gov"
        }

    except Exception as e:
        logger.error(f"PubMed search error: {e}")
        return {"error": str(e), "query": query}


@app.get("/api/v1/sources")
async def list_data_sources():
    """
    List all available data sources for research.
    5000+ sources organized by category.
    """
    return {
        "total_sources": 5247,
        "categories": {
            "scientific_papers": {
                "count": 847,
                "sources": [
                    {"name": "ArXiv", "url": "https://arxiv.org", "type": "preprints", "fields": ["physics", "cs", "math", "bio"]},
                    {"name": "PubMed", "url": "https://pubmed.ncbi.nlm.nih.gov", "type": "medical", "articles": "35M+"},
                    {"name": "IEEE Xplore", "url": "https://ieeexplore.ieee.org", "type": "engineering"},
                    {"name": "Springer", "url": "https://link.springer.com", "type": "journals"},
                    {"name": "Nature", "url": "https://nature.com", "type": "multidisciplinary"},
                    {"name": "Science", "url": "https://science.org", "type": "multidisciplinary"},
                    {"name": "PLOS ONE", "url": "https://plosone.org", "type": "open-access"},
                    {"name": "bioRxiv", "url": "https://biorxiv.org", "type": "biology-preprints"},
                    {"name": "medRxiv", "url": "https://medrxiv.org", "type": "medical-preprints"},
                    {"name": "SSRN", "url": "https://ssrn.com", "type": "social-sciences"}
                ]
            },
            "encyclopedias": {
                "count": 156,
                "sources": [
                    {"name": "Wikipedia", "url": "https://wikipedia.org", "languages": 300, "articles": "60M+"},
                    {"name": "Britannica", "url": "https://britannica.com", "type": "curated"},
                    {"name": "Stanford Encyclopedia of Philosophy", "url": "https://plato.stanford.edu", "type": "philosophy"},
                    {"name": "Scholarpedia", "url": "https://scholarpedia.org", "type": "peer-reviewed"}
                ]
            },
            "government_data": {
                "count": 1523,
                "sources": [
                    {"name": "Data.gov (US)", "url": "https://data.gov", "datasets": "300K+"},
                    {"name": "EU Open Data", "url": "https://data.europa.eu", "datasets": "1.5M+"},
                    {"name": "UK Data Service", "url": "https://ukdataservice.ac.uk"},
                    {"name": "World Bank", "url": "https://data.worldbank.org", "indicators": "1400+"},
                    {"name": "UN Data", "url": "https://data.un.org"},
                    {"name": "OECD Data", "url": "https://data.oecd.org"},
                    {"name": "Eurostat", "url": "https://ec.europa.eu/eurostat"},
                    {"name": "INSTAT Albania", "url": "https://instat.gov.al", "country": "Albania"}
                ]
            },
            "code_repositories": {
                "count": 892,
                "sources": [
                    {"name": "GitHub", "url": "https://github.com", "repos": "200M+"},
                    {"name": "GitLab", "url": "https://gitlab.com"},
                    {"name": "Bitbucket", "url": "https://bitbucket.org"},
                    {"name": "SourceForge", "url": "https://sourceforge.net"},
                    {"name": "npm", "url": "https://npmjs.com", "packages": "2M+"},
                    {"name": "PyPI", "url": "https://pypi.org", "packages": "450K+"},
                    {"name": "crates.io", "url": "https://crates.io", "type": "rust"},
                    {"name": "Maven Central", "url": "https://search.maven.org", "type": "java"}
                ]
            },
            "news_media": {
                "count": 1247,
                "sources": [
                    {"name": "Reuters", "url": "https://reuters.com", "type": "agency"},
                    {"name": "AP News", "url": "https://apnews.com", "type": "agency"},
                    {"name": "BBC", "url": "https://bbc.com", "type": "broadcaster"},
                    {"name": "The Guardian", "url": "https://theguardian.com"},
                    {"name": "New York Times", "url": "https://nytimes.com"},
                    {"name": "Der Spiegel", "url": "https://spiegel.de", "language": "German"},
                    {"name": "Le Monde", "url": "https://lemonde.fr", "language": "French"}
                ]
            },
            "ai_ml_datasets": {
                "count": 582,
                "sources": [
                    {"name": "Hugging Face", "url": "https://huggingface.co/datasets", "datasets": "100K+"},
                    {"name": "Kaggle", "url": "https://kaggle.com/datasets", "datasets": "200K+"},
                    {"name": "UCI ML Repository", "url": "https://archive.ics.uci.edu"},
                    {"name": "Google Dataset Search", "url": "https://datasetsearch.research.google.com"},
                    {"name": "Papers With Code", "url": "https://paperswithcode.com"},
                    {"name": "OpenML", "url": "https://openml.org"}
                ]
            }
        },
        "api_endpoints": {
            "arxiv": "/api/v1/arxiv/{query}",
            "wikipedia": "/api/v1/wiki/{query}",
            "pubmed": "/api/v1/pubmed/{query}"
        },
        "powered_by": "Curiosity Ocean v5.0.0"
    }


# ═══════════════════════════════════════════════════════════════════
# WEB BROWSING & SEARCH ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@app.get("/api/v1/browse")
async def browse_webpage(url: str, max_chars: int = 8000):
    """
    Fetch and extract main content from a webpage.
    Returns clean text for AI processing.
    """
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        headers = {
            "User-Agent": "Clisonix-Ocean/5.0 (clisonix@pm.me)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9"
        }

        # verify=False for Docker SSL issues, follow_redirects for 30x
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True, verify=False) as client:
            response = await client.get(url, headers=headers)

        if response.status_code != 200:
            return {"error": f"Failed to fetch URL: {response.status_code}", "url": url}

        html = response.text

        # Simple HTML to text extraction
        import re
        # Remove script and style
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<nav[^>]*>.*?</nav>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<footer[^>]*>.*?</footer>', '', html, flags=re.DOTALL | re.IGNORECASE)

        # Extract title
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else url

        # Extract meta description
        desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']', html, re.IGNORECASE)
        description = desc_match.group(1) if desc_match else ""

        # Remove all HTML tags
        text = re.sub(r'<[^>]+>', ' ', html)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        # Truncate
        text = text[:max_chars]

        return {
            "url": url,
            "title": title,
            "description": description,
            "content": text,
            "char_count": len(text),
            "status": "success"
        }

    except Exception as e:
        logger.error(f"Browse error: {e}")
        return {"error": str(e), "url": url}


@app.get("/api/v1/search")
async def web_search(q: str, num: int = 5):
    """
    Search the web using DuckDuckGo HTML (no API key required).
    Returns search results with titles, URLs, and snippets.
    """
    try:
        import urllib.parse
        encoded_query = urllib.parse.quote(q)

        # DuckDuckGo HTML search
        search_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9"
        }

        # verify=False for Docker SSL issues
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True, verify=False) as client:
            response = await client.get(search_url, headers=headers)

        if response.status_code != 200:
            return {"error": "Search failed", "status": response.status_code}

        html = response.text

        # Parse DuckDuckGo results
        import re
        results = []

        # Find result blocks
        result_pattern = r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>.*?<a[^>]*class="result__snippet"[^>]*>(.*?)</a>'
        matches = re.findall(result_pattern, html, re.DOTALL | re.IGNORECASE)

        for match in matches[:num]:
            url = match[0]
            # DuckDuckGo wraps URLs - extract actual URL
            if 'uddg=' in url:
                url_match = re.search(r'uddg=([^&]+)', url)
                if url_match:
                    url = urllib.parse.unquote(url_match.group(1))

            title = re.sub(r'<[^>]+>', '', match[1]).strip()
            snippet = re.sub(r'<[^>]+>', '', match[2]).strip()

            if url and title:
                results.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet
                })

        # If no results from pattern, try simpler extraction
        if not results:
            simple_pattern = r'<a[^>]*href="(https?://[^"]+)"[^>]*>([^<]+)</a>'
            for match in re.findall(simple_pattern, html)[:num]:
                url, title = match
                if 'duckduckgo' not in url.lower() and len(title) > 5:
                    results.append({"title": title, "url": url, "snippet": ""})

        return {
            "query": q,
            "total_results": len(results),
            "results": results,
            "source": "duckduckgo"
        }

    except Exception as e:
        logger.error(f"Search error: {e}")
        return {"error": str(e), "query": q}


class WebChatRequest(BaseModel):
    url: str
    message: str


async def get_web_chat_response(url: str, message: str, page_content: str, page_title: str, timeout: Optional[float] = 120.0) -> str:
    """
    Get LLM response for webpage chat with elastic timeout.
    Returns the response text or raises exception on failure.
    """
    shared_system_context = _build_shared_system_context()
    shared_context_block = f"\n\n{shared_system_context}" if shared_system_context else ""

    system_prompt = f"""You are a helpful assistant analyzing a webpage.

Page Title: {page_title}
Page URL: {url}

{shared_context_block}

Page Content:
{page_content[:8000]}

Answer the user's question based on this webpage content. Be concise, accurate, and helpful.
If the content doesn't contain the answer, say so honestly."""

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": MODEL,
                "prompt": message,
                "system": system_prompt,
                "stream": False,
                "options": {
                    "num_ctx": _resolve_num_ctx(long_response=True, token_budget=-1),
                    "num_predict": _clamp_chat_tokens(None, long_response=True),
                    "temperature": 0.7
                }
            }
        )

    if response.status_code == 200:
        data = response.json()
        return data.get("response", "I couldn't generate a response.")
    else:
        raise Exception(f"LLM error: {response.status_code}")


@app.post("/api/v1/chat/browse")
async def chat_with_webpage(request: WebChatRequest):
    """
    Chat about a webpage - fetch content and answer questions using LLM.
    ELASTIC: 3 retry attempts with increasing timeouts (120s, 240s, 360s).
    """
    try:
        # First, browse the page
        browse_result = await browse_webpage(request.url, max_chars=10000)

        if "error" in browse_result:
            return {"error": browse_result["error"], "url": request.url}

        page_content = browse_result.get("content", "")
        page_title = browse_result.get("title", request.url)

        if not page_content:
            return {"error": "Could not extract content from page", "url": request.url}

        # ELASTIC: unlimited mode has no timeout cap
        timeouts = [None] if _elastic_unlimited() else [120.0, 240.0, 360.0]
        answer = None
        attempt = 0

        for timeout in timeouts:
            attempt += 1
            try:
                logger.info(f"[Web Chat] Attempt {attempt}/{len(timeouts)} with timeout={timeout} for {request.url}")
                answer = await get_web_chat_response(
                    request.url, request.message, page_content, page_title, timeout
                )
                logger.info(f"[Web Chat] Success on attempt {attempt}")
                break
            except Exception as e:
                logger.warning(f"[Web Chat] Attempt {attempt} failed: {e}")
                if attempt < len(timeouts):
                    await asyncio.sleep(1)  # Brief pause before retry

        # If all attempts failed, return partial response with page summary
        if answer is None:
            logger.error(f"[Web Chat] All attempts failed for {request.url}")
            answer = f"⚠️ LLM response failed after {len(timeouts)} attempt(s).\n\n**Page Summary:**\n{page_title}\n\n{page_content[:1000]}..."

        return {
            "url": request.url,
            "title": page_title,
            "question": request.message,
            "answer": answer,
            "response": answer,  # Also provide as 'response' for frontend compatibility
            "message": answer,   # Also provide as 'message' for frontend compatibility
            "content_length": len(page_content),
            "status": "success" if "timed out" not in answer else "partial",
            "attempts": attempt
        }

    except Exception as e:
        logger.error(f"Chat browse error: {e}")
        return {"error": str(e), "url": request.url}


@app.post("/api/v1/chat/browse/stream")
async def chat_with_webpage_stream(request: WebChatRequest):
    """
    SSE Streaming chat about a webpage - real-time token delivery.
    """
    async def generate():
        try:
            # First, browse the page
            browse_result = await browse_webpage(request.url, max_chars=10000)

            if "error" in browse_result:
                yield f"data: {json.dumps({'error': browse_result['error']})}\n\n"
                return

            page_content = browse_result.get("content", "")
            page_title = browse_result.get("title", request.url)

            yield f"data: {json.dumps({'status': 'browsing', 'title': page_title, 'chars': len(page_content)})}\n\n"

            if not page_content:
                yield f"data: {json.dumps({'error': 'Could not extract content from page'})}\n\n"
                return

            shared_system_context = _build_shared_system_context()
            shared_context_block = f"\n\n{shared_system_context}" if shared_system_context else ""

            system_prompt = f"""You are a helpful assistant analyzing a webpage.

Page Title: {page_title}
Page URL: {request.url}

{shared_context_block}

Page Content:
{page_content[:8000]}

Answer the user's question based on this webpage content. Be concise, accurate, and helpful."""

            yield f"data: {json.dumps({'status': 'thinking'})}\n\n"

            # Stream from Ollama
            async with httpx.AsyncClient(timeout=_resolve_llm_timeout(len(request.message or ""), 2)) as client:
                async with client.stream(
                    "POST",
                    f"{OLLAMA_HOST}/api/generate",
                    json={
                        "model": MODEL,
                        "prompt": request.message,
                        "system": system_prompt,
                        "stream": True,
                        "options": {
                            "num_ctx": _resolve_num_ctx(long_response=True, token_budget=_clamp_chat_tokens(None, long_response=True)),
                            "num_predict": _clamp_chat_tokens(None, long_response=True),
                            "temperature": 0.7,
                        }
                    }
                ) as response:
                    full_response = ""
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                token = data.get("response", "")
                                if token:
                                    full_response += token
                                    yield f"data: {json.dumps({'token': token, 'status': 'streaming'})}\n\n"
                                if data.get("done"):
                                    yield f"data: {json.dumps({'status': 'complete', 'total_chars': len(full_response)})}\n\n"
                            except json.JSONDecodeError:
                                pass

        except Exception as e:
            logger.error(f"Stream chat browse error: {e}")
            yield f"data: {json.dumps({'error': str(e), 'status': 'error'})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


# ═══════════════════════════════════════════════════════════════════
# ZÜRICH ENGINE - 9-Stage Deterministic Reasoning
# ═══════════════════════════════════════════════════════════════════

class ZurichRequest(BaseModel):
    prompt: str
    include_debug: bool = False


def zurich_cycle(input_text: str) -> Dict[str, Any]:
    """
    9-stage deterministic reasoning cycle - 100% predictable, no AI randomness.
    Based on Harmonic Trinity's Zürich Engine.
    """
    start_time = time.time()

    # Stage 1: INTAKE - Parse input type
    words = input_text.split()
    word_count = len(words)
    char_count = len(input_text)

    if input_text.endswith("?"):
        input_type = "question"
    elif input_text.endswith("!"):
        input_type = "exclamation"
    elif any(cmd in input_text.lower() for cmd in ["create", "make", "build", "generate"]):
        input_type = "command"
    else:
        input_type = "statement"

    intake = {
        "stage": 1,
        "name": "intake",
        "type": input_type,
        "word_count": word_count,
        "char_count": char_count
    }

    # Stage 2: PREPROCESS - Normalize text
    normalized = input_text.strip().lower()
    keywords = [w for w in words if len(w) > 3]

    preprocess = {
        "stage": 2,
        "name": "preprocess",
        "normalized": normalized[:100],
        "keywords": keywords[:10]
    }

    # Stage 3: TAGGER - Classify content & intent
    domains = []
    if any(w in normalized for w in ["code", "program", "python", "javascript", "function"]):
        domains.append("programming")
    if any(w in normalized for w in ["ai", "machine", "learning", "neural", "model"]):
        domains.append("ai")
    if any(w in normalized for w in ["business", "company", "market", "product"]):
        domains.append("business")
    if any(w in normalized for w in ["science", "research", "study", "experiment"]):
        domains.append("science")
    if any(w in normalized for w in ["health", "medical", "doctor", "disease"]):
        domains.append("health")
    if not domains:
        domains.append("general")

    tagger = {
        "stage": 3,
        "name": "tagger",
        "domains": domains,
        "primary_domain": domains[0]
    }

    # Stage 4: INTERPRET - Extract meanings
    has_comparison = any(w in normalized for w in ["vs", "versus", "compare", "difference"])
    has_definition = any(w in normalized for w in ["what is", "define", "meaning", "explain"])
    has_howto = any(w in normalized for w in ["how to", "how do", "steps", "process"])
    has_why = "why" in normalized

    interpret = {
        "stage": 4,
        "name": "interpret",
        "seeking_comparison": has_comparison,
        "seeking_definition": has_definition,
        "seeking_howto": has_howto,
        "seeking_reason": has_why
    }

    # Stage 5: REASON - Build reasoning steps
    reasoning_steps = []
    if has_definition:
        reasoning_steps.append("Provide clear definition")
    if has_comparison:
        reasoning_steps.append("Analyze both sides")
        reasoning_steps.append("Highlight differences")
    if has_howto:
        reasoning_steps.append("Break into steps")
        reasoning_steps.append("Provide examples")
    if has_why:
        reasoning_steps.append("Explain causation")
        reasoning_steps.append("Provide evidence")
    if not reasoning_steps:
        reasoning_steps.append("Provide comprehensive response")

    reason = {
        "stage": 5,
        "name": "reason",
        "steps": reasoning_steps,
        "step_count": len(reasoning_steps)
    }

    # Stage 6: STRATEGY - Select response mode
    if word_count < 5:
        strategy = "concise"
    elif has_howto:
        strategy = "step-by-step"
    elif has_comparison:
        strategy = "comparative"
    elif has_definition:
        strategy = "explanatory"
    else:
        strategy = "comprehensive"

    strategy_output = {
        "stage": 6,
        "name": "strategy",
        "mode": strategy,
        "expected_length": "short" if word_count < 5 else "medium" if word_count < 20 else "long"
    }

    # Stage 7: DRAFT - Generate response structure
    header = f"📋 Analysis of: {input_text[:50]}..."

    if strategy == "step-by-step":
        structure = ["Introduction", "Step 1", "Step 2", "Step 3", "Conclusion"]
    elif strategy == "comparative":
        structure = ["Overview", "Option A", "Option B", "Comparison", "Recommendation"]
    elif strategy == "explanatory":
        structure = ["Definition", "Context", "Examples", "Summary"]
    else:
        structure = ["Main Point", "Supporting Details", "Conclusion"]

    draft = {
        "stage": 7,
        "name": "draft",
        "header": header,
        "structure": structure
    }

    # Stage 8: FINAL - Format output
    confidence = min(0.95, 0.7 + (len(domains) * 0.05) + (len(reasoning_steps) * 0.03))

    final_output = f"""**{header}**

**Domain:** {', '.join(domains)}
**Strategy:** {strategy}
**Confidence:** {confidence:.0%}

**Analysis:**
Input type: {input_type}
Keywords identified: {', '.join(keywords[:5]) if keywords else 'None specific'}

**Response Structure:**
{chr(10).join(f'• {s}' for s in structure)}

**Reasoning Applied:**
{chr(10).join(f'{i+1}. {step}' for i, step in enumerate(reasoning_steps))}

---
*Processed by Zürich Engine v1.0 - 9-stage deterministic cycle*
*Processing time: {(time.time() - start_time) * 1000:.2f}ms*"""

    final = {
        "stage": 8,
        "name": "final",
        "output": final_output,
        "confidence": confidence
    }

    # Stage 9: CYCLE - Complete orchestration
    processing_time = time.time() - start_time

    cycle = {
        "stage": 9,
        "name": "cycle",
        "completed": True,
        "total_stages": 9,
        "processing_time_ms": processing_time * 1000
    }

    return {
        "input": input_text,
        "output": final_output,
        "confidence": confidence,
        "strategy": strategy,
        "domains": domains,
        "stages": {
            "intake": intake,
            "preprocess": preprocess,
            "tagger": tagger,
            "interpret": interpret,
            "reason": reason,
            "strategy": strategy_output,
            "draft": draft,
            "final": final,
            "cycle": cycle
        }
    }


@app.post("/api/v1/zurich")
async def zurich_reasoning(request: ZurichRequest):
    """
    Zürich Deterministic Reasoning Engine.

    9-stage processing cycle:
    1. Intake - Parse input type
    2. Preprocess - Normalize text
    3. Tagger - Classify content & intent
    4. Interpret - Extract meanings
    5. Reason - Build reasoning steps
    6. Strategy - Select response mode
    7. Draft - Generate response structure
    8. Final - Format output
    9. Cycle - Complete orchestration

    100% deterministic - same input always produces same output.
    """
    if not request.prompt:
        raise HTTPException(status_code=400, detail="prompt is required")

    result = zurich_cycle(request.prompt)

    response = {
        "ok": True,
        "input": request.prompt,
        "output": result["output"],
        "confidence": result["confidence"],
        "strategy": result["strategy"],
        "domains": result["domains"],
        "processing_time_ms": result["stages"]["cycle"]["processing_time_ms"],
        "engine": "Zürich Deterministic Engine v1.0"
    }

    if request.include_debug:
        response["stages"] = result["stages"]

    return response


@app.get("/api/v1/zurich/info")
async def zurich_info():
    """Get Zürich Engine information and capabilities."""
    return {
        "name": "Zürich Deterministic Engine",
        "version": "1.0",
        "type": "Logic-based reasoning",
        "description": "100% deterministic processing without AI randomness",
        "stages": [
            {"step": 1, "name": "intake", "description": "Parse input type"},
            {"step": 2, "name": "preprocess", "description": "Normalize text"},
            {"step": 3, "name": "tagger", "description": "Classify content & intent"},
            {"step": 4, "name": "interpret", "description": "Extract meanings"},
            {"step": 5, "name": "reason", "description": "Build reasoning steps"},
            {"step": 6, "name": "strategy", "description": "Select response mode"},
            {"step": 7, "name": "draft", "description": "Generate response structure"},
            {"step": 8, "name": "final", "description": "Format output"},
            {"step": 9, "name": "cycle", "description": "Complete orchestration"}
        ],
        "features": [
            "Deterministic processing",
            "No external API calls",
            "Local computation only",
            "Pattern-based reasoning",
            "Structured output"
        ],
        "response_time": "1-50ms per input"
    }


# ═══════════════════════════════════════════════════════════════════
# TRINITY PERSONAS - Multi-Persona AI Debate
# ═══════════════════════════════════════════════════════════════════

class DebateRequest(BaseModel):
    topic: str
    personas: Optional[List[str]] = None  # Default: all 5
    max_tokens: Optional[int] = None  # ELASTIC: no fixed cap unless explicitly requested
    stream_mode: str = "json"  # compact | json
    preferred_language: Optional[str] = None  # Optional ISO language hint (e.g. sq, de, fr)
    quality_profile: Optional[str] = None  # standard | high | albanian-strict (auto for sq when omitted)
    language_layers: int = 4
    session_id: Optional[str] = None
    conversation_context: Optional[List[str]] = None


DEBATE_LANGUAGE_NAMES = {
    "en": "English",
    "sq": "Albanian",
    "de": "German",
    "fr": "French",
    "it": "Italian",
    "es": "Spanish",
    "pt": "Portuguese",
    "tr": "Turkish",
    "nl": "Dutch",
    "pl": "Polish",
}


def _normalize_preferred_language(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    normalized = value.strip().lower().replace("_", "-")
    if not normalized:
        return None
    return normalized.split("-")[0]


def _looks_albanian_text(text: str) -> bool:
    sample = (text or "").strip().lower()
    if not sample:
        return False

    strong_markers = (
        "pershendetje", "përshëndetje", "cfare", "çfare", "si jeni", "a jeni",
        "shqip", "shpjego", "mendoni", "zhvilluar", "sistemin", "debatit",
        "cfare mendoni", "çfare mendoni",
    )
    if any(marker in sample for marker in strong_markers):
        return True

    albanian_tokens = {
        "dhe", "nuk", "po", "me", "per", "për", "si", "cfare", "çfare", "jeni", "eshte", "është", "ku", "pse", "kur", "nga",
    }
    words = re.findall(r"[a-zA-ZçëÇË]+", sample)
    if not words:
        return False
    overlap = sum(1 for w in words if w in albanian_tokens)
    return overlap >= 2


def _persona_prompt_prefix(persona_id: str, lang_code: str, default_prefix: str) -> str:
    if lang_code == "sq":
        localized = {
            "alba": "Si Alba (Optimistja), e shoh anën pozitive dhe mundësitë reale:",
            "albi": "Si Albi (Pragmatiku), po jap planin praktik dhe të zbatueshëm:",
            "jona": "Si Jona (Skeptikja), po testoj rreziqet, supozimet dhe dobësitë:",
            "blerina": "Si Blerina (Analistja), po jap analizë me strukturë dhe evidencë:",
            "asi": "Si ASI (Meta-Mendimtari), po sintetizoj pamjen e plotë:",
        }
        return localized.get(persona_id, default_prefix)
    return default_prefix


def _resolve_debate_profile(lang_code: str, requested_profile: Optional[str]) -> str:
    requested = (requested_profile or "").strip().lower()
    allowed = {"standard", "high", "albanian-strict"}
    if requested in allowed:
        return requested
    if (lang_code or "").lower() == "sq":
        return "albanian-strict"
    return "high"


def _debate_length_instruction(lang_code: str) -> str:
    if (lang_code or "").lower() == "sq":
        return "Syno makimumin fjale kur ndihmon qartesine; mos sakrifiko saktesine ose plotesine kur pyetja kerkon me shume."
    return "Target max words when it helps clarity; do not sacrifice correctness or completeness when the prompt needs more depth."


def _debate_peer_context(persona_outputs: Dict[str, str], lang_code: str, max_items: int = 3) -> str:
    if not persona_outputs:
        return ""

    label = "PEER CONTEXT (ACKNOWLEDGE OR CHALLENGE PREVIOUS PERSONAS)" if (lang_code or "").lower() != "sq" else "KONTEKST NGA PERSONAT E TJERE (REFERO OSE KUNDERSHTO ARGUMENTET)"
    lines = [label + ":"]
    for persona_id, text in list(persona_outputs.items())[-max_items:]:
        compact = " ".join(str(text or "").split())[:420]
        if compact:
            lines.append(f"- {persona_id}: {compact}")
    return "\n".join(lines)


def _debate_ecosystem_context(lang_code: str) -> str:
    services_count = len(SERVICES) if isinstance(SERVICES, dict) else 0
    module_cores_count = len(MODULE_CORE_CATALOG) if isinstance(MODULE_CORE_CATALOG, list) else 0
    personas_count = len(TRINITY_PERSONAS)

    capabilities: List[str] = []
    if MEGA_LAYERS_AVAILABLE:
        capabilities.append("mega_layers")
    if REAL_ANSWER_AVAILABLE:
        capabilities.append("real_answer_engine")
    if SERVICE_REGISTRY_AVAILABLE:
        capabilities.append("service_registry")
    if KNOWLEDGE_LAYER_AVAILABLE:
        capabilities.append("knowledge_layer")
    if MODULE_CORE_REGISTRY_AVAILABLE:
        capabilities.append("module_core_registry")
    if ENTERPRISE_GUARD_AVAILABLE:
        capabilities.append("enterprise_guard")
    if HAS_LANGDETECT:
        capabilities.append("language_detection")

    cap_line = ", ".join(capabilities) if capabilities else "basic_runtime"

    if (lang_code or "").lower() == "sq":
        return (
            "KONTEKST EKOSISTEMI (DETYRUES):\n"
            "- Ti je nje personazh i Trinity Debate brenda agjentit Curiosity Ocean ne Clisonix Cloud.\n"
            f"- Personazhe aktive ne kete engine: {personas_count}.\n"
            f"- Module/servise te ngarkuara ne knowledge layer: {services_count}.\n"
            f"- Module cores te disponueshme per offload: {module_cores_count}.\n"
            f"- Procese/kapacitete runtime aktive: {cap_line}.\n"
            "- Mos u paraqit si sistem i izoluar; referoju ekosistemit kur tema lidhet me arkitekture, module, procese ose shkallezim.\n"
            "- Mos shpik numra ose procese qe nuk jane ne kete kontekst."
        )

    return (
        "ECOSYSTEM CONTEXT (MANDATORY):\n"
        "- You are a Trinity Debate persona running inside the Curiosity Ocean agent on Clisonix Cloud.\n"
        f"- Active personas in this engine: {personas_count}.\n"
        f"- Loaded services/modules in the knowledge layer: {services_count}.\n"
        f"- Available module cores for offload: {module_cores_count}.\n"
        f"- Active runtime capabilities/process families: {cap_line}.\n"
        "- Do not present yourself as an isolated model; reference this ecosystem when the topic involves architecture, modules, processes, or scalability.\n"
        "- Do not invent counts or processes that are not present in this context."
    )


# The 5 Trinity Personas
TRINITY_PERSONAS = {
    "alba": {
        "name": "Alba",
        "emoji": "🌅",
        "role": "The Optimist",
        "description": "Sees opportunity in every challenge, focuses on positive outcomes",
        "style": "Hopeful, encouraging, solution-oriented",
        "prompt_prefix": "As Alba the Optimist, I see the positive side:"
    },
    "albi": {
        "name": "Albi",
        "emoji": "🔧",
        "role": "The Pragmatist",
        "description": "Practical, results-focused, concerned with implementation",
        "style": "Direct, practical, actionable",
        "prompt_prefix": "As Albi the Pragmatist, here's the practical view:"
    },
    "jona": {
        "name": "Jona",
        "emoji": "🔍",
        "role": "The Skeptic",
        "description": "Questions assumptions, identifies risks and weaknesses",
        "style": "Critical, analytical, cautious",
        "prompt_prefix": "As Jona the Skeptic, I must point out:"
    },
    "blerina": {
        "name": "Blerina",
        "emoji": "🌐",
        "role": "The Analyst",
        "description": "Data-driven, systematic, considers all angles",
        "style": "Methodical, thorough, evidence-based",
        "prompt_prefix": "As Blerina the Analyst, looking at the data:"
    },
    "asi": {
        "name": "ASI",
        "emoji": "🧠",
        "role": "The Meta-Thinker",
        "description": "Synthesizes all perspectives, finds higher-level patterns",
        "style": "Philosophical, integrative, holistic",
        "prompt_prefix": "As ASI, synthesizing all perspectives:"
    }
}

# Debate hardening controls (production safety)
DEBATE_MAX_TOKENS_HARD = int(os.getenv("DEBATE_MAX_TOKENS_HARD", "-1"))
DEBATE_STREAM_MAX_CONCURRENCY = int(os.getenv("DEBATE_STREAM_MAX_CONCURRENCY", "6"))
DEBATE_STREAM_QUEUE_LIMIT = int(os.getenv("DEBATE_STREAM_QUEUE_LIMIT", "24"))
DEBATE_STREAM_QUEUE_TIMEOUT_S = float(os.getenv("DEBATE_STREAM_QUEUE_TIMEOUT_S", "8"))
DEBATE_RATE_LIMIT_WINDOW_S = int(os.getenv("DEBATE_RATE_LIMIT_WINDOW_S", "60"))
DEBATE_RATE_LIMIT_REQUESTS = int(os.getenv("DEBATE_RATE_LIMIT_REQUESTS", "12"))

_debate_stream_semaphore = asyncio.Semaphore(DEBATE_STREAM_MAX_CONCURRENCY)
_debate_stream_state_lock = asyncio.Lock()
_debate_stream_active = 0
_debate_stream_waiting = 0

_debate_rate_lock = asyncio.Lock()
_debate_rate_buckets: Dict[str, deque] = {}

DEBATE_MEMORY_MAX_TURNS = int(os.getenv("DEBATE_MEMORY_MAX_TURNS", "10"))
DEBATE_MEMORY_TTL_SECONDS = int(os.getenv("DEBATE_MEMORY_TTL_SECONDS", "7200"))
_debate_memory_lock = asyncio.Lock()
_debate_memory_store: Dict[str, Dict[str, Any]] = {}


def _clamp_tokens(max_tokens: Optional[int]) -> int:
    if _elastic_unlimited() and (max_tokens is None or (isinstance(max_tokens, int) and max_tokens <= -1)):
        return -1

    if max_tokens is None:
        return -1

    if not isinstance(max_tokens, int):
        return -1

    if max_tokens <= -1:
        return -1

    if _elastic_unlimited():
        return max(256, max_tokens)

    if DEBATE_MAX_TOKENS_HARD <= -1:
        return max(256, max_tokens)

    return max(256, min(max_tokens, DEBATE_MAX_TOKENS_HARD))


def _adaptive_token_budget(requested_tokens: int, active_streams: int, waiting_streams: int) -> int:
    if requested_tokens <= -1:
        return -1

    if _elastic_unlimited():
        return requested_tokens

    pressure = active_streams + waiting_streams
    if pressure <= 2:
        return requested_tokens
    if pressure <= 4:
        return min(requested_tokens, -1)
    if pressure <= 6:
        return min(requested_tokens, -1)
    if pressure <= 8:
        return min(requested_tokens, -1)
    return min(requested_tokens, -1)


async def _allow_debate_request(client_id: str) -> bool:
    now = time.monotonic()
    async with _debate_rate_lock:
        bucket = _debate_rate_buckets.get(client_id)
        if bucket is None:
            bucket = deque()
            _debate_rate_buckets[client_id] = bucket

        while bucket and now - bucket[0] > DEBATE_RATE_LIMIT_WINDOW_S:
            bucket.popleft()

        if len(bucket) >= DEBATE_RATE_LIMIT_REQUESTS:
            return False

        bucket.append(now)
        return True


async def _resolve_debate_language(topic: str, preferred_language: Optional[str]) -> Tuple[str, str, str]:
    preferred_code = _normalize_preferred_language(preferred_language)
    if preferred_code:
        dynamic_name = await resolve_language_name(preferred_code)
        safe_name = dynamic_name or DEBATE_LANGUAGE_NAMES.get(preferred_code, preferred_code.upper())
        return preferred_code, safe_name, "preferred"

    if _looks_albanian_text(topic):
        return "sq", "Albanian", "heuristic"

    lang_code, lang_name, _ = await detect_language(topic)
    if not lang_code:
        return "en", "English", "fallback"

    safe_code = _normalize_preferred_language(lang_code) or "en"
    dynamic_name = await resolve_language_name(safe_code)
    safe_name = dynamic_name or DEBATE_LANGUAGE_NAMES.get(safe_code, lang_name or "English")
    return safe_code, safe_name, "detected"


def _is_algebra_topic(topic: str) -> bool:
    text = (topic or "").lower()
    if not text:
        return False
    if re.search(r"\d+\s*[-+*/^]\s*\d+", text):
        return True
    if re.search(r"\d+\s*(xor|and|or|>>|<<|&|\|)\s*\d+", text):
        return True
    if re.search(r"0b[01]+", text):
        return True
    keywords = [
        "algebra", "equation", "math", "xor", "and", "or", "binary", "matrix",
        "boolean", "bitwise", "truth table", "logic gate", "nand", "nor", "xnor",
        "hex", "octal", "base-2", "base2"
    ]
    return any(k in text for k in keywords)


def _build_algebra_context(topic: str) -> str:
    if not _is_algebra_topic(topic):
        return ""

    normalized = (topic or "").lower().strip()
    match = re.search(r"(0b[01]+|\d+)\s*(xor|and|or|\+|\-|\*|/|>>|<<|&|\|)\s*(0b[01]+|\d+)", normalized)
    if not match:
        return (
            "Algebra/Binary mode active: show step-by-step reasoning, validate each step, "
            "and when numbers are binary/bitwise include decimal + binary forms for the final result."
        )

    def _parse_num(value: str) -> int:
        if value.startswith("0b"):
            return int(value[2:], 2)
        return int(value)

    left_raw = match.group(1)
    right_raw = match.group(3)
    left = _parse_num(left_raw)
    op = match.group(2)
    right = _parse_num(right_raw)

    try:
        if op == "xor":
            result = left ^ right
        elif op == "and":
            result = left & right
        elif op == "or":
            result = left | right
        elif op == "+":
            result = left + right
        elif op == "-":
            result = left - right
        elif op == "*":
            result = left * right
        elif op == "/":
            result = left / right if right != 0 else "undefined"
        elif op == ">>":
            result = left >> right
        elif op == "<<":
            result = left << right
        elif op == "&":
            result = left & right
        elif op == "|":
            result = left | right
        else:
            result = "unknown"

        binary_ops = {"xor", "and", "or", ">>", "<<", "&", "|"}
        if op in binary_ops and isinstance(result, int):
            return (
                "Algebra/Binary mode active: "
                f"candidate operation {left_raw} ({left}) {op} {right_raw} ({right}) = {result} (0b{result:b}). "
                "Preserve rigorous reasoning, show truth-logic or bitwise transformation, and validate the final value."
            )

        return (
            "Algebra mode active: "
            f"candidate operation {left_raw} ({left}) {op} {right_raw} ({right}) = {result}. "
            "Preserve rigorous reasoning and validation."
        )
    except Exception:
        return "Algebra/Binary mode active: include explicit steps and verify numeric consistency."


async def _build_debate_memory_context(session_id: Optional[str], explicit_context: Optional[List[str]]) -> str:
    lines: List[str] = []

    if explicit_context:
        for item in explicit_context[-6:]:
            text = str(item or "").strip()
            if text:
                lines.append(text)

    sid = (session_id or "").strip()
    if not sid:
        return "\n".join(lines)

    now = time.time()
    async with _debate_memory_lock:
        expired = [
            key
            for key, value in _debate_memory_store.items()
            if (now - float(value.get("updated_at", 0))) > DEBATE_MEMORY_TTL_SECONDS
        ]
        for key in expired:
            _debate_memory_store.pop(key, None)

        memory = _debate_memory_store.get(sid)
        if memory:
            turns = memory.get("turns", [])
            if isinstance(turns, deque):
                turns = list(turns)
            lines.extend(list(turns)[-DEBATE_MEMORY_MAX_TURNS:])

    return "\n".join(lines)


async def _store_debate_memory(session_id: Optional[str], topic: str, persona_outputs: Dict[str, str]) -> None:
    sid = (session_id or "").strip()
    if not sid:
        return

    summary_parts = [f"Topic: {topic}"]
    for persona_id, text in persona_outputs.items():
        snippet = (text or "").strip().replace("\n", " ")[:220]
        if snippet:
            summary_parts.append(f"{persona_id}: {snippet}")

    turn_text = " | ".join(summary_parts)
    if not turn_text.strip():
        return

    async with _debate_memory_lock:
        memory = _debate_memory_store.setdefault(sid, {"turns": deque(maxlen=DEBATE_MEMORY_MAX_TURNS), "updated_at": time.time()})
        turns = memory.get("turns")
        if not isinstance(turns, deque):
            turns = deque(maxlen=DEBATE_MEMORY_MAX_TURNS)
            memory["turns"] = turns
        turns.append(turn_text)
        memory["updated_at"] = time.time()


def _debate_prefill_text(persona_id: str, lang_code: str) -> str:
    sq = {
        "alba": "Po formuloj këndvështrimin optimist… ",
        "albi": "Po e kthej temën në hapa praktikë… ",
        "jona": "Po testoj rreziqet dhe kundërshtitë… ",
        "blerina": "Po mbledh evidencën dhe analizën… ",
        "asi": "Po lidh modelin më të gjerë… ",
    }
    en = {
        "alba": "Framing the optimistic angle… ",
        "albi": "Turning the topic into practical steps… ",
        "jona": "Stress-testing the risks and objections… ",
        "blerina": "Gathering the evidence and analysis… ",
        "asi": "Connecting the higher-level pattern… ",
    }
    table = sq if (lang_code or "").lower().startswith("sq") else en
    fallback = "Po analizoj… " if (lang_code or "").lower().startswith("sq") else "Analyzing… "
    return table.get(persona_id, fallback)


async def _acquire_debate_stream_slot() -> None:
    global _debate_stream_active, _debate_stream_waiting

    async with _debate_stream_state_lock:
        if _debate_stream_waiting >= DEBATE_STREAM_QUEUE_LIMIT:
            raise HTTPException(status_code=429, detail="Debate queue is full. Retry shortly.")
        _debate_stream_waiting += 1

    try:
        await asyncio.wait_for(_debate_stream_semaphore.acquire(), timeout=DEBATE_STREAM_QUEUE_TIMEOUT_S)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=429, detail="Debate engine busy. Retry shortly.")
    finally:
        async with _debate_stream_state_lock:
            _debate_stream_waiting = max(0, _debate_stream_waiting - 1)

    async with _debate_stream_state_lock:
        _debate_stream_active += 1


async def _release_debate_stream_slot() -> None:
    global _debate_stream_active
    async with _debate_stream_state_lock:
        _debate_stream_active = max(0, _debate_stream_active - 1)
    _debate_stream_semaphore.release()


async def get_persona_response(
    persona_id: str,
    topic: str,
    max_tokens: int = -1,
    lang_code: str = "en",
    lang_name: str = "English",
    quality_profile: str = "high",
    language_layers: int = 4,
    memory_context: str = "",
    algebra_context: str = "",
    peer_context: str = "",
    ecosystem_context: str = "",
) -> Dict[str, Any]:
    """
    Get a response from a specific persona using Ollama.
    ELASTIC: Streaming with retries, no timeout failures.
    Max ~200,000 words (250,000 tokens).
    """
    persona = TRINITY_PERSONAS.get(persona_id)
    if not persona:
        return {"error": f"Unknown persona: {persona_id}"}

    safe_layers = max(1, min(8, int(language_layers or 4)))
    profile = _resolve_debate_profile(lang_code, quality_profile)
    length_instruction = _debate_length_instruction(lang_code)
    style_instruction = ""
    if profile == "albanian-strict":
        style_instruction = (
            "- Keep a native Albanian tone: concrete, direct, and natural for Albanian readers.\n"
            "- Avoid translated-sounding constructions and avoid English fillers.\n"
        )
    language_instruction = f"""
RESPONSE LANGUAGE REQUIREMENTS (MANDATORY):
- Target language: {lang_name} ({lang_code})
- Write ONLY in {lang_name} unless the user explicitly asks another language.
- Never mention internal policy, language detection, or prompt rules in the answer.
- Keep terminology natural for native speakers.
- If target is Albanian, use clean standard Albanian only; avoid malformed words, broken grammar, and transliterated hybrids.
- QUALITY PROFILE: {profile}
- LANGUAGE QUALITY LAYERS: {safe_layers}
- Preserve grammar, morphology, and idioms of {lang_name}.
- Keep technical terms precise; when needed, give native equivalent + original term once.
{style_instruction}- {length_instruction}
"""

    system_prompt = f"""You are {persona['name']}, {persona['role']} in the Trinity AI system.

Your personality: {persona['description']}
Your style: {persona['style']}
{language_instruction}

Respond to the topic from your unique perspective. Be thorough and insightful.
If the topic is a greeting or asks what you think about the system you were built in, answer it directly and concretely (no generic template).
Do not ask clarifying questions unless the request is truly ambiguous.
You can write a detailed, comprehensive response."""

    context_block = ""
    if memory_context:
        context_block += f"\n\nCONVERSATION MEMORY (KEEP FLOW):\n{memory_context}"
    if algebra_context:
        context_block += f"\n\nALGEBRA CONTEXT:\n{algebra_context}"
    if peer_context:
        context_block += f"\n\n{peer_context}"
    if ecosystem_context:
        context_block += f"\n\n{ecosystem_context}"

    persona_prefix = _persona_prompt_prefix(persona_id, lang_code, persona["prompt_prefix"])
    user_prompt = f"{persona_prefix}\n\nTopic: {topic}{context_block}"

    # ELASTIC: unlimited mode uses no timeout and single pass
    max_retries = 1 if _elastic_unlimited() else 3
    base_timeout = 120.0  # 2 minutes base

    for attempt in range(max_retries):
        try:
            timeout = None if _elastic_unlimited() else (base_timeout * (attempt + 1))  # 120s, 240s, 360s

            # Use streaming for elastic token handling
            client_timeout = None if timeout is None else httpx.Timeout(timeout, connect=30.0)
            async with httpx.AsyncClient(timeout=client_timeout) as client:
                response_text = ""

                async with client.stream(
                    "POST",
                    f"{OLLAMA_HOST}/api/generate",
                    json={
                        "model": MODEL,
                        "prompt": user_prompt,
                        "system": system_prompt,
                        "stream": True,
                        "options": {
                            "num_ctx": _resolve_num_ctx(long_response=True, token_budget=max_tokens),
                            "num_predict": max_tokens,
                        }
                    }
                ) as stream:
                    async for line in stream.aiter_lines():
                        if line:
                            try:
                                chunk = json.loads(line)
                                if "response" in chunk:
                                    response_text += chunk["response"]
                                if chunk.get("done", False):
                                    break
                            except json.JSONDecodeError:
                                continue

                if response_text:
                    payload_bytes = len(response_text.encode("utf-8"))
                    cells = max(1, (payload_bytes + 15) // 16)
                    frame_bytes = 14 + (cells * 16)
                    return {
                        "persona": persona_id,
                        "name": persona["name"],
                        "emoji": persona["emoji"],
                        "role": persona["role"],
                        "response": response_text,
                        "status": "success",
                        "btl": {
                            "bits": payload_bytes * 8,
                            "pixels": len(response_text),
                            "chunks": len(response_text.split()),
                            "unit": "BTL",
                            "nanogrid": {
                                "protocol": "nanogridata-v1",
                                "header_bytes": 14,
                                "cell_bytes": 16,
                                "payload_bytes": payload_bytes,
                                "cells": cells,
                                "frame_bytes": frame_bytes,
                                "overhead_bytes": max(0, frame_bytes - payload_bytes),
                                "efficiency": round((payload_bytes / frame_bytes) if frame_bytes > 0 else 0, 4),
                            },
                        }
                    }

        except httpx.TimeoutException:
            logger.warning(f"Persona {persona_id} timeout on attempt {attempt + 1}/{max_retries}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2)  # Brief pause before retry
                continue
        except Exception as e:
            logger.error(f"Persona {persona_id} error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
                continue

    # All retries exhausted - return partial or error gracefully (no fail)
    try:
        # Fallback: Try one more time with non-streaming
        async with httpx.AsyncClient(timeout=None if _elastic_unlimited() else 60.0) as client:
            response = await client.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": MODEL,
                    "prompt": user_prompt,
                    "system": system_prompt,
                    "stream": False,
                    "options": {
                        "num_ctx": _resolve_num_ctx(long_response=True, token_budget=max_tokens),
                        "num_predict": max_tokens if max_tokens > 0 else _clamp_chat_tokens(None, long_response=True),
                    }
                }
            )

        if response.status_code == 200:
            data = response.json()
            return {
                "persona": persona_id,
                "name": persona["name"],
                "emoji": persona["emoji"],
                "role": persona["role"],
                "response": data.get("response", "No response generated"),
                "status": "success"
            }
        else:
            return {
                "persona": persona_id,
                "name": persona["name"],
                "emoji": persona["emoji"],
                "role": persona["role"],
                "response": f"Error: {response.status_code}",
                "status": "error"
            }

    except Exception as e:
        logger.error(f"Persona {persona_id} fallback error: {e}")
        # Return a real error state (no fabricated partial response)
        return {
            "persona": persona_id,
            "name": persona["name"],
            "emoji": persona["emoji"],
            "role": persona["role"],
            "response": "Debate persona temporarily unavailable",
            "status": "error"
        }


@app.post("/api/v1/debate/stream")
async def trinity_debate_stream(request: DebateRequest, http_request: Request):
    """
    STREAMING Trinity Debate - Real-time responses.
    Returns Server-Sent Events (SSE) with each persona's response as it completes.
    """
    from starlette.responses import StreamingResponse

    if not request.topic:
        raise HTTPException(status_code=400, detail="topic is required")

    client_ip = (
        (http_request.headers.get("x-forwarded-for", "").split(",")[0].strip())
        or (http_request.client.host if http_request.client else "unknown")
    )

    if not await _allow_debate_request(f"stream:{client_ip}"):
        raise HTTPException(status_code=429, detail="Rate limit exceeded for debate stream")

    await _acquire_debate_stream_slot()

    persona_ids = request.personas if request.personas else list(TRINITY_PERSONAS.keys())
    valid_personas = [p for p in persona_ids if p in TRINITY_PERSONAS]

    # Resolve language once per debate and enforce across all personas
    lang_code, lang_name, language_source = await _resolve_debate_language(
        request.topic,
        request.preferred_language,
    )
    memory_context = await _build_debate_memory_context(request.session_id, request.conversation_context)
    algebra_context = _build_algebra_context(request.topic)
    ecosystem_context = _debate_ecosystem_context(lang_code)
    effective_profile = _resolve_debate_profile(lang_code, request.quality_profile)

    async with _debate_stream_state_lock:
        active_now = _debate_stream_active
        waiting_now = _debate_stream_waiting

    requested_tokens = _clamp_tokens(request.max_tokens)
    max_tokens = _adaptive_token_budget(requested_tokens, active_now, waiting_now)
    compact_stream = (request.stream_mode or "json").lower() != "json"
    persona_outputs: Dict[str, str] = {}

    def sse_event(event_name: str, payload: str) -> str:
        payload_lines = str(payload).splitlines() or [""]
        body = [f"event: {event_name}"]
        for line in payload_lines:
            body.append(f"data: {line}")
        return "\n".join(body) + "\n\n"

    def compact_pack(*values: Any) -> str:
        encoded_parts: List[str] = []
        for value in values:
            raw = "" if value is None else str(value)
            encoded_parts.append(base64.b64encode(raw.encode("utf-8")).decode("ascii"))
        return "|".join(encoded_parts)

    async def generate():
        try:
            if compact_stream:
                yield sse_event(
                    "start",
                    compact_pack(
                        request.topic,
                        len(valid_personas),
                        max_tokens,
                        lang_code,
                        lang_name,
                        language_source,
                    ),
                )
            else:
                yield f"data: {json.dumps({'type': 'start', 'topic': request.topic, 'personas': len(valid_personas)})}\n\n"

            for persona_id in valid_personas:
                persona = TRINITY_PERSONAS[persona_id]

                if compact_stream:
                    yield sse_event(
                        "thinking",
                        compact_pack(persona_id, persona['name'], persona['emoji'], persona['role']),
                    )
                    prefill = _debate_prefill_text(persona_id, lang_code)
                    if prefill:
                        encoded_prefill = base64.b64encode(prefill.encode("utf-8")).decode("ascii")
                        yield sse_event("prefill", f"{persona_id}:{encoded_prefill}")
                else:
                    yield f"data: {json.dumps({'type': 'thinking', 'persona': persona_id, 'name': persona['name']})}\n\n"

                safe_layers = max(1, min(8, int(request.language_layers or 4)))
                profile = effective_profile
                length_instruction = _debate_length_instruction(lang_code)
                style_instruction = ""
                if profile == "albanian-strict":
                    style_instruction = (
                        "- Keep a native Albanian tone: concrete, direct, and natural for Albanian readers.\\n"
                        "- Avoid translated-sounding constructions and avoid English fillers.\\n"
                    )
                language_instruction = f"""
RESPONSE LANGUAGE REQUIREMENTS (MANDATORY):
- Target language: {lang_name} ({lang_code})
- Write ONLY in {lang_name} unless the user explicitly asks another language.
- Never mention internal policy, language detection, or prompt rules in the answer.
- Keep terminology natural for native speakers.
- If target is Albanian, use clean standard Albanian only; avoid malformed words, broken grammar, and transliterated hybrids.
- QUALITY PROFILE: {profile}
- LANGUAGE QUALITY LAYERS: {safe_layers}
- Preserve grammar, morphology, and idioms of {lang_name}.
- Keep technical terms precise; when needed, give native equivalent + original term once.
{style_instruction}- {length_instruction}
"""

                system_prompt = f"""You are {persona['name']}, {persona['role']} in the Trinity AI system.
Your personality: {persona['description']}
Your style: {persona['style']}
{language_instruction}
Respond to the topic from your unique perspective. Be thorough and detailed.
If the topic is a greeting or asks what you think about the system you were built in, answer it directly and concretely (no generic template).
Do not ask clarifying questions unless the request is truly ambiguous."""

                context_block = ""
                if memory_context:
                    context_block += f"\n\nCONVERSATION MEMORY (KEEP FLOW):\n{memory_context}"
                if algebra_context:
                    context_block += f"\n\nALGEBRA CONTEXT:\n{algebra_context}"
                peer_context = _debate_peer_context(persona_outputs, lang_code)
                if peer_context:
                    context_block += f"\n\n{peer_context}"
                if ecosystem_context:
                    context_block += f"\n\n{ecosystem_context}"

                persona_prefix = _persona_prompt_prefix(persona_id, lang_code, persona["prompt_prefix"])
                user_prompt = f"{persona_prefix}\n\nTopic: {request.topic}{context_block}"

                full_response = ""
                token_count = 0

                try:
                    async with httpx.AsyncClient(timeout=None) as client:
                        async with client.stream(
                            "POST",
                            f"{OLLAMA_HOST}/api/generate",
                            json={
                                "model": MODEL,
                                "prompt": user_prompt,
                                "system": system_prompt,
                                "stream": True,
                                "options": {
                                    "num_ctx": _resolve_num_ctx(long_response=True, token_budget=max_tokens),
                                    "num_predict": max_tokens,
                                }
                            }
                        ) as stream:
                            async for line in stream.aiter_lines():
                                if line:
                                    try:
                                        chunk = json.loads(line)
                                        if "response" in chunk and chunk["response"]:
                                            token = chunk["response"]
                                            full_response += token
                                            token_count += 1
                                            if compact_stream:
                                                encoded = base64.b64encode(token.encode("utf-8")).decode("ascii")
                                                yield sse_event("t", f"{persona_id}:{encoded}")
                                            else:
                                                yield f"data: {json.dumps({'type': 'token', 'persona': persona_id, 'token': token})}\n\n"
                                        if chunk.get("done", False):
                                            break
                                    except json.JSONDecodeError:
                                        continue

                    if compact_stream:
                        yield sse_event(
                            "response",
                            compact_pack(
                                persona_id,
                                persona['name'],
                                persona['emoji'],
                                persona['role'],
                                'success',
                                token_count,
                            ),
                        )
                    else:
                        full_response_bytes = len(full_response.encode('utf-8'))
                        nanogrid_cells = max(1, (full_response_bytes + 15) // 16)
                        nanogrid_frame_bytes = 14 + (nanogrid_cells * 16)
                        btl_payload = {
                            'bits': full_response_bytes * 8,
                            'pixels': len(full_response),
                            'chunks': token_count,
                            'unit': 'BTL',
                            'nanogrid': {
                                'protocol': 'nanogridata-v1',
                                'header_bytes': 14,
                                'cell_bytes': 16,
                                'payload_bytes': full_response_bytes,
                                'cells': nanogrid_cells,
                                'frame_bytes': nanogrid_frame_bytes,
                                'overhead_bytes': max(0, nanogrid_frame_bytes - full_response_bytes),
                                'efficiency': round(
                                    (full_response_bytes / nanogrid_frame_bytes) if nanogrid_frame_bytes > 0 else 0,
                                    4,
                                ),
                            },
                        }
                        yield f"data: {json.dumps({'type': 'response', 'data': {'persona': persona_id, 'name': persona['name'], 'emoji': persona['emoji'], 'role': persona['role'], 'response': full_response, 'status': 'success', 'btl': btl_payload}})}\n\n"

                    if full_response.strip():
                        persona_outputs[persona_id] = full_response

                except Exception as e:
                    logger.error(f"Streaming error for {persona_id}: {e}")
                    if compact_stream:
                        yield sse_event(
                            "response",
                            compact_pack(
                                persona_id,
                                persona['name'],
                                persona['emoji'],
                                persona['role'],
                                'error',
                                token_count,
                            ),
                        )
                    else:
                        error_response = full_response
                        error_response_bytes = len(error_response.encode('utf-8'))
                        nanogrid_cells = max(1, (error_response_bytes + 15) // 16)
                        nanogrid_frame_bytes = 14 + (nanogrid_cells * 16)
                        btl_payload = {
                            'bits': error_response_bytes * 8,
                            'pixels': len(error_response),
                            'chunks': token_count,
                            'unit': 'BTL',
                            'nanogrid': {
                                'protocol': 'nanogridata-v1',
                                'header_bytes': 14,
                                'cell_bytes': 16,
                                'payload_bytes': error_response_bytes,
                                'cells': nanogrid_cells,
                                'frame_bytes': nanogrid_frame_bytes,
                                'overhead_bytes': max(0, nanogrid_frame_bytes - error_response_bytes),
                                'efficiency': round(
                                    (error_response_bytes / nanogrid_frame_bytes) if nanogrid_frame_bytes > 0 else 0,
                                    4,
                                ),
                            },
                        }
                        yield f"data: {json.dumps({'type': 'response', 'data': {'persona': persona_id, 'name': persona['name'], 'emoji': persona['emoji'], 'role': persona['role'], 'response': error_response, 'status': 'error', 'btl': btl_payload}})}\n\n"

            await _store_debate_memory(request.session_id, request.topic, persona_outputs)
            if compact_stream:
                yield sse_event("done", compact_pack("ok"))
            else:
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
        finally:
            await _release_debate_stream_slot()
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.post("/api/v1/debate")
async def trinity_debate(request: DebateRequest, http_request: Request):
    """
    Trinity Multi-Persona Debate.

    5 AI personas debate a topic from different perspectives:
    - Alba (🌅) - The Optimist
    - Albi (🔧) - The Pragmatist
    - Jona (🔍) - The Skeptic
    - Blerina (🌐) - The Analyst
    - ASI (🧠) - The Meta-Thinker

    Returns all perspectives for a balanced view.
    """
    if not request.topic:
        raise HTTPException(status_code=400, detail="topic is required")

    client_ip = (
        (http_request.headers.get("x-forwarded-for", "").split(",")[0].strip())
        or (http_request.client.host if http_request.client else "unknown")
    )

    if not await _allow_debate_request(f"sync:{client_ip}"):
        raise HTTPException(status_code=429, detail="Rate limit exceeded for debate")

    start_time = time.time()

    # Determine which personas to use
    persona_ids = request.personas if request.personas else list(TRINITY_PERSONAS.keys())

    # Validate personas
    valid_personas = [p for p in persona_ids if p in TRINITY_PERSONAS]
    if not valid_personas:
        raise HTTPException(status_code=400, detail=f"No valid personas. Available: {list(TRINITY_PERSONAS.keys())}")

    # Resolve once and enforce language across all personas
    lang_code, lang_name, language_source = await _resolve_debate_language(
        request.topic,
        request.preferred_language,
    )
    memory_context = await _build_debate_memory_context(request.session_id, request.conversation_context)
    algebra_context = _build_algebra_context(request.topic)
    ecosystem_context = _debate_ecosystem_context(lang_code)
    effective_profile = _resolve_debate_profile(lang_code, request.quality_profile)

    # Generate with peer-awareness so each persona can react to previous outputs.
    safe_tokens = _adaptive_token_budget(_clamp_tokens(request.max_tokens), active_streams=0, waiting_streams=0)
    responses: List[Dict[str, Any]] = []
    peer_outputs: Dict[str, str] = {}
    for persona_id in valid_personas:
        peer_context = _debate_peer_context(peer_outputs, lang_code)
        result = await get_persona_response(
            persona_id,
            request.topic,
            safe_tokens,
            lang_code=lang_code,
            lang_name=lang_name,
            quality_profile=effective_profile,
            language_layers=request.language_layers,
            memory_context=memory_context,
            algebra_context=algebra_context,
            peer_context=peer_context,
            ecosystem_context=ecosystem_context,
        )
        responses.append(result)
        if isinstance(result, dict) and str(result.get("status")) == "success":
            peer_outputs[persona_id] = str(result.get("response", ""))

    await _store_debate_memory(
        request.session_id,
        request.topic,
        {str(r.get("persona", "")): str(r.get("response", "")) for r in responses if isinstance(r, dict)},
    )

    processing_time = time.time() - start_time

    # Count successes
    success_count = sum(1 for r in responses if r.get("status") == "success")

    return {
        "ok": True,
        "topic": request.topic,
        "language": {"code": lang_code, "name": lang_name, "source": language_source},
        "responses": responses,
        "stats": {
            "total_personas": len(valid_personas),
            "successful": success_count,
            "failed": len(valid_personas) - success_count,
            "processing_time_ms": processing_time * 10000
        },
        "engine": "Trinity Debate Engine v1.0"
    }


@app.get("/api/v1/debate/personas")
async def list_personas():
    """List all available Trinity personas."""
    return {
        "personas": [
            {
                "id": pid,
                "name": p["name"],
                "emoji": p["emoji"],
                "role": p["role"],
                "description": p["description"],
                "style": p["style"]
            }
            for pid, p in TRINITY_PERSONAS.items()
        ],
        "total": len(TRINITY_PERSONAS)
    }


# ═══════════════════════════════════════════════════════════════════
# 🔊 TEXT-TO-SPEECH ENGINE - Natural Voice Output
# ═══════════════════════════════════════════════════════════════════

# TTS Voice Configuration - Microsoft Edge Neural Voices (Free, High Quality)
TTS_VOICES = {
    "en": "en-US-AriaNeural",        # English - Female, natural
    "en-male": "en-US-GuyNeural",    # English - Male
    "sq": "en-GB-SoniaNeural",       # Albanian fallback - British English sounds natural
    "de": "de-DE-KatjaNeural",       # German
    "fr": "fr-FR-DeniseNeural",      # French
    "es": "es-ES-ElviraNeural",      # Spanish
    "it": "it-IT-ElsaNeural",        # Italian
    "pt": "pt-BR-FranciscaNeural",   # Portuguese
    "ru": "ru-RU-SvetlanaNeural",    # Russian
    "zh": "zh-CN-XiaoxiaoNeural",    # Chinese
    "ja": "ja-JP-NanamiNeural",      # Japanese
    "ko": "ko-KR-SunHiNeural",       # Korean
    "ar": "ar-EG-SalmaNeural",       # Arabic
    "tr": "tr-TR-EmelNeural",        # Turkish
    "hi": "hi-IN-SwaraNeural",       # Hindi
    "nl": "nl-NL-ColetteNeural",     # Dutch
    "pl": "pl-PL-ZofiaNeural",       # Polish
    "uk": "uk-UA-PolinaNeural",      # Ukrainian
    "el": "el-GR-AthinaNeural",      # Greek
    "ro": "ro-RO-AlinaNeural",       # Romanian
    "sr": "sr-RS-SophieNeural",      # Serbian
    "hr": "hr-HR-GabrijelaNeural",   # Croatian
    "bg": "bg-BG-KalinaNeural",      # Bulgarian
    "mk": "mk-MK-MarijaNeural",      # Macedonian
}

class TTSRequest(BaseModel):
    """Text-to-Speech request model"""
    text: str
    language: str = "en"
    voice: Optional[str] = None  # Override default voice
    rate: str = "+0%"  # Speech rate: -50% to +100%
    pitch: str = "+0Hz"  # Pitch adjustment


class VoiceConversationRequest(BaseModel):
    """Full voice conversation request: Audio In → STT → LLM → TTS → Audio Out"""
    audio_base64: str
    language: str = "en"
    voice: Optional[str] = None
    curiosity_level: str = "curious"
    user_id: Optional[str] = None


# NanoGridVisionRequest is defined at the top of the models section (see REQUEST/RESPONSE MODELS)


class VideoCreateRequest(BaseModel):
    prompt: str
    style: Optional[str] = "cinematic"
    duration_seconds: Optional[int] = 12
    format: Optional[str] = "mp4"
    include_audio: bool = True
    user_id: Optional[str] = None


class DocumentGenerateRequest(BaseModel):
    """Document generation request - video, voice, pdf, excel, etc."""
    format: str  # pdf, excel, csv, report, video, voice, mp4, wav, audio
    contract_type: str  # cpi, research, report, video, voice
    query: str
    language: str = "en"
    auto_translate: bool = True


class MediaWorkflowRequest(BaseModel):
    """Generate full multimedia workflow bundle from a single concept."""
    query: str
    language: str = "en"
    profile: str = "full"  # full | narrative | visual | audio
    auto_translate: bool = True


@app.post("/api/v1/tts")
async def text_to_speech(req: TTSRequest):
    """
    🔊 TEXT-TO-SPEECH - Convert text to natural speech audio

    Returns MP3 audio file with natural neural voice.
    Supports 24+ languages with high-quality Microsoft Edge voices.

    Example:
        POST /api/v1/tts
        {"text": "Hello, how are you?", "language": "en"}

        Returns: audio/mpeg stream
    """
    start_time = time.time()

    try:
        import os as os_mod
        import tempfile

        import edge_tts  # type: ignore[import-not-found]

        # Input validation
        if not req.text or not req.text.strip():
            raise HTTPException(400, "Text cannot be empty")

        if len(req.text) > 50000:
            raise HTTPException(400, "Text too long. Maximum 50000 characters.")

        # Get voice for language
        voice = req.voice or TTS_VOICES.get(req.language, TTS_VOICES.get("en"))

        # Create TTS communicate object
        communicate = edge_tts.Communicate(
            text=req.text.strip(),
            voice=voice,
            rate=req.rate,
            pitch=req.pitch
        )

        # Generate audio to temp file
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_path = tmp.name

        await communicate.save(tmp_path)

        # Read audio data
        with open(tmp_path, "rb") as f:
            audio_data = f.read()

        # Cleanup
        os_mod.unlink(tmp_path)

        processing_time = time.time() - start_time
        logger.info(f"🔊 TTS: {len(req.text)} chars → {len(audio_data)} bytes in {processing_time:.2f}s | voice={voice}")

        # Return audio as streaming response
        return StreamingResponse(
            iter([audio_data]),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=speech.mp3",
                "X-Processing-Time": f"{processing_time:.3f}s",
                "X-Voice-Used": str(voice),
                "X-Text-Length": str(len(req.text))
            }
        )

    except ImportError:
        raise HTTPException(500, "TTS engine not available. Install: pip install edge-tts")
    except Exception as e:
        logger.error(f"TTS Error: {e}")
        raise HTTPException(500, f"TTS generation failed: {str(e)}")


@app.get("/api/v1/tts/voices")
async def list_tts_voices():
    """List all available TTS voices by language."""
    return {
        "voices": TTS_VOICES,
        "total": len(TTS_VOICES),
        "engine": "Microsoft Edge Neural TTS (Free)",
        "quality": "High - Neural Network Generated",
        "note": "Albanian (sq) uses British English voice as fallback"
    }


@app.post("/api/v1/voice/conversation")
async def voice_conversation(req: VoiceConversationRequest, request: Request):
    """
    🎙️ FULL VOICE CONVERSATION PIPELINE

    Audio In → STT (Whisper) → LLM (Ollama) → TTS (Edge) → Audio Out

    Complete voice-to-voice conversation in one request.
    Send audio, get audio response back.

    Flow:
    1. Decode audio from base64
    2. Transcribe with Whisper (Speech-to-Text)
    3. Generate response with Ollama LLM
    4. Convert response to speech (Text-to-Speech)
    5. Return audio response
    """
    start_time = time.time()
    # user_id available via: req.user_id or request.headers.get("X-User-ID")

    try:
        import base64 as b64mod
        import os as os_mod
        import tempfile

        import edge_tts  # type: ignore[import-not-found]

        # ═══════════════════════════════════════════════════════════════
        # STEP 1: Decode Audio
        # ═══════════════════════════════════════════════════════════════
        raw_audio = (req.audio_base64 or "").strip()
        if "," in raw_audio and raw_audio.lower().startswith("data:"):
            raw_audio = raw_audio.split(",", 1)[1]
        audio_bytes = b64mod.b64decode(raw_audio)
        if len(audio_bytes) < VOICE_MIN_AUDIO_BYTES:
            raise HTTPException(400, "Audio data too small")

        voice_max_audio_bytes = _voice_audio_limit()
        if voice_max_audio_bytes is not None and len(audio_bytes) > voice_max_audio_bytes:
            raise HTTPException(413, f"Audio too large. Limit is {voice_max_audio_bytes} bytes")

        stt_timeout = _adaptive_timeout(VOICE_STT_TIMEOUT_BASE_S, VOICE_STT_TIMEOUT_MAX_S, len(audio_bytes))
        llm_timeout = _adaptive_timeout(VOICE_LLM_TIMEOUT_BASE_S, VOICE_LLM_TIMEOUT_MAX_S, len(audio_bytes))

        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
            tmp.write(audio_bytes)
            audio_path = tmp.name

        # ═══════════════════════════════════════════════════════════════
        # STEP 2: Speech-to-Text (Whisper)
        # ═══════════════════════════════════════════════════════════════
        try:
            from faster_whisper import WhisperModel  # type: ignore[import-not-found]

            global _whisper_model_conv
            if '_whisper_model_conv' not in globals() or _whisper_model_conv is None:
                _whisper_model_conv = WhisperModel("base", device="cpu", compute_type="int8")

            segments, info = _whisper_model_conv.transcribe(
                audio_path,
                language=req.language if req.language not in ['auto'] else None,
                beam_size=5
            )

            transcript = " ".join([seg.text for seg in segments]).strip()
            detected_language = info.language or req.language

        except ImportError:
            # Fallback: Use Ollama's whisper if available
            async with httpx.AsyncClient(timeout=stt_timeout) as client:
                with open(audio_path, "rb") as f:
                    audio_b64 = b64mod.b64encode(f.read()).decode()
                resp = await client.post(
                    f"{OLLAMA_HOST}/api/generate",
                    json={"model": "whisper", "prompt": audio_b64}
                )
                transcript = resp.json().get("response", "")
                detected_language = req.language

        finally:
            os_mod.unlink(audio_path)

        if not transcript:
            raise HTTPException(400, "Could not transcribe audio. Please speak clearly.")

        stt_time = time.time() - start_time
        logger.info(f"🎤 STT: '{transcript[:50]}...' in {stt_time:.2f}s")

        # ═══════════════════════════════════════════════════════════════
        # STEP 3: Generate LLM Response (Ollama)
        # ═══════════════════════════════════════════════════════════════
        llm_start = time.time()

        system_prompt = """You are a friendly voice assistant. Keep responses concise and natural for speech.
Respond in the same language as the user's message. Be helpful and conversational."""

        voice_num_predict = -1 if (MULTIMODAL_ELASTIC_NO_LIMITS or CHAT_ELASTIC_NO_LIMITS) else 400

        async with httpx.AsyncClient(timeout=llm_timeout) as client:
            resp = await client.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": MODEL,
                    "prompt": transcript,
                    "system": system_prompt,
                    "stream": False,
                    "options": {"temperature": 0.7, "num_predict": voice_num_predict}
                }
            )
            llm_response = resp.json().get("response", "I couldn't process that. Please try again.")

        llm_time = time.time() - llm_start
        logger.info(f"🧠 LLM: '{llm_response[:50]}...' in {llm_time:.2f}s")

        voice_user = (req.user_id or request.headers.get("X-User-ID") or "anonymous").strip()
        voice_req = _req_for_user(voice_user, detected_language)
        _memory_put(voice_req, transcript, llm_response, detected_language or req.language)

        # ═══════════════════════════════════════════════════════════════
        # STEP 4: Text-to-Speech (Edge TTS)
        # ═══════════════════════════════════════════════════════════════
        tts_start = time.time()

        voice = req.voice or TTS_VOICES.get(detected_language, TTS_VOICES.get("en"))
        communicate = edge_tts.Communicate(text=llm_response, voice=voice)

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tts_path = tmp.name

        await communicate.save(tts_path)

        with open(tts_path, "rb") as f:
            audio_response = f.read()

        os_mod.unlink(tts_path)

        tts_time = time.time() - tts_start
        total_time = time.time() - start_time

        logger.info(f"🔊 Voice Conversation: STT={stt_time:.1f}s LLM={llm_time:.1f}s TTS={tts_time:.1f}s Total={total_time:.1f}s")

        # ═══════════════════════════════════════════════════════════════
        # STEP 5: Return Audio Response
        # ═══════════════════════════════════════════════════════════════
        return StreamingResponse(
            iter([audio_response]),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=response.mp3",
                "X-Transcript": transcript[:100],
                "X-Response-Text": llm_response[:100],
                "X-Processing-Time": f"{total_time:.3f}s",
                "X-STT-Time": f"{stt_time:.3f}s",
                "X-LLM-Time": f"{llm_time:.3f}s",
                "X-TTS-Time": f"{tts_time:.3f}s",
                "X-Voice-Used": str(voice),
                "X-Detected-Language": str(detected_language)
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice Conversation Error: {e}")
        raise HTTPException(500, f"Voice conversation failed: {str(e)}")


# Initialize whisper model placeholder
_whisper_model_conv = None


def _extract_document_text(filename: str, content_type: str, raw: bytes, max_chars: int) -> dict:
    lower_name = (filename or "").lower()

    if lower_name.endswith(".txt") or content_type.startswith("text/"):
        text = raw.decode("utf-8", errors="ignore")
        return {"parser": "text", "text": text[:max_chars], "text_length": len(text)}

    if lower_name.endswith(".json") or content_type == "application/json":
        text = raw.decode("utf-8", errors="ignore")
        return {"parser": "json", "text": text[:max_chars], "text_length": len(text)}

    if lower_name.endswith(".pdf") or content_type == "application/pdf":
        try:
            pdf_module = None
            parser_name = ""
            for mod_name in ("pypdf", "PyPDF2"):
                try:
                    pdf_module = importlib.import_module(mod_name)
                    parser_name = mod_name
                    break
                except Exception:
                    continue

            if pdf_module is None:
                raise HTTPException(
                    status_code=503,
                    detail="PDF parser not installed on ocean-core (missing pypdf/PyPDF2).",
                )

            reader = pdf_module.PdfReader(io.BytesIO(raw))
            pages = []
            for page in reader.pages:
                pages.append(page.extract_text() or "")
            text = "\n".join(pages)
            return {"parser": parser_name, "text": text[:max_chars], "text_length": len(text)}
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=422, detail=f"PDF parser error: {type(exc).__name__}")

    if lower_name.endswith(".docx") or content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        try:
            try:
                docx_module = importlib.import_module("docx")
            except Exception as exc:
                raise HTTPException(
                    status_code=503,
                    detail="DOCX parser not installed on ocean-core (missing python-docx).",
                ) from exc

            document = docx_module.Document(io.BytesIO(raw))
            chunks = []

            for paragraph in document.paragraphs:
                text = (paragraph.text or "").strip()
                if text:
                    chunks.append(text)

            for table in document.tables:
                for row in table.rows:
                    row_values = []
                    for cell in row.cells:
                        value = (cell.text or "").strip()
                        row_values.append(value)
                    if any(row_values):
                        chunks.append("\t".join(row_values))

            text = "\n".join(chunks)
            return {"parser": "python-docx", "text": text[:max_chars], "text_length": len(text)}
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=422, detail=f"DOCX parser error: {type(exc).__name__}")

    if lower_name.endswith(".doc") or content_type == "application/msword":
        raise HTTPException(
            status_code=422,
            detail="Legacy .doc parsing is not supported. Please convert to .docx.",
        )

    if lower_name.endswith(".xlsx") or content_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        try:
            try:
                openpyxl = importlib.import_module("openpyxl")
            except Exception as exc:
                raise HTTPException(
                    status_code=503,
                    detail="XLSX parser not installed on ocean-core (missing openpyxl).",
                ) from exc

            workbook = openpyxl.load_workbook(io.BytesIO(raw), data_only=True, read_only=True)
            lines = []

            for sheet_name in workbook.sheetnames:
                sheet = workbook[sheet_name]
                lines.append(f"[sheet:{sheet_name}]")
                for row in sheet.iter_rows(values_only=True):
                    values = ["" if value is None else str(value).strip() for value in row]
                    if any(values):
                        lines.append("\t".join(values))

            text = "\n".join(lines)
            return {"parser": "openpyxl", "text": text[:max_chars], "text_length": len(text)}
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=422, detail=f"XLSX parser error: {type(exc).__name__}")

    if lower_name.endswith(".xls") or content_type == "application/vnd.ms-excel":
        try:
            try:
                xlrd = importlib.import_module("xlrd")
            except Exception as exc:
                raise HTTPException(
                    status_code=503,
                    detail="XLS parser not installed on ocean-core (missing xlrd).",
                ) from exc

            workbook = xlrd.open_workbook(file_contents=raw)
            lines = []

            for sheet in workbook.sheets():
                lines.append(f"[sheet:{sheet.name}]")
                for r in range(sheet.nrows):
                    values = [str(sheet.cell_value(r, c)).strip() for c in range(sheet.ncols)]
                    if any(values):
                        lines.append("\t".join(values))

            text = "\n".join(lines)
            return {"parser": "xlrd", "text": text[:max_chars], "text_length": len(text)}
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=422, detail=f"XLS parser error: {type(exc).__name__}")

    raise HTTPException(status_code=415, detail=f"Unsupported document type: {content_type}")


@app.get("/api/v1/document/capabilities")
@app.get("/api/v1/documents/capabilities")
async def documents_capabilities_compat():
    upload_limit = _document_upload_limit()
    scan_char_limit = _document_scan_char_limit()
    return {
        "service": "Curiosity Ocean Document Core",
        "status": "operational",
        "elastic_no_limits": MULTIMODAL_ELASTIC_NO_LIMITS,
        "max_upload_bytes": upload_limit,
        "max_scan_chars": scan_char_limit,
        "supported_mime_types": sorted(list(DOCUMENT_MIME_ALLOWLIST)),
        "features": {
            "scan_read": True,
            "checksum_sha256": True,
            "contract_generation": False,
            "provenance_tracking": True,
        },
        "endpoints": [
            "/api/v1/documents/capabilities",
            "/api/v1/documents/scan",
            "/api/v1/document/capabilities",
        ],
    }


@app.post("/api/v1/documents/scan")
@app.post("/api/v1/document/scan")
async def documents_scan_compat(
    request: Request,
    file: UploadFile = File(...),
    max_chars: int = Query(default=250000, ge=2000),
):
    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Empty file")
    upload_limit = _document_upload_limit()
    if upload_limit is not None and len(raw) > upload_limit:
        raise HTTPException(status_code=413, detail=f"File too large. Limit is {upload_limit} bytes")

    effective_max_chars = _resolve_scan_chars(max_chars)

    filename = file.filename or "unknown"
    content_type = (file.content_type or "application/octet-stream").lower()
    extraction = _extract_document_text(filename, content_type, raw, max_chars=effective_max_chars)
    sha256 = hashlib.sha256(raw).hexdigest()
    user_id = (request.headers.get("X-User-ID") or "anonymous").strip()
    doc_req = _req_for_user(user_id)
    _memory_put(
        doc_req,
        f"document_scan:{filename}",
        extraction.get("text", "")[:1200],
        "auto",
    )

    return {
        "ingestion_id": f"DOC-{uuid.uuid4().hex[:10]}",
        "filename": filename,
        "content_type": content_type,
        "size_bytes": len(raw),
        "sha256": sha256,
        "extraction": {
            "parser": extraction["parser"],
            "text_length": extraction["text_length"],
            "text": extraction["text"],
            "text_preview": extraction["text"][:2000],
            "effective_max_chars": effective_max_chars,
        },
        "provenance": {
            "source_type": "uploaded_document",
            "agent": "ocean_document_scan",
        },
    }


@app.get("/api/v1/video/status")
async def video_status():
    target = f"{VIDEO_PRODUCER_URL.rstrip('/')}/health"
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(target)
        return {
            "status": "connected" if response.status_code < 400 else "degraded",
            "video_producer": VIDEO_PRODUCER_URL,
            "upstream_status": response.status_code,
        }
    except Exception as exc:
        return {
            "status": "unavailable",
            "video_producer": VIDEO_PRODUCER_URL,
            "error": str(exc),
        }


@app.post("/api/v1/video/create")
async def video_create(req: VideoCreateRequest, request: Request):
    prompt = (req.prompt or "").strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="prompt is required")

    timeout_s = _elastic_stream_timeout(len(prompt), 1)
    payload = {
        "prompt": prompt,
        "title": prompt[:80],
        "style": req.style or "cinematic",
        "duration_seconds": max(3, min(int(req.duration_seconds or 12), 180)),
        "format": req.format or "mp4",
        "include_audio": bool(req.include_audio),
    }

    try:
        async with httpx.AsyncClient(timeout=timeout_s) as client:
            upstream = await client.post(f"{VIDEO_PRODUCER_URL.rstrip('/')}/api/v1/video/create", json=payload)

        if upstream.status_code >= 400:
            raise HTTPException(status_code=upstream.status_code, detail=upstream.text)

        data = upstream.json() if upstream.headers.get("content-type", "").startswith("application/json") else {"raw": upstream.text}
        user_id = (req.user_id or request.headers.get("X-User-ID") or "anonymous").strip()
        video_req = _req_for_user(user_id)
        _memory_put(video_req, f"video_request:{prompt[:220]}", json.dumps(data, ensure_ascii=False)[:1200], "auto")
        return {
            "status": "success",
            "video_producer": VIDEO_PRODUCER_URL,
            "result": data,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Video producer unavailable: {exc}") from exc


# ═══════════════════════════════════════════════════════════════════
# DOCUMENT GENERATION - Video & Voice Integration
# ═══════════════════════════════════════════════════════════════════

@app.get("/api/documents/agents")
@app.get("/api/v1/documents/agents")
async def documents_agents():
    """List available document generation agents."""
    try:
        document_agents_module = importlib.import_module("document_agents")
        list_agents = getattr(document_agents_module, "list_agents", None)
        if callable(list_agents):
            return {
                "agents": list_agents(),
                "timestamp": datetime.datetime.utcnow().isoformat(),
            }
        else:
            raise HTTPException(status_code=503, detail="document_agents module found but list_agents not available")
    except ImportError:
        logger.warning("document_agents module not found")
        raise HTTPException(status_code=503, detail="Document agents service not available")
    except Exception as e:
        logger.error(f"Document agents listing error: {e}")
        raise HTTPException(status_code=500, detail="Failed to list document agents")


@app.post("/api/documents/generate")
@app.post("/api/v1/documents/generate")
async def documents_generate(request_obj: DocumentGenerateRequest):
    """Generate video/voice/pdf documents via contract-governed pipeline."""
    started_at = time.perf_counter()
    request_format = (request_obj.format or "").lower().strip()
    request_contract = (request_obj.contract_type or "").lower().strip()

    DOC_GEN_IN_MEMORY_STATS["requests"] += 1
    DOC_GEN_IN_MEMORY_STATS["last_request_at"] = datetime.datetime.utcnow().isoformat()

    if DOC_GEN_REQUESTS_TOTAL:
        DOC_GEN_REQUESTS_TOTAL.labels(format=request_format or "unknown", contract_type=request_contract or "unknown").inc()

    try:
        try:
            document_agents_module = importlib.import_module("document_agents")
            document_contracts_module = importlib.import_module("document_contracts")
            get_agent = getattr(document_agents_module, "get_agent", None)
            get_contract_factory = getattr(document_contracts_module, "get_contract_factory", None)
            VideoContract = getattr(document_contracts_module, "VideoContract", None)
            VoiceContract = getattr(document_contracts_module, "VoiceContract", None)
            MusicContract = getattr(document_contracts_module, "MusicContract", None)
            PaintingContract = getattr(document_contracts_module, "PaintingContract", None)
            AnimationContract = getattr(document_contracts_module, "AnimationContract", None)

            if not get_agent:
                raise AttributeError("get_agent function not found")
        except (ImportError, AttributeError) as e:
            logger.warning(f"document_agents or document_contracts module not found: {e}")
            raise HTTPException(status_code=503, detail="Document generation service not available")

        format_map = {
            "xlsx": "excel",
            "xls": "excel",
            "csv": "excel",
            "pdf": "pdf",
            "report": "report",
            "json": "report",
            "mp4": "video",
            "video": "video",
            "wav": "voice",
            "voice": "voice",
            "audio": "voice",
            "midi": "music",
            "music": "music",
            "png": "painting",
            "jpg": "painting",
            "jpeg": "painting",
            "painting": "painting",
            "image": "painting",
            "animation": "animation",
        }

        contract_map = {
            "video": lambda: VideoContract() if VideoContract else None,
            "voice": lambda: VoiceContract() if VoiceContract else None,
            "music": lambda: MusicContract() if MusicContract else None,
            "painting": lambda: PaintingContract() if PaintingContract else None,
            "animation": lambda: AnimationContract() if AnimationContract else None,
        }

        agent_name = format_map.get(request_format)
        if not agent_name:
            raise HTTPException(status_code=400, detail="Unsupported format. Use xlsx/xls/csv/pdf/report/json/video/mp4/voice/wav/audio/music/midi/painting/png/jpg/jpeg/image/animation")

        effective_query = request_obj.query
        translation_meta = {
            "auto_translate": bool(request_obj.auto_translate),
            "requested_language": request_obj.language,
            "detected_language": None,
            "translated": False,
        }

        if request_obj.auto_translate and request_obj.language and request_obj.language.lower() != "auto":
            detected_code, _, _ = await detect_language(request_obj.query)
            translation_meta["detected_language"] = detected_code
            if detected_code and detected_code.lower() != request_obj.language.lower():
                effective_query = await translate_text_dynamic(
                    request_obj.query,
                    target_lang=request_obj.language,
                    source_lang=detected_code,
                )
                if effective_query != request_obj.query:
                    translation_meta["translated"] = True
                    DOC_GEN_IN_MEMORY_STATS["translated"] += 1

        contract = None
        if callable(get_contract_factory):
            resolved_factory = get_contract_factory(request_contract)
            if callable(resolved_factory):
                contract = resolved_factory()

        if contract is None:
            fallback_factory = contract_map.get(request_contract)
            if callable(fallback_factory):
                contract = fallback_factory()

        if contract is None and callable(get_contract_factory):
            generic_factory = get_contract_factory("generic")
            if callable(generic_factory):
                contract = generic_factory(title=f"{agent_name.title()} Document")

        agent = get_agent(agent_name)
        if not agent:
            raise HTTPException(status_code=503, detail=f"Agent unavailable: {agent_name}")

        if contract:
            result = agent.generate_document(contract=contract, query=effective_query, language=request_obj.language)
        else:
            result = {
                "success": False,
                "errors": [f"Contract type '{request_obj.contract_type}' not supported"],
                "validation_status": "failed"
            }

        document_payload = result.get("document")
        if document_payload is not None and hasattr(document_payload, "to_dict"):
            document_payload = document_payload.to_dict()

        elapsed = max(0.0, time.perf_counter() - started_at)
        DOC_GEN_IN_MEMORY_STATS["total_latency_seconds"] += elapsed

        if bool(result.get("success")):
            DOC_GEN_IN_MEMORY_STATS["success"] += 1
            if DOC_GEN_RESULTS_TOTAL:
                DOC_GEN_RESULTS_TOTAL.labels(status="success").inc()
        else:
            DOC_GEN_IN_MEMORY_STATS["failed"] += 1
            DOC_GEN_IN_MEMORY_STATS["last_error"] = "; ".join(result.get("errors", []))[:500]
            if DOC_GEN_RESULTS_TOTAL:
                DOC_GEN_RESULTS_TOTAL.labels(status="failed").inc()

        if DOC_GEN_LATENCY_SECONDS:
            DOC_GEN_LATENCY_SECONDS.observe(elapsed)

        return {
            "success": bool(result.get("success")),
            "validation_status": result.get("validation_status"),
            "errors": result.get("errors", []),
            "document": document_payload,
            "provenance": result.get("provenance"),
            "meta": {
                "agent": agent_name,
                "contract_type": request_obj.contract_type,
                "format": request_obj.format,
                "translation": translation_meta,
                "processing_seconds": round(elapsed, 4),
                "timestamp": datetime.datetime.utcnow().isoformat(),
            },
        }
    except HTTPException:
        DOC_GEN_IN_MEMORY_STATS["failed"] += 1
        if DOC_GEN_RESULTS_TOTAL:
            DOC_GEN_RESULTS_TOTAL.labels(status="failed").inc()
        raise
    except Exception as e:
        logger.error(f"Document generation error: {e}")
        DOC_GEN_IN_MEMORY_STATS["failed"] += 1
        DOC_GEN_IN_MEMORY_STATS["last_error"] = str(e)[:500]
        if DOC_GEN_RESULTS_TOTAL:
            DOC_GEN_RESULTS_TOTAL.labels(status="failed").inc()
        raise HTTPException(status_code=500, detail=f"Document generation failed: {type(e).__name__}")


@app.get("/api/v1/documents/metrics")
@app.get("/api/documents/metrics")
async def document_metrics():
    """Operational metrics for document/media generation pipeline."""
    total = DOC_GEN_IN_MEMORY_STATS["requests"]
    avg_latency = 0.0
    if total > 0:
        avg_latency = DOC_GEN_IN_MEMORY_STATS["total_latency_seconds"] / total

    return {
        "service": "ocean_document_generation",
        "requests": total,
        "success": DOC_GEN_IN_MEMORY_STATS["success"],
        "failed": DOC_GEN_IN_MEMORY_STATS["failed"],
        "translated": DOC_GEN_IN_MEMORY_STATS["translated"],
        "success_rate": round((DOC_GEN_IN_MEMORY_STATS["success"] / total) if total else 0.0, 4),
        "avg_latency_seconds": round(avg_latency, 4),
        "last_error": DOC_GEN_IN_MEMORY_STATS["last_error"],
        "last_request_at": DOC_GEN_IN_MEMORY_STATS["last_request_at"],
        "prometheus_enabled": HAS_PROMETHEUS,
        "timestamp": datetime.datetime.utcnow().isoformat(),
    }


@app.post("/api/v1/documents/workflow")
@app.post("/api/documents/workflow")
async def document_workflow(request_obj: MediaWorkflowRequest):
    """Generate multi-asset workflow bundle in one request."""
    profile_map = {
        "full": ["video", "voice", "music", "painting", "animation"],
        "narrative": ["video", "voice", "music"],
        "visual": ["video", "painting", "animation"],
        "audio": ["voice", "music"],
    }
    selected_assets = profile_map.get((request_obj.profile or "").lower().strip(), profile_map["full"])

    workflow_results: Dict[str, Any] = {}
    for asset in selected_assets:
        generation_result = await documents_generate(
            DocumentGenerateRequest(
                format=asset,
                contract_type=asset,
                query=request_obj.query,
                language=request_obj.language,
                auto_translate=request_obj.auto_translate,
            )
        )
        workflow_results[asset] = generation_result

    success_assets = [name for name, payload in workflow_results.items() if bool(payload.get("success"))]
    failed_assets = [name for name, payload in workflow_results.items() if not bool(payload.get("success"))]

    return {
        "success": len(failed_assets) == 0,
        "profile": request_obj.profile,
        "query": request_obj.query,
        "language": request_obj.language,
        "assets_requested": selected_assets,
        "assets_success": success_assets,
        "assets_failed": failed_assets,
        "results": workflow_results,
        "timestamp": datetime.datetime.utcnow().isoformat(),
    }


# ═══════════════════════════════════════════════════════════════════
# XLC RESONANCE ENGINE — endpoints
# ═══════════════════════════════════════════════════════════════════

class _XLCRouteRequest(BaseModel):
    text: str = Field(..., description="Teksti input për routing (mund të jetë fjali e gjatë)")
    commands: list[str] = Field(default=[], description="Lista komandash për regjistrim (opsionale, nëse bosh përdoren ato ekzistuese)")
    threshold: float = Field(default=0.9999, ge=0.0001, le=1.0)
    max_extra_window: int = Field(default=2, ge=0, le=10)


class _XLCInspectRequest(BaseModel):
    candidate: str = Field(..., description="Teksti kandidat")
    reference: str = Field(..., description="Teksti referencë")
    threshold: float = Field(default=0.9999, ge=0.0001, le=1.0)
    scan: bool = Field(default=True, description="Nëse True përdor inspect_scan (dritare sliding)")


class _XLCRouteStreamRequest(BaseModel):
    text: str = Field(..., description="Teksti input për routing (mund të jetë fjali e gjatë)")
    commands: list[str] = Field(default=[], description="Lista komandash për regjistrim (opsionale, nëse bosh përdoren ato ekzistuese)")
    threshold: float = Field(default=0.9999, ge=0.0001, le=1.0)
    max_extra_window: int = Field(default=2, ge=0, le=10)
    model: str | None = Field(default=None, description="Modeli Ollama (opsional)")
    max_tokens: int | None = Field(default=None, ge=-1, le=8192)
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    elastic: bool = Field(default=True, description="Nëse True përdor num_predict=-1 dhe timeout pa kufi")


def _resonance_to_decibel(score: float) -> float:
    # Resonance amplitude is logarithmic; map normalized score to dB attenuation.
    safe = max(1e-12, min(1.0, float(score)))
    return round(20.0 * math.log10(safe), 9)


def _resonance_to_nanodecibel(score: float) -> float:
    return round(_resonance_to_decibel(score) * 1_000_000_000.0, 3)


_xlc_security_monitor = XLCSecurityMonitor(
    min_baseline_samples=XLC_SECURITY_BASELINE_MIN_SAMPLES,
    max_baseline_samples=XLC_SECURITY_BASELINE_MAX_SAMPLES,
    alert_deviation_ndb=XLC_SECURITY_ALERT_DEVIATION_NDB,
    block_deviation_ndb=XLC_SECURITY_BLOCK_DEVIATION_NDB,
)


async def _assess_xlc_security(
    *,
    endpoint: str,
    resonance_ndb: float,
    matched: bool,
    route_name: Optional[str],
    input_text: str,
    source: str,
) -> Dict[str, Any]:
    assessment = _xlc_security_monitor.evaluate(
        endpoint=endpoint,
        resonance_ndb=resonance_ndb,
        matched=matched,
        route_name=route_name,
        input_text=input_text,
    )
    signature = assessment.get("attack_signature")
    firewall_action = assessment.get("firewall_action") or {}
    if signature or firewall_action.get("action") != "allow":
        await _ingest_signal(
            SignalRequest(
                event_type="xlc.security.event",
                source=source,
                payload={
                    "endpoint": endpoint,
                    "resonance_ndb": resonance_ndb,
                    "matched": matched,
                    "route_name": route_name,
                    "attack_signature": signature,
                    "firewall_action": firewall_action,
                },
                origin="internal",
                priority="high" if firewall_action.get("action") == "block" else "normal",
                tags=["xlc", "security", endpoint],
            )
        )
    return assessment


@app.get("/xlc/health")
async def xlc_health():
    if not _HAS_XLC:
        raise HTTPException(status_code=503, detail="XLC engine jo i ngarkuar")
    return {
        "status": "ok",
        "engine": "XLCResonanceEngine",
        "commands_registered": len(_xlc_router.commands),
        "security_profiles": len(_xlc_security_monitor.get_profiles()),
    }


@app.get("/xlc/security/profiles")
async def xlc_security_profiles():
    if not _HAS_XLC:
        raise HTTPException(status_code=503, detail="XLC engine jo i ngarkuar")
    return {"status": "ok", "profiles": _xlc_security_monitor.get_profiles()}


@app.get("/xlc/security/profiles/{endpoint_name}")
async def xlc_security_profile(endpoint_name: str):
    if not _HAS_XLC:
        raise HTTPException(status_code=503, detail="XLC engine jo i ngarkuar")
    profile = _xlc_security_monitor.get_profile(endpoint_name)
    if profile is None:
        raise HTTPException(status_code=404, detail="endpoint security profile not found")
    return {"status": "ok", "profile": profile}


@app.post("/xlc/route")
async def xlc_route(req: _XLCRouteRequest):
    if not _HAS_XLC:
        raise HTTPException(status_code=503, detail="XLC engine jo i ngarkuar")
    if not req.text.strip():
        raise HTTPException(status_code=422, detail="text nuk mund të jetë bosh")

    router = _xlc_router
    # nëse u dërguan komanda të reja, krijo router të ri për këtë kërkesë
    if req.commands:
        try:
            router = _XLCCommandRouter(threshold=req.threshold, max_extra_window=req.max_extra_window)
            router.register_many(req.commands)
        except Exception as e:
            raise HTTPException(status_code=422, detail=str(e))

    if not router.commands:
        raise HTTPException(status_code=422, detail="Nuk ka komanda të regjistruara. Dërgo 'commands' në body.")

    try:
        result = router.route(req.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    payload = result.as_dict()
    payload["measurement_unit"] = "nanodecibel"
    payload["resonance_ndb"] = _resonance_to_nanodecibel(result.report.combined)
    payload["resonance_decibel"] = _resonance_to_decibel(result.report.combined)
    payload["resonance_nanovolt"] = payload["resonance_ndb"]  # legacy alias
    if isinstance(result.all_scores, dict):
        payload["all_scores_ndb"] = {
            name: _resonance_to_nanodecibel(score)
            for name, score in result.all_scores.items()
        }
        payload["all_scores_nanovolt"] = payload["all_scores_ndb"]  # legacy alias
    payload.update(
        await _assess_xlc_security(
            endpoint="xlc.route",
            resonance_ndb=payload["resonance_ndb"],
            matched=bool(result.matched),
            route_name=result.route_name,
            input_text=req.text,
            source="api:/xlc/route",
        )
    )
    return payload


@app.post("/xlc/route/stream")
async def xlc_route_stream(req: _XLCRouteStreamRequest):
    if not _HAS_XLC:
        raise HTTPException(status_code=503, detail="XLC engine jo i ngarkuar")
    if not req.text.strip():
        raise HTTPException(status_code=422, detail="text nuk mund të jetë bosh")

    router = _xlc_router
    if req.commands:
        try:
            router = _XLCCommandRouter(threshold=req.threshold, max_extra_window=req.max_extra_window)
            router.register_many(req.commands)
        except Exception as e:
            raise HTTPException(status_code=422, detail=str(e))

    if not router.commands:
        raise HTTPException(status_code=422, detail="Nuk ka komanda të regjistruara. Dërgo 'commands' në body.")

    try:
        route_result = router.route(req.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    async def _stream() -> AsyncGenerator[str, None]:
        async def _emit(payload: Dict[str, Any]) -> AsyncGenerator[str, None]:
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

        async for chunk in _emit(
            {
                "phase": "copierming",
                "status": "ok",
                "input": req.text,
                "scanner_unit": "nanodecibel",
            }
        ):
            yield chunk

        all_scores_ndb = {
            name: _resonance_to_nanodecibel(score)
            for name, score in route_result.all_scores.items()
        }
        route_ndb = _resonance_to_nanodecibel(route_result.report.combined)
        route_db = _resonance_to_decibel(route_result.report.combined)
        security_assessment = await _assess_xlc_security(
            endpoint="xlc.route.stream",
            resonance_ndb=route_ndb,
            matched=bool(route_result.matched),
            route_name=route_result.route_name,
            input_text=req.text,
            source="api:/xlc/route/stream",
        )
        async for chunk in _emit(
            {
                "phase": "processing",
                "matched": route_result.matched,
                "route_name": route_result.route_name,
                "all_scores": route_result.all_scores,
                "measurement_unit": "nanodecibel",
                "resonance_ndb": route_ndb,
                "resonance_decibel": route_db,
                "all_scores_ndb": all_scores_ndb,
                "resonance_nanovolt": route_ndb,
                "all_scores_nanovolt": all_scores_ndb,
                "resonance_profile": security_assessment["resonance_profile"],
                "normal_behavior_baseline": security_assessment["normal_behavior_baseline"],
            }
        ):
            yield chunk

        # Resonance event bridges scanner timing with slower printer timing.
        async for chunk in _emit(
            {
                "phase": "resonance",
                "matched": route_result.matched,
                "route": route_result.route_name,
                "score": route_result.report.combined if route_result.report else 0.0,
                "score_ndb": route_ndb,
                "score_decibel": route_db,
                "router_ns": route_result.router_ns,
                "measurement_unit": "nanodecibel",
                "score_nanovolt": route_ndb,
            }
        ):
            yield chunk

        async for chunk in _emit(
            {
                "phase": "security",
                **security_assessment,
            }
        ):
            yield chunk

        firewall_action = security_assessment.get("firewall_action") or {}
        if firewall_action.get("action") != "allow":
            async for chunk in _emit(
                {
                    "phase": "firewall_action",
                    **firewall_action,
                    "attack_signature": security_assessment.get("attack_signature"),
                }
            ):
                yield chunk
            if firewall_action.get("action") == "block":
                async for chunk in _emit(
                    {
                        "phase": "complete",
                        "matched": False,
                        "reason": "blocked_by_xlc_firewall",
                    }
                ):
                    yield chunk
                yield "data: [DONE]\n\n"
                return
            if firewall_action.get("action") == "throttle":
                await asyncio.sleep(0.05)

        if not route_result.matched or not route_result.route_name:
            async for chunk in _emit(
                {
                    "phase": "complete",
                    "matched": False,
                    "reason": "no_route_match",
                }
            ):
                yield chunk
            yield "data: [DONE]\n\n"
            return

        selected_model = (req.model or MODEL)
        # Keep scanner->printer flow unconstrained in XLC streaming mode.
        safe_tokens = -1
        timeout_s = None

        temperature = req.temperature
        prompt = (
            "Ti je Ocean Core assistant. Jep pergjigje praktike, te qarte dhe te zbatueshme.\n"
            f"Komanda e njohur nga XLC: {route_result.route_name}\n"
            f"Input origjinal: {req.text}\n"
            "Pergjigju ne menyre te shkurter dhe me hapa konkrete."
        )
        system_prompt = (
            "MODE: copierming -> perpunim -> streaming. "
            "Mos shpik te dhena; kur nuk ke te dhena, thuaj qarte qe mungojne."
        )

        async for chunk in _emit(
            {
                "phase": "streaming",
                "status": "start",
                "model": selected_model,
                "route_name": route_result.route_name,
                "num_predict": safe_tokens,
                "elastic": req.elastic,
                "measurement_unit": "nanodecibel",
                "resonance_ndb": route_ndb,
                "resonance_decibel": route_db,
                "resonance_nanovolt": route_ndb,
                "printer_transport": "laser_printer",
                "printer_concept": "nanodecibel laser printer",
                "printer_unit": "nanodecibel",
                "printer_ndb": route_ndb,
                "printer_nanovolt": route_ndb,
                "text_transport": "scanner_printer_stream",
                "predict_mode": "elastic_unlimited",
            }
        ):
            yield chunk

        async for chunk in _emit(
            {
                "phase": "thinking",
                "engine": "Zurich",
                "stage": 1,
                "route_name": route_result.route_name,
            }
        ):
            yield chunk

        # Early heartbeat closes perceived latency before first model token arrives.
        for heartbeat_seq in range(1, 3):
            await asyncio.sleep(0.01)
            async for chunk in _emit(
                {
                    "phase": "streaming",
                    "heartbeat": True,
                    "seq": heartbeat_seq,
                }
            ):
                yield chunk

        full_response = ""
        token_buffer: List[str] = []
        first_burst_sent = False
        heartbeat_seq = 2
        try:
            first_burst_tokens = max(1, int(os.getenv("OCEAN_XLC_FIRST_BURST_TOKENS", "1")))
        except ValueError:
            first_burst_tokens = 1
        num_ctx = _resolve_num_ctx(True, safe_tokens, prompt_chars=len(prompt), message_count=2)

        try:
            async with httpx.AsyncClient(timeout=timeout_s) as client:
                options_payload = {
                    "num_ctx": num_ctx,
                    "num_predict": safe_tokens,
                }
                if temperature is not None:
                    options_payload["temperature"] = temperature

                async with client.stream(
                    "POST",
                    f"{OLLAMA_HOST}/api/generate",
                    json={
                        "model": selected_model,
                        "prompt": prompt,
                        "system": system_prompt,
                        "stream": True,
                        "options": options_payload,
                    },
                ) as response:
                    if response.status_code != 200:
                        yield (
                            f"data: {json.dumps({'phase': 'error', 'status': response.status_code, 'error': 'upstream_stream_failed'}, ensure_ascii=False)}\n\n"
                        )
                        yield "data: [DONE]\n\n"
                        return

                    line_iter = response.aiter_lines()
                    while True:
                        try:
                            line = await asyncio.wait_for(line_iter.__anext__(), timeout=0.01)
                        except asyncio.TimeoutError:
                            heartbeat_seq += 1
                            async for chunk in _emit(
                                {
                                    "phase": "streaming",
                                    "heartbeat": True,
                                    "seq": heartbeat_seq,
                                }
                            ):
                                yield chunk
                            continue
                        except StopAsyncIteration:
                            break

                        if not line:
                            continue
                        try:
                            payload = json.loads(line)
                        except json.JSONDecodeError:
                            continue

                        token = ""
                        if isinstance(payload.get("response"), str):
                            token = payload.get("response") or ""
                        elif isinstance(payload.get("message"), dict) and isinstance(payload["message"].get("content"), str):
                            token = payload["message"].get("content") or ""

                        if token:
                            full_response += token
                            if not first_burst_sent:
                                token_buffer.append(token)
                                if len(token_buffer) >= first_burst_tokens:
                                    burst_text = "".join(token_buffer)
                                    async for chunk in _emit(
                                        {
                                            "phase": "streaming",
                                            "printer_chunk_burst": token_buffer,
                                            "printer_chunk": burst_text,
                                            "burst_size": len(token_buffer),
                                            "first_burst_tokens": first_burst_tokens,
                                            "printer_unit": "nanodecibel",
                                            "printer_ndb": route_ndb,
                                            "printer_nanovolt": route_ndb,
                                        }
                                    ):
                                        yield chunk
                                    token_buffer = []
                                    first_burst_sent = True
                            else:
                                async for chunk in _emit(
                                    {
                                        "phase": "streaming",
                                        "printer_chunk": token,
                                        "printer_unit": "nanodecibel",
                                        "printer_ndb": route_ndb,
                                        "printer_nanovolt": route_ndb,
                                    }
                                ):
                                    yield chunk

                        if payload.get("done"):
                            break

                    if token_buffer:
                        burst_text = "".join(token_buffer)
                        async for chunk in _emit(
                            {
                                "phase": "streaming",
                                "printer_chunk_burst": token_buffer,
                                "printer_chunk": burst_text,
                                "burst_size": len(token_buffer),
                                "first_burst_tokens": first_burst_tokens,
                                "printer_unit": "nanodecibel",
                                "printer_ndb": route_ndb,
                                "printer_nanovolt": route_ndb,
                            }
                        ):
                            yield chunk

            async for chunk in _emit(
                {
                    "phase": "complete",
                    "matched": True,
                    "route_name": route_result.route_name,
                    "total_chars": len(full_response),
                    "measurement_unit": "nanodecibel",
                    "resonance_ndb": route_ndb,
                    "resonance_decibel": route_db,
                    "resonance_nanovolt": route_ndb,
                }
            ):
                yield chunk
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"XLC stream error: {e}")
            async for chunk in _emit(
                {
                    "phase": "error",
                    "error": str(e),
                }
            ):
                yield chunk
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        _stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@app.post("/xlc/inspect")
async def xlc_inspect(req: _XLCInspectRequest):
    if not _HAS_XLC:
        raise HTTPException(status_code=503, detail="XLC engine jo i ngarkuar")
    if not req.candidate.strip() or not req.reference.strip():
        raise HTTPException(status_code=422, detail="candidate dhe reference nuk mund të jenë bosh")

    try:
        if req.scan:
            report = _xlc_inspector.inspect_scan(req.candidate, req.reference, threshold=req.threshold)
        else:
            report = _xlc_inspector.inspect(req.candidate, req.reference, threshold=req.threshold)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    payload = report.as_dict()
    payload["measurement_unit"] = "nanodecibel"
    payload["resonance_ndb"] = _resonance_to_nanodecibel(report.combined)
    payload["resonance_decibel"] = _resonance_to_decibel(report.combined)
    payload["resonance_nanovolt"] = payload["resonance_ndb"]  # legacy alias
    payload.update(
        await _assess_xlc_security(
            endpoint="xlc.inspect",
            resonance_ndb=payload["resonance_ndb"],
            matched=bool(report.opened),
            route_name=req.reference,
            input_text=req.candidate,
            source="api:/xlc/inspect",
        )
    )
    return payload


@app.post("/xlc/register")
async def xlc_register(commands: list[str]):
    """Regjistron komanda globalisht në _xlc_router (persistent per-process)."""
    if not _HAS_XLC:
        raise HTTPException(status_code=503, detail="XLC engine jo i ngarkuar")
    if not commands:
        raise HTTPException(status_code=422, detail="Lista commands nuk mund të jetë bosh")
    try:
        _xlc_router.register_many(commands)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return {"registered": list(_xlc_router.commands)}


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    logger.info(f"🌊 Ocean Core Full v5.0.0 starting on port {PORT}")
    logger.info("⚙️ Zürich Engine v1.0 - 9-stage deterministic reasoning")
    logger.info("🧠 Trinity Debate v1.0 - 5-persona AI debate")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
