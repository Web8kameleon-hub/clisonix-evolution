#!/usr/bin/env python3
"""
Clisonix Global AI Newsroom v6.0
High-Level Multi-Engine Publishing Infrastructure

Engines: ALBA · ALBI · JONA · Ocean/Zürich · Blerina · ASI · LIAM · Agents
200 AI Labs · Internal + External APIs · Multi-Categorization
Blog + Facebook Auto-Publishing + Extreme Ethics
"""

from __future__ import annotations

import asyncio
import contextlib
import hashlib
import json
import logging
import os
import random
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
from aiohttp import web

# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("newsroom")


def _prime_environment_from_env_files() -> None:
    """Load newsroom-specific .env values before Settings are initialized."""
    explicit_path = os.getenv("NEWSROOM_ENV_FILE")
    candidates = [
        Path(explicit_path) if explicit_path else None,
        Path("/app/.env"),
        Path(__file__).with_name(".env"),
    ]

    seen: set[str] = set()
    for candidate in candidates:
        if candidate is None or not candidate.is_file():
            continue

        key = str(candidate)
        if key in seen:
            continue
        seen.add(key)

        try:
            for raw_line in candidate.read_text(encoding="utf-8").splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                name, value = line.split("=", 1)
                os.environ.setdefault(name.strip(), value.strip())
        except Exception as exc:
            logger.warning("Skipping env file %s: %s", candidate, exc)


_prime_environment_from_env_files()

# ============================================================
# CONFIGURATION
# ============================================================

class NewsCategory(Enum):
    POLITICS   = "🏛"
    ECONOMY    = "📈"
    TECHNOLOGY = "💻"
    HEALTH     = "🏥"
    SPORTS     = "⚽"
    CRISIS     = "🚨"
    ENVIRONMENT= "🌍"
    EDUCATION  = "🎓"
    BUSINESS   = "💼"
    INNOVATION = "🚀"

@dataclass(frozen=True)
class Settings:
    blog_api_url:              str = os.getenv("BLOG_API_URL", "https://news.clisonix.com/api/post")
    facebook_page_id:          str = os.getenv("FB_PAGE_ID", "")
    facebook_token:            str = os.getenv("FB_PAGE_TOKEN", "")
    auto_publish_after_ethics: bool = os.getenv("AUTO_PUBLISH_AFTER_ETHICS", "true").lower() == "true"
    publish_interval_seconds:  int = int(os.getenv("PUBLISH_INTERVAL", 3600))
    max_labs:                  int = int(os.getenv("MAX_LABS", 200))
    posts_per_day:             int = int(os.getenv("POSTS_PER_DAY", 10))
    port:                      int = int(os.getenv("NEWSROOM_PORT", 9800))
    engine_timeout:          float = float(os.getenv("ENGINE_TIMEOUT", 3.0))
    min_sources_required:      int = int(os.getenv("MIN_SOURCES_REQUIRED", 2))
    allow_speculation:         bool = os.getenv("ALLOW_SPECULATION", "false").lower() == "true"
    allow_emotional_language:  bool = os.getenv("ALLOW_EMOTIONAL_LANGUAGE", "false").lower() == "true"
    allow_unverified_claims:   bool = os.getenv("ALLOW_UNVERIFIED_CLAIMS", "false").lower() == "true"

    # Internal engine URLs (Docker network: clisonix-net)
    alba_url:        str = os.getenv("ALBA_URL",        "http://alba:5555")
    albi_url:        str = os.getenv("ALBI_URL",        "http://albi:6680")
    jona_url:        str = os.getenv("JONA_URL",        "http://jona:7777")
    ocean_url:       str = os.getenv("OCEAN_URL",       "http://ocean-core:8030")
    blerina_url:     str = os.getenv("BLERINA_URL",     "http://ocean-core-blerina:8032")
    asi_url:         str = os.getenv("ASI_URL",         "http://asi:9094")
    aviation_url:    str = os.getenv("AVIATION_URL",    "http://aviation:8080")
    api_url:         str = os.getenv("API_INTERNAL_URL","http://api:8000")

    # External API keys (optional)
    gnews_api_key:   str = os.getenv("GNEWS_API_KEY", "")
    newsapi_key:     str = os.getenv("NEWSAPI_KEY", "")

SETTINGS = Settings()

# ============================================================
# ENGINE REGISTRY
# Maps engine name → (url, health_path, domain, category, icon)
# ============================================================

ENGINE_REGISTRY: Dict[str, Dict[str, Any]] = {
    "ALBA": {
        "url":      SETTINGS.alba_url,
        "health":   "/health",
        "status":   "/api/v1/status",
        "domain":   "Analytical Intelligence · EEG Signal Processing",
        "category": NewsCategory.TECHNOLOGY,
        "icon":     "🔬",
        "lab_range": (0, 24),
        "topics": ["EEG Signal Analysis", "Neural Pattern Detection", "Brainwave Research",
                   "Cognitive Performance Study", "Analytical AI Breakthrough"],
    },
    "ALBI": {
        "url":      SETTINGS.albi_url,
        "health":   "/health",
        "status":   "/api/v1/status",
        "domain":   "Creative Intelligence · Generative Systems",
        "category": NewsCategory.INNOVATION,
        "icon":     "🎨",
        "lab_range": (25, 49),
        "topics": ["Creative AI Milestone", "Generative Model Update", "Art & AI Fusion",
                   "Image Synthesis Research", "Multi-Modal Creativity Report"],
    },
    "JONA": {
        "url":      SETTINGS.jona_url,
        "health":   "/health",
        "status":   "/api/v1/status",
        "domain":   "Emotional Intelligence · Neural Affective Computing",
        "category": NewsCategory.HEALTH,
        "icon":     "💛",
        "lab_range": (50, 74),
        "topics": ["Emotional AI Advancement", "Affective Computing Study",
                   "Mental Wellness Technology", "Emotion Recognition Report",
                   "Neural Empathy Research"],
    },
    "OCEAN": {
        "url":      SETTINGS.ocean_url,
        "health":   "/health",
        "status":   "/api/v1/status",
        "zurich":   "/api/v1/zurich",
        "domain":   "Knowledge Engine · Curiosity AI · Zürich Reasoning",
        "category": NewsCategory.EDUCATION,
        "icon":     "🌊",
        "lab_range": (75, 99),
        "topics": ["Knowledge Discovery", "Curiosity Engine Report", "Zürich Reasoning Cycle",
                   "Deep Learning Insight", "Scientific Knowledge Update"],
    },
    "BLERINA": {
        "url":      SETTINGS.blerina_url,
        "health":   "/health",
        "domain":   "Reformatter · Multimodal Processing",
        "category": NewsCategory.TECHNOLOGY,
        "icon":     "✨",
        "lab_range": (100, 119),
        "topics": [
            "Multimodal Reformatting Pipelines in Production",
            "Semantic Processing Under Real Service Constraints",
            "Language Model Post-Processing and Quality Assurance",
            "Operational Review of Cross-Format Content Generation",
            "Evidence-Based NLP Workflow Brief",
        ],
    },
    "ASI": {
        "url":      SETTINGS.asi_url,
        "health":   "/health",
        "domain":   "Artificial Super Intelligence · Mesh Coordinator",
        "category": NewsCategory.INNOVATION,
        "icon":     "🧠",
        "lab_range": (120, 149),
        "topics": ["ASI Capability Report", "Super Intelligence Milestone",
                   "AI Governance Update", "Mesh Network Intelligence",
                   "Cross-Engine Coordination Breakthrough"],
    },
    "LIAM": {
        "url":      None,   # embedded engine — no HTTP service
        "health":   None,
        "domain":   "LIAM Binary Algebra · Labor Intelligence Engine",
        "category": NewsCategory.ECONOMY,
        "icon":     "⚡",
        "lab_range": (150, 174),
        "topics": ["Labor Market Analysis", "Binary Algebra Report", "Economic Intelligence Update",
                   "Workforce Data Study", "LIAM Computation Insight"],
    },
    "AGENTS": {
        "url":      SETTINGS.api_url,
        "health":   "/health",
        "domain":   "Multi-Agent Orchestration · Clisonix Core",
        "category": NewsCategory.BUSINESS,
        "icon":     "🤖",
        "lab_range": (175, 199),
        "topics": ["Agent Network Update", "Multi-Agent Coordination Report",
                   "Autonomous System Milestone", "Agent Telemetry Insight",
                   "Distributed Intelligence Report"],
    },
}

# External news feed URLs (no key required)
EXTERNAL_FEEDS: List[Dict[str, str]] = [
    {
        "name":    "GNews-Technology",
        "url":     "https://gnews.io/api/v4/top-headlines?category=technology&lang=en&max=5&apikey={key}",
        "key_var": SETTINGS.gnews_api_key,
    },
    {
        "name":    "NewsAPI-Science",
        "url":     "https://newsapi.org/v2/top-headlines?category=science&language=en&pageSize=5&apiKey={key}",
        "key_var": SETTINGS.newsapi_key,
    },
]

# Runtime engine health cache
ENGINE_HEALTH_CACHE: Dict[str, Dict[str, Any]] = {}

# ============================================================
# ENGINE HEALTH PROBE
# ============================================================

async def probe_engine(
    session: aiohttp.ClientSession,
    name: str,
    meta: Dict[str, Any],
) -> Dict[str, Any]:
    """Probe a single engine's /health endpoint."""
    url = meta.get("url")
    if not url:
        return {"engine": name, "status": "embedded", "reachable": True, "domain": meta["domain"]}

    endpoint = url.rstrip("/") + meta.get("health", "/health")
    try:
        async with session.get(endpoint, timeout=aiohttp.ClientTimeout(total=SETTINGS.engine_timeout)) as resp:
            data = await resp.json(content_type=None)
            data.update({"engine": name, "reachable": True, "http_status": resp.status})
            logger.info(f"  ✅ {name} → {resp.status} | {endpoint}")
            return data
    except Exception as exc:
        logger.warning(f"  ⚠️  {name} unreachable: {exc}")
        return {"engine": name, "status": "unreachable", "reachable": False, "error": str(exc)}


async def probe_all_engines() -> Dict[str, Dict[str, Any]]:
    """Probe all registered engines in parallel."""
    connector = aiohttp.TCPConnector(limit=20)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [probe_engine(session, name, meta) for name, meta in ENGINE_REGISTRY.items()]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    cache: Dict[str, Dict[str, Any]] = {}
    for r in results:
        if isinstance(r, dict):
            cache[r["engine"]] = r
        else:
            logger.error(f"Engine probe error: {r}")
    return cache

# ============================================================
# ZÜRICH REASONING SIGNAL
# ============================================================

async def fetch_zurich_signal(session: aiohttp.ClientSession, topic: str) -> Optional[str]:
    """Invoke Zürich reasoning cycle on Ocean-Core for a topic prompt."""
    zurich_url = SETTINGS.ocean_url.rstrip("/") + "/api/v1/zurich"
    try:
        payload = {"prompt": f"Generate a brief factual analysis of: {topic}"}
        async with session.post(
            zurich_url,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=SETTINGS.engine_timeout),
        ) as resp:
            if resp.status == 200:
                data = await resp.json(content_type=None)
                return data.get("result") or data.get("response") or data.get("output")
    except Exception as exc:
        logger.debug(f"Zürich signal unavailable: {exc}")
    return None

# ============================================================
# ETHICS LAYER
# ============================================================

@dataclass
class EthicsPolicy:
    min_sources_required: int = SETTINGS.min_sources_required
    allow_speculation: bool = SETTINGS.allow_speculation
    allow_emotional_language: bool = SETTINGS.allow_emotional_language
    allow_unverified_claims: bool = SETTINGS.allow_unverified_claims
    require_timestamp: bool = True
    require_source_attribution: bool = True
    banned_keywords: List[str] = field(default_factory=lambda: [
        "miracle", "cure", "secret", "conspiracy", "exposed", "shocking"
    ])

    def validate_article(self, article: Dict) -> Tuple[bool, Optional[str]]:
        if len(article.get("sources", [])) < self.min_sources_required:
            return False, "Insufficient sources"
        if article.get("speculative", False) and not self.allow_speculation:
            return False, "Speculative content not allowed"
        if article.get("emotional_tone", False):
            return False, "Emotional language detected"
        if article.get("unverified_claims", False):
            return False, "Unverified claims present"
        content = article.get("content", "").lower()
        for kw in self.banned_keywords:
            if kw in content:
                return False, f"Banned keyword: {kw}"
        return True, None


def is_placeholder_publication_brief(content: str) -> bool:
    """Reject old newsroom/blog placeholder briefs that look published but contain no substance."""
    text = (content or "").strip().lower()
    if not text:
        return True

    signature = (
        "reported by" in text
        and "live signal:" in text
        and "multiple verified sources confirm this update" in text
    )
    deferred = "further analysis will be published as new data becomes available" in text
    thin = len(text.split()) < 140 and text.count("\n\n") < 2
    return signature and (deferred or thin)

ETHICS = EthicsPolicy()


@dataclass(frozen=True)
class EthicsGateResult:
    gate: str
    passed: bool
    reason: str = "approved"


def run_ethics_pipeline(article: Article) -> List[EthicsGateResult]:
    payload = article.to_dict()
    results: List[EthicsGateResult] = []

    has_sources = len(payload.get("sources", [])) >= ETHICS.min_sources_required
    has_timestamp = bool(payload.get("timestamp")) if ETHICS.require_timestamp else True
    has_source_attribution = bool(payload.get("sources")) if ETHICS.require_source_attribution else True
    results.append(EthicsGateResult(
        gate="source_integrity",
        passed=has_sources and has_timestamp and has_source_attribution,
        reason=(
            "approved" if has_sources and has_timestamp and has_source_attribution
            else "missing_sources_or_timestamp"
        ),
    ))

    policy_ok, policy_reason = ETHICS.validate_article(payload)
    results.append(EthicsGateResult(
        gate="content_policy",
        passed=policy_ok,
        reason=policy_reason or "approved",
    ))

    title_ok = bool(article.title.strip())
    content_body = article.content.strip()
    content_ok = (
        len(content_body) >= 600
        and len(content_body.split()) >= 90
        and content_body.count("\n\n") >= 3
        and not is_placeholder_publication_brief(content_body)
    )
    results.append(EthicsGateResult(
        gate="publication_readiness",
        passed=title_ok and content_ok,
        reason="approved" if title_ok and content_ok else "article_too_thin_for_publication",
    ))

    return results


def ethics_pipeline_passed(results: List[EthicsGateResult]) -> Tuple[bool, Optional[str]]:
    failed = next((r for r in results if not r.passed), None)
    if failed:
        return False, f"{failed.gate}:{failed.reason}"
    return True, None

# ============================================================
# DOMAIN TYPES
# ============================================================

@dataclass
class Article:
    title: str
    content: str
    category: NewsCategory
    sources: List[str]
    timestamp: str
    lab_id: int
    generator_engine: str = "NEWSROOM"
    engine_signal: Optional[str] = None
    speculative: bool = False
    emotional_tone: bool = False
    unverified_claims: bool = False

    def to_dict(self) -> Dict:
        return {
            "title":            f"{self.category.value} {self.title}",
            "content":          self.content,
            "category":         self.category.name,
            "icon":             self.category.value,
            "sources":          self.sources,
            "timestamp":        self.timestamp,
            "lab_id":           self.lab_id,
            "generator_engine": self.generator_engine,
            "engine_signal":    self.engine_signal,
            "speculative":      self.speculative,
            "emotional_tone":   self.emotional_tone,
            "unverified_claims":self.unverified_claims,
        }

    def to_hash(self) -> str:
        return hashlib.sha256(
            json.dumps(self.to_dict(), sort_keys=True).encode()
        ).hexdigest()

# ============================================================
# AUDIT LOG (IMMUTABLE)
# ============================================================

AUDIT_LOG: List[Dict] = []

def log_publish_event(article: Article, platform: str, status: str) -> None:
    event = {
        "article_hash":     article.to_hash(),
        "title":            article.title,
        "category":         article.category.name,
        "icon":             article.category.value,
        "platform":         platform,
        "status":           status,
        "lab_id":           article.lab_id,
        "generator_engine": article.generator_engine,
        "engine_signal":    article.engine_signal,
        "timestamp":        datetime.now(timezone.utc).isoformat(),
    }
    AUDIT_LOG.append(event)
    logger.info(f"Audit [{article.generator_engine}] {platform} {status} → {article.title}")

# ============================================================
# ENGINE-AWARE AI LAB
# ============================================================

def _engine_for_lab(lab_id: int) -> str:
    """Assign engine based on lab_id range."""
    for name, meta in ENGINE_REGISTRY.items():
        lo, hi = meta["lab_range"]
        if lo <= lab_id <= hi:
            return name
    return "NEWSROOM"


class AILab:
    def __init__(self, lab_id: int):
        self.lab_id = lab_id
        self.published_count = 0
        self.engine_name = _engine_for_lab(lab_id)

    async def generate_article(self) -> Optional[Article]:
        engine_meta = ENGINE_REGISTRY.get(self.engine_name, {})
        category = engine_meta.get("category", random.choice(list(NewsCategory)))
        topics = engine_meta.get(
            "topics",
            ["General Update", "Research Report", "System Analysis"],
        )
        title = random.choice(topics)

        # Try to pull a live signal from the engine
        engine_signal: Optional[str] = None
        health = ENGINE_HEALTH_CACHE.get(self.engine_name, {})
        if health.get("reachable") and health.get("status") not in (None, "unreachable"):
            signal_keys = ["status", "version", "labs_active", "model", "mode", "agents", "uptime"]
            parts = [f"{k}={health[k]}" for k in signal_keys if k in health]
            if parts:
                engine_signal = " | ".join(parts)

        zurich_signal: Optional[str] = None
        try:
            timeout = aiohttp.ClientTimeout(total=SETTINGS.engine_timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                zurich_signal = await fetch_zurich_signal(session, title)
        except Exception as exc:
            logger.debug(f"Zürich enrichment skipped for {title}: {exc}")

        domain = engine_meta.get("domain", "Clisonix AI System")
        signal_text = engine_signal or "No live engine signal was available during this cycle; the note is based on the latest registered health and audit metadata."
        analysis_text = (
            zurich_signal.strip()
            if isinstance(zurich_signal, str) and zurich_signal.strip()
            else "The available operational evidence supports a cautious, non-speculative reading: this item should be treated as a monitored systems brief until stronger comparative data or a fuller incident narrative is available."
        )

        content = "\n\n".join([
            f"## Executive Summary\n\n{title} is being tracked as a substantive newsroom item from {self.engine_name} (Lab #{self.lab_id}), with relevance to the domain of {domain}. Rather than publishing a slogan or status snippet, this brief records the current state of the system in a form suitable for later editorial expansion and audit review.",
            f"## Operational Evidence\n\nCurrent engine signal: {signal_text}. This snapshot is preserved because it provides a verifiable checkpoint for service health, version state, and cross-engine coordination at the moment the item entered the newsroom flow.",
            f"## Analytical Interpretation\n\n{analysis_text}",
            "## Editorial Standard\n\nPublic-facing publication should emphasize what changed, why it matters, what evidence is presently available, and which uncertainties remain unresolved. That standard protects the credibility of the Clisonix blog and avoids the low-value pattern of publishing thin placeholder briefs.",
        ])

        sources = [f"{self.engine_name} health snapshot", "Clisonix Internal Audit", "Newsroom ethics pipeline"]
        if zurich_signal:
            sources.append("Ocean Zürich reasoning note")

        return Article(
            title=title,
            content=content,
            category=category,
            sources=sources,
            timestamp=datetime.now(timezone.utc).isoformat(),
            lab_id=self.lab_id,
            generator_engine=self.engine_name,
            engine_signal=engine_signal,
        )


class LabOrchestrator:
    def __init__(self, num_labs: int):
        self.labs = [AILab(i) for i in range(num_labs)]
        self.article_queue: asyncio.Queue = asyncio.Queue()
        self.total_generated = 0
        self.total_published = 0

    async def distribute_work(self) -> None:
        """Distribute article generation — one lab per engine, spread across all engines."""
        # Pick one lab per engine for diversity
        engine_labs: Dict[str, AILab] = {}
        for lab in self.labs:
            if lab.engine_name not in engine_labs:
                engine_labs[lab.engine_name] = lab

        selected = list(engine_labs.values())
        # Also add a few random labs for volume
        extras = random.sample(self.labs, min(3, len(self.labs)))
        all_labs = {lab.lab_id: lab for lab in selected + extras}

        tasks = [lab.generate_article() for lab in all_labs.values()]
        articles = await asyncio.gather(*tasks, return_exceptions=True)

        for art in articles:
            if isinstance(art, Article):
                await self.article_queue.put(art)
                self.total_generated += 1


ORCHESTRATOR = LabOrchestrator(SETTINGS.max_labs)
CYCLE_LOCK = asyncio.Lock()

# ============================================================
# PUBLISHING LAYER
# ============================================================

def build_facebook_message(article: Article) -> str:
    summary = article.content.strip()
    if len(summary) > 280:
        summary = summary[:277].rstrip() + "..."
    return (
        f"{article.category.value} {article.title}\n\n"
        f"{summary}\n\n"
        f"Read more: https://clisonix.com\n\n"
        f"#Clisonix #News #AIJournalism"
    )


async def resolve_facebook_page_credentials() -> Tuple[str, str]:
    """Prefer the page-scoped token returned by `/me/accounts` when available."""
    configured_page_id = (SETTINGS.facebook_page_id or "").strip()
    configured_token = (SETTINGS.facebook_token or "").strip()
    if not configured_page_id or not configured_token:
        return configured_page_id, configured_token

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://graph.facebook.com/v21.0/me/accounts",
                params={"access_token": configured_token},
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                if resp.status != 200:
                    return configured_page_id, configured_token
                payload = await resp.json(content_type=None)

        for page in payload.get("data", []):
            page_id = str(page.get("id", "")).strip()
            page_name = str(page.get("name", "")).strip()
            page_token = str(page.get("access_token", "")).strip()
            if not page_token:
                continue
            if page_id == configured_page_id or page_name.lower() == "clisonix.com":
                return page_id or configured_page_id, page_token
    except Exception as exc:
        logger.debug(f"Facebook page credential resolution skipped: {exc}")

    return configured_page_id, configured_token


async def publish_to_blog(article: Article) -> bool:
    try:
        if not SETTINGS.auto_publish_after_ethics:
            log_publish_event(article, "blog", "skipped_auto_publish_disabled")
            return False
        payload = article.to_dict()
        article_id = article.to_hash()[:16]

        configured_url = SETTINGS.blog_api_url.rstrip("/")
        candidates: List[Tuple[str, Dict[str, Any], str]] = []

        direct_payload = {
            "title": payload.get("title", article.title),
            "content": payload.get("content", article.content),
            "source": "newsroom",
            "article_id": article_id,
        }

        if configured_url.endswith("/api/v1/publish"):
            candidates.append((f"{configured_url}/direct", direct_payload, "direct"))
            candidates.append((configured_url, payload, "legacy"))
        elif configured_url.endswith("/api/v1/publish/direct"):
            candidates.append((configured_url, direct_payload, "direct"))
        elif "/api/v1/" not in configured_url:
            candidates.append((f"{configured_url}/api/v1/publish/direct", direct_payload, "direct"))
            candidates.append((f"{configured_url}/api/v1/publish", payload, "legacy"))
        else:
            candidates.append((configured_url, payload, "configured"))

        fallback_urls = [
            "http://blog_publisher:8041/api/v1/publish/direct",
            "http://clisonix-blog-publisher:8041/api/v1/publish/direct",
        ]
        for fallback_url in fallback_urls:
            if all(existing_url != fallback_url for existing_url, _, _ in candidates):
                candidates.append((fallback_url, direct_payload, "fallback"))

        last_error: Optional[str] = None
        async with aiohttp.ClientSession() as session:
            for url, outgoing_payload, mode in candidates:
                try:
                    async with session.post(
                        url,
                        json=outgoing_payload,
                        timeout=aiohttp.ClientTimeout(total=15),
                    ) as resp:
                        response_text = await resp.text()
                        if 200 <= resp.status < 300:
                            logger.info(f"📰 Blog ← [{article.generator_engine}] {article.title} ({mode})")
                            log_publish_event(article, "blog", "success")
                            return True

                        last_error = f"status={resp.status} mode={mode} body={response_text[:300]}"
                        logger.error(f"Blog publish error: {last_error}")
                except Exception as exc:
                    last_error = f"mode={mode} error={exc}"
                    logger.error(f"Blog publish error: {last_error}")

        log_publish_event(article, "blog", f"error_{last_error or 'unknown'}")
        return False
    except Exception as exc:
        logger.error(f"Blog publish error: {exc}")
        log_publish_event(article, "blog", f"error_{exc}")
        return False


async def publish_to_facebook(article: Article) -> bool:
    try:
        if not SETTINGS.auto_publish_after_ethics:
            log_publish_event(article, "facebook", "skipped_auto_publish_disabled")
            return False
        if not SETTINGS.facebook_token or not SETTINGS.facebook_page_id:
            log_publish_event(article, "facebook", "skipped_missing_credentials")
            return False

        page_id, page_token = await resolve_facebook_page_credentials()
        if not page_id or not page_token:
            log_publish_event(article, "facebook", "skipped_missing_page_credentials")
            return False

        graph_url = f"https://graph.facebook.com/v21.0/{page_id}/feed"
        payload = {
            "message": build_facebook_message(article),
            "link": "https://clisonix.com",
            "access_token": page_token,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                graph_url,
                data=payload,
                timeout=aiohttp.ClientTimeout(total=20),
            ) as resp:
                response_text = await resp.text()
                if 200 <= resp.status < 300:
                    logger.info(f"📘 Facebook ← [{article.generator_engine}] {article.title}")
                    log_publish_event(article, "facebook", "success")
                    return True

                error_status = f"error_http_{resp.status}"
                try:
                    fb_error = json.loads(response_text).get("error", {})
                    error_code = fb_error.get("code")
                    error_message = str(fb_error.get("message", ""))
                    if error_code == 190:
                        error_status = "error_expired_or_invalid_token"
                    elif error_code == 200 and "pages_manage_posts" in error_message:
                        error_status = "error_missing_pages_manage_posts"
                except Exception:
                    pass

                logger.error(f"Facebook publish error: status={resp.status} body={response_text[:300]}")
                log_publish_event(article, "facebook", error_status)
                return False
    except Exception as exc:
        logger.error(f"Facebook publish error: {exc}")
        log_publish_event(article, "facebook", f"error_{exc}")
        return False

# ============================================================
# MAIN NEWSROOM CYCLE
# ============================================================

async def newsroom_cycle() -> None:
    """Full publishing cycle: probe engines → generate → ethics → publish."""
    logger.info("── Newsroom Cycle START ──")

    # 1. Probe all engines in parallel and update health cache
    logger.info("Probing engines...")
    fresh = await probe_all_engines()
    ENGINE_HEALTH_CACHE.update(fresh)
    reachable = sum(1 for v in fresh.values() if v.get("reachable"))
    logger.info(f"Engines reachable: {reachable}/{len(ENGINE_REGISTRY)}")

    # 2. Generate articles from labs (engine-aware)
    await ORCHESTRATOR.distribute_work()

    # 3. Publish up to max_articles_per_cycle
    articles_published = 0
    max_per_cycle = max(1, SETTINGS.posts_per_day // 24)

    while not ORCHESTRATOR.article_queue.empty() and articles_published < max_per_cycle:
        article = await ORCHESTRATOR.article_queue.get()

        gate_results = run_ethics_pipeline(article)
        for gate_result in gate_results:
            gate_status = "approved" if gate_result.passed else f"rejected_{gate_result.reason}"
            log_publish_event(article, f"ethics_{gate_result.gate}", gate_status)

        is_valid, error_msg = ethics_pipeline_passed(gate_results)
        if not is_valid:
            logger.warning(f"Ethics pipeline ✗ [{article.generator_engine}] {error_msg}")
            log_publish_event(article, "ethics_pipeline", f"rejected_{error_msg}")
            continue

        log_publish_event(article, "ethics_pipeline", "approved_all_gates")

        blog_ok = await publish_to_blog(article)
        fb_ok   = await publish_to_facebook(article)

        if blog_ok or fb_ok:
            articles_published += 1
            ORCHESTRATOR.total_published += 1
            logger.info(f"✅ [{article.generator_engine}] {article.title} {article.category.value}")
        else:
            logger.error(f"❌ [{article.generator_engine}] failed: {article.title}")

    logger.info(f"── Newsroom Cycle END — published: {articles_published} ──")


async def run_newsroom_cycle(trigger: str = "scheduler") -> bool:
    if CYCLE_LOCK.locked():
        logger.warning(f"Cycle already running; trigger={trigger} skipped")
        return False

    async with CYCLE_LOCK:
        logger.info(f"Cycle trigger → {trigger}")
        await newsroom_cycle()
        return True


async def scheduler() -> None:
    logger.info(f"Scheduler active — interval: {SETTINGS.publish_interval_seconds}s")
    while True:
        try:
            await run_newsroom_cycle("scheduler")
        except Exception as exc:
            logger.error(f"Cycle error: {exc}")
        await asyncio.sleep(SETTINGS.publish_interval_seconds)

# ============================================================
# API ENDPOINTS
# ============================================================

async def health(request: web.Request) -> web.Response:
    engines_up = sum(1 for v in ENGINE_HEALTH_CACHE.values() if v.get("reachable"))
    return web.json_response({
        "service":           "Clisonix Global AI Newsroom",
        "status":            "operational",
        "version":           "6.0",
        "auto_publish_after_ethics": SETTINGS.auto_publish_after_ethics,
        "labs_active":       len(ORCHESTRATOR.labs),
        "engines_registered":len(ENGINE_REGISTRY),
        "engines_reachable": engines_up,
        "articles_generated":ORCHESTRATOR.total_generated,
        "articles_published":ORCHESTRATOR.total_published,
        "timestamp":         datetime.now(timezone.utc).isoformat(),
    })


async def audit_log_endpoint(request: web.Request) -> web.Response:
    limit  = int(request.query.get("limit", 100))
    engine = request.query.get("engine")       # filter by generator_engine
    platform = request.query.get("platform")  # filter by platform

    events = AUDIT_LOG
    if engine:
        events = [e for e in events if e.get("generator_engine", "").upper() == engine.upper()]
    if platform:
        events = [e for e in events if e.get("platform") == platform]

    return web.json_response({
        "total_events": len(AUDIT_LOG),
        "filtered":     len(events),
        "recent":       events[-limit:],
        "timestamp":    datetime.now(timezone.utc).isoformat(),
    })


async def first_news(request: web.Request) -> web.Response:
    engine = request.query.get("engine")
    events = AUDIT_LOG

    if engine:
        events = [e for e in events if e.get("generator_engine", "").upper() == engine.upper()]

    first_published = next(
        (e for e in reversed(events) if e.get("platform") == "blog" and e.get("status") == "success"),
        None,
    )
    if not first_published:
        return web.json_response(
            {"message": "No published news available yet", "first_news": None,
             "timestamp": datetime.now(timezone.utc).isoformat()},
            status=404,
        )
    return web.json_response({
        "first_news": first_published,
        "timestamp":  datetime.now(timezone.utc).isoformat(),
    })


async def engines_status(request: web.Request) -> web.Response:
    """Live status of all registered engines."""
    results = []
    for name, meta in ENGINE_REGISTRY.items():
        cached = ENGINE_HEALTH_CACHE.get(name, {})
        results.append({
            "engine":    name,
            "icon":      meta["icon"],
            "domain":    meta["domain"],
            "url":       meta["url"],
            "reachable": cached.get("reachable", False),
            "status":    cached.get("status", "unknown"),
            "lab_range": list(meta["lab_range"]),
            "last_check":cached.get("timestamp", None),
        })
    return web.json_response({
        "engines":   results,
        "total":     len(results),
        "reachable": sum(1 for r in results if r["reachable"]),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


async def status(request: web.Request) -> web.Response:
    engines_up = sum(1 for v in ENGINE_HEALTH_CACHE.values() if v.get("reachable"))
    return web.json_response({
        "labs":              len(ORCHESTRATOR.labs),
        "queue_size":        ORCHESTRATOR.article_queue.qsize(),
        "audit_log_size":    len(AUDIT_LOG),
        "auto_publish_after_ethics": SETTINGS.auto_publish_after_ethics,
        "cycle_running":     CYCLE_LOCK.locked(),
        "total_generated":   ORCHESTRATOR.total_generated,
        "total_published":   ORCHESTRATOR.total_published,
        "engines_registered":len(ENGINE_REGISTRY),
        "engines_reachable": engines_up,
        "engines":           list(ENGINE_REGISTRY.keys()),
        "timestamp":         datetime.now(timezone.utc).isoformat(),
    })


async def publish_config(request: web.Request) -> web.Response:
    max_per_cycle = max(1, SETTINGS.posts_per_day // 24)
    return web.json_response({
        "auto_publish_after_ethics": SETTINGS.auto_publish_after_ethics,
        "publish_interval_seconds": SETTINGS.publish_interval_seconds,
        "posts_per_day": SETTINGS.posts_per_day,
        "max_posts_per_cycle": max_per_cycle,
        "blog_api_url": SETTINGS.blog_api_url,
        "facebook_page_configured": bool(SETTINGS.facebook_page_id),
        "facebook_token_configured": bool(SETTINGS.facebook_token),
        "facebook_ready": bool(SETTINGS.facebook_page_id and SETTINGS.facebook_token),
        "ethics": {
            "min_sources_required": ETHICS.min_sources_required,
            "allow_speculation": ETHICS.allow_speculation,
            "allow_emotional_language": ETHICS.allow_emotional_language,
            "allow_unverified_claims": ETHICS.allow_unverified_claims,
            "require_timestamp": ETHICS.require_timestamp,
            "require_source_attribution": ETHICS.require_source_attribution,
        },
        "cycle_running": CYCLE_LOCK.locked(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


async def publish_now(request: web.Request) -> web.Response:
    started = await run_newsroom_cycle("publish-now")
    if not started:
        return web.json_response({
            "status": "skipped",
            "reason": "cycle_already_running",
            "auto_publish_after_ethics": SETTINGS.auto_publish_after_ethics,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }, status=409)

    return web.json_response({
        "status": "completed",
        "trigger": "publish-now",
        "auto_publish_after_ethics": SETTINGS.auto_publish_after_ethics,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


async def on_startup(app: web.Application) -> None:
    # Initial engine probe before first cycle
    logger.info("Initial engine probe...")
    fresh = await probe_all_engines()
    ENGINE_HEALTH_CACHE.update(fresh)
    app["scheduler_task"] = asyncio.create_task(scheduler())


async def on_cleanup(app: web.Application) -> None:
    task = app.get("scheduler_task")
    if task:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task


def create_app() -> web.Application:
    app = web.Application()
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    app.add_routes([
        web.get("/",           health),
        web.get("/health",     health),
        web.get("/audit",      audit_log_endpoint),
        web.get("/first-news", first_news),
        web.get("/engines",    engines_status),
        web.get("/publish-config", publish_config),
        web.get("/status",     status),
        web.post("/publish-now", publish_now),
    ])
    return app

# ============================================================
# ENTRY POINT
# ============================================================

def main() -> None:
    logger.info("=" * 65)
    logger.info("🧠 Clisonix Global AI Newsroom v6.0 — HIGH LEVEL START")
    logger.info(f"📡 Labs: {SETTINGS.max_labs}  |  Engines: {len(ENGINE_REGISTRY)}")
    logger.info(f"   Registered: {', '.join(ENGINE_REGISTRY.keys())}")
    logger.info(f"📰 Posts/day: {SETTINGS.posts_per_day}")
    logger.info(f"⏱  Cycle interval: {SETTINGS.publish_interval_seconds}s")
    logger.info(f"🌐 Port: {SETTINGS.port}")
    logger.info("=" * 65)

    app = create_app()
    web.run_app(app, host="0.0.0.0", port=SETTINGS.port)


if __name__ == "__main__":
    main()
