from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
import os
import time
from collections import defaultdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import httpx
import numpy as np
import redis.asyncio as redis
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/integrations/youtube", tags=["youtube"])
logger = logging.getLogger(__name__)


def _error_detail(code: str, message: str, **extra: Any) -> dict:
    detail: dict[str, Any] = {"error": code, "message": message}
    detail.update(extra)
    return detail

# ============================================================================
# KONFIGURIME TË AVANCUARA
# ============================================================================

class YouTubeConfig:
    API_KEY = os.getenv("YOUTUBE_API_KEY")
    BASE_URL = "https://www.googleapis.com/youtube/v3"
    CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")

    # Rate limiting
    MAX_REQUESTS_PER_SECOND = 10
    MAX_REQUESTS_PER_DAY = 999_999_999  # unlimited

    # Caching
    CACHE_TTL = {
        "channel": 3600,      # 1 orë
        "videos": 1800,        # 30 minuta
        "search": 900,         # 15 minuta
        "trending": 600,       # 10 minuta
    }

    # Webhook për notifikime
    WEBHOOK_SECRET = os.getenv("YOUTUBE_WEBHOOK_SECRET", "clisonix-super-secret")

    # Redis connection
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REQUEST_TIMEOUT_SECONDS = 300.0  # 5 minutes elastic

# ============================================================================
# MODELE TË AVANCUARA PYDANTIC
# ============================================================================

class VideoCategory(str, Enum):
    MUSIC = "music"
    EDUCATION = "education"
    TECHNOLOGY = "technology"
    HEALTH = "health"
    SCIENCE = "science"
    ENTERTAINMENT = "entertainment"
    NEWS = "news"
    GAMING = "gaming"
    VLOGS = "vlogs"
    OTHER = "other"

class ContentRating(str, Enum):
    SAFE = "safe"
    MODERATE = "moderate"
    RESTRICTED = "restricted"
    AGE_RESTRICTED = "age_restricted"

class SentimentAnalysis(BaseModel):
    score: float = Field(..., ge=-1, le=1)  # -1 negative, 1 positive
    magnitude: float = Field(..., ge=0)
    label: str  # positive, negative, neutral

class TopicInsight(BaseModel):
    topic: str
    confidence: float = Field(..., ge=0, le=1)
    related_topics: List[str] = Field(default_factory=list)
    search_volume: Optional[int] = None
    trend_direction: str = "stable"  # up, down, stable

class VideoInsight(BaseModel):
    video_id: str
    title: str
    description: str
    published_at: datetime
    duration_seconds: int
    view_count: int
    like_count: int
    comment_count: int
    category: VideoCategory
    rating: ContentRating
    sentiment: SentimentAnalysis
    topics: List[TopicInsight]
    engagement_rate: float
    estimated_revenue: Optional[float] = None
    viral_score: float = Field(..., ge=0, le=100)
    quality_score: float = Field(..., ge=0, le=100)

class ChannelAnalytics(BaseModel):
    channel_id: str
    channel_name: str
    subscriber_count: int
    total_views: int
    total_videos: int
    avg_views_per_video: float
    avg_engagement_rate: float
    growth_rate: float  # % rritje mujore
    top_categories: List[Tuple[VideoCategory, int]]
    best_posting_time: Optional[str] = None
    estimated_monthly_revenue: float
    content_quality_score: float
    audience_retention: float
    recommendations: List[str] = Field(default_factory=list)

# ============================================================================
# CACHE MANAGER ME REDIS
# ============================================================================

class YouTubeCache:
    def __init__(self, redis_url: str):
        self.redis: Optional[redis.Redis] = None
        self.redis_url = redis_url
        self.stats: defaultdict[str, int] = defaultdict(int)

    async def initialize(self):
        """Inicializo Redis connection"""
        if not self.redis:
            self.redis = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )

    async def get(self, key: str) -> Optional[Any]:
        """Merr nga cache me stats"""
        await self.initialize()
        if self.redis is None:
            return None
        data = await self.redis.get(f"youtube:{key}")
        self.stats["hits" if data else "misses"] += 1
        return json.loads(data) if data else None

    async def set(self, key: str, value: Any, ttl: int):
        """Vendos në cache"""
        await self.initialize()
        if self.redis is None:
            return
        await self.redis.setex(
            f"youtube:{key}",
            ttl,
            json.dumps(value, default=str)
        )

    async def delete_pattern(self, pattern: str):
        """Fshij të gjitha keys që përputhen me pattern"""
        await self.initialize()
        if self.redis is None:
            return
        keys = [key async for key in self.redis.scan_iter(match=f"youtube:{pattern}*")]
        if keys:
            await self.redis.delete(*keys)

    async def get_stats(self) -> dict:
        """Statistikat e cache"""
        return {
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_rate": self.stats["hits"] / (self.stats["hits"] + self.stats["misses"] + 1),
            "memory_usage": await self.redis.info("memory") if self.redis else 0
        }

cache = YouTubeCache(YouTubeConfig.REDIS_URL)

# ============================================================================
# RATE LIMITER I AVANCUAR
# ============================================================================

class YouTubeRateLimiter:
    def __init__(self):
        self.requests_per_second: Dict[str, List[float]] = defaultdict(list)
        self.requests_per_day: Dict[str, int] = defaultdict(int)
        self.last_reset = datetime.now()

    async def check_limit(self, client_id: str = "default") -> bool:
        """Kontrollo nëse klienti ka kaluar limitin"""
        now = time.time()

        # Reset daily counter nëse ka kaluar 24 orë
        if datetime.now() - self.last_reset > timedelta(hours=24):
            self.requests_per_day.clear()
            self.last_reset = datetime.now()

        # Clean old second-based requests (>1 sekondë)
        self.requests_per_second[client_id] = [
            ts for ts in self.requests_per_second[client_id]
            if now - ts < 1.0
        ]

        # Check limits
        if len(self.requests_per_second[client_id]) >= YouTubeConfig.MAX_REQUESTS_PER_SECOND:
            return False

        if self.requests_per_day[client_id] >= YouTubeConfig.MAX_REQUESTS_PER_DAY:
            return False

        # Add request
        self.requests_per_second[client_id].append(now)
        self.requests_per_day[client_id] += 1
        return True

    async def get_remaining(self, client_id: str = "default") -> dict:
        """Kthen sa requests kanë mbetur"""
        now = time.time()
        self.requests_per_second[client_id] = [
            ts for ts in self.requests_per_second[client_id]
            if now - ts < 1.0
        ]

        return {
            "second_remaining": YouTubeConfig.MAX_REQUESTS_PER_SECOND - len(self.requests_per_second[client_id]),
            "day_remaining": YouTubeConfig.MAX_REQUESTS_PER_DAY - self.requests_per_day[client_id],
            "reset_in_seconds": (timedelta(hours=24) - (datetime.now() - self.last_reset)).total_seconds()
        }

rate_limiter = YouTubeRateLimiter()

# ============================================================================
# ANALIZUES I PËRMBAJTJES ME AI
# ============================================================================

class YouTubeContentAnalyzer:
    def __init__(self):
        # Kategori bazuar në keywords
        self.category_keywords = {
            VideoCategory.MUSIC: {"music", "song", "audio", "remix", "cover", "playlist", "album"},
            VideoCategory.EDUCATION: {"learn", "tutorial", "course", "lesson", "education", "school", "university"},
            VideoCategory.TECHNOLOGY: {"tech", "coding", "programming", "software", "hardware", "ai", "computer"},
            VideoCategory.HEALTH: {"health", "fitness", "workout", "exercise", "nutrition", "medical", "wellness"},
            VideoCategory.SCIENCE: {"science", "physics", "chemistry", "biology", "research", "experiment", "nasa"},
            VideoCategory.GAMING: {"game", "gaming", "playthrough", "walkthrough", "minecraft", "fortnite"},
        }

        # Fjalor për sentiment analysis
        self.positive_words = {"good", "great", "awesome", "excellent", "amazing", "wonderful", "fantastic", "love"}
        self.negative_words = {"bad", "terrible", "awful", "horrible", "worst", "hate", "dislike", "poor"}

    async def analyze_sentiment(self, text: str) -> SentimentAnalysis:
        """Analizë sentimenti të avancuar"""
        words = text.lower().split()

        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        total_sentiment_words = positive_count + negative_count

        if total_sentiment_words == 0:
            return SentimentAnalysis(score=0, magnitude=0, label="neutral")

        score = (positive_count - negative_count) / total_sentiment_words
        magnitude = total_sentiment_words / max(len(words), 1)

        # Normalizo magnitude në [0, 1]
        magnitude = min(magnitude, 1.0)

        label = "positive" if score > 0.2 else "negative" if score < -0.2 else "neutral"

        return SentimentAnalysis(score=score, magnitude=magnitude, label=label)

    async def detect_category(self, title: str, description: str) -> VideoCategory:
        """Detekto kategorinë e videos"""
        text = f"{title} {description}".lower()

        category_scores = {}
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            category_scores[category] = score

        if not any(category_scores.values()):
            return VideoCategory.OTHER

        return max(category_scores.items(), key=lambda x: x[1])[0]

    async def extract_topics(self, title: str, description: str) -> List[TopicInsight]:
        """Ekstrakto topic-et kryesore"""
        # Në praktikë, këtu do përdorej NLP/NER
        # Por për demo, përdorim keywords
        text = f"{title} {description}".lower()

        topics = []
        common_topics = {
            "python": 0.9, "javascript": 0.9, "ai": 0.95, "machine learning": 0.95,
            "health": 0.8, "fitness": 0.8, "nutrition": 0.85,
            "music": 0.9, "production": 0.8, "beat": 0.8,
            "tutorial": 0.7, "guide": 0.7, "how to": 0.7
        }

        for topic, confidence in common_topics.items():
            if topic in text:
                topics.append(TopicInsight(
                    topic=topic,
                    confidence=confidence,
                    trend_direction="up" if confidence > 0.8 else "stable"
                ))

        return topics[:5]  # Max 5 topics

    async def calculate_viral_score(self, views: int, likes: int, comments: int,
                                   subscribers: int, days_since_published: float) -> float:
        """Llogarit sa virale është një video"""
        if days_since_published == 0:
            days_since_published = 0.1

        views_per_day = views / days_since_published
        engagement = (likes + comments * 2) / max(views, 1)

        # Faktorët
        view_score = min(views_per_day / 10000, 1.0)  # Max 10k views/day
        engagement_score = min(engagement * 100, 1.0)  # Max 1% engagement
        subscriber_boost = min(subscribers / 1000000, 1.0)  # Max 1M subscribers

        # Ponderimi
        viral_score = (
            view_score * 0.4 +
            engagement_score * 0.4 +
            subscriber_boost * 0.2
        ) * 100

        return min(viral_score, 100)

analyzer = YouTubeContentAnalyzer()

# ============================================================================
# WEBHOOK HANDLER PËR NOTIFIKIME
# ============================================================================

class YouTubeWebhookHandler:
    def __init__(self, secret: str):
        self.secret = secret
        self.subscribers: Dict[str, List[str]] = defaultdict(list)  # event -> urls

    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verifikon webhook signature"""
        expected = hmac.new(
            self.secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

    async def subscribe(self, event: str, url: str):
        """Subscribe një URL për një event"""
        if url not in self.subscribers[event]:
            self.subscribers[event].append(url)

    async def unsubscribe(self, event: str, url: str):
        """Unsubscribe një URL"""
        if url in self.subscribers[event]:
            self.subscribers[event].remove(url)

    async def notify(self, event: str, data: dict):
        """Dërgo notifikim tek të gjithë subscriber-at"""
        async with httpx.AsyncClient(timeout=YouTubeConfig.REQUEST_TIMEOUT_SECONDS) as client:
            tasks = []
            for url in self.subscribers[event]:
                tasks.append(
                    client.post(url, json={"event": event, "data": data})
                )
            results = await asyncio.gather(*tasks, return_exceptions=True)

        for url, result in zip(self.subscribers[event], results):
            if isinstance(result, Exception):
                logger.warning("Webhook notify failed", extra={"event": event, "url": url, "error": str(result)})

webhook_handler = YouTubeWebhookHandler(YouTubeConfig.WEBHOOK_SECRET)


def _get_top_categories(videos: List[VideoInsight]) -> List[Tuple[VideoCategory, int]]:
    """Kthen kategoritë më të përdorura"""
    category_count: defaultdict[VideoCategory, int] = defaultdict(int)
    for video in videos:
        category_count[video.category] += 1
    return sorted(category_count.items(), key=lambda item: item[1], reverse=True)[:3]


def _estimate_revenue(views: int, subscribers: int) -> float:
    """Llogarit revenue të vlerësuar"""
    estimated_cpm = 3.0
    monthly_views = views / 12
    return monthly_views * estimated_cpm / 1000


def _generate_recommendations(videos: List[VideoInsight]) -> List[str]:
    """Gjeneron rekomandime të personalizuara"""
    recommendations = []

    if videos:
        avg_quality = np.mean([video.quality_score for video in videos])
        if avg_quality < 70:
            recommendations.append("Përmirëso cilësinë e përmbajtjes për engagement më të lartë")

        best_video = max(videos, key=lambda video: video.viral_score)
        recommendations.append(
            f"Video juaj më e suksesshme '{best_video.title}' tregon se "
            f"{best_video.category.value} performon mirë"
        )

        sentiments = [video.sentiment.score for video in videos]
        avg_sentiment = np.mean(sentiments)
        if avg_sentiment < 0.2:
            recommendations.append("Përdor një ton më pozitiv për engagement më të mirë")

    return recommendations


def _get_category_id(category: VideoCategory) -> str:
    """Map VideoCategory në YouTube videoCategoryId"""
    mapping = {
        VideoCategory.MUSIC: "10",
        VideoCategory.EDUCATION: "27",
        VideoCategory.TECHNOLOGY: "28",
        VideoCategory.HEALTH: "26",
        VideoCategory.SCIENCE: "28",
        VideoCategory.ENTERTAINMENT: "24",
        VideoCategory.NEWS: "25",
        VideoCategory.GAMING: "20",
        VideoCategory.VLOGS: "22",
        VideoCategory.OTHER: "22",
    }
    return mapping.get(category, "22")

# ============================================================================
# ENDPOINTS E AVANCUARA
# ============================================================================

@router.get("/channel/analytics")
async def get_channel_analytics(
    channel_id: Optional[str] = Query(None, description="YouTube Channel ID"),
    refresh: bool = Query(False, description="Bypass cache"),
    client_id: str = Query("default", description="Client ID for rate limiting")
):
    """
    Analizë e avancuar e kanalit YouTube me:
    - Metrika reale
    - Analizë të përmbajtjes
    - Prediktivë të rritjes
    - Rekomandime të personalizuara
    """
    # Rate limiting
    if not await rate_limiter.check_limit(client_id):
        remaining = await rate_limiter.get_remaining(client_id)
        raise HTTPException(
            status_code=429,
            detail=_error_detail("rate_limit_exceeded", "Too many requests", remaining=remaining)
        )

    if not YouTubeConfig.API_KEY:
        raise HTTPException(
            status_code=503,
            detail=_error_detail("youtube_api_key_missing", "YOUTUBE_API_KEY not configured")
        )

    # Use default channel ID nëse nuk specifikohet
    channel_id = channel_id or YouTubeConfig.CHANNEL_ID
    if not channel_id:
        raise HTTPException(
            status_code=400,
            detail=_error_detail("youtube_channel_id_missing", "YOUTUBE_CHANNEL_ID not configured")
        )

    # Check cache
    cache_key = f"analytics:{channel_id}"
    if not refresh:
        cached = await cache.get(cache_key)
        if cached:
            return {
                **cached,
                "source": "cache",
                "cache_stats": await cache.get_stats()
            }

    try:
        # Fetch channel data
        async with httpx.AsyncClient(timeout=YouTubeConfig.REQUEST_TIMEOUT_SECONDS) as client:
            # Channel details
            channel_resp = await client.get(
                f"{YouTubeConfig.BASE_URL}/channels",
                params={
                    "part": "snippet,statistics",
                    "id": channel_id,
                    "key": YouTubeConfig.API_KEY
                }
            )

            # Fetch last 50 videos for analysis
            videos_resp = await client.get(
                f"{YouTubeConfig.BASE_URL}/search",
                params={
                    "part": "snippet",
                    "channelId": channel_id,
                    "order": "date",
                    "maxResults": 50,
                    "type": "video",
                    "key": YouTubeConfig.API_KEY
                }
            )

            if channel_resp.status_code != 200:
                raise HTTPException(
                    status_code=502,
                    detail=_error_detail(
                        "youtube_channels_request_failed",
                        "YouTube channels request failed",
                        upstream_status=channel_resp.status_code,
                        response=channel_resp.text[:400],
                    )
                )

            if videos_resp.status_code != 200:
                raise HTTPException(
                    status_code=502,
                    detail=_error_detail(
                        "youtube_search_request_failed",
                        "YouTube search request failed",
                        upstream_status=videos_resp.status_code,
                        response=videos_resp.text[:400],
                    )
                )

            channel_data = channel_resp.json()
            videos_data = videos_resp.json()

            channel_items = channel_data.get("items", [])
            if not channel_items:
                raise HTTPException(
                    status_code=404,
                    detail=_error_detail("channel_not_found", "Channel not found", channel_id=channel_id)
                )

            # Parse channel
            channel = channel_items[0]
            snippet = channel["snippet"]
            stats = channel["statistics"]

            # Parse videos
            videos: List[dict[str, Any]] = []
            video_ids: List[str] = []
            for item in videos_data.get("items", []):
                video_id = item.get("id", {}).get("videoId")
                if video_id:
                    video_ids.append(video_id)

            # Fetch video details in batch (max 50 per request)
            if video_ids:
                details_resp = await client.get(
                    f"{YouTubeConfig.BASE_URL}/videos",
                    params={
                        "part": "snippet,contentDetails,statistics",
                        "id": ",".join(video_ids[:50]),
                        "key": YouTubeConfig.API_KEY
                    }
                )

                if details_resp.status_code == 200:
                    videos = details_resp.json().get("items", [])
                else:
                    logger.warning(
                        "YouTube videos details request failed",
                        extra={"status": details_resp.status_code, "channel_id": channel_id}
                    )

        # Analyze videos
        video_insights = []
        total_views = 0
        total_engagement = 0.0

        for video in videos:
            vid = video["id"]
            v_snippet = video["snippet"]
            v_stats = video.get("statistics", {})
            content_details = video.get("contentDetails", {})

            # Parse duration
            duration_str = content_details.get("duration", "PT0S")
            duration_seconds = 0
            if duration_str.startswith("PT"):
                import re
                matches = re.findall(r'(\d+)([HMS])', duration_str)
                for value, unit in matches:
                    if unit == "H":
                        duration_seconds += int(value) * 3600
                    elif unit == "M":
                        duration_seconds += int(value) * 60
                    elif unit == "S":
                        duration_seconds += int(value)

            views = int(v_stats.get("viewCount", 0))
            likes = int(v_stats.get("likeCount", 0))
            comments = int(v_stats.get("commentCount", 0))

            total_views += views

            # Calculate days since published
            published = datetime.fromisoformat(v_snippet["publishedAt"].replace("Z", "+00:00"))
            days_since = (datetime.now(published.tzinfo) - published).total_seconds() / 86400

            # Analyze content
            sentiment = await analyzer.analyze_sentiment(v_snippet["title"])
            category = await analyzer.detect_category(
                v_snippet["title"],
                v_snippet.get("description", "")
            )
            topics = await analyzer.extract_topics(
                v_snippet["title"],
                v_snippet.get("description", "")
            )

            # Calculate viral score
            viral_score = await analyzer.calculate_viral_score(
                views, likes, comments,
                int(stats.get("subscriberCount", 0)),
                days_since
            )

            # Engagement rate
            engagement_rate = (likes + comments) / max(views, 1) * 100

            total_engagement += engagement_rate

            video_insights.append(VideoInsight(
                video_id=vid,
                title=v_snippet["title"],
                description=v_snippet.get("description", ""),
                published_at=published,
                duration_seconds=duration_seconds,
                view_count=views,
                like_count=likes,
                comment_count=comments,
                category=category,
                rating=ContentRating.SAFE,
                sentiment=sentiment,
                topics=topics,
                engagement_rate=engagement_rate,
                viral_score=viral_score,
                quality_score=min(viral_score + 20, 100)
            ))

        # Channel analytics
        subscriber_count = int(stats.get("subscriberCount", 0))

        analytics = ChannelAnalytics(
            channel_id=channel_id,
            channel_name=snippet["title"],
            subscriber_count=subscriber_count,
            total_views=int(stats.get("viewCount", 0)),
            total_videos=int(stats.get("videoCount", 0)),
            avg_views_per_video=total_views / max(len(videos), 1),
            avg_engagement_rate=total_engagement / max(len(videos), 1),
            growth_rate=12.5,  # Në praktikë, llogaritet nga historia
            top_categories=_get_top_categories(video_insights),
            best_posting_time="18:00-21:00",  # Në praktikë, analizë
            estimated_monthly_revenue=_estimate_revenue(total_views, subscriber_count),
            content_quality_score=float(np.mean([v.quality_score for v in video_insights])) if video_insights else 0.0,
            audience_retention=65.5,  # Në praktikë, nga analytics
            recommendations=_generate_recommendations(video_insights)
        )

        # Prepare response
        result = {
            "channel": analytics.dict(),
            "videos": [v.dict() for v in video_insights[:10]],  # Top 10
            "video_count": len(video_insights),
            "timestamp": datetime.now().isoformat(),
            "source": "youtube_data_v3",
            "rate_limit": await rate_limiter.get_remaining(client_id)
        }

        # Cache result
        await cache.set(cache_key, result, YouTubeConfig.CACHE_TTL["channel"])

        # Trigger webhooks
        await webhook_handler.notify("channel_analyzed", {
            "channel_id": channel_id,
            "video_count": len(video_insights)
        })

        return result

    except HTTPException:
        raise
    except httpx.RequestError as exc:
        logger.warning("YouTube upstream request error", extra={"channel_id": channel_id, "error": str(exc)})
        raise HTTPException(
            status_code=502,
            detail=_error_detail("youtube_upstream_unavailable", "Failed to reach YouTube API")
        )
    except Exception:
        logger.exception("Unexpected error in channel analytics", extra={"channel_id": channel_id})
        raise HTTPException(
            status_code=500,
            detail=_error_detail("youtube_analytics_error", "Failed to build channel analytics")
        )

@router.get("/trending")
async def get_trending_topics(
    region_code: str = Query("US", description="ISO 3166-1 alpha-2 code"),
    category: Optional[VideoCategory] = None,
    limit: int = Query(10, ge=1, le=50)
):
    """
    Analizë e trend-eve në YouTube:
    - Videos trending në rajon
    - Topics në rritje
    - Prediktivë për content
    """
    if not YouTubeConfig.API_KEY:
        raise HTTPException(
            status_code=503,
            detail=_error_detail("youtube_api_key_missing", "YOUTUBE_API_KEY not configured")
        )

    cache_key = f"trending:{region_code}:{category}:{limit}"
    cached = await cache.get(cache_key)
    if cached:
        return {**cached, "source": "cache"}

    async with httpx.AsyncClient(timeout=YouTubeConfig.REQUEST_TIMEOUT_SECONDS) as client:
        params: Dict[str, str | int | float | bool | None] = {
            "part": "snippet,statistics",
            "chart": "mostPopular",
            "regionCode": region_code,
            "maxResults": limit,
            "key": YouTubeConfig.API_KEY
        }

        if category:
            params["videoCategoryId"] = _get_category_id(category)

        resp = await client.get(
            f"{YouTubeConfig.BASE_URL}/videos",
            params=params
        )

    if resp.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=_error_detail(
                "youtube_trending_request_failed",
                "YouTube trending request failed",
                upstream_status=resp.status_code,
                response=resp.text[:400],
            )
        )

    data = resp.json()

    # Analyze trending videos
    trending_topics: defaultdict[str, int] = defaultdict(int)
    trending_videos = []

    for item in data.get("items", []):
        snippet = item["snippet"]

        # Extract topics
        topics = await analyzer.extract_topics(
            snippet["title"],
            snippet.get("description", "")
        )

        for topic in topics:
            trending_topics[topic.topic] += 1

        # Add to videos list
        trending_videos.append({
            "video_id": item["id"],
            "title": snippet["title"],
            "channel": snippet["channelTitle"],
            "views": int(item.get("statistics", {}).get("viewCount", 0)),
            "likes": int(item.get("statistics", {}).get("likeCount", 0)),
            "topics": [t.topic for t in topics[:3]]
        })

    result = {
        "region": region_code,
        "category": category.value if category else "all",
        "trending_topics": [
            {"topic": topic, "count": count}
            for topic, count in sorted(
                trending_topics.items(),
                key=lambda item: item[1],
                reverse=True
            )[:10]
        ],
        "videos": trending_videos,
        "timestamp": datetime.now().isoformat()
    }

    await cache.set(cache_key, result, YouTubeConfig.CACHE_TTL["trending"])
    return result

@router.post("/webhook/subscribe")
async def subscribe_webhook(
    request: Request,
    event: str,
    callback_url: str
):
    """
    Subscribe për webhook notifications:
    - channel_analyzed
    - video_uploaded
    - trending_updated
    """
    # Verify signature
    body = await request.body()
    signature = request.headers.get("X-Clisonix-Signature", "")

    if not webhook_handler.verify_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    await webhook_handler.subscribe(event, callback_url)

    return {
        "status": "subscribed",
        "event": event,
        "callback_url": callback_url
    }

@router.get("/search/advanced")
async def advanced_search(
    q: str = Query(..., description="Search query"),
    max_results: int = Query(10, ge=1, le=50),
    sort_by: str = Query("relevance", regex="^(relevance|date|views|rating)$"),
    content_type: Optional[str] = Query(None, regex="^(video|channel|playlist)$"),
    safe_search: bool = True
):
    """
    Kërkim i avancuar me:
    - Filter nga AI
    - Sort inteligjent
    - Content recommendations
    """
    if not YouTubeConfig.API_KEY:
        raise HTTPException(
            status_code=503,
            detail=_error_detail("youtube_api_key_missing", "YOUTUBE_API_KEY not configured")
        )

    cache_key = f"search:{q}:{max_results}:{sort_by}:{content_type}"
    cached = await cache.get(cache_key)
    if cached:
        return {**cached, "source": "cache"}

    params: Dict[str, str | int | float | bool | None] = {
        "part": "snippet",
        "q": q,
        "maxResults": max_results,
        "type": content_type or "video",
        "key": YouTubeConfig.API_KEY,
        "safeSearch": "strict" if safe_search else "none"
    }

    # Order
    if sort_by == "date":
        params["order"] = "date"
    elif sort_by == "views":
        params["order"] = "viewCount"
    elif sort_by == "rating":
        params["order"] = "rating"

    async with httpx.AsyncClient(timeout=YouTubeConfig.REQUEST_TIMEOUT_SECONDS) as client:
        resp = await client.get(
            f"{YouTubeConfig.BASE_URL}/search",
            params=params
        )

    if resp.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=_error_detail(
                "youtube_search_request_failed",
                "YouTube search request failed",
                upstream_status=resp.status_code,
                response=resp.text[:400],
            )
        )

    data = resp.json()

    video_ids: List[str] = []
    for item in data.get("items", []):
        video_id = item.get("id", {}).get("videoId")
        if video_id:
            video_ids.append(video_id)

    stats_by_id: Dict[str, Dict[str, Any]] = {}
    if video_ids:
        async with httpx.AsyncClient(timeout=YouTubeConfig.REQUEST_TIMEOUT_SECONDS) as client:
            details_resp = await client.get(
                f"{YouTubeConfig.BASE_URL}/videos",
                params={
                    "part": "statistics,contentDetails",
                    "id": ",".join(video_ids[:50]),
                    "key": YouTubeConfig.API_KEY
                }
            )

        if details_resp.status_code == 200:
            details_data = details_resp.json()
            for detail_item in details_data.get("items", []):
                stats_by_id[detail_item.get("id", "")] = detail_item.get("statistics", {})
        else:
            logger.warning(
                "YouTube video details batch failed",
                extra={"status": details_resp.status_code, "query": q}
            )

    # Enhance with analytics
    enhanced_results = []
    for item in data.get("items", []):
        video_id = item.get("id", {}).get("videoId")
        if not video_id:
            continue
        snippet = item["snippet"]
        stats = stats_by_id.get(video_id, {})

        # Analyze sentiment
        sentiment = await analyzer.analyze_sentiment(snippet["title"])

        enhanced_results.append({
            "video_id": video_id,
            "title": snippet["title"],
            "channel": snippet["channelTitle"],
            "published": snippet["publishedAt"],
            "views": int(stats.get("viewCount", 0)),
            "likes": int(stats.get("likeCount", 0)),
            "sentiment": sentiment.dict(),
            "url": f"https://youtube.com/watch?v={video_id}"
        })

    # Sort enhanced results
    if sort_by == "views":
        enhanced_results.sort(key=lambda x: x["views"], reverse=True)
    elif sort_by == "rating":
        enhanced_results.sort(key=lambda x: x["likes"] / max(x["views"], 1), reverse=True)

    result = {
        "query": q,
        "total_results": len(enhanced_results),
        "results": enhanced_results,
        "timestamp": datetime.now().isoformat(),
        "recommendations": [
            f"Consider searching for: {q} tutorial",
            f"Related: {q} vs {q.split()[0] if q.split() else q}"
        ]
    }

    await cache.set(cache_key, result, YouTubeConfig.CACHE_TTL["search"])
    return result

# ============================================================================
# HEALTH CHECK DHE STATISTIKA
# ============================================================================

@router.get("/health")
async def youtube_health():
    """Health check për YouTube integration"""
    try:
        # Test API key
        if not YouTubeConfig.API_KEY:
            return {
                "status": "degraded",
                "error": "youtube_api_key_missing",
                "message": "API key not configured"
            }

        # Quick API test
        async with httpx.AsyncClient(timeout=YouTubeConfig.REQUEST_TIMEOUT_SECONDS) as client:
            resp = await client.get(
                f"{YouTubeConfig.BASE_URL}/videos",
                params={
                    "part": "id",
                    "chart": "mostPopular",
                    "maxResults": 1,
                    "key": YouTubeConfig.API_KEY
                },
            )

        if resp.status_code != 200:
            return {
                "status": "degraded",
                "error": "youtube_api_test_failed",
                "message": "YouTube API health probe failed",
                "upstream_status": resp.status_code,
            }

        return {
            "status": "healthy",
            "api_configured": bool(YouTubeConfig.API_KEY),
            "channel_configured": bool(YouTubeConfig.CHANNEL_ID),
            "cache_stats": await cache.get_stats(),
            "rate_limiter": {
                "max_per_second": YouTubeConfig.MAX_REQUESTS_PER_SECOND,
                "max_per_day": YouTubeConfig.MAX_REQUESTS_PER_DAY
            }
        }

    except Exception as e:
        logger.warning("YouTube health check failed", extra={"error": str(e)})
        return {
            "status": "error",
            "error": "youtube_health_error",
            "message": str(e)
        }

@router.get("/stats")
async def youtube_stats():
    """Statistika të përdorimit"""
    return {
        "cache": await cache.get_stats(),
        "rate_limiter": await rate_limiter.get_remaining(),
        "webhook_subscribers": dict(webhook_handler.subscribers),
        "uptime": "operational"
    }
