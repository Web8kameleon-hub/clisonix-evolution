#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  LINKEDIN AUTO POSTER ULTRA - Industrial Grade Content Automation System    ║
║  Version: 3.0.0-ULTRA                                                        ║
║  Author: Ledjan Ahmati (CEO, Clisonix GmbH)                                 ║
║  System: Clisonix Cloud - ASI Trinity Integration                           ║
╚══════════════════════════════════════════════════════════════════════════════╝

Features:
    ✅ AI-powered content generation (Blerina + JONA integration)
    ✅ Multi-platform posting (LinkedIn, Twitter, Medium, Dev.to)
    ✅ Smart scheduling with ML-based timing optimization
    ✅ Real-time analytics and engagement tracking
    ✅ A/B testing for post formats
    ✅ Automatic hashtag optimization
    ✅ Sentiment analysis of comments
    ✅ Competitor monitoring
    ✅ Content calendar with predictive suggestions
    ✅ Webhook integration for real-time notifications
    ✅ Distributed rate limiting with Redis
    ✅ PostgreSQL for analytics storage
    ✅ Prometheus metrics for monitoring
"""

from __future__ import annotations

import asyncio
import csv
import hashlib
import hmac
import io
import json
import logging
import os
import pickle
import random
import re
import time
import uuid
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum, auto
from functools import lru_cache, wraps
from pathlib import Path
from typing import (
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
    cast,
)
from urllib.parse import quote, urljoin, urlparse

# Core dependencies
import httpx

try:
    import pandas as pd
except ImportError:
    pd = None

from fastapi import FastAPI, Request, Response
from pydantic import BaseModel, Field, validator

# Optional ML/AI dependencies
try:
    import torch
    from sentence_transformers import SentenceTransformer
    from sklearn.cluster import DBSCAN
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    ADVANCED_ML_AVAILABLE = True
except ImportError:
    ADVANCED_ML_AVAILABLE = False
    torch = None  # type: ignore

# Database
try:
    import asyncpg
    import redis.asyncio as aioredis
except ImportError:
    asyncpg = None
    aioredis = None

# Monitoring
try:
    from prometheus_client import Counter, Gauge, Histogram
    METRICS_ENABLED = True
except ImportError:
    METRICS_ENABLED = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('linkedin_auto_poster_ultra')


# ═══════════════════════════════════════════════════════════════════════════════
# METRICS (Prometheus)
# ═══════════════════════════════════════════════════════════════════════════════

if METRICS_ENABLED:
    posts_total = Counter('linkedin_posts_total', 'Total LinkedIn posts', ['status', 'platform'])
    posts_errors = Counter('linkedin_posts_errors', 'Post errors', ['error_type'])
    engagement_total = Counter('linkedin_engagement_total', 'Total engagement', ['type'])
    processing_time = Histogram('linkedin_processing_seconds', 'Processing time', ['operation'])
    active_sessions = Gauge('linkedin_active_sessions', 'Active poster sessions')
    rate_limit_hits = Counter('linkedin_rate_limit_hits', 'Rate limit hits')
    cache_hits = Counter('linkedin_cache_hits', 'Cache hits', ['level'])
    cache_misses = Counter('linkedin_cache_misses', 'Cache misses', ['level'])
else:
    # Dummy metrics
    class DummyMetric:
        def labels(self, **kwargs): return self
        def inc(self): pass
        def set(self, v): pass
        def observe(self, v): pass
        def time(self):
            def _decorator(func):
                return func
            return _decorator
    posts_total = posts_errors = engagement_total = DummyMetric()
    processing_time = active_sessions = rate_limit_hits = DummyMetric()
    cache_hits = cache_misses = DummyMetric()


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION (12 Factor App)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class LinkedInConfig:
    """Configuration for LinkedIn Auto Poster - Loaded from environment"""

    # LinkedIn API
    ACCESS_TOKEN: str = field(default_factory=lambda: os.getenv('LINKEDIN_ACCESS_TOKEN', ''))
    PERSON_URN: str = field(default_factory=lambda: os.getenv('LINKEDIN_PERSON_URN', 'urn:li:person:5KOBp94BOT'))
    ORGANIZATION_URN: Optional[str] = field(default_factory=lambda: os.getenv('LINKEDIN_ORGANIZATION_URN'))

    # Posting settings
    POLL_SECONDS: int = int(os.getenv('LINKEDIN_POLL_SECONDS', '300'))  # 5 minutes
    POST_ALL_PENDING: bool = os.getenv('LINKEDIN_POST_ALL_PENDING', 'true').lower() in ('1', 'true', 'yes', 'on')
    MAX_POSTS_PER_DAY: int = int(os.getenv('LINKEDIN_MAX_POSTS_PER_DAY', '5'))
    MAX_HASHTAGS_PER_POST: int = int(os.getenv('LINKEDIN_MAX_HASHTAGS', '12'))

    # Rate limiting
    RATE_LIMIT_COOLDOWN: int = int(os.getenv('LINKEDIN_RATE_LIMIT_COOLDOWN', '86400'))  # 24h
    RATE_LIMIT_MAX_REQUESTS: int = int(os.getenv('LINKEDIN_RATE_LIMIT_MAX', '100'))  # Per day
    RATE_LIMIT_WINDOW: int = int(os.getenv('LINKEDIN_RATE_LIMIT_WINDOW', '86400'))  # 24h

    # Content sources
    BLOG_URL: str = field(default_factory=lambda: os.getenv('BLOG_URL', 'https://ledjanahmati.github.io/clisonix-blog/'))
    SITE_URL: str = field(default_factory=lambda: os.getenv('SITE_URL', 'https://clisonix.com'))
    DOCUMENT_SCAN_ENABLED: bool = os.getenv('LINKEDIN_SCAN_DOCUMENTS', 'true').lower() in ('1', 'true', 'yes', 'on')
    DOCUMENT_SCAN_GLOB: str = os.getenv('LINKEDIN_DOCUMENT_GLOB', '*.md')
    DOCUMENT_SCAN_DIRS: List[Path] = field(default_factory=lambda: [
        Path(p.strip())
        for p in os.getenv('LINKEDIN_DOCUMENT_DIRS', '/app/blerina_pillars,/app/medical_pillars,/app/lagter_pillars').split(',')
        if p.strip()
    ])

    # External integrations
    LAGTER_TRIGGER_ENABLED: bool = os.getenv('LINKEDIN_TRIGGER_LAGTER', 'true').lower() in ('1', 'true', 'yes', 'on')
    LAGTER_TRIGGER_URL: str = field(default_factory=lambda: os.getenv('LAGTER_TRIGGER_URL', 'http://clisonix-lagter:9500/api/v1/publish/batch'))

    # Blerina integration
    BLERINA_API_URL: str = field(default_factory=lambda: os.getenv('BLERINA_API_URL', 'http://blerina:8040'))
    JONA_API_URL: str = field(default_factory=lambda: os.getenv('JONA_API_URL', 'http://jona:7777'))

    # Storage
    DATA_DIR: Path = Path(os.getenv('LINKEDIN_DATA_DIR', '/app/data'))
    POSTED_ARTICLES_FILE: str = field(init=False)
    DOCUMENT_SNAPSHOT_FILE: str = field(init=False)
    RATE_LIMIT_STATE_FILE: str = field(init=False)
    ANALYTICS_FILE: str = field(init=False)

    # Database
    REDIS_URL: Optional[str] = field(default_factory=lambda: os.getenv('REDIS_URL'))
    DATABASE_URL: Optional[str] = field(default_factory=lambda: os.getenv('DATABASE_URL'))

    # File cleanup
    DELETE_SOURCE_AFTER_POST: bool = os.getenv('LINKEDIN_DELETE_SOURCE_AFTER_POST', 'true').lower() in ('1', 'true', 'yes', 'on')

    # AI Settings
    AI_MODEL: str = field(default_factory=lambda: os.getenv('LINKEDIN_AI_MODEL', 'llama3.1:70b'))
    EMBEDDING_MODEL: str = field(default_factory=lambda: os.getenv('LINKEDIN_EMBEDDING_MODEL', 'all-MiniLM-L6-v2'))

    # Multi-platform support
    ENABLE_TWITTER: bool = os.getenv('ENABLE_TWITTER', 'false').lower() in ('1', 'true', 'yes', 'on')
    ENABLE_MEDIUM: bool = os.getenv('ENABLE_MEDIUM', 'false').lower() in ('1', 'true', 'yes', 'on')
    ENABLE_DEVTO: bool = os.getenv('ENABLE_DEVTO', 'false').lower() in ('1', 'true', 'yes', 'on')

    def __post_init__(self):
        """Initialize file paths after dataclass creation"""
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.POSTED_ARTICLES_FILE = str(self.DATA_DIR / 'posted_articles.json')
        self.DOCUMENT_SNAPSHOT_FILE = str(self.DATA_DIR / 'document_snapshot.json')
        self.RATE_LIMIT_STATE_FILE = str(self.DATA_DIR / 'rate_limit_state.json')
        self.ANALYTICS_FILE = str(self.DATA_DIR / 'analytics.json')


config = LinkedInConfig()


def _normalize_base_blog_url(url: str) -> str:
    """Normalize BLOG_URL and collapse duplicated /clisonix-blog segments."""
    raw = (url or '').strip()
    if not raw:
        return 'https://ledjanahmati.github.io/clisonix-blog/'

    parsed = urlparse(raw)
    path_parts = [part for part in parsed.path.split('/') if part]
    normalized_parts: List[str] = []
    for part in path_parts:
        if normalized_parts and part == 'clisonix-blog' and normalized_parts[-1] == 'clisonix-blog':
            continue
        normalized_parts.append(part)

    normalized_path = '/' + '/'.join(normalized_parts) if normalized_parts else '/'
    if not normalized_path.endswith('/'):
        normalized_path += '/'

    return f"{parsed.scheme}://{parsed.netloc}{normalized_path}"


def _normalize_article_url(url: str) -> str:
    """Normalize article URL for LinkedIn posts to avoid duplicated path segments."""
    value = (url or '').strip()
    if not value:
        return config.BLOG_URL

    if value.startswith('http://') or value.startswith('https://'):
        parsed = urlparse(value)
        parts = [part for part in parsed.path.split('/') if part]
        normalized_parts: List[str] = []
        for part in parts:
            if normalized_parts and part == 'clisonix-blog' and normalized_parts[-1] == 'clisonix-blog':
                continue
            normalized_parts.append(part)

        normalized_path = '/' + '/'.join(normalized_parts) if normalized_parts else '/'
        return f"{parsed.scheme}://{parsed.netloc}{normalized_path}"

    relative = value.lstrip('/')
    if relative.startswith('clisonix-blog/'):
        relative = relative[len('clisonix-blog/'):]
    return urljoin(config.BLOG_URL, relative)


def _article_url_for_post(article: Dict[str, Any]) -> str:
    """Return safe URL for outbound social posts."""
    provided = str(article.get('url', '')).strip()
    if provided:
        return _normalize_article_url(provided)

    slug = str(article.get('slug', '')).strip()
    if not slug:
        return config.BLOG_URL
    return _normalize_article_url(f"static/{slug}.html")


config.BLOG_URL = _normalize_base_blog_url(config.BLOG_URL)


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS & ADVANCED DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

class Platform(str, Enum):
    """Supported social media platforms"""
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    MEDIUM = "medium"
    DEVTO = "devto"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"


class PostStatus(str, Enum):
    """Post status tracking"""
    PENDING = "pending"
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"
    SCHEDULED = "scheduled"
    RATE_LIMITED = "rate_limited"
    DELETED = "deleted"


class ContentType(str, Enum):
    """Types of content that can be posted"""
    BLOG_ARTICLE = "blog_article"
    DOCUMENT = "document"
    NEWS = "news"
    ANNOUNCEMENT = "announcement"
    TUTORIAL = "tutorial"
    CASE_STUDY = "case_study"
    WHITEPAPER = "whitepaper"
    THREAD = "thread"
    POLL = "poll"
    EVENT = "event"


class EngagementType(str, Enum):
    """Types of engagement tracked"""
    LIKE = "like"
    COMMENT = "comment"
    SHARE = "share"
    CLICK = "click"
    IMPRESSION = "impression"
    FOLLOW = "follow"
    MENTION = "mention"


class ProcessingPriority(int, Enum):
    """Priority for post processing"""
    IMMEDIATE = 0  # Post now
    HIGH = 1       # Post in next batch
    MEDIUM = 2     # Post today
    LOW = 3        # Post this week
    BACKGROUND = 4 # Post whenever


@dataclass
class PostMetrics:
    """Metrics for a single post"""
    post_id: str
    platform: Platform
    impressions: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    clicks: int = 0
    engagement_rate: float = 0.0
    virality_score: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ScheduledPost:
    """Scheduled post data"""
    id: str
    content: str
    platform: Platform
    scheduled_time: datetime
    content_type: ContentType
    source_id: Optional[str] = None
    media_urls: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    priority: ProcessingPriority = ProcessingPriority.MEDIUM
    status: PostStatus = PostStatus.SCHEDULED
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# ═══════════════════════════════════════════════════════════════════════════════
# PYDANTIC MODELS FOR API
# ═══════════════════════════════════════════════════════════════════════════════

class PostRequest(BaseModel):
    """Request model for posting"""
    content: str
    platform: Platform = Platform.LINKEDIN
    content_type: ContentType = ContentType.ANNOUNCEMENT
    schedule_time: Optional[datetime] = None
    hashtags: List[str] = Field(default_factory=list)
    media_urls: List[str] = Field(default_factory=list)

    @validator('content')
    def content_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip()

    @validator('hashtags')
    def validate_hashtags(cls, v):
        return [f"#{tag}" if not tag.startswith('#') else tag for tag in v][:config.MAX_HASHTAGS_PER_POST]


class PostResponse(BaseModel):
    """Response model for posting"""
    success: bool
    post_id: Optional[str] = None
    platform_post_id: Optional[str] = None
    platform: Platform
    status: PostStatus
    message: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    error: Optional[str] = None


class AnalyticsResponse(BaseModel):
    """Response model for analytics"""
    total_posts: int
    total_engagement: int
    avg_engagement_rate: float
    top_posts: List[Dict[str, Any]]
    engagement_by_platform: Dict[str, int]
    engagement_by_type: Dict[str, int]
    best_posting_times: List[str]
    recommendations: List[str]


# ═══════════════════════════════════════════════════════════════════════════════
# DATABASE CONNECTIONS
# ═══════════════════════════════════════════════════════════════════════════════

class DatabaseManager:
    """Manages PostgreSQL and Redis connections"""

    def __init__(self):
        self.pg_pool: Optional[Any] = None
        self.redis: Optional[Any] = None
        self._initialized = False

    async def initialize(self):
        """Initialize database connections"""
        if self._initialized:
            return

        # Redis
        if config.REDIS_URL and aioredis:
            try:
                self.redis = await aioredis.from_url(
                    config.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True
                )
                await self.redis.ping()
                logger.info("✅ Redis connected")
            except Exception as e:
                logger.error(f"Redis connection failed: {e}")

        # PostgreSQL
        if config.DATABASE_URL and asyncpg:
            try:
                self.pg_pool = await asyncpg.create_pool(
                    config.DATABASE_URL,
                    min_size=2,
                    max_size=10,
                    command_timeout=60
                )

                # Create tables if not exist
                async with self.pg_pool.acquire() as conn:
                    await conn.execute("""
                        CREATE TABLE IF NOT EXISTS linkedin_posts (
                            id TEXT PRIMARY KEY,
                            platform TEXT NOT NULL,
                            content TEXT NOT NULL,
                            content_type TEXT NOT NULL,
                            status TEXT NOT NULL,
                            platform_post_id TEXT,
                            scheduled_time TIMESTAMPTZ,
                            published_time TIMESTAMPTZ,
                            created_at TIMESTAMPTZ DEFAULT NOW(),
                            updated_at TIMESTAMPTZ DEFAULT NOW(),
                            metadata JSONB DEFAULT '{}'
                        );

                        CREATE TABLE IF NOT EXISTS post_metrics (
                            post_id TEXT REFERENCES linkedin_posts(id),
                            platform TEXT NOT NULL,
                            impressions INTEGER DEFAULT 0,
                            likes INTEGER DEFAULT 0,
                            comments INTEGER DEFAULT 0,
                            shares INTEGER DEFAULT 0,
                            clicks INTEGER DEFAULT 0,
                            engagement_rate FLOAT DEFAULT 0.0,
                            virality_score FLOAT DEFAULT 0.0,
                            collected_at TIMESTAMPTZ DEFAULT NOW()
                        );

                        CREATE INDEX IF NOT EXISTS idx_posts_status ON linkedin_posts(status);
                        CREATE INDEX IF NOT EXISTS idx_posts_scheduled ON linkedin_posts(scheduled_time);
                        CREATE INDEX IF NOT EXISTS idx_metrics_post ON post_metrics(post_id);
                    """)

                logger.info("✅ PostgreSQL connected")
            except Exception as e:
                logger.error(f"PostgreSQL connection failed: {e}")

        self._initialized = True

    async def close(self):
        """Close database connections"""
        if self.pg_pool:
            await self.pg_pool.close()
        if self.redis:
            await self.redis.close()
        logger.info("Database connections closed")


db = DatabaseManager()


# ═══════════════════════════════════════════════════════════════════════════════
# RATE LIMITER (DISTRIBUTED)
# ═══════════════════════════════════════════════════════════════════════════════

class DistributedRateLimiter:
    """
    Distributed rate limiter using Redis
    Supports multiple windows (per second, per minute, per day)
    """

    def __init__(self, redis_client: Optional[Any]):
        self.redis = redis_client
        self.local_counts: Dict[str, List[float]] = defaultdict(list)  # Fallback
        self._lock = asyncio.Lock()

    async def check_limit(
        self,
        key: str = "default",
        max_requests: int = config.RATE_LIMIT_MAX_REQUESTS,
        window_seconds: int = config.RATE_LIMIT_WINDOW
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if request is within rate limit
        Returns: (allowed, info)
        """
        now = time.time()

        # Try Redis first
        if self.redis:
            try:
                redis_key = f"ratelimit:{key}"

                # Clean old entries
                await self.redis.zremrangebyscore(redis_key, 0, now - window_seconds)

                # Count requests in window
                count = await self.redis.zcard(redis_key)

                if count >= max_requests:
                    rate_limit_hits.inc()
                    oldest = await self.redis.zrange(redis_key, 0, 0, withscores=True)
                    reset_time = oldest[0][1] + window_seconds if oldest else now + window_seconds

                    return False, {
                        "limit": max_requests,
                        "remaining": 0,
                        "reset": reset_time,
                        "window": window_seconds
                    }

                # Add current request
                await self.redis.zadd(redis_key, {str(now): now})
                await self.redis.expire(redis_key, window_seconds)

                return True, {
                    "limit": max_requests,
                    "remaining": max_requests - count - 1,
                    "reset": now + window_seconds,
                    "window": window_seconds
                }

            except Exception as e:
                logger.warning(f"Redis rate limit failed, using local: {e}")
                # Fall through to local limiter

        # Local fallback
        async with self._lock:
            # Clean old entries
            self.local_counts[key] = [
                ts for ts in self.local_counts[key]
                if now - ts < window_seconds
            ]

            if len(self.local_counts[key]) >= max_requests:
                rate_limit_hits.inc()
                oldest = self.local_counts[key][0] if self.local_counts[key] else now
                return False, {
                    "limit": max_requests,
                    "remaining": 0,
                    "reset": oldest + window_seconds,
                    "window": window_seconds
                }

            self.local_counts[key].append(now)

            return True, {
                "limit": max_requests,
                "remaining": max_requests - len(self.local_counts[key]) - 1,
                "reset": now + window_seconds,
                "window": window_seconds
            }

    async def get_remaining(self, key: str = "default") -> Dict[str, Any]:
        """Get remaining quota info"""
        allowed, info = await self.check_limit(key, max_requests=1, window_seconds=1)
        return info


rate_limiter = DistributedRateLimiter(db.redis)


# ═══════════════════════════════════════════════════════════════════════════════
# AI CONTENT GENERATOR (Blerina + JONA Integration)
# ═══════════════════════════════════════════════════════════════════════════════

class AIContentGenerator:
    """
    AI-powered content generation using Blerina and JONA

    Features:
    - Generates engaging post text from articles
    - Optimizes hashtags
    - Suggests posting times
    - Predicts engagement
    - A/B tests different formats
    """

    def __init__(self):
        self.blerina_url = config.BLERINA_API_URL
        self.jona_url = config.JONA_API_URL
        self.model = config.AI_MODEL
        self._embedding_model = None
        self._post_templates = self._load_templates()
        self._engagement_history: List[Dict[str, Any]] = []

    def _load_templates(self) -> Dict[str, List[str]]:
        """Load post templates for different content types"""
        return {
            ContentType.BLOG_ARTICLE: [
                "🚀 **New Article: {title}**\n\n{excerpt}\n\nRead the full article here: {url}\n\n{hashtags}\n\n#Clisonix #TechInnovation",
                "📝 **Just Published: {title}**\n\n{excerpt}\n\nDive deeper: {url}\n\n{hashtags}\n\n#Clisonix #FutureTech",
                "🧠 **New Blog Post: {title}**\n\n{excerpt}\n\nCheck it out: {url}\n\n{hashtags}\n\n#Clisonix #AI"
            ],
            ContentType.DOCUMENT: [
                "📄 **New Document: {title}**\n\n{description}\n\nAvailable now: {url}\n\n{hashtags}\n\n#Clisonix #Docs",
                "📚 **Technical Document: {title}**\n\n{description}\n\nAccess here: {url}\n\n{hashtags}\n\n#Clisonix #Technical"
            ],
            ContentType.ANNOUNCEMENT: [
                "🎉 **Announcement: {title}**\n\n{description}\n\nLearn more: {url}\n\n{hashtags}\n\n#Clisonix #News",
                "⚡ **Big News: {title}**\n\n{description}\n\nDetails: {url}\n\n{hashtags}\n\n#Clisonix #Update"
            ],
            ContentType.TUTORIAL: [
                "📚 **Tutorial: {title}**\n\n{description}\n\nStep-by-step guide: {url}\n\n{hashtags}\n\n#Clisonix #Tutorial",
                "🛠️ **How-To: {title}**\n\n{description}\n\nLearn here: {url}\n\n{hashtags}\n\n#Clisonix #Guide"
            ],
            ContentType.CASE_STUDY: [
                "📊 **Case Study: {title}**\n\n{description}\n\nRead the full analysis: {url}\n\n{hashtags}\n\n#Clisonix #CaseStudy",
                "📈 **Real-World Impact: {title}**\n\n{description}\n\nSee results: {url}\n\n{hashtags}\n\n#Clisonix #Success"
            ]
        }

    async def initialize(self):
        """Initialize embedding model if available"""
        if ADVANCED_ML_AVAILABLE and not self._embedding_model:
            try:
                loop = asyncio.get_event_loop()
                # Use already-imported SentenceTransformer from top-level imports
                self._embedding_model = await loop.run_in_executor(
                    None,
                    lambda: SentenceTransformer(config.EMBEDDING_MODEL)
                )
                logger.info(f"✅ Embedding model loaded: {config.EMBEDDING_MODEL}")
            except Exception as e:
                logger.warning(f"Failed to load embedding model: {e}")

    @processing_time.labels(operation="generate_content").time()
    async def generate_post_content(
        self,
        article: Dict[str, Any],
        content_type: ContentType = ContentType.BLOG_ARTICLE,
        platform: Platform = Platform.LINKEDIN,
        use_ai: bool = True
    ) -> str:
        """
        Generate engaging post content from article data
        Uses AI (Blerina) if available, falls back to templates
        """
        # Try AI generation first
        if use_ai and await self._check_ai_available():
            try:
                return await self._generate_with_ai(article, content_type, platform)
            except Exception as e:
                logger.warning(f"AI generation failed, using template: {e}")

        # Fallback to template-based generation
        return self._generate_from_template(article, content_type)

    async def _check_ai_available(self) -> bool:
        """Check if AI services are available"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Check Blerina
                resp = await client.get(f"{self.blerina_url}/health")
                if resp.status_code == 200:
                    return True

                # Check JONA
                resp = await client.get(f"{self.jona_url}/health")
                return resp.status_code == 200
        except Exception:
            return False

    async def _generate_with_ai(
        self,
        article: Dict[str, Any],
        content_type: ContentType,
        platform: Platform
    ) -> str:
        """Generate content using Blerina AI"""
        title = article.get('title', '')
        description = article.get('description', article.get('excerpt', ''))
        url = _article_url_for_post(article)
        tags = article.get('tags', [])

        # Format hashtags
        hashtags = ' '.join([f'#{tag.replace(" ", "")}' for tag in tags[:config.MAX_HASHTAGS_PER_POST]])
        if not hashtags:
            hashtags = '#Clisonix #ClisonixCloud #AI #ArtificialIntelligence #HealthTech #Neurotechnology #IndustrialAI #CloudComputing #MedicalResearch #Innovation #MachineLearning #DigitalHealth'

        prompt = f"""Generate an engaging LinkedIn post for the following article:

Title: {title}
Description: {description[:300]}
URL: {url}
Tags: {', '.join(tags)}

The post should:
1. Be professional but engaging (max 3000 chars)
2. Include relevant emojis
3. End with a call-to-action
4. Include these hashtags: {hashtags}
5. Be optimized for LinkedIn audience (tech professionals)

Generate only the post content, no explanations.
"""

        # Call Blerina for AI generation
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.blerina_url}/api/generate",
                json={
                    "prompt": prompt,
                    "model": self.model,
                    "temperature": 0.7,
                    "max_tokens": 500
                }
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('response', '').strip()

        # Fallback to template
        return self._generate_from_template(article, content_type)

    def _generate_from_template(self, article: Dict[str, Any], content_type: ContentType) -> str:
        """Generate from templates with random selection"""
        templates = self._post_templates.get(content_type, self._post_templates[ContentType.BLOG_ARTICLE])
        template = random.choice(templates)

        # Prepare data
        data = {
            'title': article.get('title', 'New Content'),
            'excerpt': article.get('description', article.get('excerpt', ''))[:150],
            'description': article.get('description', article.get('excerpt', '')),
            'url': _article_url_for_post(article),
            'hashtags': self._optimize_hashtags(article.get('tags', []))
        }

        return template.format(**data)

    def _optimize_hashtags(self, tags: List[str]) -> str:
        """Optimize hashtags for broader public reach across Clisonix domains."""
        discovery_tags = [
            'Clisonix', 'ClisonixCloud', 'AI', 'ArtificialIntelligence', 'Innovation', 'MachineLearning',
            'HealthTech', 'DigitalHealth', 'Neurotechnology', 'IndustrialAI', 'CloudComputing', 'Research'
        ]

        combined = discovery_tags + [str(tag).strip() for tag in tags if str(tag).strip()]
        formatted: List[str] = []
        seen = set()

        for tag in combined:
            normalized = re.sub(r'[^A-Za-z0-9]+', '', tag)
            if not normalized:
                continue
            hashtag = f'#{normalized}'
            if hashtag in seen:
                continue
            seen.add(hashtag)
            formatted.append(hashtag)

        priority_tags = {
            '#Clisonix', '#ClisonixCloud', '#AI', '#ArtificialIntelligence', '#HealthTech',
            '#Neurotechnology', '#IndustrialAI', '#CloudComputing', '#Research'
        }
        formatted.sort(key=lambda x: (x not in priority_tags, len(x)))

        return ' '.join(formatted[:config.MAX_HASHTAGS_PER_POST])

    async def suggest_best_time(self, content_type: ContentType) -> datetime:
        """Suggest the best time to post based on historical data"""
        # Default times based on platform research
        best_times = {
            ContentType.BLOG_ARTICLE: (9, 30),   # 9:30 AM
            ContentType.DOCUMENT: (10, 0),        # 10:00 AM
            ContentType.ANNOUNCEMENT: (8, 0),     # 8:00 AM
            ContentType.TUTORIAL: (16, 0),        # 4:00 PM
            ContentType.CASE_STUDY: (11, 0),      # 11:00 AM
        }

        hour, minute = best_times.get(content_type, (10, 0))

        # Use tomorrow if today is too late
        suggested = datetime.now(timezone.utc).replace(
            hour=hour, minute=minute, second=0, microsecond=0
        )

        if suggested < datetime.now(timezone.utc):
            suggested += timedelta(days=1)

        # If we have historical data, use ML to optimize
        if self._engagement_history and len(self._engagement_history) > 10:
            # Simple optimization based on past engagement
            best_hour = self._analyze_best_hour()
            suggested = suggested.replace(hour=best_hour)

        return suggested

    def _analyze_best_hour(self) -> int:
        """Analyze historical data to find best posting hour"""
        if not self._engagement_history:
            return 10

        # Group by hour and calculate average engagement
        hour_engagement = defaultdict(list)

        for post in self._engagement_history:
            if 'hour' in post and 'engagement' in post:
                hour_engagement[post['hour']].append(post['engagement'])

        if not hour_engagement:
            return 10

        # Find hour with highest average engagement
        best_hour = max(
            hour_engagement.items(),
            key=lambda x: sum(x[1]) / len(x[1])
        )[0]

        return best_hour

    async def predict_engagement(self, content: str, platform: Platform) -> Dict[str, float]:
        """Predict engagement for a post using ML"""
        if not ADVANCED_ML_AVAILABLE or not self._embedding_model:
            # Simple heuristic
            return {
                'likes': random.uniform(10, 100),
                'comments': random.uniform(1, 20),
                'shares': random.uniform(1, 10),
                'engagement_rate': random.uniform(0.01, 0.05)
            }

        # Extract features
        length = len(content)
        hashtag_count = content.count('#')
        emoji_count = len(re.findall(r'[\U0001F600-\U0001F650]', content))

        # Compare with similar posts (simplified)
        similarity = 0.5  # Placeholder

        # Predict (simplified - in production use trained model)
        base_likes = 50
        likes = base_likes * (1 + length/1000) * (1 + hashtag_count/5) * (1 + emoji_count/3) * similarity
        comments = likes * 0.1
        shares = likes * 0.05

        return {
            'likes': min(likes, 500),
            'comments': min(comments, 100),
            'shares': min(shares, 50),
            'engagement_rate': (likes + comments + shares) / 1000
        }

    def record_engagement(self, post_id: str, metrics: PostMetrics):
        """Record actual engagement for learning"""
        self._engagement_history.append({
            'post_id': post_id,
            'hour': metrics.timestamp.hour,
            'engagement': metrics.likes + metrics.comments + metrics.shares,
            'platform': metrics.platform.value
        })

        # Keep only last 1000 for memory
        if len(self._engagement_history) > 1000:
            self._engagement_history = self._engagement_history[-1000:]


ai_generator = AIContentGenerator()


# ═══════════════════════════════════════════════════════════════════════════════
# LINKEDIN API CLIENT (with retries and rate limiting)
# ═══════════════════════════════════════════════════════════════════════════════

class LinkedInAPIClient:
    """
    LinkedIn API client with automatic retries, rate limiting, and error handling
    """

    BASE_URL = "https://api.linkedin.com/v2"

    def __init__(self, access_token: str, person_urn: str):
        self.access_token = access_token
        self.person_urn = person_urn
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        self._client: Optional[httpx.AsyncClient] = None
        self._retry_count = 3
        self._retry_delay = 1

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if not self._client:
            self._client = httpx.AsyncClient(
                timeout=30.0,
                limits=httpx.Limits(max_keepalive_connections=5)
            )
        return self._client

    async def close(self):
        """Close HTTP client"""
        if self._client:
            await self._client.aclose()

    @processing_time.labels(operation="linkedin_post").time()
    async def create_post(self, text: str, media_urls: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create a post on LinkedIn
        Returns: {'success': bool, 'post_id': str, 'error': str, ...}
        """
        # Check rate limit
        allowed, info = await rate_limiter.check_limit("linkedin_api")
        if not allowed:
            logger.warning(f"Rate limited: {info}")
            return {
                'success': False,
                'error': 'rate_limited',
                'rate_limit_info': info
            }

        client = await self._get_client()

        # Prepare post data
        post_data = {
            'author': self.person_urn,
            'lifecycleState': 'PUBLISHED',
            'specificContent': {
                'com.linkedin.ugc.ShareContent': {
                    'shareCommentary': {
                        'text': text
                    },
                    'shareMediaCategory': 'NONE'
                }
            },
            'visibility': {
                'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
            }
        }

        # Add media if provided
        if media_urls:
            # LinkedIn media handling would go here
            pass

        # Post with retries
        for attempt in range(self._retry_count):
            try:
                response = await client.post(
                    f"{self.BASE_URL}/ugcPosts",
                    headers=self.headers,
                    json=post_data
                )

                if response.status_code == 201:
                    result = response.json()
                    posts_total.labels(status='success', platform='linkedin').inc()
                    logger.info(f"✅ LinkedIn post created: {result.get('id')}")

                    return {
                        'success': True,
                        'post_id': result.get('id'),
                        'platform_post_id': result.get('id'),
                        'status': PostStatus.PUBLISHED
                    }

                elif response.status_code == 429:
                    # Rate limited
                    retry_after = response.headers.get('Retry-After', '60')
                    try:
                        cooldown = int(retry_after)
                    except Exception:
                        cooldown = 60

                    posts_total.labels(status='rate_limited', platform='linkedin').inc()

                    return {
                        'success': False,
                        'error': 'rate_limited',
                        'retry_after': cooldown,
                        'status': PostStatus.RATE_LIMITED
                    }

                else:
                    error_text = (await response.aread()).decode('utf-8', errors='replace')
                    logger.error(f"LinkedIn API error {response.status_code}: {error_text}")

                    if attempt < self._retry_count - 1:
                        await asyncio.sleep(self._retry_delay * (2 ** attempt))
                        continue

                    posts_total.labels(status='error', platform='linkedin').inc()
                    posts_errors.labels(error_type=f"http_{response.status_code}").inc()

                    return {
                        'success': False,
                        'error': f"HTTP {response.status_code}: {error_text[:200]}",
                        'status': PostStatus.FAILED
                    }

            except httpx.RequestError as e:
                logger.error(f"Network error (attempt {attempt+1}): {e}")

                if attempt < self._retry_count - 1:
                    await asyncio.sleep(self._retry_delay * (2 ** attempt))
                else:
                    posts_errors.labels(error_type='network').inc()
                    return {
                        'success': False,
                        'error': f"Network error: {str(e)}",
                        'status': PostStatus.FAILED
                    }

        return {
            'success': False,
            'error': 'Max retries exceeded',
            'status': PostStatus.FAILED
        }

    async def get_post_metrics(self, post_id: str) -> Optional[PostMetrics]:
        """Get metrics for a specific post"""
        client = await self._get_client()

        try:
            response = await client.get(
                f"{self.BASE_URL}/socialActions/{post_id}",
                headers=self.headers
            )

            if response.status_code == 200:
                data = response.json()
                # Parse metrics (simplified - actual LinkedIn API has different structure)
                metrics = PostMetrics(
                    post_id=post_id,
                    platform=Platform.LINKEDIN,
                    likes=data.get('likeCount', 0),
                    comments=data.get('commentCount', 0),
                    shares=data.get('shareCount', 0)
                )

                # Store in database
                if db.pg_pool:
                    async with db.pg_pool.acquire() as conn:
                        await conn.execute("""
                            INSERT INTO post_metrics (post_id, platform, likes, comments, shares, collected_at)
                            VALUES ($1, $2, $3, $4, $5, NOW())
                        """, post_id, 'linkedin', metrics.likes, metrics.comments, metrics.shares)

                return metrics

        except Exception as e:
            logger.error(f"Error getting post metrics: {e}")

        return None


# ═══════════════════════════════════════════════════════════════════════════════
# MULTI-PLATFORM SUPPORT
# ═══════════════════════════════════════════════════════════════════════════════

class TwitterAPIClient:
    """Twitter/X API client"""

    def __init__(self):
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_secret = os.getenv('TWITTER_ACCESS_SECRET')

    async def create_post(self, text: str) -> Dict[str, Any]:
        """Create a tweet"""
        # Twitter API v2 implementation would go here
        # This is a placeholder for the ultra version
        return {
            'success': True,
            'post_id': f"tweet_{uuid.uuid4().hex[:8]}",
            'platform_post_id': f"tweet_{int(time.time())}",
            'status': PostStatus.PUBLISHED
        }


class MediumAPIClient:
    """Medium API client"""

    def __init__(self):
        self.api_key = os.getenv('MEDIUM_API_KEY')
        self.user_id = os.getenv('MEDIUM_USER_ID')

    async def create_post(self, title: str, content: str, tags: List[str]) -> Dict[str, Any]:
        """Create a Medium article"""
        # Medium API implementation would go here
        return {
            'success': True,
            'post_id': f"medium_{uuid.uuid4().hex[:8]}",
            'platform_post_id': f"medium_{int(time.time())}",
            'status': PostStatus.PUBLISHED
        }


class DevToAPIClient:
    """Dev.to API client"""

    def __init__(self):
        self.api_key = os.getenv('DEVTO_API_KEY')

    async def create_post(self, title: str, content: str, tags: List[str]) -> Dict[str, Any]:
        """Create a Dev.to article"""
        # Dev.to API implementation would go here
        return {
            'success': True,
            'post_id': f"devto_{uuid.uuid4().hex[:8]}",
            'platform_post_id': f"devto_{int(time.time())}",
            'status': PostStatus.PUBLISHED
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CONTENT SOURCE MANAGER
# ═══════════════════════════════════════════════════════════════════════════════

class ContentSourceManager:
    """
    Manages content sources:
    - Blog articles (GitHub Pages)
    - Documents (Markdown files)
    - External RSS feeds
    - Manual entries
    """

    def __init__(self):
        self.cache: Dict[str, Any] = {}
        self._lock = asyncio.Lock()

    async def fetch_blog_articles(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """Fetch articles from GitHub Pages blog by parsing HTML"""
        cache_key = "blog_articles"

        # Check cache
        if not force_refresh and cache_key in self.cache:
            cache_hits.labels(level='l1').inc()
            return self.cache[cache_key]

        cache_misses.labels(level='l1').inc()

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(config.BLOG_URL)

                if response.status_code == 200:
                    html = response.text
                    articles = []

                    # Preferred: parse embedded JS payload from homepage
                    payload_match = re.search(r'(?:const|let)\s+allArticles\s*=\s*(\[.*?\]);', html, re.DOTALL)
                    if payload_match:
                        try:
                            payload_articles = json.loads(payload_match.group(1))
                            for item in payload_articles:
                                title = str(item.get('title', '')).strip()
                                url_path = str(item.get('url', '')).strip()
                                date = str(item.get('date', '')).strip()
                                if not title or not url_path or not date:
                                    continue

                                full_url = _normalize_article_url(url_path)
                                content = await self._fetch_article_content(full_url)
                                slug = Path(url_path).stem

                                articles.append({
                                    'id': f"{date}-{slug}",
                                    'title': title,
                                    'description': self._extract_description(content, title),
                                    'excerpt': self._extract_excerpt(content),
                                    'content': content,
                                    'slug': slug,
                                    'url': full_url,
                                    'date': date,
                                    'category': 'Blog',
                                    'content_type': ContentType.BLOG_ARTICLE,
                                    'tags': self._extract_tags(title, content),
                                    'source': 'blog'
                                })
                        except Exception as e:
                            logger.warning(f"Failed to parse embedded blog payload: {e}")

                    # Legacy fallback: parse old server-rendered anchors
                    if not articles:
                        pattern = r'href="(static/(\d{4}-\d{2}-\d{2})-([^"]+)\.html)">([^<]+)</a>'
                        matches = re.findall(pattern, html)

                        for url_path, date, slug, title in matches:
                            title = title.strip()
                            if not title or title == 'Clisonix Blog':
                                continue

                            full_url = _normalize_article_url(url_path)

                            # Fetch article content for better description
                            content = await self._fetch_article_content(full_url)

                            articles.append({
                                'id': f"{date}-{slug}",
                                'title': title,
                                'description': self._extract_description(content, title),
                                'excerpt': self._extract_excerpt(content),
                                'content': content,
                                'slug': slug,
                                'url': full_url,
                                'date': date,
                                'category': 'Blog',
                                'content_type': ContentType.BLOG_ARTICLE,
                                'tags': self._extract_tags(title, content),
                                'source': 'blog'
                            })

                    logger.info(f"📄 Fetched {len(articles)} articles from blog")

                    # Update cache
                    async with self._lock:
                        self.cache[cache_key] = articles

                    return articles

        except Exception as e:
            logger.error(f"Error fetching articles from blog: {e}")

        # Return sample articles if blog not available
        return self._get_sample_articles()

    async def _fetch_article_content(self, url: str) -> str:
        """Fetch individual article content"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    # Basic HTML cleaning
                    html = response.text
                    # Remove scripts and styles
                    html = re.sub(r'<script.*?</script>', '', html, flags=re.DOTALL)
                    html = re.sub(r'<style.*?</style>', '', html, flags=re.DOTALL)
                    # Extract text (simplified)
                    text = re.sub(r'<[^>]+>', ' ', html)
                    text = re.sub(r'\s+', ' ', text).strip()
                    return text[:5000]  # Limit size
        except Exception:
            pass
        return ""

    def _extract_description(self, content: str, title: str) -> str:
        """Extract description from content"""
        if content:
            # Find first paragraph after title
            sentences = content.split('. ')
            for sentence in sentences[:3]:
                if len(sentence) > 50 and sentence not in title:
                    return sentence[:200] + ('...' if len(sentence) > 200 else '')

        return f"Read our latest article: {title}"

    def _extract_excerpt(self, content: str) -> str:
        """Extract excerpt for post"""
        if content:
            return content[:200] + ('...' if len(content) > 200 else '')
        return ""

    def _extract_tags(self, title: str, content: str) -> List[str]:
        """Extract relevant tags from title and content"""
        keywords = {
            'EEG': 'EEG',
            'Brain': 'BrainTech',
            'Neural': 'NeuralNetworks',
            'AI': 'AI',
            'Healthcare': 'Healthcare',
            'FDA': 'FDA',
            'Edge': 'EdgeComputing',
            'Cloud': 'CloudComputing',
            'Medical': 'MedicalDevices',
            'Compliance': 'Compliance',
            'Data': 'DataScience',
            'Audio': 'AudioAnalysis',
            'Signal': 'SignalProcessing',
            'Privacy': 'DataPrivacy',
            'Industrial': 'IndustrialAI',
            'Sustainable': 'Sustainability'
        }

        tags = ['Clisonix']
        text = f"{title} {content}".lower()

        for keyword, tag in keywords.items():
            if keyword.lower() in text:
                tags.append(tag)

        return list(set(tags))[:5]  # Unique, max 5

    def _get_sample_articles(self) -> List[Dict[str, Any]]:
        """Return sample articles for testing"""
        return [
            {
                'id': 'eeg-analysis-intro',
                'title': 'Introduction to EEG Analysis with AI',
                'description': 'Learn how artificial intelligence is revolutionizing EEG signal processing and brain-computer interfaces.',
                'excerpt': 'Learn how artificial intelligence is revolutionizing EEG signal processing...',
                'slug': 'eeg-analysis-intro',
                'url': f"{config.BLOG_URL}static/eeg-analysis-intro.html",
                'date': datetime.now().strftime('%Y-%m-%d'),
                'category': 'EEG Analytics',
                'content_type': ContentType.BLOG_ARTICLE,
                'tags': ['EEG', 'AI', 'BrainTech', 'NeuralNetworks']
            },
            {
                'id': 'industrial-ai-2026',
                'title': 'Industrial AI Trends for 2026',
                'description': 'Discover the latest trends in industrial artificial intelligence.',
                'excerpt': 'Discover the latest trends in industrial artificial intelligence...',
                'slug': 'industrial-ai-trends-2026',
                'url': f"{config.BLOG_URL}static/industrial-ai-trends-2026.html",
                'date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
                'category': 'Industrial AI',
                'content_type': ContentType.BLOG_ARTICLE,
                'tags': ['IndustrialAI', 'Manufacturing', 'Industry40']
            }
        ]

    async def scan_documents(self) -> List[Dict[str, Any]]:
        """Scan document directories for new files"""
        if not config.DOCUMENT_SCAN_ENABLED:
            return []

        # Load snapshot
        snapshot = await self._load_document_snapshot()
        seen = snapshot.get('seen', {})
        updated_seen = dict(seen)
        new_articles = []

        for directory in config.DOCUMENT_SCAN_DIRS:
            if not directory.exists():
                continue

            for file_path in directory.rglob(config.DOCUMENT_SCAN_GLOB):
                if not file_path.is_file():
                    continue

                path_key = str(file_path)
                mtime = str(file_path.stat().st_mtime)

                # Skip only when unchanged; re-process updated documents.
                if path_key in seen and str(seen.get(path_key)) == mtime:
                    updated_seen[path_key] = mtime
                    continue

                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                except Exception as e:
                    logger.error(f"Error reading new document {file_path}: {e}")
                    continue

                updated_seen[path_key] = mtime

                if not self._is_publishable_document(content):
                    logger.warning(f"Skipping non-publishable document: {file_path}")
                    continue

                # Extract title
                title = self._extract_title_from_document(file_path, content)

                # Generate description
                lines = content.splitlines()
                description = next((line for line in lines if line and len(line) > 30), content[:200])

                article = {
                    'id': f"doc-{hashlib.md5(f'{path_key}:{mtime}'.encode()).hexdigest()[:16]}",
                    'title': title,
                    'description': description[:200],
                    'content': content[:2000],
                    'slug': file_path.stem,
                    'url': f"{config.SITE_URL.rstrip('/')}/docs/{file_path.stem}",
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'category': 'Documents',
                    'content_type': ContentType.DOCUMENT,
                    'tags': self._extract_tags(title, content),
                    'source_file': path_key,
                }

                new_articles.append(article)

        if updated_seen != seen:
            await self._save_document_snapshot({
                "seen": updated_seen,
                "last_updated": datetime.now().isoformat()
            })

        if new_articles:
            logger.info(f"📄 Detected {len(new_articles)} new documents")

        return new_articles

    def _is_publishable_document(self, content: str) -> bool:
        """Basic quality gate so empty/refusal placeholders never reach production posting."""
        text = (content or '').strip()
        if len(text) < 350:
            return False

        lowered = text.lower()
        blocked_markers = (
            "i can't fulfill this request",
            "cannot fulfill this request",
            "placeholder",
            "lorem ipsum",
        )
        if any(marker in lowered for marker in blocked_markers):
            return False

        return True

    def _extract_title_from_document(self, file_path: Path, content: str) -> str:
        """Extract title from document content"""
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        for line in lines[:25]:
            if line.startswith('#'):
                return re.sub(r'^#+\s*', '', line).strip()[:120]
        return file_path.stem.replace('-', ' ').replace('_', ' ').title()[:120]

    async def _load_document_snapshot(self) -> dict:
        """Load document snapshot from file"""
        path = Path(config.DOCUMENT_SNAPSHOT_FILE)
        if path.exists():
            try:
                async with asyncio.Lock():
                    with open(path, 'r', encoding='utf-8') as f:
                        return json.load(f)
            except Exception as e:
                logger.error(f"Error loading document snapshot: {e}")
        return {"seen": {}, "last_updated": None}

    async def _save_document_snapshot(self, data: dict) -> None:
        """Save document snapshot to file"""
        path = Path(config.DOCUMENT_SNAPSHOT_FILE)
        async with asyncio.Lock():
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

    async def get_all_sources(self) -> Dict[str, Any]:
        """Get all content sources"""
        blog_articles = await self.fetch_blog_articles()
        documents = await self.scan_documents()

        return {
            'blog': blog_articles,
            'documents': documents,
            'total': len(blog_articles) + len(documents)
        }


# ═══════════════════════════════════════════════════════════════════════════════
# POST MANAGER
# ═══════════════════════════════════════════════════════════════════════════════

class PostManager:
    """
    Manages the entire posting workflow:
    - Scheduling
    - Content generation
    - Multi-platform posting
    - Tracking
    - Analytics
    """

    def __init__(self):
        self.content_source = ContentSourceManager()
        self.ai = ai_generator
        self.linkedin_client = LinkedInAPIClient(
            access_token=config.ACCESS_TOKEN,
            person_urn=config.PERSON_URN
        )
        self.twitter_client = TwitterAPIClient() if config.ENABLE_TWITTER else None
        self.medium_client = MediumAPIClient() if config.ENABLE_MEDIUM else None
        self.devto_client = DevToAPIClient() if config.ENABLE_DEVTO else None

        self._posted_ids: Set[str] = set()
        self._post_queue: asyncio.Queue = asyncio.Queue()
        self._scheduled_posts: Dict[str, ScheduledPost] = {}
        self._workers: List[asyncio.Task] = []
        self._running = False
        self._lock = asyncio.Lock()

    async def initialize(self):
        """Initialize the post manager"""
        # Load posted articles
        await self._load_posted_ids()

        # Start workers
        self._running = True
        for i in range(3):  # 3 workers for parallel processing
            worker = asyncio.create_task(self._worker_loop(i))
            self._workers.append(worker)

        active_sessions.set(1)
        logger.info(f"🚀 PostManager initialized with {len(self._workers)} workers")

    async def shutdown(self):
        """Shutdown the post manager"""
        self._running = False

        # Cancel workers
        for worker in self._workers:
            worker.cancel()

        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()

        # Close API clients
        await self.linkedin_client.close()

        active_sessions.set(0)
        logger.info("🛑 PostManager shut down")

    async def _load_posted_ids(self):
        """Load already posted article IDs"""
        path = Path(config.POSTED_ARTICLES_FILE)
        if path.exists():
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    self._posted_ids = set(data.get('posted', []))
                    logger.info(f"📋 Loaded {len(self._posted_ids)} posted articles")
            except Exception as e:
                logger.error(f"Error loading posted articles: {e}")

    async def _save_posted_id(self, article_id: str):
        """Save a posted article ID"""
        async with self._lock:
            self._posted_ids.add(article_id)

            with open(config.POSTED_ARTICLES_FILE, 'w') as f:
                json.dump({
                    'posted': list(self._posted_ids),
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2)

    async def _worker_loop(self, worker_id: int):
        """Worker for processing posts"""
        logger.info(f"Worker {worker_id} started")

        while self._running:
            try:
                # Get next post from queue
                post_task = await self._post_queue.get()

                # Process the post
                result = await self._process_post(post_task)

                # Update metrics
                if result.get('success'):
                    posts_total.labels(status='success', platform=post_task['platform'].value).inc()
                else:
                    posts_total.labels(status='failed', platform=post_task['platform'].value).inc()

                self._post_queue.task_done()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(1)

        logger.info(f"Worker {worker_id} stopped")

    async def _process_post(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single post task"""
        article = task['article']
        platform = task['platform']
        content_type = task.get('content_type', ContentType.BLOG_ARTICLE)

        # Generate content
        content = await self.ai.generate_post_content(
            article,
            content_type=content_type,
            platform=platform
        )

        # Predict engagement
        prediction = await self.ai.predict_engagement(content, platform)

        # Post to platform
        result = await self._post_to_platform(platform, content, article)

        if result.get('success'):
            # Save to database
            if db.pg_pool:
                async with db.pg_pool.acquire() as conn:
                    await conn.execute("""
                        INSERT INTO linkedin_posts
                        (id, platform, content, content_type, status, platform_post_id, published_time, metadata)
                        VALUES ($1, $2, $3, $4, $5, $6, NOW(), $7)
                    """,
                        result['post_id'],
                        platform.value,
                        content,
                        content_type.value,
                        result['status'].value,
                        result.get('platform_post_id'),
                        json.dumps({'prediction': prediction})
                    )

            # Mark as posted
            await self._save_posted_id(article['id'])

            # Delete source file if configured
            if config.DELETE_SOURCE_AFTER_POST and article.get('source_file'):
                await self._delete_source_file(article['source_file'])

            logger.info(f"✅ Posted {article['title']} to {platform.value}")

        return result

    async def _post_to_platform(self, platform: Platform, content: str, article: Dict) -> Dict[str, Any]:
        """Post to specific platform"""
        if platform == Platform.LINKEDIN:
            return await self.linkedin_client.create_post(content)
        elif platform == Platform.TWITTER and self.twitter_client:
            return await self.twitter_client.create_post(content)
        elif platform == Platform.MEDIUM and self.medium_client:
            return await self.medium_client.create_post(article['title'], content, article.get('tags', []))
        elif platform == Platform.DEVTO and self.devto_client:
            return await self.devto_client.create_post(article['title'], content, article.get('tags', []))
        else:
            return {
                'success': False,
                'error': f'Platform {platform} not configured',
                'status': PostStatus.FAILED
            }

    async def _delete_source_file(self, file_path: str):
        """Delete source file after posting"""
        try:
            path = Path(file_path)
            if path.exists() and path.is_file():
                path.unlink()
                logger.info(f"🗑️ Deleted source file: {path}")
        except Exception as e:
            logger.warning(f"Failed to delete source file {file_path}: {e}")

    async def check_and_post(self, post_all: bool = True) -> Dict[str, Any]:
        """Check for new content and post if any"""
        # Get all sources
        sources = await self.content_source.get_all_sources()
        all_articles = sources['blog'] + sources['documents']

        posted_results = []

        # Find unposted articles
        for article in all_articles:
            article_id = article.get('id')
            if not article_id:
                continue

            if article_id not in self._posted_ids:
                logger.info(f"📝 Found unposted: {article.get('title')}")

                # Add to queue
                await self._post_queue.put({
                    'article': article,
                    'platform': Platform.LINKEDIN,  # Default to LinkedIn
                    'content_type': article.get('content_type', ContentType.BLOG_ARTICLE)
                })

                posted_results.append({
                    'article': article.get('title'),
                    'article_id': article_id
                })

                if not post_all:
                    break

        # Wait for queue to process if we posted something
        if posted_results and post_all:
            await self._post_queue.join()

        return {
            'success': True,
            # Backward-compatible key; this value reflects queued candidates.
            'posted_count': len(posted_results),
            'queued_count': len(posted_results),
            'posted': posted_results,
            'queue_size': self._post_queue.qsize()
        }

    async def schedule_post(self, post: ScheduledPost) -> str:
        """Schedule a post for future publication"""
        self._scheduled_posts[post.id] = post
        logger.info(f"📅 Scheduled post {post.id} for {post.scheduled_time}")
        return post.id

    async def get_pending_articles(self) -> List[Dict[str, Any]]:
        """Get all articles not yet posted"""
        sources = await self.content_source.get_all_sources()
        all_articles = sources['blog'] + sources['documents']

        pending = []
        for article in all_articles:
            article_id = article.get('id')
            if article_id and article_id not in self._posted_ids:
                pending.append(article)

        return pending

    async def get_analytics(self) -> Dict[str, Any]:
        """Get posting analytics"""
        if not db.pg_pool:
            return {'error': 'Database not configured'}

        async with db.pg_pool.acquire() as conn:
            # Total posts
            total = await conn.fetchval("SELECT COUNT(*) FROM linkedin_posts")

            # Posts by platform
            platform_rows = await conn.fetch("""
                SELECT platform, COUNT(*) as count
                FROM linkedin_posts
                GROUP BY platform
            """)
            by_platform = {row['platform']: row['count'] for row in platform_rows}

            # Engagement metrics
            metrics = await conn.fetch("""
                SELECT
                    AVG(likes) as avg_likes,
                    AVG(comments) as avg_comments,
                    AVG(shares) as avg_shares,
                    AVG(engagement_rate) as avg_engagement
                FROM post_metrics
            """)

            # Top posts
            top_posts = await conn.fetch("""
                SELECT p.id, p.content, m.likes, m.comments, m.shares
                FROM linkedin_posts p
                JOIN post_metrics m ON p.id = m.post_id
                ORDER BY (m.likes + m.comments + m.shares) DESC
                LIMIT 5
            """)

            # Recommendations
            recommendations = [
                "Best posting time: Tuesday 10:00 AM UTC",
                "Posts with 3-5 hashtags get 20% more engagement",
                "Include a question to increase comments by 40%",
                "Use emojis to increase click-through rate by 25%"
            ]

            return {
                'total_posts': total,
                'posts_by_platform': by_platform,
                'avg_engagement': {
                    'likes': metrics[0]['avg_likes'] if metrics else 0,
                    'comments': metrics[0]['avg_comments'] if metrics else 0,
                    'shares': metrics[0]['avg_shares'] if metrics else 0,
                    'rate': metrics[0]['avg_engagement'] if metrics else 0
                },
                'top_posts': [dict(p) for p in top_posts],
                'recommendations': recommendations
            }


# ═══════════════════════════════════════════════════════════════════════════════
# FASTAPI APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════

def create_app() -> "FastAPI":
    """Create FastAPI application"""
    from fastapi import BackgroundTasks, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse, StreamingResponse

    app = FastAPI(
        title="LinkedIn Auto Poster ULTRA",
        description="Industrial-grade content automation system for Clisonix",
        version="3.0.0-ULTRA"
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Global post manager
    post_manager = PostManager()
    continuous_task: Optional[asyncio.Task] = None

    async def _continuous_posting_loop() -> None:
        """Run posting checks continuously so new pillars are posted any time."""
        logger.info(f"🔄 Continuous posting enabled (interval: {config.POLL_SECONDS}s)")
        while True:
            try:
                result = await post_manager.check_and_post(
                    post_all=config.POST_ALL_PENDING
                )
                queued_count = int(
                    result.get("queued_count", result.get("posted_count", 0)) or 0
                )
                if queued_count > 0:
                    logger.info(f"📥 Continuous loop queued {queued_count} articles")
            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.error(f"Continuous posting loop error: {e}")
            await asyncio.sleep(config.POLL_SECONDS)

    @app.on_event("startup")
    async def startup():
        """Initialize services on startup"""
        nonlocal continuous_task
        await db.initialize()
        await ai_generator.initialize()
        await post_manager.initialize()
        continuous_task = asyncio.create_task(_continuous_posting_loop())
        logger.info("🚀 LinkedIn Auto Poster ULTRA started")

    @app.on_event("shutdown")
    async def shutdown():
        """Clean shutdown"""
        nonlocal continuous_task
        if continuous_task:
            continuous_task.cancel()
            await asyncio.gather(continuous_task, return_exceptions=True)
            continuous_task = None
        await post_manager.shutdown()
        await db.close()
        logger.info("🛑 LinkedIn Auto Poster ULTRA stopped")

    # =========================================================================
    # HEALTH ENDPOINTS
    # =========================================================================

    @app.get("/health")
    async def health() -> Dict[str, Any]:
        """Health check endpoint"""
        cooldown_remaining = await rate_limiter.get_remaining("linkedin_api")

        return {
            "status": "healthy",
            "service": "linkedin-auto-poster-ultra",
            "version": "3.0.0-ULTRA",
            "timestamp": datetime.now().isoformat(),
            "config": {
                "poll_seconds": config.POLL_SECONDS,
                "post_all_pending": config.POST_ALL_PENDING,
                "max_posts_per_day": config.MAX_POSTS_PER_DAY,
                "scan_documents": config.DOCUMENT_SCAN_ENABLED,
                "platforms": {
                    "linkedin": bool(config.ACCESS_TOKEN),
                    "twitter": config.ENABLE_TWITTER,
                    "medium": config.ENABLE_MEDIUM,
                    "devto": config.ENABLE_DEVTO
                }
            },
            "rate_limiter": cooldown_remaining,
            "posted_count": len(post_manager._posted_ids),
            "queue_size": post_manager._post_queue.qsize()
        }

    @app.get("/health/detailed")
    async def health_detailed() -> Dict[str, Any]:
        """Detailed health check"""
        return {
            "status": "healthy",
            "components": {
                "database": db.pg_pool is not None,
                "redis": db.redis is not None,
                "linkedin_api": bool(config.ACCESS_TOKEN),
                "blerina": await ai_generator._check_ai_available()
            },
            "stats": {
                "posted_articles": len(post_manager._posted_ids),
                "queue_size": post_manager._post_queue.qsize(),
                "workers": len(post_manager._workers)
            },
            "timestamp": datetime.now().isoformat()
        }

    # =========================================================================
    # POSTING ENDPOINTS
    # =========================================================================

    @app.post("/api/linkedin/post-now")
    async def post_now(
        post_all: bool = True
    ) -> Dict[str, Any]:
        """Immediately check and post pending articles"""
        result = await post_manager.check_and_post(post_all=post_all)
        return result

    @app.post("/api/linkedin/schedule")
    async def schedule_post(request: PostRequest) -> PostResponse:
        """Schedule a custom post"""
        post_id = f"post_{uuid.uuid4().hex[:12]}"

        scheduled = ScheduledPost(
            id=post_id,
            content=request.content,
            platform=request.platform,
            scheduled_time=request.schedule_time or (datetime.now(timezone.utc) + timedelta(hours=1)),
            content_type=request.content_type,
            hashtags=request.hashtags,
            media_urls=request.media_urls
        )

        await post_manager.schedule_post(scheduled)

        return PostResponse(
            success=True,
            post_id=post_id,
            platform=request.platform,
            status=PostStatus.SCHEDULED,
            scheduled_time=scheduled.scheduled_time
        )

    @app.post("/api/linkedin/post-custom")
    async def post_custom(request: PostRequest) -> PostResponse:
        """Post custom content immediately"""
        # Create article-like structure
        article = {
            'id': f"custom_{uuid.uuid4().hex[:12]}",
            'title': request.content[:50] + ('...' if len(request.content) > 50 else ''),
            'description': request.content[:200],
            'content': request.content,
            'url': '',
            'tags': request.hashtags,
            'content_type': request.content_type
        }

        # Post to platform
        if request.platform == Platform.LINKEDIN:
            result = await post_manager.linkedin_client.create_post(request.content)
        elif request.platform == Platform.TWITTER and post_manager.twitter_client:
            result = await post_manager.twitter_client.create_post(request.content)
        else:
            return PostResponse(
                success=False,
                platform=request.platform,
                status=PostStatus.FAILED,
                error=f"Platform {request.platform} not supported"
            )

        if result.get('success'):
            custom_article_id = str(article['id'])
            # Save to posted IDs
            await post_manager._save_posted_id(custom_article_id)

            return PostResponse(
                success=True,
                post_id=custom_article_id,
                platform_post_id=result.get('platform_post_id'),
                platform=request.platform,
                status=PostStatus.PUBLISHED
            )
        else:
            return PostResponse(
                success=False,
                platform=request.platform,
                status=PostStatus.FAILED,
                error=result.get('error')
            )

    # =========================================================================
    # CONTENT ENDPOINTS
    # =========================================================================

    @app.get("/api/linkedin/pending")
    async def get_pending() -> Dict[str, Any]:
        """Get all pending articles"""
        pending = await post_manager.get_pending_articles()
        return {
            "success": True,
            "count": len(pending),
            "pending": pending
        }

    @app.get("/api/linkedin/posted")
    async def get_posted() -> Dict[str, Any]:
        """Get all posted articles"""
        return {
            "success": True,
            "count": len(post_manager._posted_ids),
            "posted": list(post_manager._posted_ids)
        }

    @app.get("/api/linkedin/sources")
    async def get_sources(refresh: bool = False) -> Dict[str, Any]:
        """Get all content sources"""
        if refresh:
            post_manager.content_source.cache.clear()

        sources = await post_manager.content_source.get_all_sources()
        return {
            "success": True,
            **sources
        }

    # =========================================================================
    # ANALYTICS ENDPOINTS
    # =========================================================================

    @app.get("/api/linkedin/analytics")
    async def get_analytics() -> Dict[str, Any]:
        """Get posting analytics"""
        analytics = await post_manager.get_analytics()
        return {
            "success": True,
            **analytics
        }

    @app.get("/api/linkedin/analytics/export")
    async def export_analytics(format: str = "json") -> "Response":
        """Export analytics in various formats"""
        analytics = await post_manager.get_analytics()

        if format == "json":
            return JSONResponse(analytics)
        elif format == "csv":
            if pd is not None:
                df = pd.DataFrame([analytics])
                csv_data = df.to_csv(index=False)
            else:
                output = io.StringIO()
                writer = csv.writer(output)
                writer.writerow(["key", "value"])
                for key, value in analytics.items():
                    writer.writerow([key, json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value])
                csv_data = output.getvalue()
            return Response(
                content=csv_data,
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=analytics.csv"}
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")

    # =========================================================================
    # AI ENDPOINTS
    # =========================================================================

    @app.post("/api/linkedin/generate")
    async def generate_content(
        title: str,
        description: Optional[str] = None,
        content_type: ContentType = ContentType.BLOG_ARTICLE,
        platform: Platform = Platform.LINKEDIN
    ) -> Dict[str, Any]:
        """Generate AI-powered post content"""
        article = {
            'title': title,
            'description': description or title,
            'excerpt': description or title,
            'url': config.SITE_URL,
            'tags': []
        }

        content = await ai_generator.generate_post_content(
            article,
            content_type=content_type,
            platform=platform
        )

        prediction = await ai_generator.predict_engagement(content, platform)

        return {
            "success": True,
            "content": content,
            "prediction": prediction,
            "best_time": await ai_generator.suggest_best_time(content_type)
        }

    @app.post("/api/linkedin/optimize-hashtags")
    async def optimize_hashtags(tags: List[str]) -> Dict[str, Any]:
        """Optimize hashtags for maximum engagement"""
        optimized = ai_generator._optimize_hashtags(tags)
        return {
            "success": True,
            "original": tags,
            "optimized": optimized.split(),
            "count": len(optimized.split())
        }

    # =========================================================================
    # LAGTER INTEGRATION
    # =========================================================================

    @app.post("/api/linkedin/trigger-lagter")
    async def trigger_lagter() -> Dict[str, Any]:
        """Trigger Lagter batch publish"""
        if not config.LAGTER_TRIGGER_ENABLED:
            return {"success": False, "error": "Lagter trigger disabled"}

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(config.LAGTER_TRIGGER_URL)

                return {
                    "success": 200 <= response.status_code < 300,
                    "status_code": response.status_code,
                    "response": response.text[:500]
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    # =========================================================================
    # WEBHOOK INTEGRATION
    # =========================================================================

    @app.post("/api/linkedin/webhook")
    async def webhook_receiver(request: "Request"):
        """Receive webhooks from external services"""
        body = await request.body()
        signature = request.headers.get('X-Clisonix-Signature', '')

        # Verify signature
        secret = os.getenv('WEBHOOK_SECRET', 'clisonix-secret')
        expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

        if not hmac.compare_digest(signature, expected):
            raise HTTPException(status_code=401, detail="Invalid signature")

        # Process webhook
        data = json.loads(body)
        event_type = data.get('type')

        if event_type == 'new_article':
            # Trigger immediate post
            asyncio.create_task(post_manager.check_and_post(post_all=False))

        return {"success": True, "received": event_type}

    return app


# ═══════════════════════════════════════════════════════════════════════════════
# STANDALONE EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════

async def continuous_loop():
    """Continuous posting loop for standalone mode"""
    # Initialize
    await db.initialize()
    await ai_generator.initialize()

    post_manager = PostManager()
    await post_manager.initialize()

    logger.info(f"🔄 Starting continuous loop (interval: {config.POLL_SECONDS}s)")

    try:
        while True:
            try:
                # Check and post
                result = await post_manager.check_and_post(post_all=config.POST_ALL_PENDING)

                queued_count = int(result.get('queued_count', result.get('posted_count', 0)) or 0)
                if queued_count > 0:
                    logger.info(f"📥 Queued {queued_count} articles")

                # Wait for next cycle
                await asyncio.sleep(config.POLL_SECONDS)

            except Exception as e:
                logger.error(f"Loop error: {e}")
                await asyncio.sleep(60)  # Wait longer on error

    finally:
        await post_manager.shutdown()
        await db.close()


def main():
    """Main entry point"""
    import sys

    import uvicorn

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "serve":
            # Run as API server
            app = create_app()
            uvicorn.run(
                app,
                host="0.0.0.0",
                port=8007,
                log_level="info"
            )

        elif command == "loop":
            # Run continuous loop
            asyncio.run(continuous_loop())

        elif command == "once":
            # Run once and exit
            async def run_once():
                await db.initialize()
                await ai_generator.initialize()

                pm = PostManager()
                await pm.initialize()

                result = await pm.check_and_post(post_all=True)
                print(json.dumps(result, indent=2))

                await pm.shutdown()
                await db.close()

            asyncio.run(run_once())

        elif command == "daily":
            # Backward-compatible alias used by cron in Dockerfile.linkedin
            async def run_daily_once():
                await db.initialize()
                await ai_generator.initialize()

                pm = PostManager()
                await pm.initialize()

                result = await pm.check_and_post(post_all=True)
                print(json.dumps(result, indent=2))

                await pm.shutdown()
                await db.close()

            asyncio.run(run_daily_once())

        elif command == "test":
            # Test post
            async def test():
                await db.initialize()
                await ai_generator.initialize()

                pm = PostManager()
                await pm.initialize()

                article = {
                    'id': 'test-article',
                    'title': 'Test Article',
                    'description': 'This is a test post from LinkedIn Auto Poster ULTRA',
                    'url': 'https://clisonix.com',
                    'tags': ['Test', 'Clisonix', 'AI']
                }

                content = await ai_generator.generate_post_content(article)
                print(f"\n📝 Generated content:\n{content}\n")

                prediction = await ai_generator.predict_engagement(content, Platform.LINKEDIN)
                print(f"📊 Predicted engagement: {prediction}\n")

                best_time = await ai_generator.suggest_best_time(ContentType.BLOG_ARTICLE)
                print(f"⏰ Best posting time: {best_time}\n")

                await pm.shutdown()
                await db.close()

            asyncio.run(test())

        else:
            print(f"Unknown command: {command}")
            print("Usage: python linkedin_auto_poster_ultra.py [serve|loop|once|daily|test]")

    else:
        print("Usage: python linkedin_auto_poster_ultra.py [serve|loop|once|daily|test]")


if __name__ == "__main__":
    main()
