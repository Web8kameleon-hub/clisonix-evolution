# ============================================================================
# CURIOSITY OCEAN API - Main API Server
# ============================================================================
# FastAPI-based knowledge portal serving global open data
# Powered by Internal AGI Engine - 100% internal, no external LLMs
# ============================================================================

import asyncio
import json
import logging
import math
import os
import re
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import httpx

# FastAPI imports
from fastapi import BackgroundTasks, FastAPI, HTTPException, Path, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

# Add parent for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)


ASK_OPERATION_TIMEOUT_SECONDS = float(os.getenv("CURIOSITY_ASK_TIMEOUT_SECONDS", "12.0"))
ASK_CONTEXT_TIMEOUT_SECONDS = float(os.getenv("CURIOSITY_CONTEXT_TIMEOUT_SECONDS", "8.0"))
ASK_REASONING_TIMEOUT_SECONDS = float(os.getenv("CURIOSITY_REASONING_TIMEOUT_SECONDS", "4.0"))
CALLBACK_POST_TIMEOUT_SECONDS = float(os.getenv("CURIOSITY_CALLBACK_TIMEOUT_SECONDS", "10.0"))


_FALLBACK_ASK_TEMPLATES: Dict[str, str] = {
    "sq": "Curiosity Ocean po kërkon në {sources} burime në {countries} shtete për: '{query}'. Kthehu pas pak për rezultate të plota.",
    "en": "Curiosity Ocean is searching through {sources} sources across {countries} countries for: '{query}'. Check back shortly for complete results.",
    "de": "Curiosity Ocean sucht in {sources} Quellen aus {countries} Ländern nach: '{query}'. Bitte schauen Sie in Kürze wieder vorbei, um vollständige Ergebnisse zu erhalten.",
    "fr": "Curiosity Ocean recherche dans {sources} sources réparties sur {countries} pays pour : '{query}'. Revenez bientôt pour obtenir les résultats complets.",
    "es": "Curiosity Ocean está buscando en {sources} fuentes de {countries} países: '{query}'. Vuelve en breve para obtener los resultados completos.",
    "it": "Curiosity Ocean sta cercando in {sources} fonti distribuite in {countries} paesi per: '{query}'. Torna a breve per i risultati completi.",
    "pt": "Curiosity Ocean está pesquisando em {sources} fontes de {countries} países por: '{query}'. Volte em breve para obter os resultados completos.",
    "tr": "Curiosity Ocean, '{query}' için {countries} ülkedeki {sources} kaynakta arama yapıyor. Tam sonuçlar için kısa süre sonra tekrar kontrol edin.",
    "ru": "Curiosity Ocean ищет по {sources} источникам в {countries} странах запрос: '{query}'. Скоро вернитесь за полными результатами.",
    "ar": "يقوم Curiosity Ocean بالبحث في {sources} مصدرًا عبر {countries} دولة عن: '{query}'. عُد بعد قليل للحصول على النتائج الكاملة.",
    "zh": "Curiosity Ocean 正在 {countries} 个国家的 {sources} 个数据源中搜索：'{query}'。请稍后回来查看完整结果。",
    "ja": "Curiosity Ocean は {countries} か国・{sources} 件のソースから「{query}」を検索しています。完全な結果はしばらくしてからご確認ください。",
}

_SEARCH_SUGGESTION_TEMPLATES: Dict[str, Dict[str, str]] = {
    "sq": {
        "broader": "Provo terma më të gjerë kërkimi",
        "remove_filters": "Hiq disa filtra për më shumë rezultate",
        "spelling": "Kontrollo drejtshkrimin",
        "related": "Provo terma të ngjashëm për më shumë rezultate",
        "categories": "Kategori të gjetura: {categories}",
    },
    "en": {
        "broader": "Try broader search terms",
        "remove_filters": "Remove some filters",
        "spelling": "Check spelling",
        "related": "Try related terms for more results",
        "categories": "Categories found: {categories}",
    },
}

_OPEN_DATA_FILTER_TEMPLATES: Dict[str, Dict[str, str]] = {
    "sq": {
        "country": "shtet:{value}",
        "region": "rajon:{value}",
        "category": "kategori:{value}",
        "all": "të gjitha (kufizuar në 100)",
        "error": "Burimet e të dhënave nuk janë të disponueshme",
    },
    "en": {
        "country": "country:{value}",
        "region": "region:{value}",
        "category": "category:{value}",
        "all": "all (limited to 100)",
        "error": "Data sources not available",
    },
}


def _language_key(value: Optional[str]) -> str:
    language = (value or "en").split("-", 1)[0].lower()
    if language in _FALLBACK_ASK_TEMPLATES:
        return language
    if language in _SEARCH_SUGGESTION_TEMPLATES:
        return language
    if language in _OPEN_DATA_FILTER_TEMPLATES:
        return language
    return "en"


def _quick_answer_for_query(query: str, language: Optional[str]) -> Optional[str]:
    language_key = _language_key(language)
    capital_patterns = [
        r"capital of\s+([^\?\.!]+)",
        r"kryeqytet(?:i)?\s+(?:i|e)\s+([^\?\.!]+)",
        r"عاصمة\s+([^\?\.!؟]+)",
    ]
    capital_aliases = {
        "germany": ("Germany", "Berlin"),
        "deutschland": ("Germany", "Berlin"),
        "gjermanisë": ("Gjermanisë", "Berlin"),
        "gjermanise": ("Gjermanisë", "Berlin"),
        "ألمانيا": ("ألمانيا", "Berlin"),
    }

    for pattern in capital_patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if not match:
            continue
        country_raw = match.group(1).strip(" ?!.؟،\"'")
        country_name, capital = capital_aliases.get(
            country_raw.casefold(),
            (country_raw, None),
        )
        if not capital:
            return None
        if language_key == "sq":
            return f"Kryeqyteti i {country_name} është {capital}."
        if language_key == "ar":
            return f"عاصمة {country_name} هي {capital}."
        return f"The capital of {country_name} is {capital}."

    return None


def _parse_region_enum(raw_value: str, region_enum: Any) -> Any:
    candidate = (raw_value or "").strip().lower()
    if not candidate:
        raise ValueError("region nuk mund të jetë bosh")
    normalized = candidate.replace("-", "_").replace(" ", "_")
    for member in region_enum:
        if member.value.lower() == candidate or member.name.lower() == normalized:
            return member
    raise ValueError(f"region '{raw_value}' nuk njihet")


def _parse_category_enum(raw_value: str, category_enum: Any) -> Any:
    candidate = (raw_value or "").strip().lower()
    if not candidate:
        raise ValueError("category nuk mund të jetë bosh")
    normalized = candidate.replace("-", "_").replace(" ", "_")
    for member in category_enum:
        if member.value.lower() == candidate or member.name.lower() == normalized:
            return member
    raise ValueError(f"category '{raw_value}' nuk njihet")


def _serialize_source(source: Any) -> Dict[str, Any]:
    return {
        "url": source.url,
        "name": source.name,
        "category": source.category.value if hasattr(source.category, "value") else str(source.category),
        "country": source.country,
        "description": source.description[:200],
        "api_available": source.api_available,
        "license": source.license,
    }


# ============================================================================
# NDV CONVERSION FUNCTIONS (Nanodecibel Resonance Metrics)
# ============================================================================

def _resonance_to_decibel(score: float) -> float:
    """Convert normalized resonance score [0,1] to decibel scale."""
    safe = max(1e-12, min(1.0, float(score)))
    return round(20.0 * math.log10(safe), 9)


def _resonance_to_nanodecibel(score: float) -> float:
    """Convert normalized resonance score [0,1] to nanodecibel scale (dB × 10^9)."""
    return round(_resonance_to_decibel(score) * 1_000_000_000.0, 3)


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class AskRequest(BaseModel):
    """Request model for /ask endpoint"""
    query: str = Field(..., min_length=1, max_length=1000, description="Your question")
    context: Optional[str] = Field(None, description="Additional context")
    language: str = Field("en", description="Response language (en, sq, de, fr, etc.)")
    max_sources: int = Field(10, ge=1, le=50, description="Maximum sources to query")
    include_reasoning: bool = Field(False, description="Include reasoning chain in response")
    callback_url: Optional[str] = Field(None, description="Webhook URL for async completion callback")
    request_id: Optional[str] = Field(None, description="Client-provided correlation/request identifier")


class SearchRequest(BaseModel):
    """Request model for /search-links"""
    query: str = Field(..., min_length=1, max_length=500)
    countries: Optional[List[str]] = Field(None, description="Filter by countries (ISO codes)")
    categories: Optional[List[str]] = Field(None, description="Filter by categories")
    language: str = Field("en", description="Response language (en, sq, de, fr, etc.)")
    api_only: bool = Field(False, description="Only return sources with APIs")
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)


class OpenDataRequest(BaseModel):
    """Request model for /open-data"""
    country: Optional[str] = Field(None, description="Country ISO code")
    region: Optional[str] = Field(None, description="Region name")
    category: Optional[str] = Field(None, description="Category name")
    language: str = Field("en", description="Response language (en, sq, de, fr, etc.)")
    format: str = Field("json", description="Output format: json, csv, summary")


class ExploreRequest(BaseModel):
    """Request model for /explore"""
    topic: str = Field(..., description="Topic to explore")
    depth: int = Field(2, ge=1, le=5, description="Exploration depth")


class AskResponse(BaseModel):
    """Response model for /ask"""
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float
    reasoning_chain: Optional[List[str]] = None
    query_id: str
    processing_time_ms: float
    measurement_unit: str = "nanodecibel"
    resonance_ndb: float = 0.0
    resonance_decibel: float = 0.0


class SearchResponse(BaseModel):
    """Response model for /search-links"""
    total: int
    results: List[Dict[str, Any]]
    query: str
    filters_applied: Dict[str, Any]
    suggestions: List[str]
    measurement_unit: str = "nanodecibel"
    resonance_ndb: float = 0.0
    resonance_decibel: float = 0.0


class OpenDataResponse(BaseModel):
    """Response model for /open-data"""
    region: str
    sources_count: int
    data: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    measurement_unit: str = "nanodecibel"
    resonance_ndb: float = 0.0
    resonance_decibel: float = 0.0


async def _post_callback(callback_url: str, payload: Dict[str, Any]) -> None:
    """Deliver final async result to client webhook."""
    timeout = httpx.Timeout(CALLBACK_POST_TIMEOUT_SECONDS)
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            callback_url,
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()


async def _run_ask_and_callback(
    ocean: "CuriosityOceanAPI",
    request: AskRequest,
    request_id: str,
    callback_url: str,
) -> None:
    """Execute ask flow and send callback with final status/result."""
    try:
        result = await ocean.ask(request)
        payload: Dict[str, Any] = {
            "event": "curiosity.ask.completed",
            "status": "completed",
            "request_id": request_id,
            "completed_at": datetime.now().isoformat(),
            "result": result.model_dump(),
        }
    except HTTPException as exc:
        payload = {
            "event": "curiosity.ask.failed",
            "status": "failed",
            "request_id": request_id,
            "completed_at": datetime.now().isoformat(),
            "error": exc.detail,
            "status_code": exc.status_code,
        }
    except Exception as exc:  # noqa: BLE001
        payload = {
            "event": "curiosity.ask.failed",
            "status": "failed",
            "request_id": request_id,
            "completed_at": datetime.now().isoformat(),
            "error": {
                "error": "internal_callback_failure",
                "message": str(exc),
            },
            "status_code": 500,
        }

    try:
        await _post_callback(callback_url, payload)
    except Exception as exc:  # noqa: BLE001
        logger.error("Callback delivery failed (request_id=%s): %s", request_id, exc)


# ============================================================================
# CURIOSITY OCEAN API CLASS
# ============================================================================

class CuriosityOceanAPI:
    """
    Main Curiosity Ocean API class

    Provides:
    - /ask - Intelligent Q&A
    - /search-links - Search 4053+ sources
    - /open-data - Access open data
    - /explore - Explore topics
    - /discover - Serendipitous discovery
    - /stream - Real-time streaming
    """

    def __init__(self):
        self.version = "1.0.0"
        self.total_sources = 4053
        self.api_sources = 988
        self.countries_covered = 155
        self._query_counter = 0

        # Initialize components
        self._init_components()

    def _init_components(self):
        """Initialize internal components"""
        try:
            # Import Internal AGI Engine
            from services.internal_agi import (
                ContextBuilder,
                FallbackManager,
                KnowledgeRouter,
                ModuleRegistry,
                ReasoningEngine,
            )

            self.module_registry = ModuleRegistry()
            self.knowledge_router = KnowledgeRouter()
            self.reasoning_engine = ReasoningEngine()
            self.context_builder = ContextBuilder()
            self.fallback_manager = FallbackManager()

            logger.info("Curiosity Ocean components initialized")

        except (ImportError, AttributeError, Exception) as e:
            logger.warning(f"Could not initialize AGI components: {e} — running in standalone mode")
            # Create mock components for standalone operation
            self.module_registry = None
            self.knowledge_router = None
            self.reasoning_engine = None
            self.context_builder = None
            self.fallback_manager = None

    def _generate_query_id(self) -> str:
        """Generate unique query ID"""
        self._query_counter += 1
        return f"co_{datetime.now().strftime('%Y%m%d%H%M%S')}_{self._query_counter:06d}"

    async def ask(self, request: AskRequest) -> AskResponse:
        """
        Process a question and return an intelligent answer

        Uses the Internal AGI Engine for reasoning - NO external LLMs
        """
        start_time = datetime.now()
        query_id = self._generate_query_id()

        try:
            if self.knowledge_router and self.reasoning_engine:
                # Route the query
                route_decision = self.knowledge_router.route(request.query)

                # Build context
                context = await asyncio.wait_for(
                    self.context_builder.build_context(
                        query=request.query,
                        sources=route_decision.primary_sources + route_decision.secondary_sources,
                        route_decision=route_decision,
                        max_sources=request.max_sources,
                    ),
                    timeout=ASK_CONTEXT_TIMEOUT_SECONDS,
                )

                # Create reasoning context
                from services.internal_agi.reasoning_engine import ReasoningContext
                reasoning_ctx = ReasoningContext(
                    query=request.query,
                    intent=self.knowledge_router.parse_query(request.query),
                    sources=context.sources,
                    data=context.data
                )

                # Get answer through reasoning engine
                result = await asyncio.wait_for(
                    self.reasoning_engine.reason(reasoning_ctx),
                    timeout=ASK_REASONING_TIMEOUT_SECONDS,
                )

                # Build response
                processing_time = (datetime.now() - start_time).total_seconds() * 1000

                return AskResponse(
                    answer=result.answer,
                    sources=[{"name": s, "type": "data_source"} for s in result.sources[:5]],
                    confidence=result.confidence,
                    reasoning_chain=result.reasoning_chain if request.include_reasoning else None,
                    query_id=query_id,
                    processing_time_ms=processing_time
                )
            else:
                # Fallback when components not available
                return await self._fallback_ask(request, query_id, start_time)

        except asyncio.TimeoutError:
            logger.warning(
                "Curiosity ask timeout reached (operation=%ss, context=%ss, reasoning=%ss)",
                ASK_OPERATION_TIMEOUT_SECONDS,
                ASK_CONTEXT_TIMEOUT_SECONDS,
                ASK_REASONING_TIMEOUT_SECONDS,
            )
            return await self._fallback_ask(request, query_id, start_time)

        except Exception as e:
            logger.error(f"Error processing ask request: {e}")
            return await self._fallback_ask(request, query_id, start_time)

    async def _fallback_ask(self, request: AskRequest, query_id: str, start_time: datetime) -> AskResponse:
        """No fake fallback responses: require async callback when engine is unavailable."""
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        callback_url = os.getenv("CURIOSITY_CALLBACK_URL", "").strip() or None

        raise HTTPException(
            status_code=503,
            detail={
                "error": "curiosity_processing_unavailable",
                "message": "Real-time reasoning is temporarily unavailable. Submit with callback for async completion.",
                "query_id": query_id,
                "callback_required": True,
                "callback_url": callback_url,
                "processing_time_ms": processing_time,
            },
        )


    async def search_links(self, request: SearchRequest) -> SearchResponse:
        """
        Search across all data sources for relevant links

        Returns matching sources based on query and filters
        """
        results: List[Dict[str, Any]] = []
        filters_applied: Dict[str, Any] = {}
        language = _language_key(request.language)

        try:
            # Import data sources
            from data_sources import (
                SourceCategory,
                get_all_sources,
                get_sources_by_category,
                get_sources_by_country,
            )

            sources: List[Any]

            # Apply filters
            if request.countries:
                filters_applied["countries"] = request.countries
                sources = []
                for country in request.countries:
                    sources.extend(get_sources_by_country(country))
            elif request.categories:
                filters_applied["categories"] = request.categories
                sources = []
                for cat in request.categories:
                    sources.extend(get_sources_by_category(_parse_category_enum(cat, SourceCategory)))
            else:
                sources = get_all_sources()

            # Filter by API availability
            if request.api_only:
                filters_applied["api_only"] = True
                sources = [s for s in sources if s.api_available]

            # Search by query
            query_lower = request.query.lower()
            matching = []
            for source in sources:
                if query_lower in source.name.lower() or query_lower in source.description.lower():
                    matching.append(_serialize_source(source))

            # Pagination
            total = len(matching)
            results = matching[request.offset:request.offset + request.limit]

            # Generate suggestions
            suggestions = self._generate_search_suggestions(request.query, results, language)

        except ImportError:
            # Return sample data if data_sources not available
            results = [
                {"name": "Example Source", "url": "https://example.com", "category": "General", "country": "Global"}
            ]
            total = 1
            suggestions = self._generate_search_suggestions(request.query, results, language)

        return SearchResponse(
            total=total,
            results=results,
            query=request.query,
            filters_applied=filters_applied,
            suggestions=suggestions
        )

    def _generate_search_suggestions(self, query: str, results: List[Dict[str, Any]], language: str = "en") -> List[str]:
        """Generate search suggestions based on results"""
        templates = _SEARCH_SUGGESTION_TEMPLATES.get(language, _SEARCH_SUGGESTION_TEMPLATES["en"])
        suggestions = []

        if len(results) == 0:
            suggestions.append(templates["broader"])
            suggestions.append(templates["remove_filters"])
            suggestions.append(templates["spelling"])
        elif len(results) < 5:
            suggestions.append(templates["related"])

        # Suggest categories from results
        categories = set(r.get("category", "") for r in results[:10])
        if categories:
            suggestions.append(templates["categories"].format(categories=", ".join(list(categories)[:3])))

        return suggestions[:3]

    async def get_open_data(self, request: OpenDataRequest) -> OpenDataResponse:
        """
        Get open data from specified region/country/category
        """
        sources: List[Any] = []
        metadata: Dict[str, Any] = {}
        language = _language_key(request.language)

        try:
            from data_sources import (
                Region,
                SourceCategory,
                get_all_sources,
                get_sources_by_category,
                get_sources_by_country,
                get_sources_by_region,
            )
            labels = _OPEN_DATA_FILTER_TEMPLATES.get(language, _OPEN_DATA_FILTER_TEMPLATES["en"])

            if request.country:
                sources = get_sources_by_country(request.country)
                metadata["filter"] = labels["country"].format(value=request.country)
            elif request.region:
                region = _parse_region_enum(request.region, Region)
                sources = get_sources_by_region(region)
                metadata["filter"] = labels["region"].format(value=request.region)
            elif request.category:
                category = _parse_category_enum(request.category, SourceCategory)
                sources = get_sources_by_category(category)
                metadata["filter"] = labels["category"].format(value=request.category)
            else:
                sources = get_all_sources()[:100]
                metadata["filter"] = labels["all"]

            # Format data
            data = [_serialize_source(s) for s in sources[:50]]

            metadata["total_in_filter"] = len(sources)
            metadata["returned"] = len(data)

        except ImportError:
            data = []
            metadata["error"] = _OPEN_DATA_FILTER_TEMPLATES["en"]["error"]
        except ValueError as exc:
            data = []
            metadata["error"] = str(exc)

        region_name = request.country or request.region or request.category or "Global"

        return OpenDataResponse(
            region=region_name,
            sources_count=len(data),
            data=data,
            metadata=metadata
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get Curiosity Ocean statistics"""
        return {
            "version": self.version,
            "total_sources": self.total_sources,
            "api_sources": self.api_sources,
            "countries_covered": self.countries_covered,
            "queries_processed": self._query_counter,
            "regions": [
                "Europe", "Asia-China", "India-South Asia", "Americas",
                "Africa-Middle East", "Asia-Oceania", "Caribbean-Central America",
                "Pacific Islands", "Central Asia-Caucasus", "Eastern Europe-Balkans"
            ],
            "categories": [
                "Government", "University", "Hospital", "Bank", "Statistics",
                "Technology", "News", "Culture", "Sport", "Entertainment",
                "Tourism", "Transport", "Energy", "Telecom", "Research",
                "Industry", "Environmental", "Agriculture", "Hobby", "Playful"
            ],
            "services": {
                "hq": {"port": 8000, "status": "active"},
                "alba": {"port": 5555, "status": "active"},
                "albi": {"port": 6680, "status": "active"},
                "jona": {"port": 7777, "status": "active"}
            }
        }


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""

    app = FastAPI(
        title="Curiosity Ocean API",
        description="Global Knowledge Portal - 4053+ sources, 155+ countries",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize API
    ocean = CuriosityOceanAPI()

    # ========================================================================
    # ENDPOINTS
    # ========================================================================

    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "service": "Curiosity Ocean",
            "version": ocean.version,
            "description": "Global Knowledge Portal",
            "endpoints": {
                "/ask": "Ask any question",
                "/search-links": "Search data sources",
                "/open-data": "Access open data",
                "/explore": "Explore topics",
                "/discover": "Serendipitous discovery",
                "/stats": "Service statistics"
            },
            "stats": {
                "sources": ocean.total_sources,
                "countries": ocean.countries_covered,
                "api_endpoints": ocean.api_sources
            }
        }

    @app.post("/ask")
    async def ask_endpoint(request: AskRequest, background_tasks: BackgroundTasks):
        """
        Ask any question - powered by Internal AGI Engine

        Examples:
        - "What is the population of Germany?"
        - "List universities in Japan"
        - "Compare healthcare systems in UK and France"
        """
        callback_url = (request.callback_url or "").strip()
        if callback_url:
            request_id = (request.request_id or "").strip() or f"cb_{uuid.uuid4().hex}"
            background_tasks.add_task(
                _run_ask_and_callback,
                ocean,
                request,
                request_id,
                callback_url,
            )
            return JSONResponse(
                status_code=202,
                content={
                    "status": "accepted",
                    "mode": "callback",
                    "request_id": request_id,
                    "callback_url": callback_url,
                    "callback_required": False,
                    "reason": "async_processing_started",
                },
            )

        return await ocean.ask(request)

    @app.post("/search-links", response_model=SearchResponse)
    async def search_links_endpoint(request: SearchRequest):
        """
        Search across 4053+ data sources

        Filter by:
        - Countries (ISO codes)
        - Categories (government, university, hospital, etc.)
        - API availability
        """
        return await ocean.search_links(request)

    @app.post("/open-data", response_model=OpenDataResponse)
    async def open_data_endpoint(request: OpenDataRequest):
        """
        Access open data from 155+ countries

        Filter by country, region, or category
        """
        return await ocean.get_open_data(request)

    @app.get("/explore/{topic}")
    async def explore_endpoint(
        topic: str = Path(..., description="Topic to explore"),
        depth: int = Query(2, ge=1, le=5)
    ):
        """Explore a topic with connections"""
        return {
            "topic": topic,
            "depth": depth,
            "exploration": {
                "related_sources": [],
                "related_topics": [],
                "data_availability": "checking..."
            }
        }

    @app.get("/discover")
    async def discover_endpoint(
        category: Optional[str] = Query(None),
        country: Optional[str] = Query(None)
    ):
        """Serendipitous discovery - find unexpected knowledge"""
        import random

        categories = ["Government", "University", "Technology", "Culture", "Sport", "Entertainment"]
        countries = ["Germany", "Japan", "Brazil", "Australia", "Kenya", "India"]

        return {
            "discovery_mode": "serendipity",
            "suggested_topic": random.choice(categories),
            "suggested_country": random.choice(countries),
            "prompt": f"Explore {random.choice(categories)} data from {random.choice(countries)}",
            "endpoint": "/open-data"
        }

    @app.get("/stats")
    async def stats_endpoint():
        """Get Curiosity Ocean statistics"""
        return ocean.get_stats()

    @app.get("/health")
    async def health_endpoint():
        """Health check"""
        return {
            "status": "healthy",
            "service": "curiosity_ocean",
            "timestamp": datetime.now().isoformat()
        }

    @app.get("/regions")
    async def regions_endpoint():
        """List all available regions"""
        return {
            "regions": [
                {"id": "europe", "name": "Europe", "countries": 25},
                {"id": "asia_china", "name": "Asia-China", "countries": 7},
                {"id": "india_south_asia", "name": "India & South Asia", "countries": 8},
                {"id": "americas", "name": "Americas", "countries": 16},
                {"id": "africa_middle_east", "name": "Africa & Middle East", "countries": 25},
                {"id": "asia_oceania", "name": "Asia-Oceania & Global", "countries": 15},
                {"id": "caribbean_central_america", "name": "Caribbean & Central America", "countries": 20},
                {"id": "pacific_islands", "name": "Pacific Islands", "countries": 12},
                {"id": "central_asia_caucasus", "name": "Central Asia & Caucasus", "countries": 8},
                {"id": "eastern_europe_balkans", "name": "Eastern Europe & Balkans", "countries": 19}
            ],
            "total_countries": 155
        }

    @app.get("/categories")
    async def categories_endpoint():
        """List all available categories"""
        return {
            "categories": [
                {"id": "government", "name": "Government", "icon": "🏛️"},
                {"id": "university", "name": "University/Education", "icon": "🎓"},
                {"id": "hospital", "name": "Healthcare", "icon": "🏥"},
                {"id": "bank", "name": "Banking/Finance", "icon": "🏦"},
                {"id": "statistics", "name": "Statistics", "icon": "📊"},
                {"id": "technology", "name": "Technology", "icon": "💻"},
                {"id": "news", "name": "News/Media", "icon": "📰"},
                {"id": "culture", "name": "Culture/Heritage", "icon": "🏛️"},
                {"id": "sport", "name": "Sports", "icon": "⚽"},
                {"id": "entertainment", "name": "Entertainment", "icon": "🎬"},
                {"id": "tourism", "name": "Tourism", "icon": "✈️"},
                {"id": "transport", "name": "Transport", "icon": "🚂"},
                {"id": "energy", "name": "Energy", "icon": "⚡"},
                {"id": "telecom", "name": "Telecommunications", "icon": "📡"},
                {"id": "research", "name": "Research", "icon": "🔬"},
                {"id": "industry", "name": "Industry", "icon": "🏭"},
                {"id": "environmental", "name": "Environment", "icon": "🌍"},
                {"id": "agriculture", "name": "Agriculture", "icon": "🌾"},
                {"id": "hobby", "name": "Hobby/Lifestyle", "icon": "🎨"},
                {"id": "playful", "name": "Playful/Fun", "icon": "🎮"}
            ],
            "total_categories": 20
        }

    return app


# ============================================================================
# MAIN
# ============================================================================

# Module-level app for uvicorn
app = create_app()

if __name__ == "__main__":
    import uvicorn

    # Port 8011 - Curiosity Ocean
    uvicorn.run(app, host="0.0.0.0", port=8031)
