"""
RESPONSE ORCHESTRATOR V5 - PRODUCTION BRAIN
============================================
Minimal, i shpejtë, 100% lokal, pa API të jashtme me pagesë.

Features:
- Fast-path conversational (RealAnswerEngine direkt)
- Multilingual hooks (pa Google/DeepL - 100% lokal)
- Timeout për ekspertët
- Përdor persona/labs/modules vetëm kur ka kuptim
- Zero external paid APIs
- MEGA LAYER ENGINE: ~2.8 MILIARD KOMBINIME
"""

import asyncio
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# Import Mega Layer Engine
try:
    from mega_layer_engine import LayerActivation, get_mega_layer_engine
    from mega_layer_engine import MegaLayerEngine as MegaLayerEngineClass
    MEGA_LAYERS_AVAILABLE = True
except ImportError:
    MEGA_LAYERS_AVAILABLE = False
    MegaLayerEngineClass = None
    LayerActivation = None

# Import Knowledge Seeds
try:
    from knowledge_seeds.core_knowledge import KnowledgeSeed, find_matching_seed, seed_stats
    KNOWLEDGE_SEEDS_AVAILABLE = True
except ImportError:
    KNOWLEDGE_SEEDS_AVAILABLE = False
    find_matching_seed = None
    seed_stats = None
    KnowledgeSeed = None

# Import Ollama FAST Engine (LINJA OPTIKE - zero overhead)
try:
    from ollama_fast_engine import OllamaFastEngine, get_fast_engine
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    OllamaFastEngine = None
    get_fast_engine = None

# Import Albanian Dictionary
try:
    from albanian_dictionary import ALL_ALBANIAN_WORDS, CLISONIX_TERMS, SENTENCE_PATTERNS, detect_albanian, get_albanian_response
    ALBANIAN_DICT_AVAILABLE = True
except ImportError:
    ALBANIAN_DICT_AVAILABLE = False
    get_albanian_response = None
    detect_albanian = None
    ALL_ALBANIAN_WORDS = {}

# SmartAPIRouter removed - Orchestrator handles all routing

logger = logging.getLogger("orchestrator_v5")
DECLARED_OWNER = "Ledjan Ahmati"
DECLARED_OWNER_TITLE = "CEO and Creator"


# ─────────────────────────────────────────────────────────
#  ENUMS & DATA CLASSES
# ─────────────────────────────────────────────────────────

class QueryCategory(str, Enum):
    FINANCIAL = "financial"
    PHILOSOPHICAL = "philosophical"
    TECHNICAL = "technical"
    OPERATIONAL = "operational"
    SCIENTIFIC = "scientific"
    NARRATIVE = "narrative"
    PERSONAL = "personal"
    ANALYTICAL = "analytical"
    EXPLORATORY = "exploratory"
    BINARY = "binary"
    CONVERSATIONAL = "conversational"  # Për chat normal


@dataclass
class ExpertConsultation:
    expert_type: str
    expert_name: str
    expert_id: str
    query_sent: str
    response: str
    confidence: float
    relevance_score: float
    processing_time_ms: float
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class OrchestratedResponse:
    query: str
    query_category: QueryCategory
    understanding: Dict[str, Any]
    consulted_experts: List[ExpertConsultation]
    fused_answer: str
    sources_cited: List[str]
    confidence: float
    narrative_quality: float
    learning_record: Dict[str, Any]
    language: str = "und"
    mega_layers: Optional[Dict[str, Any]] = None  # Mega Layer results
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ─────────────────────────────────────────────────────────
#  LANGUAGE LAYER - 100% LOKAL (PA API TË JASHTME)
# ─────────────────────────────────────────────────────────

class LocalLanguageLayer:
    """
    Multilingual Layer - 100% lokal, pa pagesë, pa cloud.

    Përdor langdetect për detektim dhe përgjigje lokale për çdo gjuhë.
    NUK përdor Google Translate, DeepL, apo çdo API të jashtme.
    """

    def __init__(self):
        self._langdetect_available = False
        try:
            from langdetect import detect as _detect
            self._detect = _detect
            self._langdetect_available = True
        except ImportError:
            self._detect = None

    def detect_language(self, text: str) -> str:
        """Detekto gjuhën - Universal (zero hardcoding), langdetect 55+ languages."""
        if not text or len(text.strip()) < 3:
            return "und"  # Too short/empty: let flow resolver decide

        # Use langdetect for universal detection (55+ languages natively)
        if self._langdetect_available and self._detect:
            try:
                detected = self._detect(text)
                logger.info(f"🌍 langdetect: {detected}")
                return detected
            except Exception as e:
                logger.warning(f"langdetect failed: {e}")

        # Fallback: Let Ollama handle language auto-detection
        logger.info("ℹ️ Ollama will auto-detect language")
        return "und"  # undefined - Ollama auto-detects

    async def to_internal(self, text: str, lang: str) -> str:
        """
        Konverto në gjuhën interne - NUK përkthejmë!

        Thjesht e ruajmë query-n origjinale dhe e procesojmë direkt.
        Sistemi ynë kupton shumë gjuhë pa përkthim.
        """
        return text  # Proceso direkt - pa përkthim!

    async def from_internal(self, text: str, lang: str) -> str:
        """
        Konverto nga gjuha interne - NUK përkthejmë!

        Përgjigjet gjenerohen direkt në gjuhën e kërkuar.
        """
        return text  # Kthu direkt - pa përkthim!

    def get_greeting(self, lang: str) -> Optional[str]:
        """Universal greeting - delegates to Ollama in user's language."""
        # Let Ollama generate greetings naturally in any language
        return None  # Ollama generates culturally appropriate greetings

    def get_fallback(self, lang: str, query: str) -> Optional[str]:
        """Universal fallback - delegates to Ollama in user's language."""
        # Let Ollama generate fallback messages naturally
        return None  # Ollama generates appropriate fallback


# ═══════════════════════════════════════════════════════════════════════════════
#  UNIVERSAL LANGUAGE SUPPORT - 100+ LANGUAGES, ZERO HARDCODING
# ═══════════════════════════════════════════════════════════════════════════════

# ISO 639-1 to full language name mapping (comprehensive, not exhaustive)
# Generated from IANA Language Subtag Registry - supports all ISO 639-1 codes
ISO_639_NAMES = {
    "sq": "Albanian", "ar": "Arabic", "hy": "Armenian", "az": "Azerbaijani",
    "eu": "Basque", "be": "Belarusian", "bn": "Bengali", "bs": "Bosnian",
    "bg": "Bulgarian", "ca": "Catalan", "ceb": "Cebuano", "zh": "Chinese",
    "co": "Corsican", "hr": "Croatian", "cs": "Czech", "da": "Danish",
    "nl": "Dutch", "en": "English", "eo": "Esperanto", "et": "Estonian",
    "fi": "Finnish", "fr": "French", "fy": "Frisian", "gl": "Galician",
    "ka": "Georgian", "de": "German", "el": "Greek", "gu": "Gujarati",
    "ht": "Haitian", "ha": "Hausa", "he": "Hebrew", "hi": "Hindi",
    "hu": "Hungarian", "is": "Icelandic", "ig": "Igbo", "id": "Indonesian",
    "ga": "Irish", "it": "Italian", "ja": "Japanese", "jv": "Javanese",
    "kn": "Kannada", "kk": "Kazakh", "km": "Khmer", "rw": "Kinyarwanda",
    "ko": "Korean", "ku": "Kurdish", "ky": "Kyrgyz", "lo": "Lao",
    "la": "Latin", "lv": "Latvian", "lt": "Lithuanian", "lb": "Luxembourgish",
    "mk": "Macedonian", "mg": "Malagasy", "ms": "Malay", "ml": "Malayalam",
    "mt": "Maltese", "mi": "Māori", "mr": "Marathi", "mn": "Mongolian",
    "my": "Burmese", "ne": "Nepali", "no": "Norwegian", "or": "Odia",
    "ps": "Pashto", "fa": "Persian", "pl": "Polish", "pt": "Portuguese",
    "pa": "Punjabi", "ro": "Romanian", "ru": "Russian", "sm": "Samoan",
    "sa": "Sanskrit", "gd": "Scottish Gaelic", "sr": "Serbian", "st": "Sesotho",
    "sn": "Shona", "sd": "Sindhi", "si": "Sinhala", "sk": "Slovak",
    "sl": "Slovenian", "so": "Somali", "es": "Spanish", "su": "Sundanese",
    "sw": "Swahili", "sv": "Swedish", "tl": "Tagalog", "tg": "Tajik",
    "ta": "Tamil", "tt": "Tatar", "te": "Telugu", "th": "Thai",
    "bo": "Tibetan", "ti": "Tigrinya", "to": "Tongan", "tr": "Turkish",
    "tk": "Turkmen", "tw": "Twi", "uk": "Ukrainian", "ur": "Urdu",
    "ug": "Uyghur", "uz": "Uzbek", "vi": "Vietnamese", "cy": "Welsh",
    "wo": "Wolof", "xh": "Xhosa", "yi": "Yiddish", "yo": "Yoruba",
    "za": "Zhuang", "zu": "Zulu", "as": "Assamese", "br": "Breton",
}

def get_language_name(iso_code: str) -> str:
    """Get language name from ISO 639-1 code (universal, no hardcoding)."""
    if not iso_code:
        return "language"
    code = iso_code.lower().strip()
    return ISO_639_NAMES.get(code, code.upper())


# ─────────────────────────────────────────────────────────
#  LANGUAGE REQUEST PATTERNS - MULTILINGUAL DETECTION
# ─────────────────────────────────────────────────────────

LANGUAGE_REQUEST_PATTERNS = {
    # Albanian
    "përgjigju në shqip": "sq",
    "përgjigju në albanisht": "sq",
    "përgjigje në shqip": "sq",

    # English
    "respond in english": "en",
    "reply in english": "en",
    "answer in english": "en",
    "in english": "en",

    # German
    "antworte auf deutsch": "de",
    "antworte in deutsch": "de",
    "respond auf deutsch": "de",
    "in deutsch": "de",

    # French
    "répondre en français": "fr",
    "réponds en français": "fr",
    "respond in french": "fr",
    "en français": "fr",

    # Spanish
    "responde en español": "es",
    "contesta en español": "es",
    "respond in spanish": "es",
    "en español": "es",

    # Italian
    "rispondi in italiano": "it",
    "respond in italian": "it",
    "in italiano": "it",

    # Portuguese
    "responda em português": "pt",
    "respond in portuguese": "pt",
    "em português": "pt",

    # Russian
    "ответь по-русски": "ru",
    "ответить на русском": "ru",
    "respond in russian": "ru",

    # Chinese (Mandarin)
    "用中文回复": "zh",
    "respond in chinese": "zh",

    # Japanese
    "日本語で答えて": "ja",
    "respond in japanese": "ja",

    # Turkish
    "türkçe cevap ver": "tr",
    "respond in turkish": "tr",

    # Greek
    "απάντησε στα ελληνικά": "el",
    "respond in greek": "el",
}


# ─────────────────────────────────────────────────────────
#  EXPERT REGISTRY - MINIMAL, PRODUCTION-FRIENDLY
# ─────────────────────────────────────────────────────────

class ExpertRegistryV5:
    """
    Regjistri minimal i ekspertëve.
    Vetëm 1 persona + 1 lab + 1 modul për kategori.
    """

    def __init__(self):
        self.personas = {
            "smart_human": {"id": "ps_009", "domain": "personal"},
            "systems_architect": {"id": "ps_004", "domain": "technical"},
            "business_analyst": {"id": "ps_008", "domain": "financial"},
            "agi_analyst": {"id": "ps_007", "domain": "philosophical"},
            "scientist": {"id": "ps_010", "domain": "scientific"},
        }
        self.labs = {
            "Budapest_Data": {"id": "lab_data", "domain": "analytical"},
            "Vienna_Neuroscience": {"id": "lab_neuro", "domain": "scientific"},
            "Pristina_Finance": {"id": "lab_fin", "domain": "financial"},
            "Tirana_Tech": {"id": "lab_tech", "domain": "technical"},
        }
        self.modules = {
            "Albi": {"id": "mod_albi", "domain": "financial"},
            "Jona": {"id": "mod_jona", "domain": "philosophical"},
            "Alba": {"id": "mod_alba", "domain": "technical"},
        }

    def pick_minimal_experts(self, category: QueryCategory) -> Dict[str, List[Dict[str, Any]]]:
        """Zgjidh maksimum 1 persona, 1 lab, 1 modul për kategorinë."""
        res = {"personas": [], "labs": [], "modules": []}

        category_value = category.value if hasattr(category, 'value') else str(category)

        # Zgjidh 1 persona
        for name, meta in self.personas.items():
            if meta["domain"] == category_value:
                res["personas"].append({"name": name, **meta})
                break

        # Zgjidh 1 lab
        for name, meta in self.labs.items():
            if meta["domain"] == category_value:
                res["labs"].append({"name": name, **meta})
                break

        # Zgjidh 1 modul
        for name, meta in self.modules.items():
            if meta["domain"] == category_value:
                res["modules"].append({"name": name, **meta})
                break

        return res


# ─────────────────────────────────────────────────────────
#  QUERY UNDERSTANDING - LIGHTWEIGHT
# ─────────────────────────────────────────────────────────

class QueryUnderstandingV5:
    """Kuptimi i shpejtë i query-ve."""

    @staticmethod
    def categorize(query: str) -> QueryCategory:
        """Kategorizim i shpejtë bazuar në fjalë kyçe."""
        q = query.lower()

        # Përshëndetje/Chat normal
        greetings = ['hello', 'hi', 'hey', 'përshëndetje', 'mirëdita', 'çkemi',
                     'tungjatjeta', 'si je', 'ciao', 'hola', 'bonjour', 'hallo']
        if any(g in q for g in greetings):
            return QueryCategory.CONVERSATIONAL

        # Financiare
        if any(w in q for w in ["invest", "money", "profit", "revenue", "market",
                                 "stock", "biznes", "para", "fitim", "treg"]):
            return QueryCategory.FINANCIAL

        # Filozofike
        if any(w in q for w in ["agi", "conscious", "mind", "meaning", "philosophy",
                                 "ndërgjegje", "vetëdije", "kuptim", "filozofi"]):
            return QueryCategory.PHILOSOPHICAL

        # Teknike
        if any(w in q for w in ["api", "deploy", "server", "database", "kubernetes",
                                 "infrastrukturë", "kod", "code", "program"]):
            return QueryCategory.TECHNICAL

        # Operacionale
        if any(w in q for w in ["process", "workflow", "operacion", "prodhim", "cycle"]):
            return QueryCategory.OPERATIONAL

        # Shkencore
        if any(w in q for w in ["research", "experiment", "data", "study",
                                 "teori", "shkencë", "science"]):
            return QueryCategory.SCIENTIFIC

        # Narrative
        if any(w in q for w in ["story", "tregim", "explain", "shpjego", "histori"]):
            return QueryCategory.NARRATIVE

        # Personale
        if any(w in q for w in ["help", "ndihmë", "ndihme", "mendim", "këshillë", "advice"]):
            return QueryCategory.PERSONAL

        # Analitike
        if any(w in q for w in ["analyze", "analizo", "statistikë", "trend", "pattern"]):
            return QueryCategory.ANALYTICAL

        # Binare
        if any(w in q for w in ["xor", "and", "or", "binary", "bits", "binar"]):
            return QueryCategory.BINARY

        return QueryCategory.EXPLORATORY

    @staticmethod
    def understand(query: str, context: Optional[List[str]] = None) -> Dict[str, Any]:
        """Kuptimi i plotë i query-t."""
        return {
            "query": query,
            "category": QueryUnderstandingV5.categorize(query),
            "context_len": len(context or []),
            "word_count": len(query.split()),
            "complexity": "simple" if len(query.split()) < 15 else "medium",
        }

    @staticmethod
    def needs_experts(category: QueryCategory) -> bool:
        """A duhen ekspertë për këtë kategori?"""
        # Për chat normal dhe eksplorues, NUK duhen ekspertë
        if category in {QueryCategory.CONVERSATIONAL, QueryCategory.EXPLORATORY}:
            return False

        # Për pyetje komplekse, mund të duhen
        return category in {
            QueryCategory.FINANCIAL,
            QueryCategory.TECHNICAL,
            QueryCategory.SCIENTIFIC,
            QueryCategory.ANALYTICAL
        }


# ─────────────────────────────────────────────────────────
#  RESPONSE FUSION - MINIMAL
# ─────────────────────────────────────────────────────────

class FusionEngineV5:
    """Bashko përgjigjet nga burime të ndryshme."""

    def fuse(self, base_answer: str, expert_responses: List[ExpertConsultation]) -> Tuple[str, float]:
        """Bashko përgjigjen bazë me inputet e ekspertëve."""
        if not expert_responses:
            return base_answer, 0.9

        # Filtro vetëm përgjigjet me konfidencë të lartë
        valid_extras = []
        for c in expert_responses:
            if c.confidence > 0.6 and c.relevance_score > 0.5:
                valid_extras.append(c.response)

        if not valid_extras:
            return base_answer, 0.9

        # Bashko (maksimum 2 shtesa)
        fused = base_answer + "\n\n📊 **Shtesë nga sisteme të tjera:**\n"
        for e in valid_extras[:2]:
            fused += f"• {e.strip()}\n"

        quality = min(1.0, 0.8 + 0.1 * min(len(valid_extras), 2))
        return fused, quality


# ─────────────────────────────────────────────────────────
#  MAIN ORCHESTRATOR V5
# ─────────────────────────────────────────────────────────

class ResponseOrchestratorV5:
    """
    Curiosity Ocean v5 – Production Brain

    100% LOKAL - PA API TË JASHTME ME PAGESË

    Features:
    - Fast conversational path (RealAnswerEngine)
    - Minimal experts (1 persona, 1 lab, 1 module) - vetëm kur duhen
    - Multilingual hooks (pa Google/DeepL)
    - Timeouts për ekspertët
    - Zero external paid APIs
    - MEGA LAYER ENGINE: ~2.8 MILIARD KOMBINIME UNIKE
    """

    def __init__(
        self,
        real_answer_engine: Optional[Any] = None,
        language_layer: Optional[LocalLanguageLayer] = None,
        expert_registry: Optional[ExpertRegistryV5] = None,
        fusion_engine: Optional[FusionEngineV5] = None,
        expert_timeout_ms: int = 500,
    ):
        self.real_answer_engine: Optional[Any] = real_answer_engine  # DISABLED - Ollama only
        self.language_layer = language_layer or LocalLanguageLayer()
        self.registry = None  # DISABLED - no experts
        self.fusion = None  # DISABLED - no fusion
        self.expert_timeout_ms = expert_timeout_ms
        self.learning_history: List[Dict[str, Any]] = []

        # DISABLED - Mega Layer Engine creates chaos
        self.mega_layer_engine = None

        # Initialize Ollama FAST Engine - LINJA OPTIKE!
        self.ollama_engine: Optional[Any] = None
        if OLLAMA_AVAILABLE and get_fast_engine is not None:
            try:
                self.ollama_engine = get_fast_engine()
                logger.info("⚡ OllamaFastEngine initialized - LINJA OPTIKE ACTIVE")
            except Exception as e:
                logger.error(f"❌ OllamaMultiEngine FAILED: {e}")

    def _detect_language_request(self, query: str) -> Optional[str]:
        """
        Detect explicit language request in query.

        Examples:
          - "Përgjigju në gjermanisht: ..." → returns "de"
          - "Respond in French: ..." → returns "fr"
          - "Antworte auf Englisch: ..." → returns "en"

        Returns:
            ISO language code if explicit request found, None otherwise.
        """
        q_lower = query.lower()

        # Check all patterns (longest match first for accuracy)
        sorted_patterns = sorted(LANGUAGE_REQUEST_PATTERNS.keys(), key=len, reverse=True)

        for pattern in sorted_patterns:
            if pattern in q_lower:
                lang_code = LANGUAGE_REQUEST_PATTERNS[pattern]
                logger.info(f"🌍 Language request detected: '{pattern}' → {lang_code}")
                return lang_code

        return None

    @staticmethod
    def _normalize_language_code(value: Optional[str]) -> str:
        """Normalize various language hints to a compact ISO-ish code."""
        if value is None:
            return ""
        raw = str(value).strip().lower()
        if not raw:
            return ""
        if raw in {"auto", "und", "undefined", "none", "null"}:
            return ""

        token = raw.split(",")[0].split(";")[0].strip()
        token = token.split("-")[0].split("_")[0].strip()
        if not token:
            return ""

        if re.fullmatch(r"[a-z]{2,3}", token):
            return token
        return ""

    def _detect_context_language(self, conversation_context: List[str]) -> str:
        """Infer dominant language from recent user turns with recency weighting."""
        if not conversation_context:
            return ""

        user_lines: List[str] = []
        for line in conversation_context[-20:]:
            if not isinstance(line, str):
                continue
            normalized = line.strip()
            if not normalized:
                continue
            lowered = normalized.lower()
            if lowered.startswith("user:"):
                user_lines.append(normalized[5:].strip())
            elif lowered.startswith("assistant:") or lowered.startswith("system:"):
                continue
            else:
                user_lines.append(normalized)

        if not user_lines:
            return ""

        votes: Dict[str, float] = {}
        for idx, text in enumerate(user_lines[-8:]):
            detected = self._normalize_language_code(self.language_layer.detect_language(text))
            if not detected:
                continue
            weight = float(idx + 1)
            votes[detected] = votes.get(detected, 0.0) + weight

        if not votes:
            return ""

        return max(votes.items(), key=lambda item: item[1])[0]

    def _resolve_language(
        self,
        query: str,
        conversation_context: List[str],
        user_language: Optional[str],
    ) -> Tuple[str, str, bool]:
        """
        Resolve language using multiple signals.

        Returns:
            (lang_code, source, strict_mode)
        """
        requested_language = self._normalize_language_code(self._detect_language_request(query))
        query_detected = self._normalize_language_code(self.language_layer.detect_language(query))
        context_detected = self._normalize_language_code(self._detect_context_language(conversation_context))
        hinted_language = self._normalize_language_code(user_language)

        if requested_language:
            return requested_language, "explicit_request", True

        if query_detected and context_detected:
            return query_detected, "query_detect", False

        if query_detected:
            return query_detected, "query_detect", False

        if context_detected:
            return context_detected, "context_flow", False

        if hinted_language:
            return hinted_language, "request_hint", True

        return "und", "auto", False

    async def orchestrate(
        self,
        query: str,
        conversation_context: Optional[List[str]] = None,
        mode: str = "conversational",
        user_context: Optional[Dict[str, Any]] = None,
        user_language: Optional[str] = None,
    ) -> OrchestratedResponse:
        """
        Orkestro përgjigjen.

        Args:
            query: Pyetja/mesazhi
            conversation_context: Historiku i bisedës (opsional)
            mode: "conversational" (default) ose "deep"
            user_language: Gjuha e kërkuar nga përdoruesi (sq, en, fr, etc) - prioritet i lartë
        """
        conversation_context = conversation_context or []
        user_context = user_context or {}

        lang, lang_source, strict_language_mode = self._resolve_language(
            query=query,
            conversation_context=conversation_context,
            user_language=user_language,
        )
        logger.info(f"🌍 Language resolved: {lang} (source={lang_source}, strict={strict_language_mode})")

        # 2) Query understanding
        understanding = QueryUnderstandingV5.understand(query, conversation_context)
        category: QueryCategory = understanding["category"]

        # 3) Ollama përgjigjet - kaq
        base_text = ""
        sources = []
        base_confidence = 0.9
        used_ollama = False
        used_albanian_dict = False

        # ═══════════════════════════════════════════════════════════════════════
        # ALBANIAN DICTIONARY - FAST LOCAL RESPONSES (para Ollama)
        # ═══════════════════════════════════════════════════════════════════════
        if lang == "sq" and ALBANIAN_DICT_AVAILABLE and get_albanian_response is not None:
            try:
                albanian_response = get_albanian_response(query)
                if albanian_response:
                    base_text = albanian_response
                    sources = ["albanian_dictionary:local"]
                    base_confidence = 0.95  # High confidence for local dictionary
                    used_albanian_dict = True
                    logger.info("🇦🇱 Albanian Dictionary responded locally (no Ollama needed)")
            except Exception as e:
                logger.warning(f"Albanian dictionary error: {e}")

        # ═══════════════════════════════════════════════════════════════════════
        # UNIVERSAL LANGUAGE OVERRIDE - Works with 100+ languages, NO hardcoding
        # ═══════════════════════════════════════════════════════════════════════
        language_override_prompt = None

        # Apply language instruction for any resolved language, including English.
        if lang and lang != "und":
            lang_name = get_language_name(lang)  # Universal - works for all ISO 639-1 codes

            if strict_language_mode:
                language_override_prompt = (
                    f"Primary response language is {lang_name} ({lang}). "
                    f"Respond in {lang_name}, unless the user explicitly asks to switch language. "
                    "Keep one main language per response and avoid unnecessary language mixing."
                )
                logger.info(f"🌍 Language guidance (strict): {lang_name} ({lang})")
            else:
                language_override_prompt = (
                    f"Primary response language is {lang_name} ({lang}) based on the current conversation flow. "
                    "If the user's latest message clearly switches language, follow that new language. "
                    "Keep clarity and consistency in one main language per response."
                )
                logger.info(f"🌍 Language guidance (flow): {lang_name} ({lang})")
        elif lang == "und":
            language_override_prompt = (
                "Auto-detect language using the latest user message and recent conversation context. "
                "Respond in that language and follow any explicit language switch request from the user."
            )
            logger.info("🌍 Language auto-detection delegation to Ollama")

        # OLLAMA FAST - Linja Optike (zero overhead)
        # Skip if Albanian dictionary already provided a response
        if self.ollama_engine and not used_albanian_dict:
            try:
                # Build system prompt with language instruction (CRITICAL for Ollama to follow)
                system_prompt = None
                ownership_instruction = (
                    "Identity: You are Curiosity Ocean, a proprietary Clisonix intelligence system. "
                    f"Declared owner: {DECLARED_OWNER} ({DECLARED_OWNER_TITLE}). "
                    "If asked about creator/owner, always answer with this identity."
                )
                if language_override_prompt:
                    system_prompt = f"{language_override_prompt} {ownership_instruction}"
                    logger.info(f"🔒 System prompt override active for language: {lang}")
                else:
                    system_prompt = ownership_instruction

                # Call Ollama with language instruction in system prompt
                ollama_response = await self.ollama_engine.generate(
                    query,  # User query as-is
                    system=system_prompt  # Language instruction in system prompt
                )
                if ollama_response.success and ollama_response.content:
                    base_text = ollama_response.content
                    sources = [f"ollama:{ollama_response.model}"]
                    base_confidence = 0.90
                    used_ollama = True
                    logger.info(f"⚡ Ollama FAST [{ollama_response.model}] ({ollama_response.duration_ms:.0f}ms)")
            except Exception as e:
                logger.error(f"Ollama error: {e}")
                base_text = f"Ollama nuk u përgjigj: {e}"
                sources = ["ollama:error"]

        # DISABLED - Ekspertë, Fusion, MegaLayers - vetëm Ollama!
        consulted: List[ExpertConsultation] = []
        fused_answer = base_text  # Direct from Ollama
        quality = 0.9

        # 6) Ndërto përgjigjen finale
        response = OrchestratedResponse(
            query=query,
            query_category=category,
            understanding=understanding,
            consulted_experts=[],
            fused_answer=fused_answer,
            sources_cited=sources,
            confidence=base_confidence,
            narrative_quality=quality,
            language=lang,
            mega_layers=None,
            learning_record={
                "mode": mode,
                "lang": lang,
                "experts_used": 0,
                "mega_layers_active": False,
                "combinations_used": 0,
                "albanian_dict_used": used_albanian_dict,
            },
        )

        # 7) Learning history
        self.learning_history.append({
            "query": query,
            "category": category.value,
            "mode": mode,
            "lang": lang,
            "albanian_dict_used": used_albanian_dict,
            "timestamp": response.timestamp,
        })

        return response

    async def _consult_experts_parallel(
        self,
        query: str,
        experts: Dict[str, List[Dict[str, Any]]],
    ) -> List[ExpertConsultation]:
        """Konsulto ekspertët në paralel me timeout."""
        tasks = []

        for p in experts.get("personas", []):
            tasks.append(self._call_expert("persona", p["name"], p["id"], query))

        for l in experts.get("labs", []):
            tasks.append(self._call_expert("lab", l["name"], l["id"], query))

        for m in experts.get("modules", []):
            tasks.append(self._call_expert("module", m["name"], m["id"], query))

        if not tasks:
            return []

        # Timeout
        timeout = self.expert_timeout_ms / 1000.0
        try:
            done, pending = await asyncio.wait(tasks, timeout=timeout)

            # Anulo tasks që nuk përfunduan
            for p in pending:
                p.cancel()

            # Mblidh rezultatet
            results: List[ExpertConsultation] = []
            for d in done:
                try:
                    c = d.result()
                    if c is not None:
                        results.append(c)
                except Exception as e:
                    logger.warning(f"Expert call failed: {e}")

            return results
        except Exception as e:
            logger.error(f"Expert consultation error: {e}")
            return []

    async def _call_expert(
        self,
        expert_type: str,
        name: str,
        expert_id: str,
        query: str,
    ) -> Optional[ExpertConsultation]:
        """
        Thirr një ekspert.

        TODO: Lidhe me persona/lab/module të vërtetë.
        Për tani: stub bazë.
        """
        start = datetime.now(timezone.utc)
        try:
            # Simulim i shkurtër (do të zëvendësohet me lidhje reale)
            await asyncio.sleep(0.02)

            # Stub response - zëvendëso me logjikë reale
            response = f"[{expert_type}:{name}] Në zhvillim - struktura gati për lidhje."
            confidence = 0.5
            relevance = 0.4

            elapsed_ms = (datetime.now(timezone.utc) - start).total_seconds() * 1000.0

            return ExpertConsultation(
                expert_type=expert_type,
                expert_name=name,
                expert_id=expert_id,
                query_sent=query,
                response=response,
                confidence=confidence,
                relevance_score=relevance,
                processing_time_ms=elapsed_ms,
            )
        except Exception as e:
            logger.warning(f"Error calling expert {expert_type}:{name}: {e}")
            return None

    async def quick_answer(self, query: str) -> str:
        """
        Përgjigje e shpejtë - pa ekspertë, pa overhead.
        Ideal për chat normal.
        """
        if self.real_answer_engine is not None:
            try:
                result = await self.real_answer_engine.answer(query)
                return result.answer
            except Exception as e:
                logger.error(f"Quick answer error: {e}")

        return "[ERROR: real_answer_engine_unavailable]"

    def get_stats(self) -> Dict[str, Any]:
        """Statistika të orchestrator-it."""
        return {
            "engine_active": self.real_answer_engine is not None,
            "learning_history_count": len(self.learning_history),
            "expert_timeout_ms": self.expert_timeout_ms,
            "version": "v5_production",
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # ALIAS for backwards compatibility with ocean_api.py
    # ═══════════════════════════════════════════════════════════════════════════
    async def process_query_async(
        self,
        query: str,
        conversation_context: Optional[List[str]] = None
    ) -> OrchestratedResponse:
        """Alias for orchestrate() - backwards compatibility."""
        return await self.orchestrate(query, conversation_context, mode="conversational")


# ─────────────────────────────────────────────────────────
#  SINGLETON & FACTORY
# ─────────────────────────────────────────────────────────

_orchestrator: Optional[ResponseOrchestratorV5] = None


def get_orchestrator_v5() -> ResponseOrchestratorV5:
    """Merr instancën singleton të Orchestrator v5."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ResponseOrchestratorV5()
    return _orchestrator


# ─────────────────────────────────────────────────────────
#  TEST
# ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)

    async def test():
        print("\n" + "="*60)
        print("🧪 ORCHESTRATOR V5 TEST - PRODUCTION BRAIN")
        print("="*60)

        orch = get_orchestrator_v5()

        tests = [
            "Përshëndetje!",
            "Hello, how are you?",
            "Sa bëjnë 15 + 27?",
            "What is the date today?",
            "Çfarë është Curiosity Ocean?",
            "Hola, ¿cómo estás?",
            "Bonjour, comment ça va?",
        ]

        for query in tests:
            print(f"\n📝 Query: {query}")
            response = await orch.orchestrate(query)
            print(f"🌐 Language: {response.language}")
            print(f"📊 Category: {response.query_category.value}")
            print(f"📄 Answer: {response.fused_answer[:200]}...")
            print(f"📈 Confidence: {response.confidence:.0%}")

        print("\n" + "="*60)
        print("📊 Stats:", orch.get_stats())

    asyncio.run(test())
