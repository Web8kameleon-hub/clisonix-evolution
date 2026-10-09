from __future__ import annotations

"""
Module Core Registry
====================
Lightweight routing/offload layer for Clisonix modules that do not need the full
Ocean Core reasoning pipeline on every request.

This registry exposes 20+ dedicated module-core profiles so callers can resolve
queries to the right dashboard/service first and only fall back to the heavy
LLM path when truly needed.
"""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Tuple

try:
    from knowledge_layer import HOW_TO_USE as KNOWLEDGE_HOW_TO_USE  # type: ignore
    from knowledge_layer import SERVICES as KNOWLEDGE_SERVICES  # type: ignore
except Exception:
    KNOWLEDGE_HOW_TO_USE = {}
    KNOWLEDGE_SERVICES = {}


@dataclass(frozen=True)
class ModuleCoreProfile:
    id: str
    name: str
    route: str
    description: str
    category: str
    offload_group: str
    keywords: Tuple[str, ...] = field(default_factory=tuple)
    capabilities: Tuple[str, ...] = field(default_factory=tuple)
    use_cases: Tuple[str, ...] = field(default_factory=tuple)
    how_to_use: str = ""
    system_prompt: str = ""


_BASE_PROFILES: Dict[str, Dict[str, Any]] = {
    "curiosity-ocean": {
        "category": "ai-chat",
        "offload_group": "conversation",
        "keywords": ("chat", "ask", "talk", "question", "assistant", "ocean"),
        "capabilities": ("conversation", "multilingual", "general_help"),
        "use_cases": ("general ai help", "multi-language chat", "assistant guidance"),
        "system_prompt": "You are the Curiosity Ocean core for Clisonix. Provide concise, helpful, multilingual product guidance.",
    },
    "specialized-chat": {
        "category": "ai-chat",
        "offload_group": "conversation",
        "keywords": ("specialized", "expert", "domain", "research", "technical"),
        "capabilities": ("expert_chat", "domain_guidance", "deep_dive"),
        "use_cases": ("expert consultation", "specialized q&a", "domain-specific help"),
        "system_prompt": "You are the Specialized Chat core for Clisonix. Answer with domain-aware precision and keep the response practical.",
    },
    "open-webui": {
        "category": "ai-chat",
        "offload_group": "conversation",
        "keywords": ("webui", "model", "chat ui", "workspace", "model switch"),
        "capabilities": ("model_selection", "chat_ui", "workspace_access"),
        "use_cases": ("choose model", "work with chat ui", "multi-model interaction"),
        "system_prompt": "You are the Open WebUI core for Clisonix. Guide users through model selection and chat workspace flows.",
    },
    "eeg-analysis": {
        "category": "biosignals",
        "offload_group": "biosignal",
        "keywords": ("eeg", "brainwave", "brain", "neural", "neuroscience", "truri"),
        "capabilities": ("signal_analysis", "brainwave_review", "visualization"),
        "use_cases": ("analyze eeg", "review brainwave trends", "biosignal workflow"),
        "system_prompt": "You are the EEG Analysis core. Focus on biosignal interpretation, EEG workflows, and careful scientific wording.",
    },
    "neural-biofeedback": {
        "category": "biosignals",
        "offload_group": "biosignal",
        "keywords": ("biofeedback", "training", "neural feedback", "focus training"),
        "capabilities": ("realtime_feedback", "training_sessions", "focus_support"),
        "use_cases": ("start a biofeedback session", "realtime neural feedback", "guided focus training"),
        "system_prompt": "You are the Neural Biofeedback core. Help with real-time training flows and sensor-guided feedback sessions.",
    },
    "neural-synthesis": {
        "category": "biosignals",
        "offload_group": "biosignal",
        "keywords": ("synthesis", "pattern generation", "neural synthesis", "neural patterns"),
        "capabilities": ("pattern_generation", "synthetic_signals", "experimentation"),
        "use_cases": ("generate neural patterns", "configure synthesis", "test synthetic signals"),
        "system_prompt": "You are the Neural Synthesis core. Support pattern generation and experimental signal workflows.",
    },
    "neuroacoustic-converter": {
        "category": "biosignals",
        "offload_group": "biosignal",
        "keywords": ("neuroacoustic", "brainmusic", "audio from eeg", "convert eeg to audio"),
        "capabilities": ("audio_conversion", "eeg_to_sound", "creative_export"),
        "use_cases": ("convert eeg to audio", "export brain music", "creative neural audio"),
        "system_prompt": "You are the Neuroacoustic Converter core. Help transform EEG or signal data into structured audio workflows.",
    },
    "hybrid-biometric-dashboard": {
        "category": "biosignals",
        "offload_group": "biosignal",
        "keywords": ("biometric", "hrv", "multi-sensor", "pulse", "wearable"),
        "capabilities": ("biometrics", "sensor_fusion", "dashboard_monitoring"),
        "use_cases": ("monitor biometrics", "multi-sensor view", "hybrid dashboard help"),
        "system_prompt": "You are the Hybrid Biometric Dashboard core. Focus on sensor fusion, health metrics, and dashboard interpretation.",
    },
    "face-detection": {
        "category": "vision",
        "offload_group": "vision",
        "keywords": ("face", "facial", "recognition", "camera", "vision"),
        "capabilities": ("image_analysis", "detection", "camera_workflows"),
        "use_cases": ("detect faces", "camera-based insights", "vision analysis"),
        "system_prompt": "You are the Face Detection core. Assist with vision, facial analysis, and camera-based workflows.",
    },
    "document-tools": {
        "category": "documents",
        "offload_group": "documents",
        "keywords": ("document", "pdf", "word", "file", "docs", "dokument"),
        "capabilities": ("document_processing", "pdf_workflows", "file_support"),
        "use_cases": ("process documents", "summarize files", "document operations"),
        "system_prompt": "You are the Document Tools core. Handle document workflows clearly and efficiently without unnecessary reasoning overhead.",
    },
    "excel-dashboard": {
        "category": "documents",
        "offload_group": "documents",
        "keywords": ("excel", "spreadsheet", "xlsx", "sheet", "table", "csv"),
        "capabilities": ("spreadsheet_analysis", "charts", "tabular_review"),
        "use_cases": ("analyze spreadsheet", "build charts", "summarize excel data"),
        "system_prompt": "You are the Excel Dashboard core. Focus on spreadsheet analysis, tables, charts, and export workflows.",
    },
    "data-collection": {
        "category": "data",
        "offload_group": "data",
        "keywords": ("collect", "gather", "ingest", "pipeline", "import data"),
        "capabilities": ("data_ingestion", "collection", "aggregation"),
        "use_cases": ("start collection", "ingest data", "aggregate multiple feeds"),
        "system_prompt": "You are the Data Collection core. Guide ingestion, synchronization, and aggregation flows.",
    },
    "user-data": {
        "category": "data",
        "offload_group": "data",
        "keywords": ("my data", "personal data", "privacy", "export data", "delete data"),
        "capabilities": ("data_management", "privacy_controls", "exports"),
        "use_cases": ("manage personal data", "export account data", "privacy settings"),
        "system_prompt": "You are the User Data core. Prioritize privacy, export/delete flows, and account data management.",
    },
    "fitness-dashboard": {
        "category": "wellness",
        "offload_group": "wellness",
        "keywords": ("fitness", "workout", "exercise", "training", "nutrition"),
        "capabilities": ("activity_tracking", "progress_monitoring", "fitness_logs"),
        "use_cases": ("track workout", "view progress", "fitness dashboard support"),
        "system_prompt": "You are the Fitness Dashboard core. Keep guidance actionable and centered on progress tracking and routines.",
    },
    "mood-journal": {
        "category": "wellness",
        "offload_group": "wellness",
        "keywords": ("mood", "journal", "emotion", "feeling", "mental health"),
        "capabilities": ("mood_tracking", "journaling", "trend_review"),
        "use_cases": ("log emotions", "review journal trends", "wellness reflection"),
        "system_prompt": "You are the Mood Journal core. Be calm, structured, and supportive while staying within product guidance.",
    },
    "focus-timer": {
        "category": "productivity",
        "offload_group": "productivity",
        "keywords": ("focus", "pomodoro", "timer", "productivity", "session"),
        "capabilities": ("timers", "focus_sessions", "streaks"),
        "use_cases": ("start pomodoro", "manage focus blocks", "productivity timing"),
        "system_prompt": "You are the Focus Timer core. Optimize responses for task sessions, timers, and productivity flow.",
    },
    "iot-network": {
        "category": "iot-industrial",
        "offload_group": "iot",
        "keywords": ("iot", "lora", "lorawan", "sensor", "telemetry", "gateway"),
        "capabilities": ("sensor_networks", "telemetry", "gateway_status"),
        "use_cases": ("inspect sensor feeds", "gateway setup", "iot telemetry"),
        "system_prompt": "You are the IoT Network core. Focus on sensors, LoRa/LoRaWAN, telemetry, and gateway operations.",
    },
    "industrial-dashboard": {
        "category": "iot-industrial",
        "offload_group": "iot",
        "keywords": ("industrial", "factory", "manufacturing", "operations", "plant"),
        "capabilities": ("industrial_metrics", "efficiency", "operations_monitoring"),
        "use_cases": ("review industrial metrics", "factory dashboard", "efficiency monitoring"),
        "system_prompt": "You are the Industrial Dashboard core. Keep answers operational, metric-driven, and production-oriented.",
    },
    "phone-sensors": {
        "category": "iot-industrial",
        "offload_group": "iot",
        "keywords": ("phone sensor", "mobile sensor", "accelerometer", "gyroscope", "device motion"),
        "capabilities": ("mobile_telemetry", "sensor_capture", "realtime_phone_data"),
        "use_cases": ("read mobile sensors", "capture phone telemetry", "device motion analysis"),
        "system_prompt": "You are the Phone Sensors core. Focus on mobile telemetry, motion sensors, and device-side capture.",
    },
    "phone-monitor": {
        "category": "iot-industrial",
        "offload_group": "iot",
        "keywords": ("phone monitor", "device monitor", "battery", "mobile status", "device health"),
        "capabilities": ("device_monitoring", "mobile_status", "alerts"),
        "use_cases": ("monitor phone health", "device stats", "mobile alerts"),
        "system_prompt": "You are the Phone Monitor core. Provide focused guidance on device health, status, and monitoring views.",
    },
    "spectrum-analyzer": {
        "category": "signal-processing",
        "offload_group": "signals",
        "keywords": ("spectrum", "frequency", "fft", "audio spectrum", "signal analyzer"),
        "capabilities": ("signal_analysis", "frequency_review", "audio_metrics"),
        "use_cases": ("analyze frequencies", "inspect spectrum", "audio/signal review"),
        "system_prompt": "You are the Spectrum Analyzer core. Stay technical and concise for signal and frequency workflows.",
    },
    "ocean-analytics": {
        "category": "analytics",
        "offload_group": "analytics",
        "keywords": ("analytics", "statistics", "insight", "metrics", "dashboard analytics"),
        "capabilities": ("platform_analytics", "insights", "reporting_overview"),
        "use_cases": ("view analytics", "inspect metrics", "platform insights"),
        "system_prompt": "You are the Ocean Analytics core. Focus on metrics, trends, insights, and dashboard summaries.",
    },
    "reporting-dashboard": {
        "category": "analytics",
        "offload_group": "analytics",
        "keywords": ("report", "reporting", "export report", "pdf report", "summary report"),
        "capabilities": ("report_generation", "exports", "scheduled_reports"),
        "use_cases": ("generate report", "export summaries", "report dashboard"),
        "system_prompt": "You are the Reporting Dashboard core. Optimize for report creation, exports, and concise summaries.",
    },
    "weather-dashboard": {
        "category": "weather",
        "offload_group": "weather",
        "keywords": ("weather", "forecast", "climate", "temperature", "rain", "wind"),
        "capabilities": ("forecasting", "weather_dashboard", "location_conditions"),
        "use_cases": ("check forecast", "weather dashboard", "location conditions"),
        "system_prompt": "You are the Weather Dashboard core. Keep answers specific to weather, conditions, and forecasts.",
    },
    "aviation-weather": {
        "category": "weather",
        "offload_group": "weather",
        "keywords": ("aviation", "metar", "taf", "airport weather", "pilot"),
        "capabilities": ("aviation_forecast", "metar", "taf"),
        "use_cases": ("check metar", "review taf", "aviation conditions"),
        "system_prompt": "You are the Aviation Weather core. Focus on METAR, TAF, and pilot-relevant weather conditions.",
    },
    "crypto-dashboard": {
        "category": "finance",
        "offload_group": "finance",
        "keywords": ("crypto", "bitcoin", "btc", "ethereum", "portfolio", "token"),
        "capabilities": ("market_tracking", "portfolio_overview", "price_monitoring"),
        "use_cases": ("track crypto", "view portfolio", "monitor token prices"),
        "system_prompt": "You are the Crypto Dashboard core. Focus on crypto tracking, portfolio views, and market summaries.",
    },
    "developer-docs": {
        "category": "developer",
        "offload_group": "developer",
        "keywords": ("developer", "api", "docs", "documentation", "integration"),
        "capabilities": ("api_docs", "integration_guides", "developer_support"),
        "use_cases": ("browse api docs", "integration help", "developer onboarding"),
        "system_prompt": "You are the Developer Docs core. Provide exact routes, docs guidance, and integration-ready help.",
    },
    "functions-registry": {
        "category": "developer",
        "offload_group": "developer",
        "keywords": ("function", "registry", "catalog", "tooling", "capabilities"),
        "capabilities": ("function_lookup", "catalog_navigation", "tool_discovery"),
        "use_cases": ("find functions", "inspect tools", "capability discovery"),
        "system_prompt": "You are the Functions Registry core. Help users find platform functions and capability mappings quickly.",
    },
    "protocol-kitchen": {
        "category": "developer",
        "offload_group": "developer",
        "keywords": ("protocol", "spec", "wire format", "integration protocol", "kitchen"),
        "capabilities": ("protocol_design", "spec_guidance", "developer_workflows"),
        "use_cases": ("design protocol", "review spec", "integration standards"),
        "system_prompt": "You are the Protocol Kitchen core. Keep answers structured around protocol design and implementation workflows.",
    },
}


def _service_meta(service_id: str) -> Dict[str, Any]:
    return KNOWLEDGE_SERVICES.get(service_id, {}) if isinstance(KNOWLEDGE_SERVICES, dict) else {}


_MODULE_CORES: Dict[str, ModuleCoreProfile] = {}
for core_id, base in _BASE_PROFILES.items():
    service_meta = _service_meta(core_id)
    _MODULE_CORES[core_id] = ModuleCoreProfile(
        id=core_id,
        name=service_meta.get("name", core_id.replace("-", " ").title()),
        route=service_meta.get("url", f"/modules/{core_id}"),
        description=service_meta.get("desc", f"Dedicated module core for {core_id.replace('-', ' ')}"),
        category=base["category"],
        offload_group=base["offload_group"],
        keywords=tuple(base.get("keywords", ())),
        capabilities=tuple(base.get("capabilities", ())),
        use_cases=tuple(base.get("use_cases", ())),
        how_to_use=KNOWLEDGE_HOW_TO_USE.get(core_id, "Open the module and follow its dedicated workflow."),
        system_prompt=base.get("system_prompt", "You are a Clisonix module core assistant."),
    )


_ALIAS_LOOKUP: Dict[str, str] = {}
for profile in _MODULE_CORES.values():
    _ALIAS_LOOKUP[profile.id] = profile.id
    _ALIAS_LOOKUP[profile.name.lower()] = profile.id
    _ALIAS_LOOKUP[profile.route.lower()] = profile.id
    for keyword in profile.keywords:
        normalized = keyword.strip().lower()
        if normalized and normalized not in _ALIAS_LOOKUP:
            _ALIAS_LOOKUP[normalized] = profile.id


def _normalize_text(value: Optional[str]) -> str:
    return " ".join((value or "").strip().lower().replace("_", " ").split())


def get_module_core_catalog() -> List[Dict[str, Any]]:
    """Return all module cores as JSON-friendly dictionaries."""
    return [
        asdict(profile)
        for profile in sorted(
            _MODULE_CORES.values(),
            key=lambda item: (item.offload_group, item.category, item.name.lower()),
        )
    ]


def get_module_core(core_id: str) -> Optional[ModuleCoreProfile]:
    key = _normalize_text(core_id).replace(" ", "-")
    alias_key = _ALIAS_LOOKUP.get(_normalize_text(core_id)) or _ALIAS_LOOKUP.get(key)
    return _MODULE_CORES.get(alias_key or key)


def _score_profile(profile: ModuleCoreProfile, text: str) -> int:
    if not text:
        return 0

    score = 0
    normalized = f" {text} "
    if profile.id.replace("-", " ") in text:
        score += 6
    if profile.name.lower() in text:
        score += 5
    for keyword in profile.keywords:
        token = _normalize_text(keyword)
        if token and f" {token} " in normalized:
            score += 3
        elif token and token in text:
            score += 2
    return score


def resolve_module_core(
    query: Optional[str] = None,
    domain: Optional[str] = None,
    module: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Resolve the most likely module core for a query/domain/module hint.
    Returns a JSON-friendly structure with confidence and offload metadata.
    """
    explicit_candidates: Iterable[Optional[str]] = (module, domain)
    for candidate in explicit_candidates:
        normalized = _normalize_text(candidate)
        if not normalized:
            continue
        direct_id = _ALIAS_LOOKUP.get(normalized) or _ALIAS_LOOKUP.get(normalized.replace(" ", "-"))
        if direct_id and direct_id in _MODULE_CORES:
            profile = _MODULE_CORES[direct_id]
            payload = asdict(profile)
            payload.update({"confidence": 0.99, "match_type": "explicit"})
            return payload

    text = _normalize_text(query)
    if not text:
        return None

    best_profile: Optional[ModuleCoreProfile] = None
    best_score = 0
    for profile in _MODULE_CORES.values():
        score = _score_profile(profile, text)
        if score > best_score:
            best_score = score
            best_profile = profile

    if not best_profile or best_score < 2:
        return None

    confidence = min(0.98, 0.42 + (best_score * 0.07))
    payload = asdict(best_profile)
    payload.update({"confidence": round(confidence, 2), "match_type": "keyword"})
    return payload


def build_module_core_brief(core_id: str, language: str = "en") -> str:
    profile = get_module_core(core_id)
    if not profile:
        raise KeyError(f"Unknown module core: {core_id}")

    capabilities = ", ".join(profile.capabilities[:4]) or "module guidance"
    use_cases = ", ".join(profile.use_cases[:3]) or profile.description
    lang = _normalize_text(language)

    if lang.startswith("sq"):
        return (
            f"`{profile.name}` është një core i dedikuar për `{profile.route}`. "
            f"Përdoret për {profile.description.lower()}. "
            f"Kapacitetet kryesore: {capabilities}. "
            f"Si përdoret: {profile.how_to_use} "
            f"Rastet tipike: {use_cases}."
        )

    return (
        f"`{profile.name}` is a dedicated core for `{profile.route}`. "
        f"It is optimized for {profile.description.lower()}. "
        f"Key capabilities: {capabilities}. "
        f"How to use: {profile.how_to_use} "
        f"Typical use cases: {use_cases}."
    )
